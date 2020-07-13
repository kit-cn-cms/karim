testsample="TTbar"
testinput="/nfs/dust/cms/user/vdlinden/karim_test_data/$testsample"
testnetwork="/nfs/dust/cms/user/vdlinden/karim_test_data/networks/recoNN"
testfile="nominal_Tree.root"
testdir="test/reco"
testconfig="../configs/test_config.py"
outfiles="output/ntuples/reco"
outshells="output/scripts/reco"

source source_cmssw.sh

# check if outputs already exist
test -f $outshells && rm -r $outshells
test -f $outfiles && rm -r $outfiles

# execute shell generation command
python ../scripts/generateSubmitScripts.py -M Reconstruction -m $testnetwork -c $testconfig -o $outfiles -s ../test/$outshells $testinput
test -f $outshells/$testsample/"$testsample"_1.sh && echo "success." || {echo "shell script not created" && return 1}

# run script
source $outshells/$testsample/"$testsample"_1.sh
test -f $outfiles/$testsample/$testfile && echo "success." || {echo "ntuple file not created" && return 1}



