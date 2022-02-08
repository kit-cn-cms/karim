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
        "genJet_jetMatcherClass",
        "genJet_hadronFlavour",
        "nGenJets",
        "nGenBJets",
        "nGenCJets"
        ]
    return variables

def base_selection(event):
    return True

def set_branches(wrapper):
    wrapper.SetIntVar("genJet_jetMatcherClass")
    wrapper.SetIntVar("genJet_hadronFlavour")
    wrapper.SetIntVar("nGenJets")
    wrapper.SetIntVar("nGenBJets")
    wrapper.SetIntVar("nGenCJets")

    wrapper.SetIntVar("isZbb")
    wrapper.SetIntVar("isZcc")
   # wrapper.SetIntVar("isZbb","nGenBJets")
   # wrapper.SetIntVar("isZcc","nGenCJets")


def calculate_variables():
    zJetFlavours = []
    for i in nGenJets:
        if genJet_jetMatcherClass[i] == 5: zjetFlavours.append(genjet_hadronFlavour[i])

    if all(zJetFlavours==5):   isZbb = 1
    elif all(zJetFlavours==4): isZcc = 1

    
    return event

    
