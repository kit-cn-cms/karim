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
    wrapper.SetFloatVarArray("genJet_jetMatcherClass","nGenJets")
    wrapper.SetFloatVarArray("genJet_hadronFlavour","nGenJets")
    wrapper.SetIntVar("nGenJets")
    wrapper.SetIntVar("nGenBJets")
    wrapper.SetIntVar("nGenCJets")

    wrapper.SetIntVar("allisZbb")
    wrapper.SetIntVar("allisZcc")
    wrapper.SetFloatVar("isZbb")
    wrapper.SetFloatVar("isZcc")
    wrapper.SetFloatVar("nZbb")
    wrapper.SetFloatVar("nZcc")

    wrapper.SetIntVar("allisHbb")
    wrapper.SetIntVar("allisHcc")
    wrapper.SetFloatVar("isHbb")
    wrapper.SetFloatVar("isHcc")
    wrapper.SetFloatVar("nHbb")
    wrapper.SetFloatVar("nHcc")
    #wrapper.SetFloatVarArray("zJetFlavours","genJet_hadronFlavour")
   

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):

    wrapper.branchArrays["event"][0] = getattr(event, "event")
    
    zJetFlavours =[]
    allisZbb = 0
    allisZcc = 0
    nZbb  = 0
    nZcc  = 0

    hJetFlavours =[]
    allisHbb = 0
    allisHcc = 0
    nHbb  = 0
    nHcc  = 0
    for i in range(event.nGenJets):
        if event.genJet_jetMatcherClass[i] == 5:   zJetFlavours.append(event.genJet_hadronFlavour[i])
        elif event.genJet_jetMatcherClass[i] == 4: hJetFlavours.append(event.genJet_hadronFlavour[i])


    #2 jets coming from the Z, so in the best case, the events have nZbb = 2 when isZbb = 1
    #zJetFlavours_combn = [i for i in combinations(zJetFlavours,2)]
    if len(zJetFlavours)>0:
        if all([f==5 for f in zJetFlavours]):   
            allisZbb = 1
        elif all([f==4 for f in zJetFlavours]): 
            allisZcc = 1
        else:
            allisZbb = 0
            allisZcc = 0
    ##ttH decay fractions
    elif len(hJetFlavours)>0:
        if all([f==5 for f in hJetFlavours]):   
            allisHbb = 1
        elif all([f==4 for f in hJetFlavours]): 
            allisHcc = 1
        else:
            allisHbb = 0
            allisHcc = 0
    

    #for i in range(0,len(zJetFlavours_combn)):
    #    if zJetFlavours_combn[i]==(5,5):
    #        #isZbb[i] = 1
    #        nbfromZ    += 1
    #    elif zJetFlavours_combn[i]==(4,4):
    #        #isZcc[i] = 1
    #        ncfromZ    += 1
    #    
    
    for i in range(0,len(zJetFlavours)):
        if zJetFlavours[i]==5:
             nZbb += 1
        elif zJetFlavours[i]==4:
             nZcc += 1
    
    #to account for b/cs out of the acceptance of the detector
    #if in an event, Z->b (one b is missed) if Z->0bs, then another type of decay, if Z->bb, then correctly identified.
    if (nZbb % 2) ==0: isZbb = nZbb
    else:              isZbb = nZbb+1
    if (nZcc % 2)==0:  isZcc = nZcc
    else:              isZcc= (nZcc)+1
    

    for i in range(0,len(hJetFlavours)):
        if hJetFlavours[i]==5:
             nHbb += 1
        elif hJetFlavours[i]==4:
             nHcc += 1
    
    if (nHbb % 2) ==0: isHbb = nHbb
    else:              isHbb = (nHbb)+1
    if (nHcc % 2)==0:  isHcc = nHcc/2
    else:              isHcc= (nHcc)+1
    
  
    wrapper.branchArrays["allisZbb"][0] = allisZbb
    wrapper.branchArrays["allisZcc"][0] = allisZcc
    wrapper.branchArrays["isZbb"][0]    = isZbb
    wrapper.branchArrays["isZcc"][0]    = isZcc
    wrapper.branchArrays["nZbb"][0]     = nZbb
    wrapper.branchArrays["nZcc"][0]     = nZcc

    wrapper.branchArrays["allisHbb"][0] = allisHbb
    wrapper.branchArrays["allisHcc"][0] = allisHcc
    wrapper.branchArrays["isHbb"][0]    = isHbb
    wrapper.branchArrays["isHcc"][0]    = isHcc
    wrapper.branchArrays["nHbb"][0]     = nHbb
    wrapper.branchArrays["nHcc"][0]     = nHcc

    print(nHbb)
    return event
    
    
