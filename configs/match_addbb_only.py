import numpy as np
import common

name = "addbbReco"
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
        "AddB1", # added
        "AddB2"  # added
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
        #added
        "AdditionalGenBJet_Phi[0]",     
        "AdditionalGenBJet_Eta[0]",     
        "AdditionalGenBJet_Pt[0]",      
        "AdditionalGenBJet_E[0]",       
        "N_AdditionalGenBJets",         
        "AdditionalGenBJet_Phi[1]",     
        "AdditionalGenBJet_Eta[1]",     
        "AdditionalGenBJet_Pt[1]",      
        "AdditionalGenBJet_E[1]",       
        "Evt_Dr_minDrTaggedJets",
        "Evt_M2_minDrTaggedJets",
        "Evt_Deta_minDetaTaggedJets",
        "Evt_M2_minM2TaggedJets",
        "Evt_M2_maxM2TaggedJets",
        "GenAdd_BB_inacceptance_jet",   
        "GenAdd_B_inacceptance_jet",
        "TaggedJet_Eta[0]",
        "TaggedJet_Pt[0]",
        "Jet_Pt[0]",
        "Jet_Pt[1]",
        "Jet_Pt[2]",
        "Jet_Pt[3]",
        "TaggedJet_Pt[1]",
        "CSV[0]",
        "CSV[1]",
        "CSV[2]",
        "CSV[3]",
        "GenEvt_I_TTPlusBB",
        ######    

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
    return event.N_Jets>=4 and event.N_AdditionalGenBJets >= 2 #TODO adjust

def calculate_variables(df):
    '''
    calculate additional variables needed
    '''

    #### Additional b jets #### 
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

    vectors.initIndexedVector(df, "AdditionalGenBJet", 0)
    vectors.initIndexedVector(df, "AdditionalGenBJet", 1)
    vectors.add(["AdditionalGenBJet_0", "AdditionalGenBJet_1"], out = "genbb")

    df[name+"_genbb_Pt"]  = vectors.get("genbb", "Pt")
    df[name+"_genbb_Eta"] = vectors.get("genbb", "Eta")
    df[name+"_genbb_M"]   = vectors.get("genbb", "M")
    df[name+"_genbb_E"]   = vectors.get("genbb", "E")

    df[name+"_genbb_dPhi"] = common.get_dPhi(df["AdditionalGenBJet_Phi[0]"].values, df["AdditionalGenBJet_Phi[1]"].values)
    df[name+"_genbb_dEta"] = abs(df["AdditionalGenBJet_Eta[0]"].values - df["AdditionalGenBJet_Eta[1]"].values)
    df[name+"_genbb_dPt"] = abs(df["AdditionalGenBJet_Pt[0]"].values - df["AdditionalGenBJet_Pt[1]"])
    df[name+"_genbb_dR"]   = np.sqrt(df[name+"_genbb_dPhi"].values**2 + df[name+"_genbb_dEta"].values**2)
    df[name+"_genbb_dKin"] = np.sqrt( (df[name+"_genbb_dPhi"].values/(2.*np.pi))**2 + \
                                   (df[name+"_genbb_dEta"].values/5.)**2 + \
                                   (df[name+"_genbb_dPt"].values/1000.)**2 )

    # new observables 
    df[name+"_bb_dR_minus_Evt_Dr_minDrTaggedJets"] = df[name+"_bb_dR"].values - df["Evt_Dr_minDrTaggedJets"].values
    df[name+"_bb_M_minus_Evt_M2_minDrTaggedJets"] = df[name+"_bb_M"].values - df["Evt_M2_minDrTaggedJets"].values
    df[name+"_bb_dEta_minus_Evt_Deta_minDetaTaggedJets"] = df[name+"_bb_dEta"].values - df["Evt_Deta_minDetaTaggedJets"].values
    df[name+"_bb_M_minus_Evt_M2_minM2TaggedJets"] = df[name+"_bb_M"].values - df["Evt_M2_minM2TaggedJets"].values
    df[name+"_bb_M_minus_Evt_M2_maxM2TaggedJets"] = df[name+"_bb_M"].values - df["Evt_M2_maxM2TaggedJets"].values
    
    df[name+"_Jet_Pt0"] = df["Jet_Pt[0]"].values
    df[name+"_Jet_Pt1"] = df["Jet_Pt[1]"].values
    df[name+"_Jet_Pt2"] = df["Jet_Pt[2]"].values
    df[name+"_Jet_Pt3"] = df["Jet_Pt[3]"].values
    df[name+"_AddB1_Pt"] = df[name+"_AddB1_Pt"].values
    df[name+"_AddB2_Pt"] = df[name+"_AddB2_Pt"].values

    df[name+"_CSV0"] = df["CSV[0]"].values
    df[name+"_CSV1"] = df["CSV[1]"].values
    df[name+"_CSV2"] = df["CSV[2]"].values
    df[name+"_CSV3"] = df["CSV[3]"].values
    df[name+"_AddB1_CSV"] = df[name+"_AddB1_CSV"].values
    df[name+"_AddB2_CSV"] = df[name+"_AddB2_CSV"].values



    return df

def get_match_variables():
    variables = [
        #name+"_dRGen_HadTopB",
        #name+"_dRGen_HadTopQ1",
        #name+"_dRGen_HadTopQ2",
        #name+"_dRGen_LepTopB",
        name+"_dRGen_0",    # added 
        name+"_dRGen_1",    # added 
        ]
    return variables

def get_random_index(df, bestIndex):
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex
