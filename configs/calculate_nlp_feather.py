import numpy as np
import common
import weightModules
from array import array
import os
import pandas as pd
import ROOT

def _dPhi(phi1, phi2):
    dphi = abs(phi1-phi2)
    return dphi*(dphi<np.pi)+(2.*np.pi-dphi)*(dphi>=np.pi)

def _dEta(eta1, eta2):
    return abs(eta1-eta2)

def _dR(eta1, phi1, eta2, phi2):
    dphi = _dPhi(phi1, phi2)
    deta = _dEta(eta1, eta2)

    dR = np.sqrt(dphi*dphi + deta*deta)
    return dR

# def _pT(pt1, phi1, pt2, phi2):
#     dphi = _dPhi(phi1, phi2)
#     return np.sqrt(pt1*pt1+pt2*pt2+2*pt1*pt2*np.cos(dphi))

# def _Minv(pt1, eta1, phi1, m1, e1, pt2, eta2, phi2, m2, e2):
#     dphi = _dPhi(phi1, phi2)
#     return np.sqrt(m1*m1+m2*m2+2*(e1*e2-pt1*pt2*(np.cos(dphi)+np.sinh(eta1)*np.sinh(eta2))))

# def eT(pt1, m1):
#     return np.sqrt(pt1*pt1+m1*m1)

# def _mT(pt1, phi1, pt2, phi2, m1, m2):
#     mtsq = m1*m1+m2*m2+2*(eT(pt1,m1)*eT(pt2, m2)-pt1*pt2*np.cos(_dPhi(phi1, phi2)))
#     return np.sqrt(mtsq)

def p4vec(pt1, eta1, phi1, m1, pt2, eta2, phi2, m2):
    v1 = ROOT.Math.PtEtaPhiMVector(pt1, eta1, phi1, m1)
    v2 = ROOT.Math.PtEtaPhiMVector(pt2, eta2, phi2, m2)
    return v1+v2

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        # "Jets_pt_nominal",
        # "Jets_eta_nominal",
        # "Jets_phi_nominal",
        # "Jets_mass_nominal",
        # "Jets_energy_nominal",
        # "Jets_mass_addjets_nominal",
        # "jetIdx_addjet_1_nominal",
        # "jetIdx_addjet_2_nominal",
        ]
    return variables

def base_selection(event):
    return True

def set_branches(wrapper, jec):
    '''
    initialize branches of output root file
    '''
    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("lumi") 
    
    wrapper.SetFloatVar("nlp_first")
    wrapper.SetFloatVar("nlp_first_idx")
    wrapper.SetFloatVar("nlp_first_Pt")
    wrapper.SetFloatVar("nlp_first_Eta")
    wrapper.SetFloatVar("nlp_first_Phi")
    wrapper.SetFloatVar("nlp_first_M")
    wrapper.SetFloatVar("nlp_first_E")
    wrapper.SetFloatVar("nlp_first_CvL")
    wrapper.SetFloatVar("nlp_first_CvB")
    wrapper.SetFloatVar("nlp_second")
    wrapper.SetFloatVar("nlp_second_idx")
    wrapper.SetFloatVar("nlp_second_Pt")
    wrapper.SetFloatVar("nlp_second_Eta")
    wrapper.SetFloatVar("nlp_second_Phi")
    wrapper.SetFloatVar("nlp_second_M")
    wrapper.SetFloatVar("nlp_second_E")
    wrapper.SetFloatVar("nlp_second_CvL")
    wrapper.SetFloatVar("nlp_second_CvB")
    wrapper.SetFloatVar("nlp_top_dR")
    wrapper.SetFloatVar("nlp_top_minv")
    wrapper.SetFloatVar("nlp_top_dPhi")
    wrapper.SetFloatVar("nlp_top_dEta")
    wrapper.SetFloatVar("nlp_top_pt")
    wrapper.SetFloatVar("nlp_top_mt")
    wrapper.SetFloatVar("nlp_average")
    
    wrapper.SetIntVar("nJets_nominal") 
    wrapper.SetFloatVarArray("eval_jets_nominal", "nJets_nominal")


