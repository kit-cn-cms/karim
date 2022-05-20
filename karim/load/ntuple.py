import ROOT
import os
from array import array

class InputFile(object):
    '''
    open input file and return tree
    '''
    def __init__(self, filename, friendTrees = [], treeName = "Events"):
        self.file = ROOT.TFile(filename)
        self.tree = self.file.Get(treeName)
        
        print("\nloading tree with {nentries} entries\n".format(
            nentries = self.tree.GetEntries()))
        
        for ft in friendTrees:
            print("adding friendTree {}".format(ft))
            self.tree.AddFriend("MVATree", ft)        
    
    def __enter__(self):
        return self.tree

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        self.file.Close()


jecs = [
    "jes",
    "jesAbsolute_2018",
    "jesAbsolute_2017",
    "jesAbsolute_2016",
    #"jesHF_2018",
    #"jesHF_2017",
    #"jesHF_2016",
    #"jesEC2_2018",
    #"jesEC2_2017",
    #"jesEC2_2016",
    "jesRelativeBal",
    "jesHEMIssue",
    "jesBBEC1_2018",
    "jesBBEC1_2017",
    "jesBBEC1_2016",
    "jesRelativeSample_2018",
    "jesRelativeSample_2017",
    "jesRelativeSample_2016",
    "jesFlavorQCD",
    "jesBBEC1",
    #"jesHF",
    "jesAbsolute",
    #"jesEC2",
    "jesTotal",
    "jer",
    "jer0",
    "jer1",
    "jer2",
    "jer3",
    "jer4",
    ]
validSysts = ["nominal"]
validSysts+= [j+"up" for j in jecs]
validSysts+= [j+"down" for j in jecs]

def getSystematics(tree):
    branches = [b.GetName() for b in tree.GetListOfBranches()]
    postfix  = []
    for b in branches:
        if not b.split("_")[-1].startswith("201"):
            postfix.append(b.split("_")[-1])
        else:
            postfix.append(b.split("_")[-2]+"_"+b.split("_")[-1])
    jecs = list(set(postfix))
    jecs = [j for j in jecs if j in validSysts]
    jecs = list(sorted(jecs))
    print("\tfound the following JECs in the input file")
    for j in jecs: 
        print("\t{}".format(j))
    return jecs



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

    def __next__(self):
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
    def __init__(self, filename, treeName = "Events"):
        self.name = filename
        self.setSampleName()
        self.file = ROOT.TFile(self.name, "RECREATE")
        self.tree = ROOT.TTree(treeName,"KarimTree")
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
        self.sampleName = os.path.basename(os.path.dirname(self.name))

    def SetBranchList(self, variables):
        '''
        initialize branches for tree
        currently all trees are of datatype float
        '''
        for i, v in enumerate(variables):
            outvar = v.replace("[","_").replace("]","")
            if outvar in self.branchArrays: continue
            self.branchArrays[outvar] = array("f", [0.])
            self.tree.Branch(outvar, self.branchArrays[outvar], "{}/F".format(outvar))

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

    def SetConfigBranches(self, config, jecs, jecDependent = False):
        if jecDependent:
            for jec in jecs:
                config.set_branches(self, jec)
        else:
            config.set_branches(self, jec = None)

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
                    self.branchArrays[key][i] = -9
                else:
                    self.branchArrays[key][i] = -9.

class GenWeights:
    def __init__(self, treepath):
        samplepath = os.path.dirname(treepath)
        ntuplepath = os.path.dirname(samplepath)
        samplename = os.path.basename(samplepath)
        self.filename = os.path.join(ntuplepath, samplename+"_genWeights.root")
        if not os.path.exists(self.filename):
            print("sample does not have genWeights file")
            self.isInitialized = False
            return
    
        print("loading genWeight file {}".format(self.filename))

        self.file = ROOT.TFile.Open(self.filename)
        self.branches = [b.GetName() for b in self.file.GetListOfKeys()]
        
        self.getProcessFractions()
        self.setRateFactors()
        self.isInitialized = True

    def getProcessFractions(self):
        # extract gen weight branches
        genWeights = [b for b in self.branches if b.startswith("genWeight")]
        self.weightTypes = [b.replace("genWeight_", "") for b in genWeights if not b == "genWeight"]

        #if not "incl" in self.weightTypes:
        #    print("ERROR: could not find 'incl' gen weight in genWeight file")
        #    sys.exit()

        self.genFractions = {}
        self.xsNorms = {}
        print("process fractions:")
        inclh = self.file.Get("genWeight")
        self.xsNorms["default"] = 1000./(inclh.GetMean()*inclh.GetEntries())
        for w in self.weightTypes:
            print(w)
            genh = self.file.Get("genWeight_"+w)
            self.genFractions[w] = genh.GetMean()*genh.GetEntries()/(inclh.GetMean()*inclh.GetEntries())
            # XS usually given in pb, lumi in fb-1
            # -> expect 1000 events for a XS of 1 [pb] in 1 [fb-1] of data if all events are selected
            # -> multiply with XS number in plotscript later on
            self.xsNorms[w] = 1000./(genh.GetMean()*genh.GetEntries())
            print("\t{}: {} (XS norm: {})".format(w, self.genFractions[w], self.xsNorms[w]))
        print("="*50)

    def setRateFactors(self):
        self.rateFactors  = {}
        print("rateFactors:")
        for b in self.branches:
            h = self.file.Get(b)
            self.rateFactors[b] = h.GetMean()
            print("{}: {}".format(b, self.rateFactors[b]))
        print("="*50)                 


    
    def getRF(self, w):
        if not self.isInitialized:
            return 1.
        if not w in self.rateFactors:
            sys.exit("could not access ratefactor {}".format(w))
        return self.rateFactors[w]

    
    def getXS(self, t = "incl"):
        if not self.isInitialized:
            return 1.
        if not t in self.xsNorms:
            sys.exit("could not access norm type {}".format(t))
        return self.xsNorms[t]




