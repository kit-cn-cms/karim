


import ROOT
import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

ROOT.TH1.AddDirectory(False)
kFactors_QCD = {}
kFactors_EW = {}
kFactors_EW1 = {}
kFactors_EW2 = {}
kFactors_EW3 = {}
for mode in ["evj","eej", "vvj", "aj"]:
    filePath = os.path.join(karimpath, "data", "kFactors", mode + ".root")
    file = ROOT.TFile(filePath)
    nnlo = file.Get(mode + "_pTV_K_NNLO").Clone()
    nlo = file.Get(mode + "_pTV_K_NLO").Clone()
    ew = file.Get(mode + "_pTV_kappa_EW").Clone()
    ew1 = file.Get(mode + "_pTV_d1kappa_EW").Clone()
    ew2 = file.Get(mode + "_pTV_d2kappa_EW").Clone()
    ew3 = file.Get(mode + "_pTV_d3kappa_EW").Clone()
    nnlo.Divide(nlo)
    kFactors_QCD[mode] = nnlo.Clone(mode)
    kFactors_EW[mode] = ew.Clone()
    kFactors_EW1[mode] = ew1.Clone()
    kFactors_EW2[mode] = ew2.Clone()
    kFactors_EW3[mode] = ew3.Clone()
    print("QCD:", kFactors_QCD)
    print("EW", kFactors_EW)
    print("EW1", kFactors_EW1)
    print("EW2", kFactors_EW2)
    print("EW3", kFactors_EW3)

from correctionlib import _core
jsonDir = os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG")
puName = {
    "2016preVFP":   "Collisions16_UltraLegacy_goldenJSON",
    "2016postVFP":  "Collisions16_UltraLegacy_goldenJSON",
    "2017":         "Collisions17_UltraLegacy_goldenJSON",
    "2018":         "Collisions18_UltraLegacy_goldenJSON",
    }

puSF = {}
for year in ["2016preVFP", "2016postVFP", "2017", "2018"]:
    # initialize pileup SFs
    pu_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "LUM", year+"_UL", "puWeights.json.gz"))
    puSF[year] = pu_evaluator[puName[year]]

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
  

    # cross section weight
    wrapper.SetFloatVar("xsNorm")

    # rate factors
    wrapper.SetFloatVar("muRUpRel_wRF")
    wrapper.SetFloatVar("muFUpRel_wRF")
    wrapper.SetFloatVar("muRDownRel_wRF")
    wrapper.SetFloatVar("muFDownRel_wRF")
    wrapper.SetFloatVar("muRUpRel")
    wrapper.SetFloatVar("muFUpRel")
    wrapper.SetFloatVar("muRDownRel")
    wrapper.SetFloatVar("muFDownRel")

    wrapper.SetFloatVar("isrUpRel_wRF")
    wrapper.SetFloatVar("fsrUpRel_wRF")
    wrapper.SetFloatVar("isrDownRel_wRF")
    wrapper.SetFloatVar("fsrDownRel_wRF")
    wrapper.SetFloatVar("isrUpRel")
    wrapper.SetFloatVar("fsrUpRel")
    wrapper.SetFloatVar("isrDownRel")
    wrapper.SetFloatVar("fsrDownRel")

    wrapper.SetFloatVar("pileup")
    wrapper.SetFloatVar("pileup_up_rel")
    wrapper.SetFloatVar("pileup_down_rel")

    wrapper.SetFloatVar("pdf_up")
    wrapper.SetFloatVar("pdf_up_rel")
    wrapper.SetFloatVar("pdf_down")
    wrapper.SetFloatVar("pdf_down_rel")

    wrapper.SetFloatVar("Boson_Pt") 
    for mode in ["evj","eej", "vvj", "aj"]:
        wrapper.SetFloatVar( mode + "_kFactor_EW")
        wrapper.SetFloatVar( mode + "_kFactor_EW1up_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW1down_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW2up_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW2down_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW3up_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW3down_rel")
        # wrapper.SetFloatVar( mode + "_kFactor_QCD")
        # wrapper.SetFloatVar( mode + "_kFactor_rel")


