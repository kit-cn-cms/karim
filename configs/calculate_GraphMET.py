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


import models.model.net as net
import models.model.utils as utils

def evaluate(model, device, loss_fn, dataloader, metrics, deltaR, deltaR_dz, model_dir, out='', mode="fix"):
    # set model to evaluation mode
    model.eval()
    with torch.no_grad():
        for data in dataloader:

            if len(dataloader)!= 1:
                print("length of dataloader list should be one")
                break

            data = data.to(device)

            phi = torch.atan2(data.x[:,1], data.x[:,0])
            etaphi = torch.cat([data.x[:,3][:,None], phi[:,None]], dim=1)
            edge_index = radius_graph(etaphi, r=deltaR, batch=data.batch, loop=True, max_num_neighbors=500)

            weights = model(data.x, edge_index=edge_index, batch=data.batch)
    
            METx = -scatter_add(weights*data.x[:,0], data.batch)
            METy = -scatter_add(weights*data.x[:,1], data.batch)
    
    MET_pt = (METx**2 + METy**2)**.5
    MET_phi = torch.atan(METy*1./ METx)

    return MET_pt, MET_phi


def load_pfinfo(event, batch_size=None, shuffle=False):
    # print("Start loading events")
    event_list = np.column_stack([
        np.multiply(np.array(getattr(event, "PFCands_pt")), np.cos(np.array(getattr(event, "PFCands_phi")))),
        np.multiply(np.array(getattr(event, "PFCands_pt")), np.sin(np.array(getattr(event, "PFCands_phi")))),
        np.array(getattr(event, "PFCands_pt")),
        np.array(getattr(event, "PFCands_eta")),
        np.array(getattr(event, "PFCands_d0")),
        np.array(getattr(event, "PFCands_dz")),
        np.array(getattr(event, "PFCands_puppiWeight")),
        np.array(getattr(event, "PFCands_mass")),
        np.array(getattr(event, "PFCands_pdgId")),
        np.array(getattr(event, "PFCands_charge")),
        np.array(getattr(event, "PFCands_fromPV")),
    ])
    edge_index = torch.empty((2,0), dtype=torch.long)

    outData = [Data(x=torch.FloatTensor(event_list), edge_index = edge_index)]
    data = DataLoader(outData, batch_size=1, shuffle=False)
    return data


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

    wrapper.SetIntVar("Evt_ID")   
    wrapper.SetIntVar("Evt_Run")   
    wrapper.SetIntVar("Evt_Lumi")   

    wrapper.SetFloatVar("GraphMET_pt")
    wrapper.SetFloatVar("GraphMET_phi")


def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):

    # add basic information for friend trees
    wrapper.branchArrays["Evt_ID"][0] = getattr(event, "Evt_ID")
    wrapper.branchArrays["Evt_Run"][0]   = getattr(event, "Evt_Run")
    wrapper.branchArrays["Evt_Lumi"][0]  = getattr(event, "Evt_Lumi")

    # load PF data from one event into torch dataloader
    data = load_pfinfo(event, batch_size=1, shuffle=False)

    # set settings for inference
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = net.Net(7, 3, output_dim=1, hidden_dim=32, conv_depth=4, mode="fix").to(device)
    optimizer = torch.optim.AdamW(model.parameters(),lr=0.001)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=500, threshold=0.05)

    loss_fn = net.loss_fn
    metrics = net.metrics
    # print(os.environ["PWD"])
    model_dir = osp.join("/nfs/dust/cms/user/jdriesch/monotopv2/karim","models/znunu_fix_500nbs_4l_dim32")
    deltaR = 0.4
    deltaR_dz = 10

    # Reload weights from the saved file
    restore_ckpt = osp.join(model_dir, 'best.pth.tar')
    # print(restore_ckpt)
    ckpt = utils.load_checkpoint(restore_ckpt, model, optimizer, scheduler, device)
    epoch = ckpt['epoch']
    #utils.load_checkpoint(os.path.join(model_dir, args.restore_file + '.pth.tar'), model)
    with open(osp.join(model_dir, 'metrics_val_best.json')) as restore_metrics:
        best_validation_loss = json.load(restore_metrics)['loss']    

    MET_pt, MET_phi= evaluate(model, device, loss_fn, data, metrics, deltaR, deltaR_dz, model_dir, "fix")


    wrapper.branchArrays["GraphMET_pt"][0]  = MET_pt
    wrapper.branchArrays["GraphMET_phi"][0] = MET_phi

    return event