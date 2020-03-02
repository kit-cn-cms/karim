import itertools
import pandas as pd
import numpy as np
from array import array

class Hypotheses:
    maxJets = 10
    def __init__(self, config):
        '''
        initialize config settings and variable lists
        '''
        if config.get_Mode() != None:
            self.mode = config.get_Mode()
            print("Running Hypotheses in {} mode".format(self.mode))
       
        else:
            print("Hypothesis Mode not specified in config doing default")
            self.mode = "PERMUTATIONS"

        self.naming   = config.get_reco_naming()
        self.objects  = config.get_objects()
        self.features = config.get_features()
        print("list of objects for reconstruction: ")
        print(self.objects)
        print("list of features for reconstruction: ")
        print(self.features)
        self.template = "{name}_OBJECT_FEATURE".format(name = self.naming)
        print("naming template for variables:" )
        print(self.template)
        self.base_selection = config.base_selection
        print("base selection {}".format(self.base_selection))

        # load function to calculate variables for all hypotheses
        self.calculate_variables = config.calculate_variables


        # generate a variable list that needs to be filled from ntuple information
        self.variables = []
        for feat in self.features:
            for obj in self.objects:
                self.variables.append(
                    self.template.replace("OBJECT",obj).replace("FEATURE", feat))

        # add jet indices for all reconstructable objects
        for obj in self.objects:
            self.variables.append(
                self.template.replace("OBJECT",obj).replace("FEATURE", "idx"))

        self.baseVariables = len(self.variables)
        # add additional variables to variable list
        self.additional_variables = config.get_additional_variables()
        #self.additional_variables+= ["Evt_ID", "Evt_Lumi", "Evt_Run"]
        self.additional_variables = list(set(self.additional_variables))
        for av in self.additional_variables:
            self.variables.append(av)

        self.hypothesisJets = len(self.objects)
        print("\nhypothesis requires {njets} jets\n".format(njets = self.hypothesisJets))

    def set_memDF(self, memDF_):
        self.memFile = memDF_

    def set_systematic(self, syst):
        self.systematic = syst

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

    def GetPermutations(self, event, nJets):
        '''
        get dataframe with all permutations for a single event with nJets
        returns error = True if e.g. number of jets is too low

        output: DataFrame, error
        '''
        error = False
        if not self.base_selection(event) or nJets < self.hypothesisJets:
            error = True
            data = np.zeros(shape = (1, len(self.variables)))
            data[:,:] = -99.
        else:
            # fill data matrix with permutations
            nJets = min(nJets, 10)
            data = np.zeros(shape = (len(self.permutations[nJets]), len(self.variables)))
            idy = 0
            for feat in self.features:
                variable = getattr(event, "Jet_{}".format(feat))
                for i, obj in enumerate(self.objects):
                    for idx, p in enumerate(self.permutations[nJets]):
                        data[idx,idy] = variable[p[i]]
                    idy += 1
            for i, obj in enumerate(self.objects):
                for idx, p in enumerate(self.permutations[nJets]):
                    data[idx, idy] = p[i]
                idy += 1

            for i, av in enumerate(self.additional_variables):
                if "[" in av and "]" in av:
                    av, avidx = av.split("[")
                    avidx = int(avidx.replace("]",""))
                    data[:,idy] = getattr(event, av)[avidx]
                else:
                    data[:,idy] = getattr(event, av)
                idy += 1

        df = pd.DataFrame(data, columns = self.variables)
        return self.calculate_variables(df), error

    def GetMEM(self, event):
        '''
        get dataframe with MEMvalue for a single event
        returns error = True if e.g. no MEM entry is found

        output: DataFrame, error
        '''
        error = False
        data = np.zeros(shape = (1, len(self.variables)))

        idy = 0
        # for feat in self.features:
        #     variable = getattr(event, "Jet_{}".format(feat))
        #     for i, obj in enumerate(self.objects):
        #         for idx, p in enumerate(self.permutations[nJets]):
        #             data[idx,idy] = variable[p[i]]
        #         idy += 1
        # for i, obj in enumerate(self.objects):
        #     for idx, p in enumerate(self.permutations[nJets]):
        #         data[idx, idy] = p[i]
        #     idy += 1

        for i, av in enumerate(self.additional_variables):
            if "[" in av and "]" in av:
                av, avidx = av.split("[")
                avidx = int(avidx.replace("]",""))
                data[:,idy] = getattr(event, av)[avidx]
            else:
                data[:,idy] = getattr(event, av)
            idy += 1
        # print(data)
        df = pd.DataFrame(data, columns = self.variables)
        # print(df.head)
        self.loadMEM(df)
        # return self.calculate_variables(df), error
        return df, error

    def loadMEM(self, df):
        if self.systematic == "nominal":
            var = "mem_p"
        else:
            var = "mem_"+self.systematic+"_p"
        filterDF = self.memFile[(self.memFile['event'] == df["Evt_ID"].values[0]) & (self.memFile['run'] == df["Evt_Run"].values[0]) & (self.memFile['lumi'] == df["Evt_Lumi"].values[0])]
        # print(filterDF[var].values)
        try:
            df["memDBp"] = filterDF[var].values[0]
        except:
            df["memDBp"] = -1