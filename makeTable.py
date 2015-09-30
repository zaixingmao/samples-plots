#!/usr/bin/env python

import ROOT as r



def loopOneFile(iFile):
    file = r.TFile(iFile)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    onlySingleTrigger = 0.0
    bothTriggers = 0.0
    bothWithTauPt40 = 0.0
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        #tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        if tree.q_1 == tree.q_2:
            continue
        bothTriggers += 1.0
        if tree.singleEPass and tree.eSingleEle and tree.ePt > 33.0:
            onlySingleTrigger += 1.0
        if (not (tree.singleEPass and tree.eSingleEle)):
            if tree.tPt > 40:
                bothWithTauPt40 += 1.0
        else:
            bothWithTauPt40 += 1.0

    return bothTriggers, onlySingleTrigger, bothWithTauPt40


fileList = ['ZPrime_500', 'ZPrime_1000', 'ZPrime_1500', 'ZPrime_2000', #'ZPrime_2500',
            'ZPrime_3000', 'ZPrime_3500', 'ZPrime_4000', #'ZPrime_4500',
            'ZPrime_5000', 'SUSY']


print "sample \t\t only_Single_Ele_Trig \t both_Trigs \t gain"
for iFile in fileList:
    bothTriggers, onlySingleTrigger,bothWithTauPt40 = loopOneFile("/nfs_scratch/zmao/13TeV_samples_25ns_Spring15_eletronID2/%s_all_SYNC_et_inclusive.root" %iFile)
#    print "%s \t %.0f \t\t\t %.0f \t\t %.2f%% \t\t\t %.0f \t\t %.2f%%" %(iFile, onlySingleTrigger, bothTriggers, (bothTriggers/onlySingleTrigger-1)*100, bothWithTauPt40, (bothWithTauPt40/onlySingleTrigger-1)*100) 
    print "%.0f (+%.1f%%)" %(bothWithTauPt40, (bothWithTauPt40/onlySingleTrigger-1)*100)
