testsample="TTbar"
testinput="/nfs/dust/cms/user/vdlinden/karim_test_data/$testsample"
testfile="nominal_Tree.root"
testconfig="../configs/test_config.py"
testmodel="../models/test_model.yml"
outfiles="output/ntuples/eval"
outshells="output/scripts/eval"

source source_cmssw.sh

# check if outputs already exist
test -f $outshells && rm -r $outshells
test -f $outfiles && rm -r $outfiles

# execute shell generation command
python ../scripts/generateSubmitScripts.py -M Evaluation -m $testmodel -c $testconfig -o $outfiles -s ../test/$outshells $testinput
test -f $outshells/$testsample/"$testsample"_1.sh && echo "success." || {echo "shell script not created" && return 1}

# run script
source $outshells/$testsample/"$testsample"_1.sh
test -f $outfiles/$testsample/$testfile && echo "success." || {echo "ntuple file not created" && return 1}



