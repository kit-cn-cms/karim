# README

A framework using **K**eras to **A**ssign **R**econstruction **I**nformation to **M**VATrees

## What is this framework good for?
Imagine developing a DNN that finds the best assignment of jets for a hypothesized particle in your event. This framework is able to evaluate this DNN for all permutations of jets in a given event, chose the best permutation based on the DNN output value and write the best configuration to new ntuple files.
The newly created ntuple files retain the original order of events, such that they can be used as friend trees to the original trees.
This enables a fast exchange and update of variables in the ntuples which are based on the assignment of jets to some hypothetical objects, e.g. in case of an updated DNN training.

## Setup
This has been tested on CentOS7 on the corresponding NAF nodes `user@naf-cms-el7.desy.de`
Either setup a local `CMSSW_10_6_8_patch1` version, or execute the following before every use
```
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
cd /nfs/dust/cms/user/vdlinden/legacyTTH/CMSSW/CMSSW_10_6_8_patch1/src
eval `scram runtime -sh`
cd -
```
If `scripts/karim.py` is executed locally make sure the Keras backend is set to `tensorflow`:
```
export KERAS_BACKEND=tensorflow
```
All of the above is automatically set for shell scripts submitted to the NAF batch system. No further python packages should be required.



## How does it work?
#### `karim.py`
All scripts that need to be executed are located in the `scripts` directory. Single ntuple files can be processes with `scripts/karim.py`. This requires some inputs:
```
python karim.py -M Reconstuction -m MODEL -c CONFIG.py -o OUTPATH INFILES
```
- `-M Reconstruction`: mode switch for reconstruction.
- `-m MODEL`: path to a DNN model. currently it is only supported to evaulate one single model at the same time.
- `-c CONFIG`: path to a config file in the config directory. how these config files need to be structured is explained further below.
- `-o OUTPATH`: path to directory where new ntuple files should be created. the structures created in this output directory correspond exactly to the input structure
- `INFILES`: paths to input ntuple files. give as many ntuple files as you want, they are processed sequentially.

`karim.py` also supports matching of reconstructed objects to generator level objects. This can be activated with `-M Matching`. You also need to specify a matching threshold, e.g. `-t 0.4`, such that an object with `dR <= 0.4` is considered to be matched.
With this mode two files are generated, one called `_sig` and one `_bkg`. This can be used for defining right and wrong jet combinations e.g. for training a reconstruction DNN. 
The `_sig` files contain the assignment of reco objects to generator objects (if any was found). The `_bkg` files contain a random combination.



#### `generateSubmitScripts.py`
For convenience `scripts/generateSubmitScripts.py` to create multiple shell scripts that execute `scripts/karim.py`. These scripts can be submitted to the NAF batch system. This requires some inputs:
```
python generateSubmitScripts.py -M MODE -m MODEL -c CONFIG.py -o OUTPATH -s SHELLPATH [-r NAME -n NEVENTS] SAMPLES
```
Some arguments are the same as for `karim.py`. Additionally required are
- `-s SHELLPATH`: path where shellfiles are created, relative to `workdir`.
- `SAMPLES`: paths to samples. Theses should be in the usual ntuple file structure
```
basepath/
----/SAMPLE1
----/----/*.root
----/SAMPLE2
----/----/*.root
```

Optionally, the following arugments can be used:
- `-r NAME`: naming requirement of the ntuple files, e.g. `nominal` matches only files which match `*nominal*.root`.
- `-n NEVENTS`: number of events per job. If none is given the default value of `50000` is used


#### `NAFSubmit.py`
Information on how to submit these shell scripts to the batch system is printed at the end of the script. In summary, use
```
python karim/submit/NAFSubmit.py -f FOLDER -n NAME -o LOGPATH -M MEMORY -r RUNTIME
```
to submit all scripts found in `FOLDER`.


#### `checkFiles.py`
After all jobs have finished running on the batch system, make sure they have terminated successfully. For this purpose `scripts/checkFiles.py` can be used:
```
python checkFiles.py -M MODE -o OUTPATH -s SHELLPATH [-r NAME] SAMPLES
```
The arguments `OUTPATH` and `SHELLPATH` are relative or absolute paths to where the newly created ntuple files and the shellscripts, respectively, are located. As usual paths to all `SAMPLES` are required. This script creates textfiles in the `SHELLPATH` directory, containing all shell scripts that need to be resubmitted due to faulty or missing output ntuple files. Instructions on how to resubmit these files is printed at the end of the script.




## How to build a new config?
The config files in `config/` are required to generate assignable jet objects and to calculate secondary variables from the hypothesized jet assignments. All functions and variables of the following template are required in these config files:
```
import common

name = "Reco"
def get_reco_naming():
    '''
    define name for this reconstruction
    '''
    return name


def get_objects():
    '''
    define a list of objects considered for the reconstruction
    '''
    objects = [
        ]
    return objects


def get_features():
    '''
    define a list of features applicable for all objects defined in get_objects()
    '''
    features = [
        ]
    return features


def get_additional_variables():
    '''
    get names of additional variables which are already defined in ntuples
    which are needed for the dnn inputs
    '''
    variables = [
        ]
    return variables

def base_selection(event):
    '''
    base selection applied to all events
    events where the base selection is not fulfilled are filled with dummy values
    '''
    return event.N_Jets>=2


def calculate_variables(df):
    '''
    calculate additional variables needed for DNN input
    '''
    return df

```
Objects are for example `HadTop_B` or `B1` of a Higgs boson.
Features are for example `CSV`, `Eta`, `Pt` of jets.
From the combinations of objects and features variables are build. All of them should be named with a common naming scheme 
```
name_OBJECT_FEATURE
```
In the `get_additional_variables` function additional variables can be included that are branches of the input ntuple files.
With `calculate_variables` additional variables can be calculated that are either needed for the evaluation of the DNNs or are supposed to be added to to the new ntuple files, e.g. variables derived from the jet assignments.

For the mode **Matching** also the following functions are needed
```
def get_match_variables():
    '''
    list of variables (usually dR variables) that should be checked for matches
    the matching threshold can be set via the -t argument
    '''
    variables = [
        ]
    return variables

def get_random_index(df, bestIndex):
    '''
    return a random index for the definition of the background
    the default implementation returns any index as long as it is not the correct assignment
    '''
    randomIndex = bestIndex
    while randomIndex==bestIndex:
        randomIndex = np.random.randint(0,df.shape[0])
    return randomIndex
```
