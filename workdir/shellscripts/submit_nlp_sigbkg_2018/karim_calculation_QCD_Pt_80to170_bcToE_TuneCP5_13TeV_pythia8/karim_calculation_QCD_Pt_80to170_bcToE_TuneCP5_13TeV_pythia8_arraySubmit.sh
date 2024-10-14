
#!/bin/bash
subtasklist=(
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/QCD_Pt_80to170_bcToE_TuneCP5_13TeV_pythia8/QCD_Pt_80to170_bcToE_TuneCP5_13TeV_pythia8_1.sh
)
thescript=${subtasklist[$SGE_TASK_ID]}
echo "starting dir: $PWD"
echo "${thescript}"
echo "$SGE_TASK_ID"
. $thescript
    