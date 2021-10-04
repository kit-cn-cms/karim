import numpy as np
import common
import weightModules
from array import array
import os
import sys
from correctionlib import _core

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

year = "18"
yearL = "2018"
sfDir = os.path.join(karimpath, "data", "UL_"+year)
sfDirLeg = os.path.join(karimpath, "data", "legacy_"+yearL)


btagSF = {}
mistagSF = {}
btagEff = {}
for year in ["2017", "2018"]:
    sfDir = os.path.join(karimpath, "data", "UL_"+year[2:])
    
    btagSFjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btaggingSF_deepJet.json"))
    btagSF[year] = btagSFjson["comb"]
    mistagSF[year] = btagSFjson["incl"]

    btagEffjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btagEff_ttbb_deepJet.json"))
    btagEff[year] = btagEffjson["btagEff"]

SFb_sys = ["up","down"]
SFl_sys = ["up","down"]

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
        wrapper.SetIntVar("event")
        wrapper.SetIntVar("run")
        wrapper.SetIntVar("lumi")

        # cross section weight
        wrapper.SetFloatVar("xsNorm")

        for sys in SFb_sys:
            wrapper.SetFloatVar("fixedWPSFb_TM_"+sys+"_rel")
        for sys in SFl_sys:
            wrapper.SetFloatVar("fixedWPSFl_TM_"+sys+"_rel")

    wrapper.SetFloatVar("fixedWPSF_TM"+suffix)

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
        wrapper.branchArrays["event"][0] = getattr(event, "event")
        wrapper.branchArrays["run"][0]   = getattr(event, "run")
        wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")

        # cross section norm
        wrapper.branchArrays["xsNorm"][0] = genWeights.getXS("incl")

    P_MC_TM   = 1.
    P_DATA_TM = 1.
    if jec == "nom":
        Pb_DATA_TM = {}
        Pl_DATA_TM = {}
        for sys in SFb_sys:
            Pb_DATA_TM[sys] = 1.
        for sys in SFl_sys:
            Pl_DATA_TM[sys] = 1.

        sfb_M = {}
        sfb_T = {}
        sfl_M = {}
        sfl_T = {}

    for idx in range(getattr(event, "nJets"+suffix)):
        eta   = abs(getattr(event, "Jet_Eta"+suffix)[idx])
        pt    = getattr(event, "Jet_Pt"+suffix)[idx]
        flav  = getattr(event, "Jet_Flav"+suffix)[idx]
        passes_M = getattr(event, "Jet_taggedM"+suffix)[idx]
        passes_T = getattr(event, "Jet_taggedM"+suffix)[idx]

        eff_M = btagEff[dataEra].evaluate("M", flav, eta, pt)
        eff_T = btagEff[dataEra].evaluate("T", flav, eta, pt)

        if flav == 0:
            sf_M = mistagSF[dataEra].evaluate("M", "central", flav, eta, pt)
            sf_T = mistagSF[dataEra].evaluate("T", "central", flav, eta, pt)
            if jec == "nom":
                for sys in SFl_sys:
                    sfl_M[sys] = mistagSF[dataEra].evaluate("M", sys, flav, eta, pt)
                    sfl_T[sys] = mistagSF[dataEra].evaluate("T", sys, flav, eta, pt)
        else:
            sf_M = btagSF[dataEra].evaluate("M", "central", flav, eta, pt)
            sf_T = btagSF[dataEra].evaluate("T", "central", flav, eta, pt)
            if jec == "nom":
                for sys in SFb_sys:
                    sfb_M[sys] = btagSF[dataEra].evaluate("M", sys, flav, eta, pt)
                    sfb_T[sys] = btagSF[dataEra].evaluate("T", sys, flav, eta, pt)

        if passes_T:
            P_MC_TM   *= eff_T
            P_DATA_TM *= eff_T*sf_T
            if jec == "nom":
                if flav == 0:
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= eff_T*sfl_T[sys]
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= eff_T*sf_T
                else:
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= eff_T*sfb_T[sys]
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= eff_T*sf_T
        elif passes_M: 
            P_MC_TM   *= (eff_M      - eff_T)
            P_DATA_TM *= (eff_M*sf_M - eff_T*sf_T)
            if jec == "nom":
                if flav == 0:
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= (eff_M*sfl_M[sys] - eff_T*sfl_T[sys])
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= (eff_M*sf_M - eff_T*sf_T)
                else:
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= (eff_M*sfb_M[sys] - eff_T*sfb_T[sys])
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= (eff_M*sf_M - eff_T*sf_T)
        else:
            P_MC_TM   *= (1. - eff_M)
            P_DATA_TM *= (1. - eff_M*sf_M)  
            if jec == "nom":
                if flav == 0:
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= (1. - eff_M*sfl_M[sys])
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= (1. - eff_M*sf_M)
                else:
                    for sys in SFb_sys:
                        Pb_DATA_TM[sys] *= (1. - eff_M*sfb_M[sys])
                    for sys in SFl_sys:
                        Pl_DATA_TM[sys] *= (1. - eff_M*sf_M)

    wrapper.branchArrays["fixedWPSF_TM"+suffix][0] = P_DATA_TM/P_MC_TM
    if jec == "nom":
        for sys in SFl_sys:
            wrapper.branchArrays["fixedWPSFb_TM_"+sys+"_rel"][0] = Pl_DATA_TM[sys]/P_DATA_TM
        for sys in SFb_sys:
            wrapper.branchArrays["fixedWPSFl_TM_"+sys+"_rel"][0] = Pb_DATA_TM[sys]/P_DATA_TM

    return event

