import ROOT
import sys
y = sys.argv[1]
f = ROOT.TFile("sf_{y}_deepJet_combined.root".format(y = y))

hists = "SF_Evt_HT_jets_vs_N_Jets__{proc}__btag_NOMINAL"
processes = ["ttH", "ttbb", "ttbb_5FS", "ttcc", "ttlf", "ttZ"]

data = {}
data["process"] = []
data["jetsMin"] = []
data["jetsMax"] = []
data["htMin"] = []
data["htMax"] = []
data["factor"] = []

for p in processes:
    h = f.Get(hists.format(proc=p))
    
    for xBin in range(h.GetXaxis().GetNbins()):
        for yBin in range(h.GetYaxis().GetNbins()):
            print(h.GetXaxis().GetBinLowEdge(xBin+1), h.GetXaxis().GetBinUpEdge(xBin+1))
            print(h.GetYaxis().GetBinLowEdge(yBin+1), h.GetYaxis().GetBinUpEdge(yBin+1))
            data["process"].append(p)
            if yBin == 0:
                data["jetsMin"].append(0.)
            else:
                data["jetsMin"].append(h.GetYaxis().GetBinLowEdge(yBin+1))

            if yBin == h.GetYaxis().GetNbins()-1:
                data["jetsMax"].append(100.)
            else:
                data["jetsMax"].append(h.GetYaxis().GetBinUpEdge(yBin+1))

            data["htMin"].append(h.GetXaxis().GetBinLowEdge(xBin+1))

            if xBin == h.GetXaxis().GetNbins()-1:
                data["htMax"].append(10000.)
            else:
                data["htMax"].append(h.GetXaxis().GetBinUpEdge(xBin+1))
            data["factor"].append(h.GetBinContent(xBin+1, yBin+1))
            print("--")

import pandas as pd
df = pd.DataFrame.from_dict(data)
df.to_csv("sfPatch_{y}.csv".format(y = y), index = False, columns = ["process", "jetsMin", "jetsMax", "htMin", "htMax", "factor"])
print(df)
