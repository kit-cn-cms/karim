import numpy as np
import common
import weightModules
from array import array
import os
import sys
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
year = "2018"
sfDir = os.path.join(karimpath, "data", "legacy_"+year)

# initialize iterative fit b-tagging sfs
btaggingSFs = weightModules.BTaggingScaleFactors(os.path.join(sfDir, "btaggingSF_deepJet_"+year+".csv"))
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
btagSF_uncs = ["up_"+u   for u in uncs] + \
              ["down_"+u for u in uncs]
btagSF_jec  = ["up_"+u   for u in jecs] + \
              ["down_"+u for u in jecs] + \
              ["central"]
btaggingSFs.removeUnusedSys(
    keep = ["central"] + btagSF_uncs,
    jec  = btagSF_jec)

# translate the BTV jes name to the official Jet name
btagJECs = {
    "nom": "nom",
    "jesTotalUp": "up_jes",
    "jesTotalDown": "down_jes",
    "jerUp": "central",   # no SFs for jer
    "jerDown": "central", # no SFs for jer
    }
for j in jecs:
    if (j == "jer" or j == "jes"):
        continue
    btagJECs[j+"Up"]   = "up_"+j
    btagJECs[j+"Down"] = "down_"+j
        

# translate jetFlavor into btv flavor definition
flavTranslator = {
    5: 0, # b jets
    4: 1, # c jets
    3: 2, # lf jets
    2: 2, # lf jets
    1: 2, # lf jets
    0: 2, # lf jets
    }

# initialize b-tagging SF correction
sfPatch = weightModules.SFPatches(os.path.join(sfDir, "btaggingSF_patches_"+year+".csv"))

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
    wrapper.SetFloatVar("btagSFPatch"+suffix)


def calculate_variables(event, wrapper, sample, jec, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    btvJECname = btagJECs[jec]

    #if getattr(event, "isRecoSelected"+suffix) < 1. and getattr(event,  "isGenSelected"+suffix) < 1.: 
    #    return event

    # add basic information for friend trees
    #wrapper.branchArrays["event"+suffix][0] = getattr(event, "event"+suffix)
    #wrapper.branchArrays["run"+suffix][0]   = getattr(event, "run"+suffix)
    #wrapper.branchArrays["lumi"+suffix][0]  = getattr(event, "lumi"+suffix)
    
    #wrapper.branchArrays["nJets"+suffix][0] = getattr(event, "nJets"+suffix)

    # b-tagging scale factor patches
    patchValue = sfPatch.getPatchValue(sample, 
        getattr(event, "ttbarID"), 
        getattr(event, "nJets"+suffix), 
        getattr(event, "HT_jets"+suffix))

    wrapper.branchArrays["btagSFPatch"+suffix][0] = patchValue

    # iterative b-tagging scale factors
    btagSF = 1.
    uncs = {}
    for u in btagSF_uncs:
        uncs[u] = 1.

    for idx in range(getattr(event, "nJets"+suffix)):
        # determine jet flavor
        flav = flavTranslator[getattr(event, "Jet_Flav"+suffix)[idx]]

        # load scale factors for eta, pt, btagValue bin
        sfs = btaggingSFs.getSFs(flav, 
            abs(getattr(event, "Jet_Eta"+suffix)[idx]), 
            getattr(event, "Jet_Pt"+suffix)[idx], 
            getattr(event, "Jet_btagValue"+suffix)[idx],
            btvJECname)

        # nominal scale factor
        if btvJECname == "nom":
            btagSF*= sfs.loc["central"]
        else:
            btagSF*= sfs.loc[btvJECname]
        # scale factor per jet
        #wrapper.branchArrays["Jet_btagSF"+suffix][idx] = sfs.loc[btagJEC]


        if jec == "nom":
            # scale factor uncertainties
            for u in btagSF_uncs:
                # cferr only exists for c-jets
                if flav == 1: 
                    if "cferr" in u:
                        uncs[u] *= sfs.loc[u]
                    else:
                        uncs[u] *= sfs.loc["central"]
                # for the others cferr does not exist
                else:
                    if "cferr" in u:
                        uncs[u] *= sfs.loc["central"]
                    else:
                        uncs[u] *= sfs.loc[u]


    wrapper.branchArrays["btagSF"+suffix][0] = btagSF
    if jec == "nom":
        for u in btagSF_uncs:
            wrapper.branchArrays["btagSF_{}_rel".format(u)+suffix][0] = uncs[u]/btagSF

    return event

