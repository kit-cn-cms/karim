import ROOT
import os
from array import array

class InputFile(object):
    '''
    open input file and return MVATree
    '''
    def __init__(self, filename, friendTrees = []):
        self.file = ROOT.TFile(filename)
        self.tree = self.file.Get("MVATree")
        
        print("\nloading tree with {nentries} entries\n".format(
            nentries = self.tree.GetEntries()))
        
        for ft in friendTrees:
            print("adding friendTree {}".format(ft))
            self.tree.AddFriend("MVATree", ft)        

    def __enter__(self):
        return self.tree

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.file.Close()



class TreeIterator:
    '''
    iterate over tree entries
        
    yields: DataFrame of all jet assignment hypotheses
    '''
    def __init__(self, tree, Hypotheses = None):
        self.tree = tree
        self.Hypotheses = Hypotheses

    def __iter__(self):
        self.idx = 0
        self.max = self.tree.GetEntries()
        self.pstep = 100
        self.scale = 100000
        # ToDo add branch address initialization?
        self.timer = ROOT.TStopwatch()
        self.timer.Start()
        return self

    def next(self):
        if self.idx%self.pstep==0 and self.idx>0:
            print("at event {}/{}".format(self.idx, self.max))
            print("  time for {} events:  {:.1f} s".format(self.pstep, self.timer.RealTime()))
            print("  estimated time for {} events: {:.0f} min".format(
                self.scale, self.timer.RealTime()/self.pstep*self.scale/60.))
            self.timer.Start()

        if self.idx < self.max:
            self.tree.GetEntry(self.idx)
            self.idx+=1

            return self.tree
            #if not self.Hypotheses is None:
            #    return self.Hypotheses.GetPermutations(self.tree, self.tree.N_Jets)
            #else:
                
        else:
            raise StopIteration
 


   
class OutputFile(object):
    '''
    recreate output file and initialize new MVATree
    write rootfile, and cutflow file upon exit
    '''
    def __init__(self, filename):
        self.name = filename
        self.setSampleName()
        self.file = ROOT.TFile(self.name, "RECREATE")
        self.tree = ROOT.TTree("MVATree","RecoTree")
        print("\nwriting info to file {}\n".format(self.name))

        self.branchArrays = {}

    def __enter__(self):
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        nentries = self.tree.GetEntries()
        self.file.Write()
        self.file.Close()
        with open(self.name.replace(".root",".cutflow.txt"), "w") as cff:
            cff.write("entries : {}".format(nentries))
        print("file {} written.".format(self.name))
        print("\n"+"="*50+"\n")
  
    def setSampleName(self):
        treeName = os.path.basename(self.name)
        treeName = treeName.replace("_Tree.root","")
        split = treeName.split("_")
        self.sampleName = "_".join(split[:-2])

    def SetBranches(self, variables):
        '''
        initialize branches for tree
        currently all trees are of datatype float
        '''
        self.branchArrays = []
        for i, v in enumerate(variables):
            outvar = v.replace("[","_").replace("]","")
            self.branchArrays.append(
                array("f", [0.]))
            self.tree.Branch(outvar, self.branchArrays[i], "{}/F".format(outvar))

    def FillTree(self, event = None):
        ''' 
        fill event into tree
        '''
        if not event is None:
            for i, val in enumerate(event):
                self.branchArrays[i][0] = val
        self.tree.Fill()

    def SetConfigBranches(self, config):
        config.set_branches(self)

    def SetIntVar(self, var):
        self.branchArrays[var] = array("l", [0]) 
        self.tree.Branch(var, self.branchArrays[var], "{}/L".format(var))

    def SetFloatVar(self, var):
        self.branchArrays[var] = array("f", [0.]) 
        self.tree.Branch(var, self.branchArrays[var], "{}/F".format(var))

    def SetFloatVarArray(self, var, idx):
        self.branchArrays[var] = array("f", [0.]*20)
        self.tree.Branch(var, self.branchArrays[var], "{}[{}]/F".format(var, idx))

    def ClearArrays(self):
        for key in self.branchArrays:
            for i in range(len(self.branchArrays[key])):
                if type(self.branchArrays[key][i]) == int:
                    self.branchArrays[key][i] = 0
                else:
                    self.branchArrays[key][i] = 0.
