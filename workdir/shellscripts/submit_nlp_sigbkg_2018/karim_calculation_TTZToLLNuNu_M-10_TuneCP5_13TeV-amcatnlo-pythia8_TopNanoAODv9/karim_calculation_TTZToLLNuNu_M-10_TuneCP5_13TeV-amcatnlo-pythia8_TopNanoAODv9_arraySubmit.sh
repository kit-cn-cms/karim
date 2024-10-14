
#!/bin/bash
subtasklist=(
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_10.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_4.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_3.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_9.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_6.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_2.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_8.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_7.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_5.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9/TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_TopNanoAODv9_1.sh
)
thescript=${subtasklist[$SGE_TASK_ID]}
echo "starting dir: $PWD"
echo "${thescript}"
echo "$SGE_TASK_ID"
. $thescript
    