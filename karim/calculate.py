import importlib
import os
import sys
import numpy as np
import pandas as pd

# from karim import load as load
import karim.load as load
import awkward as ak


def calculate_variables(
    filename,
    configpath,
    friendTrees,
    outpath,
    dataEra=None,
    apply_selection=False,
    split_feature=None,
    jecDependent=False,
):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    config = load.Config(configpath, friendTrees, "Calculation")

    genWeights = load.GenWeights(filename)

    branchesConfig = config.load_input_branches()
    branches = []

    # open input file
    with load.InputFile(filename) as inputfile:
        # open input tree
        with inputfile.load("Events") as inputtree:
            jecs = load.getSystematics(inputtree)
            # if no branches are explicitly given, consider all branches in input tree
            # else use only the ones explicitly provided
            if len(branchesConfig) == 0:
                branches = inputtree.keys()
            else:
                for branch in branchesConfig:
                    branches += inputtree.keys(filter_name=branch)

            # initialize output root file
            with load.OutputFile(outpath) as outfile:
                # open output root file
                with outfile.open() as output:
                    output_dict = None
                    # start loop over inputtree entries
                    tree_iterator = load.TreeIterator(inputtree, branches)
                    for i, event in enumerate(tree_iterator):
                        output_dict = config.calculate_variables(
                            event, output, outfile.sample_name, jecs, dataEra, genWeights
                        )
                        # write events to output file as TTree using uproot
                        if i == 0:
                            print("writing variables to output tree:")
                            output["Events"] = output_dict
                        else:
                            output["Events"].extend(output_dict)
                    # keep track of number of processed events
                    num_processed = tree_iterator.num_processed
                    # open cutflow file (cff)
                    with open(outpath.replace(".root", ".cutflow.txt"), "w") as cff:
                        cff.write("entries : {}".format(num_processed))
                        print(
                            "Cutflow file {} written.".format(
                                outpath.replace(".root", ".cutflow.txt")
                            )
                        )
                        print("\n" + "=" * 50 + "\n")
