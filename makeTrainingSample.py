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

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
j1Reg = lvClass()
j2Reg = lvClass()

def splitFileNames(inputName):
    fileNames = []
    tmpName = ''
    for i in range(len(inputName)):
        if inputName[i] != ' ' and inputName[i] != ',':
            tmpName += inputName[i]
        elif inputName[i] == ',':
            fileNames.append(tmpName)
            tmpName = ''
    fileNames.append(tmpName)
    return fileNames

def setUpFloatVarsDict():
    varDict = {}
    names = ['met1', 'iso1_1', 'iso2_1', 'svMass1', 'weight',
             'weightWithPU','EVENT1','EVENT2','EVENT3', 'EVENT4', 'sampleName2', 'category2']
    for iName in names:
        varDict[iName] = array('f', [0.])
    return varDict

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--i", dest="inputFile", default = '', help="")
    parser.add_option("--o", dest="outputFile", default = 'trainSample', help="")
    parser.add_option("--weightOne", dest="weightOne", default = -1., help="")
    parser.add_option("--weightTwo", dest="weightTwo", default = -1., help="")
    parser.add_option("--c", dest="cut", default = 'none', help="")
    parser.add_option("--iso", dest="isoSelect", default = 'none', help="")
    parser.add_option("--sign", dest="signSelect", default = 'none', help="")
    parser.add_option("--relaxRegion", dest="relaxRegion", default = 'none', help="")
    parser.add_option("--bRegion", dest="bRegion", default = 'none', help="")
    parser.add_option("--useLooseForShape", dest="useLooseForShape", default = 0, help="")

    options, args = parser.parse_args()
    return options

def passCut(iTree, bTagSelection, bRegion, isData, isEmbed):
    if bTagSelection == None:
        return False
    if isEmbed:
        if iTree.HLT_Any == 0:
            return False
    if iTree.nElectrons > 0 or iTree.nMuons > 0:
        return False
    if 'M' in bRegion:
        if '0M' not in bTagSelection:
            return True
    if 'L' in bRegion:
        if '0L' not in bTagSelection:
            return True
    if bRegion == 'none':
            return True
    return False


def findBCategory(csv1, csv2):
    CSVL = 0.244
    if csv1 < CSVL:
        return -1
    elif csv2 > CSVL:
        return 2
    else:
        return 1 

options = opts()
iFile = options.inputFile
ifile = r.TFile(iFile)
iTree = ifile.Get("eventTree")
print options.bRegion
oString = options.signSelect + options.isoSelect + options.bRegion
oFile = r.TFile("%s_%s.root" %(options.outputFile, oString),"recreate")
oTree = iTree.CloneTree(0)
total = iTree.GetEntries()

Lumi = 19.7

floatVarsDict = setUpFloatVarsDict()

for iVar in floatVarsDict.keys():
    oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/f" %iVar)

isData = False
isEmbed = False

#calculate yields
looseYield_1 = 0.0
looseYield_2 = 0.0
mediumYield_1 = 0.0
mediumYield_2 = 0.0

if int(options.useLooseForShape) != 0:
    for i in range(total):
        r.gStyle.SetOptStat(0)
        tool.printProcessStatus(iCurrent=i, total=total, processName = 'Looping sample %s, calculating yields' %iFile)
        iTree.GetEntry(i)
        if 'data' in iTree.sampleName:
            isData = True
        if 'emb' in iTree.sampleName:
            isEmbed = True
        signSelection, isoSelection, bTagSelection = makeWholeTools2.findCategory(iTree, 1.0, 'pt', isData, options.relaxRegion)
        if options.isoSelect != isoSelection and options.isoSelect != 'none':
            continue
        if options.signSelect != signSelection and options.signSelect != 'none':
            continue
        if passCut(iTree, bTagSelection, 'L', isData, isEmbed):
            if '1L' in bTagSelection:
                looseYield_1 += iTree.xs*Lumi*iTree.triggerEff*iTree.PUWeight/(iTree.initEvents)
            elif '2L' in bTagSelection:
                looseYield_2 += iTree.xs*Lumi*iTree.triggerEff*iTree.PUWeight/(iTree.initEvents)
        if passCut(iTree, bTagSelection, 'M', isData, isEmbed):
            if '1M' in bTagSelection:
                mediumYield_1 += iTree.xs*Lumi*iTree.triggerEff*iTree.PUWeight/(iTree.initEvents)
            elif '2M' in bTagSelection:
                mediumYield_2 += iTree.xs*Lumi*iTree.triggerEff*iTree.PUWeight/(iTree.initEvents)
    print 'Loose yields: %s (1M)\t  %s (2M)' %(looseYield_1, looseYield_2)
    print 'Medium yields: %s (1M)\t  %s (2M)' %(mediumYield_1, mediumYield_2)

