import numpy as np
import common
import weightModules
from array import array
import os
import sys
import ROOT
from correctionlib import _core

ROOT.TH1.AddDirectory(False)

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
kFactors_QCD = {}
kFactors_EW = {}
for mode in ["evj","eej", "vvj", "aj"]:
    filePath = os.path.join(karimpath, "data", "kFactors", mode + ".root")
    file = ROOT.TFile(filePath)
    nnlo = file.Get(mode + "_pTV_K_NNLO").Clone()
    nlo = file.Get(mode + "_pTV_K_NLO").Clone()
    ew = file.Get(mode + "_pTV_kappa_EW").Clone()
    nnlo.Divide(nlo)
    kFactors_QCD[mode] = nnlo.Clone(mode)
    kFactors_EW[mode] = ew.Clone()
    print(kFactors_QCD)
    print(kFactors_EW)

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
    wrapper.SetIntVar("Evt_ID")   
    wrapper.SetIntVar("Evt_Run")   
    wrapper.SetIntVar("Evt_Lumi") 
    wrapper.SetFloatVar("Boson_Pt") 

    for mode in ["evj","eej", "vvj", "aj"]:
        wrapper.SetFloatVar( mode + "_kFactor_QCD")
        wrapper.SetFloatVar( mode + "_kFactor_EW")
        wrapper.SetFloatVar( mode + "_kFactor")

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    # add basic information for friend trees
    wrapper.branchArrays["Evt_ID"][0] = getattr(event, "Evt_ID")
    wrapper.branchArrays["Evt_Run"][0]   = getattr(event, "Evt_Run")
    wrapper.branchArrays["Evt_Lumi"][0]  = getattr(event, "Evt_Lumi")
    
    result = {}
    for mode in ["evj","eej", "vvj", "aj"]:
        result[mode] = {
            "kFactor_QCD": 1.,
            "kFactor_EW": 1.
        }


    pT = -1.
    if "ToLNu" in sample:
        if getattr(event, "N_wBosons") >= 1:
            pT = getattr(event, "wBoson_Pt")[0]
            if  pT >= 30.:
                b = kFactors_QCD["evj"].FindBin(pT)
                result["evj"]["kFactor_QCD"] = kFactors_QCD["evj"].GetBinContent(b)
                b = kFactors_EW["evj"].FindBin(pT)
                result["evj"]["kFactor_EW"] = 1. + kFactors_EW["evj"].GetBinContent(b)
    elif "ToLL" in sample:
        if getattr(event, "N_zBosons") >= 1:
            pT = getattr(event, "zBoson_Pt")[0]
            if  pT >= 30.:
                b = kFactors_QCD["eej"].FindBin(pT)
                result["eej"]["kFactor_QCD"] = kFactors_QCD["eej"].GetBinContent(b)
                b = kFactors_EW["eej"].FindBin(pT)
                result["eej"]["kFactor_EW"] = 1. + kFactors_EW["eej"].GetBinContent(b)
    elif "NuNu" in sample:
        if getattr(event, "N_zBosons") >= 1:
            pT = getattr(event, "zBoson_Pt")[0]
            if  pT >= 30.:
                b = kFactors_QCD["vvj"].FindBin(pT)
                result["vvj"]["kFactor_QCD"] = kFactors_QCD["vvj"].GetBinContent(b)
                b = kFactors_EW["evj"].FindBin(pT)
                result["vvj"]["kFactor_EW"] = 1. + kFactors_EW["vvj"].GetBinContent(b)
    elif "G1Jet" in sample:
        if getattr(event, "N_GenIsolatedPhotons") >= 1:
            pT = getattr(event, "GenIsolatedPhoton_Pt")[0]
            if  pT >= 30.:
                b = kFactors_QCD["aj"].FindBin(pT)
                result["aj"]["kFactor_QCD"] = kFactors_QCD["aj"].GetBinContent(b)
                b = kFactors_EW["evj"].FindBin(pT)
                result["aj"]["kFactor_EW"] = 1. + kFactors_EW["aj"].GetBinContent(b)
    wrapper.branchArrays["Boson_Pt"][0] = pT
    

    for mode in ["evj","eej", "vvj", "aj"]:
        wrapper.branchArrays[ mode + "_kFactor_QCD"][0] = result[mode]["kFactor_QCD"]
        wrapper.branchArrays[ mode + "_kFactor_EW"][0] = result[mode]["kFactor_EW"]
        wrapper.branchArrays[ mode + "_kFactor"][0] =  result[mode]["kFactor_QCD"]*result[mode]["kFactor_EW"]

    return event

