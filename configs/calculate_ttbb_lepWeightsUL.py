import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

from correctionlib import _core
jsonDir = os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG")

muTrigName = {
    "2016preVFP":   "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    "2016postVFP":  "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    "2017":         "NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight",
    "2018":         "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    }

#dataEra = {
#   "2016preVFP":   "2016preVFP_UL",
#   "2016postVFP":  "2016postVFP_UL", 
#   "2017":         "2017_UL",
#   "2018":         "2018_UL",
#   }

data = {}
for year in ["2018", "2017", "2016preVFP", "2016postVFP"]:
    yearS = year[2:]

    # dict
    data[year] = {}

    # local sf directory
    sfDir = os.path.join(karimpath, "data", "UL_"+yearS)

    # electron trigger
    eleTrigFile = _core.CorrectionSet.from_file(
        os.path.join(sfDir, "EleTriggerSF_NanoAODv2_v0.json"))
    data[year]["eleTrig"] = eleTrigFile["EleTriggerSF"]

    # electron ID/RECO
    ele_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "EGM", year+"_UL", "electron.json.gz"))
    data[year]["electron"] = ele_evaluator["UL-Electron-ID-SF"]

    # muon Trig/ID/ISO
    mu_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "MUO", year+"_UL", "muon_Z.json.gz"))
    data[year]["muTrig"] = mu_evaluator[muTrigName[year]]
    data[year]["muID"]   = mu_evaluator["NUM_TightID_DEN_TrackerMuons"]
    data[year]["muISO"]  = mu_evaluator["NUM_TightRelIso_DEN_TightIDandIPCut"]

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
    wrapper.SetFloatVar("muTrigSF_up_rel")
    wrapper.SetFloatVar("muTrigSF_down_rel")

    wrapper.SetFloatVar("elTrigSF")
    wrapper.SetFloatVar("elTrigSF_up_rel")
    wrapper.SetFloatVar("elTrigSF_down_rel")

    # lepton scale factor
    wrapper.SetFloatVar("muIDSF")
    wrapper.SetFloatVar("muIDSF_up_rel")
    wrapper.SetFloatVar("muIDSF_down_rel")
    wrapper.SetFloatVar("elIDSF")
    wrapper.SetFloatVar("elIDSF_up_rel")
    wrapper.SetFloatVar("elIDSF_down_rel")

    wrapper.SetFloatVar("muIsoSF")
    wrapper.SetFloatVar("muIsoSF_up_rel")
    wrapper.SetFloatVar("muIsoSF_down_rel")
    wrapper.SetFloatVar("elRecoSF")
    wrapper.SetFloatVar("elRecoSF_up_rel")
    wrapper.SetFloatVar("elRecoSF_down_rel")


