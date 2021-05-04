import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
year = "2018"
sfDir = os.path.join(karimpath, "data", "legacy_"+year)

# initialize pileup SFs
pileupSFs = weightModules.PileupSFs(os.path.join(sfDir, "pileup_"+year+".csv"))

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
    wrapper.SetIntVar("event"+suffix)   
    wrapper.SetIntVar("run"+suffix)   
    wrapper.SetIntVar("lumi"+suffix)   

    # cross section weight
    wrapper.SetFloatVar("xsNorm"+suffix)

    if jec == "nom":
        # rate factors
        wrapper.SetFloatVar("muRUpRel_wRF"+suffix)
        wrapper.SetFloatVar("muFUpRel_wRF"+suffix)
        wrapper.SetFloatVar("muRDownRel_wRF"+suffix)
        wrapper.SetFloatVar("muFDownRel_wRF"+suffix)

        wrapper.SetFloatVar("isrUpRel_wRF"+suffix)
        wrapper.SetFloatVar("fsrUpRel_wRF"+suffix)
        wrapper.SetFloatVar("isrDownRel_wRF"+suffix)
        wrapper.SetFloatVar("fsrDownRel_wRF"+suffix)

    wrapper.SetFloatVar("pileup"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("pileup_up_rel"+suffix)
        wrapper.SetFloatVar("pileup_down_rel"+suffix)

    
    

def calculate_variables(event, wrapper, sample, jec, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    if getattr(event, "isRecoSelected"+suffix) < 1. and getattr(event,  "isGenSelected"+suffix) < 1.: 
        return event

    # add basic information for friend trees
    wrapper.branchArrays["event"+suffix][0] = getattr(event, "event"+suffix)
    wrapper.branchArrays["run"+suffix][0]   = getattr(event, "run"+suffix)
    wrapper.branchArrays["lumi"+suffix][0]  = getattr(event, "lumi"+suffix)
    
    # cross section norm
    wrapper.branchArrays["xsNorm"+suffix][0] = genWeights.getXS("incl")

    # rate factors
    # apply them directly to the weights
    if jec == "nom":
        try:
            wrapper.branchArrays["muRUpRel_wRF"  +suffix][0] = getattr(event, "Weight_muRUp"  +suffix) * genWeights.getRF("LHEScaleWeight_incl_1")
            wrapper.branchArrays["muRDownRel_wRF"+suffix][0] = getattr(event, "Weight_muRDown"+suffix) * genWeights.getRF("LHEScaleWeight_incl_5")
            wrapper.branchArrays["muFUpRel_wRF"  +suffix][0] = getattr(event, "Weight_muFUp"  +suffix) * genWeights.getRF("LHEScaleWeight_incl_3")
            wrapper.branchArrays["muFDownRel_wRF"+suffix][0] = getattr(event, "Weight_muFDown"+suffix) * genWeights.getRF("LHEScaleWeight_incl_7")
        except: pass
        try:
            wrapper.branchArrays["isrUpRel_wRF"  +suffix][0] = getattr(event, "GenWeight_isr_Def_up"  +suffix) * genWeights.getRF("PSWeight_incl_2")
            wrapper.branchArrays["isrDownRel_wRF"+suffix][0] = getattr(event, "GenWeight_isr_Def_down"+suffix) * genWeights.getRF("PSWeight_incl_0")
            wrapper.branchArrays["fsrUpRel_wRF"  +suffix][0] = getattr(event, "GenWeight_fsr_Def_up"  +suffix) * genWeights.getRF("PSWeight_incl_3")
            wrapper.branchArrays["fsrDownRel_wRF"+suffix][0] = getattr(event, "GenWeight_fsr_Def_down"+suffix) * genWeights.getRF("PSWeight_incl_1")
        except: pass

    puSF = pileupSFs.getSF(getattr(event, "nTruePU"+suffix), "central")
    wrapper.branchArrays["pileup"+suffix][0] = puSF
    if jec == "nom":
        wrapper.branchArrays["pileup_up_rel"+suffix][0] = pileupSFs.getSF(getattr(event, "nTruePU"+suffix), "up")/puSF
        wrapper.branchArrays["pileup_down_rel"+suffix][0] = pileupSFs.getSF(getattr(event, "nTruePU"+suffix), "down")/puSF
    return event

