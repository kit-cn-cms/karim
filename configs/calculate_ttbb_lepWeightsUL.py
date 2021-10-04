import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
year  = "18"
yearL = "2018"
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
for year in ["2018", "2017", "2016preVFP", "2016postVFP"]:
    # short year
    yearS = year[2:]

    # dict
    data[year] = {}

    # sf directory
    sfDir = os.path.join(karimpath, "data", "UL_"+yearS)

    # TODO update ele trig SFs
    sfDirT = os.path.join(karimpath, "data", "UL_18")
    if year == "2016postVFP":
        sfDirT = os.path.join(karimpath, "data", "UL_"+yearS)

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

def set_branches(wrapper, jec = None):
    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("lumi")   

    # lepton trigger
    wrapper.SetFloatVar("muTrigSF")
    wrapper.SetFloatVar("muTrigSF_up")
    wrapper.SetFloatVar("muTrigSF_up_rel")
    wrapper.SetFloatVar("muTrigSF_down")
    wrapper.SetFloatVar("muTrigSF_down_rel")

    wrapper.SetFloatVar("elTrigSF")
    wrapper.SetFloatVar("elTrigSF_up")
    wrapper.SetFloatVar("elTrigSF_up_rel")
    wrapper.SetFloatVar("elTrigSF_down")
    wrapper.SetFloatVar("elTrigSF_down_rel")

    # lepton scale factor
    wrapper.SetFloatVar("muIDSF")
    wrapper.SetFloatVar("muIDSF_up")
    wrapper.SetFloatVar("muIDSF_down")
    wrapper.SetFloatVar("elIDSF")
    wrapper.SetFloatVar("elIDSF_up")
    wrapper.SetFloatVar("elIDSF_down")

    wrapper.SetFloatVar("muIsoSF")
    wrapper.SetFloatVar("muIsoSF_up")
    wrapper.SetFloatVar("muIsoSF_down")
    wrapper.SetFloatVar("elRecoSF")
    wrapper.SetFloatVar("elRecoSF_up")
    wrapper.SetFloatVar("elRecoSF_down")

    wrapper.SetFloatVar("muSF")
    wrapper.SetFloatVar("muSF_up_rel")
    wrapper.SetFloatVar("muSF_down_rel")

    wrapper.SetFloatVar("elSF")
    wrapper.SetFloatVar("elSF_up_rel")
    wrapper.SetFloatVar("elSF_down_rel")
 

