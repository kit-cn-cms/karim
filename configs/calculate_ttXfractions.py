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

    wrapper.SetIntVar("isZbb")
    wrapper.SetIntVar("isZcc")
    wrapper.SetFloatVar("nZbb")
    wrapper.SetFloatVar("nZcc")
   # wrapper.SetFloatVar("Zbb_frac")
   # wrapper.SetFloatVar("Zcc_frac")
    
   # wrapper.SetIntVar("isZbb","nGenBJets")
   # wrapper.SetIntVar("isZcc","nGenCJets")
   #wrapper.SetFloatVar("Weight_GEN")

def calculate_variables():

    wrapper.branchArrays["event"][0] = getattr(event, "event")

    zJetFlavours = []
    nZbb  = 0
    nZcc  = 0
    for i in nGenJets:
        if genJet_jetMatcherClass[i] == 5: zjetFlavours.append(genjet_hadronFlavour[i])


    #2 jets coming from the Z, so in the best case, the events have nZbb = 2 when isZbb = 1
    zJetFlavours_combn = [i for i in combinations(zJetFlavours,2)]
    
    if all(zJetFlavours==5):   
        isZbb = 1
    elif all(zJetFlavours==4): 
        isZcc = 1
    else:
        isZbb = 0
        isZcc = 0

    for i in range(0,len(zJetFlavours_combn)):
        if zJetFlavours_combn[i]==(5,5):
            #isZbb[i] = 1
            nZbb    += 1
            isZbb    = 1
        elif zJetFlavours_combn[i]==(4,4):
            #isZcc[i] = 1
            nZcc    += 1
            isZcc    = 1
        else:
            isZbb = 0
            isZcc = 0

    #isZbb = nZbb/event.Weight_GEN
    #isZcc = nZcc/event.Weight_GEN
  
    wrapper.branchArrays["isZbb"][0] = isZbb
    wrapper.branchArrays["isZcc"][0] = isZcc
    wrapper.branchArrays["nZbb"][0]  = nZbb
    wrapper.branchArrays["nZcc"][0]  = nZcc

    return event

    
