import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
year = "2018"
sfDir = os.path.join(karimpath, "data", "legacy_"+year)

# initialize lepton trigger scale factors
elTrigSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "electron_triggerSF_"+year+".csv"), 
    sfName  = "ele28_ht150_OR_ele32_ele_pt_ele_sceta")
muTrigSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "muon_triggerSF_"+year+".csv"),
    sfName  = "IsoMu24_PtEtaBins")
    #sfName  = "IsoMu27_PtEtaBins") 2017 value

# initialize lepton ID scale factors
elIDSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "electron_idSF_"+year+".csv"),
    sfName  = "tightElectronID")
muIDSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "muon_idSF_"+year+".csv"),
    sfName  = "NUM_TightID_DEN_genTracks_pt_abseta")

# initialize lepton Reco/Iso scale factors
elRecoSFs = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "electron_recoSF_"+year+".csv"),
    sfName  = "electronReco")
muIsoSFs  = weightModules.LeptonSFs(
    csv     = os.path.join(sfDir, "muon_isoSF_"+year+".csv"),
    sfName  = "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta")

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
    suffix = "_"+jec
    wrapper.SetIntVar("event"+suffix)   
    wrapper.SetIntVar("run"+suffix)   
    wrapper.SetIntVar("lumi"+suffix)   

    # lepton trigger
    wrapper.SetFloatVar("muTrigSF"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("muTrigSF_up"+suffix)
        wrapper.SetFloatVar("muTrigSF_up_rel"+suffix)
        wrapper.SetFloatVar("muTrigSF_down"+suffix)
        wrapper.SetFloatVar("muTrigSF_down_rel"+suffix)

    wrapper.SetFloatVar("elTrigSF"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("elTrigSF_up"+suffix)
        wrapper.SetFloatVar("elTrigSF_up_rel"+suffix)
        wrapper.SetFloatVar("elTrigSF_down"+suffix)
        wrapper.SetFloatVar("elTrigSF_down_rel"+suffix)

    # lepton scale factor
    wrapper.SetFloatVar("muIDSF"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("muIDSF_up"+suffix)
        wrapper.SetFloatVar("muIDSF_down"+suffix)
    wrapper.SetFloatVar("elIDSF"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("elIDSF_up"+suffix)
        wrapper.SetFloatVar("elIDSF_down"+suffix)

    wrapper.SetFloatVar("muIsoSF"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("muIsoSF_up"+suffix)
        wrapper.SetFloatVar("muIsoSF_down"+suffix)
    wrapper.SetFloatVar("elRecoSF"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("elRecoSF_up"+suffix)
        wrapper.SetFloatVar("elRecoSF_down"+suffix)

    wrapper.SetFloatVar("muSF"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("muSF_up_rel"+suffix)
        wrapper.SetFloatVar("muSF_down_rel"+suffix)

    wrapper.SetFloatVar("elSF"+suffix)
    if jec == "nom":
        wrapper.SetFloatVar("elSF_up_rel"+suffix)
        wrapper.SetFloatVar("elSF_down_rel"+suffix)
 
    # additional relative weights
    #wrapper.SetFloatVar("L1ECALPrefire"+suffix)
    #wrapper.SetFloatVar("L1ECALPrefire_up_rel"+suffix)
    #wrapper.SetFloatVar("L1ECALPrefire_down_rel"+suffix)


def calculate_variables(event, wrapper, sample, jec, genWeights = None):
    '''
    calculate weights
    '''

    suffix = "_"+jec
    if getattr(event, "isRecoSelected"+suffix) < 1. and getattr(event,  "isGenSelected"+suffix) < 1.: 
        return event
    # add basic information for friend trees
    wrapper.branchArrays["event"+suffix][0] = getattr(event, "event"+suffix)
    wrapper.branchArrays["run"+suffix][0]   = getattr(event, "run"+suffix)
    wrapper.branchArrays["lumi"+suffix][0]  = getattr(event, "lumi"+suffix)
    
    # additional relative weights
    #wrapper.branchArrays["L1ECALPrefire"+suffix][0]          = getattr(event, "Weight_L1ECALPrefire"+suffix)
    #wrapper.branchArrays["L1ECALPrefire_up_rel"+suffix][0]   = getattr(event, "Weight_L1ECALPrefireUp"+suffix)/getattr(event, "Weight_L1ECALPrefire"+suffix)
    #wrapper.branchArrays["L1ECALPrefire_down_rel"+suffix][0] = getattr(event, "Weight_L1ECALPrefireDown"+suffix)/getattr(event, "Weight_L1ECALPrefire"+suffix)
    
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

    for iEl in range(getattr(event, "nEle"+suffix)):
        # TODO super cluster eta
        #trigger = elTrigSFs.getSFs(getattr(event, "Ele_Pt"+suffix)[iEl], getattr(event, "Ele_EtaSC"+suffix)[iEl])
        #idsf    = elIDSFs.getSFs(  getattr(event, "Ele_Pt"+suffix)[iEl], getattr(event, "Ele_EtaSC"+suffix)[iEl])
        #recosf  = elRecoSFs.getSFs(getattr(event, "Ele_Pt"+suffix)[iEl], getattr(event, "Ele_EtaSC"+suffix)[iEl])
        trigger = elTrigSFs.getSFs(getattr(event, "Ele_Pt"+suffix)[iEl], getattr(event, "Ele_Eta"+suffix)[iEl])
        idsf    = elIDSFs.getSFs(  getattr(event, "Ele_Pt"+suffix)[iEl], getattr(event, "Ele_Eta"+suffix)[iEl])
        recosf  = elRecoSFs.getSFs(getattr(event, "Ele_Pt"+suffix)[iEl], getattr(event, "Ele_Eta"+suffix)[iEl])

        elTrigSF      *= trigger.loc["central"]
        elIDSF        *= idsf.loc["central"]
        elRecoSF      *= recosf.loc["central"]

        if jec == "nom":
            elTrigSF_up   *= trigger.loc["up"]
            elTrigSF_down *= trigger.loc["down"]

            elIDSF_up     *= idsf.loc["up"]
            elIDSF_down   *= idsf.loc["down"]

            elRecoSF_up   *= recosf.loc["up"]
            elRecoSF_down *= recosf.loc["down"]

    wrapper.branchArrays["elTrigSF"+suffix][0] = elTrigSF
    wrapper.branchArrays["elIDSF"+suffix][0]   = elIDSF
    wrapper.branchArrays["elRecoSF"+suffix][0] = elRecoSF
    wrapper.branchArrays["elSF"+suffix][0]     = elIDSF*elRecoSF

    if jec == "nom":
        wrapper.branchArrays["elTrigSF_up"+suffix][0]       = elTrigSF_up
        wrapper.branchArrays["elTrigSF_up_rel"+suffix][0]   = elTrigSF_up/elTrigSF
        wrapper.branchArrays["elTrigSF_down"+suffix][0]     = elTrigSF_down
        wrapper.branchArrays["elTrigSF_down_rel"+suffix][0] = elTrigSF_down/elTrigSF
            
        wrapper.branchArrays["elIDSF_up"+suffix][0]     = elIDSF_up
        wrapper.branchArrays["elIDSF_down"+suffix][0]   = elIDSF_down
            
        wrapper.branchArrays["elRecoSF_up"+suffix][0]   = elRecoSF_up
        wrapper.branchArrays["elRecoSF_down"+suffix][0] = elRecoSF_down

        wrapper.branchArrays["elSF_up_rel"+suffix][0]   = (elIDSF_up*elRecoSF_up)/(elIDSF*elRecoSF)
        wrapper.branchArrays["elSF_down_rel"+suffix][0] = (elIDSF_down*elRecoSF_down)/(elIDSF*elRecoSF)
            
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

    for iMu in range(getattr(event, "nMu"+suffix)):
        trigger = muTrigSFs.getSFs(getattr(event, "Mu_Pt"+suffix)[iMu], abs(getattr(event, "Mu_Eta"+suffix)[iMu]))
        idsf    = muIDSFs.getSFs(  getattr(event, "Mu_Pt"+suffix)[iMu], abs(getattr(event, "Mu_Eta"+suffix)[iMu]))
        isosf   = muIsoSFs.getSFs( getattr(event, "Mu_Pt"+suffix)[iMu], abs(getattr(event, "Mu_Eta"+suffix)[iMu]))

        muTrigSF      *= trigger.loc["central"]
        muIDSF        *= idsf.loc["central"]
        muIsoSF       *= isosf.loc["central"]

        if jec == "nom":
            muTrigSF_up   *= trigger.loc["up"]
            muTrigSF_down *= trigger.loc["down"]

            muIDSF_up     *= idsf.loc["up"]
            muIDSF_down   *= idsf.loc["down"]

            muIsoSF_up    *= isosf.loc["up"]
            muIsoSF_down  *= isosf.loc["down"]

    wrapper.branchArrays["muTrigSF"+suffix][0] = muTrigSF
    wrapper.branchArrays["muIDSF"+suffix][0]   = muIDSF
    wrapper.branchArrays["muIsoSF"+suffix][0]  = muIsoSF
    wrapper.branchArrays["muSF"+suffix][0]     = muIDSF*muIsoSF

    if jec == "nom":
        wrapper.branchArrays["muTrigSF_up"+suffix][0]       = muTrigSF_up
        wrapper.branchArrays["muTrigSF_up_rel"+suffix][0]   = muTrigSF_up/muTrigSF
        wrapper.branchArrays["muTrigSF_down"+suffix][0]     = muTrigSF_down
        wrapper.branchArrays["muTrigSF_down_rel"+suffix][0] = muTrigSF_down/muTrigSF
            
        wrapper.branchArrays["muIDSF_up"+suffix][0]     = muIDSF_up
        wrapper.branchArrays["muIDSF_down"+suffix][0]   = muIDSF_down
            
        wrapper.branchArrays["muIsoSF_up"+suffix][0]    = muIsoSF_up
        wrapper.branchArrays["muIsoSF_down"+suffix][0]  = muIsoSF_down

        wrapper.branchArrays["muSF_up_rel"+suffix][0]     = (muIDSF_up*muIsoSF_up)/(muIDSF*muIsoSF)
        wrapper.branchArrays["muSF_down_rel"+suffix][0]   = (muIDSF_down*muIsoSF_down)/(muIDSF*muIsoSF)

    return event

