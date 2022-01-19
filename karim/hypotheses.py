import itertools
import pandas as pd
import numpy as np
from array import array

class Hypotheses:
    maxJets = 10
    def __init__(self, config):
        # generate a variable list that needs to be filled from ntuple information
        self.variables = []
        for feat in config.features:
            for obj in config.objects:
                self.variables.append(
                    config.template.replace("OBJECT",obj).replace("FEATURE", feat))

        # add jet indices for all reconstructable objects
        for obj in config.objects:
            self.variables.append(
                config.template.replace("OBJECT",obj).replace("FEATURE", config.jetColl+"idx"))

        self.nBaseVariables = len(self.variables)
        # add additional variables to variable list
        for av in config.additional_variables:
            self.variables.append(av)
        self.nAdditionalVariables = len(self.variables)

        self.hypothesisJets = len(config.objects)
        print("\nhypothesis requires {njets} jets".format(njets = self.hypothesisJets))
        print("The input jet collection is defined as {}".format(config.jetColl))

        print("the following variables are written into the hypotheses:")
        for v in self.variables: print(v)

        # save config
        self.config = config
        self.permutations = None

    def initPermutations(self):
        '''
        save permutations in a dictionary so is doesnt have to be created for every event
        all permutations for njets = [min required - max jets] are created
        '''
        self.permutations = {}
        for nJets in range(self.hypothesisJets,self.maxJets+1):
            self.permutations[nJets] = list(
                itertools.permutations(range(0,nJets), r = self.hypothesisJets)
                )
        print("\npermutation configurations initialized.")
        print("maximum number of jets set to {}\n".format(self.maxJets))

    def GetEntry(self, event, jec = "nom"):
        '''
        get dataframe with all permutations for a single event with nJets
        returns error = True if e.g. number of jets is too low

        output: DataFrame, error
        '''
        nJets = getattr(event, self.config.jetLength.replace("SYS", jec))
        error = False
        if not self.config.base_selection(event, jec) or nJets < self.hypothesisJets:
            error = True
            data = np.zeros(shape = (1, len(self.variables)))
            idy = 0
            for i, av in enumerate(self.config.additional_variables):
                if "[" in av and "]" in av:
                    av, avidx = av.split("[")
                    avidx = int(avidx.replace("]",""))
                    try:
                        data[:,idy+self.nBaseVariables] = getattr(event, av.replace("SYS",jec))[avidx]
                    except:
                        data[:,idy+self.nBaseVariables] = -99.
                else:
                    data[:,idy+self.nBaseVariables] = getattr(event, av.replace("SYS",jec))
                idy += 1
            
        else:
            if not self.permutations is None:
                # fill data matrix with permutations
                nJets = min(nJets, 20)
                data = np.zeros(shape = (len(self.permutations[nJets]), len(self.variables)))
            else:
                data = np.zeros(shape = (1, len(self.variables)))

            ordered_indices = {}
            used_indices = np.zeros(shape = (len(self.permutations[nJets]), self.hypothesisJets))
            assigned_indices = {}

            idy = 0
            for feat in self.config.features:
                variable = getattr(event, self.config.jetColl+"_"+feat.replace("SYS",jec))
                for i, obj in enumerate(self.config.objects):
                    for idx, p in enumerate(self.permutations[nJets]):
                        data[idx,idy] = variable[p[i]]
                    idy += 1
            idz = 0
            for i, obj in enumerate(self.config.objects):
                for idx, p in enumerate(self.permutations[nJets]):
                    data[idx, idy] = p[i]
                    used_indices[idx, idz] = p[i]
                idz += 1
                idy += 1
            
            # figure out indices of additional object information
            for idx in range(len(self.permutations[nJets])):
                used = used_indices[idx]

            # add additional variables
            for i, av in enumerate(self.config.additional_variables):
                if "[" in av and "]" in av:
                    av, avidx = av.split("[")
                    avidx = int(avidx.replace("]",""))
                    try:
                        data[:,idy] = getattr(event, av.replace("SYS",jec))[avidx]
                    except:
                        if len(getattr(event, av.replace("SYS",jec))) <= avidx:
                            print("index {} of {} too high, filling dummy".format(avidx, av))
                            data[:,idy] = -999.
                        else:
                            print("cannot access {} at index {}".format(getattr(event, av.replace("SYS",jec)), avidx))
                            exit()
                else:
                    data[:,idy] = getattr(event, av.replace("SYS",jec))
                idy += 1

        df = pd.DataFrame(data, columns = self.variables)
        return self.config.calculate_variables(df), error

