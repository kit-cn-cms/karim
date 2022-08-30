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
for year in ["2017"]: #, "2018", "2016postVFP", "2016preVFP"]:
    ctagSFjson = _core.CorrectionSet.from_file(
        os.path.join("/nfs/dust/cms/user/vdlinden/btv/SFs/btv-json-sf/data/UL"+year,
        "ctagging.json"))
        #os.path.join(jsonDir, "BTV", year+"_UL", "btagging.json.gz"))
    itFit[year] = ctagSFjson["deepJet_shape"]


uncs = [
    "Extrap",
    "Interp",
    "LHEScaleWeight_muF",
    "LHEScaleWeight_muR",
    "PSWeightFSR",
    "PSWeightISR",
    "PUWeight",
    "Stat",
    "XSec_BRUnc_DYJets_b",
    "XSec_BRUnc_DYJets_c",
    "XSec_BRUnc_WJets_c",
    "jer",
    "jesTotal"
    ]
SF_uncs = ["up_"+u for u in uncs] + \
        ["down_"+u for u in uncs]
#bSF_uncs = ["up_"+u   for u in uncs_b] + \
#          ["down_"+u for u in uncs_b]
#cSF_uncs = ["up_"+u   for u in uncs_c] + \
#          ["down_"+u for u in uncs_c]

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

    wrapper.SetFloatVar("ctagSF"+suffix)
    if jec == "nominal":
        for u in SF_uncs:
            wrapper.SetFloatVar("ctagSF_{}_rel".format(u))

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec

    sf = 1.
    sf_uncs = {}
    for u in SF_uncs:
        sf_uncs[u] = 1.

    for idx in range(getattr(event, "nJets"+suffix)):
        flav = getattr(event, "Jets_hadronFlavour"+suffix)[idx]
        cvl  = getattr(event, "Jets_btagDeepFlavCvL"+suffix)[idx]
        cvb  = getattr(event, "Jets_btagDeepFlavCvB"+suffix)[idx]
        nom = itFit[dataEra].evaluate("central", flav, cvl, cvb)
        sf *= nom

        if jec == "nominal":
            # scale factor uncertainties
            for u in SF_uncs:
                # TODO THIS MIGHT NOT BE CORRECT - CHECK AGAIN WHICH ORDER CvB AND CvL ARE IN
                sf_uncs[u] *= itFit[dataEra].evaluate(u, flav, cvl, cvb)
            '''
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
            '''
    wrapper.branchArrays["ctagSF"+suffix][0] = sf
    if jec == "nominal":
        for u in SF_uncs:
            wrapper.branchArrays["ctagSF_{}_rel".format(u)][0] = sf_uncs[u]/sf



    return event