def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None, nodes=None, graph=None, edge=None):

    nlp_first = -99
    nlp_first_idx = -99
    nlp_first_Pt = -99
    nlp_first_Eta = -99
    nlp_first_Phi = -99
    nlp_first_M = -99
    nlp_first_E = -99
    nlp_first_CvL = -99
    nlp_first_CvB = -99
    nlp_second = -99
    nlp_second_idx = -99
    nlp_second_Pt = -99
    nlp_second_Eta = -99
    nlp_second_Phi = -99
    nlp_second_M = -99
    nlp_second_E = -99
    nlp_second_CvL = -99
    nlp_second_CvB = -99
    dPhi = -99
    dEta = -99
    dR = -99
    minv = -99
    pt = -99
    mt = -99
    nlp_average = -99
    nJets = 0

    event_ = getattr(event, "event")
    run = getattr(event, "run")
    lumi = getattr(event, "luminosityBlock")

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = event_
    wrapper.branchArrays["run"][0]   = run
    wrapper.branchArrays["lumi"][0]  = lumi

    nlp_top2 = nodes[nodes["node_type"]==0].nlargest(2, "p_nominal")
    if len(nodes)-3>0:
        nJets = len(nodes)-3
    # print(nlp_top2)

    # jet_edge = edge.loc[edge["edge_node_index1"].isin(nodes.loc[nodes["node_type"]<1].index) & edge["edge_node_index2"].isin(nodes.loc[nodes["node_type"]<1].index)]


    try:
        nlp_first = nlp_top2["p_nominal"].values[0]
        nlp_first_idx = nlp_top2["node_mult"].values[0]
        nlp_first_Pt = nlp_top2["Pt"].values[0]
        nlp_first_Eta = nlp_top2["Eta"].values[0]
        nlp_first_Phi = nlp_top2["Phi"].values[0]
        nlp_first_M = nlp_top2["M"].values[0]
        nlp_first_E = nlp_top2["E"].values[0]
        nlp_first_CvL = nlp_top2["CvL"].values[0]
        nlp_first_CvB = nlp_top2["CvB"].values[0]
        nlp_second = nlp_top2["p_nominal"].values[1]
        nlp_second_idx = nlp_top2["node_mult"].values[1]
        nlp_second_Pt = nlp_top2["Pt"].values[1]
        nlp_second_Eta = nlp_top2["Eta"].values[1]
        nlp_second_Phi = nlp_top2["Phi"].values[1]
        nlp_second_M = nlp_top2["M"].values[1]
        nlp_second_E = nlp_top2["E"].values[1]
        nlp_second_CvL = nlp_top2["CvL"].values[1]
        nlp_second_CvB = nlp_top2["CvB"].values[1]
        dPhi = _dPhi(nlp_top2["Phi"].values[0], nlp_top2["Phi"].values[1])
        dEta = _dEta(nlp_top2["Eta"].values[0], nlp_top2["Eta"].values[1])
        dR = _dR(nlp_top2["Eta"].values[0], nlp_top2["Phi"].values[0], nlp_top2["Eta"].values[1], nlp_top2["Phi"].values[1])
        # pt = _pT(nlp_top2["Pt"].values[0], nlp_top2["Phi"].values[0], nlp_top2["Pt"].values[1], nlp_top2["Phi"].values[1])
        # mt = _mT(nlp_top2["Pt"].values[0], nlp_top2["Phi"].values[0], nlp_top2["Pt"].values[1], nlp_top2["Phi"].values[1], nlp_top2["M"].values[0], nlp_top2["M"].values[1])
        # minv = _Minv(nlp_top2["Pt"].values[0], nlp_top2["Eta"].values[0], nlp_top2["Phi"].values[0], nlp_top2["M"].values[0], nlp_top2["E"].values[0], nlp_top2["Pt"].values[1], nlp_top2["Eta"].values[1], nlp_top2["Phi"].values[1], nlp_top2["M"].values[1], nlp_top2["E"].values[1])
        p4 = (p4vec(nlp_top2["Pt"].values[0], nlp_top2["Eta"].values[0], nlp_top2["Phi"].values[0], nlp_top2["M"].values[0], nlp_top2["Pt"].values[1], nlp_top2["Eta"].values[1], nlp_top2["Phi"].values[1], nlp_top2["M"].values[1]))
        minv = p4.M()
        pt   = p4.Pt()
        mt   = p4.Mt()
        # # truth stuff
        # pt1   = event.Jets_pt_nominal[event.jetIdx_addjet_1_nominal]
        # eta1  = event.Jets_eta_nominal[event.jetIdx_addjet_1_nominal]
        # phi1  = event.Jets_phi_nominal[event.jetIdx_addjet_1_nominal]
        # mass1 = event.Jets_mass_nominal[event.jetIdx_addjet_1_nominal]
        # energy1 = event.Jets_energy_nominal[event.jetIdx_addjet_1_nominal]
        # pt2   = event.Jets_pt_nominal[event.jetIdx_addjet_2_nominal]
        # eta2  = event.Jets_eta_nominal[event.jetIdx_addjet_2_nominal]
        # phi2  = event.Jets_phi_nominal[event.jetIdx_addjet_2_nominal]
        # mass2 = event.Jets_mass_nominal[event.jetIdx_addjet_2_nominal]
        # energy2 = event.Jets_energy_nominal[event.jetIdx_addjet_2_nominal]
        # print((p4vec(pt1, eta1, phi1, mass1, pt2, eta2, phi2, mass2)).M())
        # minv_2 = _Minv(pt1, eta1, phi1, mass1, energy1, pt2, eta2, phi2, mass2, energy2)

        nlp_average = nodes[nodes["node_type"]==0]["p_nominal"].mean()
    except IndexError:
        pass
    # try:
    #     jet_edge = edge.loc[edge["edge_node_index1"].isin(nodes.loc[nodes["node_type"]<1].index) & edge["edge_node_index2"].isin(nodes.loc[nodes["node_type"]<1].index)]
    #     minv = float(jet_edge.loc[jet_edge["dR"]==jet_edge["dR"].min()]["minv"].values[0])
    # except IndexError:
    #     pass
    wrapper.branchArrays["nlp_first"][0] = nlp_first
    wrapper.branchArrays["nlp_first_idx"][0] = nlp_first_idx
    wrapper.branchArrays["nlp_first_Pt"][0] = nlp_first_Pt
    wrapper.branchArrays["nlp_first_Eta"][0] = nlp_first_Eta
    wrapper.branchArrays["nlp_first_Phi"][0] = nlp_first_Phi
    wrapper.branchArrays["nlp_first_M"][0] = nlp_first_M
    wrapper.branchArrays["nlp_first_E"][0] = nlp_first_E
    wrapper.branchArrays["nlp_first_CvL"][0] = nlp_first_CvL
    wrapper.branchArrays["nlp_first_CvB"][0] = nlp_first_CvB
    wrapper.branchArrays["nlp_second"][0] = nlp_second
    wrapper.branchArrays["nlp_second_idx"][0] = nlp_second_idx
    wrapper.branchArrays["nlp_second_Pt"][0] = nlp_second_Pt
    wrapper.branchArrays["nlp_second_Eta"][0] = nlp_second_Eta
    wrapper.branchArrays["nlp_second_Phi"][0] = nlp_second_Phi
    wrapper.branchArrays["nlp_second_M"][0] = nlp_second_M
    wrapper.branchArrays["nlp_second_E"][0] = nlp_second_E
    wrapper.branchArrays["nlp_second_CvL"][0] = nlp_second_CvL
    wrapper.branchArrays["nlp_second_CvB"][0] = nlp_second_CvB
    wrapper.branchArrays["nlp_top_dR"][0] = dR
    wrapper.branchArrays["nlp_top_dEta"][0] = dEta
    wrapper.branchArrays["nlp_top_dPhi"][0] = dPhi
    wrapper.branchArrays["nlp_top_minv"][0] = minv
    # wrapper.branchArrays["nlp_top_dR"][0] = dPhi
    # wrapper.branchArrays["nlp_top_minv"][0] = dEta
    # wrapper.branchArrays["nlp_top_dPhi"][0] = dR
    # wrapper.branchArrays["nlp_top_dEta"][0] = minv
    wrapper.branchArrays["nlp_top_pt"][0] = pt
    wrapper.branchArrays["nlp_top_mt"][0] = mt
    wrapper.branchArrays["nlp_average"][0] = nlp_average
    wrapper.branchArrays["nJets_nominal"][0] = nJets
    if len(nodes)-3>0:
        for idx in range(nJets):
            wrapper.branchArrays["eval_jets_nominal"][idx] = float(nodes[nodes["node_type"]==0]["p_nominal"].values[idx])
    
    return event