def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    
    # additional relative weights
    #wrapper.branchArrays["L1ECALPrefire"][0]          = getattr(event, "Weight_L1ECALPrefire")
    #wrapper.branchArrays["L1ECALPrefire_up_rel"][0]   = getattr(event, "Weight_L1ECALPrefireUp")/getattr(event, "Weight_L1ECALPrefire")
    #wrapper.branchArrays["L1ECALPrefire_down_rel"][0] = getattr(event, "Weight_L1ECALPrefireDown")/getattr(event, "Weight_L1ECALPrefire")
    
    # electron scale factors
    elTrigSF = 1.
    elTrigSF_up = 1.
    elTrigSF_down = 1.

    elIDSF = 1.
    elIDSF_up = 1.
    elIDSF_down = 1.

    elRecoSF = 1.
    elRecoSF_up = 1.
    elRecoSF_down = 1.

    for iEl in range(getattr(event, "nEle")):
        if event.Ele_Pt[iEl] < 500:
            pt = event.Ele_Pt[iEl]
        else:
            pt = 499.
        # TODO trigger
        idsf      = data[dataEra]["electron"].evaluate(dataEra,"sf","Tight", 
                    event.Ele_EtaSC[iEl], pt)
        idsfErr   = data[dataEra]["electron"].evaluate(dataEra,"syst","Tight", 
                    event.Ele_EtaSC[iEl], pt)
        recosf    = data[dataEra]["electron"].evaluate(dataEra,"sf","RecoAbove20", 
                    event.Ele_EtaSC[iEl], pt)
        recosfErr = data[dataEra]["electron"].evaluate(dataEra,"syst","RecoAbove20", 
                    event.Ele_EtaSC[iEl], pt)

        elTrigSF      *= data[dataEra]["eleTrig"].evaluate("central", pt, event.Ele_EtaSC[iEl])
        elIDSF        *= idsf
        elRecoSF      *= recosf

        elTrigSF_up   *= data[dataEra]["eleTrig"].evaluate("up", 
                            pt, event.Ele_EtaSC[iEl])
        elTrigSF_down *= data[dataEra]["eleTrig"].evaluate("down", 
                            pt, event.Ele_EtaSC[iEl])

        elIDSF_up     *= (idsf + idsfErr)
        elIDSF_down   *= (idsf - idsfErr)

        elRecoSF_up   *= (recosf + recosfErr)
        elRecoSF_down *= (recosf - recosfErr)

    wrapper.branchArrays["elTrigSF"][0] = elTrigSF
    wrapper.branchArrays["elIDSF"][0]   = elIDSF
    wrapper.branchArrays["elRecoSF"][0] = elRecoSF
    wrapper.branchArrays["elSF"][0]     = elIDSF*elRecoSF

    wrapper.branchArrays["elTrigSF_up"][0]   = elTrigSF_up
    wrapper.branchArrays["elTrigSF_down"][0] = elTrigSF_down
        
    wrapper.branchArrays["elIDSF_up"][0]     = elIDSF_up
    wrapper.branchArrays["elIDSF_down"][0]   = elIDSF_down
        
    wrapper.branchArrays["elRecoSF_up"][0]   = elRecoSF_up
    wrapper.branchArrays["elRecoSF_down"][0] = elRecoSF_down

    # relative SFs only when exactly one electron is present
    if event.nEle == 1 and event.nMu == 0:
        wrapper.branchArrays["elTrigSF_up_rel"][0]   = elTrigSF_up/elTrigSF
        wrapper.branchArrays["elTrigSF_down_rel"][0] = elTrigSF_down/elTrigSF
        wrapper.branchArrays["elSF_up_rel"][0]   = (elIDSF_up*elRecoSF_up)/(elIDSF*elRecoSF)
        wrapper.branchArrays["elSF_down_rel"][0] = (elIDSF_down*elRecoSF_down)/(elIDSF*elRecoSF)
    else:
        wrapper.branchArrays["elTrigSF_up_rel"][0]   = 1.
        wrapper.branchArrays["elTrigSF_down_rel"][0] = 1.
        wrapper.branchArrays["elSF_up_rel"][0]   = 1.
        wrapper.branchArrays["elSF_down_rel"][0] = 1.
            
    # muon scale factors
    muTrigSF = 1.
    muTrigSF_up = 1.
    muTrigSF_down = 1.

    muIDSF = 1.
    muIDSF_up = 1.
    muIDSF_down = 1.

    muIsoSF = 1.
    muIsoSF_up = 1.
    muIsoSF_down = 1.

    for iMu in range(getattr(event, "nMu")):
        trigger = data[dataEra]["muTrig"].getSFs(event.Mu_Pt[iMu], abs(event.Mu_Eta[iMu]))
        idsf    = data[dataEra]["muID"].getSFs(  event.Mu_Pt[iMu], abs(event.Mu_Eta[iMu]))
        isosf   = data[dataEra]["muISO"].getSFs( event.Mu_Pt[iMu], abs(event.Mu_Eta[iMu]))

        muTrigSF      *= trigger.loc["central"]
        muIDSF        *= idsf.loc["central"]
        muIsoSF       *= isosf.loc["central"]

        muTrigSF_up   *= trigger.loc["up"]
        muTrigSF_down *= trigger.loc["down"]

        muIDSF_up     *= idsf.loc["up"]
        muIDSF_down   *= idsf.loc["down"]

        muIsoSF_up    *= isosf.loc["up"]
        muIsoSF_down  *= isosf.loc["down"]

    wrapper.branchArrays["muTrigSF"][0] = muTrigSF
    wrapper.branchArrays["muIDSF"][0]   = muIDSF
    wrapper.branchArrays["muIsoSF"][0]  = muIsoSF
    wrapper.branchArrays["muSF"][0]     = muIDSF*muIsoSF

    wrapper.branchArrays["muTrigSF_up"][0]   = muTrigSF_up
    wrapper.branchArrays["muTrigSF_down"][0] = muTrigSF_down
        
    wrapper.branchArrays["muIDSF_up"][0]     = muIDSF_up
    wrapper.branchArrays["muIDSF_down"][0]   = muIDSF_down
       
    wrapper.branchArrays["muIsoSF_up"][0]    = muIsoSF_up
    wrapper.branchArrays["muIsoSF_down"][0]  = muIsoSF_down

    # relative SFs only when exactly one muon is present
    if event.nMu == 1 and event.nEle == 0:
        wrapper.branchArrays["muTrigSF_up_rel"][0]   = muTrigSF_up/muTrigSF
        wrapper.branchArrays["muTrigSF_down_rel"][0] = muTrigSF_down/muTrigSF
        wrapper.branchArrays["muSF_up_rel"][0]       = (muIDSF_up*muIsoSF_up)/(muIDSF*muIsoSF)
        wrapper.branchArrays["muSF_down_rel"][0]     = (muIDSF_down*muIsoSF_down)/(muIDSF*muIsoSF)
    else:
        wrapper.branchArrays["muTrigSF_up_rel"][0]   = 1.
        wrapper.branchArrays["muTrigSF_down_rel"][0] = 1.
        wrapper.branchArrays["muSF_up_rel"][0]       = 1.
        wrapper.branchArrays["muSF_down_rel"][0]     = 1.

    return event

