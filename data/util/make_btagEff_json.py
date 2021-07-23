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
        name        = "fixedWP",
        description = "fixedWP deepJet b-tagging SFs for UL18"):

    # define correction meta data
    corr = {}
    corr["name"] = name
    corr["description"] = description
    corr["version"] = 2

    # define inputs
    corr["inputs"] =  []

    # define output
    corr["output"] = {}
    corr["output"]["name"] = "efficiency"
    corr["output"]["type"] = "real"
    corr["output"]["description"] = "b-tag efficiency for the corresponding bin"

    # init data
    corr["data"] = {}
    
    return corr




# btv inputs
def get_inputs():
    inputs = []
    inputs.append({
        "name": "workingPoint", 
        "type": "string", 
        "description": "working point, e.g. L/M/T"})
    inputs.append({
        "name": "jetFlavor",
        "type": "int",
        "description": "flavor of jets, e.g. 5 = b, 4 = c, 0 = light"})
    inputs.append({
        "name": "eta",
        "type": "real",
        "description": "jet eta value"})
    inputs.append({
        "name": "pt",
        "type": "real",
        "description": "jet pT value"})
    return inputs

def get_data(inFiles, wps = ["L", "M", "T"]):
    data = {}
    data["nodetype"] = "category"
    data["input"] = "workingPoint"
    data["content"] = []
    for wp in wps:
        data["content"].append(
            get_wp_data(inFiles, wp))

    return data

def get_wp_data(allInFiles, wp, flavors = ["l", "b", "c"]):
    data = {}
    data["key"] = wp
    data["value"] = {}
    data["value"]["nodetype"] = "category"
    data["value"]["input"] = "jetFlavor"
    data["value"]["content"] = []

    inFiles = [f for f in allInFiles if "efficiencies"+wp in f]
    for flav in flavors:
        data["value"]["content"].append(
            get_flav_data(inFiles, flav))

    return data

convertFlav = {"b": 5, "c": 4, "l": 0}
def get_flav_data(allInFiles, flav):
    data = {}
    data["key"] = convertFlav[flav]
    data["value"] = {}

    inFile = [f for f in allInFiles if "_"+flav+".root" in f]
    if len(inFile) != 1:
        print(inFile)
        print("should only be one")
        exit()
    inFile = inFile[0]   
    
    data["value"] = get_eta_pt_bins(inFile)
    return data
    
name = "efficiencies(L|M|T)_(l|c|b)__ttbb__nom"
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

def get_eta_pt_bins(inFile):
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
        etaEdges.append(h.GetXaxis().GetBinLowEdge(iEta+1))
    for iPt in range(h.GetNbinsY()+1):
        ptEdges.append(h.GetYaxis().GetBinLowEdge(iPt+1))
    data["edges"] = [etaEdges, ptEdges]

    values = []
    for iEta in range(h.GetNbinsX()):
        for iPt in range(h.GetNbinsY()):
            values.append(h.GetBinContent(iEta+1, iPt+1))
    data["content"] = values
    return data
    
        
import optparse 
parser = optparse.OptionParser(usage = "give rootfiles with efficiency maps as arguments")
parser.add_option("-o", dest = "output", help = "output file")
(opts, args) = parser.parse_args()

wps = ["L", "M", "T"]
inFiles = args

data = get_meta_data()

# fixedWP
correction_data = get_correction_meta_data(
    name        = "btagEff",
    description = "btagEff for deepJet b-tagging SFs for UL18")
correction_data["inputs"] = get_inputs()
correction_data["data"] = get_data(inFiles, wps)
data["corrections"].append(correction_data)


write_file(opts.output, data)
#print(json.dumps(data, indent = 4))
