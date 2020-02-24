"""
Module contains configuration 
for parsing arguments for 'Sender' object
"""
import argparse

class SenderParser():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.subparser = self.parser.add_subparsers(help='Allowed commands',
                                                    dest='type')

        self.messages()
        self.default_config()
        self.update_params()
        self.measurements()
        self.amount_of_meas()
        self.device()

    def messages(self):
        self.parser.add_argument('--type', help='Message type',
                                 choices=['info', 'close', 'stop', 'wlodek'],
                                 required=False, default='empty')

    def default_config(self):
        config = self.subparser.add_parser('load', help='Device configuration file')
        config.add_argument('--cfg', help='Device config',
                            choices=['user', 'default'], required=False,
                            default='default')
    def update_params(self):
        update = self.subparser.add_parser('update', help='Configuration update')
        update.add_argument('--values', help="1. Integration time\n\
                                   2. Nr of averages", nargs=2, type=float,
                                   required=False)

    def measurements(self):
        measure = self.subparser.add_parser('measure', help='Measurement type')
        measure.add_argument('--store', help='What to measure',
                             choices=['black', 'clean', 'analyte'],
                             required=False)

    def amount_of_meas(self):
        amount = self.subparser.add_parser('amount', help='Amount of measurements')
        amount.add_argument('--amount', help='Amount of measurements',
                            type=int, required=False)
    def device(self):
        self.parser.add_argument('--dev', help='Device type',
                                 choices=['avantes'], required=False,
                                 default='avantes')
        """
        Device message queue based on it's 'id' - unique number
        """
        self.parser.add_argument('--id', help='Device id',
                                 required=True)

    def getArgs(self):
        return self.parser.parse_args()
