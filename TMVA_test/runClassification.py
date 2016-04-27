#!/user/bin/env python

import os as os

fs = 'em'

fileListNormal = ['DY-50to200_all_SYNC_%s_noIso' %fs,
                 'DY-200to400_all_SYNC_%s_noIso' %fs,
                 'DY-400to500_all_SYNC_%s_noIso' %fs,
                 'DY-500to700_all_SYNC_%s_noIso' %fs,
                 'DY-700to800_all_SYNC_%s_noIso' %fs,
                 'DY-800to1000_all_SYNC_%s_noIso' %fs,
                 'DY-1000to1500_all_SYNC_%s_noIso' %fs,
                 'antiT_all_SYNC_%s_noIso' %fs,
                 'antiT_t-channel_all_SYNC_%s_noIso' %fs,
                 'T_all_SYNC_%s_noIso' %fs,
                 'T_t-channel_all_SYNC_%s_noIso' %fs,
                 'TTJets_LO_all_SYNC_%s_noIso' %fs,
                 'WZTo1L3Nu_all_SYNC_%s_noIso' %fs,
                 'WWTo1L1Nu2Q_all_SYNC_%s_noIso' %fs,
                 'WZTo1L1Nu2Q_all_SYNC_%s_noIso' %fs,
                 'WZJets_all_SYNC_%s_noIso' %fs,
                 'ZZTo2L2Q_all_SYNC_%s_noIso' %fs,
                 'WZTo2L2Q_all_SYNC_%s_noIso' %fs,
                 'VVTo2L2Nu_all_SYNC_%s_noIso' %fs,
                 'ZZTo4L_all_SYNC_%s_noIso' %fs,
                 'WJets_LO_HT-0to100_all_SYNC_%s_noIso' %fs,
                 'WJets_LO_HT-100to200_all_SYNC_%s_noIso' %fs,
                 'WJets_LO_HT-200to400_all_SYNC_%s_noIso' %fs,
                 'WJets_LO_HT-400to600_all_SYNC_%s_noIso' %fs,
                 'WJets_LO_HT-600toInf_all_SYNC_%s_noIso' %fs,
                 'ZPrime_500_all_SYNC_%s_noIso' %fs,
                 'ZPrime_1000_all_SYNC_%s_noIso' %fs,
                 'ZPrime_1500_all_SYNC_%s_noIso' %fs,
                 'ZPrime_2000_all_SYNC_%s_noIso' %fs,
                 'ZPrime_2500_all_SYNC_%s_noIso' %fs,
                 'ZPrime_3000_all_SYNC_%s_noIso' %fs,
                 'ZPrime_3500_all_SYNC_%s_noIso' %fs,
                 'ZPrime_4000_all_SYNC_%s_noIso' %fs,
                 'data_Electron_all_SYNC_%s_noIso' %fs,
                ]


massPoints = ['500', '1500', '2000', '2500', '3000', '3500', '4000']
# Shifts = ['tauUp', 'tauDown', 'jetUp', 'jetDown', 'bSys', 'bMis']
Shifts = ['normal']

dir = '/user_data/zmao/NoBTag_7_6_X/'

for shift in Shifts:
    outputLocation = "%s%s/" %(dir, shift)
    for massPoint in massPoints:
#         location = '%s/%s/' %(dir, shift)
        location = dir
        oLocation = '%s' %(outputLocation)
        oLocation += "%s/" %massPoint
        if not os.path.isdir(oLocation):
            os.makedirs(oLocation)
        if shift == 'normal':
            fileList = fileListNormal
        else:
            fileList = fileListShift
        for iFile in fileList:
            rootCommand = "root -l -q  TMVAClassificationApplication_new.C\(\\\"BDT\\\",\\\"%s.root\\\",\\\"both\\\",\\\"%s\\\",\\\"%s\\\",\\\"%s\\\"\)" %(iFile, location, massPoint, oLocation)
            os.system(rootCommand)
