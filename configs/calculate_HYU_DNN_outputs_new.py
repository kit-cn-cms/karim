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


#modelPath = "/nfs/dust/cms/user/vdlinden/ULttbb/dnnModels/5FS_Model"
modelPath = "/nfs/dust/cms/user/vdlinden/ULttbb/dnnModels/ptModel_5FS"
weightFile = os.path.join(modelPath, "best_model.h5")
#modelFile = os.path.join(modelPath, "ttbb_is_ttbbDNN64_5f_model")
modelFile = os.path.join(modelPath, "ttbb_ptbM_model")
try:
    from keras.models import load_model
    model = load_model(modelFile)
    model.load_weights(weightFile)
except:
    from tensorflow.keras.models import load_model
    model = load_model(modelFile)
    model.load_weights(weightFile)
model.summary()

input2 = np.zeros(4*7).reshape(-1, 4, 7)
#print(input2)
input1 = np.zeros(31).reshape(-1, 31)
#print(input1)

permutations = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]
def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''


    suffix = "_"+jec
    nj = getattr(event, "nJets"+suffix)
    nt = getattr(event, "nTagsM"+suffix)
    if nj < 6 or nt < 4 or event.nLep < 1: return

    isM = np.array(getattr(event, "Jets_taggedM"+suffix))
    jetIdx = np.where(isM)[0]
    if len(jetIdx) < 4:
        return
    jetIdx = np.array(jetIdx[:4])

    isM  = isM[jetIdx]
    isT  = np.array(getattr(event, "Jets_taggedT"+suffix))[jetIdx]
    pts  = np.array(getattr(event, "Jets_pt"+suffix))[jetIdx]
    etas = np.array(getattr(event, "Jets_eta"+suffix))[jetIdx]
    phis = np.array(getattr(event, "Jets_phi"+suffix))[jetIdx]
    ms   = np.array(getattr(event, "Jets_mass"+suffix))[jetIdx]
    
    input1[0][0] = nt
    input1[0][1] = nj
    #input1[0][2] = pts[jetIdx[0]] + pts[jetIdx[1]] + pts[jetIdx[2]] + pts[jetIdx[3]]
    input1[0][2] = sum(pts)

    lepPt  = getattr(event, "Lep_pt")[0]
    lepEta = getattr(event, "Lep_eta")[0]
    lepPhi = getattr(event, "Lep_phi")[0]
    lepM   = getattr(event, "Lep_mass")[0]
    input1[0][3] = lepPt
    input1[0][4] = lepEta
    input1[0][5] = lepPhi
    input1[0][6] = lepM

    input2[0,:,0] = pts
    #input2[0][0][0] = pts[jetIdx[0]]
    #input2[0][1][0] = pts[jetIdx[1]]
    #input2[0][2][0] = pts[jetIdx[2]]
    #input2[0][3][0] = pts[jetIdx[3]]

    input2[0,:,1] = etas
    #input2[0][0][1] = etas[jetIdx[0]]
    #input2[0][1][1] = etas[jetIdx[1]]
    #input2[0][2][1] = etas[jetIdx[2]]
    #input2[0][3][1] = etas[jetIdx[3]]

    input2[0,:,2] = ms
    #input2[0][0][2] = ms[jetIdx[0]]
    #input2[0][1][2] = ms[jetIdx[1]]
    #input2[0][2][2] = ms[jetIdx[2]]
    #input2[0][3][2] = ms[jetIdx[3]]

    input2[0,:,3] = isM
    #input2[0][0][3] = isM[jetIdx[0]]
    #input2[0][1][3] = isM[jetIdx[1]]
    #input2[0][2][3] = isM[jetIdx[2]]
    #input2[0][3][3] = isM[jetIdx[3]]

    input2[0,:,4] = isT
    #input2[0][0][4] = isT[jetIdx[0]]
    #input2[0][1][4] = isT[jetIdx[1]]
    #input2[0][2][4] = isT[jetIdx[2]]
    #input2[0][3][4] = isT[jetIdx[3]]

    dRLep1 = common.get_dR(lepEta, lepPhi, etas[0], phis[0])
    dRLep2 = common.get_dR(lepEta, lepPhi, etas[1], phis[1])
    dRLep3 = common.get_dR(lepEta, lepPhi, etas[2], phis[2])
    dRLep4 = common.get_dR(lepEta, lepPhi, etas[3], phis[3])

    input2[0,0,5] = dRLep1
    input2[0,1,5] = dRLep2
    input2[0,2,5] = dRLep3
    input2[0,3,5] = dRLep4

    lep = ROOT.TLorentzVector()
    lep.SetPtEtaPhiM(lepPt, lepEta, lepPhi, lepM)
    
    v = {}
    for idx in [0, 1, 2, 3]:
        v[idx] = ROOT.TLorentzVector()
        v[idx].SetPtEtaPhiM(
            pts[idx], etas[idx], phis[idx], ms[idx])
        
        lj = lep+v[idx]
        input2[0,idx,6] = lj.M()

    # get the 6 permutations
    pidx = 0
    for p in permutations:
        idx1 = p[0]
        idx2 = p[1]
        dPhi = common.get_dPhi(phis[idx1], phis[idx2])
        dEta = common.get_dEta(etas[idx1], etas[idx2])
        input1[0,7+pidx+0*6] = dEta
        input1[0,7+pidx+1*6] = dPhi

        dijet = v[idx1]+v[idx2]
        dijetM = dijet.M()
        input1[0,7+pidx+2*6] = dijetM

        dRLep = common.get_dR(
            lepEta, lepPhi,
            dijet.Eta(), dijet.Phi()
            )
        input1[0,7+pidx+3*6] = dRLep
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
    bestIdx = permutations[bestIndex]

    if bestIdx[0] < bestIdx[1]:
        bestIdx[::-1]
    
    dijet = v[bestIdx[0]]+v[bestIdx[1]]
    wrapper.branchArrays["ttbbReco_DNNbb_Mbb"+suffix][0]  = dijet.M()
    wrapper.branchArrays["ttbbReco_DNNbb_pTbb"+suffix][0] = dijet.Pt()
    dR = common.get_dR(
        etas[bestIdx[0]], phis[bestIdx[0]],
        etas[bestIdx[1]], phis[bestIdx[1]])
    wrapper.branchArrays["ttbbReco_DNNbb_dRbb"+suffix][0] = dR
    wrapper.branchArrays["ttbbReco_DNNbb_etabb"+suffix][0] = dijet.Eta()

    wrapper.branchArrays["ttbbReco_DNNbb_b1_eta"+suffix][0]  = etas[bestIdx[0]]
    wrapper.branchArrays["ttbbReco_DNNbb_b1_pt"+suffix][0]   = pts[bestIdx[0]]
    wrapper.branchArrays["ttbbReco_DNNbb_b2_eta"+suffix][0]  = etas[bestIdx[1]]
    wrapper.branchArrays["ttbbReco_DNNbb_b2_pt"+suffix][0]   = pts[bestIdx[1]]
    return event

