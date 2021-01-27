import pandas as pd
import ROOT
import uproot
import numpy as np

import sys
import os
inf = sys.argv[1]
if not inf.endswith("_db.root"):
    sys.exit("not a valid name for database file, should end with '_db.root'")
f = ROOT.TFile(inf)
t = f.Get("Events")
branches = list([b.GetName() for b in t.GetListOfBranches()])
meta    = [b for b in branches if not b.startswith("weight")]

print("opening...")
with uproot.open(inf) as f:
    tree = f["Events"]
    
outf = inf.replace("_db.root","_idx.h5")

print("converting...")
df = tree.pandas.df(meta)
print("saving...")
df.to_hdf(outf, key = "store")
del df
