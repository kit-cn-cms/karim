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

from models.model.transf import Net

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
    # global_features = {'dR': {'mean': 2.2037378838908066, 'std': 0.9051687742485897, 'max': 5.6947613226739735, 'min': 0.004195193731893499, 'quantile': 4.244001078650436}, 'Minv': {'mean': 175.18311278313905, 'std': 162.82510570661043, 'max': 8034.468646211956, 'min': 0.210453262505733, 'quantile': 796.0236877148421}, 'Pt': {'mean': 95.77306682706848, 'std': 103.04040607050104, 'max': 2783.923095703125, 'min': 0.630344569683075, 'quantile': 505.1054302978518}, 'Phi': {'mean': 0.01604827361664354, 'std': 1.806203951859251, 'max': 3.1415836811065674, 'min': -3.1415836811065674, 'quantile': 3.0791015625}, 'Eta': {'mean': -0.0019048697871781805, 'std': 1.058123500737131, 'max': 2.39990234375, 'min': -2.39990234375, 'quantile': 2.2548828125}, 'M': {'mean': 8.508376569935008, 'std': 11.244349720156654, 'max': 372.5978698730469, 'min': -0.75048828125, 'quantile': 49.97843158721924}, 'E': {'mean': 157.33960213164076, 'std': 183.65642124382114, 'max': 5245.314453125, 'min': 0.630344569683075, 'quantile': 949.5493884277362}}
    global_features = {'dR': {'mean': 2.197342904001925, 'std': 0.9128640977686767, 'max': 5.686710916003588, 'min': 0.002069431354086177, 'quantile': 4.249086899510989}, 'Minv': {'mean': 182.60352912155972, 'std': 168.33981307856388, 'max': 4847.367937890147, 'min': 0.09109102912289697, 'quantile': 853.3743187020467}, 'Pt': {'mean': 100.8522543730786, 'std': 101.35340122800761, 'max': 2507.687255859375, 'min': 0.1224859505891799, 'quantile': 549.8974304199221}, 'Phi': {'mean': 0.018032960976131024, 'std': 1.8041834655314832, 'max': 3.1415836811065674, 'min': -3.1415836811065674, 'quantile': 3.078125}, 'Eta': {'mean': -0.0022764860733743126, 'std': 1.0651182999140745, 'max': 2.39990234375, 'min': -2.39990234375, 'quantile': 2.2587890625}, 'M': {'mean': 8.921484245964658, 'std': 11.603906339919384, 'max': 285.0723876953125, 'min': -0.97705078125, 'quantile': 53.94807807922368}, 'E': {'mean': 167.5675965295591, 'std': 193.67184117219793, 'max': 4553.6494140625, 'min': 0.1224859505891799, 'quantile': 1003.0930334472656}}       
    # global_features = {'dR': {'mean': 2.2021236276936063, 'std': 0.9055800931389962, 'max': 5.697980709663296, 'min': 0.00013025863929147987, 'quantile': 4.243693009177999}, 'Minv': {'mean': 171.64648611884365, 'std': 147.74056263338147, 'max': 6263.4296366676, 'min': 0.007345622249879813, 'quantile': 748.0251600010178}, 'dEta': {'mean': 1.1202627896547162, 'std': 0.8348680388451585, 'max': 4.79345703125, 'min': 0.0, 'quantile': 3.607421875}, 'dPhi': {'mean': 1.6998042282883998, 'std': 0.9099978277678368, 'max': 3.1415913740741175, 'min': 0.0, 'quantile': 3.1171696821795862}, 'ptinv': {'mean': 128.28310895754768, 'std': 105.9247958997645, 'max': 2517.3676249276705, 'min': 0.02190041938002916, 'quantile': 556.2345370588237}, 'Pt': {'mean': 92.85410524906729, 'std': 85.20228970744942, 'max': 2507.687255859375, 'min': 0.1211781799793243, 'quantile': 453.14086303710934}, 'Phi': {'mean': 0.013448930139404108, 'std': 1.8077399710296571, 'max': 3.1415884494781494, 'min': -3.1415836811065674, 'quantile': 3.07763671875}, 'Eta': {'mean': -0.0013648644460376033, 'std': 1.0622274902986972, 'max': 2.39990234375, 'min': -2.39990234375, 'quantile': 2.259765625}, 'M': {'mean': 8.289678370533457, 'std': 10.27323974973743, 'max': 314.4720153808594, 'min': -0.8251953125, 'quantile': 46.0891229248046}, 'E': {'mean': 154.43052754258625, 'std': 169.44390224172824, 'max': 4553.6494140625, 'min': 0.1211781799793243, 'quantile': 876.1235034179685}}

    x_attr_names = ["Pt", "Phi", "Eta", "M", "E", "charge", "btagValue", "CvL",
            "CvB", "is_Jet", "is_Lep", "is_missing"]
    edge_attr_names = ["dR", "Minv"]
    for key in global_features:
        if key in x_attr_names:
            index = x_attr_names.index(key)
            x[:,index] = (x[:,index] - global_features[key]["mean"]) / global_features[key]["std"]

        elif key in edge_attr_names:
            index = edge_attr_names.index(key)
            edge_attr[:,index] = edge_attr[:,index]/global_features[key]["quantile"]
    return x, edge_attr

