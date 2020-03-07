"""
Module contains structures and global variables definitions
based on provided header file 'avaspec.h'
"""
import sys
import json
from ctypes import *

# Global variables dictionary
user_cfg = None
NOT_VALID = 0
GLOBAL_VARS = {
        'DEVICES_AMOUNT': 1,
        'AVS_SERIAL_LEN': 10,
        'USER_ID_LEN': 64,
        'MAX_NR_PIXELS': 4096,
        'NR_WAVELEN_POL_COEF': 5,
        'NR_NONLIN_POL_COEF': 8,
        'MAX_VIDEO_CHANNELS': 2,
        'NR_DEFECTIVE_PIXELS': 30,
        'MAX_TEMP_SENSORS': 3,
        'NR_DAC_POL_COEF': 2,
        'NR_TEMP_POL_COEF': 2,
        'INPUT_ARRAY_SIZE': 2,
        'MAXIMUM_PIXELS_RANGE': 0,
        'NUMBER_OF_MEASUREMENTS': 1
        }

ACCEPTABLE_VALUES = {
    "_startPixel": [0, 4095],
    "_stopPixel": [0, 4095],
    "_integrationTime": [0.002, 600000],
    "_integrationDelay": [0, c_uint(-1).value],
    "_nrAverages": [0, 5000],
    "_enable": [0, 1],
    "_forgetPercentage": [0, 100],
    "_smoothPix": [0, 2048],
    "_smoothModel": [0, 0],
    "_saturationDetection": [0, 1],
    "_mode": [0, 1],
    "_source": [0, 1],
    "_sourceType": [0, 1],
    "_strobeControl": [0, c_uint16(-1).value],
    "_laserDelay": [0, c_uint(-1).value],
    "_laserWidth": [0, c_uint(-1).value],
    "_laserWaveLength": [0, sys.float_info.max],
    "_storeToRam": [0, 1]
}

FILES = {
        'user': 'ava_user.json',
        'default': 'ava_default.json'
        }

UPDATABLE_CFG = ['_integrationTime', '_nrAverages']


class AvsIdentityType(Structure):
    _fields_ = [
            ("_serialNumber",
                c_char * GLOBAL_VARS['AVS_SERIAL_LEN']),
            ("_userFriendlyName",
                c_char * GLOBAL_VARS['USER_ID_LEN']),
            ("_status", c_char)
            ]


class DarkCorrectionType(Structure):
    _fields_ = [
            ("_enable", c_uint8),
            ("_forgetPercentage", c_uint8)
            ]


class SmoothingType(Structure):
    _fields_ = [
            ("_smoothPix", c_uint16),
            ("_smoothModel", c_uint8)
            ]


class TriggerType(Structure):
    _fields_ = [
            ("_mode", c_uint8),
            ("_source", c_uint8),
            ("_sourceType", c_uint8)
            ]


class ControlSettingsType(Structure):
    _fields_ = [
            ("_strobeControl", c_uint16),
            ("_laserDelay", c_uint32),
            ("_laserWidth", c_uint32),
            ("_laserWaveLength", c_float),
            ("_storeToRam", c_uint16)
            ]


class MeasConfigType(Structure):
    _fields_ = [
            ("_startPixel", c_uint16),
            ("_stopPixel", c_uint16),
            ("_integrationTime", c_float),
            ("_integrationDelay", c_uint32),
            ("_nrAverages", c_uint32),
            ("_corDynDark", DarkCorrectionType),
            ("_smoothing", SmoothingType),
            ("_saturationDetection", c_uint8),
            ("_trigger", TriggerType),
            ("_control", ControlSettingsType)
            ]

    def __init__(self, dev_cfg):
        self.dev_cfg = dev_cfg
        self.loadCfg(self.dev_cfg)
        self.amount = GLOBAL_VARS['NUMBER_OF_MEASUREMENTS']

    def checkPixelRange(self):
        """
        Function validate pixel range
        Reloading from global variables
        if in config '_stopPixel' was 0
        """
        if self._startPixel > self._stopPixel:
            self._startPixel = self._stopPixel

        if self._stopPixel == 0:
            self._stopPixel = GLOBAL_VARS['MAXIMUM_PIXELS_RANGE']

    def setAmount(self, amount):
        # {(0,65535], -1}
        if ((amount > 0) and (amount <= 0xffff) or
              (amount == -1)):
            self.amount = amount
        else:
            return False
        return True

    def loadCfg(self, cfg):
        """
        Function able to load
        device configuration from 'json' file
        example of the file 'ava_user_cfg.json'
        If the provide value in config file is invalid
        the value will be set to the default value
        or initialized with 0
        """
        global user_cfg
        global FILES
        global NOT_VALID
        if not isinstance(cfg, str):
            user_cfg = cfg
        else:
            self.dev_cfg = cfg
            with open(FILES[self.dev_cfg]) as json_data:
                user_cfg = json.load(json_data)

        for key, value in user_cfg.items():
            self.setAttributes(key, value, self)

        if NOT_VALID != 0:
            NOT_VALID = 0
            return False

        self.checkPixelRange()

        return True

    def setAttributes(self, key, value, parent):
        """
        Function updates 'default' device
        config with is in use by the device
        """
        if not isinstance(value, dict):
            if self.isValid(key, value):
                try:
                    setattr(parent, key, value)
                except TypeError:
                    setattr(parent, key, int(value))
        else:
            try:
                parent = getattr(parent, key)
                for child_key, child_value in value.items():
                    self.setAttributes(child_key, child_value, parent)
            except AttributeError:
                """
                The loop is going throught key and values
                from json file, so error might be only in
                the json file
                (unspecified name of attibute)
                """
                pass



    def isValid(self, key, value):
        """
        Function check, whether the device config
        might be updted with the provied values
        dict as 'ACCEPTABLE_VALUES' with one value
        """
        global NOT_VALID
        try:
            if (value >= ACCEPTABLE_VALUES[key][0] and
                    value <= ACCEPTABLE_VALUES[key][1]):
                return True

            NOT_VALID += 1
            return False

        except KeyError:
            return False

    def cfgAsDict(self):
        """
        Collecting sturctures and substructures 
        fields with values into a dict
        """
        cfg = {}
        for paramTuple in self._fields_:
            param = paramTuple[0]
            value = getattr(self, param)
            if isinstance(value, (int,float)):
                cfg[param] = value 
            else:
                cfg[param] = {}
                for childTuple in value._fields_:
                    childParam = childTuple[0]
                    cfg[param][childParam] = getattr(value, childParam)
        return cfg




