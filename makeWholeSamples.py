#!/usr/bin/env python
import ROOT as r
import tool
import math
import optparse
import os
from array import array
import makeWholeSample_cfg


def getCorrectBDT(iTree, massPoint):
    bdts = {'260': iTree.BDT_260,
            '300': iTree.BDT_300,
            '350': iTree.BDT_350}
    return bdts[massPoint]

inputFiles = [('2Vars', 'combined_2_new.root'),
              ('3Vars', 'combined_3_new.root'),
              ('18Vars', 'combined_18_new.root')]


oFileName = 'combined_all_fixChi2.root'
oFile = r.TFile(oFileName, 'RECREATE')
oTree = r.TTree('eventTree', '')

mJJReg = array('f', [0.])
mJJ = array('f', [0.])
svMass = array('f', [0.])
fMass = array('f', [0.])
fMassKinFit = array('f', [0.])
chi2KinFit = array('f', [0.])
CSVJ2 = array('f', [0.])

triggerEff = array('f', [0.])
sampleName = bytearray(20)
genMatchName = bytearray(3)

BDTs = []
nMassPoints = len(makeWholeSample_cfg.trainedMassPoints)

for indexFiles in range(len(inputFiles)):
    for iMassPoint in makeWholeSample_cfg.trainedMassPoints:
        BDTs.append(array('f', [0.]))

oTree.Branch("mJJReg", mJJReg, "mJJReg/F")
oTree.Branch("mJJ", mJJ, "mJJ/F")
oTree.Branch("fMass", fMass, "fMass/F")
oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
oTree.Branch("svMass", svMass, "svMass/F")
oTree.Branch("triggerEff", triggerEff, "triggerEff/F")
oTree.Branch("sampleName", sampleName, "sampleName[21]/C")
oTree.Branch("genMatchName", genMatchName, "genMatchName[21]/C")
oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")

files = []
trees = []

for ifile in range(len(inputFiles)):
    files.append(r.TFile(inputFiles[ifile][1]))
    trees.append(files[ifile].Get('eventTree'))

MC_Data_svMass = files[0].Get('MC_Data_svMass')
MC_Data_mJJReg = files[0].Get('MC_Data_mJJReg')
xs = files[0].Get('xs')
initEvents = files[0].Get('initEvents')
finalEventsWithXS = files[0].Get('finalEventsWithXS')


total = trees[0].GetEntries()
for i in range(0, total):
    tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample')
    for ifile in range(len(inputFiles)):
        trees[ifile].GetEntry(i)
        for imp in range(nMassPoints):
            BDTs[ifile*nMassPoints + imp][0] = getCorrectBDT(trees[ifile], str(makeWholeSample_cfg.trainedMassPoints[imp]))

    mJJReg[0] = trees[0].mJJReg
    mJJ[0] = trees[0].mJJ
    fMass[0] = trees[0].fMass
    fMassKinFit[0] = trees[0].fMassKinFit
    chi2KinFit[0] = trees[0].chi2KinFit
    svMass[0] = trees[0].svMass
    CSVJ2[0] = trees[0].CSVJ2

    triggerEff[0] = trees[0].triggerEff
    sampleName[:21] = trees[0].sampleName
    genMatchName[:3] = trees[0].genMatchName
    oTree.Fill()

print ''

oFile.cd()
oTree.Write()
MC_Data_svMass.Write()
MC_Data_mJJReg.Write()
xs.Write()
initEvents.Write()
finalEventsWithXS.Write()

oFile.Close()

print 'Combined event saved at: %s' %oFileName


