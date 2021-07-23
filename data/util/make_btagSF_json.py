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
        "name": "operatingPoint",
        "type": "string",
        "description": "Working point, e.g. L/M/T"})
    inputs.append({
        "name": "sysType",
        "type": "string",
        "description": "systematic type, e.g. central/down/up"})
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

def get_measurement_data(df_all, measurements = ["mujets", "comb", "incl"]):
    data = []
    for measurement in measurements:
        correction_data = get_correction_meta_data(
            name        = measurement,
            description = "fixedWP {} deepJet b-tagging SFs for UL18".format(measurement))
        df = df_all.loc[(measurement, )]
        correction_data["inputs"] = get_inputs()
        correction_data["data"] = get_data(df)
        data.append(correction_data)

    return data

def get_data(df):
    data = {}
    data["nodetype"] = "category"
    data["input"] = "operatingPoint"
    data["content"] = []

    operationPoints = set(df.index.get_level_values("OperatingPoint").values)
    for wp in operationPoints:
        data["content"].append(
            get_WP_data(df, wp))

    return data

convertWP = {0: "L", 1: "M", 2: "T"}
def get_WP_data(df_all, wp):
    data = {}
    data["key"] = convertWP[int(wp)]
    data["value"] = {}
    data["value"]["nodetype"] = "category"
    data["value"]["input"] = "sysType"
    data["value"]["content"] = []
    
    df = df_all.loc[(wp, )]
    sysTypes = set(df.index.get_level_values("sysType").values)
    for st in sysTypes:
        data["value"]["content"].append(
            get_sysType_data(df, st))

    return data
    
def get_sysType_data(df_all, st):
    data = {}
    data["key"] = st
    data["value"] = {}
    data["value"]["nodetype"] = "category"
    data["value"]["input"] = "jetFlavor"
    data["value"]["content"] = []

    df = df_all.loc[(st, )]
    jetFlavs = set(df.index.get_level_values("jetFlavor").values)
    for jf in jetFlavs:
        data["value"]["content"].append(
            get_jetFlavor_data(df, jf))

    return data

convertFlav = {0: 5, 1: 4, 2: 0}
def get_jetFlavor_data(df_all, jf, dimensions = ["eta", "pt"]):
    data = {}
    data["key"] = convertFlav[int(jf)]
    df = df_all.loc[(jf, )]
    if type(df) == pd.Series:
        # write formula directly
        data["value"] = get_formula(df.formula)
    else:
        # do multi binning
        data["value"] = {}
        data["value"]["nodetype"] = "multibinning"
        data["value"]["inputs"] = []
        data["value"]["flow"] = "clamp"

        edges = []
        reindex = []
        for edge in dimensions:
            data["value"]["inputs"].append(edge)
            reindex += [edge+"Min", edge+"Max"]

            edgesMin = list(df[edge+"Min"].values)
            edgesMax = list(df[edge+"Max"].values)

            edge_values = list(sorted(set(edgesMin + edgesMax)))
            edges.append(edge_values)

        df = df.set_index(reindex)
        data["value"]["edges"] = edges
        values = get_formula_data(df, edges)
        data["value"]["content"] = values    
                    
    return data

def get_formula_data(df, edges, index = []):
    idx = len(index)
    if idx == len(edges):
        loc = []
        for iIdx, idxVal in enumerate(index):
            loc+=[edges[iIdx][idxVal], edges[iIdx][idxVal+1]]
        f = df.loc[tuple(loc)].formula
        if not type(f) == str:
            print(f)
            exit()
        return [get_formula(f)]
    else:
        values = []
        for i in range(len(edges[idx])-1):
            values += get_formula_data(df, edges, index+[i])
        return values

def get_formula(f):
    if not "x" in f:
        return float(f)
    else:
        data = {}
        data["nodetype"] = "formula"
        data["expression"] = f.replace("\"","")
        data["parser"] = "TFormula"
        data["variables"] = ["pt"]
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


data = get_meta_data()

# fixedWP
data["corrections"] = get_measurement_data(df,
    measurements = ["mujets", "comb", "incl"])


write_file(opts.output, data)
#print(json.dumps(data, indent = 4))
