import numpy as np
import common

name = "bbTop"
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
        "HadTopB",
        "LepTopB",
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

def get_additional_objects():
    '''
    define dictionary of objects that are identified based on the reconstructed objects
    dictionary entries define the order by which the objects are defined.
    e.g. objects['Pt'] = [O1, O2] defiles O1 as the object with the highest Pt that is
    not part of the default reconstructed objects
    '''
    objects = {}
    objects["btagValue"] = [
        "addB1_btag_ordered",
        "addB2_btag_ordered",
        ]
    objects["Pt"] = [
        "addB1_pt_ordered",
        "addB2_pt_ordered",
        ]
    return objects


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "GenTopHad_B_Phi[0]",
        "GenTopHad_B_Eta[0]",
        "GenTopLep_B_Phi[0]",
        "GenTopLep_B_Eta[0]",

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
        "Weight_btagSF",
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

    # get vectors to build top quarks
    vectors = common.Vectors(df, name, ["HadTopB", "LepTopB"])

    # leptonic top quark
    vectors.initIndexedVector(df, "TightLepton", 0)
    vectors.add(["TightLepton_0", "LepTopB"], out = "LepTop")

    # get ttbar b system
    vectors.add(["HadTopB", "LepTopB"], out = "bb")


    # write ttbar variables to dataframe
    df[name+"_lepBhadB_M"]   = vectors.get("bb", "M")
    
    df[name+"_lepBhadB_openingAngle"] = vectors.getOpeningAngle("HadTopB","LepTopB")

    # get dR values of jets
    df[name+"_dRGen_LepTopB"] = common.get_dR(
        eta1 = df[name+"_LepTopB_Eta"].values,
        phi1 = df[name+"_LepTopB_Phi"].values,
        eta2 = df["GenTopLep_B_Eta[0]"].values,
        phi2 = df["GenTopLep_B_Phi[0]"].values)

    df[name+"_dRGen_HadTopB"] = common.get_dR(
        eta1 = df[name+"_HadTopB_Eta"].values,
        phi1 = df[name+"_HadTopB_Phi"].values,
        eta2 = df["GenTopHad_B_Eta[0]"].values,
        phi2 = df["GenTopHad_B_Phi[0]"].values)

    # b kinematic differences
    df[name+"_lepBhadB_dPhi"] = common.get_dPhi(
        df[name+"_LepTopB_Phi"].values,
        df[name+"_HadTopB_Phi"].values)

    df[name+"_lepBhadB_dEta"] = common.get_dPhi(
        df[name+"_LepTopB_Eta"].values,
        df[name+"_HadTopB_Eta"].values)

    df[name+"_lepBhadB_dR"] = np.sqrt(
        df[name+"_lepBhadB_dEta"].values**2 + \
        df[name+"_lepBhadB_dPhi"].values**2)

    return df

def get_match_variables():
    variables = [
        name+"_dRGen_HadTopB",
        name+"_dRGen_LepTopB",
        ]
    return variables

def get_random_index(df, bestIndex):
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex
