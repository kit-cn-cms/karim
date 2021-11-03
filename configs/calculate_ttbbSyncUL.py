import numpy as np
import common
import weightModules
from array import array
import os
import sys
from correctionlib import _core
#import correctionlib
#correctionlib.register_pyroot_binding()

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))

muTrigName = {
    "2016preVFP":   "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    "2016postVFP":  "NUM_IsoMu24_or_IsoTkMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    "2017":         "NUM_IsoMu27_DEN_CutBasedIdTight_and_PFIsoTight",
    "2018":         "NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight",
    }
puName = {
    "2016preVFP":   "Collisions16_UltraLegacy_goldenJSON",
    "2016postVFP":  "Collisions16_UltraLegacy_goldenJSON",
    "2017":         "Collisions17_UltraLegacy_goldenJSON",
    "2018":         "Collisions18_UltraLegacy_goldenJSON",
    }
data = {}
itFit = {}
btagSF = {}
btagEff = {}
for year in ["2018", "2017", "2016preVFP", "2016postVFP"]:
    # short year
    yearS = year[2:]

    # dict
    data[year] = {}

    # sf directory
    sfDir = os.path.join(karimpath, "data", "UL_"+yearS)
    jsonDir = os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG")

    # electron ID/RECO/ISO
    ele_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "EGM", year+"_UL", "electron.json.gz"))
    data[year]["electron"] = ele_evaluator["UL-Electron-ID-SF"]

    # electron trigger
    eleTrigFile = _core.CorrectionSet.from_file(
        os.path.join(sfDir, "EleTriggerSF_NanoAODv2_v0.json"))
    data[year]["eleTrig"] = eleTrigFile["EleTriggerSF"]


    mu_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "MUO", year+"_UL", "muon_Z.json.gz"))
    #data[year]["muon"] = mu_evaluator
    data[year]["muTrig"] = mu_evaluator[muTrigName[year]]
    data[year]["muID"]   = mu_evaluator["NUM_TightID_DEN_TrackerMuons"]
    data[year]["muISO"]  = mu_evaluator["NUM_TightRelIso_DEN_TightIDandIPCut"]

    # initialize pileup SFs
    pu_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "LUM", year+"_UL", "puWeights.json.gz"))
    data[year]["pu"] = pu_evaluator[puName[year]]

    if year in ["2017", "2018"]:
        btagSFjson = _core.CorrectionSet.from_file(
            os.path.join(jsonDir, "BTV", year+"_UL", "btagging.json.gz"))
        btagSF[year]   = btagSFjson["deepJet_wp"]
        itFit[year]    = btagSFjson["deepJet_shape"]

        btagEffjson = _core.CorrectionSet.from_file(os.path.join(sfDir, "btagEff_ttbb_deepJet.json"))
        btagEff[year] = btagEffjson["btagEff"]
year = None

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        ]
    return variables

def base_selection(event):
    if event.nEle == 1 and event.nMu == 0 and event.nLooseLep == 1:
        return True
    if event.nEle == 0 and event.nMu == 1 and event.nLooseLep == 1:
        return True
    return False

def set_branches(wrapper, jec = None):
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("luminosityBlock")   
    wrapper.SetIntVar("event")   

    wrapper.SetIntVar("is_e")
    wrapper.SetIntVar("is_mu")

    wrapper.SetIntVar("trigger_e")
    wrapper.SetIntVar("trigger_mu")

    wrapper.SetFloatVar("trigger_SF")
    
    wrapper.SetIntVar("flags")
    
    wrapper.SetIntVar("nJets")
    wrapper.SetIntVar("nBJets_deepJetM")

    wrapper.SetIntVar("nPV")

    wrapper.SetFloatVar("lepton_pt")
    wrapper.SetFloatVar("lepton_pt_uncorr")
    wrapper.SetFloatVar("lepton_eta")
    wrapper.SetFloatVar("lepton_phi")
    wrapper.SetFloatVar("lepton_deltaEtaSC")
    wrapper.SetFloatVar("lepton_iso")
    wrapper.SetFloatVar("lepton_abs_dxy")
    wrapper.SetFloatVar("lepton_abs_dz")
    wrapper.SetFloatVar("lepton_SF")

    #wrapper.SetFloatVar("jet1_pt_raw")
    wrapper.SetFloatVar("jet1_pt")
    wrapper.SetFloatVar("jet1_eta")
    wrapper.SetFloatVar("jet1_phi")
    wrapper.SetFloatVar("jet1_deepJet")

    wrapper.SetFloatVar("jet2_pt")
    wrapper.SetFloatVar("jet2_eta")
    wrapper.SetFloatVar("jet2_phi")
    wrapper.SetFloatVar("jet2_deepJet")

    wrapper.SetFloatVar("btag_weight_fixWP_MT")
    wrapper.SetFloatVar("btag_weight_itFit")

    wrapper.SetIntVar("pu_nTrueInt")
    wrapper.SetFloatVar("pu_weight")
    
    wrapper.SetFloatVar("L1_prefire_weight")


