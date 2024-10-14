
#!/bin/zsh

echo "setting CMSSW base to /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4"
CMSSW_BASE=/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4


export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
cd /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src
eval `scram runtime -sh`
cd -



python3 /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/scripts/karim.py -M Calculation -c /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/configs/calculate_nlp_feather.py -o /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/friends/nlp_sigbkg_2018  --pred NLP --year 2018   /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/EGamma_Run2018D/tree_77.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/EGamma_Run2018D/tree_25.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/EGamma_Run2018D/tree_170.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/EGamma_Run2018D/tree_220.root
