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
parser.add_option("-m", "--model", dest="model",default=None,
    help = "path to trained dnn model")
parser.add_option("-c", "--config", dest="config_path",default=None,
    help = "module for generating variables in modules/variables directory")
parser.add_option("-r", "--requirement", dest="name_requirement",default="nominal",
    help = "naming requirement of root files to be submitted. default is 'nominal'")
parser.add_option("-o", "--output", dest="output",default=None,
    help = "output path for new ntuples. ")
parser.add_option("-s", "--shellpath", dest="shell_path",default=None,
    help = "output path for shell scripts (relative to workdir or absolute)")
parser.add_option("-n", "--nevents", dest="nevents",default=50000,
    help = "number of events per job, default = 50000")
(opts, args) = parser.parse_args()

# check arguments
if opts.model is None:
    exit("need to specify a dnn model")
opts.model = os.path.abspath(opts.model)

if opts.config_path is None:
    exit("need to specify a config module")
opts.config_path = os.path.abspath(opts.config_path)

if opts.output is None:
    exit("need to specify an output directory")
opts.output = os.path.abspath(opts.output)

if opts.shell_path is None:
    exit("need to specify path for shell scripts")
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
