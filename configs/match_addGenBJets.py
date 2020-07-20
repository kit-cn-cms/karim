import numpy as np
import common

name = "ttbbReco"
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
        "AddB1", 
        "AddB2"       
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
        "AdditionalGenBJet_Phi[0]",
        "AdditionalGenBJet_Eta[0]",
        "N_AdditionalGenBJets",
        "AdditionalGenBJet_Phi[1]",
        "AdditionalGenBJet_Eta[1]",

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
    return event.N_AdditionalGenBJets >= 2

def calculate_variables(df):
    '''
    calculate additional variables needed
    '''

    df[name+"_dPhiGen_0"]  = common.get_dPhi(df[name+"_AddB1_Phi"].values, df["AdditionalGenBJet_Phi[0]"].values)
    df[name+"_dPhiGen_1"]  = common.get_dPhi(df[name+"_AddB2_Phi"].values, df["AdditionalGenBJet_Phi[1]"].values)
    df[name+"_dEtaGen_0"]  = abs(df[name+"_AddB1_Eta"].values - df["AdditionalGenBJet_Eta[0]"].values)
    df[name+"_dEtaGen_1"]  = abs(df[name+"_AddB2_Eta"].values - df["AdditionalGenBJet_Eta[1]"].values)
    df[name+"_dRGen_0"] = np.sqrt(df[name+"_dPhiGen_0"].values**2 + df[name+"_dEtaGen_0"].values**2)
    df[name+"_dRGen_1"] = np.sqrt(df[name+"_dPhiGen_1"].values**2 + df[name+"_dEtaGen_1"].values**2)

    
    df[name+"_bb_dPhi"] = common.get_dPhi(df[name+"_AddB1_Phi"].values, df[name+"_AddB2_Phi"])
    df[name+"_bb_dEta"] = abs(df[name+"_AddB1_Eta"].values - df[name+"_AddB2_Eta"])
    df[name+"_bb_dPt"] = abs(df[name+"_AddB1_Pt"].values - df[name+"_AddB2_Pt"])
    df[name+"_bb_dR"]   = np.sqrt(df[name+"_bb_dPhi"].values**2 + df[name+"_bb_dEta"].values**2)
    df[name+"_bb_dKin"] = np.sqrt( (df[name+"_bb_dPhi"].values/(2.*np.pi))**2 + \
                                   (df[name+"_bb_dEta"].values/5.)**2 + \
                                   (df[name+"_bb_dPt"].values/1000.)**2 )

    vectors = common.Vectors(df, name, ["AddB1", "AddB2"])
    vectors.add(["AddB1", "AddB2"], out = "bb")

    df[name+"_bb_Pt"]  = vectors.get("bb", "Pt")
    df[name+"_bb_Eta"] = vectors.get("bb", "Eta")
    df[name+"_bb_M"]   = vectors.get("bb", "M")
    df[name+"_bb_E"]   = vectors.get("bb", "E")
    
    df[name+"_bb_openingAngle"] = vectors.getOpeningAngle("AddB1", "AddB2")

    vectors.initIndexedVector(df, "TightLepton", 0)
    vectors.addNeutrino(df, "Evt_MET_Pt", "Evt_MET_Phi", "TightLepton_0")
    #vectors.add(["TightLepton", "nu"], out = "lepW")

    vectors.add(["TightLepton_0", "nu", "AddB1"], out = "lepTop1")
    vectors.add(["TightLepton_0", "nu", "AddB2"], out = "lepTop2")

    #df[name+"_lepW_Pt"] = vectors.get("lepW", "Pt")
    #df[name+"_lepW_M"]  = vectors.get("lepW", "M")

    df[name+"_lepTop1_Pt"]  = vectors.get("lepTop1", "Pt")
    df[name+"_lepTop1_Eta"] = vectors.get("lepTop1", "Eta")
    df[name+"_lepTop1_M"]   = vectors.get("lepTop1", "M")
    df[name+"_lepTop1_E"]   = vectors.get("lepTop1", "E")

    df[name+"_lepTop2_Pt"]  = vectors.get("lepTop2", "Pt")
    df[name+"_lepTop2_Eta"] = vectors.get("lepTop2", "Eta")
    df[name+"_lepTop2_M"]   = vectors.get("lepTop2", "M")
    df[name+"_lepTop2_E"]   = vectors.get("lepTop2", "E")

    return df

def get_match_variables():
    variables = [
        name+"_dRGen_0",
        name+"_dRGen_1",
        ]
    return variables

def get_random_index(df, bestIndex):
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex
