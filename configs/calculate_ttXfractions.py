import numpy as np
import common
import weightModules
from array import array
import os
from itertools import combinations 

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
        #"Weight_GEN"
        ]
    return variables

def base_selection(event):
    return True

def set_branches(wrapper):
    wrapper.SetIntVar("event")
    wrapper.SetIntVar("genJet_jetMatcherClass")
    wrapper.SetIntVar("genJet_hadronFlavour")
    wrapper.SetIntVar("nGenJets")
    wrapper.SetIntVar("nGenBJets")
    wrapper.SetIntVar("nGenCJets")

    wrapper.SetIntVar("allisZbb")
    wrapper.SetIntVar("allisZcc")
    wrapper.SetIntVar("isZbb")
    wrapper.SetIntVar("isZcc")
    wrapper.SetFloatVar("nZbb")
    wrapper.SetFloatVar("nZcc")
             
   

def calculate_variables():

    wrapper.branchArrays["event"][0] = getattr(event, "event")

    zJetFlavours = []
    nZbb  = 0
    nZcc  = 0
    for i in range(event.nGenJets):
        if event.genJet_jetMatcherClass[i] == 5: zjetFlavours.append(event.genjet_hadronFlavour[i])


    #2 jets coming from the Z, so in the best case, the events have nZbb = 2 when isZbb = 1
    #zJetFlavours_combn = [i for i in combinations(zJetFlavours,2)]
    
    if all(f==5 for f in zJetFlavours):   
        allisZbb = 1
    elif all([f==4 for f in zJetFlavours): 
        allisZcc = 1
    else:
        allisZbb = 0
        allisZcc = 0

    #for i in range(0,len(zJetFlavours_combn)):
    #    if zJetFlavours_combn[i]==(5,5):
    #        #isZbb[i] = 1
    #        nbfromZ    += 1
    #    elif zJetFlavours_combn[i]==(4,4):
    #        #isZcc[i] = 1
    #        ncfromZ    += 1
    #    
    for i in range(0,len(zJetFlavours)):
        if zJetFlavour[i]==5:
             nZbb += 1
        elif zJetFlavour[i]==4:
             nZcc += 1

    if nZbb % 2 ==0: isZbb = nZbb/2
    else:            isZbb = (nZbb/2)+1
    if nZcc % 2==0:  isZbb = nZcc/2
    else:            isZcc= (nZcc/2)+1
             
  
    wrapper.branchArrays["allisZbb"][0] = allisZbb
    wrapper.branchArrays["allisZcc"][0] = allisZcc
    wrapper.branchArrays["isZbb"][0]    = isZbb
    wrapper.branchArrays["isZcc"][0]    = isZcc
    wrapper.branchArrays["nZbb"][0]     = nZbb
    wrapper.branchArrays["nZcc"][0]     = nZcc

    return event

    
