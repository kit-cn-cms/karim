import os
import sys
import json
import ROOT
import re
import numpy as np


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

def get_correction_meta_data(name, description):

    # define correction meta data
    corr = {}
    corr["name"] = name
    corr["description"] = description
    corr["version"] = 2

    # define inputs
    corr["inputs"] =  []

    # define output
    corr["output"] = {}
    corr["output"]["name"] = "weight"
    corr["output"]["type"] = "real"
    corr["output"]["description"] = "pileup weight for the corresponding nTruePU bin"

    # init data
    corr["data"] = {}
    
    return corr




# btv inputs
def get_inputs():
    inputs = []
    inputs.append({
        "name": "variation", 
        "type": "string", 
        "description": "central/up/down"})
    inputs.append({
        "name": "nTrueInt",
        "type": "real",
        "description": "number of true interactions"})
    return inputs

def get_data(dataNom, dataUp, dataDown, mc):
    data = {}
    data["nodetype"] = "category"
    data["input"] = "variation"
    data["content"] = []

    data["content"].append(
        get_var_data("central", dataNom, mc))
    data["content"].append(
        get_var_data("up", dataUp, mc))
    data["content"].append(
        get_var_data("down", dataDown, mc))

    return data

def get_var_data(var, dataValues, mcValues):
    data = {}
    data["key"] = var
    data["value"] = {}
    data["value"]["nodetype"] = "binning"
    data["value"]["input"] = "nTrueInt"
    data["value"]["flow"] = "clamp"

    binEdges = np.arange(-0.5, len(dataValues)+0.5, 1)
    weight = np.zeros(len(dataValues))
    for i in range(len(dataValues)):
        if mcValues[i] == 0:
            weight[i] = 1.
        else:
            weight[i] = dataValues[i]/mcValues[i]
    data["value"]["edges"] = list(binEdges)
    data["value"]["content"] = list(weight)
    return data

def loadHist(dataInput, hName):
    f = ROOT.TFile.Open(dataInput)
    h = f.Get(hName)
    #print("integral: {}".format(h.Integral()))
    integral = h.Integral()
    values = np.zeros(99)
    for i in range(99):
        value = h.GetBinContent(h.FindBin(i))/h.Integral()
        #print(i, value)
        values[i] = value
    return values

        
        
import optparse 
parser = optparse.OptionParser(usage = "pileup reweighting")
parser.add_option("-o", dest = "output", help = "output file")
parser.add_option("--mc", dest = "mcInput", 
    help = "input root file as described in readme")
parser.add_option("--data", dest = "dataInput",
    help = "input data root file in afs storage (also will derermine varied files automatically")
(opts, args) = parser.parse_args()

dataValues     = loadHist(opts.dataInput, "pileup")
dataValuesUp   = loadHist(opts.dataInput.replace("69200ub","72400ub"), "pileup")
dataValuesDown = loadHist(opts.dataInput.replace("69200ub", "66000ub"), "pileup")

mcValues = loadHist(opts.mcInput, "pu_mc")


data = get_meta_data()

# fixedWP
correction_data = get_correction_meta_data(
    name        = "pileup",
    description = "pileup reweighting")
correction_data["inputs"] = get_inputs()
correction_data["data"] = get_data(dataValues, dataValuesUp, dataValuesDown, mcValues)
data["corrections"].append(correction_data)


write_file(opts.output, data)
#print(json.dumps(data, indent = 4))
