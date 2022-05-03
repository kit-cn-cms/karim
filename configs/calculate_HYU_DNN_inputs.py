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

def set_branches(wrapper, jec):
    suffix = "_"+jec

    for idx in [0,1,2,3]:
        for feat in ["pt", "eta", "phi", "mass", "btag", "dRlep", "lj_invMass"]:
            wrapper.SetFloatVar("btagJets_{}_{}".format(idx, feat)+suffix)
            

    permutations = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
    for perm in permutations:
        for feat in ["dPhi", "dEta", "invMass", "dRlep"]:
            wrapper.SetFloatVar("btagdiJets_{}{}_{}".format(perm[0], perm[1], feat)+suffix)

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''


    suffix = "_"+jec
    if getattr(event, "nJets"+suffix) < 4 or event.nLep < 1: return

    try:
        btagValues = list(getattr(event, "Jets_btagDeepFlavB"+suffix))
        pts  = list(getattr(event, "Jets_pt"+suffix))
        etas = list(getattr(event, "Jets_eta"+suffix))
        phis = list(getattr(event, "Jets_phi"+suffix))
        ms   = list(getattr(event, "Jets_mass"+suffix))
        jetIdx = np.argsort(btagValues)[::-1]

        lepEta = getattr(event, "Lep_eta")[0]
        lepPhi = getattr(event, "Lep_phi")[0]
        lepPt  = getattr(event, "Lep_pt")[0]
        lepM   = getattr(event, "Lep_mass")[0]

        wrapper.branchArrays["btagJets_0_pt"+suffix][0] = pts[jetIdx[0]]
        wrapper.branchArrays["btagJets_1_pt"+suffix][0] = pts[jetIdx[1]]
        wrapper.branchArrays["btagJets_2_pt"+suffix][0] = pts[jetIdx[2]]
        wrapper.branchArrays["btagJets_3_pt"+suffix][0] = pts[jetIdx[3]]

        wrapper.branchArrays["btagJets_0_eta"+suffix][0] = etas[jetIdx[0]]
        wrapper.branchArrays["btagJets_1_eta"+suffix][0] = etas[jetIdx[1]]
        wrapper.branchArrays["btagJets_2_eta"+suffix][0] = etas[jetIdx[2]]
        wrapper.branchArrays["btagJets_3_eta"+suffix][0] = etas[jetIdx[3]]

        wrapper.branchArrays["btagJets_0_phi"+suffix][0] = phis[jetIdx[0]]
        wrapper.branchArrays["btagJets_1_phi"+suffix][0] = phis[jetIdx[1]]
        wrapper.branchArrays["btagJets_2_phi"+suffix][0] = phis[jetIdx[2]]
        wrapper.branchArrays["btagJets_3_phi"+suffix][0] = phis[jetIdx[3]]

        wrapper.branchArrays["btagJets_0_mass"+suffix][0] = ms[jetIdx[0]]
        wrapper.branchArrays["btagJets_1_mass"+suffix][0] = ms[jetIdx[1]]
        wrapper.branchArrays["btagJets_2_mass"+suffix][0] = ms[jetIdx[2]]
        wrapper.branchArrays["btagJets_3_mass"+suffix][0] = ms[jetIdx[3]]

        wrapper.branchArrays["btagJets_0_btag"+suffix][0] = btagValues[jetIdx[0]]
        wrapper.branchArrays["btagJets_1_btag"+suffix][0] = btagValues[jetIdx[1]]
        wrapper.branchArrays["btagJets_2_btag"+suffix][0] = btagValues[jetIdx[2]]
        wrapper.branchArrays["btagJets_3_btag"+suffix][0] = btagValues[jetIdx[3]]

        dRLep1 = common.get_dR(lepEta, lepPhi, etas[jetIdx[0]], phis[jetIdx[0]])
        dRLep2 = common.get_dR(lepEta, lepPhi, etas[jetIdx[1]], phis[jetIdx[1]])
        dRLep3 = common.get_dR(lepEta, lepPhi, etas[jetIdx[2]], phis[jetIdx[2]])
        dRLep4 = common.get_dR(lepEta, lepPhi, etas[jetIdx[3]], phis[jetIdx[3]])

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
                pts[jetIdx[idx]], etas[jetIdx[idx]], phis[jetIdx[idx]], ms[jetIdx[idx]])
            
            lj = lep+v[idx]
            wrapper.branchArrays["btagJets_{}_lj_invMass".format(idx)+suffix][0] = lj.M()

        # get the 6 permutations
        permutations = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
        for p in permutations:
            idx1 = p[0]
            idx2 = p[1]
            dPhi = common.get_dPhi(phis[jetIdx[idx1]], phis[jetIdx[idx2]])
            dEta = common.get_dEta(etas[jetIdx[idx1]], etas[jetIdx[idx2]])
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
            
    except: return 

    return event

