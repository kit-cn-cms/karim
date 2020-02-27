import os
import sys
base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, base)
import optparse

# local imports
from karim import submit as submit

usage = ["",
    "python checkFiles.py -o output/path -s workdir/path/for/shellscripts SAMPLE1 SAMPLE2",
    "samples should be in the usual ntuple file structure",
    "basepath/",
    "----/SAMPLE1",
    "----/----/*.root",
    "----/SAMPLE2",
    "----/----/*.root",
    "",
    "the output/path will be structured the same way",
    "all .root files matching the '-r' requirement will be checked"
    ]


parser = optparse.OptionParser(usage = "\n".join(usage))
parser.add_option("-r", "--requirement", dest="name_requirement",default="nominal",
    help = "naming requirement of root files to be submitted. default is 'nominal'")
parser.add_option("-o", "--output", dest="output",default=None,
    help = "output path for new ntuples. ")
parser.add_option("-s", "--shellpath", dest="shell_path",default=None,
    help = "output path for shell scripts")
(opts, args) = parser.parse_args()

if opts.output is None:
    exit("need to specify an output directory")
opts.output = os.path.abspath(opts.output)

if opts.shell_path is None:
    exit("need to specify path for shell scripts")
opts.shell_path = os.path.abspath(opts.shell_path)

if len(args) == 0:
    exit("need to specify at least one input file")

totalBroken = 0
for sample in args:
    sampleName = os.path.basename(sample)
    outfilePath = "/".join([opts.shell_path, sampleName])

    nbroken = submit.checkFiles(
        sample          = os.path.abspath(sample),
        nameRequirement = opts.name_requirement,
        shellPath       = opts.shell_path,
        outPath         = opts.output
        )
    totalBroken+=nbroken


cmd = " ".join([
    "for f in resubmit*.txt;",
    "do python {basedir}/karim/submit/condorSubmit.py",
    "--file $f -o ../resubmit -M 4000 -r 120 -n $f;",
    "done"]).format(basedir = base)

text = ["",
    "",
    "="*50,
    "done checking shell scripts.",
    "",
    "shell scripts to be resubmitted in total: {}".format(totalBroken),
    "these can be resubmitted with condorSubmit.py",
    "",
    "e.g. move to output directory {}".format(opts.shell_path),
    "\033[1;31mcd {}\033[0m".format(opts.shell_path),
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
    
