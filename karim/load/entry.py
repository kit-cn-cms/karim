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

    def GetEntry(self, event, variables = None):
        if variables is None:
            variables = self.variables

        error = False
        if not self.config.base_selection(event):
            error = True
            data = np.zeros(shape = (1, len(variables)))
            data[:,:] = -99.
        else:
            data = np.zeros(shape = (1, len(variables)))
            idy = 0
            for i, v in enumerate(variables):
                # print(v)
                if "[" in v and "]" in v:
                    v, vidx = v.split("[")
                    vidx = int(vidx.replace("]",""))    
                    try:
                        data[:,idy] = getattr(event, v)[vidx]
                    except:
                        data[:,idy] = 0.
                else:
                    # print(getattr(event, v))
                    # data[:,idy] = getattr(event, v)
                    try:
                        data[:,idy] = getattr(event, v)
                    except:
                        data[:,idy] = 0
                idy += 1

        return data, error

