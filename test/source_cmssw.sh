#!/bin/bash
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
cd /nfs/dust/cms/user/swieland/ttH_legacy/CMSSW_11_1_0_pre4/src
eval `scram runtime -sh`
cd -

export KERAS_BACKEND=tensorflow

