import os
import sys
import optparse
import uproot
import glob



parser = optparse.OptionParser()

parser.add_option("-i", "--input", dest="input",default=None,
    help = "input path for mem ntuples. ")

parser.add_option("-o", "--output", dest="output",default=None,
    help = "output path for mem h5 Files. ")
(opts, args) = parser.parse_args()

if not os.path.exists("workdir/" + opts.output):
    os.makedirs("workdir/" + opts.output)

memFiles = glob.glob(opts.input+"/*.root")

variables = [
    "event",
    "run",
    "lumi",
    "systematic",
    "mem_p",
    "mem_p_sig",
    "mem_p_bkg",
    "mem_JERup_p",
    "mem_JERdown_p",
    "mem_Absoluteup_p",
    "mem_Absolutedown_p",
    "mem_Absoluteyearup_p",
    "mem_Absoluteyeardown_p",
    "mem_FlavorQCDup_p",
    "mem_FlavorQCDdown_p",
    "mem_BBEC1up_p",
    "mem_BBEC1down_p",
    "mem_BBEC1yearup_p",
    "mem_BBEC1yeardown_p",
    "mem_EC2up_p",
    "mem_EC2down_p",
    "mem_EC2yearup_p",
    "mem_EC2yeardown_p",
    "mem_HFup_p",
    "mem_HFdown_p",
    "mem_HFyearup_p",
    "mem_HFyeardown_p",
    "mem_RelativeBalup_p",
    "mem_RelativeBaldown_p",
    "mem_RelativeSampleyearup_p",
    "mem_RelativeSampleyeardown_p",
    "mem_JERpt0eta0up_p",
    "mem_JERpt0eta0down_p",
    "mem_JERpt0eta1up_p",
    "mem_JERpt0eta1down_p",
    "mem_JERpt1eta0up_p",
    "mem_JERpt1eta0down_p",
    "mem_JERpt1eta1up_p",
    "mem_JERpt1eta1down_p",
    "mem_JEReta2up_p",
    "mem_JEReta2down_p",
    "blr_4b",
    "blr_2b"
]
print(variables)
print(memFiles)

for i,f in enumerate(memFiles):
    # if i == 1: break
    print("converting file {0} of {1}".format(i+1, len(memFiles)))
    tree = uproot.open(f)["MVATree"]
    df = tree.pandas.df(variables)
    # print(df)
    df.to_hdf("workdir/" + opts.output + "/" + os.path.basename(f).replace(".root",".h5"),"w")
    # for k in tree.keys():
        # print k

