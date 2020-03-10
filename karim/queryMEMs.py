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
        systematic = "nominal"
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
    if "SingleEl" in memFile:
        memFile = memPath + "/SingleElectron.h5"
    if "SingleMu" in memFile:
        memFile = memPath + "/SingleMuon.h5"
    if "EGamma" in memFile:
        memFile = memPath + "/EGamma.h5"
    memFile = memFile.replace("_new_pmx","")
    memFile = memFile.replace("_v2","")


    print("using {} as mem h5 file".format(memFile))
    try: 
        mem_df = pd.read_hdf(memFile)
    except:
        d = {'event': [-1], 'run': [-1], 'lumi': [-1]}
        mem_df = pd.DataFrame(data=d)
        print("Using dummy Dataframe!!!")
    # open input file
    with load.InputFile(filename) as ntuple:
        N_ev_input = ntuple.GetEntries()

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
        N_ev_output = outfile.tree.GetEntries()
    print("N_Events in input File: {}".format(N_ev_input))
    print("N_Events in output File: {}".format(N_ev_output))
    if N_ev_input != N_ev_output:
        sys.stderr.write("Number of events don't match up!!!")
        sys.stderr.write("N_Events in input File: {}".format(N_ev_input))
        sys.stderr.write("N_Events in output File: {}".format(N_ev_output))
    print("================="+"\n\n")
