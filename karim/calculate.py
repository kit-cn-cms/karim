import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
# from karim import load as load
import karim.load as load
import awkward as ak

def calculate_variables(filename, configpath, friendTrees, outpath, 
        dataEra = None, apply_selection = False, split_feature = None, jecDependent = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    config = load.Config(configpath, friendTrees, "Calculation")

    genWeights = load.GenWeights(filename)

    branchesConfig = config.load_input_branches()
    branches = []
    
    # open input file
    with load.InputFile(filename, config.getFriendTrees(filename), "Events") as ntuple:
        jecs = load.getSystematics(ntuple)

        if len(branchesConfig) == 0:
            branches = ntuple.keys()
        else:
            for branch in branchesConfig:
                branches += ntuple.keys(filter_name=branch)

        # open output root file
        with load.OutputFile(outpath) as outfile:
            outfile.SetConfigBranches(config, jecs, jecDependent)

            # start loop over ntuple entries
            first = True
            print("Ntuple",ntuple)
            output_array = []
            for i, event in enumerate(load.TreeIterator(ntuple, None, branches)):
                if i%51 == 0:
                    output_array = []
                if apply_selection:
                    if not config.base_selection(event):
                        continue
                if split_feature is None:
                    if not jecDependent:
                        config.calculate_variables(event, outfile, outfile.sampleName, None, dataEra, genWeights)
                    else:
                        output_array.append(config.calculate_variables(event, outfile, outfile.sampleName, jecs, dataEra, genWeights))
                    outfile.FillTree()
                else:
                    if not jecDependent:
                        loopSize = getattr(event, split_feature)
                        for idx in range(loopSize):
                            config.calculate_variables(event, outfile, outfile.sampleName, idx)
                            outfile.FillTree()
                            outfile.ClearArrays()
                    else:
                        for jec in jecs:
                            loopSize = getattr(event, split_feature+"_"+jec)
                            for idx in range(loopSize):
                                config.calculate_variables(event, outfile, outfile.sampleName, idx, jec)
                                outfile.FillTree()
                                outfile.ClearArrays()
                
                if i%50 == 0:
                    output_tree = {}
                    for key in output_array[i%50]:
                        output_tree[key] = []
                    for key in output_tree:
                        for event_dict in output_array:
                            output_tree[key].append(event_dict[key])
                    for key in output_tree:
                        output_tree[key] = ak.Array(output_tree[key])
                    print(output_tree)


                    

                if first:
                    print("writing variables to output tree:")
                    for b in list(outfile.tree.GetListOfBranches()):
                        print(b.GetName())
                    first = False

                
                if i<=10 and split_feature is None:
                    print(" === testevent ===")
                    for b in list(outfile.tree.GetListOfBranches()):
                        print(b.GetName(), ", ".join([str(entry) for entry in list(outfile.branchArrays[b.GetName()])]))
                    print(" ================="+"\n")
                outfile.ClearArrays()
                continue
