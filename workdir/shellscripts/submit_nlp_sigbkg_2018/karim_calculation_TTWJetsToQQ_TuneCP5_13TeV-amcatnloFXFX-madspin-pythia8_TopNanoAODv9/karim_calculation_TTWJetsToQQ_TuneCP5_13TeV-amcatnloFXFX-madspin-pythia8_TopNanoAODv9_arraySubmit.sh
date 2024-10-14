
#!/bin/bash
subtasklist=(
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_TopNanoAODv9/TTWJetsToQQ_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_TopNanoAODv9_1.sh
)
thescript=${subtasklist[$SGE_TASK_ID]}
echo "starting dir: $PWD"
echo "${thescript}"
echo "$SGE_TASK_ID"
. $thescript
    