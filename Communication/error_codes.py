"""
Module contains various errors codes, that might be returned by the
called functions from 'functions.py' module.
"""

ERROR_CODES_MESSAGES = {
        0: 'ERR_SUCCESS',
        -1: 'ERR_INVALID_PARAMETER',
        -2: 'ERR_OPERATION_NOT_SUPPORTED',
        -3: 'ERR_DEVICE_NOT_FOUND',
        -4: 'ERR_INVALID_DEVICE_ID',
        -5: 'ERR_OPERATION_PENDING',
        -6: 'ERR_TIMEOUT',
        -7: 'ERR_INVALID_PASSWORD',
        -8: 'ERR_INVALID_MEAS_DATA',
        -9: 'ERR_INVALID_SIZE',
        -10: 'ERR_INVALID_PIXEL_RANGE',
        -11: 'ERR_INVALID_INT_TIME',
        -12: 'ERR_INVALID_COMBINATION',
        -13: 'ERR_INVALID_CONFIGURATION',
        -14: 'ERR_NO_MEAS_BUFFER_AVAIL',
        -15: 'ERR_UNKNOWN',
        -16: 'ERR_COMMUNICATION',
        -17: 'ERR_NO_SPECTRA_IN_RAM',
        -18: 'ERR_INVALID_DLL_VERSION',
        -19: 'ERR_NO_MEMORY',
        -20: 'ERR_DLL_INITIALISATION',
        -21: 'ERR_INVALID_STATE',
        -22: 'ERR_INVALID_REPLY',
        -23: 'ERR_GIGE_MEASUREMENT_SERVER',
        # Return error codes; DeviceData check
        -100: 'ERR_INVALID_PARAMETER_NR_PIXELS',
        -101: 'ERR_INVALID_PARAMETER_ADC_GAIN',
        -102: 'ERR_INVALID_PARAMETER_ADC_OFFSET',
        # Return error codes; PrepareMeasurement check
        -110: 'ERR_INVALID_MEASPARAM_AVG_SAT2',
        -111: 'ERR_INVALID_MEASPARAM_AVG_RAM',
        -112: 'ERR_INVALID_MEASPARAM_SYNC_RAM',
        -113: 'ERR_INVALID_MEASPARAM_LEVEL_RAM',
        -114: 'ERR_INVALID_MEASPARAM_SAT2_RAM',
        -115: 'ERR_INVALID_MEASPARAM_FWVER_RAM',
        -116: 'ERR_INVALID_MEASPARAM_DYNDARK',
        # Return error codes; SetSensitivityMode check
        -120: 'ERR_NOT_SUPPORTED_BY_SENSOR_TYPE',
        -121: 'ERR_NOT_SUPPORTED_BY_FW_VER',
        -122: 'ERR_NOT_SUPPORTED_BY_FPGA_VER',
        # Return error codes; SuppressStrayLight check
        -140: 'ERR_SL_CALIBRATION_NOT_AVAILABLE',
        -141: 'ERR_SL_STARTPIXEL_NOT_IN_RANGE',
        -142: 'ERR_SL_ENDPIXEL_NOT_IN_RANGE',
        -143: 'ERR_SL_STARTPIX_GT_ENDPIX',
        -144: 'ERR_SL_MFACTOR_OUT_OF_RANGE',
        }
