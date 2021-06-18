import ROOT
import sys
inf = sys.argv[1]
f = ROOT.TFile(inf)
if "Ele_Tight" in inf:
    sfType = "tightElectronID"
elif "Ele_Medium" in inf:
    sfType = "mediumElectronID"
elif "Ele_Loose" in inf:
    sfType = "looseElectronID"
elif "Ele_Veto" in inf:
    sfType = "vetoElectronID"

if "ptAbove" in inf:
    sfType = "electronReco"

data = {}
data["sfType"] = []
data["sysType"] = []
data["ptMin"] = []
data["ptMax"] = []
data["etaMin"] = []
data["etaMax"] = []
data["factor"] = []

histName = "EGamma_SF2D"
h = f.Get(histName)

for xBin in range(h.GetXaxis().GetNbins()):
    for yBin in range(h.GetYaxis().GetNbins()):
        #print(h.GetXaxis().GetBinLowEdge(xBin+1), h.GetXaxis().GetBinUpEdge(xBin+1))
        #print(h.GetYaxis().GetBinLowEdge(yBin+1), h.GetYaxis().GetBinUpEdge(yBin+1))
        for _ in range(3):
            data["sfType"].append(sfType)
            data["etaMin"].append(h.GetXaxis().GetBinLowEdge(xBin+1))
            data["etaMax"].append(h.GetXaxis().GetBinUpEdge(xBin+1))
            if yBin == 0:
                data["ptMin"].append(0.)
            else:
                data["ptMin"].append(h.GetYaxis().GetBinLowEdge(yBin+1))
            if yBin == h.GetYaxis().GetNbins()-1:
                data["ptMax"].append(99999.)
            else:
                data["ptMax"].append(h.GetYaxis().GetBinUpEdge(yBin+1))
            
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

