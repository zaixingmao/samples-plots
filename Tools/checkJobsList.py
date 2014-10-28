#!/usr/bin/env python


import checkJobs
import os

locationList = [#'/nfs_scratch/zmao/W2JetsToLNu/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/submit',
                #'/nfs_scratch/zmao/H2hh300_newLept-SUB-TT',
                #'/nfs_scratch/zmao/bothTauID2/TauParked_Run2012D-22Jan2013-v1/submit'

                #'/nfs_scratch/elaird/nt_H2hh260_v1-SUB-TT',
                #'/nfs_scratch/elaird/nt_H2hh300_v1-SUB-TT',
                #'/nfs_scratch/elaird/nt_H2hh350_v1-SUB-TT',
                #'/nfs_scratch/elaird/nt_ttfull_v1-SUB-TT',
                #'/nfs_scratch/elaird/nt_ttsemi_v1-SUB-TT',
                '/nfs_scratch/elaird/nt_zz_v1-SUB-TT',

                #'/nfs_scratch/elaird/nt_tau_A_v1-SUB-TT-data',
                #'/nfs_scratch/elaird/nt_tauP_B_v1-SUB-TT-data',
                #'/nfs_scratch/elaird/nt_tauP_C_v1-SUB-TT-data',
                #'/nfs_scratch/elaird/nt_tauP_D_v1-SUB-TT-data',
                ]

opt = checkJobs.opts()

for iLocation in locationList:
    opt.location = iLocation
    checkJobs.checkJobs(opt)
    print '************************************************************************************'
    print ''

