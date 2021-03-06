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
             'chi2KinFit2','svMass', 'CSVJ2', 'dRTauTau', 'dRJJ',
             'triggerEff', 'PUWeight', 'xs', 'embeddedWeight', 'decayModeWeight']
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
    list = ['ZZ', 'WZ3L', 'WW', 'WZJetsTo2L2Q', 'zzTo2L2Nu', 'zzTo4L', 'DY_embed', 'tt_embed', 't', 'tbar', 'MCOSRelax',
            'DYJetsToLL', 'DY2JetsToLL', 'DY3JetsToLL', 'DY4JetsToLL', 'ZLL']
    if 'data' in sampleName and (sampleName != 'dataOSTight'):
        return True
    for i in list:
        if sampleName == i:
            return True
    return False

def makeWhole(iFileName, iLocation, weight1, weight2, sf1, sf2, sf0, additionalFiles = [], shift = 'normal'):
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

    savedSamples = []

    oFile = r.TFile('combined_%s_%s.root' %(iFileName, shift), 'recreate')
    oTree = r.TTree('eventTree', '')

    #setup branches
    for iVar in charVarsDict.keys():
        oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
    for iVar in floatVarsDict.keys():
        oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
    for iVar in intVarsDict.keys():
        oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/I" %iVar)



    #Store additional files
    ifiles = []
    trees = []
    for iName, iFile, save0tagOnly in additionalFiles:
        last = len(ifiles)
        ifiles.append(r.TFile(iFile))
        print iName
        trees.append(ifiles[last].Get('eventTree'))
        total = trees[last].GetEntries()
        for i in range(total):
            trees[last].GetEntry(i)
            tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %iFile)
            rightNBTags = trees[last].NBTags
            if 'embed' not in iName:
                if not makeWholeTools2.passJetTrigger(trees[last]):
                    continue
            if 'data' not in iName:
                if shift == 'bSysUp':
                    rightNBTags = trees[last].NBTagsSysUp
                if shift == 'bSysDown':
                    rightNBTags = trees[last].NBTagsSysDown
                if shift == 'bMisUp':
                    rightNBTags = trees[last].NBTagsMisUp
                if shift == 'bMisDown':
                    rightNBTags = trees[last].NBTagsMisDown
            if isWhichUseLooseForShape(iName):
                if trees[last].category2 == 1:
                    charVarsDict['Category'][:31] = '1M'
                elif trees[last].category2 == 2:
                    charVarsDict['Category'][:31] = '2M'
                else:
                    charVarsDict['Category'][:31] = '0M'
                floatVarsDict['PUWeight'][0] = 1.0
            else:
                if rightNBTags == 1:
                    charVarsDict['Category'][:31] = '1M'
                elif rightNBTags > 1:
                    charVarsDict['Category'][:31] = '2M'
                else:
                    charVarsDict['Category'][:31] = '0M'
            if save0tagOnly and rightNBTags != 0:
                continue
            elif save0tagOnly and rightNBTags == 0:
                charVarsDict['Category'][:31] = '0M'

            charVarsDict['sampleName'][:31] = iName
            if iName == 'useRealName':
                charVarsDict['sampleName'][:31] = tool.nameEnDecoder(int(trees[last].sampleName2), 'decode')
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
            floatVarsDict['dRTauTau'][0] = trees[last].dRTauTau
            floatVarsDict['dRJJ'][0] = trees[last].dRJJ
            intVarsDict['NBTags'][0] = int(trees[last].NBTags)
            floatVarsDict['embeddedWeight'][0] = trees[last].embeddedWeight
            floatVarsDict['decayModeWeight'][0] = trees[last].decayModeWeight

            intVarsDict['initEvents'][0] = int(trees[last].initEvents)
            if iName not in eventYieldDict[1].keys():
                eventYieldDict[0][iName] = 0.0
                eventYieldDict[1][iName] = 0.0
                eventYieldDict[2][iName] = 0.0

            if iName == 'ZLL' and trees[last].ZLL == 0:
                continue

            if 'data' in iName:
                eventYieldDict[int(trees[last].category2)][iName] += 1.0
            elif iName == 'DY_embed':
                if trees[last].HLT_Any == 0 or trees[last].ZTT == 0:
                    continue
                eventYieldDict[int(trees[last].category2)][iName] += floatVarsDict['triggerEff'][0]*floatVarsDict['embeddedWeight'][0]*floatVarsDict['decayModeWeight'][0]
            elif iName == 'tt_embed':
                if trees[last].HLT_Any == 0 or trees[last].ZTT == 0:
                    continue
                intVarsDict['initEvents'][0] = int(embedDYYieldCalculator.tt_semi_InitEvents)
                floatVarsDict['xs'][0] = floatVarsDict['xs'][0]*0.983
                eventYieldDict[int(trees[last].category2)][iName] += floatVarsDict['xs'][0]*floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['embeddedWeight'][0]*lumi/embedDYYieldCalculator.tt_semi_InitEvents
            else:
                if intVarsDict['NBTags'][0] > 2:
                    eventYieldDict[2][iName] += floatVarsDict['xs'][0]*floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*lumi/intVarsDict['initEvents'][0]
                else:
                    eventYieldDict[intVarsDict['NBTags'][0]][iName] += floatVarsDict['xs'][0]*floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*lumi/intVarsDict['initEvents'][0]

            if iName not in initEventsDict.keys():
                initEventsDict[iName] = trees[last].initEvents
                xsDict[iName] = trees[last].xs
            oTree.Fill()
            if (not save0tagOnly) and (rightNBTags == 0) and (charVarsDict['Category'][:31] != "0M"): #save twice for events that must used loose for shape
                charVarsDict['Category'][:31] = '0M'
                oTree.Fill()

            if (charVarsDict['sampleName'][:31] not in savedSamples) and (not save0tagOnly):
                savedSamples.append(charVarsDict['sampleName'][:31])
        print ''

    print ''

    totalTest = iTestTree.GetEntries()
    for i in range(totalTest):
        tool.printProcessStatus(iCurrent=i+1, total=totalTest, processName = 'Looping sample [%s]' %iFileName)
        iTestTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(int(iTestTree.sampleName2), 'decode')
        charVarsDict['sampleName'][:31] = tmpSampleName

        if ('DY' in tmpSampleName) and ('JetsToLL' in tmpSampleName):
            if iTestTree.ZLL == 0:
                continue
            charVarsDict['sampleName'][:31] = 'ZLL'

        rightNBTags = iTestTree.NBTags
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
            if rightNBTags == 1:
                charVarsDict['Category'][:31] = '1M'
            elif rightNBTags > 1:
                charVarsDict['Category'][:31] = '2M'
            else:
                charVarsDict['Category'][:31] = 'None'
            floatVarsDict['PUWeight'][0] = iTestTree.PUWeight

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
        floatVarsDict['dRTauTau'][0] = iTestTree.dRTauTau
        floatVarsDict['dRJJ'][0] = iTestTree.dRJJ
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

        if charVarsDict['sampleName'][:31] in savedSamples:
            continue
        oTree.Fill()


    printYields(eventYieldDict)
 
    L_to_T_1M = r.TH1F('L_to_T_1M', 'L_to_T_1M', 1, 0, 1)
    L_to_T_2M = r.TH1F('L_to_T_2M', 'L_to_T_2M', 1, 0, 1)
    L_to_T_SF_0M = r.TH1F('L_to_T_SF_0M', 'L_to_T_SF_0M', 1, 0, 1)
    L_to_T_SF_1M = r.TH1F('L_to_T_SF_1M', 'L_to_T_SF_1M', 1, 0, 1)
    L_to_T_SF_2M = r.TH1F('L_to_T_SF_2M', 'L_to_T_SF_2M', 1, 0, 1)
    MC2Embed2Cat_0M = r.TH1F('MC2Embed2Cat_0M', 'MC2Embed2Cat_0M', 1, 0, 1)
    MC2Embed2Cat_1M = r.TH1F('MC2Embed2Cat_1M', 'MC2Embed2Cat_1M', 1, 0, 1)
    MC2Embed2Cat_2M = r.TH1F('MC2Embed2Cat_2M', 'MC2Embed2Cat_2M', 1, 0, 1)
    VV_1M = r.TH1F('VV_1M', 'VV_1M', 1, 0, 1)
    VV_2M = r.TH1F('VV_2M', 'VV_2M', 1, 0, 1)
    singleT_1M = r.TH1F('singleT_1M', 'singleT_1M', 1, 0, 1)
    singleT_2M = r.TH1F('singleT_2M', 'singleT_2M', 1, 0, 1)
    ZLL_1M = r.TH1F('ZLL_1M', 'ZLL_1M', 1, 0, 1)
    ZLL_2M = r.TH1F('ZLL_2M', 'ZLL_2M', 1, 0, 1)

    xsHist = r.TH1F('xs', '', len(xsDict), 0, len(xsDict))
    initEventsHist = r.TH1F('initEvents', '', len(initEventsDict), 0, len(initEventsDict))
    nBtag = ''
    if 'bSys' in shift:
        shiftLocation = 'bSys'
        nBtag = shift
    elif 'bMis' in shift:
        shiftLocation = 'bMis'
        nBtag = shift
    else:
        shiftLocation = shift
    if shift == 'normal' or 'tau' in shift:
        shiftLocation2 = shift
    else:
        shiftLocation2 = 'normal'
    locationStem = '/nfs_scratch/zmao/samples_Iso'
    scaleFactor_1M, scaleFactor_2M, scaleFactor_1M2, scaleFactor_2M2, preScaleFactor = embedDYYieldCalculator.yieldCalculator(dy_mc = '%s/tauESOn/%s/dy_OSTight.root' %(locationStem, shiftLocation),
                                                                            tt_full_mc = '%s/tauESOff/%s/tt_all.root' %(locationStem, shiftLocation), 
                                                                            dy_embed = '%s/tauESOn/%s/DY_embed.root' %(locationStem, shiftLocation2), 
                                                                            tt_embed = '%s/tauESOff/%s/tt_embed_all.root' %(locationStem, shiftLocation), 
                                                                            massWindow = False,
                                                                            pairOption = 'iso',
                                                                            nBtag = nBtag)


    VV_SF_1M, VV_SF_2M = embedDYYieldCalculator.l2MYieldCalculator(sample = '%s/tauESOff/%s/Electroweak.root' %(locationStem, shiftLocation), 
                                                                   massWindow = False,
                                                                   nBtag = nBtag)
    singleT_SF_1M, singleT_SF_2M = embedDYYieldCalculator.l2MYieldCalculator(sample = '%s/tauESOff/%s/singleTop.root' %(locationStem, shiftLocation), 
                                                                             massWindow = False,
                                                                             nBtag = nBtag)
    ZLL_SF_1M, ZLL_SF_2M = embedDYYieldCalculator.l2MYieldCalculator(sample = '%s/tauESOn/%s/dy_OSTight.root' %(locationStem, shiftLocation), 
                                                                     massWindow = False,
                                                                     nBtag = nBtag,
                                                                     ZLL = True)


    L_to_T_1M.Fill(0.5, weight1*(eventCountInTestTree['dataOSRelax']+eventCountInTrainTree['dataOSRelax'])/eventCountInTestTree['dataOSRelax'])
    L_to_T_2M.Fill(0.5, weight2*(eventCountInTestTree['dataOSRelax']+eventCountInTrainTree['dataOSRelax'])/eventCountInTestTree['dataOSRelax'])
    L_to_T_SF_0M.Fill(0.5, sf0)
    L_to_T_SF_1M.Fill(0.5, sf1*(eventCountInTestTree['dataOSRelax']+eventCountInTrainTree['dataOSRelax'])/eventCountInTestTree['dataOSRelax'])
    L_to_T_SF_2M.Fill(0.5, sf2*(eventCountInTestTree['dataOSRelax']+eventCountInTrainTree['dataOSRelax'])/eventCountInTestTree['dataOSRelax'])
    VV_1M.Fill(0.5, VV_SF_1M)
    VV_2M.Fill(0.5, VV_SF_2M)
    singleT_1M.Fill(0.5, singleT_SF_1M)
    singleT_2M.Fill(0.5, singleT_SF_2M)
    ZLL_1M.Fill(0.5, ZLL_SF_1M)
    ZLL_2M.Fill(0.5, ZLL_SF_2M)
    MC2Embed2Cat_0M.Fill(0.5, preScaleFactor)
    MC2Embed2Cat_1M.Fill(0.5, scaleFactor_1M)
    MC2Embed2Cat_2M.Fill(0.5, scaleFactor_2M)
    for iSample in xsDict.keys():
        xsHist.Fill(iSample, xsDict[iSample])
        initEventsHist.Fill(iSample, initEventsDict[iSample])

    oFile.cd()
    L_to_T_1M.Write()
    L_to_T_2M.Write()
    L_to_T_SF_0M.Write()
    L_to_T_SF_1M.Write()
    L_to_T_SF_2M.Write()
    MC2Embed2Cat_0M.Write()
    MC2Embed2Cat_1M.Write()
    MC2Embed2Cat_2M.Write()
    VV_1M.Write()
    VV_2M.Write()
    singleT_1M.Write()
    singleT_2M.Write()
    ZLL_1M.Write()
    ZLL_2M.Write()
    xsHist.Write()
    initEventsHist.Write()

    oTree.SetName('eventTree')
    oTree.Write()
    oFile.Close()

    print 'sampleName\ttrain\ttest'
