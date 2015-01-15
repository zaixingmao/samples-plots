#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array
import makeWholeSample_cfg
import makeWholeTools2
import embedDYYieldCalculator

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))


lumi = 19.7

def setUpFloatVarsDict():
    varDict = {}
    names = ['mJJ', 'CSVJ2', 'BDT', 'met', 'fMass',
             'iso1','iso2','fMassKinFit','chi2KinFit',
             'chi2KinFit2','svMass', 'CSVJ2',
             'triggerEff', 'PUWeight', 'xs']
    for iName in names:
        varDict[iName] = array('f', [0.])
    return varDict

def printYields(eventYieldDict):
    dicts = {'signal': 'H2hh260',
             'VV': ('ZZ', 'WZ3L', 'WW', 'WZJetsTo2L2Q', 'zzTo2L2Nu', 'zzTo4L'),
             'TT': ('tt', 'tt_semi', 'tthad'),
             't': ('t', 'tbar'),
             'DY': ('DY_embed', '-tt_embed'),
             'DY_emb': ('DY_embed',''),
             'tt_emb': ('tt_embed','')}

    for iKey in dicts.keys():
        yieldCount_1M = 0.0
        yieldCount_2M = 0.0
        for ikey in eventYieldDict[1].keys():
            if ikey in dicts[iKey]:
                yieldCount_1M += eventYieldDict[1][ikey]
                yieldCount_2M += eventYieldDict[2][ikey]
            elif '-%s' %ikey in dicts[iKey]:
                yieldCount_1M = yieldCount_1M - eventYieldDict[1][ikey]
                yieldCount_2M = yieldCount_2M - eventYieldDict[2][ikey]

        print '%s\t: %.3f (1M) \t %.3f (2M)' %(iKey, yieldCount_1M, yieldCount_2M)

def setUpIntVarsDict():
    varDict = {}
    names = ['NBTags', 'initEvents']
    for iName in names:
        varDict[iName] = array('i', [0])
    return varDict

def setUpCharVarsDict():
    varDict = {}
    names = ['sampleName', 'Category']
    for iName in names:
        varDict[iName] = bytearray(30)
    return varDict

