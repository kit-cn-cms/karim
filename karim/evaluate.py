import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load
from hypotheses import Hypotheses

def evaluate_model(filename, modelname, configpath, outpath):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    # load the DNN model
    model = load.Model(modelname)
    
    # set variables needed for dnn training
    model.setVariables()

    # load config module
    dirname, basename = os.path.split(configpath)
    sys.path.append(dirname)
    config_name = os.path.splitext(basename)[0]
    config = importlib.import_module(config_name)
    print("\nimporting config:\n{}\n".format(configpath))

    # open input file
    with load.InputFile(filename) as ntuple:
    
        # load hypotheses module
        hypotheses = Hypotheses(config)

        # initialize hypotheses combinatorics
        hypotheses.initPermutations()

        first = True
        # start loop over ntuple entries
        for i, (entry, error) in enumerate(load.TreeIterator(ntuple, hypotheses)):
            if first:
                # check if all variables for DNN evaluation are present in dataframe
                check_entry(entry, model.variables)

                # get list of all dataframe variables
                outputVariables = entry.columns.values
                # append output value to columns
                outputVariables = np.append(outputVariables, config.get_reco_naming()+"_DNNOutput")
                outputVariables = np.append(outputVariables, config.get_reco_naming()+"_squaredDNNOutput")
                outputVariables = np.append(outputVariables, config.get_reco_naming()+"_transformedDNNOutput")
                for v in outputVariables:
                    print(v)
                
                # setup empty array for event data storage
                outputData = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))

                first = False

            if error:
                print("hypothesis not viable")
                # for some reason no hypotheses are viable
                #   e.g. not enough jets
                outputData[i,:-3] = entry.iloc[0].values
                # fill dummy output values of DNN
                outputData[i, -3] = -1.
                outputData[i, -2] = -99.
                outputData[i, -1] = -99.
            else:
                # get best permutation
                bestIndex, outputValue = model.findBest(entry)
                # fill output data array
                outputData[i,:-3] = entry.iloc[bestIndex].values
                # fill output values of DNN
                outputData[i, -3] = outputValue
                outputData[i, -2] = outputValue**2
                outputData[i, -1] = np.log(outputValue/(1.-outputValue))
                
            if i<=10:
                print("=== testevent ===")
                for name, value in zip(outputVariables, outputData[i]):
                    print(name, value)
                print("================="+"\n\n")

    # save information as h5 file
    df = pd.DataFrame(outputData, columns = outputVariables)
    df.to_hdf(outpath.replace(".root",".h5"), key = "data", mode = "w")
    del df            

    # open output root file
    with load.OutputFile(outpath) as outfile:
        # initialize branches
        outfile.SetBranches(outputVariables)
        # loop over events and fill tree
        for event in outputData:
            outfile.FillTree(event)
    


def check_entry(entry, variables):
    '''
    check if all variables needed for the DNN evaluation is found in the generated dataframe
    '''
    if set(variables).issubset(entry.columns):
        print("all variables found in dataframe for DNN evaluation")
    else:
        print("some variables are missing in dataframe:")
        available = entry.columns.values
        for v in variables:
            if v not in available:
                print("{var} missing".format(var = v))
        exit()



