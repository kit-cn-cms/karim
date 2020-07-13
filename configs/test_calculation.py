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

    wrapper.SetFloatVarArray("Jet_DeepJet_CvsL","N_Jets")
    wrapper.SetFloatVarArray("Jet_DeepJet_CvsB","N_Jets")
    wrapper.SetFloatVarArray("Jet_DeepCSV_CvsL","N_Jets")
    wrapper.SetFloatVarArray("Jet_DeepCSV_CvsB","N_Jets")

def calculate_variables(event, wrapper):
    '''
    calculate additional variables needed
    '''
    wrapper.branchArrays["Evt_ID"][0] = event.Evt_ID
    wrapper.branchArrays["Evt_Run"][0] = event.Evt_Run
    wrapper.branchArrays["Evt_Lumi"][0] = event.Evt_Lumi
    wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = event.GenEvt_I_TTPlusBB
    wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = event.GenEvt_I_TTPlusCC
    wrapper.branchArrays["N_Jets"][0] = event.N_Jets

    for jetIdx in range(event.N_Jets):
        wrapper.branchArrays["Jet_DeepJet_CvsL"][jetIdx] = \
            event.Jet_DeepJet_c[jetIdx]/(event.Jet_DeepJet_c[jetIdx] + event.Jet_DeepJet_uds[jetIdx] + event.Jet_DeepJet_g[jetIdx])
        wrapper.branchArrays["Jet_DeepJet_CvsB"][jetIdx] = \
            event.Jet_DeepJet_c[jetIdx]/(event.Jet_DeepJet_c[jetIdx] + event.Jet_DeepJet_b[jetIdx] + event.Jet_DeepJet_bb[jetIdx] + event.Jet_DeepJet_lepb[jetIdx])

        wrapper.branchArrays["Jet_DeepCSV_CvsL"][jetIdx] = \
            event.Jet_DeepCSV_c[jetIdx]/(event.Jet_DeepCSV_c[jetIdx] + event.Jet_DeepCSV_udsg[jetIdx])
        wrapper.branchArrays["Jet_DeepCSV_CvsB"][jetIdx] = \
            event.Jet_DeepCSV_c[jetIdx]/(event.Jet_DeepCSV_c[jetIdx] + event.Jet_DeepCSV_b[jetIdx] + event.Jet_DeepCSV_bb[jetIdx])

    return event

