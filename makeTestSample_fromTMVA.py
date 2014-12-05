#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array
import makeWholeSample_cfg
import makeWholeTools

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

def passCut(tree):
    if tree.chi2KinFit < -10:
        return 0
    return 1

def passCheckSame(list1, list2):
    for i in list1:
        if i in list2:
            print i, 'found same'
            return 0
    return 1

def passCheckReoccur(list):
    for i in list:
        counter = 0
        for j in list:
            if j == i:
                counter += 1
            if counter > 1:
                print 'reoccur', j
                return 0
    return 1

def fingerPrintSet(tree, sampleName, style):
    if 'tau' in style:
        return (tree.mJJ, tree.CSVJ2, tree.PUWeight, sampleName)
    else:
        return (tree.dRTauTau, tree.vertices, tree.LUMI, tree.PUWeight, sampleName)


def makeTestOnly(iLocation, iMass, iFileList, shift):
    ifile = r.TFile(iLocation)
    iTestTree = ifile.Get('TestTree')
    totalTest = iTestTree.GetEntries()
    iTrainTree = ifile.Get('TrainTree')
    totalTrain = iTrainTree.GetEntries()
    EventList = []
    EventList2 = []
    sampleName2 = array('i', [0])
    category2 = array('i', [0])
    svMass1 = array('f', [0.])
    met1 = array('f', [0.])
    sampleNameList = []
    category_char = bytearray(30)

    for i in range(totalTest):
        tool.printProcessStatus(iCurrent=i+1, total=totalTest, processName = 'Looping sample [%s]' %iLocation)
        iTestTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(iTestTree.sampleName2, 'decode')
        if 'data' not in tmpSampleName:
#             EventList.append((int(iTestTree.EVENT), tmpSampleName))
            EventList.append(fingerPrintSet(iTestTree, tmpSampleName, shift))
        if tmpSampleName not in sampleNameList:
            sampleNameList.append(tmpSampleName)
    print ' --- events in test tree: %i' %len(EventList)
    if not passCheckReoccur(EventList):
        return 0

    for i in range(totalTrain):
        tool.printProcessStatus(iCurrent=i+1, total=totalTrain, processName = 'Looping sample [%s]' %iLocation)
        iTrainTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(iTrainTree.sampleName2, 'decode')
        if tmpSampleName not in sampleNameList:
            sampleNameList.append(tmpSampleName)
        if 'data' not in tmpSampleName:
            EventList2.append(fingerPrintSet(iTrainTree, tmpSampleName, shift))
    print ' --- events in train tree: %i' %len(EventList2)
    if not passCheckReoccur(EventList2):
        return 0

    if not passCheckSame(EventList, EventList2):
        return 0

    for iFile in iFileList:
        tmpFile = r.TFile(iFile)
        tmpTree = tmpFile.Get('eventTree')
        oFileName = iFile[0:iFile.find('.root')]
        oFileName += '_%s_testOnly.root' %iMass
        oFile = r.TFile(oFileName,'recreate')
        oTree = tmpTree.CloneTree(0)
#         oTree.Branch("sampleName2", sampleName2, "sampleName2/I")
#         oTree.Branch("category2", category2, "category2/I")
#         oTree.Branch("Category", category_char, "Category[31]/C")
#         oTree.Branch("svMass1", svMass1, "svMass1/F")
#         oTree.Branch("met1", met1, "met1/F")

        total = tmpTree.GetEntries()
        counter = 0
        for i in range(total):
            tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %iFile)
            tmpTree.GetEntry(i)
            if '_semi' in tmpTree.sampleName:
                tmpName = tmpTree.sampleName[0:tmpTree.sampleName.find('_semi')+5]
            elif '_' in tmpTree.sampleName:
                tmpName = tmpTree.sampleName[0:tmpTree.sampleName.find('_')]
            else:
                tmpName = tmpTree.sampleName
            if tmpName not in sampleNameList:
                continue
            sampleName2[0] = tool.nameEnDecoder(tmpName, 'encode')
            svMass1[0] = tmpTree.svMass.at(0)
            met1[0] = tmpTree.met.at(0)

            category2[0] = 0
            if tmpTree.category == '1M1NonM':
                category_char[:31] = '1M'
            else:
                category_char[:31] = tmpTree.category
            if not passCut(tmpTree):
                continue
            if fingerPrintSet(tmpTree, tmpName, shift) in EventList:
                oTree.Fill()
                counter += 1
            elif fingerPrintSet(tmpTree, tmpName, shift) not in EventList2:
                oTree.Fill()
                counter += 1

        print ' --- saved %i' %counter
        oFile.cd()
        oTree.Write()
        oFile.Close()


# massPoints = ['260','300','350']

massPoints = ['260', '270', '280', '290', '300', '310', '320', '330', '340', '350']

nTreesList = ['150']
shift = 'jetUp'
dir = '/scratch/zmao/forPlots/%s/' %shift
# dir = '/scratch/zmao/BDT/%s/' %shift

postFix = '_tightopposite1M3rdLepVeto'
fileList = [dir+ ('signal%s.root' %postFix),
            dir+ ('Electroweak%s.root' %postFix),
            dir+ ('DYJetsToLL_all%s.root' %postFix),
            dir+ ('tt%s.root' %postFix)
            ]

for nTrees in nTreesList:
    postFix = '_7_n%s_mJJ_1M' %nTrees
    for iMass in massPoints:
        makeTestOnly('/scratch/zmao/TMVA/newMethod/TMVA%s%s.root' %(iMass,postFix), iMass, fileList, shift)
