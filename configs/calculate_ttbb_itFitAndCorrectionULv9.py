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



corr = {}
simple = {}
for year in ["2017", "2018", "2016postVFP", "2016preVFP"]:
    yearS = year[2:]
    sfDir = os.path.join(karimpath, "data", "UL_"+yearS)

    # electron trigger
    corrFile = _core.CorrectionSet.from_file(
        os.path.join(sfDir, "btagCorrection_ttbb_deepJet.json"))
    corr[year] = corrFile["shape_correction"]
    simple[year] = corrFile["simple_shape_correction"]


itFit = {}
#for year in ["2017", "2018", "2016postVFP", "2016preVFP"]:
#    btagSFjson = _core.CorrectionSet.from_file(
#        os.path.join(jsonDir, "BTV", year+"_UL", "btagging.json.gz"))
#    itFit[year] = btagSFjson["deepJet_shape"]
sfp = "/nfs/dust/cms/user/vdlinden/btv/SFs/btv-json-sf/data"
for year in ["2016postVFP", "2016preVFP", "2017", "2018"]:
    btagSFjson = _core.CorrectionSet.from_file(
        os.path.join(sfp, "UL"+year, "btagging.json"))
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

    wrapper.SetFloatVar("btagCorr"+suffix)
    wrapper.SetFloatVar("btagCorrSimple"+suffix)

def get_proc(event, sample):
    if sample.startswith("TTbb"):
        return "ttbb"
    elif sample.startswith("ST"):
        return "singlet"
    elif sample.startswith("DY") or sample.startswith("WJet"):
        return "vjets"
    elif sample.startswith("ttH") or sample.startswith("TTZ") or sample.startswith("TTW"):
        return "ttX"
    elif sample.startswith("TTTo"):
        if event.is_25ttbb64 or event.is_25ttbj64:
            return "ttbb_5FS"
        elif event.is_25ttcc64:
            return "ttcc"
        else:
            return "ttjj"
    else:
        return "MC"

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    if jec == "nominal":
        btvJECname = "central"
    elif "jer" in jec or "HEM" in jec:
        btvJECname = "central"
    elif "jesFlavorPure" in jec:
        if jec.endswith("down"):
            btvJECname = "down_jesFlavorQCD"
        if jec.endswith("up"):
            btvJECname = "up_jesFlavorQCD"
    else:
        if jec.endswith("down"):
            btvJECname = "down_"+jec.replace("down","")
        elif jec.endswith("up"):
            btvJECname = "up_"+jec.replace("up","")
        else:
            print("invalid jec name {}".format(jec))
            exit()
    if btvJECname.endswith("jesTotal"):
        btvJECname = btvJECname.replace("Total","")

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
        if (flav!=4):
            nom = itFit[dataEra].evaluate(btvJECname, flav,
                abs(getattr(event, "Jets_eta"+suffix)[idx]),
                getattr(event, "Jets_pt"+suffix)[idx],
                getattr(event, "Jets_btagDeepFlavB"+suffix)[idx])
        else:
            nom = 1.
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

    proc = get_proc(event, sample)
    nJet = getattr(event, "nJets"+suffix)
    ht = getattr(event, "HT_jets"+suffix)
    c = corr[dataEra].evaluate(proc, max(min(nJet, 8), 4), float(event.nPV), ht)
    wrapper.branchArrays["btagCorr"+suffix][0] = c
    s = simple[dataEra].evaluate(proc, float(nJet), ht)
    wrapper.branchArrays["btagCorrSimple"+suffix][0] = s


    return event

