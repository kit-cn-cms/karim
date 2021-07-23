import numpy as np
import common
import weightModules
from array import array
import os
import sys
from correctionlib import _core

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
year = "18"
yearL = "2018"
sfDir = os.path.join(karimpath, "data", "UL_"+year)
sfDirLeg = os.path.join(karimpath, "data", "legacy_"+yearL)

btagSFjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btaggingSF_deepJet_iterativeFit.json"))
itFit = btagSFjson["iterativeFit"]

# initialize iterative fit b-tagging sfs
uncs = [
    "hfstats2",
    "hfstats1",
    "lfstats2",
    "lfstats1",
    "cferr2",
    "cferr1",
    "hf",
    "lf"
    ]
btagSF_uncs = ["up_"+u   for u in uncs] + \
              ["down_"+u for u in uncs]
# translate the BTV jes name to the official Jet name
btagJECs = {
    "nom": "nom",
    "jesTotalUp": "up_jes",
    "jesTotalDown": "down_jes",
    "jerUp": "central",   # no SFs for jer
    "jerDown": "central", # no SFs for jer
    None: "nom"
    }
jecs = [
    "jes",
    "jesAbsolute_2018",
    "jesHF_2018",
    "jesEC2_2018",
    "jesRelativeBal",
    "jesHEMIssue",
    "jesBBEC1_2018",
    "jesRelativeSample_2018",
    "jesFlavorQCD",
    "jesBBEC1",
    "jesHF",
    "jesAbsolute",
    "jesEC2",
    ]

for j in jecs:
    if (j == "jer" or j == "jes"):
        continue
    btagJECs[j+"Up"]   = "up_"+j
    btagJECs[j+"Down"] = "down_"+j
        

# initialize b-tagging SF correction
# TODO
#sfPatch = weightModules.SFPatches(os.path.join(sfDirLeg, "btaggingSF_patches_"+yearL+".csv"))

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
    #wrapper.SetIntVar("event"+suffix)   
    #wrapper.SetIntVar("run"+suffix)   
    #wrapper.SetIntVar("lumi"+suffix)   

    #wrapper.SetIntVar("nJets"+suffix)

    # b tagging
    #wrapper.SetFloatVarArray("Jet_btagSF"+suffix, "nJets"+suffix)
    wrapper.SetFloatVar("btagSF"+suffix)
    
    if jec == "nom":
        # iterative fit uncertainties
        for unc in btagSF_uncs:
            wrapper.SetFloatVar("btagSF_{}_rel".format(unc)+suffix)

    # b tagging patch
    # TODO
    #wrapper.SetFloatVar("btagSFPatch"+suffix)


def calculate_variables(event, wrapper, sample, jec, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    # TODO adjust when merged JEC uncertainties are avialable
    if jec == "nom":
        btvJECname = "central"
    else:
        btvJECname = "central"
    #btvJECname = btagJECs[jec]

    # add basic information for friend trees
    #wrapper.branchArrays["event"+suffix][0] = getattr(event, "event"+suffix)
    #wrapper.branchArrays["run"+suffix][0]   = getattr(event, "run"+suffix)
    #wrapper.branchArrays["lumi"+suffix][0]  = getattr(event, "lumi"+suffix)
    
    #wrapper.branchArrays["nJets"+suffix][0] = getattr(event, "nJets"+suffix)

    # b-tagging scale factor patches
    # TODO
    #try:
    #    ttbarID = getattr(event, "ttbarID")
    #except:
    #    ttbarID = 0
    #patchValue = sfPatch.getPatchValue(sample, 
    #    ttbarID, 
    #    getattr(event, "nJets"+suffix), 
    #    getattr(event, "HT_jets"+suffix))

    #wrapper.branchArrays["btagSFPatch"+suffix][0] = patchValue

    sf = 1.
    sf_uncs = {}
    for u in btagSF_uncs:
        sf_uncs[u] = 1.

    for idx in range(getattr(event, "nJets"+suffix)):
        flav = getattr(event, "Jet_Flav"+suffix)[idx]
        
        if not (flav == 4):
            nom = itFit.evaluate(btvJECname, flav, 
                abs(getattr(event, "Jet_Eta"+suffix)[idx]),
                getattr(event, "Jet_Pt"+suffix)[idx],
                getattr(event, "Jet_btagValue"+suffix)[idx])
            sf *= nom
        else:
            nom = 1.

        if jec == "nom":
            # scale factor uncertainties
            for u in btagSF_uncs:
                # cferr only exists for c-jets
                if (flav == 4):
                    if "cferr" in u:
                        sf_uncs[u] *= itFit.evaluate(u, 4,
                            abs(getattr(event, "Jet_Eta"+suffix)[idx]),
                            getattr(event, "Jet_Pt"+suffix)[idx],
                            getattr(event, "Jet_btagValue"+suffix)[idx])
                else:
                    if "cferr" in u:
                        sf_uncs[u] *= nom
                    else:
                        sf_uncs[u] *= itFit.evaluate(u, flav,
                            abs(getattr(event, "Jet_Eta"+suffix)[idx]),
                            getattr(event, "Jet_Pt"+suffix)[idx],
                            getattr(event, "Jet_btagValue"+suffix)[idx])
                            
    wrapper.branchArrays["btagSF"+suffix][0] = sf
    if jec == "nom":
        for u in btagSF_uncs:
            wrapper.branchArrays["btagSF_{}_rel".format(u)+suffix][0] = sf_uncs[u]/sf

    return event

