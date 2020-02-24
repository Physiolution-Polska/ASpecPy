"""
Module constains functions declarations from 'libavs.so.0.2.0'
and assigment to *pythons* functions
"""
import threading
from ctypes import *
from structures import *

wait_thread = None
is_measurement_available = threading.Event()

# Loading shared library
_AvaSpecDLL = CDLL('./libavs.so.0.2.0')

init = _AvaSpecDLL.AVS_Init
init.argtypes = [c_short]
init.restype = c_int

done = _AvaSpecDLL.AVS_Done
done.argtypes = []
done.restype = c_int

activate = _AvaSpecDLL.AVS_Activate
activate.argtypes = [POINTER(AvsIdentityType)]
activate.restype = c_long

deactivate = _AvaSpecDLL.AVS_Deactivate
deactivate.argtypes = [c_long]
deactivate.restype = c_bool

getListOfDevices = _AvaSpecDLL.AVS_GetList
getListOfDevices.argtypes = [c_uint, POINTER(c_uint), POINTER(AvsIdentityType)]
getListOfDevices.restype = c_int

updateUsbDevices = _AvaSpecDLL.AVS_UpdateUSBDevices
updateUsbDevices.argtypes = []
updateUsbDevices.restype = c_int

getNumPixels = _AvaSpecDLL.AVS_GetNumPixels
getNumPixels.argtypes = [c_long, POINTER(c_ushort)]
getNumPixels.restype = c_int

getAnalogIn = _AvaSpecDLL.AVS_GetAnalogIn
getAnalogIn.argtypes = [c_long, c_ubyte, POINTER(c_float)]
getAnalogIn.restype = c_int

getDigitalIn = _AvaSpecDLL.AVS_GetDigIn
getDigitalIn.argtypes = [c_long, c_ubyte, POINTER(c_ubyte)]
getDigitalIn.restype = c_int

setDigitalOut = _AvaSpecDLL.AVS_SetDigOut
setDigitalOut.argtypes = [c_long, c_ubyte, c_ubyte]
setDigitalOut.restype = c_int

prepareMeasure = _AvaSpecDLL.AVS_PrepareMeasure
prepareMeasure.argtypes = [c_long, POINTER(MeasConfigType)]
prepareMeasure.restype = c_int

stopMeasure = _AvaSpecDLL.AVS_StopMeasure
stopMeasure.argtypes = [c_long]
stopMeasure.restype = c_int

getScopeData = _AvaSpecDLL.AVS_GetScopeData
getScopeData.argtypes = [c_long, POINTER(c_uint), POINTER(c_double)]
getScopeData.restype = c_int

CALLBACK = CFUNCTYPE(None, POINTER(c_long), POINTER(c_int))


@CALLBACK
def call_back(handle, new_scan):
    """
    Callback function which is called by 'measure' function
    after measurement data will be available

    handle: Pointer to a device handler
    new_scan: Will be set to '0', if new scan is available

    Launching a 'thread' as a workaround solution
    for waiting condition, which notify main thread
    with necessary condition.
    """
    global wait_thread
    wait_thread = threading.Thread(target=measurement_waiting)
    wait_thread.start()


measure = _AvaSpecDLL.AVS_Measure
measure.argtypes = [c_long, CALLBACK, c_short]
measure.restype = c_int

pollScan = _AvaSpecDLL.AVS_PollScan
pollScan.argtypes = [c_long]
pollScan.restype = c_int

getLambda = _AvaSpecDLL.AVS_GetLambda
getLambda.argtypes = [c_long, POINTER(c_double)]
getLambda.restype = c_int


def measurement_waiting():
    """
    Function called in a CALLBACK function,
    which allow to continue main thread,
    [my suspection] as a 'GIL unlock' cause
    unexpected behavior.

    Conditional variable 'set' is done as a necessary waiting
    condition for completing the measurements
    """
    global is_measurement_available
    is_measurement_available.set()
