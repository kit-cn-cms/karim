
#!/bin/bash
subtasklist=(
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9_6.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9_5.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9_7.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9_3.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9_2.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9_1.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9_4.sh
)
thescript=${subtasklist[$SGE_TASK_ID]}
echo "starting dir: $PWD"
echo "${thescript}"
echo "$SGE_TASK_ID"
. $thescript
    