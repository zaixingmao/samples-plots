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

dR_tauEleMu_max = 0.2
dR_b_max = 0.5
lumi = 19.0

def findDR(genPt, genEta, genPhi, pt, eta, phi):

    tmpGen = lvClass()
    tmpParticle = lvClass()
    tmpParticle.SetCoordinates(pt, eta, phi, 0)
    dR = 999999.0
    for i in range(len(genPt)):
        tmpGen.SetCoordinates(genPt.at(i), genEta.at(i), genPhi.at(i), 0)
        tmpDR = r.Math.VectorUtil.DeltaR(tmpParticle, tmpGen)
        if tmpDR < dR:
            dR = tmpDR
    return dR


def findGenMatch(dR1_tau, dR2_tau, dR1_b, dR2_b, dR1_ele, dR2_ele, dR1_mu, dR2_mu, option = ''):
    #for leg1
    leg1 = sorted([('t',dR1_tau), ('b',dR1_b), ('e',dR1_ele), ('m',dR1_mu)], key=itemgetter(1))    
    #for leg2
    leg2 = sorted([('t',dR2_tau), ('b',dR2_b), ('e',dR2_ele), ('m',dR2_mu)], key=itemgetter(1))
    leg1Match = leg1[0][0]
    leg2Match = leg2[0][0]

    if leg1[0][1] > dR_tauEleMu_max:
        leg1Match = 'x'
    if leg2[0][1] > dR_tauEleMu_max:
        leg2Match = 'x'

    if 'e(tau)' in option:
        if leg1Match == 'e' and leg1[1][0] == 't' and leg1[1][1] < dR_tauEleMu_max:
            leg1Match = 'e(t)'
        if leg2Match == 'e' and leg2[1][0] == 't' and leg2[1][1] < dR_tauEleMu_max:
            leg2Match = 'e(t)'
    
    if 'e(b)' in option:
        if leg1Match == 'e' and leg1[1][0] == 'b' and leg1[1][1] < dR_b_max:
            leg1Match = 'e(b)'
        if leg2Match == 'e' and leg2[1][0] == 'b' and leg2[1][1] < dR_b_max:
            leg2Match = 'e(b)'
        if 'e(tau)' in option:
            if leg1Match == 'e' and leg1[1][0] == 't' and leg1[1][1] < dR_tauEleMu_max:
                leg1Match = 'e(t)'
            if leg2Match == 'e' and leg2[1][0] == 't' and leg2[1][1] < dR_tauEleMu_max:
                leg2Match = 'e(t)'
    
    if 'tau(b)' in option:
        if leg1Match == 'tau':
            if leg1[1][0] == 'b' and leg1[1][1] < dR_b_max:
                leg1Match = 't(b)'
        if leg2Match == 'tau':
            if leg2[1][0] == 'b' and leg2[1][1] < dR_b_max:
                leg2Match = 't(b)'

    stringList = [leg1Match, leg2Match]
    stringList.sort()
    return '%s%s' %(stringList[0], stringList[1])

def passCut(tree, option):
    if 'bTag' in option and (tree.CSVJ1 < 0.68 or tree.CSVJ2 < 0.24):
        return 0
#     if  tree.mJJ<90  or tree.mJJ>140:
#         return 0

    passIso = 0
    passSign = 0
    if 'tight' in option and (tree.iso1.at(0) < 1.5 and tree.iso2.at(0) < 1.5):
            passIso = 1
    if 'relaxed' in option and (tree.iso1.at(0) > 3 and tree.iso2.at(0) > 3):
            passIso = 1
    if 'SS' in option and (tree.charge1.at(0) == tree.charge2.at(0)):
            passSign = 1
    if 'OS' in option and (tree.charge1.at(0) == -tree.charge2.at(0)):
            passSign = 1
    return passIso*passSign

