#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array

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

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--i", dest="inputFile", default = '', help="")
    parser.add_option("--o", dest="outputFile", default = 'trainSample', help="")
    parser.add_option("--xs", dest="xs", default = 1., help="")
    parser.add_option("--c", dest="cut", default = 'none', help="")
    options, args = parser.parse_args()
    return options

def passCut(iTree, cut):
    if 'none' in cut:
        return True
    if 'tight' in cut:
        if iTree.iso1.at(0) > 1.5 or iTree.iso2.at(0) > 1.5:
            return False
    if 'relaxed' in cut:
        if iTree.iso1.at(0) < 3 or iTree.iso2.at(0) < 3:
            return False
    if 'same' in cut:
        if iTree.charge1.at(0) == -iTree.charge2.at(0):
            return False
    if 'opposite' in cut:
        if iTree.charge1.at(0) == iTree.charge2.at(0):
            return False
    if 'bTag' in cut:
        if iTree.CSVJ1 < 0.679 or iTree.CSVJ2 < 0.244:
            return False
    if '2M' in cut:
        if iTree.CSVJ1 < 0.679 or iTree.CSVJ2 < 0.679:
            return False
    if '1M1NonM' in cut:
        if iTree.CSVJ1 < 0.679 or iTree.CSVJ2 > 0.679:
            return False
    if '1M' in cut:
        if iTree.CSVJ1 < 0.679:
            return False
    if '3rdLepVeto' in cut:
        if iTree.nElectrons > 0 or iTree.nMuons > 0:
            return False
    return True

def findCategory(csv1, csv2):
    if csv1 < 0.679:
        return -1
    elif csv2 > 0.679:
        return 2
    else:
        return 1 

options = opts()
iFile = options.inputFile
ifile = r.TFile(iFile)
iTree = ifile.Get("eventTree")
cutFlow = ifile.Get("preselection")
oFile = r.TFile("%s_%s.root" %(options.outputFile, options.cut),"recreate")
oTree = iTree.CloneTree(0)
total = iTree.GetEntries()
category = array('i', [0])
sampleName2 = array('i', [0])

nInit = int(cutFlow.GetBinContent(1))
initEvents = array('i', [0])
inputXS = float(options.xs)
xs = array('f', [0.])
met = array('f', [0.])
svMass = array('f', [0.])

oTree.Branch("sampleName2", sampleName2, "sampleName2/I")
oTree.Branch("met1", met, "met1/f")
oTree.Branch("svMass1", svMass, "svMass1/f")

oTree.Branch("category", category, "category/I")
oTree.Branch("initEvents", initEvents, "initEvents/I")
oTree.Branch("xs", xs, "xs/f")

for i in range(total):
    r.gStyle.SetOptStat(0)
    tool.printProcessStatus(iCurrent=i, total=total, processName = 'Looping sample %s' %iFile)
    iTree.GetEntry(i)
    if passCut(iTree, options.cut):
        initEvents[0] = nInit
        xs[0] = inputXS
        sampleName2[0] = tool.nameEnDecoder(iTree.sampleName, 'encode')
        category[0] = findCategory(iTree.CSVJ1, iTree.CSVJ2)
        met[0] = iTree.met.at(0)
        svMass[0] = iTree.svMass.at(0)
        oTree.Fill()

print ''

oFile.cd()
oTree.Write()
cutFlow.Write()
nSaved = oTree.GetEntries()
oFile.Close()

print 'saved %i events out of %i at: %s_%s.root' %(nSaved,total,options.outputFile, options.cut)