import numpy as np
import common
import weightModules
from array import array
import os
import sys
import ROOT
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

permutations = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
def set_branches(wrapper, jec):
    suffix = "_"+jec

    for idx in [0,1,2,3]:
        for feat in ["pt", "eta", "phi", "mass", "isM", "isT", "dRlep", "lj_invMass"]:
            wrapper.SetFloatVar("btagJets_{}_{}".format(idx, feat)+suffix)
            

    for perm in permutations:
        for feat in ["dPhi", "dEta", "invMass", "dRlep"]:
            wrapper.SetFloatVar("btagdiJets_{}{}_{}".format(perm[0], perm[1], feat)+suffix)

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    nj = getattr(event, "nJets"+suffix)
    nt = getattr(event, "nTagsM"+suffix)
    if nj < 6 or nt < 4 or event.nLep < 1: return

    isM = np.array(getattr(event, "Jets_taggedM"+suffix))
    jetIdx = np.where(isM)[0]
    if len(jetIdx) < 4:
        return
    jetIdx = np.array(jetIdx[:4])

    isM  = isM[jetIdx]
    isT  = np.array(getattr(event, "Jets_taggedT"+suffix))[jetIdx]
    pts  = np.array(getattr(event, "Jets_pt"+suffix))[jetIdx]
    etas = np.array(getattr(event, "Jets_eta"+suffix))[jetIdx]
    phis = np.array(getattr(event, "Jets_phi"+suffix))[jetIdx]
    ms   = np.array(getattr(event, "Jets_mass"+suffix))[jetIdx]

    lepEta = getattr(event, "Lep_eta")[0]
    lepPhi = getattr(event, "Lep_phi")[0]
    lepPt  = getattr(event, "Lep_pt")[0]
    lepM   = getattr(event, "Lep_mass")[0]

    wrapper.branchArrays["btagJets_0_pt"+suffix][0] = pts[0]
    wrapper.branchArrays["btagJets_1_pt"+suffix][0] = pts[1]
    wrapper.branchArrays["btagJets_2_pt"+suffix][0] = pts[2]
    wrapper.branchArrays["btagJets_3_pt"+suffix][0] = pts[3]

    wrapper.branchArrays["btagJets_0_eta"+suffix][0] = etas[0]
    wrapper.branchArrays["btagJets_1_eta"+suffix][0] = etas[1]
    wrapper.branchArrays["btagJets_2_eta"+suffix][0] = etas[2]
    wrapper.branchArrays["btagJets_3_eta"+suffix][0] = etas[3]

    wrapper.branchArrays["btagJets_0_phi"+suffix][0] = phis[0]
    wrapper.branchArrays["btagJets_1_phi"+suffix][0] = phis[1]
    wrapper.branchArrays["btagJets_2_phi"+suffix][0] = phis[2]
    wrapper.branchArrays["btagJets_3_phi"+suffix][0] = phis[3]

    wrapper.branchArrays["btagJets_0_mass"+suffix][0] = ms[0]
    wrapper.branchArrays["btagJets_1_mass"+suffix][0] = ms[1]
    wrapper.branchArrays["btagJets_2_mass"+suffix][0] = ms[2]
    wrapper.branchArrays["btagJets_3_mass"+suffix][0] = ms[3]

    wrapper.branchArrays["btagJets_0_isM"+suffix][0] = isM[0]
    wrapper.branchArrays["btagJets_1_isM"+suffix][0] = isM[1]
    wrapper.branchArrays["btagJets_2_isM"+suffix][0] = isM[2]
    wrapper.branchArrays["btagJets_3_isM"+suffix][0] = isM[3]

    wrapper.branchArrays["btagJets_0_isT"+suffix][0] = isT[0]
    wrapper.branchArrays["btagJets_1_isT"+suffix][0] = isT[1]
    wrapper.branchArrays["btagJets_2_isT"+suffix][0] = isT[2]
    wrapper.branchArrays["btagJets_3_isT"+suffix][0] = isT[3]

    dRLep1 = common.get_dR(lepEta, lepPhi, etas[0], phis[0])
    dRLep2 = common.get_dR(lepEta, lepPhi, etas[1], phis[1])
    dRLep3 = common.get_dR(lepEta, lepPhi, etas[2], phis[2])
    dRLep4 = common.get_dR(lepEta, lepPhi, etas[3], phis[3])

    wrapper.branchArrays["btagJets_0_dRlep"+suffix][0] = dRLep1
    wrapper.branchArrays["btagJets_1_dRlep"+suffix][0] = dRLep2
    wrapper.branchArrays["btagJets_2_dRlep"+suffix][0] = dRLep3
    wrapper.branchArrays["btagJets_3_dRlep"+suffix][0] = dRLep4

    lep = ROOT.TLorentzVector()
    lep.SetPtEtaPhiM(lepPt, lepEta, lepPhi, lepM)
    
    v = {}
    for idx in [0, 1, 2, 3]:
        v[idx] = ROOT.TLorentzVector()
        v[idx].SetPtEtaPhiM(
            pts[idx], etas[idx], phis[idx], ms[idx])
        
        lj = lep+v[idx]
        wrapper.branchArrays["btagJets_{}_lj_invMass".format(idx)+suffix][0] = lj.M()

    # get the 6 permutations
    for p in permutations:
        idx1 = p[0]
        idx2 = p[1]
        dPhi = common.get_dPhi(phis[idx1], phis[idx2])
        dEta = common.get_dEta(etas[idx1], etas[idx2])
        wrapper.branchArrays["btagdiJets_{}{}_dPhi".format(p[0],p[1])+suffix][0] = dPhi
        wrapper.branchArrays["btagdiJets_{}{}_dEta".format(p[0],p[1])+suffix][0] = dEta

        dijet = v[idx1]+v[idx2]
        dijetM = dijet.M()
        wrapper.branchArrays["btagdiJets_{}{}_invMass".format(p[0],p[1])+suffix][0] = dijetM

        dRLep = common.get_dR(
            lepEta, lepPhi,
            dijet.Eta(), dijet.Phi()
            )
        wrapper.branchArrays["btagdiJets_{}{}_dRlep".format(p[0],p[1])+suffix][0] = dRLep
        
    return event

