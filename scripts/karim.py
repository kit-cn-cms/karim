import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import optparse

# local imports
import karim

usage = ["",
    "python karim.py -m path/to/dnn/model -c path/to/config -o output/path FILE1 FILE2",
    "files should be in the usual ntuple file structure",
    "basepath/",
    "----/sampleA",
    "----/----/FILE1",
    "----/----/FILE2",
    "----/sampleB",
    "----/----/FILE3",
    "----/----/FILE4",
    "",
    "the output/path will be structured the same way"
    ]

    
parser = optparse.OptionParser(usage = "\n".join(usage))
parser.add_option("-M", "--mode", dest = "mode", choices = ["Reconstruction", "R", "Matching", "M", "Evaluation", "E"],
    help = "switch between reconstruction evaluation mode and gen level particle matching mode")

recoOptions = optparse.OptionGroup(parser, "Reconstruction/Evaluate options")
recoOptions.add_option("-m", "--model", dest="model",default=None,
    help = "path to trained dnn model")
parser.add_option_group(recoOptions)

matchOptions = optparse.OptionGroup(parser, "Matching options")
matchOptions.add_option("-t", "--threshold", dest = "threshold", default=0.2,
    help = "dR threshold for when a jet is considered matched to a gen object")
matchOptions.add_option("--signal-only", dest = "signal_only", default = False, action = "store_true",
    help = "activate to only write root files with correct (i.e. best) matches."
           " Default is false - i.e. a file with wrong assignments is written."
           " This can be for example be used as DNN training background definitions.")
parser.add_option_group(matchOptions)

parser.add_option("-c", "--config", dest = "config_path", default=None,
    help = "module for defining objects and variables in config directory")
parser.add_option("-o", "--output", dest="output",default=None,
    help = "output path for new ntuples. ")
(opts, args) = parser.parse_args()


if opts.mode == "R":
    opts.mode = "Reconstruction"
if opts.mode == "M":
    opts.mode = "Matching"
if opts.mode == "E":
    opts.mode = "Evaluation"

# check arguments
if opts.model is None and opts.mode == "Reconstruction":
    exit("need to specify a dnn model")
if opts.model is None and opts.mode == "Evaluation":
    exit("need to specify a dnn model")
if opts.config_path is None:
    exit("need to specify a config module")
if opts.output is None:
    exit("need to specify an output directory")
if len(args) == 0:
    exit("need to specify at least one input file")


if not os.path.exists(opts.output):
    os.makedirs(opts.output)

for ntuple in args:
    outfileName = os.path.basename(ntuple)
    outfileDir  = os.path.basename(os.path.dirname(ntuple))
    outfilePath = "/".join([opts.output, outfileDir])

    if not os.path.exists(outfilePath):
        os.makedirs(outfilePath)

    if opts.mode == "Reconstruction":
        karim.evaluate_reconstruction(
            filename   = ntuple,
            modelname  = opts.model,
            configpath = os.path.abspath(opts.config_path),
            outpath    = "/".join([outfilePath, outfileName])
            )
    elif opts.mode == "Matching":
        karim.match_jets(
            filename    = ntuple,
            configpath  = os.path.abspath(opts.config_path),
            threshold   = opts.threshold,
            signal_only = opts.signal_only,
            outpath     = "/".join([outfilePath, outfileName])
            )
    elif opts.mode == "Evaluation":
        karim.evaluate_model(
            filename   = ntuple,
            modelname  = opts.model,
            configpath = os.path.abspath(opts.config_path),
            outpath    = "/".join([outfilePath, outfileName])
            )
        
