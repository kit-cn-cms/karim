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
        "jet1",
        "jet2",
        # "HadTopQ1",
        # "HadTopQ2"
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
        "DeepJet_b",
        "DeepJet_bb",
        "DeepJet_c",
        "DeepJet_g",
        "DeepJet_lepb",
        "DeepJet_uds",
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
    return objects


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "TightLepton_Pt[0]",
        "TightLepton_Eta[0]",
        "TightLepton_Phi[0]",
        "TightLepton_E[0]",
        "TightLepton_M[0]",

        "Evt_Odd",
        "N_Jets",
        "N_BTagsM",
        "Weight_XS",
        "Weight_btagSF",
        "Weight_GEN_nom",
        "Evt_ID",
        "Evt_Run",
        "Evt_Lumi",

        #variables added from Thomas Hsu
        'Evt_Deta_JetsAverage',
        'Evt_Deta_TaggedJetsAverage',
        'Evt_Deta_maxDetaJetJet',
        'Evt_Deta_maxDetaJetTag',
        'Evt_Deta_maxDetaTagTag',
        'Evt_Dr_JetsAverage',
        'Evt_Dr_TaggedJetsAverage',
        'Evt_Dr_closestTo91TaggedJets',
        'Evt_Dr_maxDrJets',
        'Evt_Dr_maxDrTaggedJets',
        'Evt_Dr_minDrJets',
        'Evt_Dr_minDrLepJet',
        'Evt_Dr_minDrLepTag',
        'Evt_Dr_minDrTaggedJets',
        'Evt_E_JetsAverage',
        'Evt_E_TaggedJetsAverage',
        'Evt_Eta_JetsAverage',
        'Evt_Eta_TaggedJetsAverage',
        'Evt_HT',
        'Evt_HT_jets',
        'Evt_HT_tags',
        'Evt_HT_wo_MET',
        'Evt_JetPt_over_JetE',
        'Evt_M2_JetsAverage',
        'Evt_M2_TaggedJetsAverage',
        'Evt_M2_closestTo125TaggedJets',
        'Evt_M2_closestTo91TaggedJets',
        'Evt_M2_minDrJets',
        'Evt_M2_minDrTaggedJets',
        'Evt_M3',
        'Evt_MET',
        'Evt_MET_Phi',
        'Evt_MET_Pt',
        'Evt_MHT',
        'Evt_MTW',
        'Evt_M_JetsAverage',
        'Evt_M_TaggedJetsAverage',
        'Evt_M_Total',
        'Evt_M_minDrLepJet',
        'Evt_M_minDrLepTag',
        'Evt_Pt_JetsAverage',
        'Evt_Pt_TaggedJetsAverage',
        'Evt_Pt_minDrJets',
        'Evt_Pt_minDrTaggedJets',
        'Evt_TaggedJetPt_over_TaggedJetE',
        'Evt_aplanarity',
        'Evt_aplanarity_jets',
        'Evt_aplanarity_tags',
        'Evt_blr',
        'Evt_blr_transformed',
        'Evt_btagValue_avg',
        'Evt_btagValue_avg_tagged',
        'Evt_btagValue_dev',
        'Evt_btagValue_dev_tagged',
        'Evt_btagValue_min',
        'Evt_btagValue_min_tagged',
        'Evt_h0',
        'Evt_h1',
        'Evt_h2',
        'Evt_h3',
        'Evt_sphericity',
        'Evt_sphericity_jets',
        'Evt_sphericity_tags',
        'Evt_transverse_sphericity',
        'Evt_transverse_sphericity_jets',
        'Evt_transverse_sphericity_tags',


        'N_BTagsL',
        'N_BTagsT',
        'N_LooseJets',
        ]
    return variables

def base_selection(event):
    return event.N_Jets >= 2

