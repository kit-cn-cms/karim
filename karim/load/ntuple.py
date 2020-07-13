import ROOT
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
        # ToDo add branch address initialization?
        self.timer = ROOT.TStopwatch()
        self.timer.Start()
        return self

    def next(self):
        if self.idx%self.pstep==0 and self.idx>0:

            print("at event {}/{}".format(self.idx, self.max))
            print("  time for {} events:  {:.1f} s".format(self.pstep, self.timer.RealTime()))
            print("  estimated time for 50k events: {:.0f} min".format(
                self.timer.RealTime()/self.pstep*50000/60.))
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
        self.file = ROOT.TFile(self.name, "RECREATE")
        self.tree = ROOT.TTree("MVATree","RecoTree")
        print("\nwriting info to file {}\n".format(self.name))

    def __enter__(self):
        return self

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        nentries = self.tree.GetEntries()
        self.file.Write()
        self.file.Close()
        with open(self.name.replace(".root",".cutflow.txt"), "w") as cff:
            cff.write("entries : {}".format(nentries))
        print("\n"+"="*50+"\n")
       
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

    def FillTree(self, event):
        ''' 
        fill event into tree
        '''
        for i, val in enumerate(event):
            self.branchArrays[i][0] = val
        self.tree.Fill()


