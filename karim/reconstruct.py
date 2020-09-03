import ROOT
import importlib
import os
import sys
import numpy as np
import pandas as pd
from karim import load as load
from hypotheses import Hypotheses

def evaluate_reconstruction(filename, modelname, configpath, outpath, apply_selection = False):
    print(" ===== EVALUATING FILE ===== ")
    print(filename)
    print(" =========================== ")

    # load the DNN model
    model = load.Model(modelname)
    
    # set variables needed for dnn training
    model.setVariables()

    config = load.Config(configpath, "Reconstruction")

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
                # check if all variables for DNN evaluation are present in dataframe
                check_entry(entry, model.variables)

                # get list of all dataframe variables
                outputVariables = entry.columns.values
                # append output value to columns
                outputVariables = np.append(outputVariables, 
                    config.naming+"_DNNOutput")
                outputVariables = np.append(outputVariables, 
                    config.naming+"_squaredDNNOutput")
                outputVariables = np.append(outputVariables, 
                    config.naming+"_transformedDNNOutput")
                for v in outputVariables:
                    print(v)
                
                # setup empty array for event data storage
                outputData = np.zeros(shape = (ntuple.GetEntries(), len(outputVariables)))

                first = False

            if error:
                print("hypothesis not viable")
                # for some reason no hypotheses are viable
                #   e.g. not enough jets
                if not apply_selection:
                    outputData[fillIdx,:-3] = entry.iloc[0].values
                    # fill dummy output values of DNN
                    outputData[fillIdx, -3] = -1.
                    outputData[fillIdx, -2] = -99.
                    outputData[fillIdx, -1] = -99.
                    fillIdx+=1
                continue
            else:
                # get best permutation
                reco_selection = config.def_dnn_reco_selection
                entry_reco_selection = entry_selection(entry, reco_selection)
                if entry_reco_selection.shape[0] == 0:
                    outputData[fillIdx,:-3] = entry.iloc[0].values
                    # fill dummy output values of DNN
                    outputData[fillIdx, -3] = -9.
                    outputData[fillIdx, -2] = -9.
                    outputData[fillIdx, -1] = -9.
                    fillIdx+=1
                    continue
                # print entry_reco_selection
                bestIndex, outputValue = model.findBest(entry_reco_selection)
                # bestIndex, outputValue = model.findBest(entry)
                # fill output data array
                outputData[fillIdx,:-3] = entry_reco_selection.iloc[bestIndex].values
                # outputData[fillIdx,:-3] = entry.iloc[bestIndex].values
                # fill output values of DNN
                outputData[fillIdx, -3] = outputValue
                outputData[fillIdx, -2] = outputValue**2
                outputData[fillIdx, -1] = np.log(outputValue/(1.-outputValue))
                
                if fillIdx<=10:
                    print("=== testevent ===")
                    for name, value in zip(outputVariables, outputData[fillIdx]):
                        print(name, value)
                    print("================="+"\n\n")

                fillIdx += 1

    # cut outputData to filled length
    if apply_selection:
        print("events that fulfilled the selection: {}/{}".format(fillIdx, len(outputData)))
        outputData = outputData[:fillIdx]

    # save information as h5 file
    df = pd.DataFrame(outputData, columns = outputVariables)
    df.to_hdf(outpath.replace(".root",".h5"), key = "data", mode = "w")
    del df            

    # open output root file
    with load.OutputFile(outpath) as outfile:
        # initialize branches
        outfile.SetBranches(outputVariables)
        # loop over events and fill tree
        for event in outputData:
            outfile.FillTree(event)
    


def check_entry(entry, variables):
    '''
    check if all variables needed for the DNN evaluation is found in the generated dataframe
    '''
    if set(variables).issubset(entry.columns):
        print("all variables found in dataframe for DNN evaluation")
    else:
        print("some variables are missing in dataframe:")
        available = entry.columns.values
        for v in variables:
            if v not in available:
                print("{var} missing".format(var = v))
        exit()





def evaluate_reco(files, opts):
    c = ROOT.TChain("MVATree")
    for f in files:
        c.Add(f)

    # init groups
    groups = {}
    plot_vars = []
    efficiencies = {}
    for g in opts.groups:
        name, variables = g.split("=")
        groups[name] = variables.split("+")
        plot_vars += groups[name]
        efficiencies[name] = 0.

    plot_vars = list(set(plot_vars))
    print(plot_vars)

    # init binedges
    low, hi = opts.binrange.split(",")

    # init desired th1 histograms
    histograms = {}
    for i, v in enumerate(plot_vars):
        histograms[v] = ROOT.TH1F(v, v, int(opts.nbins), float(low), float(hi))
        histograms[v].SetLineColor(i+1)

    
    # event loop fill histograms
    nEvtsAfterSelection = 0
    for i in range(c.GetEntries()):
        c.GetEntry(i)
        if not eval(opts.selection):
            continue
        nEvtsAfterSelection += 1
        for v in histograms:
            histograms[v].Fill(getattr(c, v))
        for g in efficiencies:
            eff = True
            for v in groups[g]:
                if opts.mode=="leq":
                    if getattr(c, v) > float(opts.cutoff):
                        eff = False
                if opts.mode=="geq":
                    if getattr(c, v) < float(opts.cutoff):
                        eff = False
            if eff:
                efficiencies[g]+=1

    # set specs for histograms
    for v in histograms:
        histograms[v].SetLineWidth(2)
        
    # loop over groups and create some plot
    for g in groups:
        canvas = ROOT.TCanvas(g, g, 1024, 1024)

        efficiencies[g]/=nEvtsAfterSelection
        title = "efficiency for {group}{mode}{cutoff}: {eff:.2f}%".format(
            group = g, 
            mode = (">=" if opts.mode=="geq" else "<="), 
            cutoff = opts.cutoff,
            eff = efficiencies[g]*100.
            )

        for i, v in enumerate(groups[g]):
            if i == 0:
                histograms[v].Draw("histo")
                histograms[v].SetTitle(title)
            else:
                histograms[v].Draw("histo same")
                histograms[v].SetTitle(title)

        legend = ROOT.TLegend(0.6,0.7,0.88,0.88)
        for v in groups[g]:
            legend.AddEntry(histograms[v], v, "L")
        legend.Draw("SAME")
        canvas.SetTitle(title)
        print(title)
        canvas.SaveAs("/".join([opts.output, g+".pdf"]))
        canvas.SaveAs("/".join([opts.output, g+".png"]))
        canvas.Clear()
        legend.Clear()
        
def entry_selection(entry, selection):
    for i in selection:
        entry = entry.query(i)
    return entry