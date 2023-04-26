import numpy as np
import common
import weightModules
from array import array
import os
import pandas as pd

def _dPhi(phi1, phi2):
    dphi = abs(phi1-phi2)
    return dphi*(dphi<np.pi)+(2.*np.pi-dphi)*(dphi>=np.pi)

def _dEta(eta1, eta2):
    return abs(eta1-eta2)

def _dR(eta1, phi1, eta2, phi2):
    dphi = _dPhi(phi1, phi2)
    deta = _dEta(eta1, eta2)

    dR = np.sqrt(dphi*dphi + deta*deta)
    return dR

def _pT(pt1, phi1, pt2, phi2):
    dphi = _dPhi(phi1, phi2)
    return np.sqrt(pt1*pt1+pt2*pt2+2*pt1*pt2*np.cos(dphi))

def _Minv(pt1, eta1, phi1, m1, e1, pt2, eta2, phi2, m2, e2):
    dphi = _dPhi(phi1, phi2)
    return np.sqrt(m1*m1+m2*m2+2*(e1*e2-pt1*pt2*(np.cos(dphi)+np.sinh(eta1)*np.sinh(eta2))))

def eT(pt1, m1):
    return np.sqrt(pt1*pt1+m1*m1)

def _mT(pt1, phi1, pt2, phi2, m1, m2):
    mtsq = m1*m1+m2*m2+2*(eT(pt1,m1)*eT(pt2, m2)-pt1*pt2*np.cos(_dPhi(phi1, phi2)))
    return np.sqrt(mtsq)

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
    '''
    initialize branches of output root file
    '''
    if jec=="nominal":
        wrapper.SetIntVar("event")   
        wrapper.SetIntVar("run")   
        wrapper.SetIntVar("lumi")
        suffix = "_nominal"
    if jec is None:
        wrapper.SetIntVar("event")   
        wrapper.SetIntVar("run")   
        wrapper.SetIntVar("lumi")        
        suffix = "_nominal"

    wrapper.SetFloatVar("ttB"+suffix)
    wrapper.SetFloatVar("ttH"+suffix)
    wrapper.SetFloatVar("ttZB"+suffix)
    wrapper.SetFloatVar("ttZnonB"+suffix)
    wrapper.SetFloatVar("ttC"+suffix)
    wrapper.SetFloatVar("ttLF"+suffix)
    wrapper.SetFloatVar("other"+suffix)
    wrapper.SetFloatVar("HvB"+suffix)
    wrapper.SetFloatVar("HvZ"+suffix)
    wrapper.SetFloatVar("HvC"+suffix)
    wrapper.SetFloatVar("HvLFO"+suffix)
    wrapper.SetFloatVar("ZvB"+suffix)
    wrapper.SetFloatVar("ZvH"+suffix)
    wrapper.SetFloatVar("ZvC"+suffix)
    wrapper.SetFloatVar("ZvLFO"+suffix)
    wrapper.SetFloatVar("BvH"+suffix)
    wrapper.SetFloatVar("BvZ"+suffix)
    wrapper.SetFloatVar("BvC"+suffix)
    wrapper.SetFloatVar("BvLFO"+suffix)
    wrapper.SetFloatVar("CvH"+suffix)
    wrapper.SetFloatVar("CvZ"+suffix)
    wrapper.SetFloatVar("CvB"+suffix)
    wrapper.SetFloatVar("CvLFO"+suffix)


    wrapper.SetIntVar("top_idx"+suffix)


