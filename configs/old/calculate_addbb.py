import numpy as np
import common
from array import array

btagWP = 0.277
def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        "Evt_ID",
        "Evt_Run",
        "Evt_Lumi"
        "GenEvt_I_TTPlusBB",
        "GenEvt_I_TTPlusCC",

        ]
    return variables

def base_selection(event):
    return True

def set_branches(wrapper):
    wrapper.SetIntVar("Evt_ID")   
    wrapper.SetIntVar("Evt_Run")   
    wrapper.SetIntVar("Evt_Lumi")   
    wrapper.SetIntVar("GenEvt_I_TTPlusBB")   
    wrapper.SetIntVar("GenEvt_I_TTPlusCC")
    wrapper.SetIntVar("N_Jets")
    wrapper.SetIntVar("N_BTagsM")
    wrapper.SetIntVar("N_GenJets")
    wrapper.SetIntVar("N_GenBJets")
    wrapper.SetIntVar("N_AdditionalGenBJets")

    # gen values
    wrapper.SetFloatVar("ClosestGenB_dR_bb")
    wrapper.SetFloatVar("ClosestGenB_dEta_bb")
    wrapper.SetFloatVar("ClosestGenB_dPhi_bb")
    wrapper.SetFloatVar("ClosestGenB_M_bb")
    wrapper.SetFloatVar("ClosestGenB_Pt_bb")
    wrapper.SetFloatVar("ClosestGenB_Eta_bb")
    wrapper.SetFloatVar("ClosestGenB_Phi_bb")
    wrapper.SetFloatVar("ClosestGenB_E_bb")
    # gen add b jets
    wrapper.SetFloatVar("ClosestGenB_Pt_0")
    wrapper.SetFloatVar("ClosestGenB_Pt_1")
    wrapper.SetFloatVar("ClosestGenB_Eta_0")
    wrapper.SetFloatVar("ClosestGenB_Eta_1")
    ## max gen bb mass
    wrapper.SetFloatVar("GenBJets_maxM_bb")
    # gen bb system
    wrapper.SetFloatVar("AddGenB_dR_bb")
    wrapper.SetFloatVar("AddGenB_dEta_bb")
    wrapper.SetFloatVar("AddGenB_dPhi_bb")
    wrapper.SetFloatVar("AddGenB_M_bb")
    wrapper.SetFloatVar("AddGenB_Pt_bb")
    wrapper.SetFloatVar("AddGenB_Eta_bb")
    wrapper.SetFloatVar("AddGenB_Phi_bb")
    wrapper.SetFloatVar("AddGenB_E_bb")
    # gen add b jets
    wrapper.SetFloatVar("AddGenB_Pt_0")
    wrapper.SetFloatVar("AddGenB_Pt_1")
    wrapper.SetFloatVar("AddGenB_Eta_0")
    wrapper.SetFloatVar("AddGenB_Eta_1")
    ## max gen bb mass
    #wrapper.SetFloatVar("GenBJets_maxM_bb")
    ## pt of gen b jets
    #wrapper.SetFloatVar("GenBJets_Pt_0")
    #wrapper.SetFloatVar("GenBJets_Pt_1")
    #wrapper.SetFloatVar("GenBJets_Pt_2")
    #wrapper.SetFloatVar("GenBJets_Pt_3")
    ## pt of gen lf jets
    #wrapper.SetFloatVar("GenLJets_Pt_0")
    #wrapper.SetFloatVar("GenLJets_Pt_1")
    #wrapper.SetFloatVar("GenLJets_Pt_2")

    # reco values
    wrapper.SetFloatVar("mindRbb_dR_bb")
    wrapper.SetFloatVar("mindRbb_dEta_bb")
    wrapper.SetFloatVar("mindRbb_dPhi_bb")
    wrapper.SetFloatVar("mindRbb_M_bb")
    wrapper.SetFloatVar("mindRbb_Pt_bb")
    wrapper.SetFloatVar("mindRbb_Eta_bb")
    wrapper.SetFloatVar("mindRbb_Phi_bb")
    wrapper.SetFloatVar("mindRbb_E_bb")

    wrapper.SetFloatVar("mindRbb_Pt_0")
    wrapper.SetFloatVar("mindRbb_Pt_1")
    wrapper.SetFloatVar("mindRbb_Eta_0")
    wrapper.SetFloatVar("mindRbb_Eta_1")

    wrapper.SetFloatVar("maxMbb_M_bb")
    #wrapper.SetFloarVar("taggetJets_Pt_0")
    #wrapper.SetFloarVar("taggetJets_Pt_1")
    #wrapper.SetFloarVar("taggetJets_Pt_2")
    #wrapper.SetFloarVar("taggetJets_Pt_3")
    #wrapper.SetFloatVar("lfJets_Pt_0")
    #wrapper.SetFloatVar("lfJets_Pt_1")
    #wrapper.SetFloatVar("lfJets_Pt_2")

