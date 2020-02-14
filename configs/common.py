import ROOT
import numpy as np

class Vectors:
    def __init__(self, df, name, objList):
        self.vectors = {}
        for obj in objList:
            self.vectors[obj] = np.array([ROOT.TLorentzVector() for _ in range(df.shape[0])])

        for i, entry in df.iterrows():
            for obj in objList:
                self.vectors[obj][i].SetPtEtaPhiE( 
                    entry[name+"_"+obj+"_Pt"], 
                    entry[name+"_"+obj+"_Eta"], 
                    entry[name+"_"+obj+"_Phi"], 
                    entry[name+"_"+obj+"_E"] 
                    ) 

    def add(self, objList, out):
        if not len(objList)>=2: exit("cannot add only one object vector")

        self.vectors[out] = self.vectors[objList[0]]
        for obj in objList[1:]:
            self.vectors[out]+= self.vectors[obj]
    
    def get(self, obj, feat):
        if feat == "Pt":
            return [x.Pt() for x in self.vectors[obj]]
        if feat == "Phi":
            return [x.Phi() for x in self.vectors[obj]]
        if feat == "Eta":
            return [x.Eta() for x in self.vectors[obj]]
        if feat == "E":
            return [x.E() for x in self.vectors[obj]]
        if feat == "M":
            return [x.M() for x in self.vectors[obj]]

def get_dPhi(phi1, phi2):
    dphi = abs(phi1-phi2)
    return dphi*(dphi<np.pi)+(2.*np.pi-dphi)*(dphi>=np.pi)
