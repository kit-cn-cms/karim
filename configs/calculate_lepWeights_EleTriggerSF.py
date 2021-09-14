import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
year = "18"
# year = "17"
sfDir = os.path.join(karimpath, "data", "UL_"+year)

from correctionlib import _core

muYear = {
    "2016preVFP":   "2016_UL_HIPM",
    "2016postVFP":  "2016_UL",
    "2017":         "2017_UL",
    "2018":         "2018_UL",
    }

muTrigName = {
    "2016preVFP":   "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt",
    "2016postVFP":  "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt",
    "2017":         "NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt",
    "2018":         "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight_abseta_pt",
    }

data = {}
puSF = {}
for year in ["2018", "2017", "2016preVFP", "2016postVFP"]:
    # short year
    yearS = year[2:]

    # dict
    data[year] = {}

    # sf directory
    sfDir = os.path.join(karimpath, "data", "UL_"+yearS)
    sfDirT = os.path.join(karimpath, "data", "UL_18")

    # electron ID/RECO/ISO
    ele_evaluator = _core.CorrectionSet.from_file(os.path.join(sfDir, "electron.json"))
    data[year]["electron"] = ele_evaluator["UL-Electron-ID-SF"]

    # electron trigger
    eleTrigFile = _core.CorrectionSet.from_file(os.path.join(sfDirT, "EleTriggerSF_v0.json"))
    data[year]["eleTrig"] = eleTrigFile["EleTriggerSF"]


    # muon trigger
    muTrigFile = "Efficiencies_muon_generalTracks_Z_Run{}_SingleMuonTriggers.csv".format(muYear[year])
    data[year]["muTrig"] = weightModules.LeptonSFs(
        csv     = os.path.join(sfDir, muTrigFile),
        sfName  = muTrigName[year])

    # muon ID scale factors
    muIDFile = "Efficiencies_muon_generalTracks_Z_Run{}_ID.csv".format(muYear[year])
    data[year]["muID"] = weightModules.LeptonSFs(
        csv     = os.path.join(sfDir, muIDFile),
        sfName  = "NUM_TightID_DEN_TrackerMuons_abseta_pt")

    # muon Iso scale factors
    muISOFile = "Efficiencies_muon_generalTracks_Z_Run{}_ISO.csv".format(muYear[year])
    data[year]["muISO"] = weightModules.LeptonSFs(
        csv     = os.path.join(sfDir, muISOFile),
        sfName  = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt")

    # initialize pileup SFs
    pu_evaluator = _core.CorrectionSet.from_file(os.path.join(sfDir, "pileup.json"))
    puSF[year] = pu_evaluator["pileup"]


#TODO Rochester is missing
#Download the correct JSON files 
print(os.path.join(sfDir, "electron.json"))
ele_evaluator = _core.CorrectionSet.from_file(os.path.join(sfDir, "electron.json"))

pu_evaluator = _core.CorrectionSet.from_file(os.path.join(sfDir, "pileup.json"))
puSFs = pu_evaluator["pileup"]
# pileupSFs = weightModules.PileupSFs(os.path.join(sfDir, "pileup.csv"))


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
    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("lumi")   

    # electron scale factors
    wrapper.SetFloatVar("eleIDSF_tight")
    wrapper.SetFloatVar("eleIDSF_tight_up")
    wrapper.SetFloatVar("eleIDSF_tight_down")


    wrapper.SetFloatVar("eleRecoSF_tight")
    wrapper.SetFloatVar("eleRecoSF_tight_up")
    wrapper.SetFloatVar("eleRecoSF_tight_down")


    # muon scale factors
    wrapper.SetFloatVar("muIDSF_tight")
    wrapper.SetFloatVar("muIDSF_tight_up")
    wrapper.SetFloatVar("muIDSF_tight_down")


    wrapper.SetFloatVar("muIsoSF_tight")
    wrapper.SetFloatVar("muIsoSF_tight_up")
    wrapper.SetFloatVar("muIsoSF_tight_down")

    # muon trigger scale factors
    wrapper.SetFloatVar("muTrigSF")
    wrapper.SetFloatVar("muTrigSF_up")
    wrapper.SetFloatVar("muTrigSF_down")

    # PU
    # wrapper.SetFloatVar("Weight_PU")
    # wrapper.SetFloatVar("Weight_PU_down")
    # wrapper.SetFloatVar("Weight_PU_up")

    wrapper.SetFloatVar("pileup") #TODO
    wrapper.SetFloatVar("pileup_up_rel")
    wrapper.SetFloatVar("pileup_down_rel")
    
    # cross section weight
    wrapper.SetFloatVar("xsNorm")
 


# def calculate_variables(event, wrapper, sample, jec = None, genWeights = None):
def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    
    # electron scale factors
    # tight electrons
    elIDSF_tight = 1.
    elIDSF_tight_up = 1.
    elIDSF_tight_down = 1.

    elRecoSF_tight = 1.
    elRecoSF_tight_up = 1.
    elRecoSF_tight_down = 1.

    for iEl in range(getattr(event, "nEle")):
        # TODO super cluster eta
        if getattr(event, "Ele_Pt")[iEl] < 500:
            pt = getattr(event, "Ele_Pt")[iEl]
        else:
            pt = 499.
        # idsf = ele_evaluator["UL-Electron-ID-SF"].evaluate("2018","sf","Tight", getattr(event, "Ele_Eta")[iEl], pt)
        # idsfErr = ele_evaluator["UL-Electron-ID-SF"].evaluate("2018","syst","Tight", getattr(event, "Ele_Eta")[iEl], pt)

        # recosf    = ele_evaluator["UL-Electron-ID-SF"].evaluate("2018","sf","RecoAbove20", getattr(event, "Ele_Eta")[iEl], pt)
        # recosfErr    = ele_evaluator["UL-Electron-ID-SF"].evaluate("2018","syst","RecoAbove20", getattr(event, "Ele_Eta")[iEl], pt)

        idsf      = data[dataEra]["electron"].evaluate(dataEra,"sf","Tight", 
                    event.Ele_EtaSC[iEl], pt)
        idsfErr   = data[dataEra]["electron"].evaluate(dataEra,"syst","Tight", 
                    event.Ele_EtaSC[iEl], pt)
        recosf    = data[dataEra]["electron"].evaluate(dataEra,"sf","RecoAbove20", 
                    event.Ele_EtaSC[iEl], pt)
        recosfErr = data[dataEra]["electron"].evaluate(dataEra,"syst","RecoAbove20", 
                    event.Ele_EtaSC[iEl], pt)

        elIDSF_tight        *= idsf
        elIDSF_tight_up     *= (idsf + idsfErr)
        elIDSF_tight_down   *= (idsf - idsfErr)

        elRecoSF_tight      *= recosf
        elRecoSF_tight_up   *= (recosf + recosfErr)
        elRecoSF_tight_down *= (recosf - recosfErr)

    wrapper.branchArrays["eleIDSF_tight"][0]   = elIDSF_tight
    wrapper.branchArrays["eleIDSF_tight_up"][0]   = elIDSF_tight_up
    wrapper.branchArrays["eleIDSF_tight_down"][0]   = elIDSF_tight_down

    wrapper.branchArrays["eleRecoSF_tight"][0]   = elRecoSF_tight
    wrapper.branchArrays["eleRecoSF_tight_up"][0]   = elRecoSF_tight_up
    wrapper.branchArrays["eleRecoSF_tight_down"][0]   = elRecoSF_tight_down
            
    # tight muons
    muIDSF_tight = 1.
    muIDSF_tight_up = 1.
    muIDSF_tight_down = 1.

    muIsoSF_tight = 1.
    muIsoSF_tight_up = 1.
    muIsoSF_tight_down = 1.

    muTrigSF = 1.
    muTrigSF_up = 1.
    muTrigSF_down = 1.

    for iMu in range(getattr(event, "nMu")):
        # idsf    = muIDSFs_tight.getSFs(  getattr(event, "Mu_Pt")[iMu], abs(getattr(event, "Mu_Eta")[iMu]))
        # isosf   = muIsoSFs_tight.getSFs( getattr(event, "Mu_Pt")[iMu], abs(getattr(event, "Mu_Eta")[iMu]))
        # trigger = muTrigSFs.getSFs(getattr(event, "Mu_Pt")[iMu], abs(getattr(event, "Mu_Eta")[iMu]))
        trigger = data[dataEra]["muTrig"].getSFs(event.Mu_Pt[iMu], abs(event.Mu_Eta[iMu]))
        idsf    = data[dataEra]["muID"].getSFs(  event.Mu_Pt[iMu], abs(event.Mu_Eta[iMu]))
        isosf   = data[dataEra]["muISO"].getSFs( event.Mu_Pt[iMu], abs(event.Mu_Eta[iMu]))

        muIDSF_tight        *= idsf.loc["central"]
        muIDSF_tight_up     *= idsf.loc["up"]
        muIDSF_tight_down   *= idsf.loc["down"]

        muIsoSF_tight       *= isosf.loc["central"]
        muIsoSF_tight_up    *= isosf.loc["up"]
        muIsoSF_tight_down  *= isosf.loc["down"]

        muTrigSF      *= trigger.loc["central"]
        muTrigSF_up   *= trigger.loc["up"]
        muTrigSF_down *= trigger.loc["down"]
        # muTrigSF      *= trigger
        # muTrigSF_up   *= (trigger + triggerErr)
        # muTrigSF_down *= (trigger - triggerErr)

    wrapper.branchArrays["muIDSF_tight"][0]   = muIDSF_tight
    wrapper.branchArrays["muIDSF_tight_up"][0]   = muIDSF_tight_up
    wrapper.branchArrays["muIDSF_tight_down"][0]   = muIDSF_tight_down
    wrapper.branchArrays["muIsoSF_tight"][0]  = muIsoSF_tight
    wrapper.branchArrays["muIsoSF_tight_up"][0]  = muIsoSF_tight_up
    wrapper.branchArrays["muIsoSF_tight_down"][0]  = muIsoSF_tight_down

    wrapper.branchArrays["muTrigSF"][0] = muTrigSF
    wrapper.branchArrays["muTrigSF_up"][0]       = muTrigSF_up
    wrapper.branchArrays["muTrigSF_down"][0]     = muTrigSF_down

    # PU
    # print(getattr(event, "N_Pileup_nTrueInt"))
    # puSF = pileupSFs.getSF(getattr(event, "N_Pileup_nTrueInt"), "central")
    # wrapper.branchArrays["Weight_PU"+suffix][0] = puSF
    # wrapper.branchArrays["Weight_PU_Up"+suffix][0] = pileupSFs.getSF(getattr(event, "nTruePU"+suffix), "up")
    # wrapper.branchArrays["Weight_PU_Down"+suffix][0] = pileupSFs.getSF(getattr(event, "nTruePU"+suffix), "down")

    pu = puSF[year].evaluate("central", float(event.nTruePU))
    wrapper.branchArrays["pileup"][0] = pu
    wrapper.branchArrays["pileup_up_rel"][0] = puSF[dataEra].evaluate("up", float(event.nTruePU))/pu
    wrapper.branchArrays["pileup_down_rel"][0] = puSF[dataEra].evaluate("down", float(event.nTruePU))/pu

    # puSF = puSFs.evaluate("central", float(event.nTruePU))
    # wrapper.branchArrays["pileup"][0] = puSF
    # wrapper.branchArrays["pileup_up_rel"][0] = puSFs.evaluate("up", float(event.nTruePU))/puSF
    # wrapper.branchArrays["pileup_down_rel"][0] = puSFs.evaluate("down", float(event.nTruePU))/puSF

    # puSF = pileupSFs.getSF(getattr(event, "nTruePU"), "central") #TODO
    # wrapper.branchArrays["pileup"][0] = puSF #TODO 

    # cross section norm
    wrapper.branchArrays["xsNorm"][0] = genWeights.getXS("incl")

    return event

