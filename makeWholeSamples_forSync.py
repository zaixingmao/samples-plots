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
            '270': iTree.BDT_270,
            '280': iTree.BDT_280,
            '290': iTree.BDT_290,
            '300': iTree.BDT_300,
            '310': iTree.BDT_310,
            '320': iTree.BDT_320,
            '330': iTree.BDT_330,
            '340': iTree.BDT_340,
            '350': iTree.BDT_350,
#             '500': iTree.BDT_500,
#             '700': iTree.BDT_700
            }
    return bdts[massPoint]

inputFiles = [('ML', 'combined_8_all.root'),
              ('2M', 'combined_8_all_kinFitGreater200.root'),
              ('1M', 'combined_18_all.root'),
]


oFileName = 'combined_all_Cat.root'
oFile = r.TFile(oFileName, 'RECREATE')
oTree = r.TTree('eventTree', '')

BDT = array('f', [0.])
mJJReg = array('f', [0.])
mJJ = array('f', [0.])
svMass = array('f', [0.])
fMass = array('f', [0.])
fMassKinFit = array('f', [0.])
chi2KinFit = array('f', [0.])
CSVJ2 = array('f', [0.])
Category = bytearray(3)


triggerEff = array('f', [0.])
sampleName = bytearray(20)
genMatchName = bytearray(3)

BDTs = []
nMassPoints = len(makeWholeSample_cfg.trainedMassPoints)


oTree.Branch("BDT" , BDT, "BDT/F")
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
oTree.Branch("Category", Category, "Category[21]/C")


files = []
trees = []
MC_Data_svMass = []
MC_Data_mJJReg = []
xs = []
initEvents = []
finalEventsWithXS = []

for ifile in range(len(inputFiles)):
    files.append(r.TFile(inputFiles[ifile][1]))
    trees.append(files[ifile].Get('eventTree'))

    MC_Data_svMass.append(files[0].Get('MC_Data_svMass'))
    MC_Data_svMass[ifile].SetName('MC_Data_svMass_%s' %inputFiles[ifile][0])
    MC_Data_mJJReg.append(files[0].Get('MC_Data_mJJReg'))
    MC_Data_mJJReg[ifile].SetName('MC_Data_mJJReg_%s' %inputFiles[ifile][0])
    xs.append(files[0].Get('xs'))
    xs[ifile].SetName('xs_%s' %inputFiles[ifile][0])
    initEvents.append(files[0].Get('initEvents'))
    initEvents[ifile].SetName('initEvents_%s' %inputFiles[ifile][0])
    finalEventsWithXS.append(files[0].Get('finalEventsWithXS'))
    finalEventsWithXS[ifile].SetName('finalEventsWithXS_%s' %inputFiles[ifile][0])


for ifile in range(len(inputFiles)):

    total = trees[ifile].GetEntries()
    for i in range(0, total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample')
        trees[ifile].GetEntry(i)
#         BDT[0] = trees[ifile].BDT_both 
        mJJReg[0] = trees[ifile].mJJReg
        mJJ[0] = trees[ifile].mJJ
        fMass[0] = trees[ifile].fMass
        fMassKinFit[0] = trees[ifile].fMassKinFit
        chi2KinFit[0] = trees[ifile].chi2KinFit
        svMass[0] = trees[ifile].svMass
        CSVJ2[0] = trees[ifile].CSVJ2

        triggerEff[0] = trees[ifile].triggerEff
        sampleName[:21] = trees[ifile].sampleName
        genMatchName[:3] = trees[ifile].genMatchName
        Category[:3] = inputFiles[ifile][0]
        oTree.Fill()

    print ''

oFile.cd()
oTree.Write()
for i in range(len(MC_Data_svMass)):
    MC_Data_svMass[i].Write()
    MC_Data_mJJReg[i].Write()
    xs[i].Write()
    initEvents[i].Write()
    finalEventsWithXS[i].Write()

oFile.Close()

print 'Combined event saved at: %s' %oFileName


