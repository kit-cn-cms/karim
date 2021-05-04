import numpy as np
import common
from array import array

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "event",
        "run",
        "lumi"
        ]
    return variables

def base_selection(event):
    return getattr(event, "N_Jets"+suff)>=4

def set_branches(wrapper, jec):
    suff = "_"+jec
    wrapper.SetIntVar("event"+suff)   
    wrapper.SetIntVar("run"+suff)   
    wrapper.SetIntVar("lumi"+suff)   
    wrapper.SetIntVar("oddId"+suff)

def calculate_variables(event, wrapper, sampleName, jec):
    '''
    calculate additional variables needed
    '''
    suff = "_"+jec

    wrapper.branchArrays["event"+suff][0] = getattr(event, "event"+suff)
    wrapper.branchArrays["run"+suff][0]   = getattr(event, "run"+suff)
    wrapper.branchArrays["lumi"+suff][0]  = getattr(event, "lumi"+suff)
    wrapper.branchArrays["oddId"+suff][0] = getattr(event, "event"+suff)%2

    return event