def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None, nodes=None, graph=None, edge=None):

    suffix = "_{}".format(jec)
    if jec is None:
        suffix = "_nominal"
    ttB = -99
    ttH = -99
    ttZB = -99
    ttZnonB = -99
    ttC = -99
    ttLF = -99
    other = -99
    HvB = -99
    HvZ = -99
    HvC = -99
    HvLFO = -99
    ZvB = -99
    ZvH = -99
    ZvC = -99
    ZvLFO = -99
    BvH = -99
    BvZ = -99
    BvC = -99
    BvLFO = -99
    CvH = -99
    CvZ = -99
    CvB = -99
    CvLFO = -99

    idx = -99

    event_ = getattr(event, "event")
    run = getattr(event, "run")
    lumi = getattr(event, "luminosityBlock")

    try:
        ttB = graph["ttB"+suffix]
        ttH = graph["ttH"+suffix]
        ttZB = graph["ttZB"+suffix]
        ttZnonB = graph["ttZnonB"+suffix]
        ttC = graph["ttC"+suffix]
        ttLF = graph["ttLF"+suffix]
        other = graph["other"+suffix]

        HvB = ttH/(ttB+ttH)
        HvZ = ttH/(ttH+ttZB+ttZnonB)
        HvC = ttH/(ttH+ttC)
        HvLFO = ttH/(ttH+ttLF+other)

        ZvB = (ttZB+ttZnonB)/(ttB+ttZB+ttZnonB)
        ZvH = (ttZB+ttZnonB)/(ttH+ttZB+ttZnonB)
        ZvC = (ttZB+ttZnonB)/(ttZB+ttZnonB+ttC)
        ZvLFO = (ttZB+ttZnonB)/(ttZB+ttZnonB+ttLF+other)

        BvH = ttB/(ttB+ttH)
        BvZ = ttB/(ttB+ttZB+ttZnonB)
        BvC = ttB/(ttB+ttC)
        BvLFO = ttB/(ttB+ttLF+other)
        CvH = ttC/(ttC+ttH)
        CvZ = ttC/(ttC+ttZB+ttZnonB)
        CvB = ttC/(ttC+ttB)
        CvLFO = ttC/(ttC+ttLF+other)

        idx = graph[["ttB"+suffix,"ttH"+suffix,"ttZB"+suffix,"ttZnonB"+suffix,"ttC"+suffix,"ttLF"+suffix,"other"+suffix]].idxmax(axis="columns").item()
        if idx=="ttB"+suffix:
            idx=0
        elif idx=="ttH"+suffix:
            idx=1
        elif idx=="ttZB"+suffix:
            idx=2
        elif idx=="ttZnonB"+suffix:
            idx=3
        elif idx=="ttC"+suffix:
            idx=4
        elif idx=="ttLF"+suffix:
            idx=5
        elif idx=="other"+suffix:
            idx=6
        else:
            idx=-99  

    except:
        pass

    # add basic information for friend trees
    if jec=="nominal" or jec is None:
        wrapper.branchArrays["event"][0] = event_
        wrapper.branchArrays["run"][0]   = run
        wrapper.branchArrays["lumi"][0]  = lumi

    wrapper.branchArrays["ttB"+suffix][0] = ttB
    wrapper.branchArrays["ttH"+suffix][0] = ttH
    wrapper.branchArrays["ttZB"+suffix][0] = ttZB
    wrapper.branchArrays["ttZnonB"+suffix][0] = ttZnonB
    wrapper.branchArrays["ttC"+suffix][0] = ttC
    wrapper.branchArrays["ttLF"+suffix][0] = ttLF
    wrapper.branchArrays["other"+suffix][0] = other
    wrapper.branchArrays["HvB"+suffix][0] = HvB
    wrapper.branchArrays["HvZ"+suffix][0] = HvZ
    wrapper.branchArrays["HvC"+suffix][0] = HvC
    wrapper.branchArrays["HvLFO"+suffix][0] = HvLFO
    wrapper.branchArrays["ZvB"+suffix][0] = ZvB
    wrapper.branchArrays["ZvH"+suffix][0] = ZvH
    wrapper.branchArrays["ZvC"+suffix][0] = ZvC
    wrapper.branchArrays["ZvLFO"+suffix][0] = ZvLFO    
    wrapper.branchArrays["BvH"+suffix][0] = BvH
    wrapper.branchArrays["BvZ"+suffix][0] = BvZ
    wrapper.branchArrays["BvC"+suffix][0] = BvC
    wrapper.branchArrays["BvLFO"+suffix][0] = BvLFO
    wrapper.branchArrays["CvH"+suffix][0] = CvH
    wrapper.branchArrays["CvZ"+suffix][0] = CvZ
    wrapper.branchArrays["CvB"+suffix][0] = CvB
    wrapper.branchArrays["CvLFO"+suffix][0] = CvLFO


    wrapper.branchArrays["top_idx"+suffix][0] = int(idx)    

    # print("event: ", event)
    return event