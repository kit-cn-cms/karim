import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load
from hypotheses import Hypotheses

def query_MEMs(filename, configpath, outpath, memPath):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    # load config module
    dirname, basename = os.path.split(configpath)
    sys.path.append(dirname)
    config_name = os.path.splitext(basename)[0]
    config = importlib.import_module(config_name)
    print("\nimporting config:\n{}\n".format(configpath))

    # Figure out Systematic
    systematic = outpath.rsplit("/",1)[1]
    if "nominal" in systematic:
        systematic == "nominal"
    elif ("JES") in systematic:
        systematic = "JES" + systematic.rsplit("JES",1)[1]
        systematic = systematic.split("_Tree")[0].replace("JES","")
    elif ("JER") in systematic:
        systematic = "JER" + systematic.rsplit("JER",1)[1]
        systematic = systematic.split("_Tree")[0]
    else:
        print("Could not decode systematic -> aborting")
        sys.exit(1)
    print("detected Systematic {0}".format(systematic))

    print("looking for MEM dataframes in {}".format(memPath))
    memFile = memPath + os.path.basename(os.path.dirname(outpath)) + ".h5"
    memFile = memFile.replace("_new_pmx","")

    print("using {} as mem h5 file".format(memFile))
    mem_df = pd.read_hdf(memFile)

    # open input file
    with load.InputFile(filename) as ntuple:

        # load hypotheses module
        hypotheses = Hypotheses(config)

        hypotheses.set_memDF(mem_df)
        hypotheses.set_systematic(systematic)

        first = True
        # start loop over ntuple entries
        for i, (entry, error) in enumerate(load.TreeIterator(ntuple, hypotheses)):
            if first:
                # get list of all dataframe variables
                outputVariables = entry.columns.values
                # outputVariables = np.append(outputVariables, config.get_reco_naming()+"_matchable")
                for v in outputVariables:
                    print(v)
                
                # setup empty array for event data storage
                output = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))

                first = False
            
            if error:
                # for some reason no hypotheses are viable
                #   e.g. not enough jets
                output[i,:] = -1
            else:
                output[i] = entry.iloc[0].values
                
            if i<=10:
                print("=== testevent ===")
                for name, val in zip(outputVariables, output[i]):
                    print(name, val)
                print("================="+"\n\n")

    # save information as h5 file
    #df = pd.DataFrame(outputData, columns = outputVariables)
    #df.to_hdf(outpath.replace(".root",".h5"), key = "data", mode = "w")
    #del df            

    # open output root file
    outpath = outpath.replace(".root","_MEM.root")
    with load.OutputFile(outpath) as outfile:
        # initialize branches
        outfile.SetBranches(outputVariables)
        # loop over events and fill tree
        for event in output:
            outfile.FillTree(event)