#Idea: events in ntuple have a certain order.
# Check, if order of the events in ntuple before matching is the same as afterward.
import ROOT


basepath = "/nfs/dust/cms/user"
inputFile = basepath + "/vdlinden/legacyTTZ/ntuples/2017/TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8/TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8_5_nominal_Tree.root"
friendTree = basepath + "/larmbrus/combined_ttZ_ttH/ntuples/2017/new_ntuples/multiclassJAN/matchX/test/v1/match_Z_as_X/TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8/TTZToQQ_TuneCP5_13TeV-amcatnlo-pythia8_5_nominal_Tree_bkg.root"


inFile = ROOT.TFile.Open(inputFile)
outFile = ROOT.TFile.Open(friendTree)

inTree = inFile.Get("MVATree")
outTree = outFile.Get("MVATree")

#inBranches = list(inTree.GetListOfBranches())
#outBranches = list(outTree.GetListOfBranches())
print inTree.GetEntries()
print outTree.GetEntries()


for entryNum in range(0,200):
	inTree.GetEntry(entryNum)
	outTree.GetEntry(entryNum)
	inID = getattr(inTree,"Evt_ID")
	outID = getattr(outTree,"Evt_ID")

	print "inID = ",inID," , outID = ",outID