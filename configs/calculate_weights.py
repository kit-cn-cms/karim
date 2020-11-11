import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
sfDir = os.path.join(karimpath, "data", "legacy_2017")

# initialize rate factor buisness
rateFactors = weightModules.RateFactors(os.path.join(sfDir, "ratefactors_2017.csv"))

# initialize iterative fit b-tagging sfs
btaggingSFs = weightModules.BTaggingScaleFactors(os.path.join(sfDir, "btaggingSF_deepJet_2017.csv"))
uncs = [
    "hfstats2",
    "hfstats1",
    "lfstats2",
    "lfstats1",
    "cferr2",
    "cferr1",
    "hf",
    "lf"
    ]
btagSF_uncs = ["up_"+u   for u in uncs] + \
              ["down_"+u for u in uncs]
btaggingSFs.removeUnusedSys(keep =
    ["central"] + btagSF_uncs)

# initialize b-tagging SF correction
sfPatch = weightModules.SFPatches(os.path.join(sfDir, "btaggingSF_patches_2017.csv"))

# initialize lepton trigger scale factors
elTrigSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "electron_triggerSF_2017.csv"), 
    sfName  = "ele28_ht150_OR_ele32_ele_pt_ele_sceta")
muTrigSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "muon_triggerSF_2017.csv"),
    sfName  = "IsoMu27_PtEtaBins")

# initialize lepton ID scale factors
elIDSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "electron_idSF_2017.csv"),
    sfName  = "tightElectronID")
muIDSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "muon_idSF_2017.csv"),
    sfName  = "NUM_TightID_DEN_genTracks_pt_abseta")

# initialize lepton Reco/Iso scale factors
elRecoSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "electron_recoSF_2017.csv"),
    sfName  = "electronReco")
muIsoSFs  = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "muon_isoSF_2017.csv"),
    sfName  = "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta")

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "Evt_Odd",
        "N_Jets",
        "N_BTagsM",
        "Evt_ID",
        "Evt_Run",
        "Evt_Lumi"
        "GenEvt_I_TTPlusBB",
        "GenEvt_I_TTPlusCC",
        
        "Jet_Pt",
        "Jet_Eta",
        "Jet_Phi",
        "Jet_M",
        "Jet_E",
        "Jet_Flav",
        ]
    return variables

def base_selection(event):
    return event.N_Jets>=2

def set_branches(wrapper):
    wrapper.SetIntVar("Evt_ID")   
    wrapper.SetIntVar("Evt_Run")   
    wrapper.SetIntVar("Evt_Lumi")   
    wrapper.SetIntVar("GenEvt_I_TTPlusBB")   
    wrapper.SetIntVar("GenEvt_I_TTPlusCC")   
    wrapper.SetIntVar("N_Jets")   
    wrapper.SetIntVar("N_BTagsM")

    # rate factors
    wrapper.SetFloatVar("muR_up_rel_wRF")
    wrapper.SetFloatVar("muF_up_rel_wRF")
    wrapper.SetFloatVar("muR_down_rel_wRF")
    wrapper.SetFloatVar("muF_down_rel_wRF")

    wrapper.SetFloatVar("isr_up_rel_wRF")
    wrapper.SetFloatVar("fsr_up_rel_wRF")
    wrapper.SetFloatVar("isr_down_rel_wRF")
    wrapper.SetFloatVar("fsr_down_rel_wRF")

    # b tagging
    wrapper.SetFloatVarArray("Jet_btagSF", "N_Jets")
    wrapper.SetFloatVar("btagSF")
    
    # iterative fit uncertainties
    for unc in btagSF_uncs:
        wrapper.SetFloatVar("btagSF_{}_rel".format(unc))

    # additional generator level information about jet flavor
    wrapper.SetIntVar("N_bJets")
    wrapper.SetIntVar("N_cJets")
    wrapper.SetIntVar("N_lJets")

    # b tagging patch
    wrapper.SetFloatVar("sfPatch")

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
 
    # additional relative weights
    wrapper.SetFloatVar("L1ECALPrefire")
    wrapper.SetFloatVar("L1ECALPrefire_up_rel")
    wrapper.SetFloatVar("L1ECALPrefire_down_rel")

    wrapper.SetFloatVar("pileup")
    wrapper.SetFloatVar("pileup_up_rel")
    wrapper.SetFloatVar("pileup_down_rel")

    
    

