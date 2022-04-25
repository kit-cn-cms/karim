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
for year in ["2017", "2018", "2016postVFP", "2016preVFP"]:
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
    suffix = "_"+jec

    wrapper.SetFloatVar("btagSF"+suffix)
    if jec == "nominal":
        for u in bSF_uncs+cSF_uncs:
            wrapper.SetFloatVar("btagSF_{}_rel".format(u))

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    # TODO adjust when merged JEC uncertainties are avialable
    if jec == "nominal":
        btvJECname = "central"
    else:
        btvJECname = "central"

    sf = 1.
    sf_uncs = {}
    for u in bSF_uncs+cSF_uncs:
        sf_uncs[u] = 1.

    for idx in range(getattr(event, "nJets"+suffix)):
        try:
            test = getattr(event, "Jets_hadronFlavour"+suffix)[idx]
        except:
            continue

        flav = getattr(event, "Jets_hadronFlavour"+suffix)[idx]
        nom = itFit[dataEra].evaluate("central", flav,
            abs(getattr(event, "Jets_eta"+suffix)[idx]),
            getattr(event, "Jets_pt"+suffix)[idx],
            getattr(event, "Jets_btagDeepFlavB"+suffix)[idx])
        sf *= nom

        if jec == "nominal":
            # scale factor uncertainties
            if (flav == 4):
                for u in bSF_uncs:
                    sf_uncs[u] *= nom
                for u in cSF_uncs:
                    sf_uncs[u] *= itFit[dataEra].evaluate(u, flav,
                        abs(getattr(event, "Jets_eta"+suffix)[idx]),
                        getattr(event, "Jets_pt"+suffix)[idx],
                        getattr(event, "Jets_btagDeepFlavB"+suffix)[idx])
            else:
                for u in cSF_uncs:
                    sf_uncs[u] *= nom
                for u in bSF_uncs:
                    sf_uncs[u] *= itFit[dataEra].evaluate(u, flav,
                        abs(getattr(event, "Jets_eta"+suffix)[idx]),
                        getattr(event, "Jets_pt"+suffix)[idx],
                        getattr(event, "Jets_btagDeepFlavB"+suffix)[idx])

    wrapper.branchArrays["btagSF"+suffix][0] = sf
    if jec == "nominal":
        for u in bSF_uncs+cSF_uncs:
            wrapper.branchArrays["btagSF_{}_rel".format(u)][0] = sf_uncs[u]/sf



    return event