#     for iKey in eventCountInTrainTree.keys():
#         if len(iKey) < 7:
#             space = '\t\t'
#         else:
#             space = '\t' 
#         print '%s:%s%i\t%i' %(iKey, space, eventCountInTrainTree[iKey], eventCountInTestTree[iKey])
    
# weights = [1,1,1,1,1]
# massPoints = ['270', '280', '290', ]
massPoints = ['260', '270', '280', '290', '300', '310', '320', '330', '340', '350']
Shifts = ['tauUp', 'tauDown','jetUp', 'jetDown', 'bSysUp', 'bSysDown', 'bMisUp', 'bMisDown']
# Shifts = ['normal']
locationStem = '/nfs_scratch/zmao/samples_Iso/'
bdt_location = 'BDT_new'
for shift in Shifts:
    bTagShift = ''
    shiftDir = shift
    if 'Sys' in shift:
        bTagShift = shift
        shiftDir = 'bSys'
    if 'Mis' in shift:
        bTagShift = shift
        shiftDir = 'bMis'
    
    preFixTauESOffVV = '%s/tauESOff/%s/' %(locationStem, shiftDir)
    preFixTauESOff = '%s/tauESOff/%s/' %(locationStem, shiftDir)
    preFixTauESOn = '%s/tauESOn/%s/' %(locationStem, shiftDir)

    fileList = [('VV', '%s/Electroweak_withSingleTop.root' %preFixTauESOffVV),
                ('DYJetsToLL', '%s/dy_OSTight.root' %preFixTauESOn),
                ('t#bar{t}','%s/TT.root' %preFixTauESOff),
                ('data','%s/data/data.root' %locationStem)]

    weights = makeWholeTools2.calculateSF(fileList = fileList,
                                          sigRegionOption = 'Tight', 
                                          relaxedRegionOption = makeWholeSample_cfg.Relax, 
                                          verbose = True,
                                          isoTight = 1.0, 
                                          pairOption = makeWholeSample_cfg.pairOption,
                                          massWindow = False,
                                          usePassJetTrigger = True,
                                          nBtag = bTagShift)
    for iMass in massPoints:
        if 'bSys' in shift:
            locationPreFix = '%s/%s/bSys/' %(locationStem, bdt_location)
        elif 'bMis' in shift:
            locationPreFix = '%s/%s/bMis/' %(locationStem, bdt_location)
        else:
            locationPreFix = '%s/%s/%s/' %(locationStem, bdt_location, shift)

        additionalFiles = [('tt_embed', '%s/%s/ClassApp_both_tt_embed_all_OSTightnone.root' %(locationPreFix, iMass), False),
                           ('MCOSRelax', '%s/%s/ClassApp_both_MCOSRelaxnone.root' %(locationPreFix, iMass), False),
                           ('dataOSRelax', '%s/%s/normal/%s/ClassApp_both_data_OSRelaxnone.root' %(locationStem, bdt_location, iMass), True),
                           ('dataOSTight', '%s/%s/normal/%s/ClassApp_both_data_OSTightnone.root' %(locationStem, bdt_location, iMass), False),
                           ('useRealName', '%s/%s/ClassApp_both_WJets_OSTight_OSTightnone.root' %(locationPreFix, iMass), True)]

        if shift == 'normal':
            additionalFiles.append(('DY_embed', '%s/%s/ClassApp_both_DY_embed_OSTightnone.root' %(locationPreFix, iMass), False))
            additionalFiles.append(('useRealName', '%s/%s/ClassApp_both_H2hh%s_all_OSTightnone.root' %(locationPreFix, iMass, iMass), True))
            additionalFiles.append(('useRealName', '%s/%s/ClassApp_both_TT_OSTightnone.root' %(locationPreFix, iMass), True))
            additionalFiles.append(('useRealName', '%s/%s/ClassApp_both_Electroweak_OSTightnone.root' %(locationPreFix, iMass), True))
            additionalFiles.append(('useRealName', '%s/%s/ClassApp_both_singleTop_OSTightnone.root' %(locationPreFix, iMass), True))
            additionalFiles.append(('ZLL', '%s/%s/ClassApp_both_dy_OSTightnone.root' %(locationPreFix, iMass), True))

        else:
            additionalFiles.append(('useRealName', '%s/%s/ClassApp_both_H2hh%s_all_OSTightnone.root' %(locationPreFix, iMass, iMass), False))
            additionalFiles.append(('useRealName', '%s/%s/ClassApp_both_TT_OSTightnone.root' %(locationPreFix, iMass), False))
            additionalFiles.append(('useRealName', '%s/%s/ClassApp_both_Electroweak_OSTightnone.root' %(locationPreFix, iMass), False))
            additionalFiles.append(('useRealName', '%s/%s/ClassApp_both_singleTop_OSTightnone.root' %(locationPreFix, iMass), False))
            additionalFiles.append(('ZLL', '%s/%s/ClassApp_both_dy_OSTightnone.root' %(locationPreFix, iMass), False))

            if 'tau' in shift:
                additionalFiles.append(('DY_embed', '%s/%s/ClassApp_both_DY_embed_OSTightnone.root' %(locationPreFix, iMass), False))
            else:
                additionalFiles.append(('DY_embed', '%s/%s/normal/%s/ClassApp_both_DY_embed_OSTightnone.root' %(locationStem, bdt_location, iMass), False))

        makeWhole('H%s' %(iMass), '/nfs_scratch/zmao/TMVA/TMVA%s_7_n150_mJJ.root' %(iMass), weights[0], weights[1], weights[2],weights[3],weights[4], additionalFiles, shift)
