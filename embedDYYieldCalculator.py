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
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

dR_tauEleMu_max = 0.5
dR_b_max = 0.5
lumi = 19.7
tt_semi_InitEvents = 12011428.

def calcSysUncSingle(sampleYield, sampleCount):
    delta = math.sqrt(sampleCount+0.0)
    return sampleYield*delta/(sampleCount+0.0)

def calcSysUnc(sf, numA, numB, denomA, denomB, delta_numA, delta_numB, delta_denomA, delta_denomB):
    return sf*math.sqrt(((delta_numA)**2 + (delta_numB)**2)/((numA-numB)**2) + ((delta_denomA)**2 + (delta_denomB)**2)/((denomA-denomB)**2))


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


def yieldCalculator(dy_mc, tt_full_mc, dy_embed, tt_embed, massWindow, pairOption = 'iso', nBtag = '', doDraw = False):

    yieldForMediumCat = {}
    eventCounterForMediumCat = {}
    yieldForLooseCat = {}
    eventCounterForLooseCat = {}
    inclusiveYields = {}
    eventCounterForInclusive = {}

    bins = [19, 225, 700]
    dy_embed_1M = r.TH1F('dy_embed_1M', '', bins[0], bins[1], bins[2])
    dy_embed_2M = r.TH1F('dy_embed_2M', '', bins[0], bins[1], bins[2])
    tt_embed_1M = r.TH1F('tt_embed_1M', '', bins[0], bins[1], bins[2])
    tt_embed_2M = r.TH1F('tt_embed_2M', '', bins[0], bins[1], bins[2])

    fileList = [('DY_inclusive', dy_mc), ('tt_inclusive', tt_full_mc), ('DY_embed', dy_embed), ('tt_embed', tt_embed)]

    for indexFile in range(len(fileList)):
        name = fileList[indexFile][0]
        iFile =  r.TFile(fileList[indexFile][1])
        iTree = iFile.Get('eventTree')
        yieldForMediumCat[name+'_1M'] = 0.0
        yieldForMediumCat[name+'_2M'] = 0.0
        yieldForLooseCat[name+'_1L'] = 0.0
        yieldForLooseCat[name+'_2L'] = 0.0
        eventCounterForInclusive[name] = 0
        eventCounterForMediumCat[name+'_1M'] = 0
        eventCounterForMediumCat[name+'_2M'] = 0
        eventCounterForLooseCat[name+'_1L'] = 0
        eventCounterForLooseCat[name+'_2L'] = 0
        total = iTree.GetEntries()
        inclusiveYields[name] = 0.0
        counter = 0
        counter_0 = 0
        isEmbed = False
        isData = False
        if 'emb' in name:
            isEmbed = True
        if name == 'DY_embed':
            isData = True

        for i in range(0, total):
            tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %name, iPrevious=i)
            #Fill Histograms
            iTree.GetEntry(i)

            #get the right pair of taus based on isoMin or ptMax
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
                                                                                      nBtag = nBtag)
            if signSelection == None or isoSelection == None or bTagSelection == None:
                continue
            looseTag, mediumTag = getRightBTagCatName(bTagSelection)

            if iTree.HLT_Any == 0:
                continue
            if iTree.ZTT == 0:
                continue
            if 'tt' not in name:
                tmpEventYield = iTree.triggerEff*iTree.decayModeWeight
            else:
                tmpEventYield = iTree.triggerEff

            if  massWindow and not makeWholeTools2.passCut(iTree, pairOption):
                continue

            #calculate inclusiveYield
            if (signSelection == "OS") and (isoSelection == "Tight"):
                eventCounterForInclusive[name] += 1
                if 'data' in iTree.sampleName:
                    inclusiveYields[name] += tmpEventYield*iTree.embeddedWeight
                elif isEmbed:
                    inclusiveYields[name] += iTree.triggerEff*iTree.xs*0.983*(lumi/tt_semi_InitEvents)*iTree.embeddedWeight*iTree.PUWeight
                else:
                    if not makeWholeTools2.passJetTrigger(iTree):
                        continue
                    inclusiveYields[name] += tmpEventYield*iTree.xs*lumi*iTree.PUWeight/(iTree.initEvents+0.0)
            else:
                continue
                
            fillValue = iTree.fMassKinFit

            #calculate category yield
            if mediumTag != '0M':
                if isEmbed:
                    if 'data' in iTree.sampleName:
                        yieldForMediumCat["%s_%s" %(name, mediumTag)] += tmpEventYield*iTree.embeddedWeight
                        if mediumTag == '1M':
                            dy_embed_1M.Fill(fillValue, tmpEventYield*iTree.embeddedWeight)
                        else:
                            dy_embed_2M.Fill(fillValue, tmpEventYield*iTree.embeddedWeight)
                    else:
                        yieldForMediumCat["%s_%s" %(name, mediumTag)] += tmpEventYield*iTree.xs*0.983*(lumi/tt_semi_InitEvents)*iTree.embeddedWeight*iTree.PUWeight
                        if mediumTag == '1M':
                            tt_embed_1M.Fill(fillValue, tmpEventYield*iTree.xs*0.983*(lumi/tt_semi_InitEvents)*iTree.embeddedWeight*iTree.PUWeight)
                        else:
                            tt_embed_2M.Fill(fillValue, tmpEventYield*iTree.xs*0.983*(lumi/tt_semi_InitEvents)*iTree.embeddedWeight*iTree.PUWeight)

                else:
                    yieldForMediumCat["%s_%s" %(name, mediumTag)] += tmpEventYield*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents
                eventCounterForMediumCat["%s_%s" %(name, mediumTag)] += 1


            #calculate loose cat yield for embed samples
            if isEmbed and (looseTag != '0L'):
                if 'data' in iTree.sampleName:
                    yieldForLooseCat["%s_%s" %(name, looseTag)] += tmpEventYield*iTree.embeddedWeight
                else:
                    yieldForLooseCat["%s_%s" %(name, looseTag)] += tmpEventYield*iTree.embeddedWeight*iTree.xs*0.983*lumi/tt_semi_InitEvents
                eventCounterForLooseCat["%s_%s" %(name, looseTag)] += 1

        print ''

        if isEmbed:
            print name
            print 'inclusive yield for %s: %.2f +/- %.2f' %(name, inclusiveYields[name], calcSysUncSingle(inclusiveYields[name], eventCounterForInclusive[name]))
            print '1-Medium %s yield: %.2f +/- %.2f \t events: %i' %(name, yieldForMediumCat[name+'_1M'], calcSysUncSingle(yieldForMediumCat[name+'_1M'], eventCounterForMediumCat[name+'_1M']), eventCounterForMediumCat[name+'_1M'])
            print '1-Loose %s yield: %.2f  +/- %.2f \t events: %i' %(name, yieldForLooseCat[name+'_1L'], calcSysUncSingle(yieldForLooseCat[name+'_1L'], eventCounterForLooseCat[name+'_1L']), eventCounterForLooseCat[name+'_1L'])
            print '2-Medium %s yield: %.2f +/- %.2f \t events: %i' %(name, yieldForMediumCat[name+'_2M'], calcSysUncSingle(yieldForMediumCat[name+'_2M'], eventCounterForMediumCat[name+'_2M']), eventCounterForMediumCat[name+'_2M'])
            print '2-Loose %s yield: %.2f +/- %.2f \t events: %i' %(name, yieldForLooseCat[name+'_2L'], calcSysUncSingle(yieldForLooseCat[name+'_2L'], eventCounterForLooseCat[name+'_2L']), eventCounterForLooseCat[name+'_2L'])

        else:
            print 'inclusive yield for %s: %.2f' %(name, inclusiveYields[name])

    delta_dy_inclusive = calcSysUncSingle(inclusiveYields['DY_embed'], eventCounterForInclusive['DY_embed'])
    delta_tt_inclusive = calcSysUncSingle(inclusiveYields['tt_embed'], eventCounterForInclusive['tt_embed'])
    delta_dy_1M = calcSysUncSingle(yieldForMediumCat['DY_embed_1M'], eventCounterForMediumCat['DY_embed_1M'])
    delta_tt_1M = calcSysUncSingle(yieldForMediumCat['tt_embed_1M'], eventCounterForMediumCat['tt_embed_1M'])
    delta_dy_2M = calcSysUncSingle(yieldForMediumCat['DY_embed_2M'], eventCounterForMediumCat['DY_embed_2M'])
    delta_tt_2M = calcSysUncSingle(yieldForMediumCat['tt_embed_2M'], eventCounterForMediumCat['tt_embed_2M'])

    sysUnc_1M = calcSysUnc(sf = (yieldForMediumCat['DY_embed_1M']-yieldForMediumCat['tt_embed_1M'])/(inclusiveYields['DY_embed'] - inclusiveYields['tt_embed']), 
                        numA = yieldForMediumCat['DY_embed_1M'], 
                        numB = yieldForMediumCat['tt_embed_1M'],
                        denomA = inclusiveYields['DY_embed'],
                        denomB = inclusiveYields['tt_embed'],
                        delta_numA = delta_dy_1M,
                        delta_numB = delta_tt_1M,
                        delta_denomA = delta_dy_inclusive,
                        delta_denomB = delta_tt_inclusive)

    sysUnc_2M = calcSysUnc(sf = (yieldForMediumCat['DY_embed_2M']-yieldForMediumCat['tt_embed_2M'])/(inclusiveYields['DY_embed'] - inclusiveYields['tt_embed']), 
                        numA = yieldForMediumCat['DY_embed_2M'], 
                        numB = yieldForMediumCat['tt_embed_2M'],
                        denomA = inclusiveYields['DY_embed'],
                        denomB = inclusiveYields['tt_embed'],
                        delta_numA = delta_dy_2M,
                        delta_numB = delta_tt_2M,
                        delta_denomA = delta_dy_inclusive,
                        delta_denomB = delta_tt_inclusive)

    sysUnc_xs_1M = calcSysUnc(sf = (yieldForMediumCat['DY_embed_1M']-yieldForMediumCat['tt_embed_1M'])/(inclusiveYields['DY_embed'] - inclusiveYields['tt_embed']), 
                        numA = yieldForMediumCat['DY_embed_1M'], 
                        numB = yieldForMediumCat['tt_embed_1M'],
                        denomA = inclusiveYields['DY_embed'],
                        denomB = inclusiveYields['tt_embed'],
                        delta_numA = 0,
                        delta_numB = yieldForMediumCat['tt_embed_1M']*0.1,
                        delta_denomA = 0,
                        delta_denomB = inclusiveYields['tt_embed']*0.1)

    sysUnc_xs_2M = calcSysUnc(sf = (yieldForMediumCat['DY_embed_2M']-yieldForMediumCat['tt_embed_2M'])/(inclusiveYields['DY_embed'] - inclusiveYields['tt_embed']), 
                        numA = yieldForMediumCat['DY_embed_2M'], 
                        numB = yieldForMediumCat['tt_embed_2M'],
                        denomA = inclusiveYields['DY_embed'],
                        denomB = inclusiveYields['tt_embed'],
                        delta_numA = 0,
                        delta_numB = yieldForMediumCat['tt_embed_2M']*0.1,
                        delta_denomA = 0,
                        delta_denomB = inclusiveYields['tt_embed']*0.1)

    preScaleFactor = inclusiveYields['DY_inclusive']/(inclusiveYields['DY_embed'] - inclusiveYields['tt_embed'])
    scaleFactor_1M = preScaleFactor*(yieldForMediumCat['DY_embed_1M']-yieldForMediumCat['tt_embed_1M'])
    scaleFactor_2M = preScaleFactor*(yieldForMediumCat['DY_embed_2M']-yieldForMediumCat['tt_embed_2M'])

    preScaleFactor2 = (inclusiveYields['DY_inclusive']+inclusiveYields['tt_inclusive'])/(inclusiveYields['DY_embed'])
    scaleFactor_1M2 = preScaleFactor2*(yieldForMediumCat['DY_embed_1M'])
    scaleFactor_2M2 = preScaleFactor2*(yieldForMediumCat['DY_embed_2M'])

    print ''
    print 'predicted DY in 1M: %.2fx(%.2f +/- %.2f - %.2f +/- %.2f)/(%.2f +/- %.2f - %.2f +/- %.2f) = %.2f +/- %.2f%% (statistical)' %(inclusiveYields['DY_inclusive'],
                                                                         yieldForMediumCat['DY_embed_1M'],
                                                                         calcSysUncSingle(yieldForMediumCat['DY_embed_1M'], eventCounterForMediumCat['DY_embed_1M']),
                                                                         yieldForMediumCat['tt_embed_1M'],
                                                                         calcSysUncSingle(yieldForMediumCat['tt_embed_1M'], eventCounterForMediumCat['tt_embed_1M']),
                                                                         inclusiveYields['DY_embed'],
                                                                         calcSysUncSingle(inclusiveYields['DY_embed'], eventCounterForInclusive['DY_embed']),
                                                                         inclusiveYields['tt_embed'],
                                                                         calcSysUncSingle(inclusiveYields['tt_embed'], eventCounterForInclusive['tt_embed']),
                                                                         scaleFactor_1M,
                                                                         sysUnc_1M*inclusiveYields['DY_inclusive']/scaleFactor_1M*100
                                                                        )
    print 'predicted DY in 2M: %.2fx(%.2f +/- %.2f - %.2f +/- %.2f)/(%.2f +/- %.2f - %.2f +/- %.2f) = %.2f +/- %.2f%% (statistical)' %(inclusiveYields['DY_inclusive'],
                                                                         yieldForMediumCat['DY_embed_2M'],
                                                                         calcSysUncSingle(yieldForMediumCat['DY_embed_2M'], eventCounterForMediumCat['DY_embed_2M']),
                                                                         yieldForMediumCat['tt_embed_2M'],
                                                                         calcSysUncSingle(yieldForMediumCat['tt_embed_2M'], eventCounterForMediumCat['tt_embed_2M']),
                                                                         inclusiveYields['DY_embed'],
                                                                         calcSysUncSingle(inclusiveYields['DY_embed'], eventCounterForInclusive['DY_embed']),
                                                                         inclusiveYields['tt_embed'],
                                                                         calcSysUncSingle(inclusiveYields['tt_embed'], eventCounterForInclusive['tt_embed']),
                                                                         scaleFactor_2M,
                                                                         sysUnc_2M*inclusiveYields['DY_inclusive']/scaleFactor_2M*100
                                                                        )
    print ''
    print 'predicted DY in 1M: %.2fx(%.2f - %.2f +/- %.2f)/(%.2f - %.2f +/- %.2f) = %.2f +/- %.2f%% (tt_xs)' %(inclusiveYields['DY_inclusive'],
                                                                         yieldForMediumCat['DY_embed_1M'],
                                                                         yieldForMediumCat['tt_embed_1M'],
                                                                         yieldForMediumCat['tt_embed_1M']*0.1,
                                                                         inclusiveYields['DY_embed'],
                                                                         inclusiveYields['tt_embed'],
                                                                         inclusiveYields['tt_embed']*0.1,
                                                                         scaleFactor_1M,
                                                                         sysUnc_xs_1M*inclusiveYields['DY_inclusive']/scaleFactor_1M*100
                                                                        )
    print 'predicted DY in 2M: %.2fx(%.2f - %.2f +/- %.2f)/(%.2f - %.2f +/- %.2f) = %.2f +/- %.2f%% (tt_xs)' %(inclusiveYields['DY_inclusive'],
                                                                         yieldForMediumCat['DY_embed_2M'],
                                                                         yieldForMediumCat['tt_embed_2M'],
                                                                         yieldForMediumCat['tt_embed_2M']*0.1,
                                                                         inclusiveYields['DY_embed'],
                                                                         inclusiveYields['tt_embed'],
                                                                         inclusiveYields['tt_embed']*0.1,
                                                                         scaleFactor_2M,
                                                                         sysUnc_xs_2M*inclusiveYields['DY_inclusive']/scaleFactor_2M*100
                                                                        )
    print ''
    print 'DY MC in 1M: %.2f' %yieldForMediumCat['DY_inclusive_1M']
    print 'DY MC in 2M: %.2f' %yieldForMediumCat['DY_inclusive_2M']