def findMatch(iTree, isData):
    if isData:
        return 'ff'

    matchTuple1 = [iTree.pt1.at(0), iTree.eta1.at(0), iTree.phi1.at(0)]
    matchTuple2 = [iTree.pt2.at(0), iTree.eta2.at(0), iTree.phi2.at(0)]

    dR1_tau = findDR(iTree.genTauPt,iTree.genTauEta,iTree.genTauPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2])
    dR2_tau = findDR(iTree.genTauPt,iTree.genTauEta,iTree.genTauPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2])
    dR1_b = findDR(iTree.genBPt,iTree.genBEta,iTree.genBPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2])
    dR2_b = findDR(iTree.genBPt,iTree.genBEta,iTree.genBPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2])
    dR1_ele = findDR(iTree.genElePt,iTree.genEleEta,iTree.genElePhi,matchTuple1[0],matchTuple1[1],matchTuple1[2])
    dR2_ele = findDR(iTree.genElePt,iTree.genEleEta,iTree.genElePhi,matchTuple2[0],matchTuple2[1],matchTuple2[2])
    dR1_mu = findDR(iTree.genMuPt,iTree.genMuEta,iTree.genMuPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2])
    dR2_mu = findDR(iTree.genMuPt,iTree.genMuEta,iTree.genMuPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2])

    genMatch = findGenMatch(dR1_tau, dR2_tau, dR1_b, dR2_b, dR1_ele, dR2_ele, dR1_mu, dR2_mu)

    return genMatch

fileList = []
for massPoint in makeWholeSample_cfg.trainedMassPoints:
    preFix = '%s%s/ClassApp_both_TMVARegApp_' %(makeWholeSample_cfg.preFix0, massPoint)
#     preFix = makeWholeSample_cfg.preFix0
    for i in range(len(makeWholeSample_cfg.sampleConfigs)):
        fileList.append((makeWholeSample_cfg.sampleConfigs[i][0], 
                         preFix + makeWholeSample_cfg.sampleConfigs[i][1], 
                         makeWholeSample_cfg.sampleConfigs[i][2], 
                         makeWholeSample_cfg.sampleConfigs[i][3]))    

oFileName = makeWholeSample_cfg.oFileName
oFile = r.TFile(oFileName, 'RECREATE')
oTree = r.TTree('eventTree', '')

nMassPoints = len(makeWholeSample_cfg.trainedMassPoints)

nSamples = len(fileList)/nMassPoints

mJJReg = array('f', [0.])
mJJ = array('f', [0.])
svMass = array('f', [0.])
fMass = array('f', [0.])
fMassKinFit = array('f', [0.])
chi2KinFit = array('f', [0.])
CSVJ2 = array('f', [0.])
BDT_QCD = array('f', [0.])
BDT_EWK = array('f', [0.])

triggerEff = array('f', [0.])
sampleName = bytearray(20)
genMatchName = bytearray(3)
initEvents = r.TH1F('initEvents', '', nSamples, 0, nSamples)
xs = r.TH1F('xs', '', nSamples, 0, nSamples)
finalEventsWithXS = r.TH1F('finalEventsWithXS', '', nSamples, 0, nSamples)

svMassRange = [20, 0, 400]
mJJRegRange = [15, 50, 200]
BDTRange = [20, -1.0, 1.0]

BDTs = []
scaleBDTs = []
scaleBDTMCs = []
counter = 0
for iMassPoint in makeWholeSample_cfg.trainedMassPoints:
    BDTs.append(array('f', [0.]))
    scaleBDTs.append(r.TH1F("scaleBDT_%i" %iMassPoint, "", BDTRange[0], BDTRange[1], BDTRange[2]))
    scaleBDTMCs.append(r.TH1F("MC_Data_BDT_%i" %iMassPoint, "", BDTRange[0], BDTRange[1], BDTRange[2]))
    oTree.Branch("BDT_%i" %iMassPoint, BDTs[counter], "BDT_%i/F" %iMassPoint)
    counter += 1


scaleSVMass = r.TH1F("scaleSVMass", "", svMassRange[0], svMassRange[1], svMassRange[2])
scaleSVMassMC = r.TH1F("MC_Data_svMass", "", svMassRange[0], svMassRange[1], svMassRange[2])
scaleMJJReg = r.TH1F("scaleMJJReg", "", mJJRegRange[0], mJJRegRange[1], mJJRegRange[2])
scaleMJJRegMC = r.TH1F("MC_Data_mJJReg", "", mJJRegRange[0], mJJRegRange[1], mJJRegRange[2])

oTree.Branch("mJJReg", mJJReg, "mJJReg/F")
oTree.Branch("mJJ", mJJ, "mJJ/F")
oTree.Branch("fMass", fMass, "fMass/F")
oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
oTree.Branch("svMass", svMass, "svMass/F")
oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")

