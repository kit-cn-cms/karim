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
    # for corr in btagEffjson_lep.values():
    #     print(f"Correction {corr.name} has {len(corr.inputs)} inputs")
    #     for ix in corr.inputs:
    #         print(f"   Input {ix.name} ({ix.type}): {ix.description}")
    # for corr in btagEffjson_had.values():
    #     print(f"Correction {corr.name} has {len(corr.inputs)} inputs")
    #     for ix in corr.inputs:
    #         print(f"   Input {ix.name} ({ix.type}): {ix.description}")
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
SFb_sys = ["up_correlated","up_uncorrelated","down_correlated","down_uncorrelated"]
SFl_sys = ["up_correlated","up_uncorrelated","down_correlated","down_uncorrelated"]

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

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        ]
    return variables

# define base selection
def base_selection(event):
    return True

# soon not needed anymore
def set_branches(wrapper, jec):
    suffix = "_"+jec

    if jec == "nom":
        wrapper.SetIntVar("Evt_ID")   
        wrapper.SetIntVar("Evt_Run")   
        wrapper.SetIntVar("Evt_Lumi") 

        # cross section weight
        wrapper.SetFloatVar("xsNorm")

        for sys in SFb_sys:
            wrapper.SetFloatVar("fixedWPSFb_"+sys+"_rel")
            wrapper.SetFloatVar("fixedWPSFb_leptonic_"+sys+"_rel")
            wrapper.SetFloatVar("fixedWPSFb_hadronic_"+sys+"_rel")
        for sys in SFl_sys:
            wrapper.SetFloatVar("fixedWPSFl_"+sys+"_rel")
            wrapper.SetFloatVar("fixedWPSFl_leptonic_"+sys+"_rel")
            wrapper.SetFloatVar("fixedWPSFl_hadronic_"+sys+"_rel")

    wrapper.SetFloatVar("fixedWPSF_leptonic"+suffix)
    wrapper.SetFloatVar("fixedWPSF_hadronic"+suffix)

    # recoil trigger SFs
    wrapper.SetFloatVar("recoil"+suffix)

    wrapper.SetFloatVar("recoilTriggerSF"+suffix)
    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_up")
    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_down")

    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_Systup")
    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_Systdown")

    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_Statup")
    wrapper.SetFloatVar("recoilTriggerSF"+suffix+"_Statdown")

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
    
    print("eta:",eta)
    print("pt:",pt)
    print("flav:",flav)
    print("passes M:",passes_M)
    
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
    print(eta_lfjets_flattened)
    print(pt_lfjets_flattened)
    print(flav_lfjets_flattened)
    print(eta_hfjets_flattened)
    print(pt_hfjets_flattened)
    print(flav_hfjets_flattened)

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
    print("eff M",eff_M)

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
        sf_M_sys_lfjets = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate(sys, "M", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
        sf_M_sys_hfjets = btagSF[dataEra]["deepJet_comb"].evaluate("central", "M", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)
        sf_M_sys_lfjets = (ak.unflatten(ak.unflatten(sf_M_sys_lfjets,nums_njets_lf),nums_njecs_lf))[:,index_jec_nom]
        sf_M_sys_hfjets = (ak.unflatten(ak.unflatten(sf_M_sys_hfjets,nums_njets_hf),nums_njecs_hf))[:,index_jec_nom]
        sf_M_sys[sys] = ak.concatenate((sf_M_sys_lfjets,sf_M_sys_hfjets),axis=1)
    
    for sys in SFb_sys:
        sf_M_sys_lfjets = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate("central", "M", flav_lfjets_flattened, eta_lfjets_flattened, pt_lfjets_flattened)
        sf_M_sys_hfjets = btagSF[dataEra]["deepJet_comb"].evaluate(sys, "M", flav_hfjets_flattened, eta_hfjets_flattened, pt_hfjets_flattened)
        sf_M_sys_lfjets = (ak.unflatten(ak.unflatten(sf_M_sys_lfjets,nums_njets_lf),nums_njecs_lf))[:,index_jec_nom]
        sf_M_sys_hfjets = (ak.unflatten(ak.unflatten(sf_M_sys_hfjets,nums_njets_hf),nums_njecs_hf))[:,index_jec_nom]
        sf_M_sys[sys] = ak.concatenate((sf_M_sys_lfjets,sf_M_sys_hfjets),axis=1)
    
    print("sf M:",sf_M_sys)

    # rearrange kinematic variable ak arrays such that their order resembles the order in the efficiency and scale factor ak arrays
    eta = ak.concatenate((eta_lfjets,eta_hfjets),axis=2)
    pt = ak.concatenate((pt_lfjets,pt_hfjets),axis=2)
    passes_M = ak.concatenate((passes_M[mask_flav_0],passes_M[mask_flav_4_5]),axis=2)
    flav = ak.concatenate((flav_lfjets,flav_hfjets),axis=2)

    print("eta:",eta)
    print("pt:",pt)
    print("flav:",flav)
    print("passes M:",passes_M)

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
    
    print(jec)
    print("p mc",P_MC)
    print("p data:",P_DATA_sys)

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
        output_array["fixedWPSFl_leptonic_"+sys+"_rel"] = P_DATA_sys[sys]/P_DATA_sys["central"][:,index_jec_nom]
    for sys in SFb_sys:
        output_array["fixedWPSFb_leptonic_"+sys+"_rel"] = P_DATA_sys[sys]/P_DATA_sys["central"][:,index_jec_nom]
    print("\n\n")
    print(output_array)

    return output_array
    ################
    ### HADRONIC ###
    ################
    P_MC   = 1.
    P_DATA_sys = {}
    sf_L_sys = {}
    if jec == "nom":
        for sys in SFb_sys+SFl_sys:
            P_DATA_sys[sys] = 1.

    # necessary jet variables
    eta   = np.absolute(event["Jets_outside_lead_AK15Jet_Eta"+suffix][0])
    pt    = event["Jets_outside_lead_AK15Jet_Pt"+suffix][0]
    flav  = event["Jets_outside_lead_AK15Jet_HadronFlav"+suffix][0]
    passes_L = event["Jets_outside_lead_AK15Jet_taggedL"+suffix][0]

    # create some masks
    mask_flav_0 = flav == 0
    #print("flav 0 mask:",mask_flav_0)
    mask_flav_4_5 = np.logical_or(flav == 4, flav == 5)

    # use correctionlib
    eff_L = np.concatenate((btagEff[dataEra]["had"].evaluate("L", flav[mask_flav_0], eta[mask_flav_0], pt[mask_flav_0]),\
                            btagEff[dataEra]["had"].evaluate("L", flav[mask_flav_4_5], eta[mask_flav_4_5], pt[mask_flav_4_5])))
    # print("eff M",eff_M)
    # todo: check empty bins in efficiency
    eff_L[eff_L == 0.] = 0.001

    # use correctionlib
    sf_L_sys["central"] = np.concatenate((btagSF[dataEra_lightSF]["deepJet_incl"].evaluate("central", "L", flav[mask_flav_0], eta[mask_flav_0], pt[mask_flav_0]),\
                                          btagSF[dataEra]["deepJet_comb"].evaluate("central", "L", flav[mask_flav_4_5], eta[mask_flav_4_5], pt[mask_flav_4_5])))
    if jec == "nom":
        for sys in SFl_sys:
            sf_L_sys[sys] = np.concatenate((btagSF[dataEra_lightSF]["deepJet_incl"].evaluate(sys, "L", flav[mask_flav_0], eta[mask_flav_0], pt[mask_flav_0]),\
                                     btagSF[dataEra]["deepJet_comb"].evaluate("central", "L", flav[mask_flav_4_5], eta[mask_flav_4_5], pt[mask_flav_4_5])))
        for sys in SFb_sys:
            sf_L_sys[sys] = np.concatenate((btagSF[dataEra_lightSF]["deepJet_incl"].evaluate("central", "L", flav[mask_flav_0], eta[mask_flav_0], pt[mask_flav_0]),\
                                     btagSF[dataEra]["deepJet_comb"].evaluate(sys, "L", flav[mask_flav_4_5], eta[mask_flav_4_5], pt[mask_flav_4_5])))
    
    # rearrange arrays
    eta = np.concatenate((eta[mask_flav_0],eta[mask_flav_4_5]))
    pt = np.concatenate((pt[mask_flav_0],pt[mask_flav_4_5]))
    passes_L = np.concatenate((passes_L[mask_flav_0],passes_L[mask_flav_4_5]))
    flav = np.concatenate((flav[mask_flav_0],flav[mask_flav_4_5]))

    passes_L_mask = passes_L==1
    fails_L_mask = passes_L==0
    P_MC = np.prod(eff_L[passes_L_mask])*np.prod(np.add(np.negative(eff_L[fails_L_mask]),1.))
    P_DATA_sys["central"] = np.prod(np.multiply(eff_L[passes_L_mask],sf_L_sys["central"][passes_L_mask]))*np.prod(np.add(np.negative(np.multiply(eff_L[fails_L_mask],sf_L_sys["central"][fails_L_mask])),1.))

    if jec == "nom":
        for sys in SFl_sys+SFb_sys:
            P_DATA_sys[sys] = np.prod(np.multiply(eff_L[passes_L_mask],sf_L_sys[sys][passes_L_mask]))* \
                              np.prod(np.add(np.negative(np.multiply(eff_L[fails_L_mask],sf_L_sys[sys][fails_L_mask])),1.))

    wrapper.branchArrays["fixedWPSF_hadronic"+suffix][0] = P_DATA_sys["central"]/P_MC
    # print("sf central:",P_DATA_sys["central"]/P_MC)
    if jec == "nom":
        for sys in SFl_sys:
            wrapper.branchArrays["fixedWPSFl_hadronic_"+sys+"_rel"][0] = P_DATA_sys[sys]/P_DATA_sys["central"]
            # print("sf {}".format(sys),P_DATA_sys[sys]/P_DATA_sys["central"])
        for sys in SFb_sys:
            wrapper.branchArrays["fixedWPSFb_hadronic_"+sys+"_rel"][0] = P_DATA_sys[sys]/P_DATA_sys["central"]
            # print("sf {}".format(sys),P_DATA_sys[sys]/P_DATA_sys["central"])

    # for idx in range(event["N_Jets_outside_lead_AK15Jet"+suffix][0]):
    #     eta   = float(abs(event["Jets_outside_lead_AK15Jet_Eta"+suffix][0][idx]))
    #     pt    = float(event["Jets_outside_lead_AK15Jet_Pt"+suffix][0][idx])
    #     flav  = int(event["Jets_outside_lead_AK15Jet_HadronFlav"+suffix][0][idx])
    #     passes_L = event["Jets_outside_lead_AK15Jet_taggedL"+suffix][0][idx]

    #     # TODO: fix this
    #     if abs(flav) > 5:
    #         continue
    #         # flav = 0
    #     if abs(eta) > 5:
    #         continue
    #         # eta = 0.

    #     eff_L = btagEff[dataEra]["had"].evaluate("L", flav, eta, pt)


    #     if flav == 0:
    #         sf_L = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate("central", "L", flav, eta, pt)
    #         if jec == "nom":
    #             for sys in SFl_sys:
    #                 sfl_L[sys] = btagSF[dataEra_lightSF]["deepJet_incl"].evaluate(sys, "L", flav, eta, pt)
    #     else:
    #         sf_L = btagSF[dataEra]["deepJet_comb"].evaluate("central", "L", flav, eta, pt)
    #         if jec == "nom":
    #             for sys in SFb_sys:
    #                 sfb_L[sys] = btagSF[dataEra]["deepJet_comb"].evaluate(sys, "L", flav, eta, pt)

    #     if passes_L:
    #         P_MC   *= eff_L
    #         P_DATA *= eff_L*sf_L
    #         if jec == "nom":
    #             if flav == 0:
    #                 for sys in SFl_sys:
    #                     Pl_DATA[sys] *= eff_L*sfl_L[sys]
    #                 for sys in SFb_sys:
    #                     Pb_DATA[sys] *= eff_L*sf_L
    #             else:
    #                 for sys in SFb_sys:
    #                     Pb_DATA[sys] *= eff_L*sfb_L[sys]
    #                 for sys in SFl_sys:
    #                     Pl_DATA[sys] *= eff_L*sf_L
    #     else:
    #         P_MC   *= (1. - eff_L)
    #         P_DATA *= (1. - eff_L*sf_L)  
    #         if jec == "nom":
    #             if flav == 0:
    #                 for sys in SFl_sys:
    #                     Pl_DATA[sys] *= (1. - eff_L*sfl_L[sys])
    #                 for sys in SFb_sys:
    #                     Pb_DATA[sys] *= (1. - eff_L*sf_L)
    #             else:
    #                 for sys in SFb_sys:
    #                     Pb_DATA[sys] *= (1. - eff_L*sfb_L[sys])
    #                 for sys in SFl_sys:
    #                     Pl_DATA[sys] *= (1. - eff_L*sf_L)

    # wrapper.branchArrays["fixedWPSF_hadronic"+suffix][0] = P_DATA/P_MC
    # if jec == "nom":
    #     for sys in SFl_sys:
    #         wrapper.branchArrays["fixedWPSFl_hadronic_"+sys+"_rel"][0] = Pl_DATA[sys]/P_DATA
    #     for sys in SFb_sys:
    #         wrapper.branchArrays["fixedWPSFb_hadronic_"+sys+"_rel"][0] = Pb_DATA[sys]/P_DATA


    ##########################
    ### Recoil Trigger SFs ###
    ##########################

    recoil = event["Hadr_Recoil_MET_T1XY_Pt"+suffix][0]
    wrapper.branchArrays["recoil"+suffix][0] = recoil

    if (recoil > 250) and (event["N_LooseMuons"][0] >= 0 and event["N_LooseElectrons"][0] == 0 and event["N_LoosePhotons"][0] == 0):
        wrapper.branchArrays["recoilTriggerSF"+suffix][0] = btagEff[dataEra]["recoilTrig"].evaluate("central", recoil)
        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_up"][0] = btagEff[dataEra]["recoilTrig"].evaluate("up", recoil)
        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_down"][0] = btagEff[dataEra]["recoilTrig"].evaluate("down", recoil)

        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_Statup"][0] = btagEff[dataEra]["recoilTrig"].evaluate("statup", recoil)
        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_Statdown"][0] = btagEff[dataEra]["recoilTrig"].evaluate("statdown", recoil)

        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_Systup"][0] = btagEff[dataEra]["recoilTrig"].evaluate("systup", recoil)
        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_Systdown"][0] = btagEff[dataEra]["recoilTrig"].evaluate("systdown", recoil)
    else:
        wrapper.branchArrays["recoilTriggerSF"+suffix][0] = 1.
        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_up"][0] = 1.
        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_down"][0] = 1.

        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_Statup"][0] = 1.
        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_Statdown"][0] = 1.

        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_Systup"][0] = 1.
        # wrapper.branchArrays["recoilTriggerSF"+suffix+"_Systdown"][0] = 1.


    return event

