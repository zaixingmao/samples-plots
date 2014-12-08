#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array
import makeWholeSample_cfg
import makeWholeTools
lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
import cutSampleTools 

dR_tauEleMu_max = 0.2
dR_b_max = 0.5
lumi = 19.7

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

def passCut(tree, option, iso, relaxed):
    isoCut = 3.0
    isoMax = 10.0
    if relaxed == 'very_relaxed':
        isoCut = 1.5
    if 'INFN' in relaxed:
        isoMax = 4.0
        isoCut = 1.0
    if tree.pt1.at(0) < 45 or tree.pt2.at(0) < 45:
        return 0
    if 'bTag' in option and (tree.CSVJ1 < 0.679 or tree.CSVJ2 < 0.244):
        return 0
#     if '2M' in option and (tree.CSVJ1 < 0.679 or tree.CSVJ2 < 0.679):
#         return 0
#     if '1M' in option and (tree.CSVJ1 < 0.679 or tree.CSVJ2 > 0.679):
#         return 0
    if '2M' in option and (tree.NBTags < 2):
        return 0
    if '1M' in option and (tree.NBTags != 1):
        return 0
    passIso = 0
    passSign = 0
    if (tree.iso1.at(0) > isoMax) or (tree.iso2.at(0) > isoMax):
        return 0
    if 'tight' in option and (tree.iso1.at(0) < iso and tree.iso2.at(0) < iso):
            passIso = 1
    if 'relaxed' in option and (tree.iso1.at(0) > isoCut and tree.iso2.at(0) > isoCut):
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
preFix = '%s' %makeWholeSample_cfg.preFix0
for i in range(len(makeWholeSample_cfg.sampleConfigs)):
    fileList.append((makeWholeSample_cfg.sampleConfigs[i][0], 
                    preFix + makeWholeSample_cfg.sampleConfigs[i][1], 
                    makeWholeSample_cfg.sampleConfigs[i][2]))    

oFileName = makeWholeSample_cfg.oFileName
oFile = r.TFile(oFileName, 'RECREATE')
oTree = r.TTree('eventTree', '')
iso = makeWholeSample_cfg.iso
nSamples = len(fileList)

mJJ = array('f', [0.])
svMass = array('f', [0.])
fMass = array('f', [0.])
fMassKinFit = array('f', [0.])
chi2KinFit = array('f', [0.])
chi2KinFit2 = array('f', [0.])
PUWeight = array('f', [0.])
CSVJ2 = array('f', [0.])
NBTags = array('i', [0])

triggerEff = array('f', [0.])
sampleName = bytearray(20)
genMatchName = bytearray(3)
xs = array('f', [0.])
initEvents = array('f', [0.])

xsValues = {}
initEventsValues = {}
eventsSaved = {}
L2T = r.TH1F('L2T', '', 1, 0, 1)


svMassRange = [20, 0, 400]
L2T_value = 0


oTree.Branch("mJJ", mJJ, "mJJ/F")
oTree.Branch("fMass", fMass, "fMass/F")
oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
oTree.Branch("chi2KinFit2", chi2KinFit2, "chi2KinFit2/F")
oTree.Branch("xs", xs, "xs/F")
oTree.Branch("initEvents", initEvents, "initEvents/F")
oTree.Branch("NBTags", NBTags, "NBTags/I")

oTree.Branch("svMass", svMass, "svMass/F")
oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")

oTree.Branch("triggerEff", triggerEff, "triggerEff/F")
oTree.Branch("PUWeight", PUWeight, "PUWeight/F")

oTree.Branch("sampleName", sampleName, "sampleName[21]/C")
oTree.Branch("genMatchName", genMatchName, "genMatchName[21]/C")

for indexFile in range(nSamples):
    eventsSavedCounter = 0.0
    name = fileList[indexFile][0]
    option = fileList[indexFile][2]
    iFile =  r.TFile(fileList[indexFile][1])
    iTree = iFile.Get('eventTree')

    total = iTree.GetEntries()
    isData = False
    if 'data' in name:
        isData = True

    region = 'bTag'
    if '1M' in option:
        region = '1M'
    elif '2M' in option:
        region = '2M'


    for i in range(0, total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %name)
        #Fill Histograms
        iTree.GetEntry(i)
        if makeWholeSample_cfg.thirdLeptonVeto and (iTree.nElectrons > 0 or iTree.nMuons > 0):
            continue
        if not passCut(iTree, option, iso, makeWholeSample_cfg.relaxed):
            continue
        mJJ[0] = iTree.mJJ
        fMass[0] = iTree.fMass
        fMassKinFit[0] = iTree.fMassKinFit
        chi2KinFit[0] = iTree.chi2KinFit
        chi2KinFit2[0] = iTree.chi2KinFit2
        svMass[0] = iTree.svMass.at(0)
        CSVJ2[0] = iTree.CSVJ2
        NBTags[0] = int(iTree.NBTags)
        triggerEff[0] = iTree.triggerEff
        if '_semi' not in iTree.sampleName:
            tmpSampleName = iTree.sampleName[0:iTree.sampleName.find('_')]
        else:
            tmpSampleName = iTree.sampleName[0:iTree.sampleName.find('_semi')+5]
        if 'data' in tmpSampleName:
            sampleName[:21] = 'dataOSRelax'
            initEvents[0] = 0
            xs[0] = 1.0            
        else:
            initEvents[0] = iTree.initEvents
            xs[0] = iTree.xs
            sampleName[:21] = tmpSampleName
        if tmpSampleName not in initEventsValues.keys():
            if 'data' not in tmpSampleName:
                initEventsValues[tmpSampleName] = iTree.initEvents
                xsValues[tmpSampleName] = iTree.xs
            eventsSaved[tmpSampleName] = 0.0
        genMatchName[:3] = findMatch(iTree, isData)
        if isData:
            PUWeight[0] = 1.0
        else:
            PUWeight[0] = iTree.PUWeight
        oTree.Fill()
        if isData:
            eventsSaved[tmpSampleName] += 1
            eventsSavedCounter += 1
        else:
            eventsSaved[tmpSampleName] += triggerEff[0]
            eventsSavedCounter += triggerEff[0]*xsValues[tmpSampleName]/initEventsValues[tmpSampleName]*lumi
    print ' --- Events Saved: %.2f' %(eventsSavedCounter)



nSamples = len(initEventsValues.keys())
initEvents = r.TH1F('initEvents', '', nSamples, 0, nSamples)
xsHist = r.TH1F('xs', '', nSamples, 0, nSamples)
finalEventsWithXS = r.TH1F('finalEventsWithXS', '', nSamples, 0, nSamples)

for iKey in initEventsValues.keys():
    if 'data' not in iKey:
        initEvents.Fill(iKey, initEventsValues[iKey])
        xsHist.Fill(iKey, xsValues[iKey])
        finalEventsWithXS.Fill(iKey, eventsSaved[iKey]*xsValues[iKey]/initEventsValues[iKey]*lumi)


weights = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012', 'tight', makeWholeSample_cfg.relaxed, True, True, iso)

if region == "2M":
    L2T.Fill(0.5, weights[2])
elif region == "1M":
    L2T.Fill(0.5, weights[1])


oFile.cd()

initEvents.Write()
xsHist.Write()
L2T.Write()
finalEventsWithXS.Write()
oTree.Write()
oFile.Close()

print 'Combined event saved at: %s' %oFileName