# oTree.Branch("BDT_QCD", BDT_QCD, "BDT_QCD/F")
# oTree.Branch("BDT_EWK", BDT_EWK, "BDT_EWK/F")

oTree.Branch("triggerEff", triggerEff, "triggerEff/F")
oTree.Branch("sampleName", sampleName, "sampleName[21]/C")
oTree.Branch("genMatchName", genMatchName, "genMatchName[21]/C")

for indexFile in range(nSamples):
    ifiles = []
    iFiles = []
    iTrees = []
    for i in range(nMassPoints):
        if i == 0:
            name = fileList[indexFile][0]
            xsValue = fileList[indexFile][3]
            option = fileList[indexFile][2]
        ifiles.append(fileList[indexFile+i*nSamples][1])
        iFiles.append(r.TFile(ifiles[i]))
        iTrees.append(iFiles[i].Get('eventTree'))

    total = iTrees[0].GetEntries()
    tmpHist = iFiles[0].Get('preselection')
    initEvents.Fill(name, tmpHist.GetBinContent(1))
    isData = False
    if 'data' in name:
        isData = True
    eventsSaved = 0.

    scale = xsValue/tmpHist.GetBinContent(1)*lumi

    if isData:
        xsValue = xsValue*tmpHist.GetBinContent(1)

    for i in range(0, total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %name)
        for iMP in range(nMassPoints):
            iTrees[iMP].GetEntry(i)
        #Fill Histograms
        if passCut(iTrees[0], 'OSrelaxedbTag') and (not ("H2hh" in name)):
            if isData:
                scaleSVMass.Fill(iTrees[0].svMass.at(0), iTrees[0].triggerEff)
                #scaleMJJReg.Fill(iTree.mJJReg, iTree.triggerEff)
                for iMP in range(nMassPoints):
                    scaleBDTs[iMP].Fill(iTrees[iMP].BDT_both, iTrees[iMP].triggerEff)

            else:
                scaleSVMassMC.Fill(iTrees[0].svMass.at(0), iTrees[0].triggerEff*scale)
                #scaleMJJRegMC.Fill(iTree.mJJReg, iTree.triggerEff*scale)
                for iMP in range(nMassPoints):
                    scaleBDTMCs[iMP].Fill(iTrees[iMP].BDT_both, iTrees[iMP].triggerEff*scale)

        if not passCut(iTrees[0], option):
            continue
        mJJReg[0] = iTrees[0].mJJReg
        mJJ[0] = iTrees[0].mJJ
        fMass[0] = iTrees[0].fMass
        fMassKinFit[0] = iTrees[0].fMassKinFit
        chi2KinFit[0] = iTrees[0].chi2KinFit
        svMass[0] = iTrees[0].svMass.at(0)
        CSVJ2[0] = iTrees[0].CSVJ2
        triggerEff[0] = iTrees[0].triggerEff
        sampleName[:21] = name
        genMatchName[:3] = findMatch(iTrees[0], isData)
        for iMP in range(nMassPoints):
            BDTs[iMP][0] = iTrees[iMP].BDT_both
        oTree.Fill()
        eventsSaved += triggerEff[0]

    xs.Fill(name, xsValue)
    finalEventsWithXS.Fill(name, eventsSaved*xsValue/tmpHist.GetBinContent(1)*lumi)
    print ' --- Events Saved: %.2f' %(eventsSaved*xsValue/tmpHist.GetBinContent(1)*lumi) #eventsSaved

scaleSVMass.Sumw2()
scaleSVMassMC.Sumw2()
scaleSVMassMC.Divide(scaleSVMass)

scaleMJJReg.Sumw2()
scaleMJJRegMC.Sumw2()
scaleMJJRegMC.Divide(scaleMJJReg)

oFile.cd()
for iMP in range(nMassPoints):
    scaleBDTs[iMP].Sumw2()
    scaleBDTMCs[iMP].Sumw2()
    scaleBDTMCs[iMP].Divide(scaleBDTs[iMP])
    scaleBDTMCs[iMP].Write()
scaleSVMassMC.Write()
scaleMJJRegMC.Write()
initEvents.Write()
xs.Write()
finalEventsWithXS.Write()
oTree.Write()
oFile.Close()

print 'Combined event saved at: %s' %oFileName



