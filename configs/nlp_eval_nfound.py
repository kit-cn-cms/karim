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


def calculate_variables(event, wrapper, sample, jec, dataEra = None, genWeights = None):

    wrapper.branchArrays["event"][0] = getattr(event, "event")
    wrapper.branchArrays["run"][0]   = getattr(event, "run")
    wrapper.branchArrays["lumi"][0]  = getattr(event, "lumi")
    wrapper.branchArrays["nJets"][0]  = event.nJets_nom
    wrapper.branchArrays["nLep"][0]  = event.nLep





       



    
    return event