def calculate_variables(event, wrapper):
    '''
    calculate additional variables needed
    '''
    vectors = common.Vectors(event)
    wrapper.branchArrays["Evt_ID"][0] = event.Evt_ID
    wrapper.branchArrays["Evt_Run"][0] = event.Evt_Run
    wrapper.branchArrays["Evt_Lumi"][0] = event.Evt_Lumi

    wrapper.branchArrays["N_Jets"][0] = event.N_Jets
    wrapper.branchArrays["N_BTagsM"][0] = event.N_BTagsM
    try:
        wrapper.branchArrays["N_GenJets"][0] = event.N_GenJets
        wrapper.branchArrays["N_GenBJets"][0] = event.N_GenBJets
    except: pass
    try:
        wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = event.GenEvt_I_TTPlusBB 
        wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = event.GenEvt_I_TTPlusCC
    except:
        wrapper.branchArrays["GenEvt_I_TTPlusBB"][0] = -1
        wrapper.branchArrays["GenEvt_I_TTPlusCC"][0] = -1


    # gen level definition via additional gen b jets (this is not particle level)
    try:
        wrapper.branchArrays["N_AdditionalGenBJets"][0] = event.N_AdditionalGenBJets
        if event.N_AdditionalGenBJets >= 2:
            dR = common.get_dR(
                event.AdditionalGenBJet_Eta[0], event.AdditionalGenBJet_Phi[0],
                event.AdditionalGenBJet_Eta[1], event.AdditionalGenBJet_Phi[1])
            dEta = common.get_dEta(
                event.AdditionalGenBJet_Eta[0], event.AdditionalGenBJet_Eta[1])
            dPhi = common.get_dPhi(
                event.AdditionalGenBJet_Phi[0], event.AdditionalGenBJet_Phi[1])

            vectors.initIndexedVector(event, "AdditionalGenBJet", 0)
            vectors.initIndexedVector(event, "AdditionalGenBJet", 1)
            vectors.add(["AdditionalGenBJet_0", "AdditionalGenBJet_1"], out = "bb")

            wrapper.branchArrays["AddGenB_M_bb"][0]   = vectors.get("bb", "M")[0]
            wrapper.branchArrays["AddGenB_Eta_bb"][0] = abs(vectors.get("bb", "Eta")[0])
            wrapper.branchArrays["AddGenB_Phi_bb"][0] = vectors.get("bb", "Phi")[0]
            wrapper.branchArrays["AddGenB_Pt_bb"][0]  = vectors.get("bb", "Pt")[0]
            wrapper.branchArrays["AddGenB_E_bb"][0]   = vectors.get("bb", "E")[0]

            wrapper.branchArrays["AddGenB_dR_bb"][0]   = dR
            wrapper.branchArrays["AddGenB_dEta_bb"][0] = dEta
            wrapper.branchArrays["AddGenB_dPhi_bb"][0] = dPhi

            wrapper.branchArrays["AddGenB_Pt_1"][0] = event.AdditionalGenBJet_Pt[1]
            wrapper.branchArrays["AddGenB_Eta_1"][0] = abs(event.AdditionalGenBJet_Eta[1])
        if event.N_AdditionalGenBJets >= 1:
            wrapper.branchArrays["AddGenB_Pt_0"][0] = event.AdditionalGenBJet_Pt[0]
            wrapper.branchArrays["AddGenB_Eta_0"][0] = abs(event.AdditionalGenBJet_Eta[0])
    except: pass

    # gen level definition via closest particle level b jets
    try:
        if event.N_GenBJets >= 2:
            mini1 = 0
            mini2 = 0
            minVal = 999.
            maxMbb = -1.
            for i in range(event.N_GenBJets):
                vectors.initIndexedVector(event, "GenBJet", i)
            for i1 in range(event.N_GenBJets):
                for i2 in range(i1+1, event.N_GenBJets):
                    dR = common.get_dR(
                        event.GenBJet_Eta[i1], event.GenBJet_Phi[i1],
                        event.GenBJet_Eta[i2], event.GenBJet_Phi[i2])
                    if dR <= minVal:
                        minVal = dR
                        mini1 = i1
                        mini2 = i2

                    vectors.add(["GenBJet_"+str(i1), "GenBJet_"+str(i2)], out = "genb_{}_{}".format(i1, i2))
                    mbb = vectors.get("genb_{}_{}".format(i1, i2), "M")[0]
                    if mbb > maxMbb: maxMbb = mbb
            wrapper.branchArrays["GenBJets_maxM_bb"][0] = maxMbb

            dR = common.get_dR(
                event.GenBJet_Eta[mini1], event.GenBJet_Phi[mini1],
                event.GenBJet_Eta[mini2], event.GenBJet_Phi[mini2])
            dEta = common.get_dEta(
                event.GenBJet_Eta[mini1], event.GenBJet_Eta[mini2])
            dPhi = common.get_dPhi(
                event.GenBJet_Phi[mini1], event.GenBJet_Phi[mini2])

            vectors.add(["GenBJet_"+str(mini1), "GenBJet_"+str(mini2)], out = "closestbb")

            wrapper.branchArrays["ClosestGenB_M_bb"][0]   = vectors.get("closestbb", "M")[0]
            wrapper.branchArrays["ClosestGenB_Eta_bb"][0] = abs(vectors.get("closestbb", "Eta")[0])
            wrapper.branchArrays["ClosestGenB_Phi_bb"][0] = vectors.get("closestbb", "Phi")[0]
            wrapper.branchArrays["ClosestGenB_Pt_bb"][0]  = vectors.get("closestbb", "Pt")[0]
            wrapper.branchArrays["ClosestGenB_E_bb"][0]   = vectors.get("closestbb", "E")[0]

            wrapper.branchArrays["ClosestGenB_dR_bb"][0]   = dR
            wrapper.branchArrays["ClosestGenB_dEta_bb"][0] = dEta
            wrapper.branchArrays["ClosestGenB_dPhi_bb"][0] = dPhi

            wrapper.branchArrays["ClosestGenB_Pt_0"][0]  = event.GenBJet_Pt[mini1]
            wrapper.branchArrays["ClosestGenB_Eta_0"][0] = abs(event.GenBJet_Eta[mini1])
            wrapper.branchArrays["ClosestGenB_Pt_1"][0]  = event.GenBJet_Pt[mini2]
            wrapper.branchArrays["ClosestGenB_Eta_1"][0] = abs(event.GenBJet_Eta[mini2])
    except: pass
                
    # reco level definition via closest b-tagged jets
    if event.N_BTagsM >= 2:
        min_i1 = -9.
        min_i2 = -9.
        minDr = 9999.
        maxMbb = -1.
        for i in range(event.N_Jets):
            if event.Jet_CSV[i] < btagWP: continue
            vectors.initIndexedVector(event, "Jet", i)
            
        for i1 in range(event.N_Jets):
            if event.Jet_CSV[i1] < btagWP: continue
            for i2 in range(event.N_Jets):
                if i2<=i1: continue
                if event.Jet_CSV[i2] < btagWP: continue
                
                dR = common.get_dR(
                    event.Jet_Eta[i1], event.Jet_Phi[i1],
                    event.Jet_Eta[i2], event.Jet_Phi[i2])
                if dR <= minDr:
                    minDr = dR
                    min_i1 = i1
                    min_i2 = i2

                vectors.add(["Jet_"+str(i1), "Jet_"+str(i2)], "bjet_{}_{}".format(i1, i2))
                mbb = vectors.get("bjet_{}_{}".format(i1, i2), "M")[0]
                if mbb > maxMbb: maxMbb = mbb

        wrapper.branchArrays["maxMbb_M_bb"][0] = maxMbb

        mindR = common.get_dR(
            event.Jet_Eta[min_i1], event.Jet_Phi[min_i1],
            event.Jet_Eta[min_i2], event.Jet_Phi[min_i2])
        mindEta = common.get_dEta(
            event.Jet_Eta[min_i1], event.Jet_Eta[min_i2])
        mindPhi = common.get_dPhi(
            event.Jet_Phi[min_i1], event.Jet_Phi[min_i2])
        vectors.add(["Jet_{}".format(min_i1), "Jet_{}".format(min_i2)], out = "minbb")
        wrapper.branchArrays["mindRbb_M_bb"][0]   = vectors.get("minbb", "M")[0]
        wrapper.branchArrays["mindRbb_Eta_bb"][0] = abs(vectors.get("minbb", "Eta")[0])
        wrapper.branchArrays["mindRbb_Phi_bb"][0] = vectors.get("minbb", "Phi")[0]
        wrapper.branchArrays["mindRbb_Pt_bb"][0]  = vectors.get("minbb", "Pt")[0]
        wrapper.branchArrays["mindRbb_E_bb"][0]   = vectors.get("minbb", "E")[0]

        wrapper.branchArrays["mindRbb_dR_bb"][0]   = mindR
        wrapper.branchArrays["mindRbb_dEta_bb"][0] = mindEta
        wrapper.branchArrays["mindRbb_dPhi_bb"][0] = mindPhi

        wrapper.branchArrays["mindRbb_Pt_0"][0] = event.Jet_Pt[min_i1]
        wrapper.branchArrays["mindRbb_Pt_1"][0] = event.Jet_Pt[min_i2]
        wrapper.branchArrays["mindRbb_Eta_0"][0] = abs(event.Jet_Eta[min_i1])
        wrapper.branchArrays["mindRbb_Eta_1"][0] = abs(event.Jet_Eta[min_i2])
            
    return event

