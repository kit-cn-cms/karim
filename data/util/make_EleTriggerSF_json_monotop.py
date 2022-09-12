import os
import sys
import json
import ROOT
import re


def write_file(path, data):
    string = json.dumps(data, indent = 4)
    with open(path, "w") as f:
        f.write(string)
    print("output file {} written".format(path))


def get_meta_data():
    data = {}
    data["schema_version"] = 2
    data["corrections"] = []
    
    return data

# generate one for iterative fit and one for fixed WP
def get_correction_meta_data(
        name        = "EleTriggerSF",
        description = "Electron Trigger SFs"):

    # define correction meta data
    corr = {}
    corr["name"] = name
    corr["description"] = description
    corr["version"] = 2

    # define inputs
    corr["inputs"] =  []

    # define output
    corr["output"] = {}
    corr["output"]["name"] = "ScaleFactor"
    corr["output"]["type"] = "real"
    corr["output"]["description"] = "Electron Trigger SF for the corresponding bin"

    # init data
    corr["data"] = {}
    
    return corr



def get_inputs():
    inputs = []
    inputs.append({
        "name": "sf", 
        "type": "string", 
        "description": "sf, e.g. central/up/down"})
    inputs.append({
        "name": "pt",
        "type": "real",
        "description": "Electron pT value"})
    inputs.append({
        "name": "eta",
        "type": "real",
        "description": "Electron eta value"})
    return inputs

def get_data(inFiles, wps = ["central", "up", "down"]):
    data = {}
    data["nodetype"] = "category"
    data["input"] = "sf"
    data["content"] = []
    for wp in wps:
        data["content"].append(
            get_sf_data(inFiles, wp))

    return data

def get_sf_data(allInFiles, wp):
    data = {}
    data["key"] = wp
    data["value"] = {}

    inFile = [f for f in allInFiles if ".root" in f]
    if len(inFile) != 1:
        print(inFile)
        print("should only be one")
        exit()
    inFile = inFile[0]   
    
    data["value"] = get_eta_pt_bins(inFile, wp)
    return data
    
name = "EGamma_SF2D"
def get_key(f):
    key = None
    for k in list(f.GetListOfKeys()):
        match = re.match(name, k.GetName())
        if not match is None:
            key = k.GetName()
            break
    if key is None:
        print("could not find appropriate key in file")
        exit()
    return key

def get_eta_pt_bins(inFile, wp):
    f = ROOT.TFile.Open(inFile)
    
    key = get_key(f)
    h = f.Get(key)
    
    data = {}
    data["nodetype"] = "multibinning"
    data["inputs"] = ["eta", "pt"]
    data["flow"] = "clamp"

    etaEdges = []
    ptEdges = []
    for iEta in range(h.GetNbinsX()+1):
        etaEdges.append(round(h.GetXaxis().GetBinLowEdge(iEta+1),4))
    for iPt in range(h.GetNbinsY()+1):
        ptEdges.append(round(h.GetYaxis().GetBinLowEdge(iPt+1),4))
    data["edges"] = [etaEdges, ptEdges]

    values = []
    for iEta in range(h.GetNbinsX()):
        for iPt in range(h.GetNbinsY()):
            if wp == "central":
                values.append(h.GetBinContent(iEta+1, iPt+1))
            elif wp == "up":
                values.append(h.GetBinContent(iEta+1, iPt+1) + h.GetBinError(iEta+1, iPt+1))
            elif wp == "down":
                values.append(h.GetBinContent(iEta+1, iPt+1) - h.GetBinError(iEta+1, iPt+1))
    data["content"] = values
    return data
    
        
import optparse 
parser = optparse.OptionParser(usage = "give rootfile as argument")
parser.add_option("-o", dest = "output", help = "output file")
(opts, args) = parser.parse_args()

wps = ["central", "up", "down"]
inFiles = args

print ("infiles are {}".format(inFiles))

data = get_meta_data()

correction_data = get_correction_meta_data(
    name        = "EleTriggerSF",
    description = "Electron Trigger SFs")
correction_data["inputs"] = get_inputs()
correction_data["data"] = get_data(inFiles, wps)
data["corrections"].append(correction_data)


write_file(opts.output, data)
# print(json.dumps(data, indent = 4))
