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
parser.add_option("-m", "--model", dest="model",default=None,
    help = "path to trained dnn model")
parser.add_option("-c", "--config", dest="config_path",default=None,
    help = "module for generating variables in modules/variables directory")
parser.add_option("-o", "--output", dest="output",default=None,
    help = "output path for new ntuples. ")
(opts, args) = parser.parse_args()

# check arguments
if opts.model is None:
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

    karim.evaluate_model(
        filename   = ntuple,
        modelname  = opts.model,
        configpath = os.path.abspath(opts.config_path),
        outpath    = "/".join([outfilePath, outfileName])
        )

