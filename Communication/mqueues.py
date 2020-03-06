import os
import pickle
import posix_ipc as posix
from debug import log

class MQueues():
    def __init__(self):
        """
        self.queues[0] - for receiving messages
        self.queues[1] - for sending message
        self.queues[x][0] - queue name
        self.queues[x][1] - queue obj
        """
        self.queues = {
                       0:[None, None],
                       1:[None, None]
                       }

        self.answer = {}
        self.message = {}

    def setRecvQueue(self, qname=None):
        if qname is not None:
            qname = '/'+qname
        else:
            qname = '/'+str(os.getpid())

        """
        Initialization of a queue
        for receiving messages
        """
        try:
            self.queues[0][0] = qname
            self.queues[0][1] = posix.MessageQueue(self.queues[0][0],
                                                   posix.O_CREX,
                                                   mode=0o644)
            return True
        except posix.ExistentialError:
            self.queues[0][1] = posix.MessageQueue(qname)
            """
            Reopen queue
            """
            if self.closeRecvQueue():
                self.setRecvQueue()
            return False

    def closeRecvQueue(self):
        """
        Allowed to close only queue
        for receiving messages
        """
        if self.queues[0][1] is not None:
            self.queues[0][1].close()
            self.queues[0][1].unlink()
            return True
        return False

    def setSendQueue(self, qname=None):
        """
        Name of a queue, where all messages
        will be sent should be specified in first use

        After that, the queue will be set to appropriate one
        which comes in 'response' key in message dict
        Might be changed with appopriate function call
        """
        if qname is not None:
            qname = '/'+qname
            self.queues[1][0] = qname
        try:
            if ((qname is None) and
                    (self.queues[1][0]) is not None):
                qname = self.queues[1][0]
            """
            Setting receiver message queue if exist
            in order to send messages
            """
            self.queues[1][1] = posix.MessageQueue(qname)
            return True

        except ValueError as error:
            if __debug__:
                log.error(error)
                log.error('Queue name should be specified')
            return False

        except posix.ExistentialError:
            if __debug__:
                log.error('Cannot open queue %s', qname)
            return False
        return False


    def send(self, msg, timeout=5):
        """
        Sending message synchroniously
        to a queue for sending mqueue
        """
        if isinstance(self.queues[1][1], posix.MessageQueue):
            try:
                self.queues[1][1].send(pickle.dumps(msg), timeout=timeout)
                return True
            except posix.BusyError:
                return False
        return False

    def receive(self, timeout=5):
        try:
            # loading message from queue
            self.message = pickle.loads(self.queues[0][1].receive(timeout=timeout)[0])
            """
            Setting name of a queue in order
            to send a response
            """
            if 'response' in self.message.keys():
                self.queues[1][0] = self.message['response']
                self.setSendQueue()
            return True
        except posix.BusyError:
            if __debug__:
                log.error('Timeout occur while receiving message')
            return False