def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    
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

    for iEl in range(event.nEle):
        elIDSF        *= data[dataEra]["electron"].evaluate(dataEra, "sf","Tight", 
                            event.Ele_EtaSC[iEl], event.Ele_Pt[iEl])
        elIDSF_up     *= data[dataEra]["electron"].evaluate(dataEra, "sfup","Tight", 
                            event.Ele_EtaSC[iEl], event.Ele_Pt[iEl])
        elIDSF_down   *= data[dataEra]["electron"].evaluate(dataEra, "sfdown","Tight", 
                            event.Ele_EtaSC[iEl], event.Ele_Pt[iEl])
        elRecoSF      *= data[dataEra]["electron"].evaluate(dataEra, "sf","RecoAbove20", 
                            event.Ele_EtaSC[iEl], event.Ele_Pt[iEl])
        elRecoSF_up   *= data[dataEra]["electron"].evaluate(dataEra, "sfup","RecoAbove20", 
                            event.Ele_EtaSC[iEl], event.Ele_Pt[iEl])
        elRecoSF_down *= data[dataEra]["electron"].evaluate(dataEra, "sfdown","RecoAbove20", 
                            event.Ele_EtaSC[iEl], event.Ele_Pt[iEl])

        elTrigSF      *= data[dataEra]["eleTrig"].evaluate("central", 
                            event.Ele_Pt[iEl], event.Ele_EtaSC[iEl])
        elTrigSF_up   *= data[dataEra]["eleTrig"].evaluate("up", 
                            event.Ele_Pt[iEl], event.Ele_EtaSC[iEl])
        elTrigSF_down *= data[dataEra]["eleTrig"].evaluate("down", 
                            event.Ele_Pt[iEl], event.Ele_EtaSC[iEl])
            
    # apply HLT zvtx correction
    if dataEra == "2017":
        elTrigSF      *= 0.991
        elTrigSF_up   *= 0.991
        elTrigSF_down *= 0.991

    wrapper.branchArrays["elTrigSF"][0] = elTrigSF
    wrapper.branchArrays["elIDSF"][0]   = elIDSF
    wrapper.branchArrays["elRecoSF"][0] = elRecoSF

    # relative SFs only when exactly one electron is present
    if event.nEle == 1 and event.nLooseLep == 1:
        wrapper.branchArrays["elTrigSF_up_rel"][0]   = elTrigSF_up/elTrigSF
        wrapper.branchArrays["elTrigSF_down_rel"][0] = elTrigSF_down/elTrigSF

        wrapper.branchArrays["elIDSF_up_rel"][0]     = elIDSF_up/elIDSF
        wrapper.branchArrays["elIDSF_down_rel"][0]   = elIDSF_down/elIDSF
            
        wrapper.branchArrays["elRecoSF_up_rel"][0]   = elRecoSF_up/elRecoSF
        wrapper.branchArrays["elRecoSF_down_rel"][0] = elRecoSF_down/elRecoSF
    else:
        wrapper.branchArrays["elTrigSF_up_rel"][0]   = 1.
        wrapper.branchArrays["elTrigSF_down_rel"][0] = 1.

        wrapper.branchArrays["elIDSF_up_rel"][0]     = 1.
        wrapper.branchArrays["elIDSF_down_rel"][0]   = 1.
            
        wrapper.branchArrays["elRecoSF_up_rel"][0]   = 1.
        wrapper.branchArrays["elRecoSF_down_rel"][0] = 1.
            
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

    for iMu in range(event.nMu):
        muIDSF       *= data[dataEra]["muID"].evaluate(
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), event.Mu_Pt[iMu], "sf")
        muIDSF_up    *= data[dataEra]["muID"].evaluate(  
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), event.Mu_Pt[iMu], "systup")
        muIDSF_down  *= data[dataEra]["muID"].evaluate(  
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), event.Mu_Pt[iMu], "systdown")
        muIsoSF      *= data[dataEra]["muISO"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), event.Mu_Pt[iMu], "sf")
        muIsoSF_up   *= data[dataEra]["muISO"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), event.Mu_Pt[iMu], "systup")
        muIsoSF_down *= data[dataEra]["muISO"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), event.Mu_Pt[iMu], "systdown")
        
        muTrigSF      *= data[dataEra]["muTrig"].evaluate(
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), max(29.,event.Mu_Pt[iMu]), "sf")
        muTrigSF_up   *= data[dataEra]["muTrig"].evaluate(
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), max(29.,event.Mu_Pt[iMu]), "systup")
        muTrigSF_down *= data[dataEra]["muTrig"].evaluate(
                            dataEra+"_UL", abs(event.Mu_Eta[iMu]), max(29.,event.Mu_Pt[iMu]), "systdown")
        

    wrapper.branchArrays["muTrigSF"][0] = muTrigSF
    wrapper.branchArrays["muIDSF"][0]   = muIDSF
    wrapper.branchArrays["muIsoSF"][0]  = muIsoSF

    # relative SFs only when exactly one muon is present
    if event.nMu == 1 and event.nLooseLep == 1:
        wrapper.branchArrays["muTrigSF_up_rel"][0]   = muTrigSF_up/muTrigSF
        wrapper.branchArrays["muTrigSF_down_rel"][0] = muTrigSF_down/muTrigSF
            
        wrapper.branchArrays["muIDSF_up_rel"][0]     = muIDSF_up/muIDSF
        wrapper.branchArrays["muIDSF_down_rel"][0]   = muIDSF_down/muIDSF
           
        wrapper.branchArrays["muIsoSF_up_rel"][0]    = muIsoSF_up/muIsoSF
        wrapper.branchArrays["muIsoSF_down_rel"][0]  = muIsoSF_down/muIsoSF
    else:
        wrapper.branchArrays["muTrigSF_up_rel"][0]   = 1.
        wrapper.branchArrays["muTrigSF_down_rel"][0] = 1.

        wrapper.branchArrays["muIDSF_up_rel"][0]     = 1.
        wrapper.branchArrays["muIDSF_down_rel"][0]   = 1.
           
        wrapper.branchArrays["muIsoSF_up_rel"][0]    = 1.
        wrapper.branchArrays["muIsoSF_down_rel"][0]  = 1.

    return event

    
