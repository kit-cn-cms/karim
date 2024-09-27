import numpy as np
import common
import weightModules
from array import array
import os
import pandas as pd
import onnxruntime as ort
# import uproot_methods # needed for hdamp part
import math
import ROOT

filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
hdamp_dir = os.path.join(karimpath, "data/hdamp")

ort_sess_hdampUp = ort.InferenceSession(os.path.join(hdamp_dir, 'mymodel12_hdamp_up_13TeV.onnx'))
input_name_hdampUp = ort_sess_hdampUp.get_inputs()[0].name
label_name_hdampUp = ort_sess_hdampUp.get_outputs()[0].name
ort_sess_hdampDown = ort.InferenceSession(os.path.join(hdamp_dir, 'mymodel12_hdamp_down_13TeV.onnx'))
input_name_hdampDown = ort_sess_hdampDown.get_inputs()[0].name
label_name_hdampDown = ort_sess_hdampDown.get_outputs()[0].name

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
    '''
    initialize branches of output root file
    '''
    if jec=="nominal" or jec is None:
        wrapper.SetIntVar("event")   
        wrapper.SetIntVar("run")   
        wrapper.SetIntVar("lumi")
        wrapper.SetFloatVar("hdamp_up")
        wrapper.SetFloatVar("hdamp_down")
        suffix = "_nominal"
    else:
        suffix = "_{}".format(jec)

    wrapper.SetFloatVar("ttB"+suffix)
    wrapper.SetFloatVar("ttH"+suffix)
    wrapper.SetFloatVar("ttZB"+suffix)
    wrapper.SetFloatVar("ttZnonB"+suffix)
    wrapper.SetFloatVar("ttC"+suffix)
    wrapper.SetFloatVar("ttLF"+suffix)
    wrapper.SetFloatVar("other"+suffix)
    # wrapper.SetFloatVar("HvB"+suffix)
    # wrapper.SetFloatVar("HvZB"+suffix)
    # wrapper.SetFloatVar("HvZ"+suffix)
    # wrapper.SetFloatVar("HvC"+suffix)
    # wrapper.SetFloatVar("HvLFO"+suffix)
    # wrapper.SetFloatVar("ZvB"+suffix)
    # wrapper.SetFloatVar("ZvH"+suffix)
    # wrapper.SetFloatVar("ZvC"+suffix)
    # wrapper.SetFloatVar("ZvLFO"+suffix)
    # wrapper.SetFloatVar("BvH"+suffix)
    # wrapper.SetFloatVar("BvZ"+suffix)
    # wrapper.SetFloatVar("BvC"+suffix)
    # wrapper.SetFloatVar("BvLFO"+suffix)
    # wrapper.SetFloatVar("CvH"+suffix)
    # wrapper.SetFloatVar("CvZ"+suffix)
    # wrapper.SetFloatVar("CvB"+suffix)
    # wrapper.SetFloatVar("CvLFO"+suffix)

    wrapper.SetIntVar("top_idx"+suffix)

    # wrapper.SetFloatVar("hdamp_up"+suffix)
    # wrapper.SetFloatVar("hdamp_down"+suffix)

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None, nodes=None, graph=None, edge=None):
    suffix = "_{}".format(jec)
    if jec is None:
        suffix = "_nominal"
    ttB = -99
    ttH = -99
    ttZB = -99
    ttZnonB = -99
    ttC = -99
    ttLF = -99
    other = -99
    # HvB = -99
    # HvZB = -99
    # HvZ = -99
    # HvC = -99
    # HvLFO = -99
    # ZvB = -99
    # ZvH = -99
    # ZvC = -99
    # ZvLFO = -99
    # BvH = -99
    # BvZ = -99
    # BvC = -99
    # BvLFO = -99
    # CvH = -99
    # CvZ = -99
    # CvB = -99
    # CvLFO = -99

    idx = -99

    event_ = getattr(event, "event")
    run = getattr(event, "run")
    lumi = getattr(event, "luminosityBlock")

    try:
        ttB = graph["ttB"+suffix]
        ttH = graph["ttH"+suffix]
        ttZB = graph["ttZB"+suffix]
        ttZnonB = graph["ttZnonB"+suffix]
        ttC = graph["ttC"+suffix]
        ttLF = graph["ttLF"+suffix]
        other = graph["other"+suffix]

        # HvB = ttH/(ttB+ttH)
        # HvZB = ttH/(ttH+ttZB)
        # HvZ = ttH/(ttH+ttZB+ttZnonB)
        # HvC = ttH/(ttH+ttC)
        # HvLFO = ttH/(ttH+ttLF+other)

        # ZvB = (ttZB+ttZnonB)/(ttB+ttZB+ttZnonB)
        # ZvH = (ttZB+ttZnonB)/(ttH+ttZB+ttZnonB)
        # ZvC = (ttZB+ttZnonB)/(ttZB+ttZnonB+ttC)
        # ZvLFO = (ttZB+ttZnonB)/(ttZB+ttZnonB+ttLF+other)

        # BvH = ttB/(ttB+ttH)
        # BvZ = ttB/(ttB+ttZB+ttZnonB)
        # BvC = ttB/(ttB+ttC)
        # BvLFO = ttB/(ttB+ttLF+other)
        # CvH = ttC/(ttC+ttH)
        # CvZ = ttC/(ttC+ttZB+ttZnonB)
        # CvB = ttC/(ttC+ttB)
        # CvLFO = ttC/(ttC+ttLF+other)

        suffix_mapping = {
            "ttB" + suffix: 0,
            "ttH" + suffix: 1,
            "ttZB" + suffix: 2,
            "ttZnonB" + suffix: 3,
            "ttC" + suffix: 4,
            "ttLF" + suffix: 5,
            "other" + suffix: 6,
        }
        idx = suffix_mapping.get(graph[["ttB"+suffix,"ttH"+suffix,"ttZB"+suffix,"ttZnonB"+suffix,"ttC"+suffix,"ttLF"+suffix,"other"+suffix]].idxmax(axis="columns").item(), -99)

    except:
        pass

    # add basic information for friend trees
    if jec=="nominal" or jec is None:
        wrapper.branchArrays["event"][0] = event_
        wrapper.branchArrays["run"][0]   = run
        wrapper.branchArrays["lumi"][0]  = lumi
    wrapper.branchArrays["ttB"+suffix][0] = float(ttB.iloc[0])
    wrapper.branchArrays["ttH"+suffix][0] = float(ttH.iloc[0])
    wrapper.branchArrays["ttZB"+suffix][0] = float(ttZB.iloc[0])
    wrapper.branchArrays["ttZnonB"+suffix][0] = float(ttZnonB.iloc[0])
    wrapper.branchArrays["ttC"+suffix][0] = float(ttC.iloc[0])
    wrapper.branchArrays["ttLF"+suffix][0] = float(ttLF.iloc[0])
    wrapper.branchArrays["other"+suffix][0] = float(other.iloc[0])
    # wrapper.branchArrays["HvB"+suffix][0] = float(HvB.iloc[0])
    # wrapper.branchArrays["HvZB"+suffix][0] = float(HvZB.iloc[0])
    # wrapper.branchArrays["HvZ"+suffix][0] = float(HvZ.iloc[0])
    # wrapper.branchArrays["HvC"+suffix][0] = float(HvC.iloc[0])
    # wrapper.branchArrays["HvLFO"+suffix][0] = float(HvLFO.iloc[0])
    # wrapper.branchArrays["ZvB"+suffix][0] = float(ZvB.iloc[0])
    # wrapper.branchArrays["ZvH"+suffix][0] = float(ZvH.iloc[0])
    # wrapper.branchArrays["ZvC"+suffix][0] = float(ZvC.iloc[0])
    # wrapper.branchArrays["ZvLFO"+suffix][0] = float(ZvLFO.iloc[0])
    # wrapper.branchArrays["BvH"+suffix][0] = float(BvH.iloc[0])
    # wrapper.branchArrays["BvZ"+suffix][0] = float(BvZ.iloc[0])
    # wrapper.branchArrays["BvC"+suffix][0] = float(BvC.iloc[0])
    # wrapper.branchArrays["BvLFO"+suffix][0] = float(BvLFO.iloc[0])
    # wrapper.branchArrays["CvH"+suffix][0] = float(CvH.iloc[0])
    # wrapper.branchArrays["CvZ"+suffix][0] = float(CvZ.iloc[0])
    # wrapper.branchArrays["CvB"+suffix][0] = float(CvB.iloc[0])
    # wrapper.branchArrays["CvLFO"+suffix][0] = float(CvLFO.iloc[0])

    wrapper.branchArrays["top_idx"+suffix][0] = int(idx)

    # ### hdamp part ###
    if jec=="nominal" or jec is None:

        #general declarations
        hdamp = 1.379 ##This value is the value of hdamp of your NanoAOD divided by 172.5
        maxM =  243.95 ##This value is needed to normalise the mass of the particles in each event and comes from the maximum mass value we had in the training+validation sample
        # PDGid to small float dictionary
        PID2FLOAT_MAP = {6: .1, -6: .2}
        
        data = ["SingleMuon", "MuonEG", "EGamma", "DoubleMuon"]
        if any(string in sample for string in data) or not sample.startswith(("TT", "tt")):
            # wrapper.branchArrays["hdamp_up"+suffix][0] = -99.
            # wrapper.branchArrays["hdamp_down"+suffix][0] = -99.
            wrapper.branchArrays["hdamp_up"][0] = -99.
            wrapper.branchArrays["hdamp_down"][0] = -99.
        else:
            # if not suffix == "_nominal":
            #     wrapper.branchArrays["hdamp_up"+suffix][0] = 1.0
            #     wrapper.branchArrays["hdamp_down"+suffix][0] = 1.0
            # else:
                GenPart_pdgId = event.GenPart_pdgId
                GenPart_statusFlags = event.GenPart_statusFlags
                GenPart_pt = event.GenPart_pt
                GenPart_phi = event.GenPart_phi
                GenPart_eta = event.GenPart_eta
                GenPart_mass = event.GenPart_mass

                for hdamp_var in ["hdamp_up", "hdamp_down"]:
                    ## moved outside event loop
                    # if "hdamp_up" in hdamp_var:
                    #     ort_sess = ort.InferenceSession(os.path.join(hdamp_dir, 'mymodel12_hdamp_up_13TeV.onnx'))
                    # else:
                    #     ort_sess = ort.InferenceSession(os.path.join(hdamp_dir, 'mymodel12_hdamp_down_13TeV.onnx'))
                    # input_name = ort_sess.get_inputs()[0].name
                    # label_name = ort_sess.get_outputs()[0].name

                    particlesvector=[]
                    P0 = []

                    # Loop on the genParticles, selecting only INITIAL top and antitop (considering parton shower) 
                    for i in range(0, len(GenPart_pdgId)):
                        if GenPart_pdgId[i] == 6:

                            if (((GenPart_statusFlags[i] >> 12) & 0x1) > 0):
                                # ptop = uproot_methods.TLorentzVector.from_ptetaphim(GenPart_pt[i], GenPart_eta[i], GenPart_phi[i], GenPart_mass[i])
                                ptop = ROOT.Math.PtEtaPhiMVector(GenPart_pt[i], GenPart_eta[i], GenPart_phi[i], GenPart_mass[i])
                        
                        if GenPart_pdgId[i] == -6:

                            if (((GenPart_statusFlags[i] >> 12) & 0x1) > 0):
                                # patop = uproot_methods.TLorentzVector.from_ptetaphim(GenPart_pt[i], GenPart_eta[i], GenPart_phi[i], GenPart_mass[i])
                                patop = ROOT.Math.PtEtaPhiMVector(GenPart_pt[i], GenPart_eta[i], GenPart_phi[i], GenPart_mass[i])
                
                    # Creating the array with all info needed to pass to the NN model, already normalised
                    # particlesvector.append([math.log10(ptop.pt), ptop.rapidity, ptop.phi, ptop.mass/maxM, PID2FLOAT_MAP.get(6, 0), hdamp]) # if uproot_methods are used
                    # particlesvector.append([math.log10(patop.pt), patop.rapidity, patop.phi, patop.mass/maxM, PID2FLOAT_MAP.get(-6, 0), hdamp]) # if uproot_methods are used
                    # Append to the list
                    particlesvector.append([math.log10(ptop.Pt()), ptop.Rapidity(), ptop.Phi(), ptop.M()/maxM, PID2FLOAT_MAP.get(6, 0), hdamp])
                    particlesvector.append([math.log10(patop.Pt()), patop.Rapidity(), patop.Phi(), patop.M()/maxM, PID2FLOAT_MAP.get(-6, 0), hdamp])
                    P0.append(particlesvector)
                    P0=np.array(P0)

                    p_tt = ptop + patop

                    ## run inference
                    if "hdamp_up" in hdamp_var:
                        pred = ort_sess_hdampUp.run([label_name_hdampUp], {input_name_hdampUp: P0.astype(np.float32)})[0]
                    else:
                        pred = ort_sess_hdampDown.run([label_name_hdampDown], {input_name_hdampDown: P0.astype(np.float32)})[0]
                    # pred = ort_sess.run([label_name], {input_name: P0.astype(np.float32)})[0] ## moved outside event loop
                    # if (p_tt.pt<1000): # if uproot_methods are used
                    if (p_tt.Pt()<1000):
                        weight = pred[:,0]/pred[:,1]
                    else:
                        weight = 1.0

                    if "hdamp_up" in hdamp_var:
                        # wrapper.branchArrays["hdamp_up"+suffix][0] = weight
                        wrapper.branchArrays["hdamp_up"][0] = weight
                    else:
                        # wrapper.branchArrays["hdamp_down"+suffix][0] = weight
                        wrapper.branchArrays["hdamp_down"][0] = weight
    # ## end of hdamp part ##

    # print("event: ", event)
    return event