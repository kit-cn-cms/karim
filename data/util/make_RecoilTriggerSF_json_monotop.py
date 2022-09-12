import os
import sys
import json
import ROOT
import re
from pprint import pprint
from math import sqrt


import optparse 
parser = optparse.OptionParser(usage = "give rootfile as argument")
parser.add_option("-o", dest = "output", help = "output file")
parser.add_option("-e", dest = "era", help = "era")
(opts, args) = parser.parse_args()

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

def get_correction_meta_data(
        name        = "RecoilTriggerSF",
        description = "Recoil Trigger SFs"):

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
    corr["output"]["description"] = "Recoil Trigger SF for the corresponding bin"

    # init data
    corr["data"] = {}
    
    return corr



def get_inputs():
    inputs = []
    inputs.append({
        "name": "sf", 
        "type": "string", 
        "description": "sf, e.g. central/up/down/statup/statdown/systup/systdown"})
    inputs.append({
        "name": "pt",
        "type": "real",
        "description": "Recoil pT value"})
    return inputs

def get_data(inFiles, wps = ["central", "up", "down", "statup", "statdown", "systup", "systdown"]):
    data = {}
    data["nodetype"] = "category"
    data["input"] = "sf"
    data["content"] = []
    for wp in wps:
        data["content"].append(
            get_sf_data(inFiles, wp))
    pprint(data)

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
    
    data["value"] = get_pt_bins(inFile, wp)
    return data
    
name = "CR_W_muon_efficiencySF_"+opts.era
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

def get_pt_bins(inFile, wp):
    f = ROOT.TFile.Open(inFile)
    
    key = get_key(f)
    h = f.Get(key)
    
    data = {}
    data["nodetype"] = "binning"
    data["input"] = "pt"
    data["flow"] = "clamp"

    ptEdges = []
    n = h.GetN()
    # n = 3
    for iPt in range(n):
        ptEdges.append(round(h.GetPointX(iPt),4) - round(h.GetErrorXlow(iPt),4))
    ptEdges.append(round(h.GetPointX(n-1),4) + round(h.GetErrorXhigh(iPt),4))
    
    data["edges"] = ptEdges


    values = []
    for iPt in range(n):
        if wp == "central":
            values.append(h.GetPointY(iPt))
        elif wp == "up":
            values.append(h.GetPointY(iPt)+sqrt(h.GetErrorYhigh(iPt)**2+(0.01*h.GetPointY(iPt))**2))
        elif wp == "down":
            values.append(h.GetPointY(iPt)-sqrt(h.GetErrorYlow(iPt)**2+(0.01*h.GetPointY(iPt))**2))
        elif wp == "statup":
            values.append(h.GetPointY(iPt)+h.GetErrorYhigh(iPt))
        elif wp == "statdown":
            values.append(h.GetPointY(iPt)-h.GetErrorYlow(iPt))
        elif wp == "systup":
            values.append(h.GetPointY(iPt)+0.01*h.GetPointY(iPt))
        elif wp == "systdown":
            values.append(h.GetPointY(iPt)-0.01*h.GetPointY(iPt))
    data["content"] = values
    print(len(ptEdges))
    print(len(values))

    return data
    
        


wps = ["central", "up", "down", "statup", "statdown", "systup", "systdown"]
inFiles = args

print ("infiles are {}".format(inFiles))

data = get_meta_data()

correction_data = get_correction_meta_data(
    name        = "RecoilTriggerSFs",
    description = "Recoil Trigger SFs")
correction_data["inputs"] = get_inputs()
correction_data["data"] = get_data(inFiles, wps)
data["corrections"].append(correction_data)


write_file(opts.output, data)
# print(json.dumps(data, indent = 4))
