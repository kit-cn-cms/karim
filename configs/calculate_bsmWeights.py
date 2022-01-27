import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "muTrig",
        "tauTrig",
        "nMu",
        "nVetoMu",
        "nTaus_corr",
        "nPairs_corr",
        "Weight_GEN",
        "nJets_corr_nom",
        "nTagsM_corr_nom",
        "SystemFlag_corr_nom",
        ]
    return variables

def base_selection(event):
    return True

def set_branches(wrapper, jec = None):

    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("lumi") 
    
    #wrapper.SetIntVar("nTagsM_nom")
    #wrapper.SetIntVar("nJets_nom")
    #wrapper.SetIntVar("nMu")
    
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

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    
    #wrapper.branchArrays["nTagsM_nom"] = getattr(event, "nTagsM_nom")
    #wrapper.branchArrays["nJets_nom"] = getattr(event, "nJets_nom")
    #wrapper.branchArrays["nMu"] = getattr(event, "nMu")
    
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
    return event

