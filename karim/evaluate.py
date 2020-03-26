import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load

def evaluate_model(filename, modelname, configpath, outpath, apply_selection = False, write_input_vars = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    # load the DNN model
    model = load.Model(modelname)

    model.setVariables()

    config = load.Config(configpath, "Evaluation")
    
    # get information about variables that should be written into new friendtrees
    idxCommonVars = len(config.additional_variables)
    commonVars = list(config.additional_variables)

    config.additional_variables += model.variables
    
    # open input file
    with load.InputFile(filename) as ntuple:

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
                    for outVar in model.variables:
                        outputVariables = np.append(outputVariables, outVar)
                idxBaseVars = len(outputVariables)

                # append output values of dnn
                for outVar in config.dnn_output_variables:
                    outputVariables = np.append(outputVariables, outVar)
                idxOutputVars = len(outputVariables)

                # append variables containing info about maximum dnn output node
                for outVar in config.dnn_predicted_class:
                    outputVariables = np.append(outputVariables, outVar)
                idxPredictedClass = len(outputVariables)

                # print variables
                print("variables to be written to output file:")
                for v in outputVariables:
                    print(v)
                print("=======================")
                
                # setup empty array for event data storage
                outputData = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))

                # setup input array for dnn evaluation
                inputData = np.zeros(shape= (ntuple.GetEntries(), len(model.variables)))

                first = False

            if error:
                # if selection is not fulfilled
                # fill default values of -1 into entry
                if not apply_selection:
                    outputData[fillIdx,:] = -1
                    inputData[fillIdx,:] = -1
                    fillIdx += 1
                continue


            # fill output data array
            
            # common variables
            outputData[fillIdx, :idxCommonVars] = entry[0, :idxCommonVars]

            # dnn input variables
            if write_input_vars:
                outputData[fillIdx, idxCommonVars:idxBaseVars] = entry[0, idxCommonVars:idxBaseVars]

            # dnn input variables into input array
            inputData[fillIdx, :] = entry[0, idxCommonVars:]

            # test prints        
            if fillIdx<=10:
                print("=== test input ===")
                for name, value in zip(model.variables, inputData[fillIdx]):
                    print(name, value)
                print("================="+"\n\n")

            fillIdx+=1

    # cut outputData to filled length
    if apply_selection:
        print("events that fulfilled the selection: {}/{}".format(fillIdx, len(outputData)))
        outputData = outputData[:fillIdx]
        inputData = inputData[:fillIdx]

    # get dnn output
    dnnOutput, maxIndex = model.evaluate(inputData)
    
    # fill dnn output
    outputData[:, idxBaseVars:idxOutputVars] = dnnOutput
    # fill predicted index
    outputData[:, idxOutputVars:idxPredictedClass] = maxIndex.reshape(len(outputData), -1)
    
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

