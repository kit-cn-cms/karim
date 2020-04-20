import numpy as np
import common

name = "RecoZ"
def get_naming():
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

        "GenZ_B1_Phi",
        "GenZ_B2_Phi",
        "GenZ_B1_Eta",
        "GenZ_B2_Eta",

        ]
    return variables

def base_selection(event):
    return event.N_Jets>=2


def calculate_variables(df):
    '''
    calculate additional variables needed for DNN input
    '''

    # angular differences
    df[name+"_Z_dPhi"]  = common.get_dPhi(df[name+"_B1_Phi"].values, df[name+"_B2_Phi"].values)
    df[name+"_Z_dEta"]  = abs(df[name+"_B1_Eta"].values - df[name+"_B2_Eta"].values)
    df[name+"_Z_dPt"]   = abs(df[name+"_B1_Pt"].values - df[name+"_B2_Pt"].values)
    df[name+"_Z_dR"]    = np.sqrt(df[name+"_Z_dEta"].values**2 + df[name+"_Z_dPhi"].values**2)
    df[name+"_Z_dKin"] = np.sqrt((df[name+"_Z_dEta"].values/5.)**2 + \
                                (df[name+"_Z_dPhi"].values/(2.*np.pi))**2 + \
                                (df[name+"_Z_dPt"].values/1000.))

    # reconstruct Z boson
    vectors = common.Vectors(df, name, ["B1", "B2"])
    vectors.add(["B1", "B2"], out = "Z")

    df[name+"_Z_Pt"]  = vectors.get("Z", "Pt")
    df[name+"_Z_Eta"] = vectors.get("Z", "Eta")
    df[name+"_Z_M"]   = vectors.get("Z", "M")
    df[name+"_Z_E"]   = vectors.get("Z", "E")

    # log values
    for obj in ["B1", "B2", "Z"]:
        df[name+"_"+obj+"_logPt"] = np.log(df[name+"_"+obj+"_Pt"].values)
        df[name+"_"+obj+"_logM"] = np.log(df[name+"_"+obj+"_M"].values)
        df[name+"_"+obj+"_logE"] = np.log(df[name+"_"+obj+"_E"].values)

    # 3D opening angle
    df[name+"_Z_openingAngle"] = vectors.getOpeningAngle("B1", "B2")

    # boost
    vectors.boost(["B1", "B2", "Z"], frame = "Z")

    # add boosted variables
    for obj in ["B1", "B2", "Z"]:
        df[name+"_"+obj+"_Pt_boosted"] = vectors.get(obj, "Pt", boostFrame = "Z")
        df[name+"_"+obj+"_M_boosted"] = vectors.get(obj, "M", boostFrame = "Z")
        df[name+"_"+obj+"_E_boosted"] = vectors.get(obj, "E", boostFrame = "Z")
        df[name+"_"+obj+"_Eta_boosted"] = vectors.get(obj, "Eta", boostFrame = "Z")
        df[name+"_"+obj+"_Phi_boosted"] = vectors.get(obj, "Phi", boostFrame = "Z")

        df[name+"_"+obj+"_logPt_boosted"] = np.log(df[name+"_"+obj+"_Pt_boosted"])

    # boosted angular differences
    df[name+"_dPhi_boosted"] = common.get_dPhi(df[name+"_B1_Phi_boosted"].values, df[name+"_B2_Phi_boosted"].values)
    df[name+"_dEta_boosted"] = abs(df[name+"_B1_Eta_boosted"].values - df[name+"_B2_Eta_boosted"].values)
    df[name+"_dR_boosted"] = np.sqrt(df[name+"_dEta_boosted"].values**2 + df[name+"_dPhi_boosted"].values**2)

    df[name+"_dRGen_Z_genB1_recoB1"] = common.get_dR(
        eta1 = df["GenZ_B1_Eta"].values,
        phi1 = df["GenZ_B1_Phi"].values,
        eta2 = df[name+"_B1_Eta"].values,
        phi2 = df[name+"_B1_Phi"].values)

    df[name+"_dRGen_Z_genB2_recoB2"] = common.get_dR(
        eta1 = df["GenZ_B2_Eta"].values,
        phi1 = df["GenZ_B2_Phi"].values,
        eta2 = df[name+"_B2_Eta"].values,
        phi2 = df[name+"_B2_Phi"].values)

    df[name+"_dRGen_Z_genB1_recoB2"] = common.get_dR(
        eta1 = df["GenZ_B1_Eta"].values,
        phi1 = df["GenZ_B1_Phi"].values,
        eta2 = df[name+"_B2_Eta"].values,
        phi2 = df[name+"_B2_Phi"].values)

    df[name+"_dRGen_Z_genB2_recoB1"] = common.get_dR(
        eta1 = df["GenZ_B2_Eta"].values,
        phi1 = df["GenZ_B2_Phi"].values,
        eta2 = df[name+"_B1_Eta"].values,
        phi2 = df[name+"_B1_Phi"].values)
    return df

