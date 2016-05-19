#!/bin/bash

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc493

cd /cvmfs/cms.cern.ch/slc6_amd64_gcc493/cms/cmssw/CMSSW_7_6_3/src && eval `scram runtime -sh` && cd - >& /dev/null

#INSERT_BATCH_SETUP

if [ -e `pwd`/local.sh ]; then
    source `pwd`/local.sh
fi
