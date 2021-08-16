import ROOT
import sys
inf = sys.argv[1]
f = ROOT.TFile(inf)

keys = [k.GetName() for k in f.GetListOfKeys()]
print(keys)

data = {}
data["sfType"] = []
data["sysType"] = []
data["ptMin"] = []
data["ptMax"] = []
data["etaMin"] = []
data["etaMax"] = []
data["factor"] = []

for trg in keys:
    # if not trg.endswith("PtEtaBins"): continue
    if not trg.endswith("NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt"): continue
    #name = trg+"/pt_abseta_ratio"
    name = "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt"
    h = f.Get(name)

    for yBin in range(h.GetXaxis().GetNbins()):
        for xBin in range(h.GetYaxis().GetNbins()):
            # print(h.GetXaxis().GetBinLowEdge(yBin+1), h.GetXaxis().GetBinUpEdge(yBin+1))
            # print(h.GetYaxis().GetBinLowEdge(xBin+1), h.GetYaxis().GetBinUpEdge(xBin+1))
            for _ in range(3):
                data["sfType"].append(trg)
                data["etaMin"].append(h.GetXaxis().GetBinLowEdge(xBin+1))
                data["etaMax"].append(h.GetXaxis().GetBinUpEdge(xBin+1))
                if yBin == 0:
                    data["ptMin"].append(0.)
                else:
                    data["ptMin"].append(h.GetYaxis().GetBinLowEdge(yBin+1))
                if yBin == h.GetXaxis().GetNbins()-1:
                    data["ptMax"].append(99999.)
                else:
                    data["ptMax"].append(h.GetYaxis().GetBinUpEdge(yBin+1))
                
            factor = h.GetBinContent(yBin+1, xBin+1)
            data["sysType"].append("central")
            data["factor"].append(factor)

            data["sysType"].append("up")
            data["factor"].append(factor+h.GetBinError(yBin+1, xBin+1))

            data["sysType"].append("down")
            data["factor"].append(factor-h.GetBinError(yBin+1, xBin+1))
            # print("--")

import pandas as pd
df = pd.DataFrame.from_dict(data)
df.to_csv(inf.replace(".root",".csv"), index = False, columns = ["sfType", "sysType", "ptMin", "ptMax", "etaMin", "etaMax", "factor"])
print(df)

