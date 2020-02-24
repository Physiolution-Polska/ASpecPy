"""
Module contains configuration 
for parsing arguments for 'Receiver' object
"""
import argparse

class ReceiverParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        parser.add_argument('--id', help='Device id',
                            required=True)

        parser.add_argument('--dev', help='Device type',
                            choices=['avantes', 'empty'], required=False,
                            default='avantes')

        parser.add_argument('--cfg', help='Device type',
                            choices=['user', 'default'], required=False,
                            default='default')

    def getArgs(self):
        return self.parser.parse_args()

