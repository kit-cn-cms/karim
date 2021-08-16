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

btagSFjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btaggingSF_deepJet.json"))
btagSF = btagSFjson["comb"]
mistagSF = btagSFjson["incl"]

btagEffjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btagEff_ttbb_deepJet.json"))
btagEff = btagEffjson["btagEff"]

styles = ["M", "TM", "ML", "TML"]
#styles = ["M"]
workingPoints = list(set([wp for style in styles for wp in style]))

taggingUncertainties = ["up", "down"]
mistagUncertainties = ["up", "down"]
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

    # b tagging
    for style in styles:
        wrapper.SetFloatVar("btagSF_"+style+suffix)
        if jec == "nom":
            for tagUnc in taggingUncertainties:
                wrapper.SetFloatVar("btagSF_"+style+"_tag_"+tagUnc+"_rel"+suffix)
            for mistagUnc in mistagUncertainties:
                wrapper.SetFloatVar("btagSF_"+style+"_mistag_"+mistagUnc+"_rel"+suffix)


def calculate_variables(event, wrapper, sample, jec, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec

    sf = {}
    if jec == "nom":
        sf_tagunc = {}
        for tagUnc in taggingUncertainties:
            sf_tagunc[tagUnc] = {}
        sf_mistagunc = {}
        for mistagUnc in mistagUncertainties:
            sf_mistagunc[mistagUnc] = {}
    for style in styles:
        sf[style] = [1., 1.]
        if jec == "nom":
            for tagUnc in taggingUncertainties:
                sf_tagunc[tagUnc][style] = 1.
            for mistagUnc in mistagUncertainties:
                sf_mistagunc[mistagUnc][style] = 1.

    for idx in range(getattr(event, "nJets"+suffix)):
        eta = abs(getattr(event, "Jet_Eta"+suffix)[idx])
        pt  = getattr(event, "Jet_Pt"+suffix)[idx]
        passes = {}
        for wp in workingPoints:
            passes[wp] = getattr(event, "Jet_tagged"+wp+suffix)[idx]
        flav  = getattr(event, "Jet_Flav"+suffix)[idx]

        jetsfs = {}
        effs = {}
        jetuncs = {}
        if flav == 0:
            if jec == "nom":
                for mistagUnc in mistagUncertainties:
                    jetuncs[mistagUnc] = {}

            for wp in workingPoints:
                effs[wp] = btagEff.evaluate(wp, flav, eta, pt)
                jetsfs[wp]  = mistagSF.evaluate(wp, "central", flav, eta, pt)
                if jec == "nom":
                    for unc in jetuncs:
                        jetuncs[unc][wp] = mistagSF.evaluate(wp, unc, flav, eta, pt)
        else:
            if jec == "nom":
                for tagUnc in taggingUncertainties:
                    jetuncs[tagUnc] = {}

            for wp in workingPoints:
                effs[wp] = btagEff.evaluate(wp, flav, eta, pt)
                jetsfs[wp]  = btagSF.evaluate(wp, "central", flav, eta, pt)
                if jec == "nom":
                    for unc in jetuncs:
                        jetuncs[unc][wp] = btagSF.evaluate(wp, unc, flav, eta, pt)

        for s in styles:
            if passes[s[0]]:
                sf[s][0] *= effs[s[0]]*jetsfs[s[0]]
                sf[s][1] *= effs[s[0]]
                if jec == "nom":
                    for unc in jetuncs:
                        if flav == 0:
                            sf_mistagunc[unc][s]*= effs[s[0]]*jetuncs[unc][s[0]]
                            sf_tagunc[unc][s]*= effs[s[0]]*jetsfs[s[0]]
                        else:
                            sf_tagunc[unc][s]*= effs[s[0]]*jetuncs[unc][s[0]]
                            sf_mistagunc[unc][s]*= effs[s[0]]*jetsfs[s[0]]
            elif not passes[s[-1]]:
                sf[s][0] *= (1.-effs[s[-1]]*jetsfs[s[-1]])
                sf[s][1] *= (1.-effs[s[-1]])
                if jec == "nom":
                    for unc in jetuncs:
                        if flav == 0:
                            sf_mistagunc[unc][s]*= (1.-effs[s[-1]]*jetuncs[unc][s[-1]])
                            sf_tagunc[unc][s]*= (1.-effs[s[-1]]*jetsfs[s[-1]])
                        else:
                            sf_tagunc[unc][s]*= (1.-effs[s[-1]]*jetuncs[unc][s[-1]])
                            sf_mistagunc[unc][s]*= (1.-effs[s[-1]]*jetsfs[s[-1]])
            elif passes[s[1]]:
                sf[s][0] *= (effs[s[1]]*jetsfs[s[1]] - effs[s[0]]*jetsfs[s[0]])
                sf[s][1] *= (effs[s[1]] - effs[s[0]])
                if jec == "nom":
                    for unc in jetuncs:
                        if flav == 0:
                            sf_mistagunc[unc][s]*= (effs[s[1]]*jetuncs[unc][s[1]] - effs[s[0]]*jetuncs[unc][s[0]])
                            sf_tagunc[unc][s]*= (effs[s[1]]*jetsfs[s[1]] - effs[s[0]]*jetsfs[s[0]])
                        else:
                            sf_tagunc[unc][s]*= (effs[s[1]]*jetuncs[unc][s[1]] - effs[s[0]]*jetuncs[unc][s[0]])
                            sf_mistagunc[unc][s]*= (effs[s[1]]*jetsfs[s[1]] - effs[s[0]]*jetsfs[s[0]])
            elif passes[s[2]]:
                sf[s][0] *= (effs[s[2]]*jetsfs[s[2]] - effs[s[1]]*jetsfs[s[1]])
                sf[s][1] *= (effs[s[2]] - effs[s[1]])
                if jec == "nom":
                    for unc in jetuncs:
                        if flav == 0:
                            sf_mistagunc[unc][s]*= (effs[s[2]]*jetuncs[unc][s[2]] - effs[s[1]]*jetuncs[unc][s[1]])
                            sf_tagunc[unc][s]*= (effs[s[2]]*jetsfs[s[2]] - effs[s[1]]*jetsfs[s[1]])
                        else:
                            sf_tagunc[unc][s]*= (effs[s[2]]*jetuncs[unc][s[2]] - effs[s[1]]*jetuncs[unc][s[1]])
                            sf_mistagunc[unc][s]*= (effs[s[2]]*jetsfs[s[2]] - effs[s[1]]*jetsfs[s[1]])
            else:
                print("ERROR")
                exit()

    
    for style in styles:
        wrapper.branchArrays["btagSF_"+style+suffix][0] = sf[style][0]/sf[style][1]
        if jec == "nom":
            for tagUnc in taggingUncertainties:
                wrapper.branchArrays["btagSF_"+style+"_tag_"+tagUnc+"_rel"+suffix][0] = sf_tagunc[tagUnc][style] / sf[style][0]
            for mistagUnc in mistagUncertainties:
                wrapper.branchArrays["btagSF_"+style+"_mistag_"+mistagUnc+"_rel"+suffix][0] = sf_mistagunc[mistagUnc][style] / sf[style][0]

    return event

