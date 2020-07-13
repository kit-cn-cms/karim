testsample="TTbar"
testinput="/nfs/dust/cms/user/vdlinden/karim_test_data/$testsample"
testfile="nominal_Tree.root"
testdir="test/matching"
testconfig="../configs/test_config.py"
outfiles="output/ntuples/matching"
outshells="output/scripts/matching"

source source_cmssw.sh

# check if outputs already exist
test -f $outshells && rm -r $outshells
test -f $outfiles && rm -r $outfiles

# execute shell generation command
python ../scripts/generateSubmitScripts.py -M Matching -t 0.2 -c $testconfig -o $outfiles -s ../test/$outshells $testinput
test -f $outshells/$testsample/"$testsample"_1.sh && echo "success." || {echo "shell script not created" && return 1}

# run script
source $outshells/$testsample/"$testsample"_1.sh
test -f $outfiles/$testsample/${testfile:0:-5}_sig.root && echo "success." || {echo "ntuple file not created" && return 1}
test -f $outfiles/$testsample/${testfile:0:-5}_bkg.root && echo "success." || {echo "ntuple file not created" && return 1}



