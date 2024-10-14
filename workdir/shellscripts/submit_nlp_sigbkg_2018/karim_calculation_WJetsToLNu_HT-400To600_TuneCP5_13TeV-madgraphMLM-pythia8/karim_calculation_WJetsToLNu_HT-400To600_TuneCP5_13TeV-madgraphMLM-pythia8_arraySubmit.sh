
#!/bin/bash
subtasklist=(
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_1.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_2.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8/WJetsToLNu_HT-400To600_TuneCP5_13TeV-madgraphMLM-pythia8_3.sh
)
thescript=${subtasklist[$SGE_TASK_ID]}
echo "starting dir: $PWD"
echo "${thescript}"
echo "$SGE_TASK_ID"
. $thescript
    