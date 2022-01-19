import sys
import os
import json
import numpy as np
import pandas as pd

class TestModel:
    def __init__(self):
        self.config = {}
        self.testVariables = [
            "nJets_SYS",
            "Lep_Pt[0]"
            ]

class Model:
    def __init__(self, inputPath):
        '''
        load dnn model with Keras
        '''
        self.modelPath = inputPath

        self.testModel = False
        if inputPath == "test":
            self.testModel = True
            self.model = TestModel()
            self.config = self.model.config
            return

        if os.path.exists("/".join([self.modelPath, "checkpoints"])):
            self.modelPath = "/".join([self.modelPath, "checkpoints"])
        # load config file
        configFile = self.modelPath+"/net_config.json"
        if not os.path.exists(configFile):
            sys.exit("could not find config file {}, cannot load DNN".format(configFile))

        with open(configFile) as f:
            self.config = f.read()
        self.config = json.loads(self.config)


        # load trained model
        checkpointPath = self.modelPath+"/trained_model.h5py"
        if not os.path.exists(checkpointPath):
            sys.exit("could not find trained model {}".format(checkpointPath))

        print("\nloading DNN model from {}\n".format(self.modelPath))
        try:
            from keras.models import load_model
            self.model = load_model(checkpointPath)
        except:
            from tensorflow.keras.models import load_model
            self.model = load_model(checkpointPath)
            
        self.model.summary()

    
    def setVariables(self):
        '''
        read list of variables used for DNN evaluation
        read norm table with mean and std.dev values for all of theses variables
        '''
        if self.testModel:
            self.variable_norms = None
            self.variables = self.model.testVariables
            return 

        # load variable normalization
        normFile = self.modelPath+"/variable_norm.csv"
        if not os.path.exists(normFile):
            sys.exit("could not find file with variable norms {}".format(normFile))
        
        self.variable_norms = pd.read_csv(normFile, index_col=0)
        print("\nvariable norms:")
        print(self.variable_norms)
        self.variables = list(self.variable_norms.index.values)

    def findBest(self, entry):
        '''
        evaluate DNN for all entries given
        
        output: index, value of best combination
        '''
        if self.testModel:
            bestIndex = np.random.randint(entry.shape[0])
            return bestIndex, np.random.random()

        matrix = entry[self.variables].values
        idx = 0
        for _, row in self.variable_norms.iterrows():
            matrix[:,idx]-=row["mu"]
            matrix[:,idx]/=row["std"] 
            idx+=1
        predictions = self.model.predict(matrix)
        bestIndex = np.argmax(predictions[:,0])
        return bestIndex, predictions[bestIndex][0]

    
    def evaluate(self, entry):
        '''
        evaluate dnn with inputs
        inputs are either ndarray of events already cut to the dnn input variables
        or dataframe with correct input variable column names
    
        output: dnn predictions, max value of prediction vectors
        '''
        if self.testModel:
            predictions = np.random.random(entry.shape[0])
            maxIndex = np.argmax(predictions, axis = 1)
            return predictions, maxIndex

        if not type(entry) == np.ndarray:
            matrix = entry[self.variables].values
        else:
            matrix = entry

        # norm variables
        idx=0
        for _, row in self.variable_norms.iterrows():
            matrix[:,idx]-=row["mu"]
            matrix[:,idx]/=row["std"] 
            idx+=1

        # predict
        predictions = self.model.predict(matrix)

        # get maximum index 
        maxIndex = np.argmax(predictions, axis = 1)
        return predictions, maxIndex

