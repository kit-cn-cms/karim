import common

import numpy as np
import torch
from torch_geometric.data import DataLoader, Data
import json
from tqdm import tqdm
from torch_cluster import radius_graph, knn_graph
from torch_scatter import scatter_add
import os.path as osp
import os
from itertools import combinations, product

from models.model.transf_glp import Net

def get_dPhi(phi1, phi2):
    dphi = abs(phi1-phi2)
    return dphi*(dphi<np.pi)+(2.*np.pi-dphi)*(dphi>=np.pi)

def get_dEta(eta1, eta2):
    return abs(eta1-eta2)

def get_dR(eta1, phi1, eta2, phi2):
    dphi = get_dPhi(phi1, phi2)
    deta = get_dEta(eta1, eta2)

    dR = np.sqrt(dphi*dphi + deta*deta)
    return dR

def get_Minv(pt1, eta1, phi1, pt2, eta2, phi2):
    dphi = get_dPhi(phi1, phi2)
    deta = get_dEta(eta1, eta2)
    return np.sqrt(2*pt1*pt2*(np.cosh(deta) - np.cos(dphi)))

def get_edge_index(num_nodes, selfloops=False):
    if selfloops:
        edge_index = torch.tensor(list(product(range(num_nodes), range(num_nodes))), dtype=torch.long)
        edge_index = edge_index.t().contiguous()
    else:
        edge_index = torch.tensor(list(combinations(range(num_nodes), 2)), dtype=torch.long).T
        swap_index = torch.stack((edge_index[1], edge_index[0]))
        edge_index = torch.cat((edge_index, swap_index), 1)

    return edge_index

def get_edge_attr(Pt, Phi, Eta, edge_index):

    dR = torch.tensor([get_dR(Eta[edge[0]], Phi[edge[0]], Eta[edge[1]], Phi[edge[1]]) for edge in edge_index.t()])
    dR = dR.squeeze()
    Minv = torch.tensor([get_Minv(Pt[edge[0]], Eta[edge[0]], Phi[edge[0]], Pt[edge[1]], Eta[edge[1]], Phi[edge[1]]) for edge in edge_index.t()])
    Minv = Minv.squeeze()
    edge_attr = torch.stack([dR, Minv], dim=1)

    return edge_attr

def transform(x, edge_attr):
    global_features = {'dR': {'mean': 2.2037378838908066, 'std': 0.9051687742485897, 'max': 5.6947613226739735, 'min': 0.004195193731893499, 'quantile': 4.244001078650436}, 'Minv': {'mean': 175.18311278313905, 'std': 162.82510570661043, 'max': 8034.468646211956, 'min': 0.210453262505733, 'quantile': 796.0236877148421}, 'Pt': {'mean': 95.77306682706848, 'std': 103.04040607050104, 'max': 2783.923095703125, 'min': 0.630344569683075, 'quantile': 505.1054302978518}, 'Phi': {'mean': 0.01604827361664354, 'std': 1.806203951859251, 'max': 3.1415836811065674, 'min': -3.1415836811065674, 'quantile': 3.0791015625}, 'Eta': {'mean': -0.0019048697871781805, 'std': 1.058123500737131, 'max': 2.39990234375, 'min': -2.39990234375, 'quantile': 2.2548828125}, 'M': {'mean': 8.508376569935008, 'std': 11.244349720156654, 'max': 372.5978698730469, 'min': -0.75048828125, 'quantile': 49.97843158721924}, 'E': {'mean': 157.33960213164076, 'std': 183.65642124382114, 'max': 5245.314453125, 'min': 0.630344569683075, 'quantile': 949.5493884277362}}
    x_attr_names = ["Pt", "Phi", "Eta", "M", "E", "charge", "btagValue", "CvL", "CvB", "is_Jet", "is_Lep", "is_missing"]
    edge_attr_names = ["dR", "Minv"]
    for key in global_features:
        if key in x_attr_names:
            index = x_attr_names.index(key)
            x[:,index] = (x[:,index] - global_features[key]["mean"]) / global_features[key]["std"]

        elif key in edge_attr_names:
            index = edge_attr_names.index(key)
            edge_attr[:,index] = edge_attr[:,index]/global_features[key]["quantile"]
    return x, edge_attr

