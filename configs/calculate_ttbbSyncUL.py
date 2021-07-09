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
sfDir = os.path.join(karimpath, "data", "UL_"+year)

# initialize iterative fit b-tagging sfs
btaggingSFs = weightModules.BTaggingScaleFactors(os.path.join(sfDir, "btaggingSF_deepJet.csv"))
btaggingSFs.removeUnusedSys(keep = ["central"], jec = [])

# translate jetFlavor into btv flavor definition
flavTranslator = {
    5: 0, # b jets
    4: 1, # c jets
    3: 2, # lf jets
    2: 2, # lf jets
    1: 2, # lf jets
    0: 2, # lf jets
    }

#Download the correct JSON files 
ele_evaluator = _core.CorrectionSet.from_file(os.path.join(sfDir, "electron.json"))

#elTrigSFs = weightModules.LeptonSFs(
#    csv     = os.path.join(sfDir, "electron_triggerSF_"+year+".csv"),
#    sfName  = "ele28_ht150_OR_ele32_ele_pt_ele_sceta")
#muTrigSFs = weightModules.LeptonSFs(
#    csv     = os.path.join(sfDir, "muon_triggerSF_"+year+".csv"),
#    sfName  = "IsoMu24_PtEtaBins")
#    #sfName  = "IsoMu27_PtEtaBins") 2017 value

# initialize muon ID scale factors
muIDSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "Efficiencies_muon_generalTracks_Z_Run2018_UL_ID.csv"),
    sfName  = "NUM_TightID_DEN_TrackerMuons_abseta_pt")

# initialize muon Iso scale factors
muIsoSFs  = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "Efficiencies_muon_generalTracks_Z_Run2018_UL_ISO.csv"),
    sfName  = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt")

# initialize pileup SFs
pileupSFs = weightModules.PileupSFs(os.path.join(sfDir, "pileup.csv"))





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
    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("luminosityBlock")   

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
    wrapper.SetFloatVar("lepton_deltaEtaSC")
    wrapper.SetFloatVar("lepton_iso")
    wrapper.SetFloatVar("lepton_abs_dxy")
    wrapper.SetFloatVar("lepton_abs_dz")
    wrapper.SetFloatVar("lepton_SF")

    wrapper.SetFloatVar("jet1_pt")
    wrapper.SetFloatVar("jet1_eta")
    wrapper.SetFloatVar("jet1_phi")
    wrapper.SetFloatVar("jet1_deepJet")
    wrapper.SetFloatVar("jet1_deepJet_shapeSF")

    wrapper.SetFloatVar("jet2_pt")
    wrapper.SetFloatVar("jet2_eta")
    wrapper.SetFloatVar("jet2_phi")
    wrapper.SetFloatVar("jet2_deepJet")
    wrapper.SetFloatVar("jet2_deepJet_shapeSF")

    wrapper.SetFloatVar("deepJet_shapeSF_weight")

    wrapper.SetFloatVar("MET_t1_pt")
    wrapper.SetFloatVar("MET_t1_phi")
    wrapper.SetFloatVar("MET_xy_pt")
    wrapper.SetFloatVar("MET_xy_phi")
    wrapper.SetFloatVar("MET_smeared_pt")
    wrapper.SetFloatVar("MET_smeared_phi")
    
    wrapper.SetIntVar("pu_nTrueInt")
    wrapper.SetFloatVar("pu_weight")
    
    wrapper.SetFloatVar("L1_prefire_weight")


