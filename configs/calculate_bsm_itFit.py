import numpy as np
import common
import weightModules
from array import array
import os
import sys
from correctionlib import _core
jsonDir = os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG")

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))


itFit = {}
for year in ["2018"]:
    btagSFjson = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "BTV", year+"_UL", "btagging.json.gz"))
    itFit[year] = btagSFjson["deepJet_shape"]


# itFit
uncs_b = [
    "hfstats2",
    "hfstats1",
    "lfstats2",
    "lfstats1",
    "hf",
    "lf"
    ]
uncs_c = [
    "cferr2",
    "cferr1",
    ]
bSF_uncs = ["up_"+u   for u in uncs_b] + \
          ["down_"+u for u in uncs_b]
cSF_uncs = ["up_"+u   for u in uncs_c] + \
          ["down_"+u for u in uncs_c]

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
    for tec in ["corr", "corrUp", "corrDown"]:
        suffix = "_"+tec+"_"+jec

        wrapper.SetFloatVar("itFitSF"+suffix)
        if jec == "nom":
            for u in bSF_uncs+cSF_uncs:
                wrapper.SetFloatVar("itFitSF_{}_rel".format(u))

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    for tec in ["corr", "corrUp", "corrDown"]:
        suffix = "_"+tec+"_"+jec
        # TODO adjust when merged JEC uncertainties are avialable
        if jec == "nom":
            btvJECname = "central"
        else:
            btvJECname = "central"

        sf = 1.
        sf_uncs = {}
        for u in bSF_uncs+cSF_uncs:
            sf_uncs[u] = 1.

        for idx in range(getattr(event, "N_Jets"+suffix)):
            flav = getattr(event, "Jets_Flav"+suffix)[idx]

            nom = itFit[dataEra].evaluate("central", flav,
                abs(getattr(event, "Jets_Eta"+suffix)[idx]),
                getattr(event, "Jets_Pt"+suffix)[idx],
                getattr(event, "Jets_btagValue"+suffix)[idx])
            sf *= nom

            if jec == "nom":
                # scale factor uncertainties
                if (flav == 4):
                    for u in bSF_uncs:
                        sf_uncs[u] *= nom
                    for u in cSF_uncs:
                        sf_uncs[u] *= itFit[dataEra].evaluate(u, flav,
                            abs(getattr(event, "Jets_Eta"+suffix)[idx]),
                            getattr(event, "Jets_Pt"+suffix)[idx],
                            getattr(event, "Jets_btagValue"+suffix)[idx])
                else:
                    for u in cSF_uncs:
                        sf_uncs[u] *= nom
                    for u in bSF_uncs:
                        sf_uncs[u] *= itFit[dataEra].evaluate(u, flav,
                            abs(getattr(event, "Jets_Eta"+suffix)[idx]),
                            getattr(event, "Jets_Pt"+suffix)[idx],
                            getattr(event, "Jets_btagValue"+suffix)[idx])

        wrapper.branchArrays["itFitSF"+suffix][0] = sf
        if jec == "nom":
            for u in bSF_uncs+cSF_uncs:
                wrapper.branchArrays["itFitSF_{}_rel".format(u)][0] = sf_uncs[u]/sf



    return event
