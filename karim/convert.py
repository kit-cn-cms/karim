import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
#import uproot

from karim import load as load

def convert_database(filename, configpath, outpath, friendTrees, database):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    config = load.Config(configpath, friendTrees, "Database")

    # figure out the correct database to load
    dbfile, indexfile = config.getDataBase(filename, database)

    print("loading database....")
    # opening database root file
    rf = ROOT.TFile(dbfile)
    db = rf.Get(config.treename)

    # opening db file with indices
    idf = pd.read_hdf(indexfile)
    print(idf)

    # collect branches to write
    branches = list([b.GetName() for b in db.GetListOfBranches()])

    # open input file
    with load.InputFile(filename, config.getFriendTrees(filename)) as ntuple:
        # open output root file
        with load.OutputFile(outpath) as outfile:
            outfile.SetBranchList(branches+["Evt_Run", "Evt_Lumi", "Evt_ID"])

            # start loop over ntuple entries
            first = True
            for i, event in enumerate(load.TreeIterator(ntuple)):
                config.calculate_variables(event, outfile)

                # search for corresponding event in database
                foundDBEntry = False
                try:
                    # searching for event index
                    dbevt = idf.loc[(idf[config.run] == event.Evt_Run) & (idf[config.lumi] == event.Evt_Lumi) & (idf[config.evtid] == event.Evt_ID)]
                    idx = dbevt.index[0]
                    foundDBEntry = True
                except:
                    print("event ({}, {}, {}) is not in database - filling defaults".format(event.Evt_Run, event.Evt_Lumi, event.Evt_ID))

                if foundDBEntry:
                    # jumping to indexed event in tree
                    db.GetEvent(idx)
                    # filling branches
                    for b in branches:
                        outfile.branchArrays[b][0] = eval("db."+b)

                if first:
                    print("writing variables to output tree:")
                    for b in list(outfile.tree.GetListOfBranches()):
                        print(b.GetName())
                    first = False

                
                outfile.FillTree()
                if i<=10:
                    print(" === testevent ===")
                    for b in list(outfile.tree.GetListOfBranches()):
                        print(b.GetName(), ", ".join([str(entry) for entry in list(outfile.branchArrays[b.GetName()])]))
                    print(" ================="+"\n")
                outfile.ClearArrays()
                continue