def calculate_variables(event, wrapper, sample, jec, dataEra, genWeights = None):
    '''
    calculate weights
    '''
    
    wrapper.branchArrays["run"][0] = event.run
    wrapper.branchArrays["luminosityBlock"][0] = event.lumi
    wrapper.branchArrays["event"][0] = event.event

    if event.nEle == 1 and event.nLooseLep == 1:
        wrapper.branchArrays["is_e"][0] = 1
        if "SingleMu" in sample:
            wrapper.branchArrays["trigger_e"][0] = 0
        else:
            wrapper.branchArrays["trigger_e"][0] = event.triggered_El
    else:
        wrapper.branchArrays["is_e"][0] = 0
        wrapper.branchArrays["trigger_e"][0] = 0

    if event.nMu == 1 and event.nLooseLep == 1:
        wrapper.branchArrays["is_mu"][0] = 1
        if "SingleEl" in sample or "EGamma" in sample:
            wrapper.branchArrays["trigger_mu"][0] = 0
        else:
            wrapper.branchArrays["trigger_mu"][0] = event.triggered_Mu
    else:
        wrapper.branchArrays["is_mu"][0] = 0
        wrapper.branchArrays["trigger_mu"][0] = 0

    isData = False
    if "SingleEl" in sample or "EGamma" in sample or "SingleMu" in sample:
        isData = True

    if not isData:
        trigSF = 1.
        lepSF  = 1.
        
        if event.nEle == 1 and event.nLooseLep == 1:
            lepSF  *= data[dataEra]["electron"].evaluate(
                        dataEra,"sf","Tight", event.Ele_EtaSC[0], min(499., event.Ele_Pt[0]))
            lepSF  *= data[dataEra]["electron"].evaluate(
                        dataEra,"sf","RecoAbove20", event.Ele_EtaSC[0], min(499., event.Ele_Pt[0]))
            trigSF *= data[dataEra]["eleTrig"].evaluate("central", event.Ele_Pt[0], event.Ele_EtaSC[0])
            if dataEra == "2017": trigSF *= 0.991 # HLT zvtx correction


        if event.nMu == 1 and event.nLooseLep == 1:
            trigSF *= data[dataEra]["muTrig"].evaluate(abs(event.Mu_Eta[0]), min(199., event.Mu_Pt[0]), "nominal")
            if dataEra == "2018":
                lepSF  *= data[dataEra]["muID"].evaluate( min(119., event.Mu_Pt[0]), "nominal")
                lepSF  *= data[dataEra]["muISO"].evaluate(min(119., event.Mu_Pt[0]), "nominal")
            else:
                lepSF  *= data[dataEra]["muID"].evaluate(  abs(event.Mu_Eta[0]), min(119., event.Mu_Pt[0]), "nominal")
                lepSF  *= data[dataEra]["muISO"].evaluate( abs(event.Mu_Eta[0]), min(119., event.Mu_Pt[0]), "nominal")
        
    if isData:
        wrapper.branchArrays["trigger_SF"][0] = -1.
        wrapper.branchArrays["lepton_SF"][0] = -1.
    else:
        wrapper.branchArrays["trigger_SF"][0] = trigSF
        wrapper.branchArrays["lepton_SF"][0] = lepSF
        

    wrapper.branchArrays["flags"][0] = event.metFilter
    
    wrapper.branchArrays["nJets"][0] = event.nJets_nom
    wrapper.branchArrays["nBJets_deepJetM"][0] = event.nTagsM_nom

    
    if event.nLep == 1:
        wrapper.branchArrays["lepton_pt"][0]  = event.Lep_Pt[0]
        wrapper.branchArrays["lepton_eta"][0] = event.Lep_Eta[0]
        wrapper.branchArrays["lepton_phi"][0] = event.Lep_Phi[0]
        if event.nEle == 1:
            wrapper.branchArrays["lepton_deltaEtaSC"][0] = event.Ele_EtaSC[0]-event.Ele_Eta[0]
            wrapper.branchArrays["lepton_pt_uncorr"][0]  = event.Ele_Pt_uncorr[0]
        else:
            wrapper.branchArrays["lepton_deltaEtaSC"][0] = -1
            wrapper.branchArrays["lepton_pt_uncorr"][0]  = -1
        wrapper.branchArrays["lepton_iso"][0]     = event.Lep_iso[0]
        wrapper.branchArrays["lepton_abs_dxy"][0] = event.Lep_abs_dxy[0]
        wrapper.branchArrays["lepton_abs_dz"][0]  = event.Lep_abs_dz[0]
        
    if event.nJets_nom > 0:
        wrapper.branchArrays["jet1_pt"][0] = event.Jet_Pt_nom[0]
        #wrapper.branchArrays["jet1_pt"][0] = event.Jet_Pt_raw_nom[0]
        wrapper.branchArrays["jet1_eta"][0] = event.Jet_Eta_nom[0]
        wrapper.branchArrays["jet1_phi"][0] = event.Jet_Phi_nom[0]
        wrapper.branchArrays["jet1_deepJet"][0] = event.Jet_btagValue_nom[0]
    else:
        wrapper.branchArrays["jet1_pt"][0] = -1
        wrapper.branchArrays["jet1_eta"][0] = -1
        wrapper.branchArrays["jet1_phi"][0] = -1
        wrapper.branchArrays["jet1_deepJet"][0] = -1
        #wrapper.branchArrays["jet1_deepJet_shapeSF"][0] = -1
    if event.nJets_nom > 1:
        wrapper.branchArrays["jet2_pt"][0] = event.Jet_Pt_nom[1]
        #wrapper.branchArrays["jet2_pt"][0] = event.Jet_Pt_raw_nom[1]
        wrapper.branchArrays["jet2_eta"][0] = event.Jet_Eta_nom[1]
        wrapper.branchArrays["jet2_phi"][0] = event.Jet_Phi_nom[1]
        wrapper.branchArrays["jet2_deepJet"][0] = event.Jet_btagValue_nom[1]
    else:
        wrapper.branchArrays["jet2_pt"][0] = -1
        wrapper.branchArrays["jet2_eta"][0] = -1
        wrapper.branchArrays["jet2_phi"][0] = -1
        wrapper.branchArrays["jet2_deepJet"][0] = -1
        #wrapper.branchArrays["jet2_deepJet_shapeSF"][0] = -1


    if isData:
        wrapper.branchArrays["btag_weight_fixWP_MT"][0] = -1.
        wrapper.branchArrays["btag_weight_itFit"][0] = -1.
    elif "2016" in dataEra:
        wrapper.branchArrays["btag_weight_fixWP_MT"][0] = 1.
        wrapper.branchArrays["btag_weight_itFit"][0] = 1.
    else:
        P_DATA_TM = 1.
        P_MC_TM   = 1.
        shapeSF   = 1.
        for idx in range(event.nJets_nom):
            eta   = abs(getattr(event, "Jet_Eta_nom")[idx])
            pt    = getattr(event, "Jet_Pt_nom")[idx]
            flav  = getattr(event, "Jet_Flav_nom")[idx]
            passes_M = getattr(event, "Jet_taggedM_nom")[idx]
            passes_T = getattr(event, "Jet_taggedT_nom")[idx]

            eff_M = btagEff[dataEra].evaluate("M", flav, eta, pt)
            eff_T = btagEff[dataEra].evaluate("T", flav, eta, pt)

            if flav == 0:
                sf_M = btagSF[dataEra].evaluate("central", "incl", "M", flav, eta, pt)
                sf_T = btagSF[dataEra].evaluate("central", "incl", "T", flav, eta, pt)
            else:
                sf_M = btagSF[dataEra].evaluate("central", "comb", "M", flav, eta, pt)
                sf_T = btagSF[dataEra].evaluate("central", "comb", "T", flav, eta, pt)

            if passes_T:
                P_MC_TM   *= eff_T
                P_DATA_TM *= eff_T*sf_T
            elif passes_M:
                P_MC_TM   *= (eff_M      - eff_T)
                P_DATA_TM *= (eff_M*sf_M - eff_T*sf_T)
            else:
                P_MC_TM   *= (1. - eff_M)
                P_DATA_TM *= (1. - eff_M*sf_M)

            # itFit
            shapeSF *= itFit[dataEra].evaluate(
                "central", flav, eta, pt, event.Jet_btagValue_nom[idx])
        wrapper.branchArrays["btag_weight_fixWP_MT"][0] = P_DATA_TM/P_MC_TM
        wrapper.branchArrays["btag_weight_itFit"][0] = shapeSF
    

    wrapper.branchArrays["nPV"][0] = event.nPV
    if isData:
        wrapper.branchArrays["pu_nTrueInt"][0] = -1
        wrapper.branchArrays["pu_weight"][0] = -1.
    else:
        wrapper.branchArrays["pu_nTrueInt"][0] = event.nTruePU
        pu = data[dataEra]["pu"].evaluate(float(event.nTruePU), "nominal")
        wrapper.branchArrays["pu_weight"][0] = pu

    if isData:
        wrapper.branchArrays["L1_prefire_weight"][0] = -1
    elif dataEra == "2018":
        wrapper.branchArrays["L1_prefire_weight"][0] = 1.
    else:
        wrapper.branchArrays["L1_prefire_weight"][0] = event.prefireWeight
    return event