for i in range(total):
    r.gStyle.SetOptStat(0)
    tool.printProcessStatus(iCurrent=i, total=total, processName = 'Looping sample %s' %iFile)
    iTree.GetEntry(i)
    if 'data' in iTree.sampleName:
        isData = True
    if 'emb' in iTree.sampleName:
        isEmbed = True
    signSelection, isoSelection, bTagSelection = makeWholeTools2.findCategory(iTree, 1.0, 'pt', isData, options.relaxRegion)
    if options.isoSelect != isoSelection and options.isoSelect != 'none':
        continue
    if options.signSelect != signSelection and options.signSelect != 'none':
        continue
    if passCut(iTree, bTagSelection, options.bRegion, isData, isEmbed):
        floatVarsDict['category2'][0] = findBCategory(iTree.CSVJ1, iTree.CSVJ2)

        if '_semi' in iTree.sampleName:
            sampleName = iTree.sampleName[:iTree.sampleName.find('_semi')+5]
        elif '_' in iTree.sampleName and 'emb' not in iTree.sampleName:
            sampleName = iTree.sampleName[:iTree.sampleName.find('_')]
        else:
            sampleName = iTree.sampleName

        if isEmbed:
            if isData:
                sampleName = 'DY_embed'
                floatVarsDict['weight'][0] = iTree.triggerEff
                floatVarsDict['weightWithPU'][0] = floatVarsDict['weight'][0]
            else:
                sampleName = 'tt_embed'
                floatVarsDict['weight'][0] = iTree.xs*0.983*Lumi*iTree.triggerEff/(iTree.initEvents)
                floatVarsDict['weightWithPU'][0] = floatVarsDict['weight'][0]
        elif isData:
            sampleName = 'dataOSRelax_all'
            if floatVarsDict['category2'][0] == 1:
                floatVarsDict['weight'][0] = float(options.weightOne)
                floatVarsDict['weightWithPU'][0] = float(options.weightOne)
            elif floatVarsDict['category2'][0] == 2:
                floatVarsDict['weight'][0] = float(options.weightTwo)
                floatVarsDict['weightWithPU'][0] = float(options.weightTwo)            
        else:
            floatVarsDict['weight'][0] = iTree.xs*Lumi*iTree.triggerEff/(iTree.initEvents)
            floatVarsDict['weightWithPU'][0] = floatVarsDict['weight'][0]*iTree.PUWeight
            if int(options.useLooseForShape) != 0:
                if floatVarsDict['category2'][0] == 1:
                    floatVarsDict['weightWithPU'][0] = floatVarsDict['weightWithPU'][0]*mediumYield_1/looseYield_1
                elif floatVarsDict['category2'][0] == 2:
                    floatVarsDict['weightWithPU'][0] = floatVarsDict['weightWithPU'][0]*mediumYield_2/looseYield_2

        floatVarsDict['sampleName2'][0] = tool.nameEnDecoder(sampleName, 'encode')
        step = struct.calcsize("i")/4
        floatVarsDict['EVENT1'][0] = float(int(iTree.EVENT >> 8*(struct.calcsize("i")-step)))
        floatVarsDict['EVENT2'][0] = float(int((iTree.EVENT<<8*step) >> 8*(struct.calcsize("i")-step)))
        floatVarsDict['EVENT3'][0] = float(int((iTree.EVENT<<16*step) >> 8*(struct.calcsize("i")-step)))
        floatVarsDict['EVENT4'][0] = float(int((iTree.EVENT<<24*step) >> 8*(struct.calcsize("i")-step)))
        floatVarsDict['met1'][0] = iTree.met.at(0)
        floatVarsDict['svMass1'][0] = iTree.svMass.at(0)
        floatVarsDict['iso1_1'][0] = iTree.iso1.at(0)
        floatVarsDict['iso2_1'][0] = iTree.iso2.at(0)

        oTree.Fill()

print ''

oFile.cd()
oTree.Write()
# cutFlow.Write()
nSaved = oTree.GetEntries()
oFile.Close()

print 'saved %i events out of %i at: %s_%s.root' %(nSaved,total,options.outputFile, oString)