def calculate_variables(event, wrapper, sample, jec, genWeights = None):
    '''
    calculate weights
    '''
    
    wrapper.branchArrays["run"][0] = event.run
    wrapper.branchArrays["luminosityBlock"][0] = event.lumi
    wrapper.branchArrays["event"][0] = event.event

    wrapper.branchArrays["is_e"][0] = event.nEle
    if "SingleMu" in sample:
        wrapper.branchArrays["trigger_e"][0] = 0
    else:
        wrapper.branchArrays["trigger_e"][0] = event.triggered_El

    wrapper.branchArrays["is_mu"][0] = event.nMu
    if "SingleEl" in sample or "EGamma" in sample:
        wrapper.branchArrays["trigger_mu"][0] = 0
    else:
        wrapper.branchArrays["trigger_mu"][0] = event.triggered_Mu

    isData = False
    if "SingleEl" in sample or "EGamma" in sample or "SingleMu" in sample:
        isData = True

    trigSF = 1.
    lepSF  = 1.
    if event.nEle == 1:
        #trigger = elTrigSFs.getSFs(event.Ele_Pt[0], event.Ele_EtaSC[0])
        idsf    = ele_evaluator["UL-Electron-ID-SF"].evaluate(
                    "2018", "sf", "Tight", 
                    event.Ele_EtaSC[0], event.Ele_Pt[0])
        recosf    = ele_evaluator["UL-Electron-ID-SF"].evaluate(
                    "2018", "sf", "RecoAbove20", 
                    event.Ele_EtaSC[0], event.Ele_Pt[0])

        #trigSF *= trigger.loc["central"]
        lepSF  *= idsf
        lepSF  *= recosf

    if event.nMu == 1:
        #trigger = muTrigSFs.getSFs(event.Mu_Pt[0], abs(event.Mu_Eta[0]))
        idsf    = muIDSFs.getSFs(  event.Mu_Pt[0], abs(event.Mu_Eta[0]))
        isosf   = muIsoSFs.getSFs( event.Mu_Pt[0], abs(event.Mu_Eta[0]))

        #trigSF *= trigger.loc["central"]
        lepSF  *= idsf.loc["central"]
        lepSF  *= isosf.loc["central"]


    if isData:
        wrapper.branchArrays["trigger_SF"][0] = -1.
    else:
        wrapper.branchArrays["trigger_SF"][0] = trigSF

    wrapper.branchArrays["flags"][0] = event.metFilter
    
    wrapper.branchArrays["nJets"][0] = event.nJets_nom
    wrapper.branchArrays["nBJets_deepJetM"][0] = event.nTagsM_nom

    wrapper.branchArrays["nPV"][0] = event.nPV
    
    if event.nLep == 1:
        wrapper.branchArrays["lepton_pt"][0] = event.Lep_Pt[0]
        wrapper.branchArrays["lepton_pt_uncorr"][0] = event.Lep_Pt[0]
        wrapper.branchArrays["lepton_eta"][0] = event.Lep_Eta[0]
        if event.nEle == 0:
            wrapper.branchArrays["lepton_deltaEtaSC"][0] = -1
        else:
            wrapper.branchArrays["lepton_deltaEtaSC"][0] = event.Ele_EtaSC[0]-event.Ele_Eta[0]
        wrapper.branchArrays["lepton_iso"][0] = event.Lep_iso[0]
        wrapper.branchArrays["lepton_abs_dxy"][0] = event.Lep_abs_dxy[0]
        wrapper.branchArrays["lepton_abs_dz"][0] = event.Lep_abs_dz[0]
        
        if isData:
            wrapper.branchArrays["lepton_SF"][0] = -1.
        else:
            wrapper.branchArrays["lepton_SF"][0] = lepSF


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
        wrapper.branchArrays["jet1_deepJet_shapeSF"][0] = -1
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
        wrapper.branchArrays["jet2_deepJet_shapeSF"][0] = -1


    if isData:
        wrapper.branchArrays["jet1_deepJet_shapeSF"][0] = -1.
        wrapper.branchArrays["jet2_deepJet_shapeSF"][0] = -1.
        wrapper.branchArrays["deepJet_shapeSF_weight"][0] = -1.
    else:
        btagSF = 1.
        for idx in range(event.nJets_nom):
            flav = flavTranslator[event.Jet_Flav_nom[idx]]
            sfs = btaggingSFs.getSFs(flav,
                abs(event.Jet_Eta_nom[idx]),
                event.Jet_Pt_nom[idx],
                event.Jet_btagValue_nom[idx],
                "nom")
            if not (flav == 1):
                sf = sfs.loc["central"]
            else:
                sf = 1.

            if idx == 0:
                wrapper.branchArrays["jet1_deepJet_shapeSF"][0] = sf

            if idx == 1:
                wrapper.branchArrays["jet2_deepJet_shapeSF"][0] = sf

            btagSF*=sf
                    
        wrapper.branchArrays["deepJet_shapeSF_weight"][0] = btagSF
    
    wrapper.branchArrays["MET_t1_pt"][0] = event.MET_T1_Pt_nom
    wrapper.branchArrays["MET_t1_phi"][0] = event.MET_T1_Phi_nom
    wrapper.branchArrays["MET_xy_pt"][0] = -1.
    wrapper.branchArrays["MET_xy_phi"][0] = -1.
    if isData:
        wrapper.branchArrays["MET_smeared_pt"][0] = -1. 
        wrapper.branchArrays["MET_smeared_phi"][0] = -1.
    else:
        wrapper.branchArrays["MET_smeared_pt"][0] = event.MET_T1Smear_Phi_nom
        wrapper.branchArrays["MET_smeared_phi"][0] = event.MET_T1Smear_Phi_nom

    if isData:
        wrapper.branchArrays["pu_nTrueInt"][0] = -1
        wrapper.branchArrays["pu_weight"][0] = -1.
    else:
        wrapper.branchArrays["pu_nTrueInt"][0] = event.nTruePU
        puSF = pileupSFs.getSF(event.nTruePU, "central")
        wrapper.branchArrays["pu_weight"][0] = puSF

    wrapper.branchArrays["L1_prefire_weight"][0] = 1.

    return event

