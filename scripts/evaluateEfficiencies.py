import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import optparse

# local imports
import karim

usage = ["",
    "python evaluateEfficiencies.py -g NAME1=VAR1 -g NAME2=VAR1+VAR2 -c CUTOFVALUE -m SMALLER/LARGER -s ROOTSELECTIONSTRING -n NUMBEROFBINS -r BINRANGE -o output/path FILE1 FILE2",
    "files should be rootfiles, all files will be added to a chain",
    ]

    
parser = optparse.OptionParser(usage = "\n".join(usage))
parser.add_option("-g", "--group", dest = "groups", action = "append",
    help = "groups that are supposed to be matched (multiple mentions)") #add multi mention option
parser.add_option("-c", "--cutoff", dest = "cutoff", default = 0.4,
    help = "define some cutoff for which the efficiencies will be quoted")
parser.add_option("-m", "--mode", dest = "mode", choices = ["leq", "geq"], default = "leq",
    help = "leq or geq")
parser.add_option("-s", "--selection", dest = "selection", default = "True",
    help = " ".join(["selection of events via selection string that can be evaluated.",
        "prepend variables in root trees with c. (e.g. \"c.N_AdditionalGenBJets>=2\")"]))
parser.add_option("-n", "--nbins", dest = "nbins", default = 30,
    help = "number of bins")
parser.add_option("-r", "--binrange", dest = "binrange", default = "0.,4.",
    help = "bin range tuple separated by comma")
parser.add_option("-o", "--output", dest="output",default=None,
    help = "output path for new ntuples. ")
(opts, args) = parser.parse_args()


if len(opts.groups) == 0:
    exit("need to specify at least one group")
if opts.output is None:
    exit("need to specify an output directory")
if len(args) == 0:
    exit("need to specify at least one input file")

if not os.path.exists(opts.output):
    os.makedirs(opts.output)

karim.evaluate_reco(
    files = args,
    opts  = opts)
        
