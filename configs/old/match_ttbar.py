import numpy as np
import common

name = "ttbarReco"
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


def get_additional_objects():
    '''
    define dictionary of objects that are identified based on the reconstructed objects
    dictionary entries define the order by which the objects are defined.
    e.g. objects['Pt'] = [O1, O2] defiles O1 as the object with the highest Pt that is
    not part of the default reconstructed objects
    '''
    objects = {}
    objects["CSV"] = [
        "addB1_csv_ordered",
        "addB2_csv_ordered",
        ]
    objects["Pt"] = [
        "addB1_pt_ordered",
        "addB2_pt_ordered",
        ]
    objects["Pt_btag"] = [
        "addB1_pt_ordered_req_CSV_>_0.277",
        "addB2_pt_ordered_req_CSV_>_0.277",
        ]
    return objects


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "GenTopHad_Phi[0]",
        "GenTopHad_Eta[0]",
        "GenTopHad_M[0]",
        "GenTopLep_Phi[0]",
        "GenTopLep_Eta[0]",
        "GenTopLep_M[0]",

        "GenTopHad_B_Phi[0]",
        "GenTopHad_B_Eta[0]",
        "GenTopLep_B_Phi[0]",
        "GenTopLep_B_Eta[0]",

        "GenTopHad_Q1_Phi[0]",
        "GenTopHad_Q1_Eta[0]",
        "GenTopHad_Q2_Phi[0]",
        "GenTopHad_Q2_Eta[0]",

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

    # get vectors to build top quarks
    vectors = common.Vectors(df, name, ["HadTopB", "HadTopQ1", "HadTopQ2", "LepTopB"])

    # hadronic top quark
    vectors.add(["HadTopQ1","HadTopQ2"], out = "HadW")
    vectors.add(["HadTopB","HadTopQ1","HadTopQ2"], out = "HadTop")

    # leptonic top quark
    vectors.initIndexedVector(df, "TightLepton", 0)
    vectors.addNeutrino(df, "Evt_MET_Pt", "Evt_MET_Phi", "TightLepton_0")
    vectors.add(["TightLepton_0", "nu", "LepTopB"], out = "LepTop")

    # get ttbar system
    vectors.add(["HadTop", "LepTop"], out = "ttbar")


    # write ttbar variables to dataframe
    df[name+"_ttbar_Pt"]  = vectors.get("ttbar", "Pt")
    df[name+"_ttbar_Eta"] = vectors.get("ttbar", "Eta")
    df[name+"_ttbar_M"]   = vectors.get("ttbar", "M")
    df[name+"_ttbar_E"]   = vectors.get("ttbar", "E")
    
    df[name+"_ttbar_openingAngle"] = vectors.getOpeningAngle("HadTop", "LepTop")

    # write top variables to dataframe
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

    # mass corrections
    df["GenTopHad_massCorrection"] = df["GenTopHad_M[0]"].values/(df[name+"_HadTop_M"].values+1e-10)
    df["GenTopLep_massCorrection"] = df["GenTopLep_M[0]"].values/(df[name+"_LepTop_M"].values+1e-10)

    # get dR values of gen and reco top quarks
    df[name+"_dRGen_HadTop"] = common.get_dR(
        eta1 = df[name+"_HadTop_Eta"].values,
        phi1 = df[name+"_HadTop_Phi"].values,
        eta2 = df["GenTopHad_Eta[0]"].values,
        phi2 = df["GenTopHad_Phi[0]"].values)

    df[name+"_dRGen_LepTop"] = common.get_dR(
        eta1 = df[name+"_LepTop_Eta"].values,
        phi1 = df[name+"_LepTop_Phi"].values,
        eta2 = df["GenTopLep_Eta[0]"].values,
        phi2 = df["GenTopLep_Phi[0]"].values)

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

    df[name+"_dRGen_HadTopQ1"] = common.get_dR(
        eta1 = df[name+"_HadTopQ1_Eta"].values,
        phi1 = df[name+"_HadTopQ1_Phi"].values,
        eta2 = df["GenTopHad_Q1_Eta[0]"].values,
        phi2 = df["GenTopHad_Q1_Phi[0]"].values)

    df[name+"_dRGen_HadTopQ2"] = common.get_dR(
        eta1 = df[name+"_HadTopQ2_Eta"].values,
        phi1 = df[name+"_HadTopQ2_Phi"].values,
        eta2 = df["GenTopHad_Q2_Eta[0]"].values,
        phi2 = df["GenTopHad_Q2_Phi[0]"].values)

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
        name+"_dRGen_HadTopB",
        name+"_dRGen_HadTopQ1",
        name+"_dRGen_HadTopQ2",
        name+"_dRGen_LepTopB",
        ]
    return variables

def def_signal_selection():
    sig_selection = [
    "ttbarReco_HadTopB_CSV>0.277",
    "ttbarReco_LepTopB_CSV>0.277",
    ]
    return sig_selection

def def_background_selection():
    bkg_selection = [
    "ttbarReco_HadTopB_CSV>0.277",
    "ttbarReco_LepTopB_CSV>0.277",
    ]
    return bkg_selection

def def_dnn_reco_selection():
    dnn_reco_selection = [
    "ttbarReco_HadTopB_CSV>0.277",
    "ttbarReco_LepTopB_CSV>0.277",
    ]
    return dnn_reco_selection

def get_random_index(df, bestIndex):
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        # randomIndex = np.random.randint(0,df.shape[0])
        randomIndex = df.index[np.random.randint(0,df.shape[0])]
    return randomIndex
