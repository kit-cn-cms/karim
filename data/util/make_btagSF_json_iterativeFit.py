import os
import sys
import pandas as pd
import json


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
    corr["output"]["name"] = "formula"
    corr["output"]["type"] = "real"
    corr["output"]["description"] = "b-tagging SF formula for the corresponding bin"

    # init data
    corr["data"] = {}
    
    return corr




# btv inputs
def get_inputs():
    inputs = []
    inputs.append({
        "name": "sysType",
        "type": "string",
        "description": "systematic type, e.g. central/down_hfstats2/down_jesAbsoluteScale"})
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
    inputs.append({
        "name": "discr",
        "type": "real",
        "description": "jet b-tagging discriminator value"})
    return inputs


def get_data(df):
    data = {}
    data["nodetype"] = "category"
    data["input"] = "sysType"
    data["content"] = []
    
    sysTypes = set(df.index.get_level_values("sysType").values)
    for st in sysTypes:
        data["content"].append(
            get_sysType_data(df, st))

    return data
    
def get_sysType_data(df_all, st):
    data = {}
    data["key"] = st
    data["value"] = {}
    data["value"]["nodetype"] = "category"
    data["value"]["input"]    = "jetFlavor"
    data["value"]["content"]  = []

    df = df_all.loc[(st, )]
    jetFlavs = set(df.index.get_level_values("jetFlavor").values)
    for jf in jetFlavs:
        data["value"]["content"].append(
            get_jetFlavor_data(df, jf))
    return data

convertFlav = {0: 5, 1: 4, 2: 0}
def get_jetFlavor_data(df_all, jf):
    data = {}
    data["key"] = convertFlav[int(jf)]
    df = df_all.loc[(jf, )]
    if type(df) == pd.Series:
        data["value"] = get_formula(df.formula)
        return data
    else:
        data["value"] = {}
        data["value"]["nodetype"] = "binning"
        data["value"]["input"] = "eta"
        data["value"]["flow"] = "clamp"

        edgesMin = list(df["etaMin"].values)
        edgesMax = list(df["etaMax"].values)

        df = df.set_index(["etaMin", "etaMax"])

        edge_values = list(sorted(set(edgesMin + edgesMax)))
        data["value"]["edges"] = edge_values
        data["value"]["content"] = []
        for iEta in range(len(edge_values)-1):
            data["value"]["content"].append(
                get_eta_data(df, edge_values[iEta], edge_values[iEta+1]))
        return data

def get_eta_data(df_all, etaMin, etaMax):
    data = {}
    df = df_all.loc[(etaMin, etaMax, )]
    if type(df) == pd.Series:
        data["value"] = get_formula(df.formula)
        return data
    else:
        data["nodetype"] = "binning"
        data["input"] = "pt"
        data["flow"] = "clamp"

        edgesMin = list(df["ptMin"].values)
        edgesMax = list(df["ptMax"].values)
        df = df.set_index(["ptMin", "ptMax"])

        edge_values = list(sorted(set(edgesMin + edgesMax)))
        data["edges"] = edge_values
        data["content"] = []
        for iPt in range(len(edge_values)-1):
            data["content"].append(
                get_pt_data(df, edge_values[iPt], edge_values[iPt+1]))
        return data

def get_pt_data(df_all, ptMin, ptMax):
    data = {}
    df = df_all.loc[(ptMin, ptMax, )]
    if type(df) == pd.Series:
        data["value"] = get_formula(df.formula)
        return data
    else:
        data["nodetype"] = "binning"
        data["input"] = "discr"
        data["flow"] = "clamp"

        edgesMin = list(df["discrMin"].values)
        edgesMax = list(df["discrMax"].values)
        df = df.set_index(["discrMin", "discrMax"])

        edge_values = list(sorted(set(edgesMin + edgesMax)))
        data["edges"] = edge_values
        data["content"] = []
        for iX in range(len(edge_values)-1):
            f = df.loc[(edge_values[iX], edge_values[iX+1])].formula
            data["content"].append(get_formula(f))

        return data

def get_formula(f):
    if not "x" in f:
        return float(f)
    else:
        data = {}
        data["nodetype"] = "formula"
        data["expression"] = f.replace("\"","")
        data["parser"] = "TFormula"
        data["variables"] = ["discr"]
        return data

        
import optparse 
parser = optparse.OptionParser()
parser.add_option("--csv", dest = "csv", help = "input csv file")
parser.add_option("-o", dest = "output", help = "output file")
(opts, args) = parser.parse_args()

# load dataframe
df = pd.read_csv(opts.csv, 
    index_col = ["measurementType", "OperatingPoint", "sysType", "jetFlavor"], 
    delimiter = ", ", engine = "python")
df = df.sort_index()
df = df.loc[("iterativefit", 3, )]

data = get_meta_data()

# iterative fit
correction_data = get_correction_meta_data(
    name        = "iterativeFit",
    description = "iterativeFit deepJet b-tagging SFs for UL18")
correction_data["inputs"] = get_inputs()
correction_data["data"] = get_data(df)
data["corrections"].append(correction_data)

write_file(opts.output, data)
#print(json.dumps(data, indent = 4))
