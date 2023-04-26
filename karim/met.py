import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load

def evaluate_model(filename, modelconfigpath, configpath, friendTrees, outpath, apply_selection = False, write_input_vars = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    modelconfig = load.ModelConfig(modelconfigpath)
    
    model_variables = modelconfig.getAllVariables()

    config = load.Config(configpath, friendTrees, "Evaluation")
    additional_variables = []
    for v in config.additional_variables:
        if not v in model_variables:
            additional_variables.append(v)
    config.additional_variables = additional_variables

    # get information about variables that should be written into new friendtrees
    idxCommonVars = len(additional_variables)
    commonVars = list(additional_variables)

    additional_variables += model_variables
    modelconfig.setVariableIndices(additional_variables)    

    # open input file
    with load.InputFile(filename, config.getFriendTrees(filename)) as ntuple:

        # load hypothesis module
        entry_loader = load.Entry(config)

        first = True
        fillIdx = 0
        # start loop over ntuple entries
        for i, event in enumerate(load.TreeIterator(ntuple)):
            entry, error = entry_loader.GetEntry(event)
            if first:
                # get list of all dataframe variables

                # variables that are to be written to output file
                outputVariables = np.array(commonVars)

                # if 'write_input_vars' is activated also write dnn inputs to new file
                if write_input_vars:
                    for outVar in model_variables:
                        outputVariables = np.append(outputVariables, outVar)
                idxBaseVars = len(outputVariables)

                # append output values of dnn
                outputVariables = modelconfig.setOutputVariables(outputVariables)

                # remove brakets
                outputVariables = [v.replace("[","_").replace("]","") for v in outputVariables]
                    
                # print variables
                print("variables to be written to output file:")
                for v in outputVariables:
                    print(v)
                print("=======================")
                
                # setup empty array for event data storage
                outputData = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))

                # setup input array for dnn evaluation
                modelconfig.setInputData(ntuple.GetEntries()) 

                first = False

            if error:
                # if selection is not fulfilled
                # fill default values of -1 into entry
                if not apply_selection:
                    outputData[fillIdx,:] = -1
                    modelconfig.setEmptyEntry(fillIdx)
                    fillIdx += 1
                continue

            # fill output data array
            
            # common variables
            outputData[fillIdx, :idxCommonVars] = entry[0, :idxCommonVars]

            # dnn input variables
            if write_input_vars:
                outputData[fillIdx, idxCommonVars:idxBaseVars] = entry[0, idxCommonVars:idxBaseVars]

            # dnn input variables into input array
            modelconfig.fillInputData(fillIdx, entry, event)
            fillIdx+=1

    # cut outputData to filled length
    if apply_selection:
        print("events that fulfilled the selection: {}/{}".format(fillIdx, len(outputData)))
        outputData = outputData[:fillIdx]
        modelconfig.removeTrailingEntries(fillIdx)

    # get dnn output
    for dnnSet in modelconfig.dnnsets:
        dnnOutput, maxIndex = dnnSet.evaluate(len(outputData))
    
        # fill dnn output
        outputData[:, dnnSet.idxOutLo:dnnSet.idxOutHi] = dnnOutput
        # fill predicted index
        outputData[:, dnnSet.idxOutHi:dnnSet.idxPrediction] = maxIndex.reshape(len(outputData), -1)
    
    # test print of outputs
    for i in range(10):
        print("=== testevent ===")
        for name, value in zip(outputVariables, outputData[i]):
            print(name, value)
        print("================="+"\n\n")

    print("\nsaving information ...")
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

