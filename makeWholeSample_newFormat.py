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
lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
import cutSampleTools 

dR_tauEleMu_max = 0.5
dR_b_max = 0.5
lumi = 19.7
tt_semi_InitEvents = 12011428.

def findDR(genPt, genEta, genPhi, pt, eta, phi, genPtThreshold):
    tmpGen = lvClass()
    tmpParticle = lvClass()
    tmpParticle.SetCoordinates(pt, eta, phi, 0)
    dR = 999999.0
    for i in range(len(genPt)):
        if genPt.at(i) < genPtThreshold:
            continue
        tmpGen.SetCoordinates(genPt.at(i), genEta.at(i), genPhi.at(i), 0)
        tmpDR = r.Math.VectorUtil.DeltaR(tmpParticle, tmpGen)
        if tmpDR < dR:
            dR = tmpDR
    return dR

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

def passJetTrigger(tree):
    return 1
    etas = []
    if tree.HLT_DoubleMediumIsoPFTau35_Trk5_eta2p1_fired or tree.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_fired:
        return 1
    else:
        if tree.J1Pt < 50:
            return 0
        etas.append((abs(tree.J1Eta)))
        if tree.J2Pt > 50:
            etas.append((abs(tree.J2Eta)))
        if tree.J3Pt > 50:
            etas.append((abs(tree.J3Eta)))
        if tree.J4Pt > 50:
            etas.append((abs(tree.J4Eta)))
        if tree.J5Pt > 50:
            etas.append((abs(tree.J5Eta)))
        if tree.J6Pt > 50:
            etas.append((abs(tree.J6Eta)))
        etas.sort()
        if etas[0] < 3.0:
            return 1
        else:
            return 0

def findGenMatch(dR1_tau, dR2_tau, dR1_ele, dR2_ele, dR1_mu, dR2_mu, option = ''):
    #for leg1
    leg1 = sorted([('t',dR1_tau), ('e',dR1_ele), ('m',dR1_mu)], key=itemgetter(1))    
    #for leg2
    leg2 = sorted([('t',dR2_tau), ('e',dR2_ele), ('m',dR2_mu)], key=itemgetter(1))

    if (leg1[0][0] == 't') and (leg1[1][1] > dR_tauEleMu_max):
        leg1Match = leg1[0][0]
    if (leg2[0][0] == 't') and (leg2[1][1] > dR_tauEleMu_max):
        leg2Match = leg2[0][0]

    

    if leg1[0][1] > dR_tauEleMu_max:
        leg1Match = 'x'
    if leg2[0][1] > dR_tauEleMu_max:
        leg2Match = 'x'

    

#     if 'e(tau)' in option:
#         if leg1Match == 'e' and leg1[1][0] == 't' and leg1[1][1] < dR_tauEleMu_max:
#             leg1Match = 'e(t)'
#         if leg2Match == 'e' and leg2[1][0] == 't' and leg2[1][1] < dR_tauEleMu_max:
#             leg2Match = 'e(t)'
    
#     if 'e(b)' in option:
#         if leg1Match == 'e' and leg1[1][0] == 'b' and leg1[1][1] < dR_b_max:
#             leg1Match = 'e(b)'
#         if leg2Match == 'e' and leg2[1][0] == 'b' and leg2[1][1] < dR_b_max:
#             leg2Match = 'e(b)'
#         if 'e(tau)' in option:
#             if leg1Match == 'e' and leg1[1][0] == 't' and leg1[1][1] < dR_tauEleMu_max:
#                 leg1Match = 'e(t)'
#             if leg2Match == 'e' and leg2[1][0] == 't' and leg2[1][1] < dR_tauEleMu_max:
#                 leg2Match = 'e(t)'
#     
#     if 'tau(b)' in option:
#         if leg1Match == 'tau':
#             if leg1[1][0] == 'b' and leg1[1][1] < dR_b_max:
#                 leg1Match = 't(b)'
#         if leg2Match == 'tau':
#             if leg2[1][0] == 'b' and leg2[1][1] < dR_b_max:
#                 leg2Match = 't(b)'

    stringList = [leg1Match, leg2Match]
    stringList.sort()
    return '%s%s' %(stringList[0], stringList[1])

def passMassWindow(svMass, mJJ, fMassKinFit):
    if 90.0 < svMass < 150.0:
        if 70.0 < mJJ < 150.0:
            if fMassKinFit > 10.0:
                return 1
    return 0

