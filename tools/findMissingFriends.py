import ROOT
import sys
import glob
from multiprocessing import Pool
from tqdm import *
import os
import optparse 

parser = optparse.OptionParser()
parser.add_option("-i", "--ntupleDir", dest = "ntupleDir",
    help = "input Directory = Ntuple Directory")

parser.add_option("-f", "--friendDir", dest = "friendDir",
    help = "friend Directory")
(opts, args) = parser.parse_args()




brokenFiles=[]
emptyFiles=[]
fileList=[]

inSamplesPaths = glob.glob(opts.ntupleDir+"/*")
inSamples = [f.split("/")[-1] for f in inSamplesPaths]

friendSamplesPaths = glob.glob(opts.friendDir+"/*")
friendSamples = [f.split("/")[-1] for f in friendSamplesPaths]

print("#"*40)
print("checking {0} ntuple Samples ".format(len(inSamples)))
print("checking {0} Friend Samples ".format(len(friendSamples)))
print("#"*40)
if len(inSamples) != len(friendSamples):
    print("Number of samples don't match up, finding missing samples...")

s = set(friendSamples)
missing_Samples = [x for x in inSamples if x not in s]
# print(missing)

print("#"*40)
print("Following Samples are missing completely:")
for m in sorted(missing_Samples):
    print(m)
print("#"*40)

print("Checking for missing Files in existent Samples")
print("#"*40)

existentSamples = [x for x in inSamples if x in s]

inFiles =  []
friendFiles =  []
for x in existentSamples:
    for i in glob.glob(opts.ntupleDir+"/"+x+"/*.root"):
        inFiles.append(i)
    for i in glob.glob(opts.friendDir+"/"+x+"/*.root"):
        friendFiles.append(i)
# inFiles = [glob.glob(opts.ntupleDir+"/"+x+"/*.root") for x in existentSamples] 
# friendFiles = [glob.glob(opts.friendDir+"/"+x+"/*.root") for x in existentSamples] 
print("#"*40)
print("checking {0} ntupleFiles ".format(len(inFiles)))
print("checking {0} FriendFiles ".format(len(friendFiles)))
print("#"*40)
if len(inFiles) != len(friendFiles):
    print("Number of samples don't match up, finding missing samples...")

print("Checking for missing Files in existent Samples")
print("#"*40)
friendNames = [x.split("/")[-1] for x in friendFiles]
s = set(friendNames)
missing = [x for x in inFiles if x.split("/")[-1] not in s]
# print(inFiles)
# print(friendFiles)
# print(len(s))
print("#"*40)
print("Following Files are missing:")
for m in sorted(missing):
    print(m)
print("#"*40)
# print(missing)

with open("missing.txt","w") as file:
    file.write("Missing Samples:\n")
    for f in missing_Samples:
        file.write(f+"\n")
    file.write("Missing Files:\n")
    for f in missing:
        file.write(f+"\n")
    

