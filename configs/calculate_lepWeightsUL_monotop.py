import numpy as np
import common
import weightModules
from array import array
import os
from pprint import pprint
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
dataEra = "18"
sfDir = os.path.join(karimpath, "data", "UL_"+dataEra)

from correctionlib import _core


mudataEra = {
    "2016preVFP":   "2016_UL_HIPM",
    "2016postVFP":  "2016_UL",
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
    ele_evaluator = _core.CorrectionSet.from_file(os.path.join(sfDir, "electron.json"))
    data[dataEra]["electron"] = ele_evaluator["UL-Electron-ID-SF"]
    photon_evaluator = _core.CorrectionSet.from_file(os.path.join(sfDir, "photon.json"))
    data[dataEra]["photon"] = photon_evaluator["UL-Photon-ID-SF"]

    # muon ID scale factors
    muIDFile = "Efficiencies_muon_generalTracks_Z_Run{}_ID.csv".format(mudataEra[dataEra])
    data[dataEra]["muIDT"] = weightModules.LeptonSFs(
        csv     = os.path.join(sfDir, muIDFile),
        sfName  = "NUM_TightID_DEN_TrackerMuons_abseta_pt")
    data[dataEra]["muIDL"] = weightModules.LeptonSFs(
        csv     = os.path.join(sfDir, muIDFile),
        sfName  = "NUM_LooseID_DEN_TrackerMuons_abseta_pt")

    # muon Iso scale factors
    muISOFile = "Efficiencies_muon_generalTracks_Z_Run{}_ISO.csv".format(mudataEra[dataEra])
    data[dataEra]["muISOT"] = weightModules.LeptonSFs(
        csv     = os.path.join(sfDir, muISOFile),
        sfName  = "NUM_TightRelIso_DEN_TightIDandIPCut_abseta_pt")
    data[dataEra]["muISOL"] = weightModules.LeptonSFs(
        csv     = os.path.join(sfDir, muISOFile),
        sfName  = "NUM_LooseRelIso_DEN_LooseID_abseta_pt")

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

    # photon scale factors
    wrapper.SetFloatVar("phoEffSF_tight")
    wrapper.SetFloatVar("phoEffSF_tight_up")
    wrapper.SetFloatVar("phoEffSF_tight_down")

    wrapper.SetFloatVar("phoEffSF_loose")
    wrapper.SetFloatVar("phoEffSF_loose_up")
    wrapper.SetFloatVar("phoEffSF_loose_down")



def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "Evt_ID")
    wrapper.branchArrays["run"][0]   = getattr(event, "Evt_Run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "Evt_Lumi")
    
    # electron scale factors
    # tight electrons
    elIDSF_tight = 1.
    elIDSF_tight_up = 1.
    elIDSF_tight_down = 1.

    elRecoSF_tight = 1.
    elRecoSF_tight_up = 1.
    elRecoSF_tight_down = 1.

    for iEl in range(getattr(event, "N_TightElectrons")):
        # TODO super cluster eta
        if getattr(event, "TightElectron_Pt")[iEl] < 500:
            pt = getattr(event, "TightElectron_Pt")[iEl]
        else:
            pt = 499.
        idsf = data[dataEra]["electron"].evaluate(dataEra,"sf","Tight", getattr(event, "TightElectron_Eta")[iEl], pt)
        idsfErr = data[dataEra]["electron"].evaluate(dataEra,"syst","Tight", getattr(event, "TightElectron_Eta")[iEl], pt)

        recosf    = data[dataEra]["electron"].evaluate(dataEra,"sf","RecoAbove20", getattr(event, "TightElectron_Eta")[iEl], pt)
        recosfErr    = data[dataEra]["electron"].evaluate(dataEra,"syst","RecoAbove20", getattr(event, "TightElectron_Eta")[iEl], pt)

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

    # loose electrons
    elIDSF_loose = 1.
    elIDSF_loose_up = 1.
    elIDSF_loose_down = 1.

    elRecoSF_loose = 1.
    elRecoSF_loose_up = 1.
    elRecoSF_loose_down = 1.

    for iEl in range(getattr(event, "N_LooseElectrons")):
        # TODO super cluster eta
        if getattr(event, "LooseElectron_Pt")[iEl] < 500:
            pt = getattr(event, "LooseElectron_Pt")[iEl]
        else:
            pt = 499.
        idsf = data[dataEra]["electron"].evaluate(dataEra,"sf","Loose", getattr(event, "LooseElectron_Eta")[iEl], pt)
        idsfErr = data[dataEra]["electron"].evaluate(dataEra,"syst","Loose", getattr(event, "LooseElectron_Eta")[iEl], pt)

        if pt >= 20.:
            recosf    = data[dataEra]["electron"].evaluate(dataEra,"sf","RecoAbove20", getattr(event, "LooseElectron_Eta")[iEl], pt)
            recosfErr    = data[dataEra]["electron"].evaluate(dataEra,"syst","RecoAbove20", getattr(event, "LooseElectron_Eta")[iEl], pt)
        else:
            recosf    = data[dataEra]["electron"].evaluate(dataEra,"sf","RecoBelow20", getattr(event, "LooseElectron_Eta")[iEl], pt)
            recosfErr    = data[dataEra]["electron"].evaluate(dataEra,"syst","RecoBelow20", getattr(event, "LooseElectron_Eta")[iEl], pt)

        elIDSF_loose        *= idsf
        elIDSF_loose_up     *= (idsf + idsfErr)
        elIDSF_loose_down   *= (idsf - idsfErr)

        elRecoSF_loose      *= recosf
        elRecoSF_loose_up   *= (recosf + recosfErr)
        elRecoSF_loose_down *= (recosf - recosfErr)

    wrapper.branchArrays["eleIDSF_loose"][0]   = elIDSF_loose
    wrapper.branchArrays["eleIDSF_loose_up"][0]   = elIDSF_loose_up
    wrapper.branchArrays["eleIDSF_loose_down"][0]   = elIDSF_loose_down

    wrapper.branchArrays["eleRecoSF_loose"][0]   = elRecoSF_loose
    wrapper.branchArrays["eleRecoSF_loose_up"][0]   = elRecoSF_loose_up
    wrapper.branchArrays["eleRecoSF_loose_down"][0]   = elRecoSF_loose_down

    # # tight photons
    # phoEffSF_tight = 1.
    # phoEffSF_tight_up = 1.
    # phoEffSF_tight_down = 1.

    # for iPho in range(getattr(event, "N_TightPhotons")):
    #     if getattr(event, "TightPhoton_Pt")[iPho] < 500:
    #         pt = getattr(event, "TightPhoton_Pt")[iPho]
    #     else:
    #         pt = 499.
    #     sf = data[dataEra]["photon"].evaluate(dataEra,"sf","Tight", getattr(event, "TightPhoton_Eta")[iPho], pt)
    #     sfErr = data[dataEra]["photon"].evaluate(dataEra,"syst","Tight", getattr(event, "TightPhoton_Eta")[iPho], pt)

    #     phoEffSF_tight        *= sf
    #     phoEffSF_tight_up     *= (sf + sfErr)
    #     phoEffSF_tight_down   *= (sf - sfErr)

    # wrapper.branchArrays["phoEffSF_tight"][0]   = phoEffSF_tight
    # wrapper.branchArrays["phoEffSF_tight_up"][0]   = phoEffSF_tight_up
    # wrapper.branchArrays["phoEffSF_tight_down"][0]   = phoEffSF_tight_down

    # # loose photons
    # phoEffSF_loose = 1.
    # phoEffSF_loose_up = 1.
    # phoEffSF_loose_down = 1.

    # for iPho in range(getattr(event, "N_LoosePhotons")):
    #     # TODO super cluster eta
    #     if getattr(event, "TightPhoton_Pt")[iPho] < 500:
    #         pt = getattr(event, "TightPhoton_Pt")[iPho]
    #     else:
    #         pt = 499.
    #     pt = getattr(event, "LoosePhoton_Pt")[iPho]
    #     sf = data[dataEra]["photon"].evaluate(dataEra,"sf","Loose", getattr(event, "LoosePhoton_Eta")[iPho], pt)
    #     sfErr = data[dataEra]["photon"].evaluate(dataEra,"syst","Loose", getattr(event, "LoosePhoton_Eta")[iPho], pt)
    #     print("########")
    #     print(sf)
    #     print("########")
    #     phoEffSF_loose        *= sf
    #     phoEffSF_loose_up     *= (sf + sfErr)
    #     phoEffSF_loose_down   *= (sf - sfErr)

    # wrapper.branchArrays["phoEffSF_loose"][0]   = phoEffSF_loose
    # wrapper.branchArrays["phoEffSF_loose_up"][0]   = phoEffSF_loose_up
    # wrapper.branchArrays["phoEffSF_loose_down"][0]   = phoEffSF_loose_down
            
    # tight muons
    muIDSF_tight = 1.
    muIDSF_tight_up = 1.
    muIDSF_tight_down = 1.

    muIsoSF_tight = 1.
    muIsoSF_tight_up = 1.
    muIsoSF_tight_down = 1.

    for iMu in range(getattr(event, "N_TightMuons")):
        idsf    = data[dataEra]["muIDT"].getSFs(  getattr(event, "TightMuon_Pt")[iMu], abs(getattr(event, "TightMuon_Eta")[iMu]))
        isosf   = data[dataEra]["muISOT"].getSFs( getattr(event, "TightMuon_Pt")[iMu], abs(getattr(event, "TightMuon_Eta")[iMu]))

        muIDSF_tight        *= idsf.loc["central"]
        muIDSF_tight_up     *= idsf.loc["up"]
        muIDSF_tight_down   *= idsf.loc["down"]

        muIsoSF_tight       *= isosf.loc["central"]
        muIsoSF_tight_up    *= isosf.loc["up"]
        muIsoSF_tight_down  *= isosf.loc["down"]

    wrapper.branchArrays["muIDSF_tight"][0]   = muIDSF_tight
    wrapper.branchArrays["muIDSF_tight_up"][0]   = muIDSF_tight_up
    wrapper.branchArrays["muIDSF_tight_down"][0]   = muIDSF_tight_down
    wrapper.branchArrays["muIsoSF_tight"][0]  = muIsoSF_tight
    wrapper.branchArrays["muIsoSF_tight_up"][0]  = muIsoSF_tight_up
    wrapper.branchArrays["muIsoSF_tight_down"][0]  = muIsoSF_tight_down

    # loose muons
    muIDSF_loose = 1.
    muIDSF_loose_up = 1.
    muIDSF_loose_down = 1.
    
    muIsoSF_loose = 1.
    muIsoSF_loose_up = 1.
    muIsoSF_loose_down = 1.

    for iMu in range(getattr(event, "N_LooseMuons")):
        idsf    = data[dataEra]["muIDL"].getSFs(  getattr(event, "LooseMuon_Pt")[iMu], abs(getattr(event, "LooseMuon_Eta")[iMu]))
        isosf   = data[dataEra]["muISOL"].getSFs( getattr(event, "LooseMuon_Pt")[iMu], abs(getattr(event, "LooseMuon_Eta")[iMu]))

        muIDSF_loose        *= idsf.loc["central"]
        muIDSF_loose_up     *= idsf.loc["up"]
        muIDSF_loose_down   *= idsf.loc["down"]

        muIsoSF_loose       *= isosf.loc["central"]
        muIsoSF_loose_up    *= isosf.loc["up"]
        muIsoSF_loose_down  *= isosf.loc["down"]

    wrapper.branchArrays["muIDSF_loose"][0]   = muIDSF_loose
    wrapper.branchArrays["muIDSF_loose_up"][0]   = muIDSF_loose_up
    wrapper.branchArrays["muIDSF_loose_down"][0]   = muIDSF_loose_down
    wrapper.branchArrays["muIsoSF_loose"][0]  = muIsoSF_loose
    wrapper.branchArrays["muIsoSF_loose_up"][0]  = muIsoSF_loose_up
    wrapper.branchArrays["muIsoSF_loose_down"][0]  = muIsoSF_loose_down

    return event

