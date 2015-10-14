#!/usr/bin/env python
import os


inputDir = '/nfs_scratch/zmao/supy-output//slice/'
outputDir = '/nfs_scratch/zmao/13TeV_samples_25ns_Spring15_eletronID2/'
append_name = 'tightMuon'

finalStates = {'et': [('data_Electron_events.root', "data_all_SYNC_et_%s.root" %append_name), ("DY_events.root", "DY_all_SYNC_et_%s.root" %append_name)],
               #'mt': [('data_Muon_events.root', "data_all_SYNC_mt_%s.root" %append_name), ("DY_events.root", "DY_all_SYNC_mt_%s.root" %append_name)],
               }


for ikey in finalStates.keys():
    for i in range(len(finalStates[ikey])):
        command = "cp %s/%s/%s %s/%s" %(inputDir, ikey, finalStates[ikey][i][0], outputDir, finalStates[ikey][i][1])
   #     os.system(command)

for i in range(1, 101):
    print "copying file %i" %i
    command = "xrdcp root://cmsxrootd.fnal.gov//store/user/gurrola/WRToNuTauToTauTau/MINIAOD_WR1000_HeavyNu500_pythia6_Asympt25ns_0PU/150927_011627/0000/miniAOD_%i.root /nfs_scratch//zmao/WRToNuTauToTauTau_1000/" %i
    os.system(command)
    

for i in range(100, 101):
    print "copying file %i" %i
    command = "xrdcp root://cmsxrootd.fnal.gov//store/user/gurrola/WRToNuTauToTauTau/MINIAOD_WR2700_HeavyNu1350_pythia6_Asympt25ns_0PU/150926_102208/0000/miniAOD_%i.root /nfs_scratch//zmao/WRToNuTauToTauTau_2700/" %i
    os.system(command)