def load_data(event):
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
    
    wrapper.SetIntVar("nJets")   
    wrapper.SetIntVar("nLep")

    wrapper.SetFloatVarArray("Lep_Pt", "nLep")
    wrapper.SetFloatVarArray("Jet_Pt", "nJets")

    wrapper.SetFloatVar("eval_met")
    wrapper.SetFloatVarArray("eval_jets", "nJets")
    wrapper.SetFloatVarArray("eval_lep", "nLep")

    wrapper.SetIntVar("nlp_not_jet_pred")

    wrapper.SetIntVar("nlp_top_first_idx")
    wrapper.SetIntVar("nlp_top_second_idx")

    wrapper.SetFloatVar("nlp_top_first_Pt")
    wrapper.SetFloatVar("nlp_top_second_Pt")

    wrapper.SetFloatVar("nlp_top_first_Phi")
    wrapper.SetFloatVar("nlp_top_second_Phi")

    wrapper.SetFloatVar("nlp_top_first_Eta")
    wrapper.SetFloatVar("nlp_top_second_Eta")

    wrapper.SetFloatVar("nlp_top_first_M")
    wrapper.SetFloatVar("nlp_top_second_M")

    wrapper.SetFloatVar("nlp_top_first_E")
    wrapper.SetFloatVar("nlp_top_second_E")

    wrapper.SetFloatVar("nlp_top_first_btagValue")
    wrapper.SetFloatVar("nlp_top_second_btagValue")

    wrapper.SetFloatVar("nlp_top_first_CvL")
    wrapper.SetFloatVar("nlp_top_second_CvL")

    wrapper.SetFloatVar("nlp_top_first_CvB")
    wrapper.SetFloatVar("nlp_top_second_CvB")

    wrapper.SetFloatVar("nlp_top_dR")
    wrapper.SetFloatVar("nlp_top_minv")

    wrapper.SetIntVar("nlp_TP")
    wrapper.SetIntVar("nlp_FN")
    wrapper.SetIntVar("nlp_FP")
    wrapper.SetIntVar("nlp_TN")

def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):

    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    wrapper.branchArrays["nJets"][0]  = event.nJets_nom
    wrapper.branchArrays["nLep"][0]  = event.nLep
    for iJet in range(event.nJets_nom):
        wrapper.branchArrays["Jet_Pt"][iJet] = float(event.Jet_Pt_nom[iJet])
    for iLep in range(event.nLep):
        wrapper.branchArrays["Lep_Pt"][iLep] = float(event.Lep_Pt[iLep])

    nlp_not_jet_pred = 0        
    nlp_top_first_idx = 0
    nlp_top_first_Pt = 0
    nlp_top_first_Phi = 0
    nlp_top_first_Eta = 0
    nlp_top_first_M = 0
    nlp_top_first_E = 0
    nlp_top_first_btagValue = 0
    nlp_top_first_CvL = 0
    nlp_top_first_CvB = 0
    nlp_top_second_idx = 0
    nlp_top_second_Pt = 0
    nlp_top_second_Phi = 0
    nlp_top_second_Eta = 0
    nlp_top_second_M = 0
    nlp_top_second_E = 0
    nlp_top_second_btagValue = 0
    nlp_top_second_CvL = 0
    nlp_top_second_CvB = 0
    nlp_top_dR = 0
    nlp_top_minv = 0
    nlp_TP = 0
    nlp_FP = 0
    nlp_FN = 0
    nlp_TN = 0
    data = [0,0,0]
    if event.nJets_nom>0:

        # load PF data from one event into torch dataloader
        dataloader = load_data(event)

        # set settings for inference
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        model = Net()

        model.load_state_dict(torch.load("/nfs/dust/cms/user/merhart/karim/models/model/best_network_rep_2_run_219.pt", map_location=torch.device(device)))

        data = evaluate(model, dataloader, device).squeeze()
        _, topidx = data.topk(2)

        for idx in topidx:
            if event.nJets_nom<=idx:
                nlp_not_jet_pred=1

        # if nlp_not_jet_pred==0:



        if event.addjet_1 in topidx:
            nlp_TP += 1
        elif event.addjet_1>-1:
            nlp_FN += 1
        

        if event.addjet_2 in topidx:
            nlp_TP += 1
        elif event.addjet_2>-1:
            nlp_FN += 1

        nlp_FP = event.nAdd - nlp_TP
        nlp_TN = event.nJets_nom - nlp_TP - nlp_FP - nlp_FN




        nlp_top_first_idx = topidx[0]
        nlp_top_first_Pt = event.Jet_Pt_nom[topidx[0]]
        nlp_top_first_Phi = event.Jet_Phi_nom[topidx[0]]
        nlp_top_first_Eta = event.Jet_Eta_nom[topidx[0]]
        nlp_top_first_M = event.Jet_M_nom[topidx[0]]
        nlp_top_first_E = event.Jet_E_nom[topidx[0]]
        nlp_top_first_btagValue = event.Jet_btagValue_nom[topidx[0]]
        nlp_top_first_CvL = event.Jet_CvL_nom[topidx[0]]
        nlp_top_first_CvB = event.Jet_CvB_nom[topidx[0]]

        nlp_top_second_idx = topidx[1]
        nlp_top_second_Pt = event.Jet_Pt_nom[topidx[1]]
        nlp_top_second_Phi = event.Jet_Phi_nom[topidx[1]]
        nlp_top_second_Eta = event.Jet_Eta_nom[topidx[1]]
        nlp_top_second_M = event.Jet_M_nom[topidx[1]]
        nlp_top_second_E = event.Jet_E_nom[topidx[1]]
        nlp_top_second_btagValue = event.Jet_btagValue_nom[topidx[1]]
        nlp_top_second_CvL = event.Jet_CvL_nom[topidx[1]]
        nlp_top_second_CvB = event.Jet_CvB_nom[topidx[1]]

        nlp_top_dR = get_dR(nlp_top_first_Eta, nlp_top_first_Phi, nlp_top_second_Eta, nlp_top_second_Phi)
        nlp_top_minv = get_Minv(nlp_top_first_Pt, nlp_top_first_Eta, nlp_top_first_Phi, nlp_top_second_Pt, nlp_top_second_Eta, nlp_top_second_Phi)


    for iJet in range(event.nJets_nom):
        wrapper.branchArrays["eval_jets"][iJet] = float(data[iJet])
    for iLep in range(event.nLep):
        wrapper.branchArrays["eval_lep"][iLep] = float(data[event.nJets_nom+iLep])
    wrapper.branchArrays["eval_met"][0] = float(data[event.nJets_nom+2])

    wrapper.branchArrays["nlp_not_jet_pred"][0] = int(nlp_not_jet_pred)




    wrapper.branchArrays["nlp_TP"][0] = int(nlp_TP)
    wrapper.branchArrays["nlp_FN"][0] = int(nlp_FN)
    wrapper.branchArrays["nlp_FP"][0] = int(nlp_FP)
    wrapper.branchArrays["nlp_TN"][0] = int(nlp_TN)

    wrapper.branchArrays["nlp_top_first_idx"][0] = int(nlp_top_first_idx)
    wrapper.branchArrays["nlp_top_first_Pt"][0] = float(nlp_top_first_Pt)
    wrapper.branchArrays["nlp_top_first_Phi"][0] = float(nlp_top_first_Phi)
    wrapper.branchArrays["nlp_top_first_Eta"][0] = float(nlp_top_first_Eta)
    wrapper.branchArrays["nlp_top_first_M"][0] = float(nlp_top_first_M)
    wrapper.branchArrays["nlp_top_first_E"][0] = float(nlp_top_first_E)
    wrapper.branchArrays["nlp_top_first_btagValue"][0] = float(nlp_top_first_btagValue)
    wrapper.branchArrays["nlp_top_first_CvL"][0] = float(nlp_top_first_CvL)
    wrapper.branchArrays["nlp_top_first_CvB"][0] = float(nlp_top_first_CvB)


    wrapper.branchArrays["nlp_top_second_idx"][0] = int(nlp_top_second_idx)
    wrapper.branchArrays["nlp_top_second_Pt"][0] = float(nlp_top_second_Pt)
    wrapper.branchArrays["nlp_top_second_Phi"][0] = float(nlp_top_second_Phi)
    wrapper.branchArrays["nlp_top_second_Eta"][0] = float(nlp_top_second_Eta)
    wrapper.branchArrays["nlp_top_second_M"][0] = float(nlp_top_second_M)
    wrapper.branchArrays["nlp_top_second_E"][0] = float(nlp_top_second_E)
    wrapper.branchArrays["nlp_top_second_btagValue"][0] = float(nlp_top_second_btagValue)
    wrapper.branchArrays["nlp_top_second_CvL"][0] = float(nlp_top_second_CvL)
    wrapper.branchArrays["nlp_top_second_CvB"][0] = float(nlp_top_second_CvB)


    wrapper.branchArrays["nlp_top_dR"][0] = nlp_top_dR
    wrapper.branchArrays["nlp_top_minv"][0] = nlp_top_minv



       



    
    return event