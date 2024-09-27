import numpy as np
import common
import weightModules
from array import array
import os
import ROOT

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

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
        ]
    return variables

def base_selection(event):
    return True

def set_branches(wrapper, jec = None):
    suffix = "_{}".format(jec)
    if jec is None:
        suffix = "_nominal"
    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("lumi")

    wrapper.SetIntVar(f"nJets{suffix}")
    wrapper.SetIntVar(f"ttbarID")

    wrapper.SetFloatVarArray(f"Jets_pt{suffix}", 2)
    wrapper.SetFloatVarArray(f"Jets_eta{suffix}", 2)
    wrapper.SetFloatVarArray(f"Jets_phi{suffix}", 2)
    wrapper.SetFloatVarArray(f"Jets_mass{suffix}", 2)
    wrapper.SetFloatVarArray(f"Jets_energy{suffix}", 2)
    wrapper.SetFloatVarArray(f"Jets_btagDeepFlavB{suffix}", 2)
    wrapper.SetFloatVarArray(f"Jets_btagDeepFlavCvB{suffix}", 2)
    wrapper.SetFloatVarArray(f"Jets_btagDeepFlavCvL{suffix}", 2)

    wrapper.SetFloatVar(f"Jet_pair_dr{suffix}")
    wrapper.SetFloatVar(f"Jet_pair_pt{suffix}")
    wrapper.SetFloatVar(f"Jet_pair_eta{suffix}")
    wrapper.SetFloatVar(f"Jet_pair_phi{suffix}")
    wrapper.SetFloatVar(f"Jet_pair_mass{suffix}")
    wrapper.SetFloatVar(f"Jet_pair_mt{suffix}")