class DetectorType(Structure):
    _fields_ = [
            ("_sensorType", c_uint8),
            ("_nrPixels", c_uint16),
            ("_fit", c_float * GLOBAL_VARS['NR_WAVELEN_POL_COEF']),
            ("_nlEnable", c_bool),
            ("_nlCorrect", c_double * GLOBAL_VARS['NR_NONLIN_POL_COEF']),
            ("_lowNLCounts", c_double),
            ("_highNLCounts", c_double),
            ("_gain", c_float * GLOBAL_VARS['MAX_VIDEO_CHANNELS']),
            ("_reserved", c_float),
            ("_offset", c_float * GLOBAL_VARS['MAX_VIDEO_CHANNELS']),
            ("_extOffset", c_float),
            ("_defectivePixels", c_uint16
                * GLOBAL_VARS['NR_DEFECTIVE_PIXELS']),
            ]


class SmoothingType(Structure):
    _fields_ = [
            ("_smoothPix", c_uint16),
            ("_smoothModel", c_uint8)
            ]


class SpectrumCalibrationType(Structure):
    _fields_ = [
            ("_smoothing", SmoothingType),
            ("_calIntTime", c_float),
            ("_calibConvers", c_float * GLOBAL_VARS['MAX_NR_PIXELS'])
            ]


class IrradianceType(Structure):
    _fields_ = [
            ("_intensityCalib", SpectrumCalibrationType),
            ("_calibrationType", c_uint8),
            ("_fiberDiameter", c_uint32)
            ]


class SpectrumCorrectionType(Structure):
    _fields_ = [
            ("_spectrumCorrect", c_float * GLOBAL_VARS['MAX_NR_PIXELS'])
            ]


class StandAloneType(Structure):
    _fields_ = [
            ("_enable", c_bool),
            ("_measConfig", MeasConfigType),
            ("_nmsr", c_int16)
            ]


class DynamicStorageType(Structure):
    _fields_ = [
            ("_nmsr", c_int32),
            ("_reserved", c_uint8 * 8)
            ]


class TempSensorType(Structure):
    _fields_ = [
            ("_fit", c_float * GLOBAL_VARS['NR_TEMP_POL_COEF'])
            ]


class TecControlType(Structure):
    _fields_ = [
            ("_enable", c_bool),
            ("_setPoint", c_float),
            ("_fit", c_float * GLOBAL_VARS['NR_DAC_POL_COEF'])
            ]


class ProcessControlType(Structure):
    _fields_ = [
            ("_analogLow", c_float * 2),
            ("_analogHigh", c_float * 2),
            ("_digitalLow", c_float * 10),
            ("_digitalHigh", c_float * 10)
            ]


class EthernetSettingType(Structure):
    _fields_ = [
            ("_ip", c_uint32),
            ("_mask", c_uint32),
            ("_gateway", c_uint32),
            ("_dhcpEnabled", c_uint8),
            ("_tcpPort", c_uint16),
            ("_linkStatus", c_uint8)
            ]


SETTINGS_RESERVED_LEN = 62*1024
- sizeof(c_uint32)
- (sizeof(c_uint16) * 2
    + GLOBAL_VARS['USER_ID_LEN']
    + sizeof(DetectorType)
    + sizeof(IrradianceType)
    + sizeof(SpectrumCalibrationType)
    + sizeof(SpectrumCorrectionType)
    + sizeof(StandAloneType)
    + sizeof(DynamicStorageType)
    + sizeof(TempSensorType) * GLOBAL_VARS['MAX_TEMP_SENSORS']
    + sizeof(TecControlType)
    + sizeof(ProcessControlType)
    + sizeof(EthernetSettingType))

GLOBAL_VARS['SETTINGS_RESERVED_LEN'] = SETTINGS_RESERVED_LEN


class DeviceConfigType(Structure):
    _fields_ = [
            ("_len", c_uint16),
            ("_configVersion", c_uint16),
            ("_userFriendlyId", c_char * GLOBAL_VARS['USER_ID_LEN']),
            ("_detector", DetectorType),
            ("_irradiance", IrradianceType),
            ("_reflectance", SpectrumCalibrationType),
            ("_spectrumCorrect", SpectrumCorrectionType),
            ("_standAlone", StandAloneType),
            ("_dynamicStorageType", DynamicStorageType),
            ("_temperature", TempSensorType
                * GLOBAL_VARS['MAX_TEMP_SENSORS']),
            ("_tecControl", TecControlType),
            ("_processControl", ProcessControlType),
            ("_ethernetSettings", EthernetSettingType),
            ("_reserved", c_uint8 * GLOBAL_VARS['SETTINGS_RESERVED_LEN'])
            ]
