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

    wrapper.SetFloatVar("pileup")
    wrapper.SetFloatVar("pileup_up_rel")
    wrapper.SetFloatVar("pileup_down_rel")

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "luminosityBlock")
    
    # cross section norm
    wrapper.branchArrays["xsNorm"][0] = genWeights.getXS("default")

    pu = puSF[year].evaluate(float(event.nTruePU), "nominal")
    wrapper.branchArrays["pileup"][0] = pu
    wrapper.branchArrays["pileup_up_rel"][0] = puSF[dataEra].evaluate(float(event.nTruePU), "up")/pu
    wrapper.branchArrays["pileup_down_rel"][0] = puSF[dataEra].evaluate(float(event.nTruePU), "down")/pu


    return event

