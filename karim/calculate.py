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
            print("inputtree", inputtree)
            jecs = load.getSystematics(inputtree)
            # if no branches are explicitly given, consider all branches in input tree
            # else use only the ones explicitly provided
            if len(branchesConfig) == 0:
                branches = inputtree.keys()
            else:
                for branch in branchesConfig:
                    branches += inputtree.keys(filter_name=branch)

            # open output root file
            with load.OutputFile(outpath) as outfile:
                with outfile.open() as output:
                    first = True
                    output_dict = None
                    # start loop over inputtree entries
                    tree_iterator = load.TreeIterator(inputtree, branches)
                    for i, event in enumerate(tree_iterator):
                        output_dict = config.calculate_variables(
                            event, output, "FIXME", jecs, dataEra, genWeights
                        )
                        print(output_dict)
                        if first:
                            print("writing variables to output tree:")
                            output["Events"] = output_dict
                            first = False
                        else:
                            output["Events"].extend(output_dict)
                    num_processed = tree_iterator.num_processed
                    with open(outpath.replace(".root", ".cutflow.txt"), "w") as cff:
                        cff.write("entries : {}".format(num_processed))
                        print("Cutflow file {} written.".format(outpath.replace(".root", ".cutflow.txt")))
                        print("\n" + "=" * 50 + "\n")
