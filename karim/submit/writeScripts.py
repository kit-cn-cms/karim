import glob
import os
import ROOT
from common import getEntries

scriptTemplate = """
#!/bin/bash
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
cd {cmssw}/src
eval `scram runtime -sh`
cd -

export KERAS_BACKEND=tensorflow
"""
recoTemplate = """
python {basepath}/scripts/karim.py -M {mode} -m {dnnModel} -c {config} -o {outPath} {friendTrees} {dnnOutputNode} {files}
"""
evalTemplate = """
python {basepath}/scripts/karim.py -M {mode} -m {dnnModel} -c {config} -o {outPath} {friendTrees} {applySelection} {writeInputVars} {files}
"""
matchTemplate = """
python {basepath}/scripts/karim.py -M {mode} -t {threshold} -c {config} -o {outPath} {friendTrees} -b {n_bkg_combis} {assignment_method} {sigOnly} {files}
"""
calcTemplate = """
python {basepath}/scripts/karim.py -M {mode} -c {config} -o {outPath} {friendTrees} {files}
"""

def writeScripts(inputSample, scriptDir, options, basepath):
    ''' 
    split input sample in chunks according to maximum number of events per job
    create shell script to submit job
    '''
    rootfiles = glob.glob("/".join([inputSample, "*{}*.root".format(options.name_requirement)]))
    print(" ===== SAMPLE ===== ")
    print(inputSample)
    print(" ================== ")
    print("number of files: {}".format(len(rootfiles)))
    if len(rootfiles) == 0:
        print("no files found.")
        os.system("rm -r {}".format(scriptDir))
        return 

    sampleName = os.path.basename(inputSample)
    scriptNameTemplate = "/".join([scriptDir, sampleName+"_{idx}.sh"])

    friendTrees = "--friend-trees {}".format(options.friendTrees) if not options.friendTrees is None else ""

    outputNode = "-x {}".format(options.dnn_output_node) if not options.dnn_output_node is None else ""

    assignment_method = "-a {}".format(options.assignment_method) if not options.assignment_method is None else ""

    #bkg_combis = "-b {}".format(options.n_bkg_combis) if not options.n_bkg_combis is None else ""

    # collect rootfiles until number of events per job is reached
    entries = 0
    scriptID = 1
    jobfiles = []
    for rf in rootfiles:
        jobfiles.append(rf)
        entries+=getEntries(rf)

        if entries>=int(options.nevents) or rf==rootfiles[-1]:
            if options.mode == "Reconstruction":
                script = scriptTemplate+recoTemplate
                script = script.format(
                    cmssw    = os.environ['CMSSW_BASE'],
                    basepath  = basepath,
                    mode      = options.mode,
                    dnnModel  = options.model,
                    config    = options.config_path,
                    outPath   = options.output,
                    friendTrees = friendTrees,
                    dnnOutputNode = outputNode,
                    files     = " ".join(jobfiles)
                    )

            elif options.mode == "Evaluation":
                script = scriptTemplate+evalTemplate
                script = script.format(
                    cmssw    = os.environ['CMSSW_BASE'],
                    basepath  = basepath,
                    mode      = options.mode,
                    dnnModel  = options.model,
                    config    = options.config_path,
                    outPath   = options.output,
                    friendTrees = friendTrees,
                    applySelection = "--apply-selection" if options.apply_selection else "",
                    writeInputVars = "--write-input-vars" if options.write_input_vars else "",
                    files     = " ".join(jobfiles)
                    )

            elif options.mode == "Matching":
                script = scriptTemplate+matchTemplate
                script = script.format(
                    cmssw    = os.environ['CMSSW_BASE'],
                    basepath  = basepath,
                    mode      = options.mode,
                    threshold = options.threshold,
                    config    = options.config_path,
                    outPath   = options.output,
                    friendTrees = friendTrees,
                    n_bkg_combis = options.n_bkg_combis,
                    assignment_method = assignment_method,
                    sigOnly   = "--signal-only" if options.signal_only else "",
                    files     = " ".join(jobfiles))


            elif options.mode == "Calculation":
                script = scriptTemplate+calcTemplate
                script = script.format(
                    cmssw    = os.environ['CMSSW_BASE'],
                    basepath  = basepath,
                    mode      = options.mode,
                    config    = options.config_path,
                    outPath   = options.output,
                    friendTrees = friendTrees,
                    files     = " ".join(jobfiles))

            outFile = scriptNameTemplate.format(idx = scriptID)
            with open(outFile, "w") as of:
                of.write(script)
            print("created script {}".format(outFile))
            
            entries   = 0
            scriptID += 1
            jobfiles  = []
            
            
    
