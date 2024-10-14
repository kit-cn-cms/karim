
#!/bin/bash
subtasklist=(
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_2.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_1.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_5.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_3.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_6.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8/ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_4.sh
)
thescript=${subtasklist[$SGE_TASK_ID]}
echo "starting dir: $PWD"
echo "${thescript}"
echo "$SGE_TASK_ID"
. $thescript
    