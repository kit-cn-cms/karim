import numpy as np
import common
from array import array

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        ]
    return variables

def base_selection(event):
    return event.N_Jets>=4

def set_branches(wrapper):
    wrapper.SetIntVar("Evt_ID")   
    wrapper.SetIntVar("Evt_Run")   
    wrapper.SetIntVar("Evt_Lumi")   
    wrapper.SetIntVar("N_Jets")   

    wrapper.SetIntVar("N_thad_b")
    wrapper.SetIntVar("N_tlep_b")
    wrapper.SetIntVar("N_thad_q")
    wrapper.SetIntVar("N_h_b")
    wrapper.SetIntVar("N_z_b")
    wrapper.SetIntVar("N_addb")
    wrapper.SetIntVar("N_addc")

    wrapper.SetIntVar("has_thad_b")
    wrapper.SetIntVar("has_tlep_b")
    wrapper.SetIntVar("has_thad_q")
    wrapper.SetIntVar("has_thad_qq")

    wrapper.SetIntVar("has_h_b")
    wrapper.SetIntVar("has_h_bb")

    wrapper.SetIntVar("has_z_b")
    wrapper.SetIntVar("has_z_bb")
    
    wrapper.SetIntVar("has_add_b")
    wrapper.SetIntVar("has_add_bb")

    wrapper.SetIntVar("has_add_c")
    wrapper.SetIntVar("has_add_cc")

    

threshold = 0.1
def calculate_variables(event, wrapper):
    '''
    calculate additional variables needed
    '''
    wrapper.branchArrays["Evt_ID"][0] = event.Evt_ID
    wrapper.branchArrays["Evt_Run"][0] = event.Evt_Run
    wrapper.branchArrays["Evt_Lumi"][0] = event.Evt_Lumi

    n_thad_b = 0
    n_tlep_b = 0
    n_thad_q = 0

    n_h_b = 0
    n_z_b = 0
    n_addb = 0
    n_addc = 0

    for jetIdx in range(event.N_Jets):

        if event.N_GenTopHad > 0:
            # b from hadronic top decay
            dR_thad_b = common.get_dR(
                event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
                event.GenTopHad_B_Eta[0], event.GenTopHad_B_Phi[0])
            if dR_thad_b < threshold:
                n_thad_b += 1

            # lf quarks from hadronic top decay
            dR_thad_q1 = common.get_dR(
                event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
                event.GenTopHad_Q1_Eta[0], event.GenTopHad_Q1_Phi[0])
            dR_thad_q2 = common.get_dR(
                event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
                event.GenTopHad_Q2_Eta[0], event.GenTopHad_Q2_Phi[0])
            if dR_thad_q1 < threshold or dR_thad_q2 < threshold:
                n_thad_q += 1
             
        if event.N_GenTopLep > 0:   
            # b from leptonic top decay
            dR_tlep_b = common.get_dR(
                event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
                event.GenTopLep_B_Eta[0], event.GenTopLep_B_Phi[0])
            if dR_tlep_b < threshold:
                n_tlep_b += 1

        # higgs
        dR_h_b1 = common.get_dR(
            event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
            event.GenHiggs_B1_Eta, event.GenHiggs_B1_Phi)
        dR_h_b2 = common.get_dR(
            event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
            event.GenHiggs_B2_Eta, event.GenHiggs_B2_Phi)
        if dR_h_b1 < threshold or dR_h_b2 < threshold:
            n_h_b += 1

        # Z boson
        dR_z_b1 = common.get_dR(
            event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
            event.GenZ_B1_Eta, event.GenZ_B1_Phi)
        dR_z_b2 = common.get_dR(
            event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
            event.GenZ_B2_Eta, event.GenZ_B2_Phi)
        if dR_z_b1 < threshold or dR_z_b2 < threshold:
            n_z_b += 1

        # additional b jets
        for bIdx in range(event.N_AdditionalGenBJets):
            dR_addb = common.get_dR(
                event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
                event.AdditionalGenBJet_Eta[bIdx], event.AdditionalGenBJet_Phi[bIdx])
            if dR_addb < threshold:
                n_addb += 1

        # additional c jets (needs new ntupling omg)
        #for cIdx in range(event.N_AdditionalGenCJets):
        #    dR_addc = common.get_dR(
        #        event.Jet_Eta[jetIdx], event.Jet_Phi[jetIdx],
        #        event.AdditionalGenCJet_Eta[bIdx], event.AdditionalGenCJet_Phi[bIdx])
        #    if dR_addc < threshold:
        #        n_addc += 1

    # fill numbers
    wrapper.branchArrays["N_thad_b"][0] = n_thad_b
    wrapper.branchArrays["N_tlep_b"][0] = n_tlep_b
    wrapper.branchArrays["N_thad_q"][0] = n_thad_q

    wrapper.branchArrays["N_h_b"][0]    = n_h_b
    wrapper.branchArrays["N_z_b"][0]    = n_z_b
    wrapper.branchArrays["N_addb"][0]   = n_addb
    wrapper.branchArrays["N_addc"][0]   = n_addc

    # fill 'has_attribute' variables
    wrapper.branchArrays["has_thad_b"][0]  = 1 if n_thad_b > 0 else 0
    wrapper.branchArrays["has_tlep_b"][0]  = 1 if n_tlep_b > 0 else 0
    wrapper.branchArrays["has_thad_q"][0]  = 1 if n_thad_q > 0 else 0
    wrapper.branchArrays["has_thad_qq"][0] = 1 if n_thad_q > 1 else 0

    wrapper.branchArrays["has_h_b"][0]     = 1 if n_h_b    > 0 else 0
    wrapper.branchArrays["has_h_bb"][0]    = 1 if n_h_b    > 1 else 0

    wrapper.branchArrays["has_z_b"][0]     = 1 if n_z_b    > 0 else 0
    wrapper.branchArrays["has_z_bb"][0]    = 1 if n_z_b    > 1 else 0

    wrapper.branchArrays["has_add_b"][0]   = 1 if n_addb   > 0 else 0
    wrapper.branchArrays["has_add_bb"][0]  = 1 if n_addb   > 1 else 0

    wrapper.branchArrays["has_add_c"][0]   = 1 if n_addc   > 0 else 0
    wrapper.branchArrays["has_add_cc"][0]  = 1 if n_addc   > 1 else 0
    return event

