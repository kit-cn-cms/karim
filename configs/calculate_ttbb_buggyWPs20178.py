import numpy as np
import common
import weightModules
from array import array
import os
import sys
from correctionlib import _core

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

    # b tagging
    wrapper.SetIntVar("nTagsT"+suffix)
    wrapper.SetIntVar("nTagsM"+suffix)
    wrapper.SetIntVar("nTagsL"+suffix)

    wrapper.SetIntVar("nJets"+suffix)

    wrapper.SetFloatVarArray("Jet_taggedT"+suffix, "nJets"+suffix)
    wrapper.SetFloatVarArray("Jet_taggedM"+suffix, "nJets"+suffix)
    wrapper.SetFloatVarArray("Jet_taggedL"+suffix, "nJets"+suffix)


def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    nTagsT = 0
    nTagsM = 0
    nTagsL = 0
    wrapper.branchArrays["nJets"+suffix][0] = getattr(event, "nJets"+suffix)
    for idx in range(getattr(event, "nJets"+suffix)):
        wrapper.branchArrays["Jet_taggedT"+suffix][idx] = getattr(event, "Jet_taggedT"+suffix)[idx]
        wrapper.branchArrays["Jet_taggedM"+suffix][idx] = getattr(event, "Jet_taggedM"+suffix)[idx]
        wrapper.branchArrays["Jet_taggedL"+suffix][idx] = getattr(event, "Jet_taggedL"+suffix)[idx]
        if getattr(event, "Jet_taggedL"+suffix)[idx]:
            nTagsL+=1
            if getattr(event, "Jet_taggedM"+suffix)[idx]:
                nTagsM+=1
                if getattr(event, "Jet_taggedT"+suffix)[idx]:
                    nTagsT+=1
    
    wrapper.branchArrays["nTagsT"+suffix][0] = nTagsT
    wrapper.branchArrays["nTagsM"+suffix][0] = nTagsM
    wrapper.branchArrays["nTagsL"+suffix][0] = nTagsL

    return event

