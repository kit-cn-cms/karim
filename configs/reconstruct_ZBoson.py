import numpy as np
import common

name = "RecoDNN_Z"
def get_reco_naming():
    '''
    define name for this reconstruction
    '''
    return name


def get_objects():
    '''
    define a list of objects considered for the reconstruction
    '''
    objects = [
        "B1", 
        "B2"       
        ]
    return objects


def get_features():
    '''
    define a list of features applicable for all objects defined in get_objects()
    '''
    features = [
        "CSV", 
        "Pt", 
        "M", 
        "E", 
        "Eta", 
        "Phi"
        ]
    return features


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "N_BTagsM",
        "N_Jets",
        ]
    return variables



def calculate_variables(df):
    '''
    calculate additional variables needed for DNN input
    '''

    df[name+"_dPhi"] = common.get_dPhi(df[name+"_B1_Phi"].values, df[name+"_B2_Phi"].values)
    df[name+"_dEta"] = abs(df[name+"_B1_Eta"].values - df[name+"_B2_Eta"].values)
    df[name+"_dR"]   = np.sqrt(df[name+"_dEta"].values**2 + df[name+"_dPhi"].values**2)

    # reconstruct Z boson
    vectors = common.Vectors(df, name, ["B1", "B2"])
    vectors.add(["B1", "B2"], out = "Z")

    df[name+"_Z_Pt"]  = vectors.get("Z", "Pt")
    df[name+"_Z_Eta"] = vectors.get("Z", "Eta")
    df[name+"_Z_M"]   = vectors.get("Z", "M")
    df[name+"_Z_E"]   = vectors.get("Z", "E")

    return df