def calculate_variables(df):
    '''
    calculate additional variables needed
    '''

    #Rename lepton variables
    #Otherwise the generateSubmitScript wouldnt find the variables!!
    df["TightLepton_E_0"] = df["TightLepton_E[0]"].values
    df["TightLepton_Eta_0"] = df["TightLepton_Eta[0]"].values
    df["TightLepton_M_0"] = df["TightLepton_M[0]"].values
    df["TightLepton_Phi_0"] = df["TightLepton_Phi[0]"].values
    df["TightLepton_Pt_0"] = df["TightLepton_Pt[0]"].values


    # get vectors to build top quarks
    vectors = common.Vectors(df, name, ["jet1", "jet2"]) # new
    vectors.add(["jet1", "jet2"], out = "X")


    # recoX variables to df
    df[name+"_X_Pt"]  = vectors.get("X", "Pt")
    df[name+"_X_Eta"] = vectors.get("X", "Eta")
    df[name+"_X_M"]   = vectors.get("X", "M")
    df[name+"_X_E"]   = vectors.get("X", "E")
    df[name+"_X_Phi"]   = vectors.get("X", "Phi")
    df[name+"_X_openingAngle"] = vectors.getOpeningAngle("jet1", "jet2")

    #get average of btag-values of the two b-jets
    df[name+"_X_btagAverage"] = (df[name+"_jet1_btagValue"].values + df[name+"_jet2_btagValue"].values) / 2.
    

    # kinematic features of X constituents
    df[name+"_jet1_Pt"]  = vectors.get("jet1", "Pt")
    df[name+"_jet1_Eta"] = vectors.get("jet1", "Eta")
    df[name+"_jet1_M"]   = vectors.get("jet1", "M")
    df[name+"_jet1_E"]   = vectors.get("jet1", "E")
    df[name+"_jet1_Phi"] = vectors.get("jet1", "Phi")

    df[name+"_jet2_Pt"]  = vectors.get("jet2", "Pt")
    df[name+"_jet2_Eta"] = vectors.get("jet2", "Eta")
    df[name+"_jet2_M"]   = vectors.get("jet2", "M")
    df[name+"_jet2_E"]   = vectors.get("jet2", "E")
    df[name+"_jet2_Phi"] = vectors.get("jet2", "Phi")


    # log values
    for obj in ["jet1", "jet2", "X"]:
        df[name+"_"+obj+"_logPt"] = np.log(df[name+"_"+obj+"_Pt"].values)
        df[name+"_"+obj+"_logM"] = np.log(df[name+"_"+obj+"_M"].values)
        df[name+"_"+obj+"_logE"] = np.log(df[name+"_"+obj+"_E"].values)

    # boost
    vectors.boost(["jet1", "jet2", "X"], frame = "X")

    # add boosted variables
    for obj in ["jet1", "jet2", "X"]:
        df[name+"_"+obj+"_Pt_boosted"] = vectors.get(obj, "Pt", boostFrame = "X")
        df[name+"_"+obj+"_M_boosted"] = vectors.get(obj, "M", boostFrame = "X")
        df[name+"_"+obj+"_E_boosted"] = vectors.get(obj, "E", boostFrame = "X")
        df[name+"_"+obj+"_Eta_boosted"] = vectors.get(obj, "Eta", boostFrame = "X")
        df[name+"_"+obj+"_Phi_boosted"] = vectors.get(obj, "Phi", boostFrame = "X")

        df[name+"_"+obj+"_logPt_boosted"] = np.log(df[name+"_"+obj+"_Pt_boosted"])

    # boosted angular differences
    df[name+"_dPhi_boosted"] = common.get_dPhi(df[name+"_jet1_Phi_boosted"].values, df[name+"_jet2_Phi_boosted"].values)
    df[name+"_dEta_boosted"] = abs(df[name+"_jet1_Eta_boosted"].values - df[name+"_jet2_Eta_boosted"].values)
    df[name+"_dR_boosted"] = np.sqrt(df[name+"_dEta_boosted"].values**2 + df[name+"_dPhi_boosted"].values**2)


    #get delta variables of lepton and b-jets
    df[name+"_jet1_dEta_lept"] = common.get_dEta(df["TightLepton_Eta[0]"].values,df[name+"_jet1_Eta"].values)
    df[name+"_jet2_dEta_lept"] = common.get_dEta(df["TightLepton_Eta[0]"].values,df[name+"_jet2_Eta"].values)
    df[name+"_jet1_dPhi_lept"] = common.get_dPhi(df["TightLepton_Phi[0]"].values,df[name+"_jet1_Phi"].values)
    df[name+"_jet2_dPhi_lept"] = common.get_dPhi(df["TightLepton_Phi[0]"].values,df[name+"_jet2_Phi"].values)

    df[name+"_jet1_dR_lept"] = common.get_dR(
         df["TightLepton_Eta[0]"].values,
         df["TightLepton_Phi[0]"].values,
         df[name+"_jet1_Eta"].values,
         df[name+"_jet1_Phi"].values)

    df[name+"_jet2_dR_lept"] = common.get_dR(
         df["TightLepton_Eta[0]"].values,
         df["TightLepton_Phi[0]"].values,
         df[name+"_jet2_Eta"].values,
         df[name+"_jet2_Phi"].values)


    #get delta variables of lepton and X-boson
    df[name+"_X_dEta_lept"] = common.get_dEta(df["TightLepton_Eta[0]"].values,df[name+"_X_Eta"].values)
    df[name+"_X_dPhi_lept"] = common.get_dPhi(df["TightLepton_Phi[0]"].values,df[name+"_X_Phi"].values)

    df[name+"_X_dR_lept"] = common.get_dR(
         df["TightLepton_Eta[0]"].values,
         df["TightLepton_Phi[0]"].values,
         df[name+"_X_Eta"].values,
         df[name+"_X_Phi"].values)



    vectors.initIndexedVector(df, "TightLepton", 0)
    vectors.add(["TightLepton_0", "jet2"], out = "LepTopBTightLepton")
    vectors.add(["TightLepton_0", "jet1"], out = "HadTopBTightLepton")

    df[name+"_jet2_M_lept"]   = vectors.get("LepTopBTightLepton", "M")
    df[name+"_jet1_M_lept"]   = vectors.get("HadTopBTightLepton", "M")



    df[name+"_X_dPhi"] = common.get_dPhi(
        df[name+"_jet1_Phi"].values,
        df[name+"_jet2_Phi"].values)
    df[name+"_X_dEta"] = common.get_dEta(
        df[name+"_jet1_Eta"].values,
        df[name+"_jet2_Eta"].values)
    df[name+"_X_dPt"] = abs(
        df[name+"_jet1_Pt"].values - \
        df[name+"_jet2_Pt"].values)

    df[name+"_X_dR"] = np.sqrt(
        df[name+"_X_dEta"].values**2 + \
        df[name+"_X_dPhi"].values**2)
    df[name+"_X_dKin"] = np.sqrt(
        (df[name+"_X_dPhi"].values/(2.*np.pi))**2 + \
        (df[name+"_X_dEta"].values/(5.))**2 + \
        (df[name+"_X_dPt"].values/(1000.))**2)


    # c-tag information
    df[name+"_jet1_CvsL_deepJet"] = df[name+"_jet1_DeepJet_c"].values/ \
        (df[name+"_jet1_DeepJet_c"].values + df[name+"_jet1_DeepJet_uds"].values + df[name+"_jet1_DeepJet_g"].values)
    df[name+"_jet1_CvsB_deepJet"] = df[name+"_jet1_DeepJet_c"].values/ \
        (df[name+"_jet1_DeepJet_c"].values + df[name+"_jet1_DeepJet_b"].values + df[name+"_jet1_DeepJet_bb"].values + df[name+"_jet1_DeepJet_lepb"].values)


    df[name+"_jet2_CvsL_deepJet"] = df[name+"_jet2_DeepJet_c"].values/ \
        (df[name+"_jet2_DeepJet_c"].values + df[name+"_jet2_DeepJet_uds"].values + df[name+"_jet2_DeepJet_g"].values)
    df[name+"_jet2_CvsB_deepJet"] = df[name+"_jet2_DeepJet_c"].values/ \
        (df[name+"_jet2_DeepJet_c"].values + df[name+"_jet2_DeepJet_b"].values + df[name+"_jet2_DeepJet_bb"].values + df[name+"_jet2_DeepJet_lepb"].values)

    return df

def get_match_variables():
    variables = [
        name+"_dRGen_jet1",
        # name+"_dRGen_HadTopQ1",
        # name+"_dRGen_HadTopQ2",
        name+"_dRGen_jet2",
        ]
    return variables

def def_signal_selection():
    sig_selection = [
    #name+"_jet1_btagValue>0.3033",
    #name+"_jet2_btagValue>0.3033",
    ]
    return sig_selection

def def_background_selection():
    bkg_selection = [
    #name+"_jet1_btagValue>0.3033",
    #name+"_jet2_btagValue>0.3033",
    ]
    return bkg_selection

def def_dnn_reco_selection():
    dnn_reco_selection = [
    #name+"_jet1_btagValue>0.3033",
    #name+"_jet2_btagValue>0.3033",
    ]
    return dnn_reco_selection
