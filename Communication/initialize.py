"""
Script will run after 
avantes device will be
connected via usb 
"""
RETRY_AFTER_ERROR = 10
# setting working directory 
import os

# the file is a link
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# set up logger
import logging.config
logging.config.fileConfig(fname='avantes_log.conf')

import time
import ctypes as ct
from structures import *
from avantes_func import *
from subprocess import run

# getting dev_id
if init(ct.c_short(0)) <= 0:
    logging.error('Failed to connect the device')
else:
    # the device is only 1
    device = (AvsIdentityType
                    * GLOBAL_VARIABLES['DEVICES_AMOUNT'])()

    getListOfDevices(sizeof(device),
                     ct.c_uint(1),
                     device)
    dev_id = device[0]._serialNumber.decode()
    done()
    logging.debug('Found device: %s', dev_id)
    logging.debug('Calling receiver process')
    """
    to start process without logs
    change process call to:

    process = run(['python3', '-O', 'receiver.py', '--id', dev_id])
    """
    process = run(['python3', 'receiver.py', '--id', dev_id])
    while (RETRY_AFTER_ERROR > 0 and process.returncode == 1):
        # communication terminated
        # because of timeout
        logging.warning('Retrying')
        process = run(['python3', 'receiver.py', '--id', dev_id])
        RETRY_AFTER_ERROR -= 1
    # any other error return code
    if (RETRY_AFTER_ERROR == 0 and process.returncode == 1):
        logging.warning('Too many timeout errors occur')

    logging.debug('Receiver exited with code: %s', process.returncode)
    import posix_ipc as posix
    mq = posix.MessageQueue('/' + str(dev_id), posix.O_CREAT, mode=0o644)
    mq.close()
    mq.unlink()
