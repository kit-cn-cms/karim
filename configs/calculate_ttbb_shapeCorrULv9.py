import numpy as np
import common
import weightModules
from array import array
import os
import sys
from correctionlib import _core
jsonDir = os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG")

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))


corr = {}
simple = {}
for year in ["2017", "2018", "2016postVFP", "2016preVFP"]:
    yearS = year[2:]
    sfDir = os.path.join(karimpath, "data", "UL_"+yearS)

    # electron trigger
    corrFile = _core.CorrectionSet.from_file(
        os.path.join(sfDir, "btagCorrection_ttbb_deepJet.json"))
    corr[year] = corrFile["shape_correction"]
    simple[year] = corrFile["simple_shape_correction"]

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

    wrapper.SetFloatVar("btagCorr"+suffix)
    wrapper.SetFloatVar("btagCorrSimple"+suffix)

def get_proc(event, sample):
    if sample.startswith("TTbb"):
        return "ttbb"
    elif sample.startswith("ST"):
        return "singlet"
    elif sample.startswith("DY") or sample.startswith("WJet"):
        return "vjets"
    elif sample.startswith("ttH") or sample.startswith("TTZ") or sample.startswith("TTW"):
        return "ttX"
    elif sample.startswith("TTTo"):
        if event.is_ttbb64 or event.is_ttbj64:
            return "ttbb_5FS"
        elif event.is_ttcc64:
            return "ttcc"
        else:
            return "ttjj"
    else: 
        return "MC"

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec

    proc = get_proc(event, sample)
    nJet = getattr(event, "nJets"+suffix)
    ht = getattr(event, "HT_jets"+suffix)
    c = corr[dataEra].evaluate(proc, max(min(nJet, 8), 4), float(event.nPV), ht)
    wrapper.branchArrays["btagCorr"+suffix][0] = c
    s = simple[dataEra].evaluate(proc, float(nJet), ht)
    wrapper.branchArrays["btagCorrSimple"+suffix][0] = s
    

    return event