#     print 'predicted DY+tt in 1M: %.2f' %scaleFactor_1M2
#     print 'predicted DY+tt in 2M: %.2f' %scaleFactor_2M2


    if doDraw:
        position = (0.6, 0.9 - 0.06*2, 0.87, 0.9)
        l1 = tool.setMyLegend(position, [(dy_embed_1M, 'dy_embed_1M'), (tt_embed_1M, 'tt_embed_1M')])
        l2 = tool.setMyLegend(position, [(dy_embed_2M, 'dy_embed_2M'), (tt_embed_2M, 'tt_embed_2M')])

        psfile = 'DY_embed_tauUp.pdf'
        c = r.TCanvas("c","Test", 800, 600)
        dy_embed_1M.Draw()
        dy_embed_1M.SetTitle(';fMassKinFit;')
        tt_embed_1M.SetLineStyle(2)
        tt_embed_1M.SetLineColor(r.kRed)
        tt_embed_1M.Draw('same')
        l1.Draw('same')

        c.Print('%s(' %psfile)
        dy_embed_2M.Draw()
        dy_embed_2M.SetTitle(';fMassKinFit;')

        tt_embed_2M.SetLineStyle(2)
        tt_embed_2M.SetLineColor(r.kRed)
        tt_embed_2M.Draw('same')
        l2.Draw('same')

        c.Print('%s)' %psfile)


    return scaleFactor_1M, scaleFactor_2M, scaleFactor_1M2, scaleFactor_2M2, preScaleFactor

