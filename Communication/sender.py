import os
from debug import log
from mqueues import MQueues
from sender_parser import SenderParser

class Sender(MQueues):
    def __init__(self, parser, timeout=5):
        super().__init__()
        self.timeout = timeout
        """
        Proceeding parameters based on device type
        """
        try:
            #calling appropriate function with necessary params
            #parser contains all params
            getattr(self, parser.dev)(parser)
        except AttributeError:
            exit(-1)

        
    def switch_case(self, func_name):
        """
        If message should be proceed in a specified way
        the function should be defined for this.
        Otherwise:
            send -> receive
            wait for response
            receiv <- send
            return response
        """
        device = self.message['dev']
        if not getattr(self, device+'_'+func_name, lambda: False)():
            if self.send(self.message):
                self.receive()

    def avantes_info(self):
        """
        Sending message to receiver
        and expecting a dict, as an answer,
        with all parameters from the device
        """
        #receiving dict with keys (maybe all keys)
        if self.send(self.message):
            if self.receive():
                return self.answer
        return None

    def avantes_measure(self):
        try:
            self.send(self.message)
            # receiving timeout
            _timeout = self.receive()

            # posix timeout should be grater then 1
            if _timeout < 1:
                _timeout = 2 
            else:
                _timeout *= 2
            return self.receive(_timeout)

        except posix.BusyError:
            return False

        return False

    def avantes(self, args):
        """
        Function parses arguments and building message
        specified for 'avantes' spectrometers
        """
        self.message['response'] = '/'+str(os.getpid())
        self.message['type'] = args.type
        self.message['dev'] = args.dev
        try:
            self.message['mkeys'] = args.values
        except AttributeError:
            self.message['mkeys'] = None

        try:
            self.message['cfg'] = args.cfg
        except AttributeError:
            self.message['cfg'] = None

        try:
            self.message['mtype'] = args.store
        except AttributeError:
            self.message['mtype'] = 'black'

        try:
            # {(0,65535], -1}
            if ((args.amount > 0) and (args.amount <= 0xffff) or
                  (args.amount == -1)):
                self.message['amount'] = args.amount
            else:
                self.message['amount'] = 1
        except AttributeError:
            pass

args = SenderParser().getArgs()
sender = Sender(args)

if __debug__:
    log.info('Sender openning queues')
    if sender.setRecvQueue():
        if sender.setSendQueue('recv'):
            print(sender.queues)
    if ((sender.queues[0][1] is not None) and
            (sender.queues[1][1] is not None)):
        sender.switch_case(sender.message['type'])
    else:
        log.error('Error occur when trying to open queues')
        sender.closeRecvQueue()
        exit(-2)
else:
    if sender.setRecvQueue():
        if sender.setSendQueue():
            if ((sender.queues[0][1] is not None) and
                    (sender.queues[1][1] is not None)):
                sender.switch_case()
            else:
                sender.closeRecvQueue()
                exit(-2)

sender.closeRecvQueue()
