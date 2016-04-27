#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array
import struct
import makeWholeTools2
import plots
import plots_cfg
import cutSampleTools
lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
l1 = lvClass()
l2 = lvClass()
met = lvClass()


def setUpFloatVarsDict():
    varDict = {}
    names = ['met', 'pZetaCut', 'cosDPhi', 'm_eff', 'weightWithPU']
    for iName in names:
        varDict[iName] = array('f', [0.])

    return varDict

def runOneFile(iFS, inputFile, signSelect, isoSelect, output_dir):
    inputFile = inputFile + "%s_noIso.root" %iFS
    ifile = r.TFile(inputFile)
    iTree = ifile.Get("Ntuple")
    eventCountWeighted = ifile.Get('eventCountWeighted')

    oString = signSelect + isoSelect
    outputFile = "%s_%s.root" %(output_dir+inputFile[inputFile.rfind("/"):inputFile.find(".root")], oString)
    oFile = r.TFile(outputFile,"recreate")

    iTree.SetBranchStatus("*",1)

    oTree = r.TTree('eventTree','')
    total = iTree.GetEntries()

    Lumi = plots.lumi
    isData = False
    isSignal = False

    floatVarsDict = setUpFloatVarsDict()

    for iVar in floatVarsDict.keys():
        oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/f" %iVar)

    isoSelection = 'control'
    if isoSelect == 'Tight':
        isoSelection = 'signal'

    for i in range(total):
        r.gStyle.SetOptStat(0)
        tool.printProcessStatus(iCurrent=i, total=total, processName = 'Looping sample %s' %inputFile)
        iTree.GetEntry(i)

        if 'data' in iTree.sampleName:
            isData = True
        if 'ZPrime' in iTree.sampleName:
            isSignal = True

        if signSelect == 'OS' and iTree.q_1 == iTree.q_2:
            continue
        elif signSelect == 'SS' and iTree.q_1 != iTree.q_2:
            continue
        if plots.regionSelection(iTree, iFS, isoSelection, 'Loose', plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            if isData:
                floatVarsDict['weightWithPU'][0] = 1.0            
            else:
                floatVarsDict['weightWithPU'][0] = cutSampleTools.getPUWeight(iTree.nTruePU)*iTree.xs*Lumi*iTree.genEventWeight/(int(eventCountWeighted.GetBinContent(1)))

            met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)
            l1.SetCoordinates(iTree.pt_1, iTree.eta_1, iTree.phi_1, iTree.m_1)
            l2.SetCoordinates(iTree.pt_2, iTree.eta_2, iTree.phi_2, iTree.m_2)

            floatVarsDict['met'][0] = iTree.met
            floatVarsDict['pZetaCut'][0] = iTree.pZetaCut
            floatVarsDict['cosDPhi'][0] = iTree.cosDPhi
            floatVarsDict['m_eff'][0] = iTree.m_eff
            oTree.Fill()

    print ''

    oFile.cd()
    oTree.Write()
    nSaved = oTree.GetEntries()
    oFile.Close()
    print 'saved %i events out of %i at: %s' %(nSaved,total,outputFile)


dir = '/user_data/zmao/NoBTag_7_6_X'
output_dir = '/user_data/zmao/TMVA/'

fs = 'em'
listToRun = [(fs, '%s/DY-50to200_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/DY-200to400_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/DY-400to500_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/DY-500to700_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/DY-700to800_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/DY-800to1000_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/DY-1000to1500_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/antiT_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/antiT_t-channel_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/T_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/T_t-channel_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/TTJets_LO_all_SYNC_' %dir, 'OS', 'Tight', output_dir),

             (fs, '%s/WZTo1L3Nu_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/WWTo1L1Nu2Q_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/WZTo1L1Nu2Q_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/WZJets_all_SYNC_' %dir, 'OS', 'Tight', output_dir),

             (fs, '%s/ZZTo2L2Q_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/WZTo2L2Q_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/VVTo2L2Nu_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/ZZTo4L_all_SYNC_' %dir, 'OS', 'Tight', output_dir),

             (fs, '%s/ZPrime_500_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/ZPrime_1000_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/ZPrime_1500_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/ZPrime_2000_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/ZPrime_2500_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/ZPrime_3000_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/ZPrime_3500_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/ZPrime_4000_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/data_Electron_all_SYNC_' %dir, 'OS', 'Loose', output_dir),
            ]

cutSampleTools.setupLumiReWeight()
for iFS, iSample, iCharge, iIsoRegion, output_dir in listToRun:
    runOneFile(iFS, iSample, iCharge, iIsoRegion, output_dir)    
cutSampleTools.freeLumiReWeight()


