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
parser.add_option("-M", "--mode", dest = "mode", choices = [
    "Reconstruction", "R", 
    "Matching",       "M", 
    "Evaluation",     "E", 
    "Calculation",    "C",
    "Database",       "DB"],
    help = "switch between modes")

recoOptions = optparse.OptionGroup(parser, "Reconstruction/Evaluate options")
recoOptions.add_option("-m", "--model", dest="model",default=None,
    help = "path to trained dnn model")
recoOptions.add_option("--write-input-vars", dest = "write_input_vars",default=False,action="store_true",
    help = "by default only the DNN outputs are written to the new trees, activate"
           " this option to write input features as well")
parser.add_option_group(recoOptions)

matchOptions = optparse.OptionGroup(parser, "Matching options")
matchOptions.add_option("-t", "--threshold", dest = "threshold", default=0.2,
    help = "dR threshold for when a jet is considered matched to a gen object")
matchOptions.add_option("--signal-only", dest = "signal_only", default = False, action = "store_true",
    help = "activate to only write root files with correct (i.e. best) matches."
           " Default is false - i.e. a file with wrong assignments is written."
           " This can be for example be used as DNN training background definitions.")
parser.add_option_group(matchOptions)

calcOptions = optparse.OptionGroup(parser, "Calculation options")
calcOptions.add_option("--split", dest="split_feature", default = None,
    help = "define variable upon which to split events and corresponding event vectors."
            "e.g. 'N_Jets' creates a single ntuple entry for each jet in each event")
parser.add_option_group(calcOptions)

dbOptions = optparse.OptionGroup(parser, "Database options", 
    "Requires single database file '_db.root' in the path given with -d"
    " following the same structure as the friend trees."
    " Additionally need '_idx.h5' which consists of the indices"
    " of the db root file in the same order. This can be created"
    " with the create_idx_file.py script")
dbOptions.add_option("--database", "-d", dest = "database", default = None,
    help = "specify base path to unordered database to convert into friend trees.")
parser.add_option_group(dbOptions)

parser.add_option("-c", "--config", dest = "config_path", default=None,
    help = "module for defining objects and variables in config directory")
parser.add_option("-o", "--output", dest="output",default=None,
    help = "output path for new ntuples. ")
parser.add_option("--apply-selection", dest="apply_selection",default=False,action="store_true",
    help = "by default, default values are written for variables in events where"
           " base selection or other criteria are not fulfilled. Activate this"
           " option to skip these events. this is not usable as friendtree anymore.")
parser.add_option("--friend-trees", "-f", dest = "friendTrees", default = None,
    help = "add friend trees as additional source of input information. comma separated list.")
parser.add_option("--jec-dependent", "-j", dest = "jecDependent", default = False, action = "store_true",
    help = "perform jec loop instead of just calculating variables once")
(opts, args) = parser.parse_args()


if opts.mode == "R":
    opts.mode = "Reconstruction"
if opts.mode == "M":
    opts.mode = "Matching"
if opts.mode == "E":
    opts.mode = "Evaluation"
if opts.mode == "C":
    opts.mode = "Calculation"
if opts.mode == "DB":
    opts.mode = "Database"

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

friendTrees = opts.friendTrees.split(",") if not opts.friendTrees is None else []

for ntuple in args:
    outfileName = os.path.basename(ntuple)
    outfileDir  = os.path.basename(os.path.dirname(ntuple))
    outfilePath = "/".join([opts.output, outfileDir])

    if not os.path.exists(outfilePath):
        os.makedirs(outfilePath)

    if opts.mode == "Reconstruction":
        karim.evaluate_reconstruction(
            filename    = ntuple,
            modelname   = opts.model,
            configpath  = os.path.abspath(opts.config_path),
            friendTrees = friendTrees,
            outpath     = "/".join([outfilePath, outfileName]),
            )
    elif opts.mode == "Evaluation":
        karim.evaluate_model(
            filename        = ntuple,
            modelconfigpath = opts.model,
            configpath      = os.path.abspath(opts.config_path),
            friendTrees     = friendTrees,
            outpath         = "/".join([outfilePath, outfileName]),
            apply_selection = opts.apply_selection,
            write_input_vars= opts.write_input_vars
            )
    elif opts.mode == "Matching":
        karim.match_jets(
            filename    = ntuple,
            configpath  = os.path.abspath(opts.config_path),
            friendTrees = friendTrees,
            threshold   = opts.threshold,
            signal_only = opts.signal_only,
            outpath     = "/".join([outfilePath, outfileName])
            )
    elif opts.mode == "Calculation":
        karim.calculate_variables(
            filename        = ntuple,
            configpath      = os.path.abspath(opts.config_path),
            friendTrees     = friendTrees,
            outpath         = "/".join([outfilePath, outfileName]),
            apply_selection = opts.apply_selection,
            split_feature   = opts.split_feature,
            jecDependent    = opts.jecDependent,
            )

    elif opts.mode == "Database":
        karim.convert_database(
            filename        = ntuple,
            configpath      = os.path.abspath(opts.config_path),
            friendTrees     = friendTrees,
            database        = opts.database,
            outpath         = "/".join([outfilePath, outfileName])
            )        
