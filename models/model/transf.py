import torch
import pandas as pd
import numpy as np
from torch_geometric.nn import TransformerConv
from torch.nn import Linear, BatchNorm1d, ModuleList
import torch.nn.functional as F

class Net(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.name = "TRANSF"
        features = 12
        edge_dim = 2
        embedding_size = 32
        n_layers = 4
        batch_norm = True
        relu = True
        dropout = 0.1

        aggr = "add"
        heads = 2
        beta = False
        dense_neurons = 64
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

    def forward(self, batch):
        x = batch.x
        edge_index = batch.edge_index   
        edge_attr = batch.edge_attr
        n_layers = 4
        dropout = 0.1
        batch_norm = True
        relu = True

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
        # print(x)
        # print(len(x))
        x = torch.sigmoid(x)
        # x = self.logsoftmax(x)
        # input()
        return x