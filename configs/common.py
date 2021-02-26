import ROOT
import numpy as np

class Vectors:
    def __init__(self, event, name = "", objList = []):
        self.vectors = {}
        self.isTree = True
        self.length = 1
        if type(event) != ROOT.TTree:
            self.isTree = False
            self.length = event.shape[0]

        for obj in objList:
            self.vectors[obj] = np.array([ROOT.TLorentzVector() for _ in range(self.length)])

        if self.isTree:
            for obj in objList:
                self.vectors[obj][0].SetPtEtaPhiE(
                    eval("event."+name+"_"+obj+"_Pt"),
                    eval("event."+name+"_"+obj+"_Eta"),
                    eval("event."+name+"_"+obj+"_Phi"),
                    eval("event."+name+"_"+obj+"_E")
                    )
        else:
            for i, entry in event.iterrows():
                for obj in objList:
                    self.vectors[obj][i].SetPtEtaPhiE( 
                        entry[name+"_"+obj+"_Pt"], 
                        entry[name+"_"+obj+"_Eta"], 
                        entry[name+"_"+obj+"_Phi"], 
                        entry[name+"_"+obj+"_E"] 
                        ) 

    def add(self, objList, out):
        if not len(objList)>=2: exit("cannot add only one object vector")

        self.vectors[out] = np.copy(self.vectors[objList[0]])
        for obj in objList[1:]:
            self.vectors[out]+= self.vectors[obj]
    
    def get(self, obj, feat, boostFrame = None):
        if not boostFrame is None:
            obj+="_boosted_"+boostFrame

        if feat == "Pt":
            return [x.Pt() for x in self.vectors[obj]]
        if feat == "Px":
            return [x.Px() for x in self.vectors[obj]]
        if feat == "Py":
            return [x.Py() for x in self.vectors[obj]]
        if feat == "Pz":
            return [x.Pz() for x in self.vectors[obj]]
        if feat == "Phi":
            return [x.Phi() for x in self.vectors[obj]]
        if feat == "Eta":
            return [x.Eta() for x in self.vectors[obj]]
        if feat == "E":
            return [x.E() for x in self.vectors[obj]]
        if feat == "M":
            return [x.M() for x in self.vectors[obj]]
            

    def boost(self, objList, frame):
        for obj in objList:
            boostName = obj+"_boosted_"+frame
            self.vectors[boostName] = np.copy(self.vectors[obj])
            for i in range(len(self.vectors[obj])):
                self.vectors[boostName][i].Boost(-self.vectors[frame][i].BoostVector())

    def getOpeningAngle(self, obj1, obj2):
        vectors1 = self.vectors[obj1]
        vectors2 = self.vectors[obj2]
        return [vectors1[i].Angle(vectors2[i].Vect()) for i in range(len(vectors1))]

    def initIndexedVector(self, event, obj, idx):
        self.vectors[obj+"_"+str(idx)] = np.array([ROOT.TLorentzVector() for _ in range(self.length)])
        if self.isTree:
            self.vectors[obj+"_"+str(idx)][0].SetPtEtaPhiE(
                eval("event."+obj+"_Pt[{}]".format(idx)),
                eval("event."+obj+"_Eta[{}]".format(idx)),
                eval("event."+obj+"_Phi[{}]".format(idx)),
                eval("event."+obj+"_E[{}]".format(idx))
                )
        else:
            for i, entry in event.iterrows():
                self.vectors[obj+"_"+str(idx)][i].SetPtEtaPhiE(
                    entry[obj+"_Pt[{}]".format(idx)],
                    entry[obj+"_Eta[{}]".format(idx)],
                    entry[obj+"_Phi[{}]".format(idx)],
                    entry[obj+"_E[{}]".format(idx)]
                    )

    def addNeutrino(self, event, metPt, metPhi, lepName):
        self.vectors["nu"] = np.array([ROOT.TLorentzVector() for _ in range(event.shape[0])])
        nu_px = event[metPt].values*np.cos(event[metPhi].values)
        nu_py = event[metPt].values*np.sin(event[metPhi].values)
        
        mu = (80.4**2/2.) + self.get(lepName, "Px")*nu_px + self.get(lepName, "Py")*nu_py
        a  = (mu * self.get(lepName, "Pz"))/(np.power(self.get(lepName, "Pt"),2))
        a2 = a**2
        b  = (np.power(self.get(lepName, "E"),2)*np.power(event[metPt].values,2) - mu**2)/(np.power(self.get(lepName, "Pt"),2)) 

        for i, entry in event.iterrows():
            if a2[i] < b[i]:
                pz = a[i]
            else:
                pz1 = a[i]+(a2[i]-b[i])**0.5
                pz2 = a[i]-(a2[i]-b[i])**0.5
                if abs(pz1) <= abs(pz2):
                    pz = pz1
                else:
                    pz = pz2
            self.vectors["nu"][i].SetPxPyPzE(
                nu_px[i], nu_py[i], pz, 0.)
            self.vectors["nu"][i].SetE(
                self.vectors["nu"][i].P())




def get_dPhi(phi1, phi2):
    dphi = abs(phi1-phi2)
    return dphi*(dphi<np.pi)+(2.*np.pi-dphi)*(dphi>=np.pi)


def get_dEta(eta1, eta2):
    deta = abs(eta1-eta2)
    return deta

def get_dR(eta1, phi1, eta2, phi2):
    dphi = get_dPhi(phi1, phi2)
    deta = get_dEta(eta1, eta2)
    dr = np.sqrt(dphi**2 + deta**2)
    return dr

