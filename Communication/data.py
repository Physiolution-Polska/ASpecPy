import time
import pandas
import os.path
import numpy as np

DATA = {
        'black': 'black.csv',
        'clean': 'clean.csv',
        'analyte': 'analyte.csv',
        'absorbance': 'absorbance.csv'
        }


class Data():
    def __init__(self):
        self.type = None
        self.black = None
        self.clean = None
        self.analyte = None
        self.wavelength = None
        self._absorbrance = None
        self.c_double_array = None

    def write(self):
        """
        Function writes data value
        that defined in 'self.type' variable
        which depends on a 'sender' measure call
        parametr (black, clean, analyte)

        With 'analyte' parametr function will
        also calls an 'absorbance' function
        which is calculating the absorbance and
        writing it to the csv file.

        DB should be used instead of this.
        """
        data_frame = None

        if os.path.exists(DATA[self.type]):
            try:
                data_frame = pandas.read_csv(DATA[self.type])
            except pandas.errors.EmptyDataError:
                data_frame = pandas.DataFrame({'lambda': self.wavelength})
        else:
            data_frame = pandas.DataFrame({'lambda': self.wavelength})

        data = getattr(self, '_' + self.type)

        data_frame[int(time.time())] = pandas.DataFrame({'value': data})
        data_frame.to_csv(DATA[self.type], index=False)

        return True

    def absorbance(self):
        if (self.black is None or self.clean is None
                or self.analyte is None):
            return False
        with np.errstate(divide='ignore', invalid='ignore'):
            self.absorbanace = np.log10(np.divide(np.subtract(self.clean,
                                                              self.black),
                                                  np.subtract(self.analyte,
                                                              self.black)))
            self.absorbanace[self.absorbanace == np.inf] = 0
            self.absorbanace = np.nan_to_num(self.absorbanace)
        self.type = 'absorbance'
        self.write()
        self.type = 'analyte'
        return True
