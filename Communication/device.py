import time
import data
import threading
import numpy as np
import ctypes as ct
import avantes_func as ava
from structures import *
from error_codes import *
from avantes_func import *
from debug import log

MEASUREMENT_TIMEOUT = None
measuring_thread = None
stop_measuring = threading.Event()

class Device():
    def __init__(self, devType, devCfg):
        self.cfg = None
        self.handler = None
        self.devList = None
        self.data = data.Data()
        self.devType = devType
        self.cfgType = devCfg
        self.initialize()
        if not self.deviceSelfTest():
            if __debug__:
                log.error('Unsuccessful device self test')
            exit(-6)

    def initialize(self):
        try:
            return getattr(self, self.devType)()
        except AttributeError:
            return False

    def avantes(self):
        """
        Value '0' means communication via 'USB'
        """
        if ava.init(ct.c_short(0)) <= 0:
            if __debug__:
                log.error('Unsuccessful initialization')
            exit(-2)
        else:
            self.devList = (AvsIdentityType
                            * GLOBAL_VARS['DEVICES_AMOUNT'])()

            ava.getListOfDevices(sizeof(self.devList),
                                 ct.c_uint(1), self.devList)

            """
            Activation of the first 'not used' device
            in the device list. 
            Probably should be changed to device ID
            (serial number which is a message queue name)
            """
            for device in self.devList:
                if device._status[0] == 1:
                    self.handler = ava.activate(device)
                    break

            if not self.handler:
                if __debug__:
                    log.error('No handler for device')
                exit(-3)

            pixelRange = ct.c_ushort(0)
            ava.getNumPixels(self.handler, pixelRange)
            pixelRange.value -= 1
            GLOBAL_VARS['MAXIMUM_PIXELS_RANGE'] = pixelRange.value
            self.cfg = MeasConfigType(self.cfgType)
            """
            If the config was set to 'user'
            the stop pixel value won't be updated
            """
            if self.cfgType != 'user':
                self.cfg.loadCfg({'_stopPixel': pixelRange.value})
            
            """
            Pickle cannot handle such types in a raw
            format
            """
            self.devList = None

            return self.deviceSelfTest()
        return False

    def deviceSelfTest(self):
        try:
            return getattr(self, 'test_' + self.devType)()
        except AttributeError:
            return False


    def test_avantes(self):
        if (self.handler > 0 and
                ava.prepareMeasure(self.handler, self.cfg) == 0):
            """
            Setting wavelength data
            based on the documentation
            """
            self.data.c_double_array = (c_double
                                        * GLOBAL_VARS['MAX_NR_PIXELS'])()
            cast(self.data.c_double_array, POINTER(c_double))

            if ava.getLambda(self.handler, self.data.c_double_array) == 0:
                data = np.ctypeslib.as_array(self.data.c_double_array)
                self.data.wavelength = np.copy(data)
                """
                Array resizing as the max pixel range might be bigger,
                than capabilities of the device itself
                (2048 or 4096 series)
                No need in unused data structures filled with '0'
                """
                self.data.wavelength = np.resize(self.data.wavelength,
                                       GLOBAL_VARS['MAXIMUM_PIXELS_RANGE'])
            return True
        return False

    def update(self, values):
        try:
            return getattr(self, 'update_' + self.devType)(values)
        except AttributeError:
            return False

    def update_avantes(self, values):
        updateDict = dict(zip(UPDATABLE_CFG, values))
        if self.cfg.loadCfg(updateDict):
            return ava.prepareMeasure(self.handler, self.cfg)
        return False

    def measure(self, values):
        try:
            #type of measurement result storage
            #{black, clean, analyte}
            self.data.type = values
            return getattr(self, 'measure_' + self.devType)()
        except AttributeError:
            return False

    def measure_avantes(self):
        exitStatus = ava.prepareMeasure(self.handler, self.cfg)
        if __debug__:
            log.warning('Prepare measurenet function return %s',
                        ERROR_CODES_MESSAGES[exitStatus])
        if exitStatus == 0:
            if self.data.type != 'black':
                ava.setDigitalOut(self.handler, c_ubyte(3), c_ubyte(1))
            else:
                ava.setDigitalOut(self.handler, c_ubyte(3), c_ubyte(0))

            if self.cfg.amount == -1:
                global measuring_thread
                # infinite measurement
                exitStatus = ava.measure(self.handler,
                                         call_back,
                                         c_short(self.cfg.amount))

                measuring_thread = threading.Thread(target=self.infinite_measure)
                measuring_thread.start()
            else:
                exitStatus = ava.measure(self.handler,
                                         call_back,
                                         c_short(self.cfg.amount))
                if __debug__:
                    log.warning('Measurement function return %s',
                                ERROR_CODES_MESSAGES[exitStatus])

                if exitStatus == 0:
                    """
                    Main thread stop as a workaround for
                    Incorrect behavior
                    """
                    global MEASUREMENT_TIMEOUT
                    global is_measurement_available

                    if not is_measurement_available.wait(timeout=MEASUREMENT_TIMEOUT):
                        if __debug__:
                            log.error('Measurement timeout occur %s',
                                      ERROR_CODES_MESSAGES[exitStatus])
                        return False
                    else:

                        is_measurement_available.clear()
                        # arbitrary defined timeout time
                        return avantesGetScopeData()
        return False

    def avantesGetScopeData(self):
        """
        Scoped data should be collected as many times,
        as measurement amount was set
        (amount of measurements)
        """
        for i in range (0, self.cfg.amount):
            """
            Data might not be ready yet,
            so a procedure will be repeated a few more times,
            for successful data collection
            """
            timeout = time.time() + 6
            while time.time() < timeout:
                time.sleep(0.5)
                exitStatus = ava.getScopeData(self.handler,
                                              c_uint(1),
                                              self.data.c_double_array)
                if exitStatus != 0:
                    if __debug__:
                        log.error('Cannot get scoped data %s',
                                  ERROR_CODES_MESSAGES[exitStatus])
                else:
                    break

            """
            Device hadn't sent the data
            errors in communication might be
            """
            if exitStatus != 0:
                if __debug__:
                    log.warning('Data receiving timeout')
                return False

            avantesSetMeasAttribute()
             
            if self.data.type == 'analyte':
                self.data.absorbance()

        return True

    def avantesSetMeasAttribute(self):
        data = np.ctypeslib.as_array(self.data.c_double_array)
        data = np.resize(data, GLOBAL_VARS['MAXIMUM_PIXELS_RANGE'])
        try:
            setattr(self.data, self.data.type, data) 
        except AttributeError:
            if __debug__:
                log.error('Uspecified attribute for data storing')

    def measurement_timeout(self):
        try:
            return getattr(self, 'timeout_' + self.devType)()
        except AttributeError:
            return False

    def timeout_avantes(self):
        global MEASUREMENT_TIMEOUT
        """
        Time is in seconds
        (as the integration time defined in milliseconds)
        """
        MEASUREMENT_TIMEOUT = (self.cfg._integrationTime
                               * self.cfg._nrAverages
                               * self.cfg.amount) // 1000

        if MEASUREMENT_TIMEOUT < 1:
            MEASUREMENT_TIMEOUT = 2
        else:
            MEASUREMENT_TIMEOUT *= 2

        return MEASUREMENT_TIMEOUT
    
    def infinite_measure(self):
        global stop_measuring
        while not stop_measuring.is_set():
            time.sleep(0.5)
            exitStatus = ava.getScopeData(self.handler,
                                          c_uint(1),
                                          self.data.c_double_array)
            if exitStatus == 0:
                avantesSetMeasAttribute()
                if self.data.type == 'analyte':
                    self.data.absorbance()

            if __debug__:
                log.error('While loop return %s',
                          ERROR_CODES_MESSAGES[exitStatus])
            # hook to update the graph
            # socket io for flask
            # js on web page
        return True

    def stop(self):
        try:
            return getattr(self, 'stop_' + self.devType)()
        except AttributeError:
            return False

    def stop_avantes(self):
        global measuring_thread
        stop_measuring.set()
        measuring_thread.join()
        exitStatus = ava.stopMeasure(self.handler)
        if __debug__:
            log.warning('Stopped infinite measurement with code: %s',
                        ERROR_CODES_MESSAGES[exitStatus])
            """
            Probably, last measurement should be written to a
            file/db
            """
        return True

    def release(self):
        try:
            return getattr(self, 'release_' + self.devType)()
        except AttributeError:
            return False

    def release_avantes(self):
        ava.setDigitalOut(self.handler, c_ubyte(3), c_ubyte(0))
        if ava.deactivate(self.handler):
            ava.done()
            return True
        ava.done()
        return False