def getEventsCountInTree(iTree):
    eventCountInTree = {}
    total = iTree.GetEntries()
    for i in range(total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample ')
        iTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(iTree.sampleName2, 'decode')            
        if tmpSampleName not in eventCountInTree.keys():
            eventCountInTree[tmpSampleName] = 0.0
        else:
            eventCountInTree[tmpSampleName] += 1.0
    print ''

    return eventCountInTree

def isWhichUseLooseForShape(sampleName):
    list = ['ZZ', 'WZ3L', 'WW', 'WZJetsTo2L2Q', 'zzTo2L2Nu', 'zzTo4L', 'DY_embed', 'tt_embed', 't', 'tbar', 'MCOSRelax']
    if 'data' in sampleName and (sampleName != 'dataOSTight'):
        return True
    for i in list:
        if sampleName == i:
            return True
    return False

def makeWhole(iFileName, iLocation, weight1, weight2, sf1, sf2, additionalFiles = []):
    #get event count in train/test tree
    ifile = r.TFile(iLocation)
    iTrainTree = ifile.Get('TrainTree')
    iTestTree = ifile.Get('TestTree')
    eventCountInTrainTree = getEventsCountInTree(iTrainTree)
    eventCountInTestTree = getEventsCountInTree(iTestTree)

    charVarsDict = setUpCharVarsDict()
    floatVarsDict = setUpFloatVarsDict()
    intVarsDict = setUpIntVarsDict()

    eventYieldDict = []
    eventYieldDict.append({})
    eventYieldDict.append({})
    eventYieldDict.append({})

    initEventsDict = {}
    xsDict = {}

    oFile = r.TFile('combined_%s.root' %iFileName, 'recreate')
    oTree = r.TTree('eventTree', '')

    #setup branches
    for iVar in charVarsDict.keys():
        oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
    for iVar in floatVarsDict.keys():
        oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
    for iVar in intVarsDict.keys():
        oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/I" %iVar)

    totalTest = iTestTree.GetEntries()
    for i in range(totalTest):
        tool.printProcessStatus(iCurrent=i+1, total=totalTest, processName = 'Looping sample [%s]' %iFileName)
        iTestTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(int(iTestTree.sampleName2), 'decode')

        if ('DY' in tmpSampleName) and ('JetsToLL' in tmpSampleName):
            if iTestTree.ZLL == 0:
                continue
            tmpSampleName == 'ZLL'

        #Save values         
        if isWhichUseLooseForShape(tmpSampleName):
            if iTestTree.category2 == 1:
                charVarsDict['Category'][:31] = '1M'
            elif iTestTree.category2 == 2:
                charVarsDict['Category'][:31] = '2M'
            else:
                charVarsDict['Category'][:31] = 'None'
            floatVarsDict['PUWeight'][0] = 1.0

        else:
            if iTestTree.NBTags == 1:
                charVarsDict['Category'][:31] = '1M'
            elif iTestTree.NBTags > 1:
                charVarsDict['Category'][:31] = '2M'
            else:
                charVarsDict['Category'][:31] = 'None'
            floatVarsDict['PUWeight'][0] = iTestTree.PUWeight

        charVarsDict['sampleName'][:31] = tmpSampleName

        floatVarsDict['BDT'][0] = iTestTree.BDT
        floatVarsDict['mJJ'][0] = iTestTree.mJJ
        floatVarsDict['CSVJ2'][0] = iTestTree.CSVJ2
        floatVarsDict['fMass'][0] = iTestTree.fMass
        floatVarsDict['fMassKinFit'][0] = iTestTree.fMassKinFit
        floatVarsDict['chi2KinFit'][0] = iTestTree.chi2KinFit
        floatVarsDict['chi2KinFit2'][0] = iTestTree.chi2KinFit2
        floatVarsDict['met'][0] = iTestTree.met1
        floatVarsDict['iso1'][0] = iTestTree.iso1_1
        floatVarsDict['iso2'][0] = iTestTree.iso2_1
        floatVarsDict['svMass'][0] = iTestTree.svMass1
        floatVarsDict['triggerEff'][0] = iTestTree.triggerEff
        floatVarsDict['xs'][0] = iTestTree.xs
        intVarsDict['NBTags'][0] = int(iTestTree.NBTags)
        intVarsDict['initEvents'][0] = int((iTestTree.initEvents+0.0)*eventCountInTestTree[tmpSampleName]/(eventCountInTestTree[tmpSampleName]+eventCountInTrainTree[tmpSampleName]))

        if tmpSampleName not in eventYieldDict[1].keys():
            eventYieldDict[0][tmpSampleName] = 0.0
            eventYieldDict[1][tmpSampleName] = 0.0
            eventYieldDict[2][tmpSampleName] = 0.0

        if 'data' in tmpSampleName:
            eventYieldDict[int(iTestTree.category2)][tmpSampleName] += 1.0
        else:
            if intVarsDict['NBTags'][0] > 2:
                eventYieldDict[2][tmpSampleName] += floatVarsDict['xs'][0]*floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*lumi/intVarsDict['initEvents'][0]
            else:
                eventYieldDict[intVarsDict['NBTags'][0]][tmpSampleName] += floatVarsDict['xs'][0]*floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*lumi/intVarsDict['initEvents'][0]

        if tmpSampleName not in initEventsDict.keys():
            initEventsDict[tmpSampleName] = int((iTestTree.initEvents+0.0)*eventCountInTestTree[tmpSampleName]/(eventCountInTestTree[tmpSampleName]+eventCountInTrainTree[tmpSampleName]))
            xsDict[tmpSampleName] = iTestTree.xs

        oTree.Fill()

    #Store additional files
    ifiles = []
    trees = []
    for iName, iFile in additionalFiles:
        last = len(ifiles)
        ifiles.append(r.TFile(iFile))
        trees.append(ifiles[last].Get('eventTree'))
        total = trees[last].GetEntries()
        for i in range(total):
            trees[last].GetEntry(i)
            tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %iFile)
            if isWhichUseLooseForShape(iName):
                if trees[last].category2 == 1:
                    charVarsDict['Category'][:31] = '1M'
                elif trees[last].category2 == 2:
                    charVarsDict['Category'][:31] = '2M'
                else:
                    charVarsDict['Category'][:31] = 'None'
                floatVarsDict['PUWeight'][0] = 1.0
            else:
                if trees[last].NBTags == 1:
                    charVarsDict['Category'][:31] = '1M'
                elif trees[last].NBTags > 1:
                    charVarsDict['Category'][:31] = '2M'
                else:
                    charVarsDict['Category'][:31] = 'None'
            charVarsDict['sampleName'][:31] = iName
            floatVarsDict['BDT'][0] = trees[last].BDT
            floatVarsDict['PUWeight'][0] = trees[last].PUWeight
            floatVarsDict['mJJ'][0] = trees[last].mJJ
            floatVarsDict['CSVJ2'][0] = trees[last].CSVJ2
            floatVarsDict['fMass'][0] = trees[last].fMass
            floatVarsDict['fMassKinFit'][0] = trees[last].fMassKinFit
            floatVarsDict['chi2KinFit'][0] = trees[last].chi2KinFit
            floatVarsDict['chi2KinFit2'][0] = trees[last].chi2KinFit2
            floatVarsDict['met'][0] = trees[last].met1
            floatVarsDict['iso1'][0] = trees[last].iso1_1
            floatVarsDict['iso2'][0] = trees[last].iso2_1
            floatVarsDict['svMass'][0] = trees[last].svMass1
            floatVarsDict['triggerEff'][0] = trees[last].triggerEff
            floatVarsDict['xs'][0] = trees[last].xs
            intVarsDict['NBTags'][0] = int(trees[last].NBTags)
            intVarsDict['initEvents'][0] = int(trees[last].initEvents)
            if iName not in eventYieldDict[1].keys():
                eventYieldDict[0][iName] = 0.0
                eventYieldDict[1][iName] = 0.0
                eventYieldDict[2][iName] = 0.0

            if 'data' in iName:
                eventYieldDict[int(trees[last].category2)][iName] += 1.0
            elif iName == 'DY_embed':
                if trees[last].HLT_Any == 0 or trees[last].ZTT == 0:
                    continue
                eventYieldDict[int(trees[last].category2)][iName] += floatVarsDict['triggerEff'][0]
            elif iName == 'tt_embed':
                if trees[last].HLT_Any == 0 or trees[last].ZTT == 0:
                    continue
                floatVarsDict['xs'][0] = floatVarsDict['xs'][0]*0.983
                eventYieldDict[int(trees[last].category2)][iName] += floatVarsDict['xs'][0]*floatVarsDict['triggerEff'][0]*lumi/embedDYYieldCalculator.tt_semi_InitEvents
            else:
                if intVarsDict['NBTags'][0] > 2:
                    eventYieldDict[2][iName] += floatVarsDict['xs'][0]*floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*lumi/intVarsDict['initEvents'][0]
                else:
                    eventYieldDict[intVarsDict['NBTags'][0]][iName] += floatVarsDict['xs'][0]*floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*lumi/intVarsDict['initEvents'][0]

            if iName not in initEventsDict.keys():
                initEventsDict[iName] = trees[last].initEvents
                xsDict[iName] = trees[last].xs
            oTree.Fill()

        print ''

    print ''

    printYields(eventYieldDict)
 
    L_to_T_1M = r.TH1F('L_to_T_1M', 'L_to_T_1M', 1, 0, 1)
    L_to_T_2M = r.TH1F('L_to_T_2M', 'L_to_T_2M', 1, 0, 1)
    L_to_T_SF_1M = r.TH1F('L_to_T_SF_1M', 'L_to_T_SF_1M', 1, 0, 1)
    L_to_T_SF_2M = r.TH1F('L_to_T_SF_2M', 'L_to_T_SF_2M', 1, 0, 1)
    MC2Embed2Cat_1M = r.TH1F('MC2Embed2Cat_1M', 'MC2Embed2Cat_1M', 1, 0, 1)
    MC2Embed2Cat_2M = r.TH1F('MC2Embed2Cat_2M', 'MC2Embed2Cat_2M', 1, 0, 1)
    VV_1M = r.TH1F('VV_1M', 'VV_1M', 1, 0, 1)
    VV_2M = r.TH1F('VV_2M', 'VV_2M', 1, 0, 1)
    singleT_1M = r.TH1F('singleT_1M', 'singleT_1M', 1, 0, 1)
    singleT_2M = r.TH1F('singleT_2M', 'singleT_2M', 1, 0, 1)
    xsHist = r.TH1F('xs', '', len(xsDict), 0, len(xsDict))
    initEventsHist = r.TH1F('initEvents', '', len(initEventsDict), 0, len(initEventsDict))

    scaleFactor_1M, scaleFactor_2M, scaleFactor_1M2, scaleFactor_2M2 = embedDYYieldCalculator.yieldCalculator(dy_mc = '/nfs_scratch/zmao/samples/tauESOn/normal/dy.root', 
                                                                            tt_full_mc = '/nfs_scratch/zmao/samples/tauESOff/normal/tt_all.root', 
                                                                            dy_embed = '/nfs_scratch/zmao/samples/tauESOn/normal/DY_embed.root', 
                                                                            tt_embed = '/nfs_scratch/zmao/samples/tauESOff/normal/tt_embed_all.root', 
                                                                            massWindow = False,
                                                                            pairOption = 'pt')


    VV_SF_1M, VV_SF_2M = embedDYYieldCalculator.l2MYieldCalculator(sample = '/nfs_scratch/zmao/samples/tauESOff/normal/Electroweak.root', 
                                                                massWindow = False)
    singleT_SF_1M, singleT_SF_2M = embedDYYieldCalculator.l2MYieldCalculator(sample = '/nfs_scratch/zmao/samples/tauESOff/normal/singleTop.root', 
                                                                             massWindow = False)

    L_to_T_1M.Fill(0.5, weight1*(eventCountInTestTree['dataOSRelax']+eventCountInTrainTree['dataOSRelax'])/eventCountInTestTree['dataOSRelax'])
    L_to_T_2M.Fill(0.5, weight2*(eventCountInTestTree['dataOSRelax']+eventCountInTrainTree['dataOSRelax'])/eventCountInTestTree['dataOSRelax'])
    L_to_T_SF_1M.Fill(0.5, sf1)
    L_to_T_SF_2M.Fill(0.5, sf2)
    VV_1M.Fill(0.5, VV_SF_1M)
    VV_2M.Fill(0.5, VV_SF_2M)
    singleT_1M.Fill(0.5, singleT_SF_1M)
    singleT_2M.Fill(0.5, singleT_SF_2M)
    MC2Embed2Cat_1M.Fill(0.5, scaleFactor_1M)
    MC2Embed2Cat_2M.Fill(0.5, scaleFactor_2M)
    for iSample in xsDict.keys():
        xsHist.Fill(iSample, xsDict[iSample])
        initEventsHist.Fill(iSample, initEventsDict[iSample])

    oFile.cd()
    L_to_T_1M.Write()
    L_to_T_2M.Write()
    L_to_T_SF_1M.Write()
    L_to_T_SF_2M.Write()
    MC2Embed2Cat_1M.Write()
    MC2Embed2Cat_2M.Write()
    VV_1M.Write()
    VV_2M.Write()
    singleT_1M.Write()
    singleT_2M.Write()
    xsHist.Write()
    initEventsHist.Write()

    oTree.SetName('eventTree')
    oTree.Write()
    oFile.Close()

    print 'sampleName\ttrain\ttest'
    for iKey in eventCountInTrainTree.keys():
        if len(iKey) < 7:
            space = '\t\t'
        else:
            space = '\t' 
        print '%s:%s%i\t%i' %(iKey, space, eventCountInTrainTree[iKey], eventCountInTestTree[iKey])
    
weights = makeWholeTools2.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'SF12', 'Tight', 'one1To4', True, 1.0, 'pt', False)

massPoints = ['260']#, '270', '280', '290', '300', '310', '320', '330', '340']

for iMass in massPoints:
    additionalFiles = [('tt_embed', '/nfs_scratch/zmao/samples/BDT_1.0/%s/ClassApp_both_tt_embed_all_OSTightL.root' %iMass),
                       ('DY_embed', '/nfs_scratch/zmao/samples/BDT_1.0/%s/ClassApp_both_DY_embed_OSTightL.root' %iMass),
                       ('MCOSRelax', '/nfs_scratch/zmao/samples/BDT_1.0/%s/ClassApp_both_MCOSRelax_L.root' %iMass),
                       ('dataOSTight', '/nfs_scratch/zmao/samples/BDT_1.0/%s/ClassApp_both_data_OSTightM.root' %iMass)]

    makeWhole('H%s' %(iMass), '/nfs_scratch/zmao/TMVA/TMVA%s_7_n150_mJJ.root' %(iMass), weights[0], weights[1], weights[2],weights[3], additionalFiles)
