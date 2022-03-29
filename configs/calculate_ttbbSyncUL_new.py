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
ltagSF = {}
btagSFold = {}
ltagSFold = {}
btagEff = {}
for year in ["2017"]:#["2018", "2017", "2016preVFP", "2016postVFP"]:
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
        btagSF[year]   = btagSFjson["deepJet_comb"]
        ltagSF[year]   = btagSFjson["deepJet_incl"]
        itFit[year]    = btagSFjson["deepJet_shape"]

        btagSFjsonold = _core.CorrectionSet.from_file(
            os.path.join(sfDir, "btagging.json"))
        print(os.path.join(sfDir, "btagging.json"))
        btagSFold[year]   = btagSFjsonold["deepJet_wp"]

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
    wrapper.SetFloatVar("btag_weight_fixWP_MT_og")
    wrapper.SetFloatVar("btag_weight_fixWP_MT_alt")
    wrapper.SetFloatVar("btag_weight_itFit")

    wrapper.SetFloatVar("pu_nTrueInt")
    wrapper.SetFloatVar("pu_weight")
    
    wrapper.SetFloatVar("L1_prefire_weight")


def calculate_variables(event, wrapper, sample, jec, dataEra, genWeights = None):
    '''
    calculate weights
    '''
    
    wrapper.branchArrays["run"][0] = event.run
    wrapper.branchArrays["luminosityBlock"][0] = event.luminosityBlock
    wrapper.branchArrays["event"][0] = event.event

    if event.nEle == 1 and event.nvetoLep == 1:
        wrapper.branchArrays["is_e"][0] = 1
        if "SingleMu" in sample:
            wrapper.branchArrays["trigger_e"][0] = 0
        else:
            wrapper.branchArrays["trigger_e"][0] = event.isTriggeredEl
    else:
        wrapper.branchArrays["is_e"][0] = 0
        wrapper.branchArrays["trigger_e"][0] = 0

    if event.nMu == 1 and event.nvetoLep == 1:
        wrapper.branchArrays["is_mu"][0] = 1
        if "SingleEl" in sample or "EGamma" in sample:
            wrapper.branchArrays["trigger_mu"][0] = 0
        else:
            wrapper.branchArrays["trigger_mu"][0] = event.isTriggeredMu
    else:
        wrapper.branchArrays["is_mu"][0] = 0
        wrapper.branchArrays["trigger_mu"][0] = 0

    isData = False
    if "SingleEl" in sample or "EGamma" in sample or "SingleMu" in sample:
        isData = True

    if not isData:
        trigSF = 1.
        lepSF  = 1.
        
        if event.nEle == 1 and event.nvetoLep == 1:
            lepSF  *= data[dataEra]["electron"].evaluate(
                        dataEra,"sf","Tight", event.Ele_etaSC[0], event.Ele_pt[0])
            lepSF  *= data[dataEra]["electron"].evaluate(
                        dataEra,"sf","RecoAbove20", event.Ele_etaSC[0], event.Ele_pt[0])
            trigSF *= data[dataEra]["eleTrig"].evaluate("central", event.Ele_pt[0], event.Ele_etaSC[0])
            if dataEra == "2017": trigSF *= 0.991 # HLT zvtx correction


        if event.nMu == 1 and event.nvetoLep == 1:
            trigSF *= data[dataEra]["muTrig"].evaluate(
                        dataEra+"_UL", abs(event.Mu_eta[0]), event.Mu_pt[0], "sf")
            lepSF  *= data[dataEra]["muID"].evaluate( 
                        dataEra+"_UL", abs(event.Mu_eta[0]), event.Mu_pt[0], "sf")
            lepSF  *= data[dataEra]["muISO"].evaluate(
                        dataEra+"_UL", abs(event.Mu_eta[0]), event.Mu_pt[0], "sf")
        
    if isData:
        wrapper.branchArrays["trigger_SF"][0] = -1.
        wrapper.branchArrays["lepton_SF"][0] = -1.
    else:
        wrapper.branchArrays["trigger_SF"][0] = trigSF
        wrapper.branchArrays["lepton_SF"][0] = lepSF
        

    wrapper.branchArrays["flags"][0] = event.metFilter
    
    wrapper.branchArrays["nJets"][0] = event.nJets_nominal
    wrapper.branchArrays["nBJets_deepJetM"][0] = event.nTagsM_nominal

    
    if event.nLep == 1:
        wrapper.branchArrays["lepton_pt"][0]  = event.Lep_pt[0]
        wrapper.branchArrays["lepton_eta"][0] = event.Lep_eta[0]
        wrapper.branchArrays["lepton_phi"][0] = event.Lep_phi[0]
        if event.nEle == 1:
            wrapper.branchArrays["lepton_deltaEtaSC"][0] = event.Ele_etaSC[0]-event.Ele_eta[0]
            #wrapper.branchArrays["lepton_pt_uncorr"][0]  = event.Ele_Pt_uncorr[0]
            wrapper.branchArrays["lepton_pt_uncorr"][0]  = -1
        else:
            wrapper.branchArrays["lepton_deltaEtaSC"][0] = -1
            wrapper.branchArrays["lepton_pt_uncorr"][0]  = -1
        wrapper.branchArrays["lepton_iso"][0]     = event.Lep_iso[0]
        wrapper.branchArrays["lepton_abs_dxy"][0] = abs(event.Lep_dxy[0])
        wrapper.branchArrays["lepton_abs_dz"][0]  = abs(event.Lep_dz[0])
        
    if event.nJets_nominal > 0:
        wrapper.branchArrays["jet1_pt"][0] = event.Jets_pt_nominal[0]
        #wrapper.branchArrays["jet1_pt"][0] = event.Jets_Pt_raw_nom[0]
        wrapper.branchArrays["jet1_eta"][0] = event.Jets_eta_nominal[0]
        wrapper.branchArrays["jet1_phi"][0] = event.Jets_phi_nominal[0]
        wrapper.branchArrays["jet1_deepJet"][0] = event.Jets_btagDeepFlavB_nominal[0]
    else:
        wrapper.branchArrays["jet1_pt"][0] = -1
        wrapper.branchArrays["jet1_eta"][0] = -1
        wrapper.branchArrays["jet1_phi"][0] = -1
        wrapper.branchArrays["jet1_deepJet"][0] = -1
        #wrapper.branchArrays["jet1_deepJet_shapeSF"][0] = -1
    if event.nJets_nominal > 1:
        wrapper.branchArrays["jet2_pt"][0] = event.Jets_pt_nominal[1]
        #wrapper.branchArrays["jet2_pt"][0] = event.Jets_Pt_raw_nom[1]
        wrapper.branchArrays["jet2_eta"][0] = event.Jets_eta_nominal[1]
        wrapper.branchArrays["jet2_phi"][0] = event.Jets_phi_nominal[1]
        wrapper.branchArrays["jet2_deepJet"][0] = event.Jets_btagDeepFlavB_nominal[1]
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
        jetSFs = []
        shapeSF   = 1.
        ts = []
        ms = []
        te = []
        me = []
        for idx in range(event.nJets_nominal):
            eta   = getattr(event, "Jets_eta_nominal")[idx]
            abseta=abs(eta)
            pt    = getattr(event, "Jets_pt_nominal")[idx]
            flav  = getattr(event, "Jets_hadronFlavour_nominal")[idx]
            passes_M = getattr(event, "Jets_taggedM_nominal")[idx]
            passes_T = getattr(event, "Jets_taggedT_nominal")[idx]

            eff_M = btagEff[dataEra].evaluate("M", flav, eta, pt)
            eff_T = btagEff[dataEra].evaluate("T", flav, eta, pt)

            if flav == 0:
                sf_M = btagSFold[dataEra].evaluate("central", "incl", "M", flav, abseta, pt)
                sf_T = btagSFold[dataEra].evaluate("central", "incl", "T", flav, abseta, pt)
            else:
                sf_M = btagSFold[dataEra].evaluate("central", "comb", "M", flav, abseta, pt)
                sf_T = btagSFold[dataEra].evaluate("central", "comb", "T", flav, abseta, pt)

            if passes_T:
                jetSFs.append(sf_T)
                P_MC_TM   *= eff_T
                P_DATA_TM *= eff_T*sf_T
            elif passes_M:
                jetSFs.append( (sf_M*eff_M - sf_T*eff_T)/(eff_M-eff_T) )
                P_MC_TM   *= (eff_M      - eff_T)
                P_DATA_TM *= (eff_M*sf_M - eff_T*sf_T)
            else:
                jetSFs.append( (1.-sf_M*eff_M)/(1.-eff_M) )
                P_MC_TM   *= (1. - eff_M)
                P_DATA_TM *= (1. - eff_M*sf_M)

            ts.append(sf_T)
            ms.append(sf_M)
            te.append(eff_T)
            me.append(eff_M)
            # itFit
            shapeSF *= itFit[dataEra].evaluate(
                "central", flav, abseta, pt, event.Jets_btagDeepFlavB_nominal[idx])
        finalSF = 1.
        for s in jetSFs: finalSF*=s
        if event.event in [608, 8328, 9619, 10298, 11357, 14281]:
            print("eta", [event.Jets_eta_nominal[i] for i in range(event.nJets_nominal)])
            print("pt", [event.Jets_pt_nominal[i] for i in range(event.nJets_nominal)])
            print("flav", [event.Jets_hadronFlavour_nominal[i] for i in range(event.nJets_nominal)])
            print("isM", [event.Jets_taggedM_nominal[i] for i in range(event.nJets_nominal)])
            print("isT", [event.Jets_taggedT_nominal[i] for i in range(event.nJets_nominal)])
            print(event.event, event.nTagsM_nominal, event.nTagsT_nominal)
            print("sfT", ts)
            print("sfM", ms)
            print("effT", te)
            print("effM", me)
            print("jetSFs", jetSFs)
            print("SF", finalSF)
        wrapper.branchArrays["btag_weight_fixWP_MT_og"][0] = finalSF
        wrapper.branchArrays["btag_weight_fixWP_MT"][0] = P_DATA_TM/P_MC_TM
        diff= finalSF-(P_DATA_TM/P_MC_TM)
        if diff > 1e-10: print(diff)
        wrapper.branchArrays["btag_weight_itFit"][0] = shapeSF

        jetSF = 1.
        for idx in range(event.nJets_nominal):
            if event.Jets_taggedT_nominal[idx]:
                if event.Jets_hadronFlavour_nominal[idx] == 0:
                    sfT = ltagSF[dataEra].evaluate("central", "T",
                        event.Jets_hadronFlavour_nominal[idx], abs(event.Jets_eta_nominal[idx]), event.Jets_pt_nominal[idx])
                else:
                    sfT = btagSF[dataEra].evaluate("central", "T",
                        event.Jets_hadronFlavour_nominal[idx], abs(event.Jets_eta_nominal[idx]), event.Jets_pt_nominal[idx])

                jetSF *= sfT

            elif event.Jets_taggedM_nominal[idx]:
                effT = btagEff[dataEra].evaluate("T", 
                    event.Jets_hadronFlavour_nominal[idx], event.Jets_eta_nominal[idx], event.Jets_pt_nominal[idx])
                effM = btagEff[dataEra].evaluate("M", 
                    event.Jets_hadronFlavour_nominal[idx], event.Jets_eta_nominal[idx], event.Jets_pt_nominal[idx])
                if event.Jets_hadronFlavour_nominal[idx] == 0:
                    sfT = ltagSF[dataEra].evaluate("central", "T",
                        event.Jets_hadronFlavour_nominal[idx], abs(event.Jets_eta_nominal[idx]), event.Jets_pt_nominal[idx])
                    sfM = ltagSF[dataEra].evaluate("central", "M",
                        event.Jets_hadronFlavour_nominal[idx], abs(event.Jets_eta_nominal[idx]), event.Jets_pt_nominal[idx])
                else:
                    sfT = btagSF[dataEra].evaluate("central", "T",
                        event.Jets_hadronFlavour_nominal[idx], abs(event.Jets_eta_nominal[idx]), event.Jets_pt_nominal[idx])
                    sfM = btagSF[dataEra].evaluate("central", "M",
                        event.Jets_hadronFlavour_nominal[idx], abs(event.Jets_eta_nominal[idx]), event.Jets_pt_nominal[idx])

                jetSF *= ((sfM*effM - sfT*effT)/(effM - effT))

            else:
                effM = btagEff[dataEra].evaluate("M", 
                    event.Jets_hadronFlavour_nominal[idx], event.Jets_eta_nominal[idx], event.Jets_pt_nominal[idx])
    
                if event.Jets_hadronFlavour_nominal[idx] == 0:
                    sfM = ltagSF[dataEra].evaluate("central", "M",
                        event.Jets_hadronFlavour_nominal[idx], abs(event.Jets_eta_nominal[idx]), event.Jets_pt_nominal[idx])
                else:
                    sfM = btagSF[dataEra].evaluate("central", "M",
                        event.Jets_hadronFlavour_nominal[idx], abs(event.Jets_eta_nominal[idx]), event.Jets_pt_nominal[idx])

                jetSF *= ((1. - sfM*effM)/(1. - effM))

        wrapper.branchArrays["btag_weight_fixWP_MT_alt"][0] = jetSF

    wrapper.branchArrays["nPV"][0] = event.nPV
    if isData:
        wrapper.branchArrays["pu_nTrueInt"][0] = -1
        wrapper.branchArrays["pu_weight"][0] = -1.
    else:
        wrapper.branchArrays["pu_nTrueInt"][0] = event.nTruePU
        pu = data[dataEra]["pu"].evaluate(event.nTruePU, "nominal")
        wrapper.branchArrays["pu_weight"][0] = pu

    if isData:
        wrapper.branchArrays["L1_prefire_weight"][0] = -1
    elif dataEra == "2018":
        wrapper.branchArrays["L1_prefire_weight"][0] = 1.
    else:
        wrapper.branchArrays["L1_prefire_weight"][0] = event.prefireWeight
    return event