def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    # add basic information for friend trees
    wrapper.branchArrays["Evt_ID"][0] = getattr(event, "Evt_ID")
    wrapper.branchArrays["Evt_Run"][0]   = getattr(event, "Evt_Run")
    wrapper.branchArrays["Evt_Lumi"][0]  = getattr(event, "Evt_Lumi")
    
    # cross section norm
    wrapper.branchArrays["xsNorm"][0] = genWeights.getXS("incl")

    # rate factors
    # apply them directly to the weights
    try:
        wrapper.branchArrays["muRUpRel_wRF"  ][0] = getattr(event, "Weight_muRUp"  ) * genWeights.getRF("LHEScaleWeight_incl_1")
        wrapper.branchArrays["muRDownRel_wRF"][0] = getattr(event, "Weight_muRDown") * genWeights.getRF("LHEScaleWeight_incl_5")
        wrapper.branchArrays["muFUpRel_wRF"  ][0] = getattr(event, "Weight_muFUp"  ) * genWeights.getRF("LHEScaleWeight_incl_3")
        wrapper.branchArrays["muFDownRel_wRF"][0] = getattr(event, "Weight_muFDown") * genWeights.getRF("LHEScaleWeight_incl_7")
    except: pass
    try:
        wrapper.branchArrays["muRUpRel"  ][0] = getattr(event, "Weight_muRUp"  ) 
        wrapper.branchArrays["muRDownRel"][0] = getattr(event, "Weight_muRDown")
        wrapper.branchArrays["muFUpRel"  ][0] = getattr(event, "Weight_muFUp"  )
        wrapper.branchArrays["muFDownRel"][0] = getattr(event, "Weight_muFDown")
    except: pass
    try:
        wrapper.branchArrays["isrUpRel_wRF"  ][0] = getattr(event, "Weight_isrUp"  ) * genWeights.getRF("PSWeight_incl_2")
        wrapper.branchArrays["isrDownRel_wRF"][0] = getattr(event, "Weight_isrDown") * genWeights.getRF("PSWeight_incl_0")
        wrapper.branchArrays["fsrUpRel_wRF"  ][0] = getattr(event, "Weight_fsrUp"  ) * genWeights.getRF("PSWeight_incl_3")
        wrapper.branchArrays["fsrDownRel_wRF"][0] = getattr(event, "Weight_fsrDown") * genWeights.getRF("PSWeight_incl_1")
    except: pass
    try:
        wrapper.branchArrays["isrUpRel"  ][0] = getattr(event, "Weight_isrUp"  )
        wrapper.branchArrays["isrDownRel"][0] = getattr(event, "Weight_isrDown")
        wrapper.branchArrays["fsrUpRel"  ][0] = getattr(event, "Weight_fsrUp"  )
        wrapper.branchArrays["fsrDownRel"][0] = getattr(event, "Weight_fsrDown")
    except: pass

    pu = puSF[year].evaluate(float(event.nTruePU), "nominal")
    wrapper.branchArrays["pileup"][0] = pu
    wrapper.branchArrays["pileup_up_rel"][0] = puSF[dataEra].evaluate(float(event.nTruePU), "up")/pu
    wrapper.branchArrays["pileup_down_rel"][0] = puSF[dataEra].evaluate(float(event.nTruePU), "down")/pu

    # calculate kFactors
    result = {}
    for mode in ["evj","eej", "vvj", "aj"]:
        result[mode] = {
            # "kFactor_QCD": 1.,
            "kFactor_EW": 1.,
            "kFactor_EW1_up_rel": 1.,
            "kFactor_EW1_down_rel": 1.,
            "kFactor_EW2_up_rel": 1.,
            "kFactor_EW2_down_rel": 1.,
            "kFactor_EW3_up_rel": 1.,
            "kFactor_EW3_down_rel": 1.,
        }


    pT = -1.
    if "ToLNu" in sample:
        label = "evj"
        if getattr(event, "N_wBosons") >= 1:
            pT = getattr(event, "wBoson_Pt")[0]
    elif "ToLL" in sample:
        label = "eej"
        if getattr(event, "N_zBosons") >= 1:
            pT = getattr(event, "zBoson_Pt")[0]
    elif "NuNu" in sample:
        label = "vvj"
        if getattr(event, "N_zBosons") >= 1:
            pT = getattr(event, "zBoson_Pt")[0]

    if  pT >= 30.:
        b = kFactors_QCD[label].FindBin(pT)
        result[label]["kFactor_QCD"] = kFactors_QCD[label].GetBinContent(b)

        b = kFactors_EW[label].FindBin(pT)
        nom = 1. + kFactors_EW[label].GetBinContent(b)
        ew1 = kFactors_EW1[label].GetBinContent(b)
        ew2 = kFactors_EW2[label].GetBinContent(b)
        ew3 = kFactors_EW3[label].GetBinContent(b)

        result[label]["kFactor_EW"] = nom
        
        result[label]["kFactor_EW1_up_rel"] = (nom + ew1)/nom
        result[label]["kFactor_EW1_down_rel"] = (nom - ew1)/nom

        result[label]["kFactor_EW2_up_rel"] = (nom + ew2)/nom
        result[label]["kFactor_EW2_down_rel"] = (nom - ew2)/nom

        result[label]["kFactor_EW3_up_rel"] = (nom + ew3)/nom
        result[label]["kFactor_EW3_down_rel"] = (nom - ew3)/nom

    wrapper.branchArrays["Boson_Pt"][0] = pT
    

    for mode in ["evj","eej", "vvj", "aj"]:
        wrapper.branchArrays[ mode + "_kFactor_EW"][0] = result[mode]["kFactor_EW"]
        wrapper.branchArrays[ mode + "_kFactor_EW1up_rel"][0] = result[mode]["kFactor_EW1_up_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW1down_rel"][0] = result[mode]["kFactor_EW1_down_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW2up_rel"][0] = result[mode]["kFactor_EW2_up_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW2down_rel"][0] = result[mode]["kFactor_EW2_down_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW3up_rel"][0] = result[mode]["kFactor_EW3_up_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW3down_rel"][0] = result[mode]["kFactor_EW3_down_rel"]
        # wrapper.branchArrays[ mode + "_kFactor_QCD"][0] = result[mode]["kFactor_QCD"]
        # wrapper.branchArrays[ mode + "_kFactor"][0] =  result[mode]["kFactor_QCD"]*result[mode]["kFactor_EW"] 


    # simple pdf weight
    # TODO update 
    # nom_pdf = event.Weight_pdf[0]
    # residuals = np.array([nom_pdf - event.Weight_pdf[i+1] for i in range(len(event.Weight_pdf)-1)])
    # if sample.startswith("TTbb"):
    #     variation = (np.mean(residuals**2, axis = 0))**0.5
    # else:
    #     variation = (residuals)**2
    #     variation = (variation.sum(axis=0))**0.5
    # wrapper.branchArrays["pdf_up"][0]       =  nom_pdf+variation
    # wrapper.branchArrays["pdf_up_rel"][0]   = (nom_pdf+variation)/nom_pdf
    # wrapper.branchArrays["pdf_down"][0]     =  nom_pdf-variation
    # wrapper.branchArrays["pdf_down_rel"][0] = (nom_pdf-variation)/nom_pdf

        
    
    return event