def passCut(tree, option, iso, relaxed, rightPair, massWindow = False):
    isoCut = 1.0
    isoMax = 4.0
    CSVL = 0.244
    if tree.CSVJ1 < 0:
        return 0
    if massWindow and (not passMassWindow(tree.svMass.at(rightPair), tree.mJJ, tree.fMassKinFit)):
        return 0
    if relaxed == 'very_relaxed':
        isoCut = 1.5
    if '1To10' in relaxed:
        isoMax = 10.0
        isoCut = 1.0
    if '3To10' in relaxed:
        isoMax = 10.0
        isoCut = 3.0

    if tree.nElectrons > 0 or tree.nMuons > 0:
        return 0
    if tree.pt1.at(rightPair) < 45 or tree.pt2.at(rightPair) < 45:
        return 0
    if 'bTag' in option and (tree.CSVJ1 < 0.679 or tree.CSVJ2 < 0.244):
        return 0
#     if '2M' in option and (tree.CSVJ1 < 0.679 or tree.CSVJ2 < 0.679):
#         return 0
#     if '1M' in option and (tree.CSVJ1 < 0.679 or tree.CSVJ2 > 0.679):
#         return 0
    if ('M' in option) or ('L' in option):
        if tree.CSVJ1 < 0:
            return 0
    if '2M' in option and (tree.NBTags < 2):
        return 0
    if '1M' in option and (tree.NBTags != 1):
        return 0
    if '2L' in option and (tree.CSVJ2 < CSVL):
        return 0
    if '1L' in option and ((tree.CSVJ1 < CSVL) or (tree.CSVJ2 > CSVL)):
        return 0

    passIso = 0
    passSign = 0
    if (tree.iso1.at(rightPair) > isoMax) or (tree.iso2.at(rightPair) > isoMax):
        return 0
    if 'tight' in option and (tree.iso1.at(rightPair) < iso and tree.iso2.at(rightPair) < iso):
        passIso = 1
    if 'relaxed' in option:
        if 'both' in relaxed:
            if tree.iso1.at(rightPair) > isoCut and tree.iso2.at(rightPair) > isoCut:
                passIso = 1
        else:
            if ((tree.iso1.at(rightPair) > isoCut and tree.iso2.at(rightPair) < iso) or (tree.iso2.at(rightPair) > isoCut and tree.iso1.at(rightPair) < iso)):
                passIso = 1
    if 'SS' in option and (tree.charge1.at(rightPair) == tree.charge2.at(rightPair)):
        passSign = 1
    if 'OS' in option and (tree.charge1.at(rightPair) == -tree.charge2.at(rightPair)):
        passSign = 1
    return passIso*passSign

def findMatch(iTree, isData, rightPair):
    if isData:
        return 'ff'

    matchTuple1 = [iTree.pt1.at(rightPair), iTree.eta1.at(rightPair), iTree.phi1.at(rightPair)]
    matchTuple2 = [iTree.pt2.at(rightPair), iTree.eta2.at(rightPair), iTree.phi2.at(rightPair)]

    dR1_tau = findDR(iTree.genTauPt,iTree.genTauEta,iTree.genTauPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2], 18.0)
    dR2_tau = findDR(iTree.genTauPt,iTree.genTauEta,iTree.genTauPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2], 18.0)
#     dR1_b = findDR(iTree.genBPt,iTree.genBEta,iTree.genBPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2], 18.0)
#     dR2_b = findDR(iTree.genBPt,iTree.genBEta,iTree.genBPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2], 18.0)
    dR1_ele = findDR(iTree.genElePt,iTree.genEleEta,iTree.genElePhi,matchTuple1[0],matchTuple1[1],matchTuple1[2], 8.0)
    dR2_ele = findDR(iTree.genElePt,iTree.genEleEta,iTree.genElePhi,matchTuple2[0],matchTuple2[1],matchTuple2[2], 8.0)
    dR1_mu = findDR(iTree.genMuPt,iTree.genMuEta,iTree.genMuPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2], 8.0)
    dR2_mu = findDR(iTree.genMuPt,iTree.genMuEta,iTree.genMuPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2], 8.0)
    genMatch = findGenMatch(dR1_tau, dR2_tau, dR1_ele, dR2_ele, dR1_mu, dR2_mu)
