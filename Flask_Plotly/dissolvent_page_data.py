import numpy as np


class Page_data():
    def __init__(self):
        self._plot = None
        self._time = None
        self._absorbance = None
        self._correction = None
        self._concentration = None
        self._dissolved = None

    def round(self):
        self._time = np.around(self._time.astype(np.float), decimals=3)
        self._absorbance = np.around(self._absorbance, decimals=3)
        self._correction = np.around(self._correction, decimals=3)
        self._concentration = np.around(self._concentration, decimals=3)
        self._dissolved = np.around(self._dissolved, decimals=3)
        return True
