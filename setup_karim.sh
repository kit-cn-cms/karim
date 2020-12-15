export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
cd /nfs/dust/cms/user/vdlinden/legacyTTH/CMSSW/CMSSW_10_6_8_patch1/src
eval `scram runtime -sh`
cd ..
