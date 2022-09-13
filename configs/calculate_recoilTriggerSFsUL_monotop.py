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


data = {}
for dataEra in ["2018", "2017", "2016preVFP", "2016postVFP"]:
    # short dataEra
    dataEraS = dataEra[2:]

    # dict
    data[dataEra] = {}

    # sf directory
    sfDir = os.path.join(karimpath, "data", "UL_"+dataEraS)
    # recoil trigger SFs
    recoilTrig_evaluator = _core.CorrectionSet.from_file(os.path.join(sfDir, "RecoilTriggerSF.json"))
    data[dataEra]["recoilTrig"] = recoilTrig_evaluator["RecoilTriggerSFs"]

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

    wrapper.SetFloatVar("recoil"+suffix)


    # recoil trigger scale factors
    wrapper.SetFloatVar("recoilTriggerSF"+suffix)
    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_up")
    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_down")

    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_Systup")
    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_Systdown")

    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_Statup")
    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_Statdown")


def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    recoil = getattr(event, "Hadr_Recoil_MET_T1XY_Pt"+suffix)

    wrapper.branchArrays["recoil"+suffix][0] = recoil
    if jec == "nom":
        # add basic information for friend trees
        wrapper.branchArrays["Evt_ID"][0] = getattr(event, "Evt_ID")
        wrapper.branchArrays["Evt_Run"][0]   = getattr(event, "Evt_Run")
        wrapper.branchArrays["Evt_Lumi"][0]  = getattr(event, "Evt_Lumi")

    # # recoil trigger scale factors
    if recoil > 0:
        wrapper.branchArrays["recoilTriggerSF"+suffix][0] = data[dataEra]["recoilTrig"].evaluate("central", recoil)
        wrapper.branchArrays["recoilTriggerSF"+suffix+"_up"][0] = data[dataEra]["recoilTrig"].evaluate("up", recoil)
        wrapper.branchArrays["recoilTriggerSF"+suffix+"_down"][0] = data[dataEra]["recoilTrig"].evaluate("down", recoil)

        wrapper.branchArrays["recoilTriggerSF"+suffix+"_Statup"][0] = data[dataEra]["recoilTrig"].evaluate("statup", recoil)
        wrapper.branchArrays["recoilTriggerSF"+suffix+"_Statdown"][0] = data[dataEra]["recoilTrig"].evaluate("statdown", recoil)

        wrapper.branchArrays["recoilTriggerSF"+suffix+"_Systup"][0] = data[dataEra]["recoilTrig"].evaluate("systup", recoil)
        wrapper.branchArrays["recoilTriggerSF"+suffix+"_Systdown"][0] = data[dataEra]["recoilTrig"].evaluate("systdown", recoil)
    else:
        wrapper.branchArrays["recoilTriggerSF"+suffix][0] = 1.
        wrapper.branchArrays["recoilTriggerSF"+suffix+"_up"][0] = 1.
        wrapper.branchArrays["recoilTriggerSF"+suffix+"_down"][0] = 1.

        wrapper.branchArrays["recoilTriggerSF"+suffix+"_Statup"][0] = 1.
        wrapper.branchArrays["recoilTriggerSF"+suffix+"_Statdown"][0] = 1.

        wrapper.branchArrays["recoilTriggerSF"+suffix+"_Systup"][0] = 1.
        wrapper.branchArrays["recoilTriggerSF"+suffix+"_Systdown"][0] = 1.

    return event

