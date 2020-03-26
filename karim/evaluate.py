import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load
from hypotheses import Hypotheses

def evaluate_model(filename, modelname, configpath, outpath, apply_selection = False, write_input_vars = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    # load the DNN model
    model = load.Model(modelname)

    model.setVariables()

    config = load.Config(configpath, "Evaluation")
    config.additional_variables += model.variables
    
    # open input file
    with load.InputFile(filename) as ntuple:

        # load hypothesis module
        entry_loader = Hypotheses(config)

        first = True
        fillIdx = 0
        # start loop over ntuple entries
        for i, event in enumerate(load.TreeIterator(ntuple)):
            entry, error = entry_loader.GetEntry(event, event.N_Jets)
            if first:
                # check if all variables for DNN evaluation are present in dataframe
                check_entry(entry, model.variables)

                # get list of all dataframe variables
                if write_input_vars:
                    outputVariables = entry.columns.values
                    idxBaseVars = len(outputVariables)
                else:
                    outputVariables = np.array([])
                    idxBaseVars = 0

                # append output values to columns
                for outVar in config.dnn_output_variables:
                    outputVariables = np.append(outputVariables, outVar)
                idxOutputVars = len(outputVariables)

                # append variables containing info about maximum dnn output node
                for outVar in config.dnn_predicted_class:
                    outputVariables = np.append(outputVariables, outVar)
                idxPredictedClass = len(outputVariables)

                # print variables
                for v in outputVariables:
                    print(v)
                
                # setup empty array for event data storage
                outputData = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))

                first = False
            if error:
                #print("selection not fulfulled")
                if not apply_selection:
                    outputData[fillIdx,:] = -1
                    fillIdx += 1
                continue
            else:
                # get dnn output
                dnnOutput, maxIndex = model.evaluate(entry)

                # fill output data array
                if write_input_vars:
                    outputData[fillIdx, :idxBaseVars] = entry.iloc[0].values

                # only one event evaluated at a time -> get zeroth element of output lists
                outputData[fillIdx, idxBaseVars:idxOutputVars] = dnnOutput[0]
                outputData[fillIdx, idxOutputVars:idxPredictedClass] = maxIndex[0]


                if fillIdx<=10:
                    print("=== testevent ===")
                    for name, value in zip(outputVariables, outputData[fillIdx]):
                        print(name, value)
                    print("================="+"\n\n")

                fillIdx += 1

    # cut outputData to filled length
    if apply_selection:
        print("events that fulfilled the selection: {}/{}".format(fillIdx, len(outputData)))
        outputData = outputData[:fillIdx]

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


