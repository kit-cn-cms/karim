import numpy as np
import common
import weightModules
from array import array
import os
import sys
import correctionlib
from pprint import pprint
import awkward as ak

# path to file
filepath = os.path.abspath(__file__)
# path to karim
karimpath = os.path.dirname(os.path.dirname(filepath))

# dicts for btag scale factors and efficiencies
btagSF = {}
btagEff = {}
# directory to always updated correctionlib corrections from jsonpog
jsonDir = os.path.join("/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration", "POG")

# load all btag efficiencies and scale factors as well as recoil trigger scale factors
for year in ["2016preVFP", "2016postVFP", "2017", "2018"]:
    sfDir = os.path.join(karimpath, "data", "UL_"+year[2:])
    # efficiencies
    btagEffjson_lep = correctionlib.CorrectionSet.from_file(os.path.join(sfDir, "btagEff_monotop_lep_deepJet.json"))
    btagEffjson_had = correctionlib.CorrectionSet.from_file(os.path.join(sfDir, "btagEff_monotop_had_deepJet.json"))
    btagEff[year] = {}
    btagEff[year]["lep"] = btagEffjson_lep["btagEff"]
    btagEff[year]["had"] = btagEffjson_had["btagEff"]

    # scale factors
    btagSFjson = correctionlib.CorrectionSet.from_file(
        os.path.join(jsonDir, "BTV", year+"_UL", "btagging.json.gz"))
    btagSF[year]   = btagSFjson

    # recoil trigger SFs
    recoilTrig_evaluator = correctionlib.CorrectionSet.from_file(os.path.join(sfDir, "RecoilTriggerSF.json"))
    btagEff[year]["recoilTrig"] = recoilTrig_evaluator["RecoilTriggerSFs"]

pprint(btagEff)

# systematic variations of btag scale factors
SFb_sys = ["b_up_correlated","b_up_uncorrelated","b_down_correlated","b_down_uncorrelated"]
SFl_sys = ["l_up_correlated","l_up_uncorrelated","l_down_correlated","l_down_uncorrelated"]

# systematic variations of the recoil trigger scale factors
sys_recoil_triggersf = ["up","down","statup","statdown","systup","systdown"]

# function to define which branches from the ntuples are needed
# accepts * as wildcard
def load_input_branches():
    a = """Evt_ID
Evt_Run
Evt_Lumi
N_TightMuons
N_LooseMuons
N_LooseElectrons
N_LoosePhotons
N_Jets*
Jet_Eta*
Jet_Pt*
Jet_HadronFlav*
Jet_taggedM*
N_Jets_outside_lead_AK15Jet*
Jets_outside_lead_AK15Jet_Eta*
Jets_outside_lead_AK15Jet_Pt*
Jets_outside_lead_AK15Jet_HadronFlav*
Jets_outside_lead_AK15Jet_taggedL*
Hadr_Recoil_MET_T1XY_Pt*"""
    branches = a.split("\n")
    return branches

# config object currently still expects this function to exist
def get_additional_variables():
    pass

# define base selection
def base_selection(event):
    return True

# config object currently still expects this function to exist
def set_branches(wrapper, jec):
    pass

