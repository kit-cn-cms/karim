import numpy as np
import common
import weightModules
from array import array
import os
import sys
from correctionlib import _core

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

btagSF = {}
btagEff = {}
jsonDir = os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG")


for year in ["2016preVFP", "2016postVFP", "2017", "2018"]:
    # efficiencies
    sfDir = os.path.join(karimpath, "data", "UL_"+year[2:])
    btagEffjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btagEff_monotop_had_deepJet.json"))
    btagEff[year] = btagEffjson["btagEff"]

    # scale factors
    btagSFjson = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "BTV", year+"_UL", "btagging.json.gz"))
    btagSF[year]   = btagSFjson

SFb_sys = ["up_correlated","up_uncorrelated","down_correlated","down_uncorrelated"]
SFl_sys = ["up_correlated","up_uncorrelated","down_correlated","down_uncorrelated"]

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

    if jec == "nom":
        wrapper.SetIntVar("Evt_ID")   
        wrapper.SetIntVar("Evt_Run")   
        wrapper.SetIntVar("Evt_Lumi") 

        # cross section weight
        wrapper.SetFloatVar("xsNorm")

        for sys in SFb_sys:
            wrapper.SetFloatVar("fixedWPSFb_"+sys+"_rel")
        for sys in SFl_sys:
            wrapper.SetFloatVar("fixedWPSFl_"+sys+"_rel")

    wrapper.SetFloatVar("fixedWPSF"+suffix)

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    # TODO adjust when merged JEC uncertainties are avialable
    if jec == "nom":
        btvJECname = "central"
    else:
        btvJECname = "central"

    if jec == "nom":
        # add basic information for friend trees
        wrapper.branchArrays["Evt_ID"][0] = getattr(event, "Evt_ID")
        wrapper.branchArrays["Evt_Run"][0]   = getattr(event, "Evt_Run")
        wrapper.branchArrays["Evt_Lumi"][0]  = getattr(event, "Evt_Lumi")

        # cross section norm
        wrapper.branchArrays["xsNorm"][0] = genWeights.getXS("incl")

    P_MC   = 1.
    P_DATA = 1.
    if jec == "nom":
        Pb_DATA = {}
        Pl_DATA = {}
        for sys in SFb_sys:
            Pb_DATA[sys] = 1.
        for sys in SFl_sys:
            Pl_DATA[sys] = 1.

        sfb_L = {}
        sfl_L = {}

    for idx in range(getattr(event, "N_Jets_outside_lead_AK15Jet"+suffix)):
        eta   = abs(getattr(event, "Jets_outside_lead_AK15Jet_Eta"+suffix)[idx])
        pt    = getattr(event, "Jets_outside_lead_AK15Jet_Pt"+suffix)[idx]
        flav  = getattr(event, "Jets_outside_lead_AK15Jet_HadronFlav"+suffix)[idx]
        passes_L = getattr(event, "Jets_outside_lead_AK15Jet_taggedL"+suffix)[idx]

        # TODO: fix this
        if abs(flav) > 5:
            continue
            # flav = 0
        if abs(eta) > 5:
            continue
            # eta = 0.

        eff_L = btagEff[dataEra].evaluate("L", flav, eta, pt)


        if flav == 0:
            sf_L = btagSF[dataEra]["deepJet_incl"].evaluate("central", "L", flav, eta, pt)
            if jec == "nom":
                for sys in SFl_sys:
                    sfl_L[sys] = btagSF[dataEra]["deepJet_incl"].evaluate(sys, "L", flav, eta, pt)
        else:
            sf_L = btagSF[dataEra]["deepJet_comb"].evaluate("central", "L", flav, eta, pt)
            if jec == "nom":
                for sys in SFb_sys:
                    sfb_L[sys] = btagSF[dataEra]["deepJet_comb"].evaluate(sys, "L", flav, eta, pt)

        if passes_L:
            P_MC   *= eff_L
            P_DATA *= eff_L*sf_L
            if jec == "nom":
                if flav == 0:
                    for sys in SFl_sys:
                        Pl_DATA[sys] *= eff_L*sfl_L[sys]
                    for sys in SFb_sys:
                        Pb_DATA[sys] *= eff_L*sf_L
                else:
                    for sys in SFb_sys:
                        Pb_DATA[sys] *= eff_L*sfb_L[sys]
                    for sys in SFl_sys:
                        Pl_DATA[sys] *= eff_L*sf_L
        else:
            P_MC   *= (1. - eff_L)
            P_DATA *= (1. - eff_L*sf_L)  
            if jec == "nom":
                if flav == 0:
                    for sys in SFl_sys:
                        Pl_DATA[sys] *= (1. - eff_L*sfl_L[sys])
                    for sys in SFb_sys:
                        Pb_DATA[sys] *= (1. - eff_L*sf_L)
                else:
                    for sys in SFb_sys:
                        Pb_DATA[sys] *= (1. - eff_L*sfb_L[sys])
                    for sys in SFl_sys:
                        Pl_DATA[sys] *= (1. - eff_L*sf_L)

    wrapper.branchArrays["fixedWPSF"+suffix][0] = P_DATA/P_MC
    if jec == "nom":
        for sys in SFl_sys:
            wrapper.branchArrays["fixedWPSFl_"+sys+"_rel"][0] = Pl_DATA[sys]/P_DATA
        for sys in SFb_sys:
            wrapper.branchArrays["fixedWPSFb_"+sys+"_rel"][0] = Pb_DATA[sys]/P_DATA

    return event