def calculate_variables(event, wrapper, sample):
    '''
    calculate weights
    '''

    # add basic information for friend trees
    wrapper.branchArrays["Evt_ID"][0] = event.Evt_ID
    wrapper.branchArrays["Evt_Run"][0] = event.Evt_Run
    wrapper.branchArrays["Evt_Lumi"][0] = event.Evt_Lumi
    try:
        wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = event.GenEvt_I_TTPlusBB 
        wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = event.GenEvt_I_TTPlusCC
    except:
        wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = -1
        wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = -1
    wrapper.branchArrays["N_Jets"][0] = event.N_Jets
    wrapper.branchArrays["N_BTagsM"][0] = event.N_BTagsM


    # additional relative weights
    wrapper.branchArrays["L1ECALPrefire"][0]          = event.Weight_L1ECALPrefire
    wrapper.branchArrays["L1ECALPrefire_up_rel"][0]   = event.Weight_L1ECALPrefireUp/event.Weight_L1ECALPrefire
    wrapper.branchArrays["L1ECALPrefire_down_rel"][0] = event.Weight_L1ECALPrefireDown/event.Weight_L1ECALPrefire
    
    wrapper.branchArrays["pileup"][0]          = event.Weight_pu69p2
    wrapper.branchArrays["pileup_up_rel"][0]   = event.Weight_pu69p2Up/event.Weight_pu69p2
    wrapper.branchArrays["pileup_down_rel"][0] = event.Weight_pu69p2Down/event.Weight_pu69p2
    

    # rate factors
    # apply them directly to the weights
    try:
        wrapper.branchArrays["muR_up_rel_wRF"][0]   = event.Weight_scale_variation_muR_2p0_muF_1p0 * rateFactors.getRF(sample, "Weight_scale_variation_muR_2p0_muF_1p0")
        wrapper.branchArrays["muR_down_rel_wRF"][0] = event.Weight_scale_variation_muR_0p5_muF_1p0 * rateFactors.getRF(sample, "Weight_scale_variation_muR_0p5_muF_1p0")
        wrapper.branchArrays["muF_up_rel_wRF"][0]   = event.Weight_scale_variation_muR_1p0_muF_2p0 * rateFactors.getRF(sample, "Weight_scale_variation_muR_1p0_muF_2p0")
        wrapper.branchArrays["muF_down_rel_wRF"][0] = event.Weight_scale_variation_muR_1p0_muF_0p5 * rateFactors.getRF(sample, "Weight_scale_variation_muR_1p0_muF_0p5")
     
        wrapper.branchArrays["isr_up_rel_wRF"][0]   = event.GenWeight_isr_Def_up   * rateFactors.getRF(sample, "GenWeight_isr_Def_up")
        wrapper.branchArrays["isr_down_rel_wRF"][0] = event.GenWeight_isr_Def_down * rateFactors.getRF(sample, "GenWeight_isr_Def_down")
        wrapper.branchArrays["fsr_up_rel_wRF"][0]   = event.GenWeight_fsr_Def_up   * rateFactors.getRF(sample, "GenWeight_fsr_Def_up")
        wrapper.branchArrays["fsr_down_rel_wRF"][0] = event.GenWeight_fsr_Def_down * rateFactors.getRF(sample, "GenWeight_fsr_Def_down")
    except: pass

    # b-tagging scale factor patches
    patchValue = sfPatch.getPatchValue(sample, event.GenEvt_I_TTPlusBB, event.GenEvt_I_TTPlusCC, event.N_Jets, event.Evt_HT_jets)
    wrapper.branchArrays["sfPatch"][0] = patchValue

    # iterative b-tagging scale factors
    btagSF = 1.
    uncs = {}
    for u in btagSF_uncs:
        uncs[u] = 1.

    nB = 0
    nC = 0
    nL = 0
    for idx in range(event.N_Jets):
        # determine jet flavor
        if   event.Jet_Flav[idx] == 5: 
            flav = 0
            nB += 1
        elif event.Jet_Flav[idx] == 4: 
            flav = 1
            nC += 1
        elif event.Jet_Flav[idx] <= 3: 
            flav = 2
            nL += 1
        else: sys.exit("jet flavor not supported")

        # load scale factors for eta, pt, btagValue bin
        sfs = btaggingSFs.getSFs(flav, abs(event.Jet_Eta[idx]), event.Jet_Pt[idx], event.Jet_btagValue[idx])

        # nominal scale factor
        btagSF*= sfs.loc["central"]

        # scale factor per jet
        wrapper.branchArrays["Jet_btagSF"][idx] = sfs.loc["central"]

        # scale factor uncertainties
        for u in btagSF_uncs:
            # cferr only exists for c-jets
            if flav == 1: 
                if "cferr" in u:
                    uncs[u] *= sfs.loc[u]
                else:
                    uncs[u] *= sfs.loc["central"]
            # for the others cferr does not exist
            else:
                if "cferr" in u:
                    uncs[u] *= sfs.loc["central"]
                else:
                    uncs[u] *= sfs.loc[u]


    wrapper.branchArrays["btagSF"][0] = btagSF
    for u in btagSF_uncs:
        wrapper.branchArrays["btagSF_{}_rel".format(u)][0] = uncs[u]/btagSF

    # save jet flavor numbers
    wrapper.branchArrays["N_bJets"][0] = nB
    wrapper.branchArrays["N_cJets"][0] = nC
    wrapper.branchArrays["N_lJets"][0] = nL

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

    for iEl in range(event.N_TightElectrons):
        trigger = elTrigSFs.getSFs(event.Electron_Pt[iEl], event.Electron_Eta_Supercluster[iEl])
        idsf    = elIDSFs.getSFs(  event.Electron_Pt[iEl], event.Electron_Eta_Supercluster[iEl])
        recosf  = elRecoSFs.getSFs(event.Electron_Pt[iEl], event.Electron_Eta_Supercluster[iEl])

        elTrigSF      *= trigger.loc["central"]
        elTrigSF_up   *= trigger.loc["up"]
        elTrigSF_down *= trigger.loc["down"]

        elIDSF        *= idsf.loc["central"]
        elIDSF_up     *= idsf.loc["up"]
        elIDSF_down   *= idsf.loc["down"]

        elRecoSF      *= recosf.loc["central"]
        elRecoSF_up   *= recosf.loc["up"]
        elRecoSF_down *= recosf.loc["down"]

    wrapper.branchArrays["elTrigSF"][0]          = elTrigSF
    wrapper.branchArrays["elTrigSF_up"][0]       = elTrigSF_up
    wrapper.branchArrays["elTrigSF_up_rel"][0]   = elTrigSF_up/elTrigSF
    wrapper.branchArrays["elTrigSF_down"][0]     = elTrigSF_down
    wrapper.branchArrays["elTrigSF_down_rel"][0] = elTrigSF_down/elTrigSF
        
    wrapper.branchArrays["elIDSF"][0]        = elIDSF
    wrapper.branchArrays["elIDSF_up"][0]     = elIDSF_up
    wrapper.branchArrays["elIDSF_down"][0]   = elIDSF_down
        
    wrapper.branchArrays["elRecoSF"][0]      = elRecoSF
    wrapper.branchArrays["elRecoSF_up"][0]   = elRecoSF_up
    wrapper.branchArrays["elRecoSF_down"][0] = elRecoSF_down

    wrapper.branchArrays["elSF"][0]          = elIDSF*elRecoSF
    wrapper.branchArrays["elSF_up_rel"][0]   = (elIDSF_up*elRecoSF_up)/(elIDSF*elRecoSF)
    wrapper.branchArrays["elSF_down_rel"][0] = (elIDSF_down*elRecoSF_down)/(elIDSF*elRecoSF)
        
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

    for iMu in range(event.N_TightMuons):
        trigger = muTrigSFs.getSFs(event.Muon_Pt[iMu], abs(event.Muon_Eta[iMu]))
        idsf    = muIDSFs.getSFs(  event.Muon_Pt[iMu], abs(event.Muon_Eta[iMu]))
        isosf   = muIsoSFs.getSFs( event.Muon_Pt[iMu], abs(event.Muon_Eta[iMu]))

        muTrigSF      *= trigger.loc["central"]
        muTrigSF_up   *= trigger.loc["up"]
        muTrigSF_down *= trigger.loc["down"]

        muIDSF        *= idsf.loc["central"]
        muIDSF_up     *= idsf.loc["up"]
        muIDSF_down   *= idsf.loc["down"]

        muIsoSF       *= isosf.loc["central"]
        muIsoSF_up    *= isosf.loc["up"]
        muIsoSF_down  *= isosf.loc["down"]

    wrapper.branchArrays["muTrigSF"][0]          = muTrigSF
    wrapper.branchArrays["muTrigSF_up"][0]       = muTrigSF_up
    wrapper.branchArrays["muTrigSF_up_rel"][0]   = muTrigSF_up/muTrigSF
    wrapper.branchArrays["muTrigSF_down"][0]     = muTrigSF_down
    wrapper.branchArrays["muTrigSF_down_rel"][0] = muTrigSF_down/muTrigSF
        
    wrapper.branchArrays["muIDSF"][0]        = muIDSF
    wrapper.branchArrays["muIDSF_up"][0]     = muIDSF_up
    wrapper.branchArrays["muIDSF_down"][0]   = muIDSF_down
        
    wrapper.branchArrays["muIsoSF"][0]       = muIsoSF
    wrapper.branchArrays["muIsoSF_up"][0]    = muIsoSF_up
    wrapper.branchArrays["muIsoSF_down"][0]  = muIsoSF_down

    wrapper.branchArrays["muSF"][0]            = muIDSF*muIsoSF
    wrapper.branchArrays["muSF_up_rel"][0]     = (muIDSF_up*muIsoSF_up)/(muIDSF*muIsoSF)
    wrapper.branchArrays["muSF_down_rel"][0]   = (muIDSF_down*muIsoSF_down)/(muIDSF*muIsoSF)

    return event

