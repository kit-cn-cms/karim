import numpy as np
import common
import weightModules
from array import array
import os
import sys
import ROOT
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

    wrapper.SetFloatVar("dnnOutput_0"+suffix)
    wrapper.SetFloatVar("dnnOutput_1"+suffix)
    wrapper.SetFloatVar("dnnOutput_2"+suffix)
    wrapper.SetFloatVar("dnnOutput_3"+suffix)
    wrapper.SetFloatVar("dnnOutput_4"+suffix)
    wrapper.SetFloatVar("dnnOutput_5"+suffix)

    wrapper.SetIntVar("dnnBestIndex"+suffix)
    
    wrapper.SetFloatVar("ttbbReco_DNNbb_Mbb"+suffix)
    wrapper.SetFloatVar("ttbbReco_DNNbb_dRbb"+suffix)
    wrapper.SetFloatVar("ttbbReco_DNNbb_etabb"+suffix)
    wrapper.SetFloatVar("ttbbReco_DNNbb_pTbb"+suffix)
    wrapper.SetFloatVar("ttbbReco_DNNbb_b1_eta"+suffix)
    wrapper.SetFloatVar("ttbbReco_DNNbb_b1_pt"+suffix)
    wrapper.SetFloatVar("ttbbReco_DNNbb_b2_eta"+suffix)
    wrapper.SetFloatVar("ttbbReco_DNNbb_b2_pt"+suffix)


modelPath = "/nfs/dust/cms/user/vdlinden/ULttbb/dnnModels/5FS_Model"
weightFile = os.path.join(modelPath, "best_model.h5")
modelFile = os.path.join(modelPath, "ttbb_is_ttbbDNN64_5f_model")
try:
    from keras.models import load_model
    model = load_model(modelFile)
    model.load_weights(weightFile)
except:
    from tensorflow.keras.models import load_model
    model = load_model(modelFile)
    model.load_weights(weightFile)
model.summary()

