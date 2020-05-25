import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load
from hypotheses import Hypotheses

def calculate_variables(filename, configpath, friendTrees, outpath, apply_selection = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    config = load.Config(configpath, friendTrees, "Calculation")

    
    # open input file
    with load.InputFile(filename, config.getFriendTrees(filename)) as ntuple:

        # load hypothesis module
        entry_loader = Hypotheses(config)

        first = True
        fillIdx = 0
        # start loop over ntuple entries
        for i, event in enumerate(load.TreeIterator(ntuple)):
            entry, error = entry_loader.GetEntry(event, event.N_Jets)
            if first:
                # get list of all dataframe variables
                outputVariables = entry.columns.values
                # append output value to columns
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
                # fill output data array
                outputData[fillIdx,:] = entry.iloc[0].values
                fillIdx += 1
            if fillIdx<=10:
                print("=== testevent ===")
                for name, value in zip(outputVariables, outputData[fillIdx]):
                    print(name, value)
                print("================="+"\n\n")

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

