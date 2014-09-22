#!/usr/bin/env python
import checkJobs
import os

locationList = ['/nfs_scratch/zmao/W2JetsToLNu/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/submit',
                '/nfs_scratch/zmao/H2hh300_newLept-SUB-TT',
                #'/nfs_scratch/zmao/bothTauID2/TauParked_Run2012D-22Jan2013-v1/submit'
                ]

opt = checkJobs.opts()

for iLocation in locationList:
    opt.location = iLocation
    checkJobs.checkJobs(opt)
    print '************************************************************************************'
    print ''

