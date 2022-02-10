import numpy as np
import common
import weightModules
from array import array
import os

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

    wrapper.SetFloatVar("isZbb")
    wrapper.SetFloatVar("isZcc")
    wrapper.SetFloatVar("nZbb")
    wrapper.SetFloatVar("nZcc")
   # wrapper.SetFloatVar("Zbb_frac")
   # wrapper.SetFloatVar("Zcc_frac")
    
   # wrapper.SetIntVar("isZbb","nGenBJets")
   # wrapper.SetIntVar("isZcc","nGenCJets")
   #wrapper.SetFloatVar("Weight_GEN")

def calculate_variables():
    zJetFlavours = []
    isZbb = 1.
    isZcc = 1.
    nZbb  = 0
    nZcc  = 0
    for i in nGenJets:
        if genJet_jetMatcherClass[i] == 5: zjetFlavours.append(genjet_hadronFlavour[i])

    if all(zJetFlavours==5):   isZbb = 1
    elif all(zJetFlavours==4): isZcc = 1

    for i in zJetFlavours:
        if zJetFlavours[i]==5:
            #isZbb[i] = 1
            nZbb    += 1
        if zJetFlavours[i]==4:
            #isZcc[i] = 1
            nZcc    += 1
    
    isZbb = nZbb/len(event.Weight_GEN)
    isZcc = nZcc/len(event.Weight_GEN)
    
    return event

    
