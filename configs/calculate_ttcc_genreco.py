import numpy as np
import common
import weightModules
from array import array
import os
from correctionlib import _core

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))


setups = {
    "cM_nobM": "(event.Jet_bM{suffix}[{idx}] == 0) and (event.Jet_cM{suffix}[{idx}] == 1)",
    "cM_nobT": "(event.Jet_bT{suffix}[{idx}] == 0) and (event.Jet_cM{suffix}[{idx}] == 1)",
    "cT_nobM": "(event.Jet_bM{suffix}[{idx}] == 0) and (event.Jet_cT{suffix}[{idx}] == 1)",
    "cT_nobT": "(event.Jet_bT{suffix}[{idx}] == 0) and (event.Jet_cT{suffix}[{idx}] == 1)",
    "cM":      "(event.Jet_cM{suffix}[{idx}] == 1)",
    "cT":      "(event.Jet_cT{suffix}[{idx}] == 1)",
    "cMax":    "(event.Jet_ctagValue{suffix}[{idx}] > event.Jet_btagValue{suffix}[{idx}]) and (event.Jet_ctagValue{suffix}[{idx}] > event.Jet_ltagValue{suffix}[{idx}])",
    }

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

def set_branches(wrapper, jec):
    suffix = "_"+jec

    wrapper.SetFloatVar("nbMax"+suffix)
    wrapper.SetFloatVar("ncMax"+suffix)
    wrapper.SetFloatVar("nlMax"+suffix)

    for s in setups:
        wrapper.SetFloatVar("reco_cjets_"+s+"_dRcc"+suffix)
        wrapper.SetIntVar("reco_ncjets_"+s+suffix)

    wrapper.SetFloatVar("gen_cjets_dRcc"+suffix)
    wrapper.SetFloatVar("gen_ncjets"+suffix)

def get_reco_c_jets(event, suffix, requirement = None):
    jet_indices = []
    for i in range(getattr(event, "nJets"+suffix)):
        if not requirement is None:
            parse = requirement.format(suffix = suffix, idx = i)
        else:
            parse = "True"
        #print(parse)
        if eval(parse):
            jet_indices.append(i)
    return jet_indices
        
def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec

    nbMax, ncMax, nlMax = 0, 0, 0
    for idx in range(getattr(event, "nJets"+suffix)):
        if getattr(event, "Jet_btagValue"+suffix)[idx] > getattr(event, "Jet_ctagValue"+suffix)[idx]:
            if getattr(event, "Jet_btagValue"+suffix)[idx] > getattr(event, "Jet_ltagValue"+suffix)[idx]:
                nbMax+=1
                continue
        if getattr(event, "Jet_ctagValue"+suffix)[idx] > getattr(event, "Jet_btagValue"+suffix)[idx]:
            if getattr(event, "Jet_ctagValue"+suffix)[idx] > getattr(event, "Jet_ltagValue"+suffix)[idx]:
                ncMax+=1
                continue
        if getattr(event, "Jet_ltagValue"+suffix)[idx] > getattr(event, "Jet_ctagValue"+suffix)[idx]:
            if getattr(event, "Jet_ltagValue"+suffix)[idx] > getattr(event, "Jet_btagValue"+suffix)[idx]:
                nlMax+=1
                continue

    if nbMax+ncMax+nlMax != getattr(event, "nJets"+suffix):
        print("ERRORRRRR")

    wrapper.branchArrays["nbMax"+suffix][0] = nbMax
    wrapper.branchArrays["ncMax"+suffix][0] = ncMax
    wrapper.branchArrays["nlMax"+suffix][0] = nlMax

    for s in setups:
        jet_indices = get_reco_c_jets(event, suffix, setups[s])
        #print(s, jet_indices)
        wrapper.branchArrays["reco_ncjets_"+s+suffix][0] = len(jet_indices)
        if len(jet_indices) < 2:
            wrapper.branchArrays["reco_cjets_"+s+"_dRcc"+suffix][0] = -1.
            continue

        dR = common.get_dR(
            getattr(event, "Jet_Eta"+suffix)[jet_indices[0]],   
            getattr(event, "Jet_Phi"+suffix)[jet_indices[0]],
            getattr(event, "Jet_Eta"+suffix)[jet_indices[1]],   
            getattr(event, "Jet_Phi"+suffix)[jet_indices[1]]
            )
        wrapper.branchArrays["reco_cjets_"+s+"_dRcc"+suffix][0] = dR
        

    gen_indices = []
    for i in range(event.nGenJets):
        if abs(event.genJet_partonFlav[i]) == 4:
            gen_indices.append(i)

    wrapper.branchArrays["gen_ncjets"+suffix][0] = len(gen_indices)
    if len(gen_indices) < 2:
        wrapper.branchArrays["gen_cjets_dRcc"+suffix][0] = -1
    else:
        dR = common.get_dR(
            event.genJet_Eta[gen_indices[0]],
            event.genJet_Phi[gen_indices[0]],
            event.genJet_Eta[gen_indices[1]],
            event.genJet_Phi[gen_indices[1]]
            )
        wrapper.branchArrays["gen_cjets_dRcc"+suffix][0] = dR
        


            
    return event

