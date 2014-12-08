#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array
import makeWholeSample_cfg

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))


lumi = 19.7

def calcSysUnc(sf, num, denom, delta_num = 0, delta_denom = 0):
    if delta_num == 0:
        delta_num = math.sqrt(num)
    if delta_denom == 0:
        delta_denom = math.sqrt(denom)
    return sf*math.sqrt((delta_num/num)**2 + (delta_denom/denom)**2)

pair_0_counter = 0
pairNot_0_counter = 0

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

def addYieldInRegion(dict, name):
    out = 0.0
    ignoreKeys = ['0L1M', '0L2M', '1L2M']
    ignoreKeys = []
    for ikey in dict.keys():
        if ikey in ignoreKeys:
            continue
        if name in ikey:
            out += dict[ikey]
    return out

def findSignSelection(charge1, charge2):
    if charge1 == charge2:
        return 'SS'
    else:
        return 'OS'

def findIsoSelection(iso1, iso2, iso = 1.0):
    isoTight = iso
    isoCut = 1.0
    isoMax = 4.0

    isoSelection = None
    if (iso1 > isoMax) or (iso2 > isoMax):
        return None
    elif (iso1 < isoTight) and (iso2 < isoTight):
        return 'Tight'
    elif (iso1 > isoCut) and (iso2 > isoCut):
        return 'Relax'
    else:
        return None

def findBTagSelection(CSVJ1, CSVJ2, NBTags):
    CSVL = 0.244
    bTagSelection = None
    if CSVJ1 < CSVL:
        bTagSelection = '0L'
    elif (CSVJ1 > CSVL) and (CSVJ2 < CSVL):
        bTagSelection = '1L'
    else:
        bTagSelection = '2L'

    if bTagSelection == None:
        return bTagSelection

    if NBTags < 1:
        bTagSelection += '0M'
    if NBTags == 1:
        bTagSelection += '1M'
    if NBTags > 1:
        bTagSelection += '2M'
    return bTagSelection

def findCategory(tree, iso):
    global pair_0_counter
    global pairNot_0_counter

    if findRightPair(tree, 'iso') == 0:
        pair_0_counter += 1
    else:
        pairNot_0_counter += 1
    rightPair = findRightPair(tree, '')
    if tree.pt1.at(rightPair) < 45 or tree.pt2.at(rightPair) < 45:
        return None, None, None

    #sign selection
    signSelection = findSignSelection(tree.charge1.at(rightPair), tree.charge2.at(rightPair))

    #iso selections
    isoSelection = findIsoSelection(tree.iso1.at(rightPair), tree.iso2.at(rightPair), iso)
    
    #b-tag selections
    bTagSelection = findBTagSelection(tree.CSVJ1, tree.CSVJ2, tree.NBTags)

    return signSelection, isoSelection, bTagSelection
        

