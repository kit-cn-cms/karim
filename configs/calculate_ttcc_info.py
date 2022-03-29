import numpy as np
import common
import weightModules
from array import array
import os
from correctionlib import _core

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))


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

    wrapper.SetIntVar("top_b1_idx"+suffix)
    wrapper.SetIntVar("top_b2_idx"+suffix)
    wrapper.SetIntVar("add_j1_idx"+suffix)
    wrapper.SetIntVar("add_j2_idx"+suffix)
    wrapper.SetIntVar("light_j1_idx"+suffix)
    wrapper.SetIntVar("light_j2_idx"+suffix)
    
def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec

    btagValues = list(getattr(event, "Jets_btagDeepFlavB"+suffix))
    indices = np.argsort(np.array(btagValues))[::-1]
    
    if len(indices) >= 4:
        wrapper.branchArrays["top_b1_idx"+suffix][0] = indices[0]
        wrapper.branchArrays["top_b2_idx"+suffix][0] = indices[1]
        wrapper.branchArrays["add_j1_idx"+suffix][0] = indices[2]
        wrapper.branchArrays["add_j2_idx"+suffix][0] = indices[3]
        if len(indices) >= 6:
            wrapper.branchArrays["light_j1_idx"+suffix][0] = indices[4]
            wrapper.branchArrays["light_j2_idx"+suffix][0] = indices[5]

    return event

