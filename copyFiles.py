#!/usr/bin/env python
import os


inputDir = '/nfs_scratch/zmao/supy-output//slice/'
outputDir = '/nfs_scratch/zmao/miniAODv2_ntuples_noIso/'
append_name = 'noIso'



# finalStates = {'em': [('data_MuonEG_events.root', "data_all_SYNC_em_%s.root" %append_name), 
#                       ("DY_events.root", "DY_all_SYNC_" %append_name),
#                       ("WJets_events.root", "WJets_all_SYNC_em_%s.root" %append_name),
# 
#                       ("WW_events.root", "WW_all_SYNC_em_%s.root" %append_name),
#                       ("WZ_events.root", "WZ_all_SYNC_em_%s.root" %append_name),
#                       ("ZZ_events.root", "ZZ_all_SYNC_em_%s.root" %append_name),
#                       ("antiT_events.root", "antiT_all_SYNC_em_%s.root" %append_name),
#                       ("T_events.root", "T_all_SYNC_em_%s.root" %append_name),
#                      ] + [('ZPrime_%d_events.root' % m, 'ZPrime_%d_all_SYNC_em_%s.root' % (m, append_name)) for m in (set(range(500, 5500, 500)))],
#                #'mt': [('data_Muon_events.root', "data_all_SYNC_mt_%s.root" %append_name), ("DY_events.root", "DY_all_SYNC_mt_%s.root" %append_name)],
#                }

files = ['DY-50_events.root',
         'DY-10to50_events.root',
         'WJets_events.root',
         'WJets_MLM_events.root',
         'WW_events.root',
         'ggH_events.root',
         'WZ_events.root',
         'ZZ_events.root',
         'T_events.root',
         'antiT_events.root',
#          'ZPrime_1000_events.root',
#          'ZPrime_2000_events.root',
#          'ZPrime_2500_events.root',
#          'ZPrime_4000_events.root',
#          'ZPrime_4500_events.root',
#          'ZPrime_5000_events.root',
#         'ZPrime_3500_events.root',
#         'ZPrime_3000_events.root',
#         'ZPrime_500_events.root',
#         'ZPrime_1500_events.root',
# #          'SUSY_events.root',
        'vbfH_events.root',
        'TTJets_events.root',
        ]




# for ikey in finalStates.keys():
#     for i in range(len(finalStates[ikey])):
#         command = "cp %s/%s/%s %s/%s" %(inputDir, ikey, finalStates[ikey][i][0], outputDir, finalStates[ikey][i][1])
#         print command
#         os.system(command)

for fs in ['em']:#, 'em', 'mt', 'tt']:
    for iFile in files:
        command = "cp %s/%s/%s %s/%s_all_SYNC_%s_%s.root" %(inputDir, fs, iFile, outputDir, iFile[:iFile.find("_events")], fs, append_name)
        os.system(command)

# for i in range(1, 101):
# 
#     command = "xrdcp root://cmsxrootd.fnal.gov//store/user/gurrola/WRToNuTauToTauTau/MINIAOD_WR1000_HeavyNu500_pythia6_Asympt25ns_0PU/150927_011627/0000/miniAOD_%i.root /nfs_scratch//zmao/WRToNuTauToTauTau_1000/" %i
# #    os.system(command)
#     
# 
# for i in range(100, 101):
# 
#     command = "xrdcp root://cmsxrootd.fnal.gov//store/user/gurrola/WRToNuTauToTauTau/MINIAOD_WR2700_HeavyNu1350_pythia6_Asympt25ns_0PU/150926_102208/0000/miniAOD_%i.root /nfs_scratch//zmao/WRToNuTauToTauTau_2700/" %i
# #    os.system(command)
