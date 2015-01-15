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
import cutSampleTools 

dR_tauEleMu_max = 0.5
dR_b_max = 0.5
lumi = 19.7
tt_semi_InitEvents = 12011428.


def findRightPair(tree, option):
    if option == 'iso':
        isoMin = 999.9
        bestPair = 0
        for iPair in range(len(tree.pt1)):
            if (tree.iso1.at(iPair) + tree.iso2.at(iPair)) < isoMin:
                isoMin = tree.iso1.at(iPair) + tree.iso2.at(iPair)
                bestPair = iPair
        return iPair
    else:
        return 0


def passMassWindow(svMass, mJJ, fMassKinFit):
    if 90.0 < svMass < 150.0:
        if 70.0 < mJJ < 150.0:
            if fMassKinFit > 10.0:
                return 1
    return 0

def passCut(option, signSelection, isoSelection, looseTag, mediumTag):
    if 'L' in option and looseTag != '0L':
        check = signSelection+isoSelection+'L'
        if option == check:
            return True, looseTag[0:1]+'M'
        else:
            return False, looseTag[0:1]+'M'
    if 'M' in option and mediumTag != '0M':
        check = signSelection+isoSelection+'M'
        if option == check:
            return True, mediumTag
        else:
            return False, mediumTag
    return False, mediumTag


def getRightBTagCatName(bTagSelection):
    if bTagSelection == None:
        return '0L', '0M'
    return bTagSelection[0:2], bTagSelection[2:4]


def yieldCalculator(dy_mc, tt_full_mc, dy_embed, tt_embed, massWindow, pairOption = 'pt'):

    yieldForMediumCat = {}
    eventCounterForMediumCat = {}
    yieldForLooseCat = {}
    eventCounterForLooseCat = {}
    inclusiveYields = {}

    fileList = [('DY_inclusive', dy_mc), ('tt_inclusive', tt_full_mc), ('DY_embed', dy_embed), ('tt_embed', tt_embed)]

    for indexFile in range(len(fileList)):
        name = fileList[indexFile][0]
        iFile =  r.TFile(fileList[indexFile][1])
        iTree = iFile.Get('eventTree')
        yieldForMediumCat[name+'_1M'] = 0.0
        yieldForMediumCat[name+'_2M'] = 0.0
        yieldForLooseCat[name+'_1L'] = 0.0
        yieldForLooseCat[name+'_2L'] = 0.0
        eventCounterForMediumCat[name+'_1M'] = 0
        eventCounterForMediumCat[name+'_2M'] = 0
        eventCounterForLooseCat[name+'_1L'] = 0
        eventCounterForLooseCat[name+'_2L'] = 0
        total = iTree.GetEntries()
        inclusiveYields[name] = 0.0
        counter = 0
        counter_0 = 0
        isEmbed = False
        isData == False
        if 'emb' in name:
            isEmbed = True
        if name == 'DY_embed':
            isData = True

        for i in range(0, total):
            tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %name)
            #Fill Histograms
            iTree.GetEntry(i)

            #get the right pair of taus based on isoMin or ptMax
            rightPair = findRightPair(iTree, pairOption)

            if (iTree.nElectrons > 0 or iTree.nMuons > 0):
                continue

            #get event category
            signSelection, isoSelection, bTagSelection = makeWholeTools2.findCategory(tree = iTree, 
                                                                                      iso = makeWholeSample_cfg.iso, 
                                                                                      option = pairOption,
                                                                                      isData = isData,
                                                                                      relaxedRegionOption = makeWholeSample_cfg.Relax,
                                                                                      isEmbed = isEmbed,
                                                                                      usePassJetTrigger = makeWholeSample_cfg.usePassJetTrigger,
                                                                                      nBtag = makeWholeSample_cfg.bTagShift)
            if signSelection == None or isoSelection == None:
                continue
            looseTag, mediumTag = getRightBTagCatName(bTagSelection)

            if iTree.HLT_Any == 0:
                continue
            #calculate inclusiveYield
            if (signSelection == "OS") and (isoSelection == "Tight"):
                if 'data' in iTree.sampleName:
                    inclusiveYields[name] += iTree.triggerEff
                elif isEmbed:
                    inclusiveYields[name] += iTree.triggerEff*iTree.xs*0.983*lumi/tt_semi_InitEvents
                else:
                    if not makeWholeTools2.passJetTrigger(iTree):
                        continue
                    inclusiveYields[name] += iTree.triggerEff*iTree.xs*lumi/(iTree.initEvents+0.0)
            else:
                continue

            if isEmbed:
                if iTree.ZTT == 0:
                    continue
            if  massWindow and not passMassWindow(iTree.svMass.at(0),iTree.mJJ, iTree.fMassKinFit):
                continue
                
            #calculate category yield
            if mediumTag != '0M':
                if isEmbed:
                    if 'data' in iTree.sampleName:
                        yieldForMediumCat["%s_%s" %(name, mediumTag)] += iTree.triggerEff
                    else:
                        yieldForMediumCat["%s_%s" %(name, mediumTag)] += iTree.triggerEff*iTree.xs*0.983*lumi/tt_semi_InitEvents
                else:
                    yieldForMediumCat["%s_%s" %(name, mediumTag)] += iTree.triggerEff*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents
                eventCounterForMediumCat["%s_%s" %(name, mediumTag)] += 1


            #calculate loose cat yield for embed samples
            if isEmbed and (looseTag != '0L'):
                if 'data' in iTree.sampleName:
                    yieldForLooseCat["%s_%s" %(name, looseTag)] += iTree.triggerEff
                else:
                    yieldForLooseCat["%s_%s" %(name, looseTag)] += iTree.triggerEff*iTree.xs*0.983*lumi/tt_semi_InitEvents
                eventCounterForLooseCat["%s_%s" %(name, looseTag)] += 1

        print ''
        if isEmbed:
            print name
            print 'inclusive yield for %s: %.2f' %(name, inclusiveYields[name])
            print '1-Medium %s yield: %.2f \t events: %i' %(name, yieldForMediumCat[name+'_1M'], eventCounterForMediumCat[name+'_1M'])
            print '1-Loose %s yield: %.2f \t events: %i' %(name, yieldForLooseCat[name+'_1L'], eventCounterForLooseCat[name+'_1L'])
            print '2-Medium %s yield: %.2f \t events: %i' %(name, yieldForMediumCat[name+'_2M'], eventCounterForMediumCat[name+'_2M'])
            print '2-Loose %s yield: %.2f \t events: %i' %(name, yieldForLooseCat[name+'_2L'], eventCounterForLooseCat[name+'_2L'])

        else:
            print 'inclusive yield for %s: %.2f' %(name, inclusiveYields[name])


    preScaleFactor = inclusiveYields['DY_inclusive']/(inclusiveYields['DY_embed'] - inclusiveYields['tt_embed'])
    scaleFactor_1M = preScaleFactor*(yieldForMediumCat['DY_embed_1M']-yieldForMediumCat['tt_embed_1M'])
    scaleFactor_2M = preScaleFactor*(yieldForMediumCat['DY_embed_2M']-yieldForMediumCat['tt_embed_2M'])

    preScaleFactor2 = (inclusiveYields['DY_inclusive']+inclusiveYields['tt_inclusive'])/(inclusiveYields['DY_embed'])
    scaleFactor_1M2 = preScaleFactor2*(yieldForMediumCat['DY_embed_1M'])
    scaleFactor_2M2 = preScaleFactor2*(yieldForMediumCat['DY_embed_2M'])

    print 'predicted DY in 1M: %.2f' %scaleFactor_1M
    print 'predicted DY in 2M: %.2f' %scaleFactor_2M
    print 'predicted DY+tt in 1M: %.2f' %scaleFactor_1M2
    print 'predicted DY+tt in 2M: %.2f' %scaleFactor_2M2

    return scaleFactor_1M, scaleFactor_2M, scaleFactor_1M2, scaleFactor_2M2, preScaleFactor

