import numpy as np
import common

name = "ttbarReco"
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
        "HadTopB",
        "LepTopB",
        "HadTopQ1",
        "HadTopQ2"
        ]
    return objects


def get_features():
    '''
    define a list of features applicable for all objects defined in get_objects()
    '''
    features = [
        "Eta", 
        "Phi",
        "CSV",
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
        "GenTopHad_Phi[0]",
        "GenTopHad_Eta[0]",
        "GenTopLep_Phi[0]",
        "GenTopLep_Eta[0]",

        "TightLepton_Pt[0]",
        "TightLepton_Eta[0]",
        "TightLepton_Phi[0]",
        "TightLepton_E[0]",
        "Evt_MET_Pt",
        "Evt_MET_Phi",

        "Evt_Odd",
        "N_Jets",
        "N_BTagsM",
        "Weight_XS",
        "Weight_CSV",
        "Weight_GEN_nom",
        "Evt_ID",
        "Evt_Run",
        "Evt_Lumi"
        ]
    return variables

def base_selection(event):
    return event.N_Jets>=4

def calculate_variables(df):
    '''
    calculate additional variables needed
    '''

    # build top quarks
    vectors = common.Vectors(df, name, ["HadTopB", "HadTopQ1", "HadTopQ2", "LepTopB"])
    # hadronic top quark
    vectors.add(["HadTopQ1","HadTopQ2"], out = "HadW")
    vectors.add(["HadTopB","HadTopQ1","HadTopQ2"], out = "HadTop")
    # leptonic top quark
    vectors.initIndexedVector(df, "TightLepton", 0)
    vectors.addNeutrino(df, "Evt_MET_Pt", "Evt_MET_Phi", "TightLepton_0")
    vectors.add(["TightLepton_0", "nu", "LepTopB"], out = "LepTop")

    # ttbar variables to df
    vectors.add(["HadTop", "LepTop"], out = "ttbar")

    df[name+"_ttbar_Pt"]  = vectors.get("ttbar", "Pt")
    df[name+"_ttbar_Eta"] = vectors.get("ttbar", "Eta")
    df[name+"_ttbar_M"]   = vectors.get("ttbar", "M")
    df[name+"_ttbar_E"]   = vectors.get("ttbar", "E")
    
    df[name+"_ttbar_openingAngle"] = vectors.getOpeningAngle("HadTop", "LepTop")

    df[name+"_LepTop_Pt"]  = vectors.get("LepTop", "Pt")
    df[name+"_LepTop_Eta"] = vectors.get("LepTop", "Eta")
    df[name+"_LepTop_M"]   = vectors.get("LepTop", "M")
    df[name+"_LepTop_E"]   = vectors.get("LepTop", "E")
    df[name+"_LepTop_Phi"] = vectors.get("LepTop", "Phi")

    df[name+"_HadTop_Pt"]  = vectors.get("HadTop", "Pt")
    df[name+"_HadTop_Eta"] = vectors.get("HadTop", "Eta")
    df[name+"_HadTop_M"]   = vectors.get("HadTop", "M")
    df[name+"_HadTop_E"]   = vectors.get("HadTop", "E")
    df[name+"_HadTop_Phi"] = vectors.get("HadTop", "Phi")

    # get dR values of gen and reco top quarks
    df[name+"_dRGen_had"] = common.get_dR(
        eta1 = df[name+"_HadTop_Eta"].values,
        phi1 = df[name+"_HadTop_Phi"].values,
        eta2 = df["GenTopHad_Eta[0]"].values,
        phi2 = df["GenTopHad_Phi[0]"].values)

    df[name+"_dRGen_lep"] = common.get_dR(
        eta1 = df[name+"_LepTop_Eta"].values,
        phi1 = df[name+"_LepTop_Phi"].values,
        eta2 = df["GenTopLep_Eta[0]"].values,
        phi2 = df["GenTopLep_Phi[0]"].values)

    
    # ttbar kinematic differences
    df[name+"_ttbar_dPhi"] = common.get_dPhi(
        df[name+"_LepTop_Phi"].values,
        df[name+"_HadTop_Phi"].values)
    df[name+"_ttbar_dEta"] = common.get_dPhi(
        df[name+"_HadTop_Eta"].values,
        df[name+"_LepTop_Eta"].values)
    df[name+"_ttbar_dPt"] = abs(
        df[name+"_HadTop_Pt"].values - \
        df[name+"_LepTop_Pt"].values)

    df[name+"_ttbar_dR"] = np.sqrt(
        df[name+"_ttbar_dEta"].values**2 + \
        df[name+"_ttbar_dPhi"].values**2)
    df[name+"_ttbar_dKin"] = np.sqrt(
        (df[name+"_ttbar_dPhi"].values/(2.*np.pi))**2 + \
        (df[name+"_ttbar_dEta"].values/(5.))**2 + \
        (df[name+"_ttbar_dPt"].values/(1000.))**2)
    return df

def get_match_variables():
    variables = [
        name+"_dRGen_had",
        name+"_dRGen_lep",
        ]
    return variables

def get_random_index(df, bestIndex):
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex
