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
    
    wrapper.SetFloatVar(f"nlp_first_{jec}")
    wrapper.SetFloatVar(f"nlp_first_idx_{jec}")
    wrapper.SetFloatVar(f"nlp_first_Pt_{jec}")
    wrapper.SetFloatVar(f"nlp_first_Eta_{jec}")
    wrapper.SetFloatVar(f"nlp_first_Phi_{jec}")
    wrapper.SetFloatVar(f"nlp_first_M_{jec}")
    wrapper.SetFloatVar(f"nlp_first_E_{jec}")
    wrapper.SetFloatVar(f"nlp_first_CvL_{jec}")
    wrapper.SetFloatVar(f"nlp_first_CvB_{jec}")
    wrapper.SetFloatVar(f"nlp_second_{jec}")
    wrapper.SetFloatVar(f"nlp_second_idx_{jec}")
    wrapper.SetFloatVar(f"nlp_second_Pt_{jec}")
    wrapper.SetFloatVar(f"nlp_second_Eta_{jec}")
    wrapper.SetFloatVar(f"nlp_second_Phi_{jec}")
    wrapper.SetFloatVar(f"nlp_second_M_{jec}")
    wrapper.SetFloatVar(f"nlp_second_E_{jec}")
    wrapper.SetFloatVar(f"nlp_second_CvL_{jec}")
    wrapper.SetFloatVar(f"nlp_second_CvB_{jec}")
    wrapper.SetFloatVar(f"nlp_top_dR_{jec}")
    wrapper.SetFloatVar(f"nlp_top_minv_{jec}")
    wrapper.SetFloatVar(f"nlp_top_dPhi_{jec}")
    wrapper.SetFloatVar(f"nlp_top_dEta_{jec}")
    wrapper.SetFloatVar(f"nlp_top_pt_{jec}")
    wrapper.SetFloatVar(f"nlp_top_mt_{jec}")
    wrapper.SetFloatVar(f"nlp_average_{jec}")
    
    wrapper.SetIntVar(f"nJets_{jec}") 
    wrapper.SetFloatVarArray(f"eval_jets_{jec}", f"nJets_{jec}")


def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None, nodes=None, graph=None, edge=None):
    suffix = "_{}".format(jec)
    if jec is None:
        suffix = "_nominal"

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

    nlp_top2 = nodes[nodes["node_type"]==0].nlargest(2, f"p_{jec}")
    if len(nodes)-3>0:
        nJets = len(nodes)-3
    # print(nlp_top2)

    # jet_edge = edge.loc[edge["edge_node_index1"].isin(nodes.loc[nodes["node_type"]<1].index) & edge["edge_node_index2"].isin(nodes.loc[nodes["node_type"]<1].index)]


    try:
        nlp_first = nlp_top2[f"p_{jec}"].values[0]
        nlp_first_idx = nlp_top2["node_mult"].values[0]
        nlp_first_Pt = nlp_top2["Pt"].values[0]
        nlp_first_Eta = nlp_top2["Eta"].values[0]
        nlp_first_Phi = nlp_top2["Phi"].values[0]
        nlp_first_M = nlp_top2["M"].values[0]
        nlp_first_E = nlp_top2["E"].values[0]
        nlp_first_CvL = nlp_top2["CvL"].values[0]
        nlp_first_CvB = nlp_top2["CvB"].values[0]
        nlp_second = nlp_top2[f"p_{jec}"].values[1]
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

        nlp_average = nodes[nodes["node_type"]==0][f"p_{jec}"].mean()
    except IndexError:
        pass
    # try:
    #     jet_edge = edge.loc[edge["edge_node_index1"].isin(nodes.loc[nodes["node_type"]<1].index) & edge["edge_node_index2"].isin(nodes.loc[nodes["node_type"]<1].index)]
    #     minv = float(jet_edge.loc[jet_edge["dR"]==jet_edge["dR"].min()]["minv"].values[0])
    # except IndexError:
    #     pass
    wrapper.branchArrays[f"nlp_first_{jec}"][0] = nlp_first
    wrapper.branchArrays[f"nlp_first_idx_{jec}"][0] = nlp_first_idx
    wrapper.branchArrays[f"nlp_first_Pt_{jec}"][0] = nlp_first_Pt
    wrapper.branchArrays[f"nlp_first_Eta_{jec}"][0] = nlp_first_Eta
    wrapper.branchArrays[f"nlp_first_Phi_{jec}"][0] = nlp_first_Phi
    wrapper.branchArrays[f"nlp_first_M_{jec}"][0] = nlp_first_M
    wrapper.branchArrays[f"nlp_first_E_{jec}"][0] = nlp_first_E
    wrapper.branchArrays[f"nlp_first_CvL_{jec}"][0] = nlp_first_CvL
    wrapper.branchArrays[f"nlp_first_CvB_{jec}"][0] = nlp_first_CvB
    wrapper.branchArrays[f"nlp_second_{jec}"][0] = nlp_second
    wrapper.branchArrays[f"nlp_second_idx_{jec}"][0] = nlp_second_idx
    wrapper.branchArrays[f"nlp_second_Pt_{jec}"][0] = nlp_second_Pt
    wrapper.branchArrays[f"nlp_second_Eta_{jec}"][0] = nlp_second_Eta
    wrapper.branchArrays[f"nlp_second_Phi_{jec}"][0] = nlp_second_Phi
    wrapper.branchArrays[f"nlp_second_M_{jec}"][0] = nlp_second_M
    wrapper.branchArrays[f"nlp_second_E_{jec}"][0] = nlp_second_E
    wrapper.branchArrays[f"nlp_second_CvL_{jec}"][0] = nlp_second_CvL
    wrapper.branchArrays[f"nlp_second_CvB_{jec}"][0] = nlp_second_CvB
    wrapper.branchArrays[f"nlp_top_dR_{jec}"][0] = dR
    wrapper.branchArrays[f"nlp_top_dEta_{jec}"][0] = dEta
    wrapper.branchArrays[f"nlp_top_dPhi_{jec}"][0] = dPhi
    wrapper.branchArrays[f"nlp_top_minv_{jec}"][0] = minv
    # wrapper.branchArrays["nlp_top_dR"][0] = dPhi
    # wrapper.branchArrays["nlp_top_minv"][0] = dEta
    # wrapper.branchArrays["nlp_top_dPhi"][0] = dR
    # wrapper.branchArrays["nlp_top_dEta"][0] = minv
    wrapper.branchArrays[f"nlp_top_pt_{jec}"][0] = pt
    wrapper.branchArrays[f"nlp_top_mt_{jec}"][0] = mt
    wrapper.branchArrays[f"nlp_average_{jec}"][0] = nlp_average
    wrapper.branchArrays[f"nJets_{jec}"][0] = nJets
    if len(nodes)-3>0:
        for idx in range(nJets):
            wrapper.branchArrays[f"eval_jets_{jec}"][idx] = float(nodes[nodes["node_type"]==0][f"p_{jec}"].values[idx])
    
    return event