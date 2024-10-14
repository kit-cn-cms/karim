
#!/bin/bash
subtasklist=(
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_13.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_18.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_10.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_5.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_6.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_12.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_9.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_21.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_14.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_7.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_19.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_4.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_3.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_15.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_1.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_20.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_17.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_22.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_11.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_16.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_8.sh
/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/workdir/shellscripts/nlp_sigbkg_2018/EGamma_Run2018A/EGamma_Run2018A_2.sh
)
thescript=${subtasklist[$SGE_TASK_ID]}
echo "starting dir: $PWD"
echo "${thescript}"
echo "$SGE_TASK_ID"
. $thescript
    