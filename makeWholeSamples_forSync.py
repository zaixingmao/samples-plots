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

inputFiles = [('2M', 'combined_2M_iso1.0.root'),
              ('1M', 'combined_1M_iso1.0.root'),
]


oFileName = 'combined_iso1.0.root'
oFile = r.TFile(oFileName, 'RECREATE')
oTree = r.TTree('eventTree', '')

BDT = array('f', [0.])
mJJ = array('f', [0.])
svMass = array('f', [0.])
fMass = array('f', [0.])
fMassKinFit = array('f', [0.])
chi2KinFit = array('f', [0.])
chi2KinFit2 = array('f', [0.])

CSVJ2 = array('f', [0.])
Category = bytearray(5)


triggerEff = array('f', [0.])
sampleName = bytearray(20)
genMatchName = bytearray(3)

BDTs = []
nMassPoints = len(makeWholeSample_cfg.trainedMassPoints)


oTree.Branch("BDT" , BDT, "BDT/F")
oTree.Branch("mJJ", mJJ, "mJJ/F")
oTree.Branch("fMass", fMass, "fMass/F")
oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
oTree.Branch("svMass", svMass, "svMass/F")
oTree.Branch("triggerEff", triggerEff, "triggerEff/F")
oTree.Branch("sampleName", sampleName, "sampleName[21]/C")
oTree.Branch("genMatchName", genMatchName, "genMatchName[21]/C")
oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
oTree.Branch("chi2KinFit2", chi2KinFit2, "chi2KinFit2/F")

oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")
oTree.Branch("Category", Category, "Category[21]/C")


files = []
trees = []
MC_Data_svMass = []
xs = []
initEvents = []
finalEventsWithXS = []
L2Ts = []

for ifile in range(len(inputFiles)):
    files.append(r.TFile(inputFiles[ifile][1]))
    trees.append(files[ifile].Get('eventTree'))
    L2Ts.append(files[ifile].Get('L2T'))
    L2Ts[ifile].SetName('L_to_T_%s' %inputFiles[ifile][0])
    MC_Data_svMass.append(files[ifile].Get('MC_Data_svMass'))
    MC_Data_svMass[ifile].SetName('MC_Data_svMass_%s' %inputFiles[ifile][0])
    finalEventsWithXS.append(files[ifile].Get('finalEventsWithXS'))
    finalEventsWithXS[ifile].SetName('finalEventsWithXS_%s' %inputFiles[ifile][0])

xs = files[0].Get('xs')
initEvents= files[0].Get('initEvents')

for ifile in range(len(inputFiles)):

    total = trees[ifile].GetEntries()
    for i in range(0, total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample')
        trees[ifile].GetEntry(i)
#         BDT[0] = trees[ifile].BDT_both 
        mJJ[0] = trees[ifile].mJJ
        fMass[0] = trees[ifile].fMass
        fMassKinFit[0] = trees[ifile].fMassKinFit
        chi2KinFit[0] = trees[ifile].chi2KinFit
        chi2KinFit2[0] = trees[ifile].chi2KinFit2

        svMass[0] = trees[ifile].svMass
        CSVJ2[0] = trees[ifile].CSVJ2

        triggerEff[0] = trees[ifile].triggerEff
        sampleName[:21] = trees[ifile].sampleName
        genMatchName[:3] = trees[ifile].genMatchName
        Category[:5] = inputFiles[ifile][0]
        oTree.Fill()

    print ''

oFile.cd()
oTree.Write()
xs.Write()
initEvents.Write()
for i in range(len(MC_Data_svMass)):
    MC_Data_svMass[i].Write()
    finalEventsWithXS[i].Write()
    L2Ts[i].Write()
oFile.Close()

print 'Combined event saved at: %s' %oFileName