input2 = np.zeros(4*6).reshape(-1, 4, 6)
#print(input2)
input1 = np.zeros(31).reshape(-1, 31)
#print(input1)
def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''


    suffix = "_"+jec
    if getattr(event, "nJets"+suffix) < 6 or getattr(event, "nTagsM"+suffix) < 4 or event.nLep < 1: return

    btagValues = list(getattr(event, "Jets_btagDeepFlavB"+suffix))
    pts  = list(getattr(event, "Jets_pt"+suffix))
    etas = list(getattr(event, "Jets_eta"+suffix))
    phis = list(getattr(event, "Jets_phi"+suffix))
    ms   = list(getattr(event, "Jets_mass"+suffix))
    jetIdx = np.argsort(btagValues)[::-1]

    input1[0][0] = getattr(event, "nTagsM"+suffix)
    input1[0][1] = getattr(event, "nJets"+suffix)
    input1[0][2] = getattr(event, "HT_4bjets"+suffix)

    lepPt  = getattr(event, "Lep_pt")[0]
    lepEta = getattr(event, "Lep_eta")[0]
    lepPhi = getattr(event, "Lep_phi")[0]
    lepM   = getattr(event, "Lep_mass")[0]
    input1[0][3] = lepPt
    input1[0][4] = lepEta
    input1[0][5] = lepPhi
    input1[0][6] = lepM

    input2[0][0][0] = pts[jetIdx[0]]
    input2[0][1][0] = pts[jetIdx[1]]
    input2[0][2][0] = pts[jetIdx[2]]
    input2[0][3][0] = pts[jetIdx[3]]

    input2[0][0][1] = etas[jetIdx[0]]
    input2[0][1][1] = etas[jetIdx[1]]
    input2[0][2][1] = etas[jetIdx[2]]
    input2[0][3][1] = etas[jetIdx[3]]

    input2[0][0][2] = ms[jetIdx[0]]
    input2[0][1][2] = ms[jetIdx[1]]
    input2[0][2][2] = ms[jetIdx[2]]
    input2[0][3][2] = ms[jetIdx[3]]

    input2[0][0][3] = btagValues[jetIdx[0]]
    input2[0][1][3] = btagValues[jetIdx[1]]
    input2[0][2][3] = btagValues[jetIdx[2]]
    input2[0][3][3] = btagValues[jetIdx[3]]

    dRLep1 = common.get_dR(lepEta, lepPhi, etas[jetIdx[0]], phis[jetIdx[0]])
    dRLep2 = common.get_dR(lepEta, lepPhi, etas[jetIdx[1]], phis[jetIdx[1]])
    dRLep3 = common.get_dR(lepEta, lepPhi, etas[jetIdx[2]], phis[jetIdx[2]])
    dRLep4 = common.get_dR(lepEta, lepPhi, etas[jetIdx[3]], phis[jetIdx[3]])

    input2[0][0][4] = dRLep1
    input2[0][1][4] = dRLep2
    input2[0][2][4] = dRLep3
    input2[0][3][4] = dRLep4

    lep = ROOT.TLorentzVector()
    lep.SetPtEtaPhiM(lepPt, lepEta, lepPhi, lepM)
    
    v = {}
    for idx in [0, 1, 2, 3]:
        v[idx] = ROOT.TLorentzVector()
        v[idx].SetPtEtaPhiM(
            pts[jetIdx[idx]], etas[jetIdx[idx]], phis[jetIdx[idx]], ms[jetIdx[idx]])
        
        lj = lep+v[idx]
        input2[0][idx][5] = lj.M()

    # get the 6 permutations
    permutations = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
    pidx = 0
    for p in permutations:
        idx1 = p[0]
        idx2 = p[1]
        dPhi = common.get_dPhi(phis[jetIdx[idx1]], phis[jetIdx[idx2]])
        dEta = common.get_dEta(etas[jetIdx[idx1]], etas[jetIdx[idx2]])
        input1[0][7+pidx+0*6] = dEta
        input1[0][7+pidx+1*6] = dPhi

        dijet = v[idx1]+v[idx2]
        dijetM = dijet.M()
        input1[0][7+pidx+2*6] = dijetM

        dRLep = common.get_dR(
            lepEta, lepPhi,
            dijet.Eta(), dijet.Phi()
            )
        input1[0][7+pidx+3*6] = dRLep
        pidx += 1

    # evaluate the network
    prediction = model.predict([input1, input2])[0]
    wrapper.branchArrays["dnnOutput_0"+suffix][0] = prediction[0]
    wrapper.branchArrays["dnnOutput_1"+suffix][0] = prediction[1]
    wrapper.branchArrays["dnnOutput_2"+suffix][0] = prediction[2]
    wrapper.branchArrays["dnnOutput_3"+suffix][0] = prediction[3]
    wrapper.branchArrays["dnnOutput_4"+suffix][0] = prediction[4]
    wrapper.branchArrays["dnnOutput_5"+suffix][0] = prediction[5]

    bestIndex = np.argmax(prediction)
    wrapper.branchArrays["dnnBestIndex"+suffix][0] = bestIndex
    if bestIndex == 0:
        bbidx = [jetIdx[0], jetIdx[1]]
        btagidx = [0, 1]
    elif bestIndex == 1:
        bbidx = [jetIdx[0], jetIdx[2]]
        btagidx = [0, 2]
    elif bestIndex == 2:
        bbidx = [jetIdx[0], jetIdx[3]]
        btagidx = [0, 3]
    elif bestIndex == 3:
        bbidx = [jetIdx[1], jetIdx[2]]
        btagidx = [1, 2]
    elif bestIndex == 4:
        bbidx = [jetIdx[1], jetIdx[3]]
        btagidx = [1, 3]
    elif bestIndex == 5:
        bbidx = [jetIdx[2], jetIdx[3]]
        btagidx = [2, 3]
    else:
        print("ERROR no valid output value")
        sys.exit()

    bbidx = [jetIdx[btagidx[0]], jetIdx[btagidx[1]]]

    if pts[bbidx[0]] < pts[bbidx[1]]:
        bbidx = bbidx[::-1]
    
    dijet = v[btagidx[0]]+v[btagidx[1]]
    wrapper.branchArrays["ttbbReco_DNNbb_Mbb"+suffix][0]  = dijet.M()
    wrapper.branchArrays["ttbbReco_DNNbb_pTbb"+suffix][0] = dijet.Pt()
    dR = common.get_dR(
        etas[bbidx[0]], phis[bbidx[0]],
        etas[bbidx[1]], phis[bbidx[1]])
    wrapper.branchArrays["ttbbReco_DNNbb_dRbb"+suffix][0] = dR
    wrapper.branchArrays["ttbbReco_DNNbb_etabb"+suffix][0] = dijet.Eta()

    wrapper.branchArrays["ttbbReco_DNNbb_b1_eta"+suffix][0]  = etas[bbidx[0]]
    wrapper.branchArrays["ttbbReco_DNNbb_b1_pt"+suffix][0]   = pts[bbidx[0]]
    wrapper.branchArrays["ttbbReco_DNNbb_b2_eta"+suffix][0]  = etas[bbidx[1]]
    wrapper.branchArrays["ttbbReco_DNNbb_b2_pt"+suffix][0]   = pts[bbidx[1]]
    return event

