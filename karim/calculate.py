import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
# from karim import load as load
import karim.load as load

def calculate_variables(filename, configpath, friendTrees, outpath, pred_type,
        dataEra = None, apply_selection = False, split_feature = None, jecDependent = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    config = load.Config(configpath, friendTrees, "Calculation")

    genWeights = load.GenWeights(filename)
    
    # open input file
    with load.InputFile(filename, config.getFriendTrees(filename)) as ntuple:
        jecs = load.getSystematics(ntuple)

        # open output root file
        with load.OutputFile(outpath) as outfile:
            outfile.SetConfigBranches(config, jecs, jecDependent)

            print("## pred type is: {}".format(pred_type))

            dir = "/nfs/dust/cms/user/epfeffer/ttxdl/feathers/ntuples_v14_all/2018"

            if pred_type == "NLP":
                preds_dir = "/nfs/dust/cms/user/epfeffer/ttxdl/feathers/ntuples_v14_all_eval_nlp_1_1/2018"

            if pred_type == "GLP":
                preds_dir = "/nfs/dust/cms/user/epfeffer/ttxdl/feathers/ntuples_v14_all_eval_glp_2/2018"

            head, filename = os.path.split(filename)
            idx = filename[5:-5]
            nodes = pd.read_feather(os.path.join(dir,outfile.sampleName, "nodes_tree_{}_nominal.feather".format(idx)))
            edges = pd.read_feather(os.path.join(dir,outfile.sampleName, "edges_tree_{}_nominal.feather".format(idx)))
            edges = edges.groupby(["event", "run", "lumi"])

            if pred_type == "NLP":
                preds = pd.read_feather(os.path.join(preds_dir,outfile.sampleName, "nlp_prediction_tree_{}_nominal.feather".format(idx)))
                nodes = pd.merge(nodes,preds,on=["event", "run", "lumi", "idx", "node_type", "node_mult"])
            nodes = nodes.groupby(["event", "run", "lumi"])

            graphs = pd.read_feather(os.path.join(dir,outfile.sampleName, "graphs_tree_{}_nominal.feather".format(idx)))
            
            if pred_type == "GLP":
                glp_preds = pd.read_feather(os.path.join(preds_dir,outfile.sampleName, "glp_prediction_tree_{}_nominal.feather".format(idx)))
                graphs = pd.merge(graphs,glp_preds,on=["event", "run", "lumi", "idx"])
            
            # graphs = glp_preds.groupby(["event", "run", "lumi"])
            graphs = graphs.groupby(["event", "run", "lumi"])
            
            # start loop over ntuple entries
            first = True
            node = None
            graph = None
            for i, event in enumerate(load.TreeIterator(ntuple)):
                # if getattr(event, f"nJets_nominal") < 3 or getattr(event, f"nLep") < 2:
                node = nodes.get_group((event.event, event.run, event.luminosityBlock))
                edge = edges.get_group((event.event, event.run, event.luminosityBlock))
                graph = graphs.get_group((event.event, event.run, event.luminosityBlock))
                if apply_selection:
                    if not config.base_selection(event):
                        continue
                if split_feature is None:
                    if not jecDependent:
                        config.calculate_variables(event, outfile, outfile.sampleName, None, dataEra, genWeights, node, graph, edge)
                    else:
                        for jec in jecs:
                            config.calculate_variables(event, outfile, outfile.sampleName, jec, dataEra, genWeights, node, graph, edge)
                    outfile.FillTree()
                else:
                    if not jecDependent:
                        loopSize = getattr(event, split_feature)
                        for idx in range(loopSize):
                            config.calculate_variables(event, outfile, outfile.sampleName, idx, node, graph, edge)
                            outfile.FillTree()
                            outfile.ClearArrays()
                    else:
                        for jec in jecs:
                            loopSize = getattr(event, split_feature+"_"+jec)
                            for idx in range(loopSize):
                                config.calculate_variables(event, outfile, outfile.sampleName, idx, jec, node, graph, edge)
                                outfile.FillTree()
                                outfile.ClearArrays()

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
