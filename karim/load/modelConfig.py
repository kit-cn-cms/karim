import yaml
import numpy as np

from karim.load.model import Model as ModelBase

class ModelConfig:
    def __init__(self, modelconfigpath):
        with open(modelconfigpath, "r") as f:
            data = yaml.safe_load(f)


        # load all DNN sets
        self.dnnsets = []
        for setkey in data["sets"]:
            dnnset = data["sets"][setkey]
            print("reading information for DNN set '{}'".format(setkey))
            self.dnnsets.append(
                dnnSet(setkey, dnnset))
                
    def getAllVariables(self):
        '''
        loop over all sets and all dnns and gather the input variables
        '''
        variables = []
        for dnnset in self.dnnsets:
            variables += dnnset.getAllVariables()
        variables = list(set(variables))

        self.variables = variables
        print("evaluation of DNNs requires {} variables in total".format(len(self.variables)))
        return variables

    def setVariableIndices(self, all_variables):
        '''
        save the indices of these variables per dnn
        '''
        for dnnset in self.dnnsets:
            dnnset.setVariableIndices(all_variables)
        
    def setOutputVariables(self, output_variables):
        '''
        add output nodes to variable list for root file creation
        '''
        for dnnset in self.dnnsets:
            output_variables = dnnset.setOutputVariables(output_variables)
        return output_variables
   
    def setInputData(self, n_entries):
        '''
        generate empty matrix for input features
        '''
        for dnnset in self.dnnsets:
            dnnset.setInputData(n_entries)

    def setEmptyEntry(self, fillIdx):
        '''
        generate entries filled with -1 if base selection is not fulfilled
        '''
        for dnnset in self.dnnsets:
            dnnset.setEmptyEntry(fillIdx)

    def fillInputData(self, fillIdx, entry, event):
        '''
        add input data to saved arrays and figure out of event would be selected   
        '''
        for dnnset in self.dnnsets:
            dnnset.fillInputData(fillIdx, entry, event)

    def removeTrailingEntries(self, fillIdx):
        '''
        in case the apply_selection option is avtivated
        remove empty entries at end of pregenerated arrays
        '''
        for dnnset in self.dnnsets:
            dnnset.removeTrailingEntries(fillIdx)

class dnnSet:
    def __init__(self, key, config):
        self.key = key
        self.nodes = config["nodes"]
        print("dnns have output nodes labelled: \n{}".format("\n".join(self.nodes)))
        
        self.name = config["name"]
        print("output name is {}".format(self.name))

        self.prediction_name = config["predicted_class"]
        print("predicted class name is {}".format(self.prediction_name))

        self.models = {}
        for modelkey in config["models"]:
            self.models[modelkey] = config["models"][modelkey]
            self.models[modelkey]["model"] = Model(self.models[modelkey]["path"])

            self.models[modelkey]["model"].setVariables()
        
            self.models[modelkey]["model"].setSelection(
                self.models[modelkey]["selection"])


    def getAllVariables(self):
        variables = []
        for modelkey in self.models:
            variables += self.models[modelkey]["model"].variables
        return variables

    def setVariableIndices(self, all_variables):
        for modelkey in self.models:
            self.models[modelkey]["model"].setVariableIndices(all_variables)

    def setOutputVariables(self, output_variables):
        self.idxOutLo = len(output_variables)
        for idx, n in enumerate(self.nodes):
            output_variables = np.append(output_variables, 
                self.name.replace("$NODE", n).replace("$IDX", str(idx)))
        self.idxOutHi = len(output_variables)

        if not self.prediction_name is None:
            output_variables = np.append(output_variables, self.prediction_name)
        self.idxPrediction = len(output_variables)
        return output_variables

    def setInputData(self, n_entries):
        for modelkey in self.models:
            self.models[modelkey]["model"].setInputData(n_entries)

    def setEmptyEntry(self, fillIdx):
        for modelkey in self.models:
            self.models[modelkey]["model"].setEmptyEntry(fillIdx)

    def fillInputData(self, fillIdx, entry, event):
        for modelkey in self.models:
            self.models[modelkey]["model"].fillInputData(fillIdx, entry, event)

    def removeTrailingEntries(self, fillIdx):
        for modelkey in self.models:
            self.models[modelkey]["model"].removeTrailingEntries(fillIdx)


    def evaluate(self, n_entries):
        dnnOutputs = np.zeros(shape = (n_entries, len(self.nodes)))
        maxIndices = np.zeros(shape = (n_entries, 1))
        for modelkey in self.models:
            print("-----------------------------")
            print("evaluating model - {}/{}".format(self.key, modelkey))
            dnnOutput, maxIndex = self.models[modelkey]["model"].evaluate(
                self.models[modelkey]["model"].inputData[:,1:])
            print("filling outputs that fulfill the selection...")
            filled = 0
            for idx in range(len(dnnOutput)):
                if self.models[modelkey]["model"].inputData[idx,0] == 1:
                    dnnOutputs[idx] = dnnOutput[idx]
                    maxIndices[idx] = maxIndex[idx]
                    filled+=1
                # also fill empty entries
                if self.models[modelkey]["model"].inputData[idx,0] == -1:
                    dnnOutputs[idx, :] = -1
                    maxIndices[idx] = -1
            print("entries filled: {}/{}".format(filled, len(dnnOutputs)))
        

        return dnnOutputs, maxIndices
            

        
class Model(ModelBase):
    def setSelection(self, selection):
        self.selection = selection

    def setVariableIndices(self, all_variables):
        self.indices = []
        for variable in self.variables:
            self.indices.append(all_variables.index(variable))
        print("variable indices:")
        for v, i in zip(self.variables, self.indices):
            print(v, i)

    def setInputData(self, n_entries):
        '''
        the first columns is reserved for whether or not an event fulfills the selection
        '''
        self.inputData = np.zeros(shape = (n_entries, len(self.variables)+1))
        print(self.inputData.shape)

    def setEmptyEntry(self, fillIdx):
        self.inputData[fillIdx, :] = -1

    def fillInputData(self, fillIdx, entry, event):
        '''
        the first column should be filled with 1 if the event is selected by the network
        '''
        self.inputData[fillIdx, 0] = 1 if eval(self.selection) else 0

        if eval(self.selection):
            self.inputData[fillIdx, 1:] = entry[0, self.indices]
            if fillIdx <= 10:
                print("=== test input ===")
                for name, value in zip(self.variables, self.inputData[fillIdx, 1:]):
                    print(name, value)
                print("==================\n\n")

    def removeTrailingEntries(self, fillIdx):
        self.inputData = self.inputData[:fillIdx]

    
