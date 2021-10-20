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



btagSF = {}
mistagSF = {}
btagEff = {}
for year in ["2017", "2018"]:
    sfDir = os.path.join(karimpath, "data", "UL_"+year[2:])
    
    itFitSFjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btaggingSF_deepJet_iterativeFit.json"))
    itFit = itFitSFjson["iterativeFit"]

# itFit
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

    wrapper.SetFloatVar("itFitSF"+suffix)
    if jec == "nom":
        for u in btagSF_uncs:
            wrapper.SetFloatVar("itFitSF_{}_rel".format(u))

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    # TODO adjust when merged JEC uncertainties are avialable
    if jec == "nom":
        btvJECname = "central"
    else:
        btvJECname = "central"

    sf = 1.
    sf_uncs = {}
    for u in btagSF_uncs:
        sf_uncs[u] = 1.

    for idx in range(getattr(event, "nJets"+suffix)):
        flav = getattr(event, "Jet_Flav"+suffix)[idx]

        if not (flav == 4):
            nom = itFit.evaluate("central", flav,
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

    wrapper.branchArrays["itFitSF"+suffix][0] = sf
    if jec == "nom":
        for u in btagSF_uncs:
            wrapper.branchArrays["itFitSF_{}_rel".format(u)][0] = sf_uncs[u]/sf



    return event