def l2MYieldCalculator(sample, massWindow, pairOption = 'iso', nBtag = '', ZLL = False):

    yieldForMediumCat = {}
    yieldForLooseCat = {}
    eventCounterForMediumCat = {}
    eventCounterForLooseCat = {}

    iFile =  r.TFile(sample)
    iTree = iFile.Get('eventTree')
    yieldForMediumCat['1M'] = 0.0
    yieldForMediumCat['2M'] = 0.0
    yieldForLooseCat['1L'] = 0.0
    yieldForLooseCat['2L'] = 0.0
    eventCounterForMediumCat['1M'] = 0.0
    eventCounterForMediumCat['2M'] = 0.0
    eventCounterForLooseCat['1L'] = 0.0
    eventCounterForLooseCat['2L'] = 0.0

    total = iTree.GetEntries()

    for i in range(0, total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %sample, iPrevious=i)
        iTree.GetEntry(i)
            
        #get the right pair of taus based on isoMin or ptMax
        if (iTree.nElectrons > 0 or iTree.nMuons > 0):
            continue
        if not makeWholeTools2.passJetTrigger(iTree):
            continue

        if ZLL and iTree.ZLL == 0:
            continue
        #get event category
        signSelection, isoSelection, bTagSelection = makeWholeTools2.findCategory(tree = iTree, 
                                                                                  iso = makeWholeSample_cfg.iso, 
                                                                                  option = pairOption,
                                                                                  isData = False,
                                                                                  relaxedRegionOption = makeWholeSample_cfg.Relax,
                                                                                  isEmbed = False,
                                                                                  usePassJetTrigger = makeWholeSample_cfg.usePassJetTrigger,
                                                                                  nBtag = nBtag)

        if signSelection == None or isoSelection == None:
            continue
        looseTag, mediumTag = getRightBTagCatName(bTagSelection)

        if  massWindow and not makeWholeTools2.passCut(iTree, pairOption):
            continue
        #calculate category yield
        if (signSelection == "OS") and (isoSelection == "Tight") and (mediumTag != '0M'):
            yieldForMediumCat[mediumTag] += iTree.triggerEff*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents
            eventCounterForMediumCat[mediumTag] += 1

        #calculate loose cat yield for embed samples
        if (signSelection == "OS") and (isoSelection == "Tight") and (looseTag != '0L'):
            yieldForLooseCat[looseTag] += iTree.triggerEff*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents
            eventCounterForLooseCat[looseTag] += 1
    print ''


    scaleFactor_1M = yieldForMediumCat['1M']/yieldForLooseCat['1L']
    scaleFactor_2M = yieldForMediumCat['2M']/yieldForLooseCat['2L']

    print '[%s] (1L): %.2f  %.0f'%(sample, yieldForLooseCat['1L'], eventCounterForLooseCat['1L'])
    print '[%s] (2L): %.2f  %.0f'%(sample, yieldForLooseCat['2L'], eventCounterForLooseCat['2L'])
    print '[%s] (1M): %.2f  %.0f'%(sample, yieldForMediumCat['1M'], eventCounterForMediumCat['1M'])
    print '[%s] (2M): %.2f  %.0f'%(sample, yieldForMediumCat['2M'], eventCounterForMediumCat['2M'])

    unc_1M = calcSysUncSingle(yieldForMediumCat['1M'], eventCounterForMediumCat['1M'])
    unc_2M = calcSysUncSingle(yieldForMediumCat['2M'], eventCounterForMediumCat['2M'])

    print '1M: %.2f +/- %.1f%%' %(yieldForMediumCat['1M'], unc_1M*100/yieldForMediumCat['1M'])
    print '2M: %.2f +/- %.1f%%' %(yieldForMediumCat['2M'], unc_2M*100/yieldForMediumCat['2M'])

    return yieldForMediumCat['1M'], yieldForMediumCat['2M']


shift = 'normal'
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

location = "samples_Iso"

# yieldCalculator(dy_mc = '/nfs_scratch/zmao/%s/tauESOn/%s/dy_OSTight.root' %(location, shiftLocation),
#                 tt_full_mc = '/nfs_scratch/zmao/%s/tauESOff/%s/tt_all.root' %(location, shiftLocation),
#                 dy_embed = '/nfs_scratch/zmao/%s/tauESOn/%s/DY_embed.root' %(location, shiftLocation2), 
#                 tt_embed = '/nfs_scratch/zmao/%s/tauESOff/%s/tt_embed_all.root' %(location, shiftLocation), 
#                 massWindow = True,
#                 pairOption = 'iso',
#                 nBtag = nBtag,
#                 doDraw = False,
# )

# massWindow = True
# l2MYieldCalculator(sample = '/nfs_scratch/zmao/%s/tauESOff/%s/Electroweak_withSingleTop.root' %(location, shiftLocation), 
#                    massWindow = massWindow,
#                    nBtag = nBtag)
# l2MYieldCalculator(sample = '/nfs_scratch/zmao/%s/tauESOn/%s/dy.root' %(location, shiftLocation), 
#                    massWindow = massWindow,
#                    nBtag = nBtag,
#                    ZLL = True)