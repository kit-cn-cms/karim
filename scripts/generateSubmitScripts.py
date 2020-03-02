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
parser.add_option("-M", "--mode", dest = "mode", choices = ["Reconstruction", "R", "Matching", "M", "MEM"],
    help = "switch between reconstruction evaluation mode and gen level particle matching mode")

recoOptions = optparse.OptionGroup(parser, "Reconstruction options")
recoOptions.add_option("-m", "--model", dest="model",default=None,
    help = "path to trained dnn model")
parser.add_option_group(recoOptions)

matchOptions = optparse.OptionGroup(parser, "Matching options")
matchOptions.add_option("-t", "--threshold", dest = "threshold", default=0.2,
    help = "dR threshold for when a jet is considered matched to a gen object")
parser.add_option_group(matchOptions)

memOptions = optparse.OptionGroup(parser, "MEM options")
memOptions.add_option("--memPath", dest="memPath",default=None,
    help = "path to MEM h5 Files")
parser.add_option_group(memOptions)

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
(opts, args) = parser.parse_args()


if opts.mode == "R":
    opts.mode = "Reconstruction"
if opts.mode == "M":
    opts.mode = "Matching"
# check arguments
if opts.mode == "Reconstruction":
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


cmd = " ".join([
    "for f in *;",
    "do python {basedir}/karim/submit/condorSubmit.py",
    "-f $f -o ../submit -M 4000 -r 120 -n $f;",
    "done"]).format(basedir = base)

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
