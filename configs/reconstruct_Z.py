import numpy as np
import common

name = "Reco_Z"
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

    # angular differences
    df[name+"_Delta_Phi"]  = common.get_dPhi(df[name+"_B1_Phi"].values, df[name+"_B2_Phi"].values)
    df[name+"_Delta_Eta"]  = abs(df[name+"_B1_Eta"].values - df[name+"_B2_Eta"].values)
    df[name+"_Delta_Pt"]   = abs(df[name+"_B1_Pt"].values - df[name+"_B2_Pt"].values)
    df[name+"_Delta_R"]    = np.sqrt(df[name+"_Delta_Eta"].values**2 + df[name+"_Delta_Phi"].values**2)
    df[name+"_Delta_R3D"] = np.sqrt((df[name+"_Delta_Eta"].values/5.)**2 + \
                                (df[name+"_Delta_Phi"].values/(2.*np.pi))**2 + \
                                (df[name+"_Delta_Pt"].values/1000.))

    # reconstruct Z boson
    vectors = common.Vectors(df, name, ["B1", "B2"])
    vectors.add(["B1", "B2"], out = "Z")

    df[name+"_Pt"]  = vectors.get("Z", "Pt")
    df[name+"_Eta"] = vectors.get("Z", "Eta")
    df[name+"_M"]   = vectors.get("Z", "M")
    df[name+"_E"]   = vectors.get("Z", "E")

    # log values
    for obj in ["B1", "B2"]:
        df[name+"_"+obj+"_logPt"] = np.log(df[name+"_"+obj+"_Pt"].values)
        df[name+"_"+obj+"_logM"] = np.log(df[name+"_"+obj+"_M"].values)
        df[name+"_"+obj+"_logE"] = np.log(df[name+"_"+obj+"_E"].values)

    df[name+"_logPt"] = np.log(df[name+"_Pt"].values)
    df[name+"_logM"] = np.log(df[name+"_M"].values)
    df[name+"_logE"] = np.log(df[name+"_E"].values)

    # 3D opening angle
    df[name+"_Angle"] = vectors.getOpeningAngle("B1", "B2")

    # boost
    vectors.boost(["B1", "B2", "Z"], frame = "Z")

    # add boosted variables
    for obj in ["1", "2"]:
        df[name+"_Boosted"+obj+"_Pt"] = vectors.get(obj, "Pt", boostFrame = "Z")
        df[name+"_Boosted"+obj+"_M"] = vectors.get(obj, "M", boostFrame = "Z")
        df[name+"_Boosted"+obj+"_E"] = vectors.get(obj, "E", boostFrame = "Z")
        df[name+"_Boosted"+obj+"_Eta"] = vectors.get(obj, "Eta", boostFrame = "Z")
        df[name+"_Boosted"+obj+"_Phi"] = vectors.get(obj, "Phi", boostFrame = "Z")

        df[name+"_Boosted"+obj+"_logPt"] = np.log(df[name+"_Boosted"+obj+"_Pt"])

    # boosted angular differences
    #df[name+"_dPhi_boosted"] = common.get_dPhi(df[name+"_B1_Phi_boosted"].values, df[name+"_B2_Phi_boosted"].values)
    #df[name+"_dEta_boosted"] = abs(df[name+"_B1_Eta_boosted"].values - df[name+"_B2_Eta_boosted"].values)
    #df[name+"_dR_boosted"] = np.sqrt(df[name+"_dEta_boosted"].values**2 + df[name+"_dPhi_boosted"].values**2)
    #test

    return df