# function to calculate all variables in the friend tree
def calculate_variables(events, wrapper, sample, jecs, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    # apparently the 2016postVFP light btag SFs are bad
    # therefore use the preVFP ones
    if dataEra == "2016postVFP":
        dataEra_lightSF = "2016preVFP"
    else:
        dataEra_lightSF = dataEra

    suffix = "_"

    # number of events in current event batch
    nevents = len(events)
    # number of jec variations to consider
    njecs = len(jecs)
    # the index of the nominal jec variation in the jecs list
    index_jec_nom = None
    for i,jec in enumerate(jecs):
        if jec == "nom":
                index_jec_nom = i
    # the nominal jec variations always needs to be there
    assert(index_jec_nom)

    # dictionary to collect all variables written into the friend tree
    output_array = {}
    # basic necessary variables
    output_array["Evt_ID"] = events["Evt_ID"]
    output_array["Evt_Run"] = events["Evt_Run"]
    output_array["Evt_Lumi"] = events["Evt_Lumi"]
    output_array["xsNorm"] = ak.Array([genWeights.getXS("incl")]*nevents)

    ################
    ### LEPTONIC ###
    ################

    # array to hold all the MC event probabilities i.e. will later contain nevents*njecs values
    P_MC   = None
    # dict to hold the data event probabilities
    # the data probabilities are subject to jec variations and btag sf variation
    # each btag sf variation has its own key
    # value to each key will later be an array
    P_DATA_sys = {}
    sf_M_sys = {}
    for sys in SFb_sys+SFl_sys+["central"]:
        P_DATA_sys[sys] = None
        sf_M_sys[sys] = None

    # jet variables necessary to calculate the btag weights: eta, pt, flavor, and whether jet passes medium working point
    eta = []
    pt = []
    flav = []
    passes_M = []

    # need to rearrange the array structure a bit because the jec variations shall be a dimension in the used awkward arrays
    # loop over events
    for event in events:
        eta_ = []
        pt_ = []
        flav_ = []
        passes_M_ = []
        # first put a single awkward array for each jec variation in a list ...
        for i,jec in enumerate(jecs):
            suffix = "_"+jec
            #print(event["Jet_Eta"+suffix])
            eta_.append(np.absolute(event["Jet_Eta"+suffix]))
            pt_.append(event["Jet_Pt"+suffix])
            flav_.append(event["Jet_HadronFlav"+suffix])
            passes_M_.append(event["Jet_taggedM"+suffix])
        # ... then turn the list into an awkward array containing all jec variations per event
        eta.append(ak.Array(eta_))
        pt.append(ak.Array(pt_))
        flav.append(ak.Array(flav_))
        passes_M.append(ak.Array(passes_M_))
    
    # now put the per-event arrays into the final array with the following structure:
    # event -> jec variation -> variable
    eta = ak.Array(eta)
    pt = ak.Array(pt)
    flav = ak.Array(flav)
    passes_M = ak.Array(passes_M)    

    # create some masks ...
    # ... to get jets with flavor 0 (necessary because correctionlib returns error if the corresponding correction gets jets with flavor != 0)
    mask_flav_0 = flav == 0
    # print("flav 0 mask:",mask_flav_0)
    # ... to get jets with flavor 4 or 5 (necessary because ... flavor != 4 or 5)
    mask_flav_4_5 = np.logical_or(flav == 4, flav == 5)
    # print("flav 4/5 mask:",mask_flav_4_5)
    
    # print("eta:",eta)
    # print("pt:",pt)
    # print("flav:",flav)
    # print("passes M:",passes_M)
    
    # apply the defined masks to get the corresponding light flavor and heavy flavor jets
    eta_lfjets = eta[mask_flav_0]
    pt_lfjets = pt[mask_flav_0]
    flav_lfjets = flav[mask_flav_0]
    eta_hfjets = eta[mask_flav_4_5]
    pt_hfjets = pt[mask_flav_4_5]
    flav_hfjets = flav[mask_flav_4_5]

    # for the correctionlib the arrays first have to be flattened
    # after the evaluation we unflatten them again
    # num arrays containing the (un)flattening structure
    nums_njets_lf = ak.flatten(ak.num(eta_lfjets,axis=2))
    nums_njecs_lf = ak.num(eta_lfjets,axis=1)
    nums_njets_hf = ak.flatten(ak.num(eta_hfjets,axis=2))
    nums_njecs_hf = ak.num(eta_hfjets,axis=1)

    # flatten the arrays
    eta_lfjets_flattened = ak.flatten(ak.flatten(eta_lfjets,axis=2),axis=1)
    pt_lfjets_flattened = ak.flatten(ak.flatten(pt_lfjets,axis=2),axis=1)
    flav_lfjets_flattened = ak.flatten(ak.flatten(flav_lfjets,axis=2),axis=1)
    eta_hfjets_flattened = ak.flatten(ak.flatten(eta_hfjets,axis=2),axis=1)
    pt_hfjets_flattened = ak.flatten(ak.flatten(pt_hfjets,axis=2),axis=1)
    flav_hfjets_flattened = ak.flatten(ak.flatten(flav_hfjets,axis=2),axis=1)
    # print(eta_lfjets_flattened)
    # print(pt_lfjets_flattened)
    # print(flav_lfjets_flattened)
    # print(eta_hfjets_flattened)
    # print(pt_hfjets_flattened)
    # print(flav_hfjets_flattened)

    # use correctionlib to determine efficiencies on the flattened arrays
    eff_M_lfjets = btagEff[dataEra]["lep"].evaluate("M", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
    eff_M_hfjets = btagEff[dataEra]["lep"].evaluate("M", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)

    # now unflatten the efficiencies again into the proper structure similar to the kinematic variables
    eff_M_lfjets = ak.unflatten(eff_M_lfjets,nums_njets_lf)
    eff_M_lfjets = ak.unflatten(eff_M_lfjets,nums_njecs_lf)
    eff_M_hfjets = ak.unflatten(eff_M_hfjets,nums_njets_hf)
    eff_M_hfjets = ak.unflatten(eff_M_hfjets,nums_njecs_hf)

    # now concatenation
    eff_M = ak.concatenate((eff_M_lfjets,eff_M_hfjets),axis=2)
    # print("eff M",eff_M)

    # todo: check empty bins in efficiency
    #eff_M[eff_M == 0.] = 0.001

    # use correctionlib to determine scale factors
    sf_M_sys_lfjets = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate("central", "M", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
    sf_M_sys_hfjets = btagSF[dataEra]["deepJet_comb"].evaluate("central", "M", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)
    sf_M_sys_lfjets = ak.unflatten(ak.unflatten(sf_M_sys_lfjets,nums_njets_lf),nums_njecs_lf)
    sf_M_sys_hfjets = ak.unflatten(ak.unflatten(sf_M_sys_hfjets,nums_njets_hf),nums_njecs_hf)

    sf_M_sys["central"] = ak.concatenate((sf_M_sys_lfjets,sf_M_sys_hfjets),axis=2)

    # also consider btag systematics
    for sys in SFl_sys:
        sf_M_sys_lfjets = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate(sys.replace("l_",""), "M", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
        sf_M_sys_hfjets = btagSF[dataEra]["deepJet_comb"].evaluate("central", "M", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)
        sf_M_sys_lfjets = (ak.unflatten(ak.unflatten(sf_M_sys_lfjets,nums_njets_lf),nums_njecs_lf))[:,index_jec_nom]
        sf_M_sys_hfjets = (ak.unflatten(ak.unflatten(sf_M_sys_hfjets,nums_njets_hf),nums_njecs_hf))[:,index_jec_nom]
        sf_M_sys[sys] = ak.concatenate((sf_M_sys_lfjets,sf_M_sys_hfjets),axis=1)
    
    for sys in SFb_sys:
        sf_M_sys_lfjets = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate("central", "M", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
        sf_M_sys_hfjets = btagSF[dataEra]["deepJet_comb"].evaluate(sys.replace("b_",""), "M", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)
        sf_M_sys_lfjets = (ak.unflatten(ak.unflatten(sf_M_sys_lfjets,nums_njets_lf),nums_njecs_lf))[:,index_jec_nom]
        sf_M_sys_hfjets = (ak.unflatten(ak.unflatten(sf_M_sys_hfjets,nums_njets_hf),nums_njecs_hf))[:,index_jec_nom]
        sf_M_sys[sys] = ak.concatenate((sf_M_sys_lfjets,sf_M_sys_hfjets),axis=1)
    
    # print("sf M:",sf_M_sys)

    # rearrange kinematic variable ak arrays such that their order resembles the order in the efficiency and scale factor ak arrays
    eta = ak.concatenate((eta_lfjets,eta_hfjets),axis=2)
    pt = ak.concatenate((pt_lfjets,pt_hfjets),axis=2)
    passes_M = ak.concatenate((passes_M[mask_flav_0],passes_M[mask_flav_4_5]),axis=2)
    flav = ak.concatenate((flav_lfjets,flav_hfjets),axis=2)

    # print("eta:",eta)
    # print("pt:",pt)
    # print("flav:",flav)
    # print("passes M:",passes_M)

    # find the jets that pass the medium working point
    passes_M_mask = passes_M==1
    fails_M_mask = passes_M==0

    eff_M_passes_M = eff_M[passes_M_mask]
    eff_M_fails_M = eff_M[fails_M_mask]

    # calculate array of MC probabilities
    P_MC = ak.prod(eff_M_passes_M,axis=2)*ak.prod(np.add(np.negative(eff_M_fails_M),1.),axis=2)
    # calculate array of Data probabilities
    P_DATA_sys["central"] = ak.prod(eff_M_passes_M*sf_M_sys["central"][passes_M_mask],axis=2)*\
                            ak.prod(np.add(np.negative(eff_M_fails_M*sf_M_sys["central"][fails_M_mask]),1.),axis=2)
    
    # also consider btag systematics
    for sys in SFl_sys+SFb_sys:
        P_DATA_sys[sys] = ak.prod(eff_M_passes_M[:,index_jec_nom]*sf_M_sys[sys][passes_M[:,index_jec_nom]==1],axis=1)* \
                          ak.prod(np.add(np.negative((eff_M_fails_M[:,index_jec_nom])*(sf_M_sys[sys][passes_M[:,index_jec_nom]==0])),1.),axis=1)
    
    # print(jec)
    # print("p mc",P_MC)
    # print("p data:",P_DATA_sys)

    # for i,jec in enumerate(jecs):
    #     suffix = "_"+jec
    #     wrapper.branchArrays["fixedWPSF_leptonic"+suffix][0] = P_DATA_sys["central"][i]/P_MC[i]

    #     # print("sf central: {}".format(jec),P_DATA_sys["central"][i]/P_MC[i])
    #     if jec == "nom":
    #         for sys in SFl_sys:
    #             wrapper.branchArrays["fixedWPSFl_leptonic_"+sys+"_rel"][0] = P_DATA_sys[sys]/P_DATA_sys["central"][index_jec_nom]
    #             # print("sf {}".format(sys),P_DATA_sys[sys]/P_DATA_sys["central"][index_jec_nom])
    #         for sys in SFb_sys:
    #             wrapper.branchArrays["fixedWPSFb_leptonic_"+sys+"_rel"][0] = P_DATA_sys[sys]/P_DATA_sys["central"][index_jec_nom]
    #             # print("sf {}".format(sys),P_DATA_sys[sys]/P_DATA_sys["central"][index_jec_nom])
    
    for i,jec in enumerate(jecs):
        suffix = "_"+jec
        output_array["fixedWPSF_leptonic"+suffix] = P_DATA_sys["central"][:,i]/P_MC[:,i]
    #print("blablablabla",P_DATA_sys["central"].layout)
    #print("blablablabla",P_DATA_sys["central"][:,0].layout)
    
    for sys in SFl_sys:
        output_array["fixedWPSFl_leptonic_"+sys.replace("l_","")+"_rel"] = P_DATA_sys[sys]/P_DATA_sys["central"][:,index_jec_nom]
    for sys in SFb_sys:
        output_array["fixedWPSFb_leptonic_"+sys.replace("b_","")+"_rel"] = P_DATA_sys[sys]/P_DATA_sys["central"][:,index_jec_nom]
    # print("\n\n")
    # print(output_array)

    
    ################
    ### HADRONIC ###
    ################

    # similar to leptonic, only difference is other jet variable names and light (L) working instead of medium (M) wp

    P_MC   = None
    P_DATA_sys = {}
    sf_L_sys = {}
    for sys in SFb_sys+SFl_sys+["central"]:
        P_DATA_sys[sys] = None
        sf_L_sys[sys] = None

    
    eta = []
    pt = []
    flav = []
    passes_L = []

    for event in events:
        eta_ = []
        pt_ = []
        flav_ = []
        passes_L_ = []
        for i,jec in enumerate(jecs):
            suffix = "_"+jec
            eta_.append(np.absolute(event["Jets_outside_lead_AK15Jet_Eta"+suffix]))
            pt_.append(event["Jets_outside_lead_AK15Jet_Pt"+suffix])
            flav_.append(event["Jets_outside_lead_AK15Jet_HadronFlav"+suffix])
            passes_L_.append(event["Jets_outside_lead_AK15Jet_taggedL"+suffix])
        eta.append(ak.Array(eta_))
        pt.append(ak.Array(pt_))
        flav.append(ak.Array(flav_))
        passes_L.append(ak.Array(passes_L_))
    
    eta = ak.Array(eta)
    pt = ak.Array(pt)
    flav = ak.Array(flav)
    passes_L = ak.Array(passes_L)

    mask_flav_0 = flav == 0
    mask_flav_4_5 = np.logical_or(flav == 4, flav == 5)
    
    eta_lfjets = eta[mask_flav_0]
    pt_lfjets = pt[mask_flav_0]
    flav_lfjets = flav[mask_flav_0]
    eta_hfjets = eta[mask_flav_4_5]
    pt_hfjets = pt[mask_flav_4_5]
    flav_hfjets = flav[mask_flav_4_5]

    nums_njets_lf = ak.flatten(ak.num(eta_lfjets,axis=2))
    nums_njecs_lf = ak.num(eta_lfjets,axis=1)
    nums_njets_hf = ak.flatten(ak.num(eta_hfjets,axis=2))
    nums_njecs_hf = ak.num(eta_hfjets,axis=1)

    eta_lfjets_flattened = ak.flatten(ak.flatten(eta_lfjets,axis=2),axis=1)
    pt_lfjets_flattened = ak.flatten(ak.flatten(pt_lfjets,axis=2),axis=1)
    flav_lfjets_flattened = ak.flatten(ak.flatten(flav_lfjets,axis=2),axis=1)
    eta_hfjets_flattened = ak.flatten(ak.flatten(eta_hfjets,axis=2),axis=1)
    pt_hfjets_flattened = ak.flatten(ak.flatten(pt_hfjets,axis=2),axis=1)
    flav_hfjets_flattened = ak.flatten(ak.flatten(flav_hfjets,axis=2),axis=1)

    eff_L_lfjets = btagEff[dataEra]["had"].evaluate("L", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
    eff_L_hfjets = btagEff[dataEra]["had"].evaluate("L", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)

    eff_L_lfjets = ak.unflatten(eff_L_lfjets,nums_njets_lf)
    eff_L_lfjets = ak.unflatten(eff_L_lfjets,nums_njecs_lf)
    eff_L_hfjets = ak.unflatten(eff_L_hfjets,nums_njets_hf)
    eff_L_hfjets = ak.unflatten(eff_L_hfjets,nums_njecs_hf)

    eff_L = ak.concatenate((eff_L_lfjets,eff_L_hfjets),axis=2)

    sf_L_sys_lfjets = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate("central", "L", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
    sf_L_sys_hfjets = btagSF[dataEra]["deepJet_comb"].evaluate("central", "L", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)
    sf_L_sys_lfjets = ak.unflatten(ak.unflatten(sf_L_sys_lfjets,nums_njets_lf),nums_njecs_lf)
    sf_L_sys_hfjets = ak.unflatten(ak.unflatten(sf_L_sys_hfjets,nums_njets_hf),nums_njecs_hf)

    sf_L_sys["central"] = ak.concatenate((sf_L_sys_lfjets,sf_L_sys_hfjets),axis=2)

    for sys in SFl_sys:
        sf_L_sys_lfjets = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate(sys.replace("l_",""), "L", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
        sf_L_sys_hfjets = btagSF[dataEra]["deepJet_comb"].evaluate("central", "L", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)
        sf_L_sys_lfjets = (ak.unflatten(ak.unflatten(sf_L_sys_lfjets,nums_njets_lf),nums_njecs_lf))[:,index_jec_nom]
        sf_L_sys_hfjets = (ak.unflatten(ak.unflatten(sf_L_sys_hfjets,nums_njets_hf),nums_njecs_hf))[:,index_jec_nom]
        sf_L_sys[sys] = ak.concatenate((sf_L_sys_lfjets,sf_L_sys_hfjets),axis=1)
    
    for sys in SFb_sys:
        sf_L_sys_lfjets = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate("central", "L", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
        sf_L_sys_hfjets = btagSF[dataEra]["deepJet_comb"].evaluate(sys.replace("b_",""), "L", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)
        sf_L_sys_lfjets = (ak.unflatten(ak.unflatten(sf_L_sys_lfjets,nums_njets_lf),nums_njecs_lf))[:,index_jec_nom]
        sf_L_sys_hfjets = (ak.unflatten(ak.unflatten(sf_L_sys_hfjets,nums_njets_hf),nums_njecs_hf))[:,index_jec_nom]
        sf_L_sys[sys] = ak.concatenate((sf_L_sys_lfjets,sf_L_sys_hfjets),axis=1)

    eta = ak.concatenate((eta_lfjets,eta_hfjets),axis=2)
    pt = ak.concatenate((pt_lfjets,pt_hfjets),axis=2)
    passes_L = ak.concatenate((passes_L[mask_flav_0],passes_L[mask_flav_4_5]),axis=2)
    flav = ak.concatenate((flav_lfjets,flav_hfjets),axis=2)

    passes_L_mask = passes_L==1
    fails_L_mask = passes_L==0

    eff_L_passes_L = eff_L[passes_L_mask]
    eff_L_fails_L = eff_L[fails_L_mask]

    P_MC = ak.prod(eff_L_passes_L,axis=2)*ak.prod(np.add(np.negative(eff_L_fails_L),1.),axis=2)
    P_DATA_sys["central"] = ak.prod(eff_L_passes_L*sf_L_sys["central"][passes_L_mask],axis=2)*\
                            ak.prod(np.add(np.negative(eff_L_fails_L*sf_L_sys["central"][fails_L_mask]),1.),axis=2)
    
    for sys in SFl_sys+SFb_sys:
        P_DATA_sys[sys] = ak.prod(eff_L_passes_L[:,index_jec_nom]*sf_L_sys[sys][passes_L[:,index_jec_nom]==1],axis=1)* \
                          ak.prod(np.add(np.negative((eff_L_fails_L[:,index_jec_nom])*(sf_L_sys[sys][passes_L[:,index_jec_nom]==0])),1.),axis=1)
    
    for i,jec in enumerate(jecs):
        suffix = "_"+jec
        output_array["fixedWPSF_hadronic"+suffix] = P_DATA_sys["central"][:,i]/P_MC[:,i]
    
    for sys in SFl_sys:
        output_array["fixedWPSFl_hadronic_"+sys.replace("l_","")+"_rel"] = P_DATA_sys[sys]/P_DATA_sys["central"][:,index_jec_nom]
    for sys in SFb_sys:
        output_array["fixedWPSFb_hadronic_"+sys.replace("b_","")+"_rel"] = P_DATA_sys[sys]/P_DATA_sys["central"][:,index_jec_nom]
    

    ##########################
    ### Recoil Trigger SFs ###
    ##########################
    
    recoilTriggerSF = {}
    recoil = None
    # put recoils into structure events->jec variations
    for i,jec in enumerate(jecs):
        suffix = "_"+jec
        output_array["recoil"+suffix] = np.reshape(events["Hadr_Recoil_MET_T1XY_Pt"+suffix],(nevents,1))
        if i==0:
            recoil = output_array["recoil"+suffix]
        else:
            recoil = np.concatenate((recoil,output_array["recoil"+suffix]),axis=1)
    
    # evaluate recoil trigger sfs using correctionlib
    recoilTriggerSF["central"] = btagEff[dataEra]["recoilTrig"].evaluate("central", recoil)

    # consider systematics
    for sys in sys_recoil_triggersf:
        recoilTriggerSF[sys] = btagEff[dataEra]["recoilTrig"].evaluate(sys, recoil[:,index_jec_nom])
    
    # number of loose leptons and photons for selection mask
    nmuons = events["N_LooseMuons"]
    nelectrons = events["N_LooseElectrons"]
    nphotons = events["N_LoosePhotons"]

    # selection masks
    mask_nlep_npho = np.logical_not((nmuons>=0) & (nelectrons==0) & (nphotons==0))
    mask_recoil = np.logical_not(recoil>=250.)
    mask_recoil_nom = np.logical_not(recoil[:,index_jec_nom]>=250.)

    # use masks to set sf to 1 if event does not fulfill selections
    recoilTriggerSF["central"][mask_nlep_npho,:] = 1.
    recoilTriggerSF["central"][mask_recoil] = 1.
    for sys in sys_recoil_triggersf:
        recoilTriggerSF[sys][mask_nlep_npho] = 1.
        recoilTriggerSF[sys][mask_recoil_nom] = 1.


    # write recoil trigger sfs to output dict
    for i,jec in enumerate(jecs):
        suffix = "_"+jec
        output_array["recoilTriggerSF"+suffix] = recoilTriggerSF["central"][:,i]

    # consider systematics
    for sys in sys_recoil_triggersf:
        output_array["recoilTriggerSF_nom_"+sys] = recoilTriggerSF[sys]

    # return output dict
    return output_array

