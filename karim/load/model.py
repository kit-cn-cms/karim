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

        # load trained model
        checkpointPath = self.modelPath

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

    def findBest(self, data):
        '''
        evaluate DNN for all entries given
        
        output: node index of highest output value
        '''

        if self.testModel:
            predictions = np.random.random(15)
            bestIndex = np.argmax(predictions)
            return bestIndex, predictions[bestIndex]

        predictions = self.model.predict(data)[0]
        bestIndex = np.argmax(predictions)
        return bestIndex, predictions[bestIndex]
