import numpy as np
import common

name = "RecoX"
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
        "B2",
        ]
    return objects


def get_features():
    '''
    define a list of features applicable for all objects defined in get_objects()
    '''
    features = [
        "Eta", 
        "Phi",
        "btagValue",
        "M",
        "E",
        "Pt",
        ]
    return features


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "GenHiggs_B1_Phi",
        "GenHiggs_B2_Phi",
        "GenHiggs_B1_E",
        "GenHiggs_B2_E",
        "GenHiggs_B1_Eta",
        "GenHiggs_B2_Eta",
        "GenHiggs_B1_Pt",
        "GenHiggs_B2_Pt",

        "Evt_Odd",
        "N_Jets",
        "N_BTagsM",
        "Weight_XS",
        "Weight_btagSF",
        "Weight_GEN_nom",
        "Evt_ID",
        "Evt_Run",
        "Evt_Lumi",


        #add lepton variables
        "TightLepton_E[0]",
        "TightLepton_Eta[0]",
        "TightLepton_M[0]",
        "TightLepton_Phi[0]",
        "TightLepton_Pt[0]",

        ]
    return variables

def base_selection(event):
    return event.N_Jets>=2

def calculate_variables(df):
    '''
    calculate additional variables needed
    '''

    # genX vectors
    genvecs = common.Vectors(df, "GenHiggs", ["B1", "B2"])
    genvecs.add(["B1","B2"], out = "H")
    df["GenHiggs_H_M"] = genvecs.get("H","M")

    # recoX vectors
    vectors = common.Vectors(df, name, ["B1", "B2"])
    vectors.add(["B1","B2"], out = "X")

    # recoX variables to df
    df[name+"_X_Pt"]  = vectors.get("X", "Pt")
    df[name+"_X_Eta"] = vectors.get("X", "Eta")
    df[name+"_X_M"]   = vectors.get("X", "M")
    df[name+"_X_E"]   = vectors.get("X", "E")
    df[name+"_X_Phi"]   = vectors.get("X", "Phi")
    
    # correction for X mass
    df["GenHiggs_H_massCorrection"] = df["GenHiggs_H_M"].values/(df[name+"_X_M"].values+1e-10)

    # generator X opening angle
    df[name+"_X_openingAngle"] = vectors.getOpeningAngle("B1", "B2")
    df["GenHiggs_H_openingAngle"] = genvecs.getOpeningAngle("B1", "B2")

    # kinematic features of X constituents
    df[name+"_B1_Pt"]  = vectors.get("B1", "Pt")
    df[name+"_B1_Eta"] = vectors.get("B1", "Eta")
    df[name+"_B1_M"]   = vectors.get("B1", "M")
    df[name+"_B1_E"]   = vectors.get("B1", "E")
    df[name+"_B1_Phi"] = vectors.get("B1", "Phi")

    df[name+"_B2_Pt"]  = vectors.get("B2", "Pt")
    df[name+"_B2_Eta"] = vectors.get("B2", "Eta")
    df[name+"_B2_M"]   = vectors.get("B2", "M")
    df[name+"_B2_E"]   = vectors.get("B2", "E")
    df[name+"_B2_Phi"] = vectors.get("B2", "Phi")

    # get dR values of gen and reco top quarks
    df[name+"_dRGen_B1"] = common.get_dR(
        eta1 = df[name+"_B1_Eta"].values,
        phi1 = df[name+"_B1_Phi"].values,
        eta2 = df["GenHiggs_B1_Eta"].values,
        phi2 = df["GenHiggs_B1_Phi"].values)

    df[name+"_dRGen_B2"] = common.get_dR(
        eta1 = df[name+"_B2_Eta"].values,
        phi1 = df[name+"_B2_Phi"].values,
        eta2 = df["GenHiggs_B2_Eta"].values,
        phi2 = df["GenHiggs_B2_Phi"].values)


    #get delta variables of lepton and b-jets
    df[name+"_B1_dEta_lept"] = common.get_dEta(df["TightLepton_Eta[0]"].values,df[name+"_B1_Eta"].values)
    df[name+"_B2_dEta_lept"] = common.get_dEta(df["TightLepton_Eta[0]"].values,df[name+"_B2_Eta"].values)
    df[name+"_B1_dPhi_lept"] = common.get_dPhi(df["TightLepton_Phi[0]"].values,df[name+"_B1_Phi"].values)
    df[name+"_B2_dPhi_lept"] = common.get_dPhi(df["TightLepton_Phi[0]"].values,df[name+"_B2_Phi"].values)

    df[name+"_B1_dR_lept"] = common.get_dR(
         df["TightLepton_Eta[0]"].values,
         df["TightLepton_Phi[0]"].values,
         df[name+"_B1_Eta"].values,
         df[name+"_B1_Phi"].values)

    df[name+"_B2_dR_lept"] = common.get_dR(
         df["TightLepton_Eta[0]"].values,
         df["TightLepton_Phi[0]"].values,
         df[name+"_B2_Eta"].values,
         df[name+"_B2_Phi"].values)

    #get delta variables of lepton and X-boson
    df[name+"_X_dEta_lept"] = common.get_dEta(df["TightLepton_Eta[0]"].values,df[name+"_X_Eta"].values)
    df[name+"_X_dPhi_lept"] = common.get_dPhi(df["TightLepton_Phi[0]"].values,df[name+"_X_Phi"].values)

    df[name+"_X_dR_lept"] = common.get_dR(
         df["TightLepton_Eta[0]"].values,
         df["TightLepton_Phi[0]"].values,
         df[name+"_X_Eta"].values,
         df[name+"_X_Phi"].values)


    #get average of btag-values of the two b-jets
    df[name+"_X_btagAverage"] = (df[name+"_B1_btagValue"].values + df[name+"_B2_btagValue"].values) / 2.


    
    # ttbar kinematic differences
    df[name+"_X_dPhi"] = common.get_dPhi(
        df[name+"_B1_Phi"].values,
        df[name+"_B2_Phi"].values)
    df[name+"_X_dEta"] = common.get_dEta(
        df[name+"_B1_Eta"].values,
        df[name+"_B2_Eta"].values)
    df[name+"_X_dPt"] = abs(
        df[name+"_B1_Pt"].values - \
        df[name+"_B2_Pt"].values)

    df[name+"_X_dR"] = np.sqrt(
        df[name+"_X_dEta"].values**2 + \
        df[name+"_X_dPhi"].values**2)
    df[name+"_X_dKin"] = np.sqrt(
        (df[name+"_X_dPhi"].values/(2.*np.pi))**2 + \
        (df[name+"_X_dEta"].values/(5.))**2 + \
        (df[name+"_X_dPt"].values/(1000.))**2)

    return df

def get_match_variables():
    variables = [
        name+"_dRGen_B1",
        name+"_dRGen_B2",
        ]
    return variables

def get_random_index(df, bestIndex):
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex
