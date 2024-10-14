import numpy as np
import common
import weightModules
from array import array
import os
from torch_geometric.data import InMemoryDataset, Data, Dataset
from itertools import combinations, product
import torch
from torch_geometric.loader import DataLoader
from collections import namedtuple
from torch_geometric.nn import TransformerConv
from torch.nn import Linear, BatchNorm1d, ModuleList
import torch.nn.functional as F

class Net1(torch.nn.Module):
    def __init__(self, run):
        super().__init__()
        self.name = "TRANSF"
        features = run.features
        edge_dim = run.edge_dim
        embedding_size = run.embedding_size
        n_layers = run.n_layers
        batch_norm = run.batch_norm
        relu = run.relu
        dropout = run.dropout

        aggr = run.aggr
        heads = run.heads
        beta = run.beta
        dense_neurons = run.dense_neurons
        # in
        self.conv1 = TransformerConv(features, embedding_size, aggr=aggr, heads=heads, beta=beta, dropout=dropout, edge_dim=edge_dim)
        self.transf1 = Linear(embedding_size*heads, embedding_size)

        if batch_norm:
            self.bn1 = BatchNorm1d(embedding_size)



        # body
        self.bn_layers = ModuleList([])
        self.conv_layers = ModuleList([])
        self.transf_layers = ModuleList([])

        for i in range(n_layers):
            self.conv_layers.append(
                TransformerConv(embedding_size, embedding_size, aggr=aggr, heads=heads, beta=beta, dropout=dropout, edge_dim=edge_dim)
            )
            self.transf_layers.append(
                Linear(embedding_size*heads, embedding_size)
            )
            if batch_norm:
                self.bn_layers.append(
                    BatchNorm1d(embedding_size)
                )

        # out
        self.lin_out1 = Linear(embedding_size, dense_neurons)
        self.lin_out2 = Linear(dense_neurons, int(dense_neurons/2))
        self.lin_out3 = Linear(int(dense_neurons/2), 1)

    def forward(self, batch, run):
        x = batch.x
        x = x[:,:run.features]
        edge_index = batch.edge_index   
        edge_attr = batch.edge_attr
        n_layers = run.n_layers
        dropout = run.dropout
        batch_norm = run.batch_norm
        relu = run.relu

        x = self.conv1(x, edge_index, edge_attr)
        x = self.transf1(x)
        if relu:
            x = torch.relu(x)
        if batch_norm:
            x = self.bn1(x)


        for i in range(n_layers):
            x = self.conv_layers[i](x, edge_index, edge_attr)
            x = self.transf_layers[i](x)
            if relu:
                x = torch.relu(x)            
            if batch_norm:
                x = self.bn_layers[i](x)
        
        x = self.lin_out1(x)
        if relu:
            x = torch.relu(x)        
        x = F.dropout(x, p=dropout, training=self.training)

        x = self.lin_out2(x)
        if relu:
            x = torch.relu(x)        
        x = F.dropout(x, p=dropout, training=self.training)
        x = self.lin_out3(x)
        
        x = torch.sigmoid(x)
        return x

class FullyRecIM(InMemoryDataset):
    def __init__(self, root, entry, transform=None, pre_transform=None):
        super().__init__(root, transform, pre_transform)
        self.data, self.slices = torch.load(self.processed_paths[0])
        self.entry = entry

    @property
    def raw_file_names(self):
        return []

    @property
    def processed_file_names(self):
        return ['simulation_dilep.pt']

    def download(self):
        pass

    def _dPhi(self, phi1, phi2):
        dphi = abs(phi1-phi2)
        return dphi*(dphi<np.pi)+(2.*np.pi-dphi)*(dphi>=np.pi)
    
    def _dEta(self, eta1, eta2):
        return abs(eta1-eta2)

    def _dR(self, eta1, phi1, eta2, phi2):
        dphi = self._dPhi(phi1, phi2)
        deta = self._dEta(eta1, eta2)

        dR = np.sqrt(dphi*dphi + deta*deta)
        return dR

    def _Minv(self, pt1, eta1, phi1, pt2, eta2, phi2):
        dphi = self._dPhi(phi1, phi2)
        deta = self._dEta(eta1, eta2)
        return np.sqrt(2*pt1*pt2*(np.cosh(deta) - np.cos(dphi)))

    def _get_edge_index(self, num_nodes, selfloops=False):
        if selfloops:
            edge_index = torch.tensor(list(product(range(num_nodes), range(num_nodes))), dtype=torch.long)
            edge_index = edge_index.t().contiguous()
        else:
            edge_index = torch.tensor(list(combinations(range(num_nodes), 2)), dtype=torch.long).T
            swap_index = torch.stack((edge_index[1], edge_index[0]))
            edge_index = torch.cat((edge_index, swap_index), 1)

        return edge_index

    def _get_edge_attr(self, Pt, Phi, Eta, edge_index):

        dR = torch.tensor([self._dR(Eta[edge[0]], Phi[edge[0]], Eta[edge[1]], Phi[edge[1]]) for edge in edge_index.t()])
        dR = dR.squeeze()
        Minv = torch.tensor([self._Minv(Pt[edge[0]], Eta[edge[0]], Phi[edge[0]], Pt[edge[1]], Eta[edge[1]], Phi[edge[1]]) for edge in edge_index.t()])
        Minv = Minv.squeeze()
        edge_attr = torch.stack([dR, Minv], dim=1)

        return edge_attr

    def _global_features(self, groups):
        keys = ["Pt", "Phi", "Eta", "M", "E"]
        features_list = {"dR": [], "Minv": []}

        for _, group in groups:
            num_nodes = len(group)
            for key in keys:
                if key not in features_list:
                    features_list[key] = []
                features_list[key].extend(group[key].values)
            edges = list(combinations(range(num_nodes), 2))
            dR = [self._dR(group["Eta"].values[x[0]], group["Phi"].values[x[0]], group["Eta"].values[x[1]], group["Phi"].values[x[1]]) for x in edges]
            Minv = [self._Minv(group["Pt"].values[x[0]], group["Eta"].values[x[0]], group["Phi"].values[x[0]], group["Pt"].values[x[1]], group["Eta"].values[x[1]], group["Phi"].values[x[1]]) for x in edges]
            features_list["dR"].extend(dR)
            features_list["Minv"].extend(Minv)

        global_features = {}
        for key in features_list:
            mean = torch.mean(torch.tensor(features_list[key]))
            std = torch.std(torch.tensor(features_list[key]))
            max = torch.max(torch.tensor(features_list[key]))
            min = torch.min(torch.tensor(features_list[key]))
            quantile = torch.quantile(torch.tensor(features_list[key]), 0.99)
            global_features[key] = {"mean": float(mean), "std": float(std), "max": float(max), "min": float(min), "quantile": float(quantile)}

        return global_features

    def _transform(self, x, edge_attr):
        for key in self.global_features:
            if key in self.x_attr_names:
                index = self.x_attr_names.index(key)
                x[:,index] = (x[:,index] - self.global_features[key]["mean"]) / self.global_features[key]["std"]

            elif key in self.edge_attr_names:
                index = self.edge_attr_names.index(key)
                edge_attr[:,index] = edge_attr[:,index]/self.global_features[key]["quantile"]
        return x, edge_attr


    def process(self):
        entry = self.entry
        # Read data into huge `Data` list.
        data_list = []
        
        num_nodes = entry.nJets_nom + entry.nLep + 1
        x = []
        for iJet in range(entry.nJets_nom):
            x.append([
                entry.Jet_Pt_nom[iJet],
                entry.Jet_Phi_nom[iJet],
                entry.Jet_Eta_nom[iJet],
                entry.Jet_M_nom[iJet],
                entry.Jet_E_nom[iJet],
                0,
                entry.Jet_btagValue_nom[iJet],
                entry.Jet_CvL_nom[iJet],
                entry.Jet_CvB_nom[iJet],
                1,
                0,
                0,
            ])
        for iLep in range(entry.nLep):
            x.append([
                entry.Lep_Pt[iJet],
                entry.Lep_Phi[iJet],
                entry.Lep_Eta[iJet],
                entry.Lep_M[iJet],
                entry.Lep_E[iJet],
                entry.Lep_Charge[iLep],
                0,
                0,
                0,
                0,
                1,
                0,
            ])                
        x.append([
            entry.MET_T1_Pt_nom,
            entry.MET_T1_Phi_nom,
            0,
            0,
            entry.MET_T1_Pt_nom,
            0,
            0,
            0,
            0,
            0,
            0,
            1,
        ])
        x = torch.tensor(x)
        edge_index = self._get_edge_index(num_nodes)
        edge_attr = self._get_edge_attr(x[:,0], x[:,1], x[:,2], edge_index)
        x, edge_attr = self._transform(x, edge_attr)
        data = Data(x=x, edge_index=edge_index, edge_attr=edge_attr)

        data_list.append(data)



filepath = os.path.abspath(__file__)
karimpath = os.path.dirname(os.path.dirname(filepath))


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

    # gen dataset

    wrapper.SetFloatVarArray("eval_jets","nJets_nom")
    wrapper.SetFloatVarArray("eval_lep", "nLep")
    wrapper.SetFloatVar("eval_et")

def calculate_variables(event, wrapper, sample, jec = None, dataEra = None, genWeights = None):
    '''
    calculate weights
    '''
    print("ssdf")
    input()
    Run = namedtuple('Run', ["embedding_size", "dropout", "n_layers", "batch_norm", "relu", "aggr", "head", "beta", "dense_neurons"])
    r = Run(38, 0.1, 4, True, True, "add", 1, False, 64)
    net = Net1(run=r).double()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dataset = FullyRecIM("", entry=event)
    loader = DataLoader(dataset, batch_size=len(dataset), shuffle=False)
    for batch in loader:
        batch.to(device)
        net.load_state_dict(torch.load("/nfs/dust/cms/user/merhart/graph-maga/configs/train_add_all/out_7/nets/best_network_run_37.pt"))
        net.eval()
        preds = net(batch=batch, run=r)
        
    # add basic information for friend trees
    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")

    for iJet in range(event.nJets_nom):
        wrapper.branchArrays["eval_jets"][iJet] = preds[iJet]

    for iLep in range(event.nLeps):
        wrapper.branchArrays["eval_lep"][iLep] = preds[event.nJets_nom + iLep]
    wrapper.branchArrays["eval_et"][0] = preds[event.nJets_nom + 2]

    return event

