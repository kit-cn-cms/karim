import numpy as np
import common
import weightModules
from array import array
import os
filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))
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

def set_branches(wrapper, jec = None):
    wrapper.SetIntVar("is_25ttbbDNN64")   
    wrapper.SetIntVar("is_25ttbjDNN64")   

    wrapper.SetFloatVar("ttbbGen25_DNNbb_etabb")
    wrapper.SetFloatVar("ttbbGen25_DNNbb_dRbb")
    wrapper.SetFloatVar("ttbbGen25_DNNbb_pTbb")
    wrapper.SetFloatVar("ttbbGen25_DNNbb_Mbb")
    wrapper.SetFloatVar("ttbbGen25_DNNbb_b1_pt")
    wrapper.SetFloatVar("ttbbGen25_DNNbb_b1_eta")
    wrapper.SetFloatVar("ttbbGen25_DNNbb_b2_pt")
    wrapper.SetFloatVar("ttbbGen25_DNNbb_b2_eta")


def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    wrapper.branchArrays["is_25ttbbDNN64"][0] = event.is_25ttbbDNN and event.is_25ttbb64
    wrapper.branchArrays["is_25ttbjDNN64"][0] = event.ttbarID >= 50 and not (event.is_25ttbbDNN and event.is_25ttbb64)

    if event.nAddGenBJets25 >= 2:
        i1 = -1
        i2 = -1
        for j1 in range(event.nAddGenBJets):
            for j2 in range(event.nAddGenBJets):
                if j1 >= j2: continue
                if event.addGenBJets_pt[j1] >= 25 and event.addGenBJets_pt[j2] >= 25:
                    i1 = j1
                    i2 = j2
                    break
            if i1>=0 and i2>=0: break

        if i1>=0 and i2>=0:
            dR = common.get_dR(
                event.addGenBJets_eta[i1], event.addGenBJets_phi[i1],
                event.addGenBJets_eta[i2], event.addGenBJets_phi[i2]
                )
            v1 = ROOT.TLorentzVector()
            v2 = ROOT.TLorentzVector()
            v1.SetPtEtaPhiM(
                event.addGenBJets_pt[i1], event.addGenBJets_eta[i1], 
                event.addGenBJets_phi[i1], event.addGenBJets_mass[i1])            
            v2.SetPtEtaPhiM(
                event.addGenBJets_pt[i2], event.addGenBJets_eta[i2], 
                event.addGenBJets_phi[i2], event.addGenBJets_mass[i2])            
            dj = v1+v2
            wrapper.branchArrays["ttbbGen25_DNNbb_Mbb"][0] = dj.M()
            wrapper.branchArrays["ttbbGen25_DNNbb_pTbb"][0] = dj.Pt()
            wrapper.branchArrays["ttbbGen25_DNNbb_dRbb"][0] = dR
            wrapper.branchArrays["ttbbGen25_DNNbb_etabb"][0] = dj.Eta()

            wrapper.branchArrays["ttbbGen25_DNNbb_b1_eta"][0] = event.addGenBJets_eta[i1]
            wrapper.branchArrays["ttbbGen25_DNNbb_b2_eta"][0] = event.addGenBJets_eta[i2]
            wrapper.branchArrays["ttbbGen25_DNNbb_b1_pt"][0] = event.addGenBJets_pt[i1]
            wrapper.branchArrays["ttbbGen25_DNNbb_b2_pt"][0] = event.addGenBJets_pt[i2]
                        

                
    return event

        
