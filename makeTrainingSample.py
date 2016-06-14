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
import random
lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
l1 = lvClass()
l2 = lvClass()
met = lvClass()


def setUpFloatVarsDict():
    varDict = {}
    names = ['pt_1', 'eta_1', 'phi_1', 'm_1',
            'pt_2', 'eta_2', 'phi_2', 'm_2',
            'met', 'met_phi',
            'jpt_1', 'jeta_1', 'jphi_1',
            'jpt_2', 'jeta_2', 'jphi_2',
            'pZetaCut', 'm_eff', 'weightWithPU']
    for iName in names:
        varDict[iName] = array('f', [0.])

    return varDict

def runOneFile(iFS, inputFile, signSelect, isoSelect, output_dir, split):
    inputFile = inputFile + "%s_noIso.root" %iFS
    ifile = r.TFile(inputFile)
    iTree = ifile.Get("Ntuple")
    eventCountWeighted = ifile.Get('eventCountWeighted')

    oString = signSelect + isoSelect

    outputFile = "%s_%s.root" %(output_dir+inputFile[inputFile.rfind("/"):inputFile.find(".root")], oString)
    oFile = r.TFile(outputFile,"recreate")

    iTree.SetBranchStatus("*",1)

    oTree = r.TTree('eventTree','')
    oTree_train = r.TTree('eventTree_train','')
    oTree_test = r.TTree('eventTree_test','')

    total = iTree.GetEntries()

    Lumi = plots.lumi
    isData = False
    isSignal = False

    floatVarsDict = setUpFloatVarsDict()

    for iVar in floatVarsDict.keys():
        oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/f" %iVar)
        oTree_train.Branch("%s" %iVar, floatVarsDict[iVar], "%s/f" %iVar)
        oTree_test.Branch("%s" %iVar, floatVarsDict[iVar], "%s/f" %iVar)

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
                if split:
                    floatVarsDict['weightWithPU'][0] = 2*floatVarsDict['weightWithPU'][0]

            met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)
            l1.SetCoordinates(iTree.pt_1, iTree.eta_1, iTree.phi_1, iTree.m_1)
            l2.SetCoordinates(iTree.pt_2, iTree.eta_2, iTree.phi_2, iTree.m_2)

            floatVarsDict['pt_1'][0] = iTree.pt_1
            floatVarsDict['eta_1'][0] = iTree.eta_1
            floatVarsDict['phi_1'][0] = iTree.phi_1
            floatVarsDict['m_1'][0] = iTree.m_1
            floatVarsDict['pt_2'][0] = iTree.pt_2
            floatVarsDict['eta_2'][0] = iTree.eta_2
            floatVarsDict['phi_2'][0] = iTree.phi_2
            floatVarsDict['m_2'][0] = iTree.m_2
            floatVarsDict['met'][0] = iTree.pfMetEt
            floatVarsDict['met_phi'][0] = iTree.pfMetPhi
            floatVarsDict['jpt_1'][0] = iTree.jpt_1
            if iTree.jpt_1 > 0:
                floatVarsDict['jeta_1'][0] = iTree.jeta_1
                floatVarsDict['jphi_1'][0] = iTree.jphi_1
            else:
                floatVarsDict['jeta_1'][0] = -999.0
                floatVarsDict['jphi_1'][0] = -999.0
            floatVarsDict['jpt_2'][0] = iTree.jpt_2
            if iTree.jpt_2 > 0:
                floatVarsDict['jeta_2'][0] = iTree.jeta_2
                floatVarsDict['jphi_2'][0] = iTree.jphi_2
            else:
                floatVarsDict['jeta_2'][0] = -999.0
                floatVarsDict['jphi_2'][0] = -999.0
            floatVarsDict['pZetaCut'][0] = iTree.pZetaCut
            floatVarsDict['m_eff'][0] = iTree.m_eff
            oTree.Fill()
            if random.random() < 0.5:
                oTree_train.Fill()
            else:
                oTree_test.Fill()

    print ''
    oFile.cd()
    if not split:
        oTree.Write()
        nSaved = oTree.GetEntries()
        print 'saved %i events out of %i at: %s' %(nSaved,total,outputFile)
    else:
        oTree_train.Write()
        nSaved = oTree_train.GetEntries()
        print 'for training: saved %i events out of %i at: %s' %(nSaved,total,outputFile)
        oTree_test.Write()
        nSaved = oTree_test.GetEntries()
        print 'for testing: saved %i events out of %i at: %s' %(nSaved,total,outputFile)
    oFile.Close()

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
             (fs, '%s/WJets_LO_HT-0to100_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/WJets_LO_HT-100to200_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/WJets_LO_HT-200to400_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/WJets_LO_HT-400to600_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
             (fs, '%s/WJets_LO_HT-600toInf_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
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
#              (fs, '%s/data_Electron_all_SYNC_' %dir, 'OS', 'Loose', output_dir),
             (fs, '%s/data_Electron_all_SYNC_' %dir, 'OS', 'Tight', output_dir),
            ]

split = True
cutSampleTools.setupLumiReWeight()
for iFS, iSample, iCharge, iIsoRegion, output_dir in listToRun:
    runOneFile(iFS, iSample, iCharge, iIsoRegion, output_dir, split)    
cutSampleTools.freeLumiReWeight()


