import numpy as np
import common
import weightModules
from array import array
import os
from pprint import pprint
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

from correctionlib import _core
jsonDir = os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG")

muTrigNameTight = {
    "2016preVFP":   "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    "2016postVFP":  "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    "2017":         "NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight",
    "2018":         "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    }


mudataEra = {
    "2016preVFP":   "2016preVFP_UL",
    "2016postVFP":  "2016postVFP_UL",
    "2017":         "2017_UL",
    "2018":         "2018_UL",
    }

data = {}
for dataEra in ["2018", "2017", "2016preVFP", "2016postVFP"]:
    # short dataEra
    dataEraS = dataEra[2:]

    # dict
    data[dataEra] = {}

    # sf directory
    sfDir = os.path.join(karimpath, "data", "UL_"+dataEraS)

    # electron ID/RECO/ISO
    ele_evaluator = _core.CorrectionSet.from_file(os.path.join(jsonDir, "EGM", dataEra+"_UL", "electron.json.gz"))
    data[dataEra]["electron"] = ele_evaluator["UL-Electron-ID-SF"]
    # electron trigger SF
    sfDir = os.path.join(karimpath, "data", "UL_"+dataEra[2:])
    # tight
    eleTrig_evaluator_tight = _core.CorrectionSet.from_file(os.path.join(sfDir, "EleTriggerSF_monotop_tight.json"))
    data[dataEra]["eleTrig_tight"] = eleTrig_evaluator_tight["EleTriggerSF"]
    # loose
    eleTrig_evaluator_loose = _core.CorrectionSet.from_file(os.path.join(sfDir, "EleTriggerSF_monotop_loose.json"))
    data[dataEra]["eleTrig_loose"] = eleTrig_evaluator_loose["EleTriggerSF"]

    # photon ID SF
    photon_evaluator = _core.CorrectionSet.from_file(os.path.join(jsonDir, "EGM", dataEra+"_UL", "photon.json.gz"))
    data[dataEra]["photon"] = photon_evaluator["UL-Photon-ID-SF"]

    # muon Trig/ID/ISO
    mu_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "MUO", dataEra+"_UL", "muon_Z.json.gz"))
    data[dataEra]["muTrig_tight"] = mu_evaluator[muTrigNameTight[dataEra]]
    data[dataEra]["muIDT"]   = mu_evaluator["NUM_TightID_DEN_TrackerMuons"]
    data[dataEra]["muIDL"]   = mu_evaluator["NUM_LooseID_DEN_TrackerMuons"]
    data[dataEra]["muISOT"]  = mu_evaluator["NUM_TightRelIso_DEN_TightIDandIPCut"]
    data[dataEra]["muISOL"]  = mu_evaluator["NUM_LooseRelIso_DEN_TightIDandIPCut"]

