import numpy as np
import common
from array import array

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
        ]
    return variables

def base_selection(event):
    return event.N_Jets>=4

def set_branches(wrapper):
    wrapper.SetIntVar("Evt_ID")   
    wrapper.SetIntVar("Evt_Run")   
    wrapper.SetIntVar("Evt_Lumi")   
    wrapper.SetIntVar("GenEvt_I_TTPlusBB")   
    wrapper.SetIntVar("GenEvt_I_TTPlusCC")   
    wrapper.SetIntVar("N_Jets")   

    wrapper.SetIntVar("N_bJets")
    wrapper.SetIntVar("N_cJets")
    wrapper.SetIntVar("N_lfJets")

    wrapper.SetFloatVarArray("Jet_DeepJet_CvsL","N_Jets")
    wrapper.SetFloatVarArray("Jet_DeepJet_CvsB","N_Jets")
    wrapper.SetFloatVarArray("Jet_DeepCSV_CvsL","N_Jets")
    wrapper.SetFloatVarArray("Jet_DeepCSV_CvsB","N_Jets")

    wrapper.SetFloatVarArray("bJet_DeepJet_CvsL","N_bJets")
    wrapper.SetFloatVarArray("bJet_DeepJet_CvsB","N_bJets")
    wrapper.SetFloatVarArray("bJet_DeepCSV_CvsL","N_bJets")
    wrapper.SetFloatVarArray("bJet_DeepCSV_CvsB","N_bJets")
    wrapper.SetFloatVarArray("bJet_btagValue","N_bJets")

    wrapper.SetFloatVarArray("cJet_DeepJet_CvsL","N_cJets")
    wrapper.SetFloatVarArray("cJet_DeepJet_CvsB","N_cJets")
    wrapper.SetFloatVarArray("cJet_DeepCSV_CvsL","N_cJets")
    wrapper.SetFloatVarArray("cJet_DeepCSV_CvsB","N_cJets")
    wrapper.SetFloatVarArray("cJet_btagValue","N_cJets")

    wrapper.SetFloatVarArray("lfJet_DeepJet_CvsL","N_lfJets")
    wrapper.SetFloatVarArray("lfJet_DeepJet_CvsB","N_lfJets")
    wrapper.SetFloatVarArray("lfJet_DeepCSV_CvsL","N_lfJets")
    wrapper.SetFloatVarArray("lfJet_DeepCSV_CvsB","N_lfJets")
    wrapper.SetFloatVarArray("lfJet_btagValue","N_cJets")

def calculate_variables(event, wrapper):
    '''
    calculate additional variables needed
    '''
    wrapper.branchArrays["Evt_ID"][0] = event.Evt_ID
    wrapper.branchArrays["Evt_Run"][0] = event.Evt_Run
    wrapper.branchArrays["Evt_Lumi"][0] = event.Evt_Lumi
    try:
        wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = event.GenEvt_I_TTPlusBB 
        wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = event.GenEvt_I_TTPlusCC
    except:
        wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = -1
        wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = -1
    wrapper.branchArrays["N_Jets"][0] = event.N_Jets
    
    N_bJets = 0
    N_cJets = 0
    N_lfJets = 0
    for jetIdx in range(event.N_Jets):
        CvsL_deepJet = event.Jet_DeepJet_c[jetIdx]/ \
            (event.Jet_DeepJet_c[jetIdx] + event.Jet_DeepJet_uds[jetIdx] + event.Jet_DeepJet_g[jetIdx])
        CvsB_deepJet = event.Jet_DeepJet_c[jetIdx]/ \
            (event.Jet_DeepJet_c[jetIdx] + event.Jet_DeepJet_b[jetIdx] + event.Jet_DeepJet_bb[jetIdx] + event.Jet_DeepJet_lepb[jetIdx])
        CvsL_deepCSV = event.Jet_DeepCSV_c[jetIdx]/ \
            (event.Jet_DeepCSV_c[jetIdx] + event.Jet_DeepCSV_udsg[jetIdx])
        CvsB_deepCSV = event.Jet_DeepCSV_c[jetIdx]/ \
            (event.Jet_DeepCSV_c[jetIdx] + event.Jet_DeepCSV_b[jetIdx] + event.Jet_DeepCSV_bb[jetIdx])

        wrapper.branchArrays["Jet_DeepJet_CvsL"][jetIdx] = CvsL_deepJet
        wrapper.branchArrays["Jet_DeepJet_CvsB"][jetIdx] = CvsB_deepJet

        wrapper.branchArrays["Jet_DeepCSV_CvsL"][jetIdx] = CvsL_deepCSV
        wrapper.branchArrays["Jet_DeepCSV_CvsB"][jetIdx] = CvsB_deepCSV

        if event.Jet_Flav[jetIdx] == 5:
            wrapper.branchArrays["bJet_DeepJet_CvsL"][N_bJets] = CvsL_deepJet
            wrapper.branchArrays["bJet_DeepJet_CvsB"][N_bJets] = CvsB_deepJet
            wrapper.branchArrays["bJet_DeepCSV_CvsL"][N_bJets] = CvsL_deepCSV
            wrapper.branchArrays["bJet_DeepCSV_CvsB"][N_bJets] = CvsB_deepCSV
            wrapper.branchArrays["bJet_btagValue"][N_bJets] = event.Jet_btagValue[jetIdx]
            N_bJets += 1
        elif event.Jet_Flav[jetIdx] == 4:
            wrapper.branchArrays["cJet_DeepJet_CvsL"][N_cJets] = CvsL_deepJet
            wrapper.branchArrays["cJet_DeepJet_CvsB"][N_cJets] = CvsB_deepJet
            wrapper.branchArrays["cJet_DeepCSV_CvsL"][N_cJets] = CvsL_deepCSV
            wrapper.branchArrays["cJet_DeepCSV_CvsB"][N_cJets] = CvsB_deepCSV
            wrapper.branchArrays["cJet_btagValue"][N_cJets] = event.Jet_btagValue[jetIdx]
            N_cJets += 1
        else:
            wrapper.branchArrays["lfJet_DeepJet_CvsL"][N_lfJets] = CvsL_deepJet
            wrapper.branchArrays["lfJet_DeepJet_CvsB"][N_lfJets] = CvsB_deepJet
            wrapper.branchArrays["lfJet_DeepCSV_CvsL"][N_lfJets] = CvsL_deepCSV
            wrapper.branchArrays["lfJet_DeepCSV_CvsB"][N_lfJets] = CvsB_deepCSV
            wrapper.branchArrays["lfJet_btagValue"][N_lfJets] = event.Jet_btagValue[jetIdx]
            N_lfJets += 1
        
        wrapper.branchArrays["N_bJets"][0] = N_bJets
        wrapper.branchArrays["N_cJets"][0] = N_cJets
        wrapper.branchArrays["N_lfJets"][0] = N_lfJets


    return event

