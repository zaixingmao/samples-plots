#!/usr/bin/env python


import checkJobs
import os

postFix = 'shift'

locationList = [# '/nfs_scratch/zmao/nt_H2hh260_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh270_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh280_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh290_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh300_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh310_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh320_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh330_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh340_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_H2hh350_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/H2hh500_rad_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/H2hh700_rad_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/H2hh1000_rad_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_ttfull_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_ttsemi_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/v4/DY4JetsToLL_M-50_TuneZ2Star_8TeV-madgraph'
#                 '/nfs_scratch/zmao/nt_zz_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_w1_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_w2_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_w3_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_wz_%s-SUB-TT' %postFix, 
#                 '/nfs_scratch/zmao/nt_dy_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_dy1_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_dy2_%s-SUB-TT' %postFix,
#                 '/nfs_scratch/zmao/nt_dy3_%s-SUB-TT' %postFix,
                '/nfs_scratch/zmao/nt_dy4_%s-SUB-TT' %postFix,

#                 '/nfs_scratch/zmao/nt_tau_A_%s-SUB-TT-data' %postFix,
#                 '/nfs_scratch/zmao/nt_tauP_B_%s-SUB-TT-data' %postFix,
#                 '/nfs_scratch/zmao/nt_tauP_C_%s-SUB-TT-data' %postFix,
#                 '/nfs_scratch/zmao/nt_tauP_D_%s-SUB-TT-data' %postFix,
                ]

opt = checkJobs.opts()

for iLocation in locationList:
    opt.location = iLocation
    checkJobs.checkJobs(opt)
    print '************************************************************************************'
    print ''

