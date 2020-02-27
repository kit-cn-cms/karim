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
python {basepath}/scripts/karim.py -m {dnnModel} -c {config} -o {outPath} {files}
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

    sampleName = os.path.basename(inputSample)
    scriptNameTemplate = "/".join([scriptDir, sampleName+"_{idx}.sh"])
    # collect rootfiles until number of events per job is reached
    entries = 0
    scriptID = 1
    jobfiles = []
    for rf in rootfiles:
        jobfiles.append(rf)
        entries+=getEntries(rf)

        if entries>=int(options.nevents) or rf==rootfiles[-1]:
            script = scriptTemplate.format(
                cmssw    = os.environ['CMSSW_BASE'],
                basepath = basepath,
                dnnModel = options.model,
                config   = options.config_path,
                outPath  = options.output,
                files    = " ".join(jobfiles))
            outFile = scriptNameTemplate.format(idx = scriptID)
            with open(outFile, "w") as of:
                of.write(script)
            print("created script {}".format(outFile))
            
            entries   = 0
            scriptID += 1
            jobfiles  = []
            
            
    
