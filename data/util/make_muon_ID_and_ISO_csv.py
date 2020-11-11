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
    h = f.Get(trg)

    for xBin in range(h.GetXaxis().GetNbins()):
        for yBin in range(h.GetYaxis().GetNbins()):
            #print(h.GetXaxis().GetBinLowEdge(xBin+1), h.GetXaxis().GetBinUpEdge(xBin+1))
            #print(h.GetYaxis().GetBinLowEdge(yBin+1), h.GetYaxis().GetBinUpEdge(yBin+1))
            for _ in range(3):
                data["sfType"].append(trg)
                data["etaMin"].append(h.GetYaxis().GetBinLowEdge(yBin+1))
                data["etaMax"].append(h.GetYaxis().GetBinUpEdge(yBin+1))
                if xBin == 0:
                    data["ptMin"].append(0.)
                else:
                    data["ptMin"].append(h.GetXaxis().GetBinLowEdge(xBin+1))
                if xBin == h.GetXaxis().GetNbins()-1:
                    data["ptMax"].append(99999.)
                else:
                    data["ptMax"].append(h.GetXaxis().GetBinUpEdge(xBin+1))
                
            factor = h.GetBinContent(xBin+1, yBin+1)
            data["sysType"].append("central")
            data["factor"].append(factor)

            data["sysType"].append("up")
            data["factor"].append(factor+h.GetBinError(xBin+1, yBin+1))

            data["sysType"].append("down")
            data["factor"].append(factor-h.GetBinError(xBin+1, yBin+1))
            #print("--")

import pandas as pd
df = pd.DataFrame.from_dict(data)
df.to_csv(inf.replace(".root",".csv"), index = False, columns = ["sfType", "sysType", "ptMin", "ptMax", "etaMin", "etaMax", "factor"])
print(df)

