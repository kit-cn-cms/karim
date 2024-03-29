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

def set_branches(wrapper, jec = None):
    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("lumi")   

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
    #wrapper.SetFloatVar("L1ECALPrefire")
    #wrapper.SetFloatVar("L1ECALPrefire_up_rel")
    #wrapper.SetFloatVar("L1ECALPrefire_down_rel")


def calculate_variables(event, wrapper, sample, jec = None, genWeights = None):
    '''
    calculate weights
    '''

    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    
    # additional relative weights
    #wrapper.branchArrays["L1ECALPrefire"][0]          = getattr(event, "Weight_L1ECALPrefire")
    #wrapper.branchArrays["L1ECALPrefire_up_rel"][0]   = getattr(event, "Weight_L1ECALPrefireUp")/getattr(event, "Weight_L1ECALPrefire")
    #wrapper.branchArrays["L1ECALPrefire_down_rel"][0] = getattr(event, "Weight_L1ECALPrefireDown")/getattr(event, "Weight_L1ECALPrefire")
    
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

    for iEl in range(getattr(event, "nEle")):
        # TODO super cluster eta
        trigger = elTrigSFs.getSFs(getattr(event, "Ele_Pt")[iEl], getattr(event, "Ele_EtaSC")[iEl])
        idsf    = elIDSFs.getSFs(  getattr(event, "Ele_Pt")[iEl], getattr(event, "Ele_EtaSC")[iEl])
        recosf  = elRecoSFs.getSFs(getattr(event, "Ele_Pt")[iEl], getattr(event, "Ele_EtaSC")[iEl])

        elTrigSF      *= trigger.loc["central"]
        elIDSF        *= idsf.loc["central"]
        elRecoSF      *= recosf.loc["central"]

        elTrigSF_up   *= trigger.loc["up"]
        elTrigSF_down *= trigger.loc["down"]

        elIDSF_up     *= idsf.loc["up"]
        elIDSF_down   *= idsf.loc["down"]

        elRecoSF_up   *= recosf.loc["up"]
        elRecoSF_down *= recosf.loc["down"]

    wrapper.branchArrays["elTrigSF"][0] = elTrigSF
    wrapper.branchArrays["elIDSF"][0]   = elIDSF
    wrapper.branchArrays["elRecoSF"][0] = elRecoSF
    wrapper.branchArrays["elSF"][0]     = elIDSF*elRecoSF

    wrapper.branchArrays["elTrigSF_up"][0]       = elTrigSF_up
    wrapper.branchArrays["elTrigSF_down"][0]     = elTrigSF_down
        
    wrapper.branchArrays["elIDSF_up"][0]     = elIDSF_up
    wrapper.branchArrays["elIDSF_down"][0]   = elIDSF_down
        
    wrapper.branchArrays["elRecoSF_up"][0]   = elRecoSF_up
    wrapper.branchArrays["elRecoSF_down"][0] = elRecoSF_down

    # relative SFs only when exactly one electron is present
    if event.nEle == 1 and event.nMu == 0:
        wrapper.branchArrays["elTrigSF_up_rel"][0]   = elTrigSF_up/elTrigSF
        wrapper.branchArrays["elTrigSF_down_rel"][0] = elTrigSF_down/elTrigSF
        wrapper.branchArrays["elSF_up_rel"][0]   = (elIDSF_up*elRecoSF_up)/(elIDSF*elRecoSF)
        wrapper.branchArrays["elSF_down_rel"][0] = (elIDSF_down*elRecoSF_down)/(elIDSF*elRecoSF)
    else:
        wrapper.branchArrays["elTrigSF_up_rel"][0]   = 1.
        wrapper.branchArrays["elTrigSF_down_rel"][0] = 1.
        wrapper.branchArrays["elSF_up_rel"][0]   = 1.
        wrapper.branchArrays["elSF_down_rel"][0] = 1.
            
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

    for iMu in range(getattr(event, "nMu")):
        trigger = muTrigSFs.getSFs(getattr(event, "Mu_Pt")[iMu], abs(getattr(event, "Mu_Eta")[iMu]))
        idsf    = muIDSFs.getSFs(  getattr(event, "Mu_Pt")[iMu], abs(getattr(event, "Mu_Eta")[iMu]))
        isosf   = muIsoSFs.getSFs( getattr(event, "Mu_Pt")[iMu], abs(getattr(event, "Mu_Eta")[iMu]))

        muTrigSF      *= trigger.loc["central"]
        muIDSF        *= idsf.loc["central"]
        muIsoSF       *= isosf.loc["central"]

        muTrigSF_up   *= trigger.loc["up"]
        muTrigSF_down *= trigger.loc["down"]

        muIDSF_up     *= idsf.loc["up"]
        muIDSF_down   *= idsf.loc["down"]

        muIsoSF_up    *= isosf.loc["up"]
        muIsoSF_down  *= isosf.loc["down"]

    wrapper.branchArrays["muTrigSF"][0] = muTrigSF
    wrapper.branchArrays["muIDSF"][0]   = muIDSF
    wrapper.branchArrays["muIsoSF"][0]  = muIsoSF
    wrapper.branchArrays["muSF"][0]     = muIDSF*muIsoSF

    wrapper.branchArrays["muTrigSF_up"][0]       = muTrigSF_up
    wrapper.branchArrays["muTrigSF_down"][0]     = muTrigSF_down
        
    wrapper.branchArrays["muIDSF_up"][0]     = muIDSF_up
    wrapper.branchArrays["muIDSF_down"][0]   = muIDSF_down
        
    wrapper.branchArrays["muIsoSF_up"][0]    = muIsoSF_up
    wrapper.branchArrays["muIsoSF_down"][0]  = muIsoSF_down

    # relative SFs only when exactly one muon is present
    if event.nMu == 1 and event.nEle == 0:
        wrapper.branchArrays["muTrigSF_up_rel"][0]   = muTrigSF_up/muTrigSF
        wrapper.branchArrays["muTrigSF_down_rel"][0] = muTrigSF_down/muTrigSF
        wrapper.branchArrays["muSF_up_rel"][0]     = (muIDSF_up*muIsoSF_up)/(muIDSF*muIsoSF)
        wrapper.branchArrays["muSF_down_rel"][0]   = (muIDSF_down*muIsoSF_down)/(muIDSF*muIsoSF)
    else:
        wrapper.branchArrays["muTrigSF_up_rel"][0]   = 1.
        wrapper.branchArrays["muTrigSF_down_rel"][0] = 1.
        wrapper.branchArrays["muSF_up_rel"][0]     = 1.
        wrapper.branchArrays["muSF_down_rel"][0]   = 1.

    return event

