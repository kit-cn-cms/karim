import os
import sys
base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base)
import optparse

# local imports
from karim import submit as submit

usage = ["",
    "python generateSubmitScripts.py -m path/to/dnn/model -c path/to/config -o output/path -s workdir/path/for/shellscripts SAMPLE1 SAMPLE2",
    "samples should be in the usual ntuple file structure",
    "basepath/",
    "----/SAMPLE1",
    "----/----/*.root",
    "----/SAMPLE2",
    "----/----/*.root",
    "",
    "the output/path will be structured the same way",
    "all .root files matching the '-r' requirement will be processed" 
    ]

 
parser = optparse.OptionParser(usage = "\n".join(usage))
parser.add_option("-M", "--mode", dest = "mode", 
    choices = ["Reconstruction", "R", "Matching", "M", "Evaluation", "E", "Calculation", "C"],
    help = "switch between reconstruction evaluation mode and gen level particle matching mode")

recoOptions = optparse.OptionGroup(parser, "Reconstruction/Evaluation options")
recoOptions.add_option("-m", "--model", dest="model",default=None,
    help = "path to yml file with information about trained dnn model(s).")
recoOptions.add_option("--write-input-vars", dest = "write_input_vars",default=False,action="store_true",
    help = "by default only the DNN outputs are written to the new trees, activate"
           " this option to write input features as well")

#####################################################################
recoOptions.add_option("-x", dest = "dnn_output_node",default=None,
    help = "by default the zeroth output node of the reconstruction dnn is evaluated."
           "Give sample name of the output node (e.g. sig_Z) to evaluate a specific node")
#####################################################################

parser.add_option_group(recoOptions)

matchOptions = optparse.OptionGroup(parser, "Matching options")
matchOptions.add_option("-t", "--threshold", dest = "threshold", default=0.2,
    help = "dR threshold for when a jet is considered matched to a gen object")
matchOptions.add_option("--signal-only", dest = "signal_only", default = False, action = "store_true",
    help = "activate to only write root files with correct (i.e. best) matches."
           " Default is false - i.e. a file with wrong assignments is written."
           " This can be for example be used as DNN training background definitions.")

#########################################################################
matchOptions.add_option("-b", dest = "n_bkg_combis", default=1,
    help = "Give number of random di-jet combinations to be considered as background."
            "By default only one random combination is considered.")
#########################################################################

#########################################################################
#news Lukas, 14.01.2021
#########################################################################
matchOptions.add_option("-a", dest = "assignment_method", default=None,
    help = "Give method for jet assignemnt, enter c for chi^2 method,"
            "or t for threshold-based method, respectively."
            "By default the threshold-based method is applied.")
#########################################################################
parser.add_option_group(matchOptions)

submitOptions = optparse.OptionGroup(parser, "Submit options")
submitOptions.add_option("-c", "--config", dest = "config_path", default=None,
    help = "module for defining objects and variables in config directory")
submitOptions.add_option("-o", "--output", dest="output",default=None,
    help = "output path for new ntuples. ")
submitOptions.add_option("-r", "--requirement", dest="name_requirement",default="nominal",
    help = "naming requirement of root files to be submitted. default is 'nominal'")
submitOptions.add_option("-s", "--shellpath", dest="shell_path",default=None,
    help = "output path for shell scripts (relative to workdir or absolute)")
submitOptions.add_option("-n", "--nevents", dest="nevents",default=50000,
    help = "number of events per job, default = 50000")

parser.add_option_group(submitOptions)

parser.add_option("--apply-selection", dest="apply_selection",default=False,action="store_true",
    help = "by default, default values are written for variables in events where"
           " base selection or other criteria are not fulfilled. Activate this"
           " option to skip these events. this is not usable as friendtree anymore.")
parser.add_option("--friend-trees", "-f", dest = "friendTrees", default = None,
    help = "add friend trees as additional source of input information. comma separated list.")
(opts, args) = parser.parse_args()


if opts.mode == "R":
    opts.mode = "Reconstruction"
if opts.mode == "M":
    opts.mode = "Matching"
if opts.mode == "E":
    opts.mode = "Evaluation"
if opts.mode == "C":
    opts.mode = "Calculation"

# check arguments
if opts.mode == "Reconstruction" or opts.mode == "Evaluation":
    if opts.model is None:
        exit("need to specify a dnn model")
    opts.model = os.path.abspath(opts.model)
    
if opts.config_path is None:
    exit("need to specify a config module")
opts.config_path = os.path.abspath(opts.config_path)

if opts.output is None:
    exit("need to specify an output directory")
opts.output = os.path.abspath(opts.output)

if len(args) == 0:
    exit("need to specify at least one input file")

if not os.path.exists(opts.output):
    os.makedirs(opts.output)

# setting shell path
shell_path = opts.shell_path
if not os.path.isabs(shell_path):
    shell_path = "/".join([base, "workdir", shell_path])
print("output directory for shellscripts: {}".format(shell_path))
if not os.path.exists(shell_path):
    os.makedirs(shell_path)

print("set max events per job to {}".format(opts.nevents))

for sample in args:
    sampleName = os.path.basename(sample)
    outfilePath = "/".join([shell_path, sampleName])

    if not os.path.exists(outfilePath):
        os.makedirs(outfilePath)

    submit.writeScripts(
        inputSample = os.path.abspath(sample),
        scriptDir   = outfilePath,
        options     = opts,
        basepath    = base)

shelldir = os.path.basename(shell_path)

cmd = " ".join([
    "for f in *;",
    "do python {basedir}/karim/submit/condorSubmit.py",
    "-f $f -o ../submit_{name} -M 2000 -r 120 -n {mode}_$f;",
    "done"]).format(
        mode = "karim_"+opts.mode.lower(),
        name = shelldir,
        basedir = base)

text = ["",
    "",
    "="*50,
    "done creating shell scripts.",
    "",
    "the scripts can be submitted with condorSubmit.py",
    "",
    "e.g. move to output directory {}".format(shell_path),
    "\033[1;31mcd {}\033[0m".format(shell_path),
    "",
    "and execute",
    "\033[1;31m{}\033[0m".format(cmd),
    "",
    "",
    "disclaimer:",
    "a runtime of '-r 120' minutes should work well for",
    "  max. 50k events per job. higher number of events",
    "  might lead to longer runtimes. jobs that are",
    "  submitted with more than 3 hrs are placed into a",
    "  long queue and might take longer to be processed.",
    "",
    "try executing one shell script locally before",
    "  submitting everything tho the batch system",
    "  (source /shell/path.sh)",
    "",
    "this also gives you an approximation of the expected",
    "  runtime for a number of events (i.e. 500) via a",
    "  dedicated printout.",
    ""
    ]
print("\n".join(text))
