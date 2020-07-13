import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load

def calculate_variables(filename, configpath, friendTrees, outpath, apply_selection = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    config = load.Config(configpath, friendTrees, "Calculation")

    
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
                inputVariables = config.additional_variables
                # append output value to columns
                print("input variables:")
                for v in inputVariables:
                    print(v)
                
                # setup empty array for event data storage
                inputData = np.zeros(shape = (ntuple.GetEntries(), len(inputVariables)))

                first = False

            if error:
                #print("selection not fulfulled")
                if not apply_selection:
                    inputData[fillIdx,:] = -1
                    fillIdx += 1
                continue
            else:
                # fill output data array
                inputData[fillIdx,:] = entry[0]
                fillIdx += 1

    # cut outputData to filled length
    if apply_selection:
        print("events that fulfilled the selection: {}/{}".format(fillIdx, len(outputData)))
        inputData = inputData[:fillIdx]

    # convert information to h5 file
    df = pd.DataFrame(inputData, columns = inputVariables)

    # caluclate variables
    df = config.calculate_variables(df)
    outputVariables = df.columns.values
    outputData = df.values
    for i in range(10):
        print("=== testevent ===")
        for name in outputVariables:
            print(name, df[name].values[i])
        print("================="+"\n")

    df.to_hdf(outpath.replace(".root",".h5"), key = "data", mode = "w")
    del df            

    # open output root file
    with load.OutputFile(outpath) as outfile:
        # initialize branches
        outfile.SetBranches(outputVariables)
        # loop over events and fill tree
        for event in outputData:
            outfile.FillTree(event)

