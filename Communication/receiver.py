import device as dev
import posix_ipc as posix
from mqueues import MQueues
from debug import _if_debug, log
from receiver_parser import ReceiverParser


class Receiver(MQueues):
    def __init__(self, args):
        super().__init__()
        self.device = dev.Device(args.dev, args.cfg)

        if not self.device.cfg:
            if __debug__:
                log.error('Config was not loaded')
            exit(-1)

    def switch_case(self, func_name):
        try:
            device = self.device.dev_type
            return getattr(self, device+'_'+func_name)()
        except AttributeError:
            return False

    @_if_debug(log)
    def avantes_empty(self):
        return True

    @_if_debug(log)
    def avantes_info(self):
        config = self.device.cfg.cfgAsDict()
        self.send(config)

    @_if_debug(log)
    def avantes_amount(self):
        answer = self.device.cfg.setAmount(self.message['amount'])
        self.send(answer)

    @_if_debug(log)
    def avantes_update(self):
        answer = self.device.update(self.message['mkeys'])
        self.send(self.answer)

    @_if_debug(log)
    def avantes_measure(self):
        # sending timeout for a 'sender'
        answer = self.device.measurement_timeout()
        self.send(answer)

        # starting measurements
        answer = self.device.measure(self.message['mtype'])
        self.send(answer)

    @_if_debug(log)
    def avantes_load(self):
        answer = self.device.cfg.load_cfg(self.message['cfg'])
        self.send(self.answer)

    @_if_debug(log)
    def avantes_stop(self):
        answer = self.device.stop()
        self.send(answer)

    @_if_debug(log)
    def avantes_close(self):
        return False

    @_if_debug(log)
    def readQueue(self):
        while True:
            if self.receive(timeout=0):
                switch = self.switch_case(self.message['type'])
                if switch == False:
                    if __debug__:
                        log.warning('Exiting')
                    break
        # release communication with the device
        if __debug__:
            log.warning('Removing the device')
        self.closeRecvQueue()
        self.device.release()

args = ReceiverParser().getArgs()
mq_receiver = Receiver(args)
if mq_receiver.setRecvQueue():
    mq_receiver.readQueue()
    log.info('New queue created %s', args.id)
else:
    log.warning('Using old queue %s', args.id)
    mq_receiver.readQueue()
