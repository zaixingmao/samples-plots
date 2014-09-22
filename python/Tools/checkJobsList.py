#!/usr/bin/env python
import checkJobs
import os

locationList = ['/nfs_scratch/zmao/bothTauID2/TauParked_Run2012B-22Jan2013-v1/submit',
                '/nfs_scratch/zmao/bothTauID2/TauParked_Run2012C-22Jan2013-v1/submit',
                '/nfs_scratch/zmao/bothTauID2/TauParked_Run2012D-22Jan2013-v1/submit'
                ]

for iLocation in locationList:
    os.chdir(iLocation)
    print 'In %s' %iLocation
    checkJobs.checkJobs()
    print ' '