pprint(data)
# exit()

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

    wrapper.SetIntVar("nEle_loose")   
    wrapper.SetIntVar("nEle_tight")   
    wrapper.SetIntVar("nMuon_loose")   
    wrapper.SetIntVar("nMuon_tight")   



   # electron scale factors
    wrapper.SetFloatVar("eleIDSF_tight")
    wrapper.SetFloatVar("eleIDSF_tight_up")
    wrapper.SetFloatVar("eleIDSF_tight_down")

    wrapper.SetFloatVar("eleIDSF_loose")
    wrapper.SetFloatVar("eleIDSF_loose_up")
    wrapper.SetFloatVar("eleIDSF_loose_down")

    wrapper.SetFloatVar("eleRecoSF_tight")
    wrapper.SetFloatVar("eleRecoSF_tight_up")
    wrapper.SetFloatVar("eleRecoSF_tight_down")

    wrapper.SetFloatVar("eleRecoSF_loose")
    wrapper.SetFloatVar("eleRecoSF_loose_up")
    wrapper.SetFloatVar("eleRecoSF_loose_down")

    wrapper.SetFloatVar("eleTriggerSF_tight")
    wrapper.SetFloatVar("eleTriggerSF_tight_up")
    wrapper.SetFloatVar("eleTriggerSF_tight_down")

    wrapper.SetFloatVar("eleTriggerSF_loose")
    wrapper.SetFloatVar("eleTriggerSF_loose_up")
    wrapper.SetFloatVar("eleTriggerSF_loose_down")

    # muon scale factors
    wrapper.SetFloatVar("muIDSF_tight")
    wrapper.SetFloatVar("muIDSF_tight_up")
    wrapper.SetFloatVar("muIDSF_tight_down")

    wrapper.SetFloatVar("muIDSF_loose")
    wrapper.SetFloatVar("muIDSF_loose_up")
    wrapper.SetFloatVar("muIDSF_loose_down")

    wrapper.SetFloatVar("muIsoSF_tight")
    wrapper.SetFloatVar("muIsoSF_tight_up")
    wrapper.SetFloatVar("muIsoSF_tight_down")
      
    wrapper.SetFloatVar("muIsoSF_loose")
    wrapper.SetFloatVar("muIsoSF_loose_up")
    wrapper.SetFloatVar("muIsoSF_loose_down")

    wrapper.SetFloatVar("muTriggerSF_tight")
    wrapper.SetFloatVar("muTriggerSF_tight_up")
    wrapper.SetFloatVar("muTriggerSF_tight_down")

    # photon scale factors
    wrapper.SetFloatVar("phoIDSF_tight")
    wrapper.SetFloatVar("phoIDSF_tight_up")
    wrapper.SetFloatVar("phoIDSF_tight_down")

    wrapper.SetFloatVar("phoIDSF_loose")
    wrapper.SetFloatVar("phoIDSF_loose_up")
    wrapper.SetFloatVar("phoIDSF_loose_down")



def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "Evt_ID")
    wrapper.branchArrays["run"][0]   = getattr(event, "Evt_Run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "Evt_Lumi")

    wrapper.branchArrays["nEle_loose"][0]  = getattr(event, "N_LooseElectrons")
    wrapper.branchArrays["nEle_tight"][0]  = getattr(event, "N_TightElectrons")
    wrapper.branchArrays["nMuon_loose"][0]  = getattr(event, "N_LooseMuons")
    wrapper.branchArrays["nMuon_tight"][0]  = getattr(event, "N_TightMuons")
    
    # electron scale factors
    # tight electrons
    elIDSF_tight = 1.
    elIDSF_tight_up = 1.
    elIDSF_tight_down = 1.

    elRecoSF_tight = 1.
    elRecoSF_tight_up = 1.
    elRecoSF_tight_down = 1.

    elTriggerSF_tight = 1.
    elTriggerSF_tight_up = 1.
    elTriggerSF_tight_down = 1.

    for iEl in range(getattr(event, "N_TightElectrons")):
        # TODO super cluster eta
        if getattr(event, "TightElectron_Pt")[iEl] < 500:
            pt = getattr(event, "TightElectron_Pt")[iEl]
        else:
            pt = 499.
        idsf = data[dataEra]["electron"].evaluate(dataEra,"sf","Tight", getattr(event, "TightElectron_EtaSC")[iEl], pt)
        idsfErr_up = data[dataEra]["electron"].evaluate(dataEra,"sfup","Tight", getattr(event, "TightElectron_EtaSC")[iEl], pt)
        idsfErr_down = data[dataEra]["electron"].evaluate(dataEra,"sfdown","Tight", getattr(event, "TightElectron_EtaSC")[iEl], pt)

        recosf    = data[dataEra]["electron"].evaluate(dataEra,"sf","RecoAbove20", getattr(event, "TightElectron_EtaSC")[iEl], pt)
        recosfErr_up    = data[dataEra]["electron"].evaluate(dataEra,"sfup","RecoAbove20", getattr(event, "TightElectron_EtaSC")[iEl], pt)
        recosfErr_down    = data[dataEra]["electron"].evaluate(dataEra,"sfdown","RecoAbove20", getattr(event, "TightElectron_EtaSC")[iEl], pt)

        triggersf = data[dataEra]["eleTrig_tight"].evaluate("central", pt, getattr(event, "TightElectron_EtaSC")[iEl])
        triggersf_up = data[dataEra]["eleTrig_tight"].evaluate("up", pt, getattr(event, "TightElectron_EtaSC")[iEl])
        triggersf_down = data[dataEra]["eleTrig_tight"].evaluate("down", pt, getattr(event, "TightElectron_EtaSC")[iEl])

        elIDSF_tight        *= idsf
        elIDSF_tight_up     *= idsfErr_up
        elIDSF_tight_down   *= idsfErr_down

        elRecoSF_tight      *= recosf
        elRecoSF_tight_up   *= recosfErr_up
        elRecoSF_tight_down *= recosfErr_down

        elTriggerSF_tight      *= triggersf
        elTriggerSF_tight_up   *= triggersf_up
        elTriggerSF_tight_down *= triggersf_down

    wrapper.branchArrays["eleIDSF_tight"][0]   = elIDSF_tight
    wrapper.branchArrays["eleIDSF_tight_up"][0]   = elIDSF_tight_up
    wrapper.branchArrays["eleIDSF_tight_down"][0]   = elIDSF_tight_down

    wrapper.branchArrays["eleRecoSF_tight"][0]   = elRecoSF_tight
    wrapper.branchArrays["eleRecoSF_tight_up"][0]   = elRecoSF_tight_up
    wrapper.branchArrays["eleRecoSF_tight_down"][0]   = elRecoSF_tight_down

    wrapper.branchArrays["eleTriggerSF_tight"][0]   = elTriggerSF_tight
    wrapper.branchArrays["eleTriggerSF_tight_up"][0]   = elTriggerSF_tight_up
    wrapper.branchArrays["eleTriggerSF_tight_down"][0]   = elTriggerSF_tight_down

    # loose electrons
    elIDSF_loose = 1.
    elIDSF_loose_up = 1.
    elIDSF_loose_down = 1.

    elRecoSF_loose = 1.
    elRecoSF_loose_up = 1.
    elRecoSF_loose_down = 1.


    elTriggerSF_loose = 1.
    elTriggerSF_loose_up = 1.
    elTriggerSF_loose_down = 1.

    for iEl in range(getattr(event, "N_LooseElectrons")):
        # TODO super cluster eta
        if getattr(event, "LooseElectron_Pt")[iEl] < 500:
            pt = getattr(event, "LooseElectron_Pt")[iEl]
        else:
            pt = 499.
        idsf = data[dataEra]["electron"].evaluate(dataEra,"sf","Loose", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
        idsfErr_up = data[dataEra]["electron"].evaluate(dataEra,"sfup","Loose", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
        idsfErr_down = data[dataEra]["electron"].evaluate(dataEra,"sfdown","Loose", getattr(event, "LooseElectron_EtaSC")[iEl], pt)

        if pt >= 20.:
            recosf    = data[dataEra]["electron"].evaluate(dataEra,"sf","RecoAbove20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
            recosfErr_up    = data[dataEra]["electron"].evaluate(dataEra,"sfup","RecoAbove20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
            recosfErr_down    = data[dataEra]["electron"].evaluate(dataEra,"sfdown","RecoAbove20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
        else:
            recosf    = data[dataEra]["electron"].evaluate(dataEra,"sf","RecoBelow20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
            recosfErr_up    = data[dataEra]["electron"].evaluate(dataEra,"sfup","RecoBelow20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)
            recosfErr_down    = data[dataEra]["electron"].evaluate(dataEra,"sfdown","RecoBelow20", getattr(event, "LooseElectron_EtaSC")[iEl], pt)

        triggersf = data[dataEra]["eleTrig_loose"].evaluate("central", getattr(event, "LooseElectron_Pt")[iEl], getattr(event, "LooseElectron_EtaSC")[iEl])
        triggersf_up = data[dataEra]["eleTrig_loose"].evaluate("up", getattr(event, "LooseElectron_Pt")[iEl], getattr(event, "LooseElectron_EtaSC")[iEl])
        triggersf_down = data[dataEra]["eleTrig_loose"].evaluate("down",  getattr(event, "LooseElectron_Pt")[iEl], getattr(event, "LooseElectron_EtaSC")[iEl])

        elIDSF_loose        *= idsf
        elIDSF_loose_up     *= idsfErr_up
        elIDSF_loose_down   *= idsfErr_down

        elRecoSF_loose      *= recosf
        elRecoSF_loose_up   *= recosfErr_up
        elRecoSF_loose_down *= recosfErr_down

        elTriggerSF_loose      *= triggersf
        elTriggerSF_loose_up   *= triggersf_up
        elTriggerSF_loose_down *= triggersf_down

    wrapper.branchArrays["eleIDSF_loose"][0]   = elIDSF_loose
    wrapper.branchArrays["eleIDSF_loose_up"][0]   = elIDSF_loose_up
    wrapper.branchArrays["eleIDSF_loose_down"][0]   = elIDSF_loose_down

    wrapper.branchArrays["eleRecoSF_loose"][0]   = elRecoSF_loose
    wrapper.branchArrays["eleRecoSF_loose_up"][0]   = elRecoSF_loose_up
    wrapper.branchArrays["eleRecoSF_loose_down"][0]   = elRecoSF_loose_down

    wrapper.branchArrays["eleTriggerSF_loose"][0]   = elTriggerSF_loose
    wrapper.branchArrays["eleTriggerSF_loose_up"][0]   = elTriggerSF_loose_up
    wrapper.branchArrays["eleTriggerSF_loose_down"][0]   = elTriggerSF_loose_down

    # # tight photons
    phoIDSF_tight = 1.
    phoIDSF_tight_up = 1.
    phoIDSF_tight_down = 1.

    for iPho in range(getattr(event, "N_TightPhotons")):
        if getattr(event, "TightPhoton_Pt")[iPho] < 500:
            pt = getattr(event, "TightPhoton_Pt")[iPho]
        else:
            pt = 499.
        sf = data[dataEra]["photon"].evaluate(dataEra,"sf","Tight", getattr(event, "TightPhoton_Eta")[iPho], pt)
        sf_up = data[dataEra]["photon"].evaluate(dataEra,"sfup","Tight", getattr(event, "TightPhoton_Eta")[iPho], pt)
        sf_down = data[dataEra]["photon"].evaluate(dataEra,"sfdown","Tight", getattr(event, "TightPhoton_Eta")[iPho], pt)

        phoIDSF_tight        *= sf
        phoIDSF_tight_up     *= sf_up
        phoIDSF_tight_down   *= sf_down

    wrapper.branchArrays["phoIDSF_tight"][0]   = phoIDSF_tight
    wrapper.branchArrays["phoIDSF_tight_up"][0]   = phoIDSF_tight_up
    wrapper.branchArrays["phoIDSF_tight_down"][0]   = phoIDSF_tight_down

           
    # tight muons
    muIDSF_tight = 1.
    muIDSF_tight_up = 1.
    muIDSF_tight_down = 1.

    muIsoSF_tight = 1.
    muIsoSF_tight_up = 1.
    muIsoSF_tight_down = 1.
    
    muTrigSF_tight = 1.
    muTrigSF_tight_up = 1.
    muTrigSF_tight_down = 1.


    for iMu in range(getattr(event, "N_TightMuons")):
        idsf     = data[dataEra]["muIDT"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), min(119., event.TightMuon_Pt[iMu]), "sf")
        idsfErr_up  = data[dataEra]["muIDT"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), min(119., event.TightMuon_Pt[iMu]), "systup")
        idsfErr_down  = data[dataEra]["muIDT"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), min(119., event.TightMuon_Pt[iMu]), "systdown")
        isosf    = data[dataEra]["muISOT"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), min(119., event.TightMuon_Pt[iMu]), "sf")
        isosfErr_up = data[dataEra]["muISOT"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), min(119., event.TightMuon_Pt[iMu]), "systup")
        isosfErr_down = data[dataEra]["muISOT"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), min(119., event.TightMuon_Pt[iMu]), "systdown")

        muTrigSF_tight      *= data[dataEra]["muTrig_tight"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), max(29.,event.TightMuon_Pt[iMu]), "sf")
        muTrigSF_tight_up   *= data[dataEra]["muTrig_tight"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), max(29.,event.TightMuon_Pt[iMu]), "systup")
        muTrigSF_tight_down *= data[dataEra]["muTrig_tight"].evaluate(mudataEra[dataEra], abs(event.TightMuon_Eta[iMu]), max(29.,event.TightMuon_Pt[iMu]), "systdown")

        muIDSF_tight        *= idsf
        muIsoSF_tight       *= isosf

        muIDSF_tight_up     *= idsfErr_up
        muIDSF_tight_down   *= idsfErr_down

        muIsoSF_tight_up    *= isosfErr_up
        muIsoSF_tight_down  *= isosfErr_down

    wrapper.branchArrays["muIDSF_tight"][0]   = muIDSF_tight
    wrapper.branchArrays["muIDSF_tight_up"][0]   = muIDSF_tight_up
    wrapper.branchArrays["muIDSF_tight_down"][0]   = muIDSF_tight_down

    wrapper.branchArrays["muIsoSF_tight"][0]  = muIsoSF_tight
    wrapper.branchArrays["muIsoSF_tight_up"][0]  = muIsoSF_tight_up
    wrapper.branchArrays["muIsoSF_tight_down"][0]  = muIsoSF_tight_down

    wrapper.branchArrays["muTriggerSF_tight"][0] = muTrigSF_tight
    wrapper.branchArrays["muTriggerSF_tight_up"][0] = muTrigSF_tight_up
    wrapper.branchArrays["muTriggerSF_tight_down"][0] = muTrigSF_tight_down

    # loose muons
    muIDSF_loose = 1.
    muIDSF_loose_up = 1.
    muIDSF_loose_down = 1.
    
    muIsoSF_loose = 1.
    muIsoSF_loose_up = 1.
    muIsoSF_loose_down = 1.

    for iMu in range(getattr(event, "N_LooseMuons")):
        idsf     = data[dataEra]["muIDT"].evaluate(mudataEra[dataEra], abs(event.LooseMuon_Eta[iMu]), min(119., event.LooseMuon_Pt[iMu]), "sf")
        idsfErr_up  = data[dataEra]["muIDT"].evaluate(mudataEra[dataEra], abs(event.LooseMuon_Eta[iMu]), min(119., event.LooseMuon_Pt[iMu]), "systup")
        idsfErr_down  = data[dataEra]["muIDT"].evaluate(mudataEra[dataEra], abs(event.LooseMuon_Eta[iMu]), min(119., event.LooseMuon_Pt[iMu]), "systdown")

        isosf    = data[dataEra]["muISOT"].evaluate(mudataEra[dataEra], abs(event.LooseMuon_Eta[iMu]), min(119., event.LooseMuon_Pt[iMu]), "sf")
        isosfErr_up = data[dataEra]["muISOT"].evaluate(mudataEra[dataEra], abs(event.LooseMuon_Eta[iMu]), min(119., event.LooseMuon_Pt[iMu]), "systup")
        isosfErr_down = data[dataEra]["muISOT"].evaluate(mudataEra[dataEra], abs(event.LooseMuon_Eta[iMu]), min(119., event.LooseMuon_Pt[iMu]), "systdown")

        muIDSF_loose       *= idsf
        muIsoSF_loose      *= isosf

        muIDSF_loose_up     *= idsfErr_up
        muIDSF_loose_down   *= idsfErr_down

        muIsoSF_loose_up    *= isosfErr_up
        muIsoSF_loose_down  *= isosfErr_down


    wrapper.branchArrays["muIDSF_loose"][0]   = muIDSF_loose
    wrapper.branchArrays["muIDSF_loose_up"][0]   = muIDSF_loose_up
    wrapper.branchArrays["muIDSF_loose_down"][0]   = muIDSF_loose_down
    wrapper.branchArrays["muIsoSF_loose"][0]  = muIsoSF_loose
    wrapper.branchArrays["muIsoSF_loose_up"][0]  = muIsoSF_loose_up
    wrapper.branchArrays["muIsoSF_loose_down"][0]  = muIsoSF_loose_down
    return event

