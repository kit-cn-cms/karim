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
        # open output root file
        with load.OutputFile(outpath) as outfile:
            outfile.SetConfigBranches(config)

            # start loop over ntuple entries
            first = True
            for i, event in enumerate(load.TreeIterator(ntuple)):
                config.calculate_variables(event, outfile)
                outfile.FillTree()

                if first:
                    print("writing variables to output tree:")
                    for b in list(outfile.tree.GetListOfBranches()):
                        print(b.GetName())
                    first = False

                if i<=10:
                    print(" === testevent ===")
                    for b in list(outfile.tree.GetListOfBranches()):
                        print(b.GetName(), ", ".join([str(entry) for entry in list(outfile.branchArrays[b.GetName()])]))
                    print(" ================="+"\n")
                outfile.ClearArrays()
                continue
            
