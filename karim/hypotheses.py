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
                config.template.replace("OBJECT",obj).replace("FEATURE", "idx"))

        # if available add additional objects
        for order in config.additional_objects:
            for feat in config.features:
                for obj in config.additional_objects[order]:
                    self.variables.append(
                        config.template.replace("OBJECT",obj).replace("FEATURE", feat))
            for obj in config.additional_objects[order]:
                self.variables.append(
                    config.template.replace("OBJECT",obj).replace("FEATURE", "idx"))
            
                

        self.nBaseVariables = len(self.variables)
        # add additional variables to variable list
        for av in config.additional_variables:
            self.variables.append(av)
        self.nAdditionalVariables = len(self.variables)

        self.hypothesisJets = len(config.objects)
        print("\nhypothesis requires {njets} jets\n".format(njets = self.hypothesisJets))

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

    def GetEntry(self, event, nJets):
        '''
        get dataframe with all permutations for a single event with nJets
        returns error = True if e.g. number of jets is too low

        output: DataFrame, error
        '''
        error = False
        if not self.config.base_selection(event) or nJets < self.hypothesisJets:
            error = True
            data = np.zeros(shape = (1, len(self.variables)))
            idy = 0
            for i, av in enumerate(self.config.additional_variables):
                if "[" in av and "]" in av:
                    av, avidx = av.split("[")
                    avidx = int(avidx.replace("]",""))
                    try:
                        data[:,idy+self.nBaseVariables] = getattr(event, av)[avidx]
                    except:
                        data[:,idy+self.nBaseVariables] = -99.
                else:
                    data[:,idy+self.nBaseVariables] = getattr(event, av)
                idy += 1
            
        else:
            if not self.permutations is None:
                # fill data matrix with permutations
                nJets = min(nJets, 10)
                data = np.zeros(shape = (len(self.permutations[nJets]), len(self.variables)))
            else:
                data = np.zeros(shape = (1, len(self.variables)))

            ordered_indices = {}
            used_indices = np.zeros(shape = (len(self.permutations[nJets]), self.hypothesisJets))
            assigned_indices = {}
            for order in self.config.additional_objects:
                print "order", order
                values = np.zeros(shape = nJets)
                variable = getattr(event, "Jet_{}".format((order.split("_"))[0]))
                parsed_req = (self.config.additional_objects[order][0]).split("_")
                cut = 0
                for idx in range(nJets):
                    if self.config.additional_objects[order][0].find("req") > 0:
                        if float(getattr(event, "Jet_{}".format(parsed_req[4]))[idx]) > float(parsed_req[6]):
                            values[idx] = variable[idx]
                        else:
                            values[idx] = -1337
                            cut += 1
                    else:
                        values[idx] = variable[idx]
                ordered_indices[order] = np.argsort(values)[::-1]
                print "cut", cut
                print "ordered_indices[order] bef", ordered_indices[order]
                if self.config.additional_objects[order][0].find("req") > 0:
                    ordered_indices[order] = (ordered_indices[order])[:-cut]
                print "ordered_indices[order] aft", ordered_indices[order]
                assigned_indices[order] = np.zeros(shape = 
                    (len(self.permutations[nJets]), len(self.config.additional_objects[order])))

            idy = 0
            for feat in self.config.features:
                variable = getattr(event, "Jet_{}".format(feat))
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
                for order in self.config.additional_objects:
                    for iobj in range(len(self.config.additional_objects[order])):
                        # if (iobj+1)+self.hypothesisJets > nJets:
                        if (iobj+1)+self.hypothesisJets > len(ordered_indices[order]): #length is shorter than nJets due to "req" option
                            assigned_indices[order][idx, iobj] = -1
                            continue

                        used_here = np.concatenate((used, assigned_indices[order][idx, :iobj]))
                        freeIndex = 0
                        while ordered_indices[order][freeIndex] in used_here:
                            freeIndex += 1
                        assigned_indices[order][idx, iobj] = ordered_indices[order][freeIndex]
                    

            # if available add additional objects
            for order in self.config.additional_objects:
                for feat in self.config.features:
                    variable = getattr(event, "Jet_{}".format(feat))

                    for i in range(len(self.config.additional_objects[order])):
                        for idx in range(len(self.permutations[nJets])):
                            assigned_index = int(assigned_indices[order][idx, i])
                            if assigned_index == -1:
                                data[idx,idy] = -99.
                            else:
                                data[idx,idy] = variable[assigned_index]
                        idy += 1

                for i in range(len(self.config.additional_objects[order])):
                    for idx in range(len(self.permutations[nJets])):
                        data[idx, idy] = assigned_indices[order][idx, i]
                    idy += 1


            # add additional variables
            for i, av in enumerate(self.config.additional_variables):
                if "[" in av and "]" in av:
                    av, avidx = av.split("[")
                    avidx = int(avidx.replace("]",""))
                    data[:,idy] = getattr(event, av)[avidx]
                else:
                    data[:,idy] = getattr(event, av)
                idy += 1

        df = pd.DataFrame(data, columns = self.variables)
        return self.config.calculate_variables(df), error

