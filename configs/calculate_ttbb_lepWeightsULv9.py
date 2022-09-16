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

puName = {
    "2016preVFP":   "Collisions16_UltraLegacy_goldenJSON",
    "2016postVFP":  "Collisions16_UltraLegacy_goldenJSON",
    "2017":         "Collisions17_UltraLegacy_goldenJSON",
    "2018":         "Collisions18_UltraLegacy_goldenJSON",
    }

puSF = {}
for year in ["2016preVFP", "2016postVFP", "2017", "2018"]:
    # initialize pileup SFs
    pu_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "LUM", year+"_UL", "puWeights.json.gz"))
    puSF[year] = pu_evaluator[puName[year]]

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
        #os.path.join(sfDir, "EleTriggerSF_NanoAODv2_v0.json"))
        os.path.join(sfDir, "EleTriggerSF_NanoAODv9_v0.json"))
    data[year]["eleTrig"] = eleTrigFile["EleTriggerSF"]

    # electron ID/RECO
    ele_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "EGM", year+"_UL", "electron.json.gz"))
    data[year]["electron"] = ele_evaluator["UL-Electron-ID-SF"]

    # muon Trig/ID/ISO
    mu_evaluator = _core.CorrectionSet.from_file(
        os.path.join(jsonDir, "MUO", year+"_UL", "muon_Z.json.gz"))
    data[year]["muTrig"] = mu_evaluator[muTrigName[year]]
    data[year]["muReco"] = mu_evaluator["NUM_TrackerMuons_DEN_genTracks"]
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
    wrapper.SetFloatVar("muRecoSF")
    wrapper.SetFloatVar("muRecoSF_up_rel")
    wrapper.SetFloatVar("muRecoSF_down_rel")
    wrapper.SetFloatVar("elRecoSF")
    wrapper.SetFloatVar("elRecoSF_up_rel")
    wrapper.SetFloatVar("elRecoSF_down_rel")

    wrapper.SetFloatVar("pileup")
    wrapper.SetFloatVar("pileup_up_rel")
    wrapper.SetFloatVar("pileup_down_rel")

    wrapper.SetFloatVar("pdf_up")
    wrapper.SetFloatVar("pdf_up_rel")
    wrapper.SetFloatVar("pdf_down")
    wrapper.SetFloatVar("pdf_down_rel")

    wrapper.SetFloatVar("pdf_up_rel_noAS")
    wrapper.SetFloatVar("pdf_up_rel_AS")
    wrapper.SetFloatVar("pdf_down_rel_noAS")
    wrapper.SetFloatVar("pdf_down_rel_AS")

    wrapper.SetFloatVar("muR_up")
    wrapper.SetFloatVar("muR_down")
    wrapper.SetFloatVar("muF_up")
    wrapper.SetFloatVar("muF_down")

    wrapper.SetFloatVar("isr_up")
    wrapper.SetFloatVar("isr_down")
    wrapper.SetFloatVar("fsr_up")
    wrapper.SetFloatVar("fsr_down")
    

