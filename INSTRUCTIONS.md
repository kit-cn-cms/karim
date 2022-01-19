## Instructions for evaluating HYU DNNs

The setup has been tested with a `CMSSW_11_3_1` installation and setting the Keras backend to tensorflow via
```bash
export KERAS_BACKEND=tensorflow
```

It can be tested if the general setup works e.g. via
```python
cd scripts

python3 karim.py -M "R" -c ../configs/evaluate_HYU_DNN.py -o ../workdir/testEval -j -y 2018 -m test /PATH/TO/KIT/NTUPLE/FILE.root
```

The options that have to be set are:
- `-M`: Mode for running the framework, where "R" refers to the reconstruction mode used to evaluate the DNNs
- `-c`: path to the config file
- `-o`: output directory for files and ntuples
- `-j`: flag to specify that this is to be done for each available JEC source
- `-y`: data era (here 2018)
- `-m`: path to the trained DNN model from Keras. If "test" is given a random dummy DNN is evaluated for testing the general event loop setup
- `ARGS`: list of ntuple files as input