#     genMatch = findGenMatch(dR1_tau, dR2_tau, dR1_b, dR2_b, dR1_ele, dR2_ele, dR1_mu, dR2_mu)

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
iso1 = array('f', [0.])
iso2 = array('f', [0.])

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
L2T_SF = r.TH1F('L2T_SF', '', 1, 0, 1)
MC2Embed2Cat = r.TH1F('MC2Embed2Cat', '', 1, 0, 1)
singleTop = r.TH1F('singleTop', '', 1, 0, 1)
VV = r.TH1F('VV', '', 1, 0, 1)
yieldHistsInMediumCategory = []

WPlusJets = r.TH1F('WPlusJets', '', 1, 0, 1)
singleTopYield = 0.0
WPlusJetsYield = 0.0
VVYield = 0.0

inclusiveYields = {}
catYields = {}
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
oTree.Branch("iso1", iso1, "iso1/F")
oTree.Branch("iso2", iso2, "iso2/F")
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

    if 'emb' in name:
        isEmbed = True
    else:
        isEmbed = False
    if 'inclusive' in name:
        isInclusive = True
    else:
        isInclusive = False
    cat = ''
    region = 'bTag'
    if '1M' in option:
        region = '1M'

    elif '2M' in option:
        region = '2M'
    elif '1L' in option:
        region = '1L'
        cat = '1M'
    elif '2L' in option:
        region = '2L'
        cat = '2M'

    categoryYield = 0.0
    categoryYield2 = 0.0
    inclusiveYield = 0.0
    for i in range(0, total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %name)
        #Fill Histograms
        iTree.GetEntry(i)

        #get the right pair of taus based on isoMin or ptMax
        rightPair = findRightPair(iTree, makeWholeSample_cfg.pairOption)

        if makeWholeSample_cfg.thirdLeptonVeto and (iTree.nElectrons > 0 or iTree.nMuons > 0):
            continue

        #calculate inclusiveYield
        if isEmbed or isInclusive:
            if iTree.HLT_Any == 0:
                continue
            if passCut(iTree, "OStight", iso, makeWholeSample_cfg.relaxed, rightPair):
                if 'data' in iTree.sampleName:
                    inclusiveYield += iTree.triggerEff
                elif isEmbed:
                    inclusiveYield += iTree.triggerEff*iTree.xs*0.983*lumi/tt_semi_InitEvents
                else:
                    if not passJetTrigger(iTree):
                        continue
                    inclusiveYield += iTree.triggerEff*iTree.xs*lumi/(iTree.initEvents+0.0)

        #calculate category yield
        if isEmbed or name == 'singleT' or name =='Electroweak':
            if passCut(iTree, "OStight%s" %cat, iso, makeWholeSample_cfg.relaxed, rightPair, makeWholeSample_cfg.massWindow):
                if isEmbed:
                    if 'data' in iTree.sampleName:
                        categoryYield += iTree.triggerEff
                    else:
                        categoryYield += iTree.triggerEff*iTree.xs*0.983*lumi/tt_semi_InitEvents
                elif name == 'singleT':
                    singleTopYield += iTree.triggerEff*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents
                elif name == 'Electroweak':
                    VVYield += iTree.triggerEff*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents
        if isEmbed:
            if passCut(iTree, option, iso, makeWholeSample_cfg.relaxed, rightPair, makeWholeSample_cfg.massWindow):
                if 'data' in iTree.sampleName:
                    categoryYield2 += iTree.triggerEff
                else:
                    categoryYield2 += iTree.triggerEff*iTree.xs*0.983*lumi/tt_semi_InitEvents
        

        if not passCut(iTree, option, iso, makeWholeSample_cfg.relaxed, rightPair):
            continue
        if (not isEmbed) and (not passJetTrigger(iTree)) and (not isData):
            continue
        mJJ[0] = iTree.mJJ
        fMass[0] = iTree.fMass
        fMassKinFit[0] = iTree.fMassKinFit
        chi2KinFit[0] = iTree.chi2KinFit
        chi2KinFit2[0] = iTree.chi2KinFit2
        svMass[0] = iTree.svMass.at(rightPair)
        iso1[0] = iTree.iso1.at(rightPair)
        iso2[0] = iTree.iso2.at(rightPair)
        CSVJ2[0] = iTree.CSVJ2
        NBTags[0] = int(iTree.NBTags)
        triggerEff[0] = iTree.triggerEff
        if '_semi' not in iTree.sampleName:
            tmpSampleName = iTree.sampleName[0:iTree.sampleName.find('_')]
        else:
            tmpSampleName = iTree.sampleName[0:iTree.sampleName.find('_semi')+5]
        if 'data' in tmpSampleName and (not isEmbed):
            sampleName[:21] = 'dataOSRelax'
            initEvents[0] = 0
            xs[0] = 1.0           
        elif ('data' in tmpSampleName) and isEmbed:
            sampleName[:21] = 'DY_embed'
            initEvents[0] = 19.7
            xs[0] = 1.0            
        elif not isEmbed:
            initEvents[0] = iTree.initEvents
            xs[0] = iTree.xs
            sampleName[:21] = tmpSampleName
            if name == 'MCOSRelax':
                sampleName[:21] = 'MCOSRelax'
        else:
            initEvents[0] = tt_semi_InitEvents
            xs[0] = iTree.xs*0.983
            sampleName[:21] = 'tt_embed'
            
        if tmpSampleName not in initEventsValues.keys():
            if 'data' not in tmpSampleName:
                initEventsValues[tmpSampleName] = iTree.initEvents
                xsValues[tmpSampleName] = iTree.xs
            eventsSaved[tmpSampleName] = 0.0