def l2MYieldCalculator(sample, massWindow, pairOption = 'pt'):

    yieldForMediumCat = {}
    yieldForLooseCat = {}

    iFile =  r.TFile(sample)
    iTree = iFile.Get('eventTree')
    yieldForMediumCat['1M'] = 0.0
    yieldForMediumCat['2M'] = 0.0
    yieldForLooseCat['1L'] = 0.0
    yieldForLooseCat['2L'] = 0.0

    total = iTree.GetEntries()

    for i in range(0, total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %sample)
        iTree.GetEntry(i)
            
        #get the right pair of taus based on isoMin or ptMax
        rightPair = findRightPair(iTree, pairOption)

        if (iTree.nElectrons > 0 or iTree.nMuons > 0):
            continue
        if not makeWholeTools2.passJetTrigger(iTree):
            continue
        #get event category
        signSelection, isoSelection, bTagSelection = makeWholeTools2.findCategory(tree = iTree, 
                                                                                  iso = makeWholeSample_cfg.iso, 
                                                                                  option = pairOption,
                                                                                  isData = False,
                                                                                  relaxedRegionOption = makeWholeSample_cfg.Relax,
                                                                                  isEmbed = False,
                                                                                  usePassJetTrigger = makeWholeSample_cfg.usePassJetTrigger,
                                                                                  nBtag = makeWholeSample_cfg.bTagShift)

        if signSelection == None or isoSelection == None:
            continue
        looseTag, mediumTag = getRightBTagCatName(bTagSelection)

        if  massWindow and not passMassWindow(iTree.svMass.at(0),iTree.mJJ, iTree.fMassKinFit):
            continue
        #calculate category yield
        if (signSelection == "OS") and (isoSelection == "Tight") and (mediumTag != '0M'):
            yieldForMediumCat[mediumTag] += iTree.triggerEff*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents


        #calculate loose cat yield for embed samples
        if (signSelection == "OS") and (isoSelection == "Tight") and (looseTag != '0L'):
            yieldForLooseCat[looseTag] += iTree.triggerEff*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents

    print ''


    scaleFactor_1M = yieldForMediumCat['1M']/yieldForLooseCat['1L']
    scaleFactor_2M = yieldForMediumCat['2M']/yieldForLooseCat['2L']

    print '[%s]: %.2f (1L) \t  %.2f (2L)' %(sample, yieldForLooseCat['1L'], yieldForLooseCat['2L'])
    print '[%s]: %.2f (1M) \t  %.2f (2M)' %(sample, yieldForMediumCat['1M'], yieldForMediumCat['2M'])

    return yieldForMediumCat['1M'], yieldForMediumCat['2M']

# l2MYieldCalculator('/nfs_scratch/zmao/samples/BDT_1.0/Electroweak_withSingleTop_OSTightL.root', True, 'iso')

# yieldCalculator(dy_mc = '/nfs_scratch/zmao/samples/tauESOn/normal/dy.root', 
#                 tt_full_mc = '/nfs_scratch/zmao/samples/tauESOff/normal/tt_all.root', 
#                 dy_embed = '/nfs_scratch/zmao/samples/tauESOn/normal//DY_embed.root', 
#                 tt_embed = '/nfs_scratch/zmao/samples/tauESOff/normal/tt_embed_all.root', 
#                 massWindow = True,
#                 pairOption = 'pt'
#                 )


