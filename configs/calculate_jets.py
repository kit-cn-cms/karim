import numpy as np
import common
from array import array

btagWP = 0.3033
def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "Evt_Odd",
        "N_Jets",
        "N_BTagsM",
        "Weight_XS",
        "Weight_btagSF",
        "Weight_GEN_nom",
        "Evt_ID",
        "Evt_Run",
        "Evt_Lumi"
        "GenEvt_I_TTPlusBB",
        "GenEvt_I_TTPlusCC",

        "Jet_btagValue",
        "Jet_DeepCSV",
        "Jet_DeepCSV_b",
        "Jet_DeepCSV_bb",
        "Jet_DeepCSV_c",
        "Jet_DeepCSV_udsg",
        "Jet_DeepJet_b",
        "Jet_DeepJet_bb",
        "Jet_DeepJet_c",
        "Jet_DeepJet_g",
        "Jet_DeepJet_lepb",
        "Jet_DeepJet_uds",

        "Jet_Flav",
        "Jet_E",
        "Jet_Eta",
        "Jet_M",
        "Jet_PartonFlav",
        "Jet_Phi",
        "Jet_Pt",
        "Jet_Charge",

        "TightLepton_Pt",
        "TightLepton_Eta",
        "TightLepton_Phi",
        "TightLepton_E",
        ]
    return variables

def base_selection(event):
    return event.N_Jets>=4

def set_branches(wrapper):
    wrapper.SetIntVar("Evt_ID")   
    wrapper.SetIntVar("Evt_Run")   
    wrapper.SetIntVar("Evt_Lumi")   
    wrapper.SetIntVar("Evt_JetIdx")   
    wrapper.SetIntVar("GenEvt_I_TTPlusBB")   
    wrapper.SetIntVar("GenEvt_I_TTPlusCC")   
    wrapper.SetIntVar("N_Jets")   
    wrapper.SetIntVar("N_BTagsM")   

    wrapper.SetIntVar("isTagged")
    wrapper.SetIntVar("jetFlavor")
    wrapper.SetIntVar("jetPartonFlavor")

    wrapper.SetFloatVar("jetEnergy")
    wrapper.SetFloatVar("jetPt")
    wrapper.SetFloatVar("jetMass")
    wrapper.SetFloatVar("jetPhi")
    wrapper.SetFloatVar("jetEta")
    wrapper.SetFloatVar("jetCharge")

    wrapper.SetFloatVar("deepJetValue")
    wrapper.SetFloatVar("deepCSVValue")

    wrapper.SetFloatVar("deepJet_CvsL")
    wrapper.SetFloatVar("deepJet_CvsB")
    wrapper.SetFloatVar("deepCSV_CvsL")
    wrapper.SetFloatVar("deepCSV_CvsB")

    wrapper.SetFloatVar("leptonPt")
    wrapper.SetFloatVar("leptonEta")
    wrapper.SetFloatVar("leptonPhi")
    wrapper.SetFloatVar("leptonE")

def calculate_variables(event, wrapper, jetIdx):
    '''
    calculate additional variables needed
    '''
    wrapper.branchArrays["Evt_ID"][0] = event.Evt_ID
    wrapper.branchArrays["Evt_Run"][0] = event.Evt_Run
    wrapper.branchArrays["Evt_Lumi"][0] = event.Evt_Lumi
    wrapper.branchArrays["Evt_JetIdx"][0] = jetIdx
    try:
        wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = event.GenEvt_I_TTPlusBB 
        wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = event.GenEvt_I_TTPlusCC
    except:
        wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = -1
        wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = -1
    wrapper.branchArrays["N_Jets"][0] = event.N_Jets
    wrapper.branchArrays["N_BTagsM"][0] = event.N_BTagsM
    
    CvsL_deepJet = event.Jet_DeepJet_c[jetIdx]/ \
        (event.Jet_DeepJet_c[jetIdx] + event.Jet_DeepJet_uds[jetIdx] + event.Jet_DeepJet_g[jetIdx])
    CvsB_deepJet = event.Jet_DeepJet_c[jetIdx]/ \
        (event.Jet_DeepJet_c[jetIdx] + event.Jet_DeepJet_b[jetIdx] + event.Jet_DeepJet_bb[jetIdx] + event.Jet_DeepJet_lepb[jetIdx])
    CvsL_deepCSV = event.Jet_DeepCSV_c[jetIdx]/ \
        (event.Jet_DeepCSV_c[jetIdx] + event.Jet_DeepCSV_udsg[jetIdx])
    CvsB_deepCSV = event.Jet_DeepCSV_c[jetIdx]/ \
        (event.Jet_DeepCSV_c[jetIdx] + event.Jet_DeepCSV_b[jetIdx] + event.Jet_DeepCSV_bb[jetIdx])

    wrapper.branchArrays["deepJet_CvsL"][0] = CvsL_deepJet
    wrapper.branchArrays["deepJet_CvsB"][0] = CvsB_deepJet
    wrapper.branchArrays["deepCSV_CvsL"][0] = CvsL_deepCSV
    wrapper.branchArrays["deepCSV_CvsB"][0] = CvsB_deepCSV

    wrapper.branchArrays["jetFlavor"][0] = int(event.Jet_Flav[jetIdx])
    wrapper.branchArrays["jetPartonFlavor"][0] = int(event.Jet_PartonFlav[jetIdx])

    wrapper.branchArrays["jetEnergy"][0] = event.Jet_E[jetIdx]
    wrapper.branchArrays["jetPt"][0] = event.Jet_Pt[jetIdx]
    wrapper.branchArrays["jetMass"][0] = event.Jet_M[jetIdx]
    wrapper.branchArrays["jetEta"][0] = event.Jet_Eta[jetIdx]
    wrapper.branchArrays["jetCharge"][0] = event.Jet_Charge[jetIdx]
    wrapper.branchArrays["jetPhi"][0] = event.Jet_Phi[jetIdx]

    wrapper.branchArrays["deepJetValue"][0] = event.Jet_btagValue[jetIdx]
    wrapper.branchArrays["deepCSVValue"][0] = event.Jet_DeepCSV[jetIdx]

    
    if event.Jet_btagValue[jetIdx] >= btagWP:
        wrapper.branchArrays["isTagged"][0] = 1
    else:
        wrapper.branchArrays["isTagged"][0] = 0

    wrapper.branchArrays["leptonPt"][0] = event.TightLepton_Pt[0]
    wrapper.branchArrays["leptonEta"][0] = event.TightLepton_Eta[0]
    wrapper.branchArrays["leptonPhi"][0] = event.TightLepton_Phi[0]
    wrapper.branchArrays["leptonE"][0] = event.TightLepton_E[0]
    return event

