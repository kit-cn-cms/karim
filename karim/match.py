import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load
from hypotheses import Hypotheses

def match_jets(filename, configpath, threshold, outpath):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    # load config module
    dirname, basename = os.path.split(configpath)
    sys.path.append(dirname)
    config_name = os.path.splitext(basename)[0]
    config = importlib.import_module(config_name)
    print("\nimporting config:\n{}\n".format(configpath))

    match_variables = config.get_match_variables()
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
                # get list of all dataframe variables
                outputVariables = entry.columns.values
                outputVariables = np.append(outputVariables, config.get_reco_naming()+"_matchable")
                for v in outputVariables:
                    print(v)
                
                # setup empty array for event data storage
                outputSig = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))
                outputBkg = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))

                first = False

            if error:
                # for some reason no hypotheses are viable
                #   e.g. not enough jets
                outputSig[i,:] = -99
                outputBkg[i,:] = -99
            else:
                # get best permutation
                bestIndex = findBest(entry, threshold, match_variables)
                if bestIndex == -1:
                    
                    outputSig[i,:] = -1.
                    outputBkg[i,:] = -1.
                else:
                    randIndex = config.get_random_index(entry, bestIndex)

                    outputSig[i,:-1] = entry.iloc[bestIndex].values
                    outputBkg[i,:-1] = entry.iloc[randIndex].values
                    outputSig[i, -1] = 1
                    outputBkg[i, -1] = 1

                
            if i<=10:
                print("=== testevent ===")
                for name, sigval, bkgval in zip(outputVariables, outputSig[i], outputBkg[i]):
                    print(name, sigval, bkgval)
                print("================="+"\n\n")

    # save information as h5 file
    #df = pd.DataFrame(outputData, columns = outputVariables)
    #df.to_hdf(outpath.replace(".root",".h5"), key = "data", mode = "w")
    #del df            

    # open output root file
    sigpath = outpath.replace(".root","_sig.root")
    bkgpath = outpath.replace(".root","_bkg.root")
    with load.OutputFile(sigpath) as outfile:
        # initialize branches
        outfile.SetBranches(outputVariables)
        # loop over events and fill tree
        for event in outputSig:
            outfile.FillTree(event)
    
    with load.OutputFile(bkgpath) as outfile:
        # initialize branches
        outfile.SetBranches(outputVariables)
        # loop over events and fill tree
        for event in outputBkg:
            outfile.FillTree(event)


def findBest(entry, threshold, match_variables):
    for v in match_variables:
        entry = entry.query(v+"<="+threshold)

    bestIndex = -1
    if entry.shape[0]>=1:
        bestIndex =  entry.index.values[0]

    return bestIndex
    