def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    if sample.startswith("TTJets"):
        wrapper.branchArrays["muR_down"][0] = event.LHEScaleWeights[1]*2
        wrapper.branchArrays["muR_up"][0] = event.LHEScaleWeights[7]*2
        wrapper.branchArrays["muF_down"][0] = event.LHEScaleWeights[3]*2
        wrapper.branchArrays["muF_up"][0] = event.LHEScaleWeights[5]*2
        wrapper.branchArrays["isr_down"][0] = event.psWeights[24]
        wrapper.branchArrays["isr_up"][0] = event.psWeights[25]
        wrapper.branchArrays["fsr_down"][0] = event.psWeights[2]
        wrapper.branchArrays["fsr_up"][0] = event.psWeights[3]
    elif sample.startswith("TT_TuneCH3"):
        wrapper.branchArrays["muR_down"][0] = event.LHEScaleWeights[1]
        wrapper.branchArrays["muR_up"][0] = event.LHEScaleWeights[7]
        wrapper.branchArrays["muF_down"][0] = event.LHEScaleWeights[3]
        wrapper.branchArrays["muF_up"][0] = event.LHEScaleWeights[5]
        # TODO: weights seem broken
        #print(event.psWeights)
        wrapper.branchArrays["isr_down"][0] = 1
        wrapper.branchArrays["isr_up"][0] = 1
        wrapper.branchArrays["fsr_down"][0] = 1
        wrapper.branchArrays["fsr_up"][0] = 1
    elif sample.startswith("ttbb_4FS"):
        wrapper.branchArrays["muR_down"][0] = event.LHEScaleWeights[1]
        wrapper.branchArrays["muR_up"][0] = event.LHEScaleWeights[7]
        wrapper.branchArrays["muF_down"][0] = event.LHEScaleWeights[3]
        wrapper.branchArrays["muF_up"][0] = event.LHEScaleWeights[5]
        wrapper.branchArrays["isr_down"][0] = event.psWeights[24]
        wrapper.branchArrays["isr_up"][0] = event.psWeights[25]
        wrapper.branchArrays["fsr_down"][0] = event.psWeights[2]
        wrapper.branchArrays["fsr_up"][0] = event.psWeights[3]
    elif sample.startswith("TTTo") or sample.startswith("TTbb"):
        wrapper.branchArrays["muR_down"][0] = event.LHEScaleWeights[1]
        wrapper.branchArrays["muR_up"][0] = event.LHEScaleWeights[7]
        wrapper.branchArrays["muF_down"][0] = event.LHEScaleWeights[3]
        wrapper.branchArrays["muF_up"][0] = event.LHEScaleWeights[5]
        wrapper.branchArrays["isr_down"][0] = event.psWeights[24]
        wrapper.branchArrays["isr_up"][0] = event.psWeights[25]
        wrapper.branchArrays["fsr_down"][0] = event.psWeights[2]
        wrapper.branchArrays["fsr_up"][0] = event.psWeights[3]
    else:
        wrapper.branchArrays["muR_down"][0] = event.LHEScaleWeights[1]
        wrapper.branchArrays["muR_up"][0] = event.LHEScaleWeights[7]
        wrapper.branchArrays["muF_down"][0] = event.LHEScaleWeights[3]
        wrapper.branchArrays["muF_up"][0] = event.LHEScaleWeights[5]
        wrapper.branchArrays["isr_down"][0] = event.psWeights[2]
        wrapper.branchArrays["isr_up"][0] = event.psWeights[0]
        wrapper.branchArrays["fsr_down"][0] = event.psWeights[3]
        wrapper.branchArrays["fsr_up"][0] = event.psWeights[1]
        

    try:
        nom_pdf = event.Weight_pdf[0]
        weights = np.array([event.Weight_pdf[i+1] for i in range(len(event.Weight_pdf)-1)])
        if sample.startswith("TTJets"):
            weights *= 2

        if sample.startswith("TTbb"):
            residuals = weights-np.mean(weights)
            variation = (residuals)**2
            variation = sum(variation)/(len(variation)-1)
            
        else:
            residuals = weights-nom_pdf
            variation = (residuals)**2
            variation = sum(variation)

        variation = np.sqrt(variation)
        wrapper.branchArrays["pdf_up"][0]       =  nom_pdf+variation
        wrapper.branchArrays["pdf_up_rel"][0]   = (nom_pdf+variation)/nom_pdf
        wrapper.branchArrays["pdf_down"][0]     =  nom_pdf-variation
        wrapper.branchArrays["pdf_down_rel"][0] = (nom_pdf-variation)/nom_pdf

        if not sample.startswith("TTbb") and len(weights) == 102:
            weights_noAS = weights[:-2]
            residuals_noAS = weights_noAS - nom_pdf
            variation_noAS = (residuals_noAS)**2
            variation_noAS = sum(variation_noAS)

            wrapper.branchArrays["pdf_up_rel_noAS"][0] = (nom_pdf+variation_noAS)/nom_pdf
            wrapper.branchArrays["pdf_up_rel_AS"][0] = weights[-2]
            wrapper.branchArrays["pdf_down_rel_noAS"][0] = (nom_pdf-variation_noAS)/nom_pdf
            wrapper.branchArrays["pdf_down_rel_AS"][0] = weights[-1]
        else:
            wrapper.branchArrays["pdf_up_rel_noAS"][0] = (nom_pdf+variation)/nom_pdf
            wrapper.branchArrays["pdf_up_rel_AS"][0] = 1.
            wrapper.branchArrays["pdf_down_rel_noAS"][0] = (nom_pdf-variation)/nom_pdf
            wrapper.branchArrays["pdf_down_rel_AS"][0] = 1.

    except: pass

    if sample.startswith("TTJets") or sample.startswith("TT_TuneCH3") or sample.startswith("ttbb_4FS"): return 

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "luminosityBlock")
    
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
                            event.Ele_etaSC[iEl], event.Ele_pt[iEl])
        elIDSF_up     *= data[dataEra]["electron"].evaluate(dataEra, "sfup","Tight", 
                            event.Ele_etaSC[iEl], event.Ele_pt[iEl])
        elIDSF_down   *= data[dataEra]["electron"].evaluate(dataEra, "sfdown","Tight", 
                            event.Ele_etaSC[iEl], event.Ele_pt[iEl])
        elRecoSF      *= data[dataEra]["electron"].evaluate(dataEra, "sf","RecoAbove20", 
                            event.Ele_etaSC[iEl], event.Ele_pt[iEl])
        elRecoSF_up   *= data[dataEra]["electron"].evaluate(dataEra, "sfup","RecoAbove20", 
                            event.Ele_etaSC[iEl], event.Ele_pt[iEl])
        elRecoSF_down *= data[dataEra]["electron"].evaluate(dataEra, "sfdown","RecoAbove20", 
                            event.Ele_etaSC[iEl], event.Ele_pt[iEl])

        elTrigSF      *= data[dataEra]["eleTrig"].evaluate("central", 
                            event.Ele_pt[iEl], event.Ele_etaSC[iEl])
        elTrigSF_up   *= data[dataEra]["eleTrig"].evaluate("up", 
                            event.Ele_pt[iEl], event.Ele_etaSC[iEl])
        elTrigSF_down *= data[dataEra]["eleTrig"].evaluate("down", 
                            event.Ele_pt[iEl], event.Ele_etaSC[iEl])
            
    # apply HLT zvtx correction
    if dataEra == "2017":
        elTrigSF      *= 0.991
        elTrigSF_up   *= 0.991
        elTrigSF_down *= 0.991

    wrapper.branchArrays["elTrigSF"][0] = elTrigSF
    wrapper.branchArrays["elIDSF"][0]   = elIDSF
    wrapper.branchArrays["elRecoSF"][0] = elRecoSF

    # relative SFs only when exactly one electron is present
    if event.nEle == 1 and event.nvetoLep == 1:
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

    muRecoSF = 1.
    muRecoSF_up = 1.
    muRecoSF_down = 1.

    for iMu in range(event.nMu):
        muIDSF       *= data[dataEra]["muID"].evaluate(
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "sf")
        muIDSF_up    *= data[dataEra]["muID"].evaluate(  
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "systup")
        muIDSF_down  *= data[dataEra]["muID"].evaluate(  
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "systdown")
        muIsoSF      *= data[dataEra]["muISO"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "sf")
        muIsoSF_up   *= data[dataEra]["muISO"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "systup")
        muIsoSF_down *= data[dataEra]["muISO"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "systdown")
        muRecoSF      *= data[dataEra]["muReco"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "sf")
        muRecoSF_up   *= data[dataEra]["muReco"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "systup")
        muRecoSF_down *= data[dataEra]["muReco"].evaluate( 
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), event.Mu_pt[iMu], "systdown")

        muTrigSF      *= data[dataEra]["muTrig"].evaluate(
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), max(29.,event.Mu_pt[iMu]), "sf")
        muTrigSF_up   *= data[dataEra]["muTrig"].evaluate(
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), max(29.,event.Mu_pt[iMu]), "systup")
        muTrigSF_down *= data[dataEra]["muTrig"].evaluate(
                            dataEra+"_UL", abs(event.Mu_eta[iMu]), max(29.,event.Mu_pt[iMu]), "systdown")
        

    wrapper.branchArrays["muTrigSF"][0] = muTrigSF
    wrapper.branchArrays["muIDSF"][0]   = muIDSF
    wrapper.branchArrays["muIsoSF"][0]  = muIsoSF
    wrapper.branchArrays["muRecoSF"][0]  = muRecoSF

    # relative SFs only when exactly one muon is present
    if event.nMu == 1 and event.nvetoLep == 1:
        wrapper.branchArrays["muTrigSF_up_rel"][0]   = muTrigSF_up/muTrigSF
        wrapper.branchArrays["muTrigSF_down_rel"][0] = muTrigSF_down/muTrigSF
            
        wrapper.branchArrays["muIDSF_up_rel"][0]     = muIDSF_up/muIDSF
        wrapper.branchArrays["muIDSF_down_rel"][0]   = muIDSF_down/muIDSF
           
        wrapper.branchArrays["muIsoSF_up_rel"][0]    = muIsoSF_up/muIsoSF
        wrapper.branchArrays["muIsoSF_down_rel"][0]  = muIsoSF_down/muIsoSF
           
        wrapper.branchArrays["muRecoSF_up_rel"][0]    = muRecoSF_up/muRecoSF
        wrapper.branchArrays["muRecoSF_down_rel"][0]  = muRecoSF_down/muRecoSF
    else:
        wrapper.branchArrays["muTrigSF_up_rel"][0]   = 1.
        wrapper.branchArrays["muTrigSF_down_rel"][0] = 1.

        wrapper.branchArrays["muIDSF_up_rel"][0]     = 1.
        wrapper.branchArrays["muIDSF_down_rel"][0]   = 1.
           
        wrapper.branchArrays["muIsoSF_up_rel"][0]    = 1.
        wrapper.branchArrays["muIsoSF_down_rel"][0]  = 1.

        wrapper.branchArrays["muRecoSF_up_rel"][0]    = 1.
        wrapper.branchArrays["muRecoSF_down_rel"][0]  = 1.

    pu = puSF[dataEra].evaluate(float(event.nTruePU), "nominal")
    wrapper.branchArrays["pileup"][0] = pu
    wrapper.branchArrays["pileup_up_rel"][0] = puSF[dataEra].evaluate(float(event.nTruePU), "up")/pu
    wrapper.branchArrays["pileup_down_rel"][0] = puSF[dataEra].evaluate(float(event.nTruePU), "down")/pu



    return event

    
