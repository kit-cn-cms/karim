import numpy as np
import common
import weightModules
from array import array
import os
from itertools import combinations 

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

def get_additional_variables():
    '''                                                                                                                                                                 
    get names of additional variables which are already defined in ntuples                                                                                              
    which are needed for the dnn inputs                                                                                                                                 
    '''
    variables = [
        "event",
        "genJet_jetMatcherClass",
        "genJet_hadronFlavour",
        "nGenJets",
        "nGenBJets",
        "nGenCJets",
        
        ]
    return variables

def base_selection(event):
    return True

def set_branches(wrapper, jec):
    wrapper.SetIntVar("event")
    wrapper.SetIntVar("genJet_jetMatcherClass")
    wrapper.SetIntVar("genJet_hadronFlavour")
    wrapper.SetIntVar("nGenJets")
    wrapper.SetIntVar("nGenBJets")
    wrapper.SetIntVar("nGenCJets")

    #wrapper.SetIntVar("allisZbb")
    #wrapper.SetIntVar("allisZcc")
    #wrapper.SetIntVar("isZbb")
    #wrapper.SetIntVar("isZcc")
    #wrapper.SetFloatVar("nZbb")
    #wrapper.SetFloatVar("nZcc")

    wrapper.SetIntVar("allisHbb")
    wrapper.SetIntVar("allisHcc")
    wrapper.SetIntVar("isHbb")
    wrapper.SetIntVar("isHcc")
    wrapper.SetFloatVar("nHbb")
    wrapper.SetFloatVar("nHcc")
    #wrapper.SetFloatVarArray("zJetFlavours","genJet_hadronFlavour")
   

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):

    wrapper.branchArrays["event"][0] = getattr(event, "event")

    hJetFlavours =[]
    allisHbb = 0
    allisHcc = 0
    nHbb  = 0
    nHcc  = 0
    for i in range(event.nGenJets):
        #if event.genJet_jetMatcherClass[i] == 5: zJetFlavours.append(event.genJet_hadronFlavour[i])
        if event.genJet_jetMatcherClass[i] == 4: hJetFlavours.append(event.genJet_hadronFlavour[i])
    

    ##ttH decay fractions
    if all([f==5 for f in hJetFlavours]):   
        allisHbb = 1
    elif all([f==4 for f in hJetFlavours]): 
        allisHcc = 1
    else:
        allisHbb = 0
        allisHcc = 0
        
    for i in range(0,len(hJetFlavours)):
        if hJetFlavours[i]==5:
             nHbb += 1
        elif hJetFlavours[i]==4:
             nHcc += 1

    if nHbb % 2 ==0: isHbb = nHbb/2
    else:            isHbb = (nHbb/2)+1
    if nHcc % 2==0:  isHcc = nHcc/2
    else:            isHcc= (nHcc/2)+1
    
    
    wrapper.branchArrays["allisHbb"][0] = allisHbb
    wrapper.branchArrays["allisHcc"][0] = allisHcc
    wrapper.branchArrays["isHbb"][0]    = isHbb
    wrapper.branchArrays["isHcc"][0]    = isHcc
    wrapper.branchArrays["nHbb"][0]     = nHbb
    wrapper.branchArrays["nHcc"][0]     = nHcc

    return event

    
