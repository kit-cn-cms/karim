import numpy as np
import common

name = "addbb"
def get_naming():
    '''
    define name for this reconstruction
    '''
    return name

def get_jet_collection():
    ''' define name of jet collection to read '''
    return "taggedJet", "nTagsM_SYS"

def get_objects():
    '''
    define a list of objects considered for the reconstruction
    '''
    objects = [
        "b1",
        "b2"
        ]
    return objects


def get_features():
    '''
    define a list of features applicable for all objects defined in get_objects()
    '''
    features = [
        "E_SYS", 
        "Eta_SYS",
        "M_SYS",
        "Phi_SYS",
        "Pt_SYS",
        "btagValue_SYS",
        ]
    return features


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "Lep_E[0]",
        "Lep_Eta[0]",
        "Lep_M[0]",
        "Lep_Phi[0]",
        "Lep_Pt[0]",

        "MET_T1_Phi_SYS",
        "MET_T1_Pt_SYS",

        "nJets_SYS",
        "nTagsM_SYS",
        "nTagsT_SYS",
        ]
    return variables

def get_output_variables():
    '''
    write all variables to be written out to the friend tree in this list
    '''
    variables = [
        name+"_Pt",
        name+"_Eta",
        name+"_M",
        name+"_E",
        name+"_dPhi",
        name+"_dEta",
        name+"_dR",
        "nJets_SYS",
        "nTagsM_SYS",
        ]
    return variables

def base_selection(event, syst = "nom"):
    return getattr(event, "nJets_"+syst) >= 6 and getattr(event, "nTagsM_"+syst) >= 4

def calculate_variables(df, syst = "nom"):
    '''
    calculate additional variables needed
    '''

    # get vectors to build top quarks
    vectors = common.Vectors(df, name, ["b1", "b2"], jecDependent = True)

    # get add bb system
    vectors.add(["b1", "b2"], out = "addbb")

    # lepton
    vectors.initIndexedVector(df, "Lep", 0)
    # met
    #vectors.addNeutrino(df, "MET_T1_Pt_SYS", "MET_T1_Phi_SYS", "Lep_0")

    # write ttbar variables to dataframe
    df[name+"_Pt"]  = vectors.get("addbb", "Pt")
    df[name+"_Eta"] = vectors.get("addbb", "Eta")
    df[name+"_M"]   = vectors.get("addbb", "M")
    df[name+"_E"]   = vectors.get("addbb", "E")
    
    df[name+"_dPhi"]  = common.get_dPhi(df[name+"_b1_Phi_SYS"].values, df[name+"_b2_Phi_SYS"].values)
    df[name+"_dEta"]  = abs(df[name+"_b1_Eta_SYS"].values - df[name+"_b2_Eta_SYS"].values)
    df[name+"_dR"]  = np.sqrt(df[name+"_dPhi"].values**2 + df[name+"_dEta"]**2)

    return df

def get_match_variables():
    ''' function not needed '''
    variables = [
        ]
    return variables

def get_random_index(df, bestIndex):
    ''' function not needed '''
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex
