import numpy as np
import common
import weightModules
from array import array
import os
import ROOT
from pprint import pprint
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

ROOT.TH1.AddDirectory(False)
kFactors_QCD = {}
kFactors_EW = {}
kFactors_EW1 = {}
kFactors_EW2 = {}
kFactors_EW3 = {}
for mode in ["evj","eej", "vvj", "aj"]:
    filePath = os.path.join(karimpath, "data", "kFactors", mode + ".root")
    file = ROOT.TFile(filePath)
    nnlo = file.Get(mode + "_pTV_K_NNLO").Clone()
    nlo = file.Get(mode + "_pTV_K_NLO").Clone()
    ew = file.Get(mode + "_pTV_kappa_EW").Clone()
    ew1 = file.Get(mode + "_pTV_d1kappa_EW").Clone()
    ew2 = file.Get(mode + "_pTV_d2kappa_EW").Clone()
    ew3 = file.Get(mode + "_pTV_d3kappa_EW").Clone()
    nnlo.Divide(nlo)
    kFactors_QCD[mode] = nnlo.Clone(mode)
    kFactors_EW[mode] = ew.Clone()
    kFactors_EW1[mode] = ew1.Clone()
    kFactors_EW2[mode] = ew2.Clone()
    kFactors_EW3[mode] = ew3.Clone()
    print("QCD:", kFactors_QCD)
    print("EW", kFactors_EW)
    print("EW1", kFactors_EW1)
    print("EW2", kFactors_EW2)
    print("EW3", kFactors_EW3)


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

puName = {
    "2016preVFP":   "Collisions16_UltraLegacy_goldenJSON",
    "2016postVFP":  "Collisions16_UltraLegacy_goldenJSON",
    "2017":         "Collisions17_UltraLegacy_goldenJSON",
    "2018":         "Collisions18_UltraLegacy_goldenJSON",
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

    # pileup SFs
    pu_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "LUM", dataEra+"_UL", "puWeights.json.gz"))
    data[dataEra]["puSF"] = pu_evaluator[puName[dataEra]]

pprint(data)

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

 # cross section weight
    wrapper.SetFloatVar("xsNorm")

    # rate factors
    wrapper.SetFloatVar("muRUpRel_wRF")
    wrapper.SetFloatVar("muFUpRel_wRF")
    wrapper.SetFloatVar("muRDownRel_wRF")
    wrapper.SetFloatVar("muFDownRel_wRF")
    wrapper.SetFloatVar("muRUpRel")
    wrapper.SetFloatVar("muFUpRel")
    wrapper.SetFloatVar("muRDownRel")
    wrapper.SetFloatVar("muFDownRel")

    wrapper.SetFloatVar("isrUpRel_wRF")
    wrapper.SetFloatVar("fsrUpRel_wRF")
    wrapper.SetFloatVar("isrDownRel_wRF")
    wrapper.SetFloatVar("fsrDownRel_wRF")
    wrapper.SetFloatVar("isrUpRel")
    wrapper.SetFloatVar("fsrUpRel")
    wrapper.SetFloatVar("isrDownRel")
    wrapper.SetFloatVar("fsrDownRel")

    wrapper.SetFloatVar("pileup")
    wrapper.SetFloatVar("pileup_up_rel")
    wrapper.SetFloatVar("pileup_down_rel")

    wrapper.SetFloatVar("pdf_up")
    wrapper.SetFloatVar("pdf_up_rel")
    wrapper.SetFloatVar("pdf_down")
    wrapper.SetFloatVar("pdf_down_rel")

    wrapper.SetFloatVar("Boson_Pt") 
    for mode in ["evj","eej", "vvj", "aj"]:
        wrapper.SetFloatVar( mode + "_kFactor_EW")
        wrapper.SetFloatVar( mode + "_kFactor_EW1up_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW1down_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW2up_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW2down_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW3up_rel")
        wrapper.SetFloatVar( mode + "_kFactor_EW3down_rel")
        # wrapper.SetFloatVar( mode + "_kFactor_QCD")
        # wrapper.SetFloatVar( mode + "_kFactor_rel")



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
    
    ###########################
    ### LEPTON/PHOTON STUFF ###
    ###########################


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

    ##################
    ### GENWEIGHTS ###
    ##################

   # cross section norm
    wrapper.branchArrays["xsNorm"][0] = genWeights.getXS("incl")

    # rate factors
    # apply them directly to the weights
    try:
        wrapper.branchArrays["muRUpRel_wRF"  ][0] = getattr(event, "Weight_muRUp"  ) * genWeights.getRF("LHEScaleWeight_incl_1")
        wrapper.branchArrays["muRDownRel_wRF"][0] = getattr(event, "Weight_muRDown") * genWeights.getRF("LHEScaleWeight_incl_5")
        wrapper.branchArrays["muFUpRel_wRF"  ][0] = getattr(event, "Weight_muFUp"  ) * genWeights.getRF("LHEScaleWeight_incl_3")
        wrapper.branchArrays["muFDownRel_wRF"][0] = getattr(event, "Weight_muFDown") * genWeights.getRF("LHEScaleWeight_incl_7")
    except: pass
    try:
        wrapper.branchArrays["muRUpRel"  ][0] = getattr(event, "Weight_muRUp"  ) 
        wrapper.branchArrays["muRDownRel"][0] = getattr(event, "Weight_muRDown")
        wrapper.branchArrays["muFUpRel"  ][0] = getattr(event, "Weight_muFUp"  )
        wrapper.branchArrays["muFDownRel"][0] = getattr(event, "Weight_muFDown")
    except: pass
    try:
        wrapper.branchArrays["isrUpRel_wRF"  ][0] = getattr(event, "Weight_isrUp"  ) * genWeights.getRF("PSWeight_incl_2")
        wrapper.branchArrays["isrDownRel_wRF"][0] = getattr(event, "Weight_isrDown") * genWeights.getRF("PSWeight_incl_0")
        wrapper.branchArrays["fsrUpRel_wRF"  ][0] = getattr(event, "Weight_fsrUp"  ) * genWeights.getRF("PSWeight_incl_3")
        wrapper.branchArrays["fsrDownRel_wRF"][0] = getattr(event, "Weight_fsrDown") * genWeights.getRF("PSWeight_incl_1")
    except: pass
    try:
        wrapper.branchArrays["isrUpRel"  ][0] = getattr(event, "Weight_isrUp"  )
        wrapper.branchArrays["isrDownRel"][0] = getattr(event, "Weight_isrDown")
        wrapper.branchArrays["fsrUpRel"  ][0] = getattr(event, "Weight_fsrUp"  )
        wrapper.branchArrays["fsrDownRel"][0] = getattr(event, "Weight_fsrDown")
    except: pass

    pu = data[dataEra]["puSF"].evaluate(float(event.nTruePU), "nominal")
    wrapper.branchArrays["pileup"][0] = pu
    wrapper.branchArrays["pileup_up_rel"][0] = data[dataEra]["puSF"].evaluate(float(event.nTruePU), "up")/pu
    wrapper.branchArrays["pileup_down_rel"][0] = data[dataEra]["puSF"].evaluate(float(event.nTruePU), "down")/pu

    # calculate kFactors
    result = {}
    for mode in ["evj","eej", "vvj", "aj"]:
        result[mode] = {
            # "kFactor_QCD": 1.,
            "kFactor_EW": 1.,
            "kFactor_EW1_up_rel": 1.,
            "kFactor_EW1_down_rel": 1.,
            "kFactor_EW2_up_rel": 1.,
            "kFactor_EW2_down_rel": 1.,
            "kFactor_EW3_up_rel": 1.,
            "kFactor_EW3_down_rel": 1.,
        }


    pT = -1.
    if "ToLNu" in sample:
        label = "evj"
        if getattr(event, "N_wBosons") >= 1:
            pT = getattr(event, "wBoson_Pt")[0]
    elif "ToLL" in sample:
        label = "eej"
        if getattr(event, "N_zBosons") >= 1:
            pT = getattr(event, "zBoson_Pt")[0]
    elif "NuNu" in sample:
        label = "vvj"
        if getattr(event, "N_zBosons") >= 1:
            pT = getattr(event, "zBoson_Pt")[0]

    if  pT >= 30.:
        b = kFactors_QCD[label].FindBin(pT)
        result[label]["kFactor_QCD"] = kFactors_QCD[label].GetBinContent(b)

        b = kFactors_EW[label].FindBin(pT)
        nom = 1. + kFactors_EW[label].GetBinContent(b)
        ew1 = kFactors_EW1[label].GetBinContent(b)
        ew2 = kFactors_EW2[label].GetBinContent(b)
        ew3 = kFactors_EW3[label].GetBinContent(b)

        result[label]["kFactor_EW"] = nom
        
        result[label]["kFactor_EW1_up_rel"] = (nom + ew1)/nom
        result[label]["kFactor_EW1_down_rel"] = (nom - ew1)/nom

        result[label]["kFactor_EW2_up_rel"] = (nom + ew2)/nom
        result[label]["kFactor_EW2_down_rel"] = (nom - ew2)/nom

        result[label]["kFactor_EW3_up_rel"] = (nom + ew3)/nom
        result[label]["kFactor_EW3_down_rel"] = (nom - ew3)/nom

    wrapper.branchArrays["Boson_Pt"][0] = pT
    

    for mode in ["evj","eej", "vvj", "aj"]:
        wrapper.branchArrays[ mode + "_kFactor_EW"][0] = result[mode]["kFactor_EW"]
        wrapper.branchArrays[ mode + "_kFactor_EW1up_rel"][0] = result[mode]["kFactor_EW1_up_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW1down_rel"][0] = result[mode]["kFactor_EW1_down_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW2up_rel"][0] = result[mode]["kFactor_EW2_up_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW2down_rel"][0] = result[mode]["kFactor_EW2_down_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW3up_rel"][0] = result[mode]["kFactor_EW3_up_rel"]
        wrapper.branchArrays[ mode + "_kFactor_EW3down_rel"][0] = result[mode]["kFactor_EW3_down_rel"]
        # wrapper.branchArrays[ mode + "_kFactor_QCD"][0] = result[mode]["kFactor_QCD"]
        # wrapper.branchArrays[ mode + "_kFactor"][0] =  result[mode]["kFactor_QCD"]*result[mode]["kFactor_EW"] 


    # simple pdf weight
    # TODO update 
    # nom_pdf = event.Weight_pdf[0]
    # residuals = np.array([nom_pdf - event.Weight_pdf[i+1] for i in range(len(event.Weight_pdf)-1)])
    # if sample.startswith("TTbb"):
    #     variation = (np.mean(residuals**2, axis = 0))**0.5
    # else:
    #     variation = (residuals)**2
    #     variation = (variation.sum(axis=0))**0.5
    # wrapper.branchArrays["pdf_up"][0]       =  nom_pdf+variation
    # wrapper.branchArrays["pdf_up_rel"][0]   = (nom_pdf+variation)/nom_pdf
    # wrapper.branchArrays["pdf_down"][0]     =  nom_pdf-variation
    # wrapper.branchArrays["pdf_down_rel"][0] = (nom_pdf-variation)/nom_pdf













    return event