def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    suffix = "_{}".format(jec)
    if jec is None:
        suffix = "_nominal"

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "luminosityBlock")
    wrapper.branchArrays[f"nJets{suffix}"][0] = getattr(event, f"nJets{suffix}")
    try:
        wrapper.branchArrays[f"ttbarID"][0] = getattr(event, f"ttbarID")
    except:
        wrapper.branchArrays[f"ttbarID"][0] = -1
    
    do_addjets = True 
    if do_addjets:
        jet1_idx = getattr(event, f"jetIdx_addjet_1{suffix}")
        jet2_idx = getattr(event, f"jetIdx_addjet_2{suffix}")
    else:
        jet1_idx = getattr(event, f"jetIdx_top_b{suffix}")
        jet2_idx = getattr(event, f"jetIdx_topbar_b{suffix}")

    njets = 0
    if jet1_idx>-1:
        njets+=1
    if jet2_idx>-1:
        njets+=1

    if jet1_idx>-1:
        wrapper.branchArrays[f"Jets_pt{suffix}"][0] = getattr(event, f"Jets_pt{suffix}")[jet1_idx]
        wrapper.branchArrays[f"Jets_eta{suffix}"][0] = getattr(event, f"Jets_eta{suffix}")[jet1_idx]
        wrapper.branchArrays[f"Jets_phi{suffix}"][0] = getattr(event, f"Jets_phi{suffix}")[jet1_idx]
        wrapper.branchArrays[f"Jets_mass{suffix}"][0] = getattr(event, f"Jets_mass{suffix}")[jet1_idx]
        wrapper.branchArrays[f"Jets_energy{suffix}"][0] = getattr(event, f"Jets_energy{suffix}")[jet1_idx]
        wrapper.branchArrays[f"Jets_btagDeepFlavB{suffix}"][0] = getattr(event, f"Jets_btagDeepFlavB{suffix}")[jet1_idx]
        wrapper.branchArrays[f"Jets_btagDeepFlavCvB{suffix}"][0] = getattr(event, f"Jets_btagDeepFlavCvB{suffix}")[jet1_idx]
        wrapper.branchArrays[f"Jets_btagDeepFlavCvL{suffix}"][0] = getattr(event, f"Jets_btagDeepFlavCvL{suffix}")[jet1_idx]
    
    if jet2_idx>-1:
        wrapper.branchArrays[f"Jets_pt{suffix}"][1] = getattr(event, f"Jets_pt{suffix}")[jet2_idx]
        wrapper.branchArrays[f"Jets_eta{suffix}"][1] = getattr(event, f"Jets_eta{suffix}")[jet2_idx]
        wrapper.branchArrays[f"Jets_phi{suffix}"][1] = getattr(event, f"Jets_phi{suffix}")[jet2_idx]
        wrapper.branchArrays[f"Jets_mass{suffix}"][1] = getattr(event, f"Jets_mass{suffix}")[jet2_idx]
        wrapper.branchArrays[f"Jets_energy{suffix}"][1] = getattr(event, f"Jets_energy{suffix}")[jet2_idx]
        wrapper.branchArrays[f"Jets_btagDeepFlavB{suffix}"][1] = getattr(event, f"Jets_btagDeepFlavB{suffix}")[jet2_idx]
        wrapper.branchArrays[f"Jets_btagDeepFlavCvB{suffix}"][1] = getattr(event, f"Jets_btagDeepFlavCvB{suffix}")[jet2_idx]
        wrapper.branchArrays[f"Jets_btagDeepFlavCvL{suffix}"][1] = getattr(event, f"Jets_btagDeepFlavCvL{suffix}")[jet2_idx]



    if do_addjets:
        wrapper.branchArrays[f"Jet_pair_dr{suffix}"][0] = getattr(event, f"Jets_dR_addjets{suffix}")
        wrapper.branchArrays[f"Jet_pair_pt{suffix}"][0] = getattr(event, f"Jets_pt_addjets{suffix}")
        # wrapper.branchArrays[f"Jet_pair_eta{suffix}"][0] = getattr(event, f"Jets_eta_addjets{suffix}") # bug in v27, resolved in future versions
        # wrapper.branchArrays[f"Jet_pair_phi{suffix}"][0] = getattr(event, f"Jets_phi_addjets{suffix}") # bug in v27, resolved in future versions
        wrapper.branchArrays[f"Jet_pair_mass{suffix}"][0] = getattr(event, f"Jets_mass_addjets{suffix}")
        wrapper.branchArrays[f"Jet_pair_mt{suffix}"][0] = getattr(event, f"Jets_mt_addjets{suffix}")

    else:
        wrapper.branchArrays[f"Jet_pair_dr{suffix}"][0] = getattr(event, f"Jets_dR_topbjets{suffix}")
        wrapper.branchArrays[f"Jet_pair_pt{suffix}"][0] = getattr(event, f"Jets_pt_topbjets{suffix}")
        # wrapper.branchArrays[f"Jet_pair_eta{suffix}"][0] = getattr(event, f"Jets_eta_topbjets{suffix}") # bug in v27, resolved in future versions
        # wrapper.branchArrays[f"Jet_pair_phi{suffix}"][0] = getattr(event, f"Jets_phi_topbjets{suffix}") # bug in v27, resolved in future versions
        wrapper.branchArrays[f"Jet_pair_mass{suffix}"][0] = getattr(event, f"Jets_mass_topbjets{suffix}")
        wrapper.branchArrays[f"Jet_pair_mt{suffix}"][0] = getattr(event, f"Jets_mt_topbjets{suffix}")

    # intermediate solution for the bug in v27
    if njets==2:
        wrapper.branchArrays[f"Jet_pair_eta{suffix}"][0] = p4vec(
            wrapper.branchArrays[f"Jets_pt{suffix}"][jet1_idx], wrapper.branchArrays[f"Jets_eta{suffix}"][jet1_idx], wrapper.branchArrays[f"Jets_phi{suffix}"][jet1_idx], wrapper.branchArrays[f"Jets_mass{suffix}"][jet1_idx],
            wrapper.branchArrays[f"Jets_pt{suffix}"][jet2_idx], wrapper.branchArrays[f"Jets_eta{suffix}"][jet2_idx], wrapper.branchArrays[f"Jets_phi{suffix}"][jet2_idx], wrapper.branchArrays[f"Jets_mass{suffix}"][jet2_idx]
        ).Eta()
        wrapper.branchArrays[f"Jet_pair_phi{suffix}"][0] = p4vec(
            wrapper.branchArrays[f"Jets_pt{suffix}"][jet1_idx], wrapper.branchArrays[f"Jets_eta{suffix}"][jet1_idx], wrapper.branchArrays[f"Jets_phi{suffix}"][jet1_idx], wrapper.branchArrays[f"Jets_mass{suffix}"][jet1_idx],
            wrapper.branchArrays[f"Jets_pt{suffix}"][jet2_idx], wrapper.branchArrays[f"Jets_eta{suffix}"][jet2_idx], wrapper.branchArrays[f"Jets_phi{suffix}"][jet2_idx], wrapper.branchArrays[f"Jets_mass{suffix}"][jet2_idx]
        ).Phi()

    return event
