import glob
import os
import ROOT

from common import getEntries

def checkFiles(sample, nameRequirement, shellPath, outPath):
    '''
    collect all files in input directory
    check if same file exists in output directory
    check if file is broken
    check if entries match in both files

    if files are missing/broken collect shell scripts to resubmit
    '''
    inFiles = glob.glob("/".join(
        [sample, "*{}*.root".format(nameRequirement)]
        ))
    print("\n\n")
    print(" ===== SAMPLE ===== ")
    print(sample)
    print(" ================== ")
    print("number of files: {}".format(len(inFiles)))
    sampleName = os.path.basename(sample)

    missingFiles = []
    for f in inFiles:
        fName = os.path.basename(f)

        # check if cutflow exists
        if not os.path.exists("/".join([outPath, sampleName, fName.replace(".root",".cutflow.txt")])):
            print("file {} missing .cutflow.txt".format(fName))
            missingFiles.append(fName)
            continue

        # check if output file exists
        if not os.path.exists("/".join([outPath, sampleName, fName])):
            print("output file {} missing".format(fName))
            missingFiles.append(fName)
            continue

        # check if root file can be opened
        if not testFile("/".join([outPath, sampleName, fName])):
            print("output file {} corrupted".format(fName))
            missingFiles.append(fName)
            continue

        # check if entries in output file matches original root file
        entries_infile = getEntries(f)
        entries_outfile = getEntries("/".join([outPath, sampleName, fName]))
        if not entries_infile == entries_outfile:
            print("outout file {} ({} entries) not same as input ({} entries)".format(
                fName, entries_outfile, entries_infile))
            missingFiles.append(fName)

    print("\n{}/{} output files broken/missing.\n".format(len(missingFiles), len(inFiles)))

    resubmitFile = "/".join([shellPath, "resubmit_"+sampleName+".txt"])
    if len(missingFiles)>0:
        shellDict = getShellDictionary("/".join([shellPath, sampleName,"*.sh"]))
        resubmitShells = []
        for m in missingFiles:
            resubmitShells.append(shellDict[m])
        resubmitShells = list(set(resubmitShells))

        print("need to resubmit {} shell scripts".format(len(resubmitShells)))
        with open(resubmitFile, "w") as rf:
            rf.write("\n".join(resubmitShells))
        print("wrote shell scripts to resubmit to {}".format(resubmitFile))
        return len(resubmitShells)
    else:
        print("all files found")
        if os.path.exists(resubmitFile):
            os.remove(resubmitFile)
        return 0


def testFile(path):
    '''
    test if rootfile is corrupted
    '''
    rf = ROOT.TFile.Open(path)
    if rf is None or len(rf.GetListOfKeys())==0 or rf.TestBit(ROOT.TFile.kZombie):
        return False
    elif rf.TestBit(ROOT.TFile.kRecovered):
        return False
    else:
        tree = rf.Get("MVATree")
        if tree is None:
            return False
        else:
            nevents = tree.GetEntries()
            if nevents<0:
                return False
    if not rf is None:
        rf.Close()
    return True

def getShellDictionary(shellPath):
    '''
    match output files to shell scripts
    '''
    shellScripts = glob.glob(shellPath)
    shellDict = {}
    for script in shellScripts:
        with open(script, "r") as s:
            entries = s.read().replace("\n","").split(" ")
            
        for e in entries:
            if ".root" in e:
                shellDict[os.path.basename(e)] = script
    return shellDict
        







