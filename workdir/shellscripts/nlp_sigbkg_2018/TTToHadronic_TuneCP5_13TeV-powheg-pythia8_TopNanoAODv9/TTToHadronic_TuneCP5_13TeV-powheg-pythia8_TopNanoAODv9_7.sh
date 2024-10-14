
#!/bin/zsh

echo "setting CMSSW base to /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4"
CMSSW_BASE=/nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4


export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
cd /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src
eval `scram runtime -sh`
cd -



python3 /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/scripts/karim.py -M Calculation -c /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/configs/calculate_nlp_feather.py -o /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/karim/friends/nlp_sigbkg_2018  --pred NLP --year 2018   /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_46.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_34.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_58.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_89.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_90.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_68.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_97.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_82.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_60.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_93.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_126.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_85.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_51.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_67.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_54.root /nfs/dust/cms/user/rrafeek/CMSSW_14_1_0_pre4/src/smeacol/workdir/ntuples_GNN_2018/ntuples/2018/TTToHadronic_TuneCP5_13TeV-powheg-pythia8_TopNanoAODv9/tree_53.root
