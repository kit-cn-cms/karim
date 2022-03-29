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
python3 {basepath}/scripts/karim.py -M {mode} -m {dnnModel} -c {config} -o {outPath} {dataEra} {friendTrees} {files}
"""
evalTemplate = """
python3 {basepath}/scripts/karim.py -M {mode} -m {dnnModel} -c {config} -o {outPath} {dataEra} {friendTrees} {applySelection} {writeInputVars} {files}
"""
matchTemplate = """
python3 {basepath}/scripts/karim.py -M {mode} -t {threshold} -c {config} -o {outPath} {dataEra} {friendTrees} {sigOnly} {files}
"""
calcTemplate = """
python3 {basepath}/scripts/karim.py -M {mode} -c {config} -o {outPath} {friendTrees} {dataEra} {split} {jecDependent} {files}
"""
databaseTemplate = """
python3 {basepath}/scripts/karim.py -M {mode} -c {config} -o {outPath} {friendTrees} {dataEra} -d {database} {files}
"""

def writeScripts(inputSample, scriptDir, options, basepath):
    ''' 
    split input sample in chunks according to maximum number of events per job
    create shell script to submit job
    '''
    rootfiles = glob.glob("/".join([inputSample, "tree*{}*.root".format(options.name_requirement)]))
    rootfiles = [r for r in rootfiles if not "genWeight" in r]
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
    dataEra = "--year {}".format(options.dataEra) if not options.dataEra is None else ""
    splitFeature = "--split {}".format(options.split_feature) if not options.split_feature is None else ""
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
                    dataEra   = dataEra,
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
                    dataEra   = dataEra,
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
                    dataEra   = dataEra,
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
                    dataEra   = dataEra,
                    jecDependent = "--jec-dependent" if options.jecDependent else "",
                    split       = splitFeature,
                    files     = " ".join(jobfiles))

            elif options.mode == "Database":
                script = scriptTemplate+databaseTemplate
                script = script.format(
                    cmssw    = os.environ['CMSSW_BASE'],
                    basepath  = basepath,
                    mode      = options.mode,
                    config    = options.config_path,
                    outPath   = options.output,
                    friendTrees = friendTrees,
                    dataEra   = dataEra,
                    database  = options.database,
                    files     = " ".join(jobfiles))

                    
            outFile = scriptNameTemplate.format(idx = scriptID)
            with open(outFile, "w") as of:
                of.write(script)
            print("created script {}".format(outFile))
            
            entries   = 0
            scriptID += 1
            jobfiles  = []
            
            
    
