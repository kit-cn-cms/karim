import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load
from hypotheses import Hypotheses

def match_jets(filename, configpath, threshold, signal_only, outpath, apply_selection = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    config = load.Config(configpath, "Matching")

    # open input file
    with load.InputFile(filename) as ntuple:
    
        # load hypotheses module
        hypotheses = Hypotheses(config)

        # initialize hypotheses combinatorics
        hypotheses.initPermutations()

        first = True
        fillIdx = 0
        # start loop over ntuple entries
        for i, event in enumerate(load.TreeIterator(ntuple)):
            entry, error = hypotheses.GetEntry(event, event.N_Jets)

            if first:
                # get list of all dataframe variables
                outputVariables = entry.columns.values
                outputVariables = np.append(outputVariables, config.naming+"_matchable")
                for v in outputVariables:
                    print(v)

                # setup empty array for event data storage
                outputSig = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))
                if not signal_only:
                    outputBkg = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))

                first = False

                # indices to fill basic variables regardless of matching status
                loIdxVars = hypotheses.nBaseVariables
                hiIdxVars = hypotheses.nAdditionalVariables

            if error:
                # for some reason no hypotheses are viable
                #   e.g. not enough jets
                if not apply_selection:
                    outputSig[fillIdx,:loIdxVars] = -99
                    outputSig[fillIdx,loIdxVars:hiIdxVars] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                    outputSig[fillIdx,hiIdxVars:] = -99
                    if not signal_only:
                        outputBkg[fillIdx,:loIdxVars] = -99
                        outputBkg[fillIdx,loIdxVars:hiIdxVars] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                        outputBkg[fillIdx,hiIdxVars:] = -99
                    fillIdx+=1
                continue

            # apply signal selection
            sig_selection = config.def_signal_selection
            entry_signal_selection = entry_selection(entry, sig_selection)
            # get best permutation
            # bestIndex = findBest(entry, threshold, config.match_variables)
            bestIndex = findBest(entry_signal_selection, threshold, config.match_variables)
            # fill -1 if no match was found
            if bestIndex == -1:
                if not apply_selection:
                    outputSig[fillIdx,:loIdxVars] = -1
                    outputSig[fillIdx,loIdxVars:hiIdxVars] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                    outputSig[fillIdx,hiIdxVars:] = -1
                    if not signal_only:
                        outputBkg[fillIdx,:loIdxVars] = -1
                        outputBkg[fillIdx,loIdxVars:hiIdxVars] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                        outputBkg[fillIdx,hiIdxVars:] = -1
            else:
                # randIndex = config.get_random_index(entry, bestIndex)
                outputSig[fillIdx,:-1] = entry.iloc[bestIndex].values
                outputSig[fillIdx, -1] = 1
                if not signal_only:
                    bkg_selection = config.def_background_selection
                    entry_background_selection = entry_selection(entry, bkg_selection)
                    # print entry_background_selection
                    # print entry_background_selection.shape[0]
                    fill = True
                    if entry_background_selection.shape[0] == 1:
                        if entry_background_selection.index[0] == bestIndex:
                            fill = False
                    if entry_background_selection.shape[0] == 0:
                        fill = False
                    if not fill:
                        if not apply_selection:
                            outputBkg[fillIdx,:loIdxVars] = -99
                            outputBkg[fillIdx,loIdxVars:hiIdxVars] = entry.iloc[0].values[loIdxVars:hiIdxVars]
                            outputBkg[fillIdx,hiIdxVars:] = -99
                    else:
                        randIndex = config.get_random_index(entry_background_selection, bestIndex)
                        outputBkg[fillIdx,:-1] = entry.iloc[randIndex].values
                        outputBkg[fillIdx, -1] = 1
                
            if fillIdx<=10:
                print("=== testevent ===")
                if not signal_only:
                    for name, sigval, bkgval in zip(
                        outputVariables, outputSig[fillIdx], outputBkg[fillIdx]):
                        print(name, sigval, bkgval)
                else:
                    for name, sigval in zip(outputVariables, outputSig[fillIdx]):
                        print(name, sigval)
                print("================="+"\n\n")

            fillIdx+=1

    # save information as h5 file
    #df = pd.DataFrame(outputData, columns = outputVariables)
    #df.to_hdf(outpath.replace(".root",".h5"), key = "data", mode = "w")
    #del df            
    if apply_selection:
        print("events that fulfilled the selection {}/{}".format(fillIdx, len(outputSig)))
        outputSig = outputSig[:fillIdx]
        if not signal_only:
            outputBkg = outputBkg[:fillIdx]

    # open output root file
    if not signal_only:
        sigpath = outpath.replace(".root","_sig.root")
        bkgpath = outpath.replace(".root","_bkg.root")
    else:
        sigpath = outpath

    with load.OutputFile(sigpath) as outfile:
        # initialize branches
        outfile.SetBranches(outputVariables)
        # loop over events and fill tree
        for event in outputSig:
            outfile.FillTree(event)

    if not signal_only:    
        with load.OutputFile(bkgpath) as outfile:
            # initialize branches
            outfile.SetBranches(outputVariables)
            # loop over events and fill tree
            for event in outputBkg:
                outfile.FillTree(event)


def findBest(entry, threshold, match_variables):
    # print(list(entry.columns))
    # entry = entry.query("bbfromttbar_HadTopB_CSV>0.277")
    # entry = entry.query("bbfromttbar_LepTopB_CSV>0.277")
    # print(entry)
    # print(match_variables)
    for v in match_variables:
        entry = entry.query(v+"<="+threshold)

    bestIndex = -1
    if entry.shape[0]>=1:
        bestIndex =  entry.index.values[0]
    return bestIndex

def entry_selection(entry, selection):
    # print (sig_selection)
    for i in selection:
        entry = entry.query(i)
    return entry

# def signal_selection(entry, sig_selection):
#     # print (sig_selection)
#     for i in sig_selection:
#         entry = entry.query(i)
#     return entry

# def background_selection(entry, bkg_selection):
#     # print (bkg_selection)
#     for i in bkg_selection:
#         entry = entry.query(i)
#     return entry




