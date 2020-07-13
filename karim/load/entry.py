import itertools
import pandas as pd
import numpy as np
from array import array

class Entry:
    maxJets = 10
    def __init__(self, config):
        # generate a variable list that needs to be filled from ntuple information
        self.variables = []
        # add additional variables to variable list
        for av in config.additional_variables:
            self.variables.append(av)

        # save config
        self.config = config

    def GetEntry(self, event):
        error = False
        if not self.config.base_selection(event):
            error = True
            data = np.zeros(shape = (1, len(self.variables)))
            data[:,:] = -99.
        else:
            data = np.zeros(shape = (1, len(self.variables)))
            idy = 0
            for i, av in enumerate(self.config.additional_variables):
                if "[" in av and "]" in av:
                    av, avidx = av.split("[")
                    avidx = int(avidx.replace("]",""))
                    data[:,idy] = getattr(event, av)[avidx]
                else:
                    data[:,idy] = getattr(event, av)
                idy += 1

        return data, error

