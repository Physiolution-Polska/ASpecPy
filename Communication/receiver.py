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
            device = self.device.devType
            return getattr(self, device+'_'+func_name)()
        except AttributeError:
            return False

    @_if_debug(log)
    def avantes_empty(self):
        return None

    @_if_debug(log)
    def avantes_info(self):
        config = self.device.cfg.cfgAsDict()
        self.send(config)

    @_if_debug(log)
    def avantes_amount(self):
        devAnswer = self.device.cfg.setAmount(self.message['amount'])
        reply = self.buildReply(devAnswer)
        self.send(reply)

    @_if_debug(log)
    def avantes_update(self):
        devAnswer = self.device.update(self.message['mkeys'])
        reply = self.buildReply(devAnswer)
        self.send(reply)

    @_if_debug(log)
    def avantes_measure(self):
        # sending timeout for a 'sender'
        devAnswer = self.device.measurement_timeout()
        reply = self.buildReply(devAnswer)
        self.send(reply)

        # starting measurements
        devAnswer = self.device.measure(self.message['mtype'])
        reply = self.buildReply(devAnswer)
        self.send(reply)

    @_if_debug(log)
    def avantes_load(self):
        devAnswer = self.device.cfg.loadCfg(self.message['cfg'])
        reply = self.buildReply(devAnswer)
        self.send(reply)

    @_if_debug(log)
    def avantes_stop(self):
        devAnswer = self.device.stop()
        reply = self.buildReply(devAnswer)
        self.send(reply)

    @_if_debug(log)
    def avantes_close(self):
        reply = self.buildReply('Closing communication')
        self.send(reply)
        return False

    def buildReply(self, message):
        reply = {'reply':str(message)}
        return reply

    @_if_debug(log)
    def readQueue(self):
        while True:
            if self.receive(timeout=None):
                if 'type' in self.message.keys():
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
if mq_receiver.setRecvQueue(args.id):
    log.info('New queue created %s', args.id)
    mq_receiver.readQueue()
else:
    log.warning('Using old queue %s', args.id)
    mq_receiver.readQueue()
