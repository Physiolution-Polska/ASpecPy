import logging
import logging.config
"""
Logger config filename
"""
filename = 'avantes_log.conf'
logging.config.fileConfig(fname=filename)
log = logging.getLogger()
"""
'Debug' decorator for function call
"""
def _if_debug(logger=None):
    def debug(func):
        def wrapper(*args, **kwargs):
            if __debug__:
                logger.info('Called function: %s with args: %s',
                            func.__name__,
                            [arg for arg in args[-1:]])
            return func(*args, **kwargs)
        return wrapper
    return debug