#         genMatchName[:3] = findMatch(iTree, isData, rightPair)
        if isData:
            PUWeight[0] = 1.0
        else:
            PUWeight[0] = iTree.PUWeight
        oTree.Fill()
        if makeWholeSample_cfg.massWindow and (not passMassWindow(iTree.svMass.at(rightPair), iTree.mJJ, iTree.fMassKinFit)):
            continue
        if isData:
            eventsSaved[tmpSampleName] += 1
            eventsSavedCounter += 1
        elif not isEmbed:
            eventsSaved[tmpSampleName] += triggerEff[0]
            eventsSavedCounter += triggerEff[0]*xsValues[tmpSampleName]/initEventsValues[tmpSampleName]*PUWeight[0]*lumi

    print ' --- Events Saved: %.2f' %(eventsSavedCounter)
    if isEmbed:
        print sampleName
        inclusiveYields[str(sampleName)] =  inclusiveYield
        catYields[str(sampleName)] = categoryYield
        print 'inclusive yield for %s: %.2f' %(str(sampleName), inclusiveYield)
        print 'Medium category yield for %s: %.2f' %(str(sampleName), categoryYield)
        print 'Loose category yield for %s: %.2f' %(str(sampleName), categoryYield2)

    elif isInclusive:
        inclusiveYields['DY_MC'] = inclusiveYield
        print 'inclusive yield for DY_MC: %.2f' %(inclusiveYield)



nSamples = len(initEventsValues.keys())
initEvents = r.TH1F('initEvents', '', nSamples, 0, nSamples)
xsHist = r.TH1F('xs', '', nSamples, 0, nSamples)
finalEventsWithXS = r.TH1F('finalEventsWithXS', '', nSamples, 0, nSamples)

for iKey in initEventsValues.keys():
    if 'data' not in iKey:
        initEvents.Fill(iKey, initEventsValues[iKey])
        xsHist.Fill(iKey, xsValues[iKey])
        finalEventsWithXS.Fill(iKey, eventsSaved[iKey]*xsValues[iKey]/initEventsValues[iKey]*lumi)


# weights = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012', 'tight', makeWholeSample_cfg.relaxed, True, True, iso)
weights = makeWholeTools2.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'SF12', 'tight', makeWholeSample_cfg.relaxed, True, 1.0, makeWholeSample_cfg.pairOption, makeWholeSample_cfg.massWindow)

print weights

if region == "1M" or region == "1L":
    L2T.Fill(0.5, weights[0])
    L2T_SF.Fill(0.5, weights[2])

elif region == "2M" or region == "2L":
    L2T.Fill(0.5, weights[1])
    L2T_SF.Fill(0.5, weights[3])

scaleFactor = inclusiveYields['DY_MC']*(catYields['DY_embed']-catYields['tt_embed'])/(inclusiveYields['DY_embed'] - inclusiveYields['tt_embed'])

MC2Embed2Cat.Fill(0.5, scaleFactor)
singleTop.Fill(0.5, singleTopYield)
WPlusJets.Fill(0.5, WPlusJetsYield)
VV.Fill(0.5, VVYield)

print 'Embed DY prediction: %.2f' %scaleFactor
print 'Single Top prediction: %.2f' %singleTopYield
print 'VV prediction: %.2f' %VVYield

oFile.cd()

initEvents.Write()
xsHist.Write()
L2T.Write()
L2T_SF.Write()
MC2Embed2Cat.Write()
VV.Write()
singleTop.Write()
WPlusJets.Write()
finalEventsWithXS.Write()
oTree.Write()
oFile.Close()

print 'Combined event saved at: %s' %oFileName