def load_data(event, add_jet):
    num_nodes = event.nJets_nom + event.nLep + 1
    x = []
    for iJet in range(event.nJets_nom):
        x.append([
            event.Jet_Pt_nom[iJet],
            event.Jet_Phi_nom[iJet],
            event.Jet_Eta_nom[iJet],
            event.Jet_M_nom[iJet],
            event.Jet_E_nom[iJet],
            0,
            event.Jet_btagValue_nom[iJet],
            event.Jet_CvL_nom[iJet],
            event.Jet_CvB_nom[iJet],
            1,
            0,
            0,
            add_jet[iJet],
        ])
    for iLep in range(event.nLep):
        x.append([
            event.Lep_Pt[iLep],
            event.Lep_Phi[iLep],
            event.Lep_Eta[iLep],
            event.Lep_M[iLep],
            event.Lep_E[iLep],
            event.Lep_Charge[iLep],
            0,
            0,
            0,
            0,
            1,
            0,
            add_jet[event.nJets_nom + iLep],
        ])                
    x.append([
        event.MET_T1_Pt_nom,
        event.MET_T1_Phi_nom,
        0,
        0,
        event.MET_T1_Pt_nom,
        0,
        0,
        0,
        0,
        0,
        0,
        1,
        add_jet[event.nJets_nom + 2],
    ])
    x = torch.tensor(x)
    edge_index = get_edge_index(num_nodes)
    edge_attr = get_edge_attr(x[:,0], x[:,1], x[:,2], edge_index)
    x, edge_attr = transform(x, edge_attr)
    data = [Data(x=x, edge_index=edge_index, edge_attr=edge_attr)]
    data = DataLoader(data, batch_size=1, shuffle=False)
    return data

def evaluate(model, dataloader, device):
    model.eval()
    with torch.no_grad():
        for data in dataloader:

            data = data.to(device)
            preds = model(batch=data)
    return preds

def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        ]
    return variables


def base_selection(event):
    '''
    base selection applied to all events
    events where the base selection is not fulfilled are filled with dummy values
    '''
    return True


def set_branches(wrapper, jec=None):

    wrapper.SetIntVar("event")   
    wrapper.SetIntVar("run")   
    wrapper.SetIntVar("lumi")   

    wrapper.SetIntVar("glp_num_nodes")   
    wrapper.SetIntVar("glp_highest_node")

    wrapper.SetFloatVar("glp_ttB")   
    wrapper.SetFloatVar("glp_ttHB")   
    wrapper.SetFloatVar("glp_ttZB")   
    wrapper.SetFloatVar("glp_ttC")   
    wrapper.SetFloatVar("glp_ttLF")   
    wrapper.SetFloatVar("glp_other")   
  

    wrapper.SetFloatVar("glp_BvHB")   
    wrapper.SetFloatVar("glp_HBvB")   
    wrapper.SetFloatVar("glp_BvZB")   
    wrapper.SetFloatVar("glp_ZBvB")   
    wrapper.SetFloatVar("glp_BvC")   
    wrapper.SetFloatVar("glp_CvB")   
    wrapper.SetFloatVar("glp_BvLF")   
    wrapper.SetFloatVar("glp_LFvB")   
    wrapper.SetFloatVar("glp_BvOther")   
    wrapper.SetFloatVar("glp_OthervB")   

    wrapper.SetFloatVar("glp_HBvZB")   
    wrapper.SetFloatVar("glp_ZBvHB")   
    wrapper.SetFloatVar("glp_HBvC")   
    wrapper.SetFloatVar("glp_CvHB")   
    wrapper.SetFloatVar("glp_HBvLF")   
    wrapper.SetFloatVar("glp_LFvHB")   
    wrapper.SetFloatVar("glp_HBvOther")   
    wrapper.SetFloatVar("glp_OthervHB")   

    wrapper.SetFloatVar("glp_ZBvC")   
    wrapper.SetFloatVar("glp_CvZB")   
    wrapper.SetFloatVar("glp_ZBvLF")   
    wrapper.SetFloatVar("glp_LFvZB")   
    wrapper.SetFloatVar("glp_ZBvOther")   
    wrapper.SetFloatVar("glp_OthervZB")   

    wrapper.SetFloatVar("glp_CvLF")   
    wrapper.SetFloatVar("glp_LFvC")   
    wrapper.SetFloatVar("glp_CvOther")   
    wrapper.SetFloatVar("glp_OthervC")   

    wrapper.SetFloatVar("glp_LFvOther")   
    wrapper.SetFloatVar("glp_OthervLf")   

    wrapper.SetFloatVar("glp_AllBvC")   
    wrapper.SetFloatVar("glp_CvAllB")   
    wrapper.SetFloatVar("glp_CvLFOther")   
    wrapper.SetFloatVar("glp_LFOthervC")   



def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):

    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    wrapper.branchArrays["glp_num_nodes"][0] = 6

    glp_ttB = -99
    glp_ttHB = -99
    glp_ttZB = -99
    glp_ttC = -99
    glp_ttLF = -99
    glp_other = -99
    glp_BvHB = -99
    glp_HBvB = -99
    glp_BvZB = -99
    glp_ZBvB = -99
    glp_BvC = -99
    glp_CvB = -99
    glp_BvLF = -99
    glp_LFvB = -99
    glp_BvOther = -99
    glp_OthervB = -99
    glp_HBvZB = -99
    glp_ZBvHB = -99
    glp_HBvC = -99
    glp_CvHB = -99
    glp_HBvLF = -99
    glp_LFvHB = -99
    glp_HBvOther = -99
    glp_OthervHB = -99
    glp_ZBvC = -99
    glp_CvZB = -99
    glp_ZBvLF = -99
    glp_LFvZB = -99
    glp_ZBvOther = -99
    glp_OthervZB = -99
    glp_CvLF = -99
    glp_LFvC = -99
    glp_CvOther = -99
    glp_OthervC = -99
    glp_LFvOther = -99
    glp_OthervLf = -99
    glp_AllBvC = -99
    glp_CvAllB = -99
    glp_CvLFOther = -99
    glp_LFOthervC = -99
    node = -99

    if event.nJets_nom>0:

        add_jet_preds = []
        for iJet in range(event.nJets_nom):
            add_jet_preds.append(event.eval_jets[iJet])
        for iLep in range(event.nLep):
            add_jet_preds.append(event.eval_lep[iLep])
        add_jet_preds.append(event.eval_met)

        # load PF data from one event into torch dataloader
        dataloader = load_data(event, add_jet_preds)

        # set settings for inference
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        model = Net()

        # model.load_state_dict(torch.load("/nfs/dust/cms/user/merhart/karim/models/model/best_network_rep_2_run_19.pt", map_location=torch.device(device)))
        model.load_state_dict(torch.load("/nfs/dust/cms/user/merhart/karim/models/model/best_network_rep_0_run_159.pt", map_location=torch.device(device)))

        data = evaluate(model, dataloader, device)[0]
        _, node = data.topk(1)
        
        glp_ttB = float(data[0])
        glp_ttHB = float(data[1])
        glp_ttZB = float(data[2])
        glp_ttC = float(data[3])
        glp_ttLF = float(data[4])
        glp_other = float(data[5])

        if data[0]+data[1]>0:
            glp_BvHB = float(data[0]/(data[0]+data[1]))
            glp_HBvB = float(data[1]/(data[0]+data[1]))

        if data[0]+data[2]>0:
            glp_BvZB = float(data[0]/(data[0]+data[2]))
            glp_ZBvB = float(data[2]/(data[0]+data[2]))

        if data[0]+data[3]>0:
            glp_BvC = float(data[0]/(data[0]+data[3]))
            glp_CvB = float(data[3]/(data[0]+data[3]))

        if data[0]+data[4]>0:
            glp_BvLF = float(data[0]/(data[0]+data[4]))
            glp_LFvB = float(data[4]/(data[0]+data[4]))

        if data[0]+data[5]>0:
            glp_BvOther = float(data[0]/(data[0]+data[5]))
            glp_OthervB = float(data[5]/(data[0]+data[5]))

        if data[1]+data[2]>0:
            glp_HBvZB = float(data[1]/(data[1]+data[2]))
            glp_ZBvHB = float(data[2]/(data[1]+data[2]))

        if data[1]+data[3]>0:
            glp_HBvC = float(data[1]/(data[1]+data[3]))
            glp_CvHB = float(data[3]/(data[1]+data[3]))

        if data[1]+data[4]>0:
            glp_HBvLF = float(data[1]/(data[1]+data[4]))
            glp_LFvHB = float(data[4]/(data[1]+data[4]))

        if data[1]+data[4]>0:
            glp_HBvOther = float(data[1]/(data[1]+data[5]))
            glp_OthervHB = float(data[5]/(data[1]+data[5]))

        if data[2]+data[3]>0:
            glp_ZBvC = float(data[2]/(data[2]+data[3]))
            glp_CvZB = float(data[3]/(data[2]+data[3]))

        if data[2]+data[4]>0:
            glp_ZBvLF = float(data[2]/(data[2]+data[4]))
            glp_LFvZB = float(data[4]/(data[2]+data[4]))

        if data[2]+data[5]>0:
            glp_ZBvOther = float(data[2]/(data[2]+data[5]))
            glp_OthervZB = float(data[5]/(data[2]+data[5]))

        if data[3]+data[4]>0:
            glp_CvLF = float(data[3]/(data[3]+data[4]))
            glp_LFvC = float(data[4]/(data[3]+data[4]))

        if data[3]+data[5]>0:
            glp_CvOther = float(data[3]/(data[3]+data[5]))
            glp_OthervC = float(data[5]/(data[3]+data[5]))

        if data[4]+data[5]>0:
            glp_LFvOther = float(data[4]/(data[4]+data[5]))
            glp_OthervLf = float(data[5]/(data[4]+data[5]))

        if data[0]+data[1]+data[2]+data[3]>0:
            glp_AllBvC = float((data[0]+data[1]+data[2])/(data[0]+data[1]+data[2]+data[3]))
            glp_CvAllB = float(data[3]/(data[0]+data[1]+data[2]+data[3]))

        if data[3]+data[4]+data[5]>0:
            glp_CvLFOther = float(data[3]/(data[3]+data[4]+data[5]))
            glp_LFOthervC = float((data[4]+data[5])/(data[3]+data[4]+data[5]))


    wrapper.branchArrays["glp_highest_node"][0] = int(node)

    wrapper.branchArrays["glp_ttB"][0] = glp_ttB
    wrapper.branchArrays["glp_ttHB"][0] = glp_ttHB
    wrapper.branchArrays["glp_ttZB"][0] = glp_ttZB
    wrapper.branchArrays["glp_ttC"][0] = glp_ttC
    wrapper.branchArrays["glp_ttLF"][0] = glp_ttLF
    wrapper.branchArrays["glp_other"][0] = glp_other






    # BvHB
    wrapper.branchArrays["glp_BvHB"][0] = glp_BvHB 
    wrapper.branchArrays["glp_HBvB"][0] = glp_HBvB 

    # BvZB
    wrapper.branchArrays["glp_BvZB"][0] = glp_BvZB 
    wrapper.branchArrays["glp_ZBvB"][0] = glp_ZBvB 
    
    # BvC
    wrapper.branchArrays["glp_BvC"][0] = glp_BvC 
    wrapper.branchArrays["glp_CvB"][0] = glp_CvB 

    # BvLF
    wrapper.branchArrays["glp_BvLF"][0] = glp_BvLF 
    wrapper.branchArrays["glp_LFvB"][0] = glp_LFvB 

    # BvOther
    wrapper.branchArrays["glp_BvOther"][0] = glp_BvOther 
    wrapper.branchArrays["glp_OthervB"][0] = glp_OthervB 

    # HBvZB
    wrapper.branchArrays["glp_HBvZB"][0] = glp_HBvZB 
    wrapper.branchArrays["glp_ZBvHB"][0] = glp_ZBvHB 

    # HBvC
    wrapper.branchArrays["glp_HBvC"][0] = glp_HBvC 
    wrapper.branchArrays["glp_CvHB"][0] = glp_CvHB 

    # HBvLF
    wrapper.branchArrays["glp_HBvLF"][0] = glp_HBvLF 
    wrapper.branchArrays["glp_LFvHB"][0] = glp_LFvHB 

    # HBvOther
    wrapper.branchArrays["glp_HBvOther"][0] = glp_HBvOther 
    wrapper.branchArrays["glp_OthervHB"][0] = glp_OthervHB 

    # ZBvC
    wrapper.branchArrays["glp_ZBvC"][0] = glp_ZBvC 
    wrapper.branchArrays["glp_CvZB"][0] = glp_CvZB 

    # ZBvLF
    wrapper.branchArrays["glp_ZBvLF"][0] = glp_ZBvLF 
    wrapper.branchArrays["glp_LFvZB"][0] = glp_LFvZB 

    # ZBvOther
    wrapper.branchArrays["glp_ZBvOther"][0] = glp_ZBvOther 
    wrapper.branchArrays["glp_OthervZB"][0] = glp_OthervZB 

    # CvLF
    wrapper.branchArrays["glp_CvLF"][0] = glp_CvLF 
    wrapper.branchArrays["glp_LFvC"][0] = glp_LFvC 

    # CvOther
    wrapper.branchArrays["glp_CvOther"][0] = glp_CvOther 
    wrapper.branchArrays["glp_OthervC"][0] = glp_OthervC 

    # LFvOther
    wrapper.branchArrays["glp_LFvOther"][0] = glp_LFvOther 
    wrapper.branchArrays["glp_OthervLf"][0] = glp_OthervLf 

    # AllBvC
    wrapper.branchArrays["glp_AllBvC"][0] = glp_AllBvC 
    wrapper.branchArrays["glp_CvAllB"][0] = glp_CvAllB 
    
    # CvLFOther
    wrapper.branchArrays["glp_CvLFOther"][0] = glp_CvLFOther 
    wrapper.branchArrays["glp_LFOthervC"][0] = glp_LFOthervC 
    return event