def calculateSF(fileList, location0, out, sigRegionOption = 'tight', relaxedRegionOption = 'relaxed', verbose = False, isoTight = 1.0):
    files = []
    trees = []
    yields = {'MC': {},
              'Data': {},
              'QCD': {}}
    yields = {'MC': {},
              'Data': {},
              'QCD': {}}

    #build yield dictionary
    for sign in ['SS', 'OS']:
        for ikey in yields.keys():
            yields[ikey][sign] = {}
            for iso in ['Tight', 'Relax']:
                yields[ikey][sign][iso] = {}
                for l in ['0L', '1L', '2L']:
                    for m in ['0M', '1M', '2M']:
                        yields[ikey][sign][iso][l+m] = 0.0

    for fileName, location, in fileList:

        files.append(r.TFile(location0+location))
        trees.append(files[len(files)-1].Get("eventTree"))
        total = trees[len(trees)-1].GetEntries()
        if 'data' in fileName:
            isData = True
        else:
            isData = False
        if 'H2hh' in fileName:
            continue
        for i in range(total):
            tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %fileName)
            trees[len(trees)-1].GetEntry(i)
            if not isData:
                puWeight = trees[len(trees)-1].PUWeight
            else:
                puWeight = 1.0
            if trees[len(trees)-1].nElectrons == 0 and trees[len(trees)-1].nMuons == 0:
                signSelection, isoSelection, bTagSelection = findCategory(trees[len(trees)-1], isoTight)
                if (signSelection == None) or (isoSelection == None) or (bTagSelection == None):
                    continue
                if isData:
                    yields['Data'][signSelection][isoSelection][bTagSelection] += 1.0
                else:
                    yields['MC'][signSelection][isoSelection][bTagSelection]+=trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff*puWeight
        print ''

    #get QCD values
    for sign in ['SS', 'OS']:
        for iso in ['Tight', 'Relax']:
            for l in ['0L', '1L', '2L']:
                for m in ['0M', '1M', '2M']:
                    if  yields['Data'][sign][iso][l+m] - yields['MC'][sign][iso][l+m] > 0.0:
                        yields['QCD'][sign][iso][l+m] = yields['Data'][sign][iso][l+m] - yields['MC'][sign][iso][l+m]
                    else:
                        yields['QCD'][sign][iso][l+m] = 0.0
    if verbose:
        
        print 'SST__________________________________'
        for region in ['0L','1L','2L']:
            out = ''
            for region2 in ['0M','1M','2M']:
                out += "%.2f/%.2f/%.0f\t" %(yields['QCD']['SS']['Tight'][region+region2], yields['MC']['SS']['Tight'][region+region2], yields['Data']['SS']['Tight'][region+region2])
            print out
        print 'MC (1M): %.2f\tData (1M): %.2f' %(addYieldInRegion(yields['MC']['SS']['Tight'], '1M'), addYieldInRegion(yields['Data']['SS']['Tight'], '1M'))
        print 'MC (2M): %.2f\tData (2M): %.2f' %(addYieldInRegion(yields['MC']['SS']['Tight'], '2M'), addYieldInRegion(yields['Data']['SS']['Tight'], '2M'))
        print 'MC (1L): %.2f\tData (1L): %.2f' %(addYieldInRegion(yields['MC']['SS']['Tight'], '1L'), addYieldInRegion(yields['Data']['SS']['Tight'], '1L'))
        print 'MC (2L): %.2f\tData (2L): %.2f' %(addYieldInRegion(yields['MC']['SS']['Tight'], '2L'), addYieldInRegion(yields['Data']['SS']['Tight'], '2L'))
        print ''
        print 'SSR__________________________________'
        for region in ['0L','1L','2L']:
            out = ''
            for region2 in ['0M','1M','2M']:
                out += "%.2f/%.2f/%.0f\t" %(yields['QCD']['SS']['Relax'][region+region2], yields['MC']['SS']['Relax'][region+region2], yields['Data']['SS']['Relax'][region+region2])
            print out
        print 'MC (1M): %.2f\tData (1M): %.2f' %(addYieldInRegion(yields['MC']['SS']['Relax'], '1M'), addYieldInRegion(yields['Data']['SS']['Relax'], '1M'))
        print 'MC (2M): %.2f\tData (2M): %.2f' %(addYieldInRegion(yields['MC']['SS']['Relax'], '2M'), addYieldInRegion(yields['Data']['SS']['Relax'], '2M'))
        print 'MC (1L): %.2f\tData (1L): %.2f' %(addYieldInRegion(yields['MC']['SS']['Relax'], '1L'), addYieldInRegion(yields['Data']['SS']['Relax'], '1L'))
        print 'MC (2L): %.2f\tData (2L): %.2f' %(addYieldInRegion(yields['MC']['SS']['Relax'], '2L'), addYieldInRegion(yields['Data']['SS']['Relax'], '2L'))

        print ''
        print 'OSR__________________________________'
        for region in ['0L','1L','2L']:
            out = ''
            for region2 in ['0M','1M','2M']:
                out += "%.2f/%.2f/%.0f\t" %(yields['QCD']['OS']['Relax'][region+region2], yields['MC']['OS']['Relax'][region+region2], yields['Data']['OS']['Relax'][region+region2])
            print out

    #define scale factors
    SF = {'relax2tight': {},
          'loose2medium': {},
          'data2QCD': {},
          'weight': {},
         }
    SF_unc = {'relax2tight': {},
              'loose2medium': {},
              'data2QCD': {},
              'weight': {},
             }

    for region in ['0', '1', '2']:
        #calculate scale factors
        if addYieldInRegion(yields['QCD']['SS']['Relax'], region + 'L') != 0:
            SF['relax2tight'][region] = addYieldInRegion(yields['QCD']['SS']['Tight'], region + 'L')/addYieldInRegion(yields['QCD']['SS']['Relax'], region + 'L')
        else:
            SF['relax2tight'][region] = 0
        if addYieldInRegion(yields['QCD']['SS']['Relax'], region + 'L') != 0:
            SF['loose2medium'][region] = addYieldInRegion(yields['QCD']['SS']['Relax'], region + 'M')/addYieldInRegion(yields['QCD']['SS']['Relax'], region + 'L')
        else:
            SF['loose2medium'][region] = 0
        if addYieldInRegion(yields['Data']['OS']['Relax'], region + 'M') != 0:
            SF['data2QCD'][region] = addYieldInRegion(yields['QCD']['OS']['Relax'], region + 'L')/addYieldInRegion(yields['Data']['OS']['Relax'], region + 'L')
        else:
            SF['data2QCD'][region] = 0
        SF['weight'][region] = SF['relax2tight'][region]*SF['loose2medium'][region]*SF['data2QCD'][region]
        
        #calculate uncertainties factors
        SF_unc['relax2tight'][region] = calcSysUnc(sf = SF['relax2tight'][region], 
                                                   num = addYieldInRegion(yields['QCD']['SS']['Tight'], region + 'L'), 
                                                   denom = addYieldInRegion(yields['QCD']['SS']['Relax'], region + 'L'))
        SF_unc['loose2medium'][region] = calcSysUnc(sf = SF['loose2medium'][region], 
                                                    num = addYieldInRegion(yields['QCD']['SS']['Relax'], region + 'M'), 
                                                    denom = addYieldInRegion(yields['QCD']['SS']['Relax'], region + 'L'))
        SF_unc['data2QCD'][region] = calcSysUnc(sf = 1.0 - SF['data2QCD'][region], 
                                                num = addYieldInRegion(yields['MC']['OS']['Relax'], region + 'L'), 
                                                denom = addYieldInRegion(yields['Data']['OS']['Relax'], region + 'L'))
        unc_weight1 = calcSysUnc(sf = SF['relax2tight'][region]*SF['loose2medium'][region], 
                                 num = SF['relax2tight'][region], 
                                 denom = SF['loose2medium'][region],
                                 delta_num = SF_unc['relax2tight'][region],
                                 delta_denom = SF_unc['loose2medium'][region])
        SF_unc['weight'][region] = calcSysUnc(sf = SF['relax2tight'][region]*SF['loose2medium'][region]*SF['data2QCD'][region], 
                                              num = SF['relax2tight'][region]*SF['loose2medium'][region], 
                                              denom = SF['data2QCD'][region],
                                              delta_num = unc_weight1,
                                              delta_denom = SF_unc['data2QCD'][region])
                                

    if verbose:
        for region in ['1M', '2M', '1L', '2L']:
            print '%s_________________________' %region
            print '%.2f\t\t%.2f/%.0f' %(addYieldInRegion(yields['MC']['OS']['Tight'], region), 
                                        addYieldInRegion(yields['MC']['SS']['Tight'], region), 
                                        addYieldInRegion(yields['Data']['SS']['Tight'], region))
            print '%.2f/%.0f\t%.2f/%.0f' %(addYieldInRegion(yields['MC']['OS']['Relax'], region), 
                                           addYieldInRegion(yields['Data']['OS']['Relax'], region), 
                                           addYieldInRegion(yields['MC']['SS']['Relax'], region), 
                                           addYieldInRegion(yields['Data']['SS']['Relax'], region))
            print ''


        print 'Results__________________________________'
        print 'Category\t\t1tag_veto\t\t2tag_veto'

        line1 = 'relax2tight\t'
        line2 = 'loose2medium\t'
        line3 = 'data2QCD\t'
        line4 = 'weights\t\t'

        for region in ['1', '2']:
            line1 += '\t%.3f +/- %.3f (%.f%%)' %(SF['relax2tight'][region], SF_unc['relax2tight'][region], 100*SF_unc['relax2tight'][region]/SF['relax2tight'][region])
            line2 += '\t%.3f +/- %.3f (%.f%%)' %(SF['loose2medium'][region], SF_unc['loose2medium'][region], 100*SF_unc['loose2medium'][region]/SF['loose2medium'][region])
            line3 += '\t%.3f +/- %.3f (%.f%%)' %(SF['data2QCD'][region], SF_unc['data2QCD'][region], 100*SF_unc['data2QCD'][region]/SF['data2QCD'][region])
            line4 += '\t%.3f +/- %.3f (%.f%%)' %(SF['weight'][region], SF_unc['weight'][region], 100*SF_unc['weight'][region]/SF['weight'][region])

        print line1
        print line2
        print line3
        print line4

        print 'QCD in 1M: %.2f' %(addYieldInRegion(yields['Data']['OS']['Relax'], '1L')*SF['weight']['1'])
        print 'QCD in 2M: %.2f' %(addYieldInRegion(yields['Data']['OS']['Relax'], '2L')*SF['weight']['2'])
        print 'MC in 1M: %.2f' %(addYieldInRegion(yields['MC']['OS']['Tight'], '1M'))
        print 'MC in 2M: %.2f' %(addYieldInRegion(yields['MC']['OS']['Tight'], '2M'))

    output = []
    output.append(SF['weight']['1']) 
    output.append(SF['weight']['2'])
    output.append(SF['relax2tight']['1']*SF['loose2medium']['1']) 
    output.append(SF['relax2tight']['2']*SF['loose2medium']['2']) 

    return output

# calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012None', 'very_semiTight','very_relaxed',False, True)
# calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012None', 'semiTight','relaxed',False, True)
calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, '012None', 'tight','relaxed', True)
print pair_0_counter
print pairNot_0_counter