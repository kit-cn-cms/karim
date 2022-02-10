import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

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

    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("lumi")   

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

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    
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


    # simple pdf weight
    # TODO update 
    try:
        nom_pdf = event.Weight_pdf[0]
        if sample.startswith("TTbb"):
            weights = np.array([event.Weight_pdf[i+1] for i in range(len(event.Weight_pdf)-1)])
            avg = weights.sum(axis=0)/len(weights)
            residuals = np.array([w-avg for w in weights])
            variation = (residuals)**2
            variation = (residuals.sum(axis=0)/(len(residuals)-1))**0.5
            #variation = (np.mean(residuals**2, axis = 0))**0.5
        else:
            residuals = np.array([nom_pdf - event.Weight_pdf[i+1] for i in range(len(event.Weight_pdf)-1)])
            variation = (residuals)**2
            variation = (variation.sum(axis=0))**0.5
        wrapper.branchArrays["pdf_up"][0]       =  nom_pdf+variation
        wrapper.branchArrays["pdf_up_rel"][0]   = (nom_pdf+variation)/nom_pdf
        wrapper.branchArrays["pdf_down"][0]     =  nom_pdf-variation
        wrapper.branchArrays["pdf_down_rel"][0] = (nom_pdf-variation)/nom_pdf
    except: pass

        
    
    return event

