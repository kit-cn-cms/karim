# README

A framework using **K**eras to **A**ssign **R**econstruction **I**nformation to **M**VATrees

# ATTENTION

The rework to adjust to the new ntuple structure is currently work in progress.
At the moment the following applications are working:
- calculation

## What is this framework good for?
With this framework a multitude of friend trees for existing ntuples and nanoAOD files can be created.
Various modes enable the user to create various types of friend trees, or just new flat root trees.

The main (name-giving) feature finds the best assignment of jets for a hypothesized particle in your event. This framework is able to evaluate a neural network for all permutations of jets in a given event, chose the best permutation based on the NN output value and write the best configuration to new flat root trees.
The newly created root files retain the original order of events, such that they can be used as friend trees to the original trees.
This enables a fast exchange and update of variables in the ntuples which are based on the assignment of jets to some hypothetical objects, e.g. in case of an updated NN training.

## Setup
This has been tested on CentOS7 on the corresponding NAF nodes `user@naf-cms-el7.desy.de`
Either setup a local `CMSSW_11_3_1` version, or execute the following before every use
```
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
cd /nfs/dust/cms/user/vdlinden/nanoAOD/CMSSW_11_3_1/src
eval `scram runtime -sh`

cd -
```
If `scripts/karim.py` is executed locally make sure the Keras backend is set to `tensorflow`:
```
export KERAS_BACKEND=tensorflow
```
All of the above is automatically set for shell scripts submitted to the NAF batch system. No further python packages should be required.

For reading scale factors an up-to-date installation of the jsonPOG correction lib is needed. This can be for example installed via
```
pip3 install git+https://github.com/cms-nanoAOD/correctionlib.git@master
```
and should regularly be upgraded via
```
pip3 install --upgrade git+https://github.com/cms-nanoAOD/correctionlib.git@master
```



## How does it work?
#### `karim.py`
All scripts that need to be executed are located in the `scripts` directory. Single root files can be processes with `scripts/karim.py`. This requires some inputs:
```
python karim.py -M MODE -c CONFIG.py -o OUTPATH [MODE SPECIFIC OPTIONS] INFILES
```
- `-M MODE`: mode switch for different modes.
- `-c CONFIG`: path to a config file in the config directory. how these config files need to be structured is explained further below.
- `-o OUTPATH`: path to directory where new ntuple files should be created. the structures created in this output directory correspond exactly to the input structure
- `INFILES`: paths to input ntuple files. give as many ntuple files as you want, they are processed sequentially.

The available execution modes are described further below.


#### `generateSubmitScripts.py`
For convenience `scripts/generateSubmitScripts.py` is available to create multiple shell scripts that execute `scripts/karim.py`. These scripts can be submitted to the NAF batch system. This requires some inputs:
```
python generateSubmitScripts.py -M MODE -c CONFIG.py -o OUTPATH -s SHELLPATH [-r NAME -n NEVENTS] [MODE SPECIFIC OPTIONS] SAMPLES
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


## What execution modes are there?

#### Matching

Define objects on generator level that are supposed to be matched to reconstructed objects (i.e. jets)
In the configs you can define which objects to define on reconstruction level, e.g. the both decay products of a Higgs boson
```
objects = ["B1", "B2"]
```
These objects have features which can be defined via
```
features = ["Eta", "Phi", ...]
```
For all combinations of jets in an event these newly defined objects (with corresponding features) are constructed.
You can then implement the calculation of distances of these hypothetical objects to generator quantities. You might for example want to calculate the distance in `deltaR` between a new object and the generator quantity, e.g.
```
df[name+"_dRGen_higgsB1"] = common.get_dR(
    eta1 = df[name+"_B1_Eta"].values,
    phi1 = df[name+"_B1_Phi"].values,   
    eta2 = df["GenHiggsB1_Eta"].values,
    phi2 = df["GenHiggsB1_Phi"].values)
```
Finally you can define which variables to consider when matching, e.g
```
def get_match_variables():
    variables = [
        name+"_dRGen_higgsB1",
        name+"_dRGen_higgsB2"
        ]
```
When calling `karim.py` the threshold for matching (in units of `dR`) can be set via `-t THRESHOLD`, e.g. `-t 0.4` defines a new object to be matched to the generator level quantity when `dR <= 0.4`. 
It is required that all variables that are considered for matching fulfill the matching criterion. 
If such a permutation of jet assignments is found the new objects are written to the outpu
With this mode two files are generated, one called `_sig` and one `_bkg`. This can be used for defining right and wrong jet combinations e.g. for training a reconstruction NN.
The `_sig` files contain the assignment of reco objects to generator objects (if any was found). The `_bkg` files contain a random combination.

#### Reconstruction

With the reconstruction mode a NN that is trained to differentiate between correct and wrong jet assignments to new objects can be evaluated.
This approach is based on the `Matching` mode described previously. The same config can be used.
Additionally you have to specify the NN model that is evaluated with `-m MODEL`.
The permutation of jets that produces the highest output value of the given model is taken as the best hypothesis and is written to a new root file.

#### Evaluation

Independent of the previous two modes this modes enables the fast evaluation of NNs, e.g. classification NNs of the ttH analysis.
For that purpose a `.yml` config has to be created where the NNs, the expected classes and the derived output values and predictions are defined.
This `.yml` file has to be specified via the `-m MODEL` option.
Instructions on how to build such a model config are given in the respective README (`models/README.md`).

#### Calculation

This mode is used to calculate new variables based on features already in the input file.
In the config file you need to initialize new branches in the output file and define calculations for the new variables.

## How to build a new config?
For the `Reconstruction` and `Matching` modes the config files in `config/` are required to generate assignable jet objects and to calculate secondary variables from the hypothesized jet assignments. All functions and variables of the following template are required in these config files:
```
import common

name = "Reco"
def get_naming():
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
Features are for example `btagValue`, `Eta`, `Pt` of jets.
From the combinations of objects and features variables are build. All of them should be named with a common naming scheme 
```
name_OBJECT_FEATURE
```
In the `get_additional_variables` function additional variables can be included that are branches of the input ntuple files.
With `calculate_variables` additional variables can be calculated that are either needed for the evaluation of the NNs or are supposed to be added to to the new ntuple files, e.g. variables derived from the jet assignments.

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

When using the **Evaluation** mode only the functions
```
get_additional_variables()
base_selection(event)
calculate_variables(df)
```
are required. Everything else is set via the model configs

When using the **Calculation** mode only the 
```
get_additional_variables()
base_selction(event)
calculate_variables(event, wrapper)
```
function are needed. In this case the `calculate_variables` function is a little different. it takes two inputs (first the usual `event`) and second a `wrapper` arond the output file.
In the `calculate_variables` function new variables can be calculated and written into the output file, shown here as an example for the c- vs b-tagging value for each jet in the event:
```
for jetIdx in range(event.N_Jets):
    c_vs_b = event.Jet_deepJet_c[jetIdx] / (event.Jet_deepJet_c[jetIdx] + event.Jet_btagValue[jetIdx])
    wrapper.branchArrays["Jet_CvsB"][jetIdx] = c_vs_b
```
Non-vectorized variables need to be set as
```
wrapper.branchArrays["N_Jets"][0] = event.N_Jets
```
In addition a new function is needed to initialize the branches in the output file:
```
def set_branches(wrapper):
    '''
    initialize branches of output root file
    '''
    # integer variable
    wrapper.SetIntVar("Evt_ID")
    
    # float variable
    wrapper.SetFloatVar("Evt_Rho")
    
    # array of float variables (second argument is array length)
    wrapper.SetFloatVarArray("Jet_Mt", N_Jets)
```
