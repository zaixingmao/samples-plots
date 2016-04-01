#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import varsList
import FWCore.ParameterSet.Config as cms
import math
import os
# from makeWholeTools2 import findRightPair
r.gSystem.Load("libFWCoreFWLite.so")
r.AutoLibraryLoader.enable()
# r.gSystem.Load("libPhysicsToolsUtilities.so")

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
combinedJJ = lvClass()
l1 = lvClass()
l2 = lvClass()
l_1 = lvClass()
l_2 = lvClass()
jet = lvClass()
met = lvClass()
deltaTauES = lvClass()

reWeight = 1.0


loose_53X_WP = [
    (0, 2.5, -0.63),
    (2.5, 2.75, -0.60),
    (2.75, 3.0, -0.55),
    (3.0, 5.2, -0.45),
    ]
def pZetaCut(t1, t2, met):
    zetaX = math.cos(t1.phi()) + math.cos(t2.phi())
    zetaY = math.sin(t1.phi()) + math.sin(t2.phi())
    zetaR = math.sqrt(zetaX*zetaX + zetaY*zetaY)
    if zetaR > 0.0:
        zetaX /= zetaR
        zetaY /= zetaR
    pZeta = zetaX*(t1.px() + t2.px() + met.px()) + zetaY*(t1.py() + t2.py() + met.py()) 
    pZetaVis = zetaX*(t1.px() + t2.px()) + zetaY*(t1.py() + t2.py())
    return pZeta - 3.1*pZetaVis

def getNCSVLJets(tree, sys, isData, l1, l2):
    n = 0
    for i in range(1, 9):
        CSVL = 0#getattr(tree, "jet%iCSVL" %i)
        jetPt = getattr(tree, "jet%iPt" %i)
        jetEta = getattr(tree, "jet%iEta" %i)
        if getattr(tree, "jet%iCSVBtag" %i) > 0.605:
            CSVL = 1
        CSVL_old = CSVL
        if not isData:
            if sys == 'bScaleUp':
                CSVL = getattr(tree, "jet%iCSVL_up" %i)
            elif sys == 'bScaleDown':
                CSVL = getattr(tree, "jet%iCSVL_down" %i)
            elif sys == 'jetECUp':
                if hasattr(tree, "jet%iJES_Up" %i):
                    jetPt = getattr(tree, "jet%iJES_Up" %i)
                else:
                    jetPt = getattr(tree, "jet%iEC_up" %i)
            elif sys == 'jetECDown':
                if hasattr(tree, "jet%iJES_Down" %i):
                    jetPt = getattr(tree, "jet%iJES_Down" %i)
                else:
                    jetPt = getattr(tree, "jet%iEC_down" %i)

        if CSVL and  jetPt > 30 and abs(jetEta) < 2.4 and abs(getattr(tree, "jet%iPFJetIDLoose" %i)):
            jet.SetCoordinates(jetPt, 
                               jetEta, 
                               getattr(tree, "jet%iPhi" %i), 
                               0)
            dR_1 = r.Math.VectorUtil.DeltaR(l1, jet)
            if dR_1 <= 0.4:
                continue
            dR_2 = r.Math.VectorUtil.DeltaR(l2, jet)
            if dR_2 > 0.4:
                n += 1
    return n

def eleTrigEff(absEta):
    if absEta <= 1.479:
        return 1.0
    else:
        return 0.93

def puJetId(jetEta, jetFullDiscriminant):
    wp = loose_53X_WP
    for etamin, etamax, cut in wp:
        if not(jetEta>=etamin and jetEta<etamax):
            continue
        return jetFullDiscriminant>cut


def findCategory(csv1, csv2):
    if csv1 < 0.679:
        return 'none'
    elif csv2 > 0.679:
        return '2M'
    else:
        return '1M1NonM'

def setupLumiReWeight():
    location = "%s/pileUp/" %os.path.dirname(os.path.realpath(__file__))
#     location = "/scratch/zmao/CMSSW_5_3_15/src/samples-plots/"
    global reWeight
    reWeight = r.edm.LumiReWeighting("%sMC_50bins.root" %location,"%sdata_50bins.root" %location,"pileup","pileup")
    
def getPUWeight(npu = 0):
    return reWeight.weight(npu)

def freeLumiReWeight():
    global reWeight
    del reWeight

def findRightPair(iChain, iEntry, bestPair, isoValue_1, isoValue, ptValue_1, ptValue, pairChoice = 'pt', FS = 'tt'):
    if FS == 'tt':
        #order by iso
        if iChain.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits <= iChain.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits:
            object_1 = 't1'
            object_2 = 't2'
        else:
            object_1 = 't2'
            object_2 = 't1'
        currentIsoValue_1 = getattr(iChain, "%sByCombinedIsolationDeltaBetaCorrRaw3Hits" %object_1)
        currentPtValue_1 = getattr(iChain, "%sPt" %object_1)
        currentIsoValue = iChain.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits + iChain.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits
        currentPtValue = iChain.t1Pt + iChain.t2Pt
    elif FS == 'et':
        currentIsoValue_1 = iChain.eRelIso
        currentIsoValue = iChain.eRelIso + iChain.tByCombinedIsolationDeltaBetaCorrRaw3Hits
        currentPtValue = iChain.ePt + iChain.tPt
        currentPtValue_1 = iChain.ePt
    elif FS == 'em':
        currentIsoValue_1 = iChain.mRelIso
        currentIsoValue = iChain.eRelIso + iChain.mRelIso
        currentPtValue_1 = iChain.mPt
        currentPtValue = iChain.ePt + iChain.mPt
    elif FS == 'mt':
        currentIsoValue_1 = iChain.mRelIso
        currentIsoValue = iChain.mRelIso + iChain.tByCombinedIsolationDeltaBetaCorrRaw3Hits
        currentPtValue = iChain.mPt + iChain.tPt
        currentPtValue_1 = iChain.mPt
    elif FS == 'ee':
        if iChain.e1RelIso <= iChain.e2RelIso:
            object_1 = 'e1'
            object_2 = 'e2'
        else:
            object_1 = 'e2'
            object_2 = 'e1'
        currentIsoValue_1 = getattr(iChain, "%sRelIso" %object_1)
        currentPtValue_1 = getattr(iChain, "%sPt" %object_1)
        currentIsoValue = iChain.e1RelIso + iChain.e2RelIso
        currentPtValue = iChain.e1Pt + iChain.e2Pt
    elif FS == 'mm':
        if iChain.m1RelIso <= iChain.m2RelIso:
            object_1 = 'm1'
            object_2 = 'm2'
        else:
            object_1 = 'm2'
            object_2 = 'm1'
        currentIsoValue_1 = getattr(iChain, "%sRelIso" %object_1)
        currentPtValue_1 = getattr(iChain, "%sPt" %object_1)
        currentIsoValue = iChain.m1RelIso + iChain.m2RelIso
        currentPtValue = iChain.m1Pt + iChain.m2Pt


    if pairChoice == 'iso':
        # most isolated candidate 1
        if currentIsoValue_1 < isoValue_1:
            return iEntry, currentIsoValue_1, currentIsoValue, currentPtValue_1, currentPtValue
        # highest candidate 1 pt
        elif currentIsoValue_1 == isoValue_1 and currentPtValue_1 > ptValue_1:
            return iEntry, currentIsoValue_1, currentIsoValue, currentPtValue_1, currentPtValue
        # most isolated candidate 2
        elif currentIsoValue_1 == isoValue_1 and currentPtValue_1 == ptValue_1 and currentIsoValue < isoValue:
            return iEntry, currentIsoValue_1, currentIsoValue, currentPtValue_1, currentPtValue
        # highest candidate 1 pt
        elif currentIsoValue_1 == isoValue_1 and currentPtValue_1 == ptValue_1 and currentIsoValue == isoValue and currentPtValue > ptValue:
            return iEntry, currentIsoValue_1, currentIsoValue, currentPtValue_1, currentPtValue
        else:
            return bestPair, isoValue_1, isoValue, ptValue_1, ptValue
    elif pairChoice == 'pt':
        # highest pt candidate 1
        if currentPtValue_1 > ptValue_1:
            return iEntry, currentIsoValue_1, currentIsoValue, currentPtValue_1, currentPtValue
        elif currentPtValue_1 == ptValue_1 and currentPtValue > ptValue:
            return iEntry, currentIsoValue_1, currentIsoValue, currentPtValue_1, currentPtValue
        else:
            return bestPair, isoValue_1, isoValue, ptValue_1, ptValue


def findDR(genPt, genEta, genPhi, pt, eta, phi, genPtThreshold):
    tmpGen = lvClass()
    tmpParticle = lvClass()
    dR = 999999.0
    tmpParticle.SetCoordinates(pt, eta, phi, 0)
    if genPt < genPtThreshold:
        return dR
    tmpGen.SetCoordinates(genPt, genEta, genPhi, 0)
    dR = r.Math.VectorUtil.DeltaR(tmpParticle, tmpGen)
    return dR

def findDR_betweenTau(pt1, eta1, phi1, pt2, eta2, phi2, jpt, jeta, jphi):
    tau1 = lvClass()
    tau2 = lvClass()
    jet = lvClass()
    tau1.SetCoordinates(pt1, eta1, phi1, 0)
    tau2.SetCoordinates(pt2, eta2, phi2, 0)
    jet.SetCoordinates(jpt, jeta, jphi, 0)
    dR1 = r.Math.VectorUtil.DeltaR(tau1, jet)
    dR2 = r.Math.VectorUtil.DeltaR(tau2, jet)
    if dR1 < dR2:
        return dR1
    else:
        return dR2

def findMinDR(genPt, genEta, genPhi, pt, eta, phi, genPtThreshold):
    minDR = 99999.9
    for iGen in range(len(genPt)):
        tmpDR = findDR(genPt.at(iGen), genEta.at(iGen), genPhi.at(iGen), pt, eta, phi, genPtThreshold)
        if tmpDR < minDR:
            minDR = tmpDR
    return minDR

def dR_genLept(genElePt, genEleEta, genElePhi, genMuPt, genMuEta, genMuPhi, pt, eta, phi):
    dR_ele = findMinDR(genPt = genElePt,
                       genEta = genEleEta,
                       genPhi = genElePhi,
                       pt = pt,
                       eta = eta,
                       phi = phi,
                       genPtThreshold = 8.0)
    dR_mu = findMinDR(genPt = genMuPt,
                      genEta = genMuEta,
                      genPhi = genMuPhi,
                      pt = pt,
                      eta = eta,
                      phi = phi,
                      genPtThreshold = 8.0)
    return dR_ele, dR_mu

def getDRs(iChain, bestPair, option = 'all', tauPtThreshold = 18.0):
    dR_tau_leg1 = findDR(genPt = iChain.genVisPt1.at(bestPair),
                         genEta = iChain.genVisEta1.at(bestPair),
                         genPhi = iChain.genVisPhi1.at(bestPair),
                         pt = iChain.pt1.at(bestPair),
                         eta = iChain.eta1.at(bestPair),
                         phi = iChain.phi1.at(bestPair),
                         genPtThreshold = tauPtThreshold)

    dR_tau_leg2 = findDR(genPt = iChain.genVisPt2.at(bestPair),
                         genEta = iChain.genVisEta2.at(bestPair),
                         genPhi = iChain.genVisPhi2.at(bestPair),
                         pt = iChain.pt2.at(bestPair),
                         eta = iChain.eta2.at(bestPair),
                         phi = iChain.phi2.at(bestPair),
                         genPtThreshold = tauPtThreshold)
    if option == 'all':
        dR_ele_leg2, dR_mu_leg2 = dR_genLept(genElePt = iChain.genElePt, 
                                             genEleEta = iChain.genEleEta,
                                             genElePhi = iChain.genElePhi, 
                                             genMuPt = iChain.genMuPt,
                                             genMuEta = iChain.genMuEta,
                                             genMuPhi = iChain.genMuPhi,
                                             pt = iChain.pt2.at(bestPair),
                                             eta = iChain.eta2.at(bestPair),
                                             phi = iChain.phi2.at(bestPair))
        dR_ele_leg1, dR_mu_leg1 = dR_genLept(genElePt = iChain.genElePt, 
                                             genEleEta = iChain.genEleEta,
                                             genElePhi = iChain.genElePhi, 
                                             genMuPt = iChain.genMuPt,
                                             genMuEta = iChain.genMuEta,
                                             genMuPhi = iChain.genMuPhi,
                                             pt = iChain.pt1.at(bestPair),
                                             eta = iChain.eta1.at(bestPair),
                                             phi = iChain.phi1.at(bestPair))
        return dR_tau_leg1, dR_ele_leg1, dR_mu_leg1, dR_tau_leg2, dR_ele_leg2, dR_mu_leg2
    else:
        return dR_tau_leg1, dR_tau_leg2

def getDecayModeWeight(iChain, bestPair):
    weight1 = 1.0
    weight2 = 1.0
    dR_tau_leg1, dR_tau_leg2 = getDRs(iChain, bestPair, 'tau', 0.0)
    if iChain.tauDecayMode1.at(bestPair) == 0 and dR_tau_leg1 < 0.5:
        weight1 = 0.88
    if iChain.tauDecayMode2.at(bestPair) == 0 and dR_tau_leg1 < 0.5:
        weight2 = 0.88
    return weight1, weight2

def passCategory(iChain, separate, pairOption):
    if separate == 'all':
        return True
    elif separate == 'ZTT' and iChain.genTausFromZ < 2:
        return False
    bestPair = findRightPair(iChain, pairOption)
    dR_tau_leg1, dR_ele_leg1, dR_mu_leg1, dR_tau_leg2, dR_ele_leg2, dR_mu_leg2 = getDRs(iChain, bestPair)
    case = ''
    #check if any of the gen particles are within dR < 0.5
    dRs1 = [dR_tau_leg1, dR_ele_leg1, dR_mu_leg1]
    dRs2 = [dR_tau_leg2, dR_ele_leg2, dR_mu_leg2]
    dRs1.sort()
    dRs2.sort()
    if separate == 'ZTT':
        if dRs1[0] < 0.5 and dRs2[0] < 0.5:
            return True
        else:
            return False

    elif separate == 'ZLL':
        #ZL+ZJ case
        if iChain.genTausFromZ < 2:
            return True
        else:
            if dRs1[0] > 0.5 or dRs2[0] > 0.5:
                return True
            else:
                return False

    print 'If it got to this point, check separate option: %s' %separate


def findFullMass(iTree, rightPair = 0, jetsList = [], sv4Vec = '', ptThreshold = 20):
    newList = []
    emptyV4 = lvClass()
    emptyV4.SetCoordinates(0,0,0,0)
    for i in range(len(jetsList)):
        if jetsList[i][1].pt() > ptThreshold and abs(jetsList[i][1].eta()) < 2.4:
            dR = findDR_betweenTau(iTree.pt1.at(rightPair),
                                   iTree.eta1.at(rightPair),
                                   iTree.phi1.at(rightPair),
                                   iTree.pt2.at(rightPair),
                                   iTree.eta2.at(rightPair),
                                   iTree.phi2.at(rightPair), 
                                   jetsList[i][1].pt(),
                                   jetsList[i][1].eta(), 
                                   jetsList[i][1].phi())

            if dR > 0.5:
                if iTree.EVENT == 179372769:
                    print ''
                    print dR, jetsList[i]
                newList.append(jetsList[i])
    newList = sorted(newList, key=itemgetter(0), reverse=True)
    if len(newList) < 2:
        return emptyV4, -1.0, -1.0, emptyV4, emptyV4, 0.0, -1.0, 'J1', 'J1'
#     if newList[1][0] > 0:
    combinedJJ = newList[0][1]+newList[1][1]
    return combinedJJ, newList[0][0], newList[1][0], newList[0][1], newList[1][1], (combinedJJ+sv4Vec).mass(), r.Math.VectorUtil.DeltaR(newList[0][1], newList[1][1]), newList[0][2], newList[1][2]
#     else:
#         return emptyV4, -1.0, -1.0, emptyV4, emptyV4, 0.0, -1.0, 'J1', 'J1'


def findJetPair(iTree, jetsList = [], ptThreshold = 20):
    newList = []
    emptyV4 = lvClass()
    emptyV4.SetCoordinates(0,0,0,0)
    for i in range(len(jetsList)):
        if jetsList[i][1].pt() > ptThreshold and abs(jetsList[i][1].eta()) < 2.4:
            dR = findDR_betweenTau(iTree.t1Pt,
                                   iTree.t1Eta,
                                   iTree.t1Phi,
                                   iTree.t2Pt,
                                   iTree.t2Eta,
                                   iTree.t2Phi, 
                                   jetsList[i][1].pt(),
                                   jetsList[i][1].eta(), 
                                   jetsList[i][1].phi())

            if dR > 0.5:
                newList.append(jetsList[i])
    newList = sorted(newList, key=itemgetter(0), reverse=True)
    if len(newList) < 2:
        return -1.0, -1.0, emptyV4, emptyV4, -9999, -9999
    return newList[0][0], newList[1][0], newList[0][1], newList[1][1], newList[0][2], newList[1][2]


def findGenJet(j1Name, jet1, j2Name, jet2, tChain):
    genJet1 = lvClass()
    genJet2 = lvClass()
    genJet1.SetCoordinates(0,0,0,0)
    genJet2.SetCoordinates(0,0,0,0)
    if j1Name != 'J5' and j1Name != 'J6': 
        pt1, eta1, phi1, mass1 = varsList.findVarInChain_GenJet_speed(tChain, '%s' %j1Name)
        if pt1 > 0 and mass1 > 0:
            genJet1.SetCoordinates(pt1, eta1, phi1, mass1)
    if j2Name != 'J5' and j2Name != 'J6': 
        pt2, eta2, phi2, mass2 = varsList.findVarInChain_GenJet_speed(tChain, '%s' %j2Name)
        if pt2 > 0 and mass2 > 0:
            genJet2.SetCoordinates(pt2, eta2, phi2, mass2)

    dR1 = r.Math.VectorUtil.DeltaR(genJet1, jet1)
    dR2 = r.Math.VectorUtil.DeltaR(genJet2, jet2)
    return dR1, genJet1, dR2, genJet2

def findGenBJet(jet1, jet2, tChain):
    genJet1 = lvClass()
    genJet2 = lvClass()
    genJet1.SetCoordinates(0,0,0,0)
    genJet2.SetCoordinates(0,0,0,0)
    tmpJet = lvClass()
    tmpJet.SetCoordinates(0,0,0,0)
    dR1 = 0.5
    dR2 = 0.5
    for i in range(tChain.genBPt.size()):
        tmpJet.SetCoordinates(tChain.genBPt.at(i), tChain.genBEta.at(i), tChain.genBPhi.at(i), tChain.genBMass.at(i))
        tmpDR1 = r.Math.VectorUtil.DeltaR(tmpJet, jet1)
        if dR1 > tmpDR1:
            dR1 = tmpDR1
            genJet1.SetCoordinates(tChain.genBPt.at(i), tChain.genBEta.at(i), tChain.genBPhi.at(i), tChain.genBMass.at(i))

    for i in range(tChain.genBPt.size()):
        tmpJet.SetCoordinates(tChain.genBPt.at(i), tChain.genBEta.at(i), tChain.genBPhi.at(i), tChain.genBMass.at(i))
        tmpDR2 = r.Math.VectorUtil.DeltaR(tmpJet, jet2)
        if dR2 > tmpDR2 and genJet1 != tmpJet:
            dR2 = tmpDR2
            genJet2.SetCoordinates(tChain.genBPt.at(i), tChain.genBEta.at(i), tChain.genBPhi.at(i), tChain.genBMass.at(i))

    if genJet1 == genJet2:
        print '  WARNING:: Matched to the same b quark (b mass = %.3f)' %genJet2.mass() 
    return dR1, genJet1, dR2, genJet2

def getRegVars(j1Name, j2Name, tChain):
    jet1 = lvClass()
    jet2 = lvClass()

    SoftLep = 0
    PtUncorr1, VtxPt1, Vtx3dL1, Vtx3deL1, ptLeadTrk1, vtxMass1, vtxPt1, Ntot1, SoftLepPt1, SoftLepEta1, SoftLepPhi1, SoftLepPID1, JECUnc1, Et1, Mt1, Pt1, Eta1, Phi1, Mass1, PtUncorr2, VtxPt2, Vtx3dL2, Vtx3deL2, ptLeadTrk2, vtxMass2, vtxPt2, Ntot2, SoftLepPt2, SoftLepEta2, SoftLepPhi2, SoftLepPID2, JECUnc2, Et2, Mt2, Pt2, Eta2, Phi2, Mass2 = varsList.findVarInChain_Data_speed(tChain,j1Name,j2Name)

    jet1.SetCoordinates(Pt1, Eta1, Phi1, 0)
    if SoftLepPID1 == 0:
        SoftLepPtRel1 = 0
        SoftLepdR1 = 0
    else:
        SoftLepPtRel1 = Pt1 - SoftLepPt1
        softLept1 = lvClass()
        softLept1.SetCoordinates(SoftLepPt1, SoftLepEta1, SoftLepPhi1, 0)
        SoftLepdR1 = r.Math.VectorUtil.DeltaR(softLept1, jet1)
        SoftLepPt1 = SoftLepPt1
    if SoftLepPt1 < 0:
        SoftLepPt1 = 0

    jet2.SetCoordinates(Pt2, Eta2, Phi2, 0)
    if SoftLepPID2 == 0:
        SoftLepPtRel2 = 0
        SoftLepdR2 = 0
    else:
        SoftLepPtRel2 = Pt2 - SoftLepPt2
        softLept2 = lvClass()
        softLept2.SetCoordinates(SoftLepPt2, SoftLepEta2, SoftLepPhi2, 0)
        SoftLepdR2 = r.Math.VectorUtil.DeltaR(softLept2, jet2)
        SoftLepPt2 = SoftLepPt2
    if SoftLepPt2 < 0:
        SoftLepPt2 = 0

    return PtUncorr1, Et1, Mt1, ptLeadTrk1, Vtx3dL1,Vtx3deL1, vtxMass1, VtxPt1, JECUnc1, float(Ntot1), SoftLepPtRel1, SoftLepPt1, SoftLepdR1, PtUncorr2, Et2, Mt2, ptLeadTrk2, Vtx3dL2,Vtx3deL2, vtxMass2, VtxPt2, JECUnc2, float(Ntot2), SoftLepPtRel2, SoftLepPt2, SoftLepdR2

def triggerMatch(iTree, channel = 'tt', isData = False):
    HLTandFilter = {}
    HLTandFilter['tt'] = {'doubleTau': ['t1DiPFTau40', 't2DiPFTau40']}

    HLTandFilter['et'] = {# 'eTau': ['eEle22', 'eOverlapEle22', 'tTau20', 'tTauOverlapEle'],
#                           'singleE': ['eSingleEle'],
#                           'singleE22': ['eSingleEle22hlt23'],
                          'singleE27_2p1_WP75': ['eSingleEle27_2p1_WP75'],

                         }

    HLTandFilter['et_data'] = {#'eTau_WPLoose': ['eEle22Loose', 'eOverlapEle22Loose', 'tTau20', 'tTauOverlapEleLoose'],
#                                 'singleETight': ['eSingleEleTight'],
                                'singleE27_2p1_WPLoose': ['eSingleEle27_2p1_WPLoose'],
#                                 'singleE23_WPLoose': ['eSingleEle23_WPLoose'],
                              }

    HLTandFilter['mt'] = {# 'muTau': ['mMuTau', 'mMuTauOverlap', 'tTau20AgainstMuon', 'tTauOverlapMu'],
#                           'singleMu24': ['mIsoMu24'],
                          'singleMu17': ['mIsoMu17hlt18'],

#                           'singleMu27': ['mIsoMu27']
                         }

    HLTandFilter['em'] = {# 'singleMu24': ['mIsoMu24'],
#                           'Mu23e12': ['mMu23El12', 'eMu23El12'],
#                           'Mu8e23': ['mMu8El23', 'eMu8El23'],
#                           'Mu8e17': ['mMu8El17', 'eMu8El17'],
#                           'Mu17e12': ['mMu17El12', 'eMu17El12'],
#                           'singleMu17': ['mIsoMu17hlt18'],
#                           'singleMu27': ['mIsoMu27']
                          'singleE27_2p1_WP75': ['eSingleEle27_2p1_WP75'],
                          }
    HLTandFilter['em_data'] = {# 'singleMu18': ['mIsoMu18'],
                              'singleE27_2p1_WPLoose': ['eSingleEle27_2p1_WPLoose'],
                                }

#     HLTandFilter['em'] = {'Mu30e30': ['mMu30El30_MC', 'eMu30El30']}
#     HLTandFilter['em_data'] = {'Mu30e30': ['mMu30El30_data', 'eMu30El30']}

    HLTandFilter['ee_data'] = {'singleETight': ['e1SingleEleTight'],
                          'singleETight': ['e2SingleEleTight'],
                          'doubleE_WPLoose': ['e1DoubleE_WPLooseLeg1', 'e2DoubleE_WPLooseLeg2'],
                          'doubleE_WPLoose': ['e1DoubleE_WPLooseLeg2', 'e2DoubleE_WPLooseLeg1'],
                          }

    HLTandFilter['ee'] = {'singleE': ['e1SingleEle'],
                          'singleE': ['e2SingleEle'],
                          'doubleE_WP75': ['e1DoubleE_WP75Leg1', 'e2DoubleE_WP75Leg2'],
                          'doubleE_WP75': ['e1DoubleE_WP75Leg2', 'e2DoubleE_WP75Leg1'],
                          }

    HLTandFilter['mm'] = {'singleMu24': ['m1IsoMu24'],
                          'singleMu24': ['m2IsoMu24'],
                          'doubleMu': ['m1MatchesDoubleMu', 'm2MatchesDoubleMu'],
                          }

    if isData:
        if (channel + "_data") in HLTandFilter.keys():
            channel = channel + "_data"

    passSingleTrigger = False
    for iHLT in HLTandFilter[channel].keys():
        if getattr(iTree, '%sPass' %iHLT):
            passFilter = True
            for ihlt_filter in HLTandFilter[channel][iHLT]:
                if not getattr(iTree, '%s' %ihlt_filter):
                    passFilter = False
            if passFilter: #if pass all filters for that HLT
                if 'single' in iHLT:
                    passSingleTrigger = True
                else: #return true if it passed cross trigger
                    if iHLT == 'Mu17e12':
                        if iTree.mPt > 18:
                            return True
                    elif iHLT == 'Mu8e17':
                        if iTree.ePt > 18:
                            return True
                    elif iHLT == 'doubleE_WP75':
                        if (iTree.e1DoubleE_WP75Leg1 and iTree.e2DoubleE_WP75Leg2) or (iTree.e1DoubleE_WP75Leg2 and iTree.e2DoubleE_WP75Leg1):
                            if iTree.e1Pt > 25 and iTree.e2Pt > 25:
                                return True
                    elif iHLT == 'doubleE_WPLoose':
                        if (iTree.e1DoubleE_WPLooseLeg1 and iTree.e2DoubleE_WPLooseLeg2) or (iTree.e1DoubleE_WPLooseLeg2 and iTree.e2DoubleE_WPLooseLeg1):
                            if iTree.e1Pt > 25 and iTree.e2Pt > 25:
                                return True

                    else:
                        return True

    if passSingleTrigger: #if it only passed single lepton trigger
        if 'mt' in channel:
#             return 1 if iTree.mPt > 25.0 else 0
            return 1 if iTree.mPt > 30.0 else 0
        if 'et' in channel:
            return 1 if iTree.ePt > 35.0 else 0
#             return 1 if iTree.ePt > 27.0 else 0
#             return 1 if iTree.ePt > 24.0 else 0
        if 'em' in channel:
            return 1 if iTree.ePt > 35.0 else 0
        if 'ee' in channel:
            if (iTree.e1SingleEle or iTree.e1SingleEleTight) and iTree.e1Pt > 33:
                return 1
            if (iTree.e2SingleEle or iTree.e2SingleEleTight) and iTree.e2Pt > 33:
                return 1
            return 0
        if 'mm' in channel:
            return 1

    return 0

def passCut(iTree, FS, isData = False, sys = ''):
########tt
    if FS == 'tt':
        if not (abs(iTree.t1dZ) < 0.2 and abs(iTree.t2dZ) < 0.2):
            return 0, 'dZ'
        if not triggerMatch(iTree, FS, isData):
            return 0, 'triggerMatch'
        if not (iTree.t1_t2_DR > 0.5):
            return 0, 'dR'
        if (abs(iTree.t1Charge) > 1 or abs(iTree.t2Charge) > 1):
            return 0, 'tauChage'

########et
    elif FS == 'et':
        if not (abs(iTree.tdZ) < 0.2 and abs(iTree.edZ) < 0.2 and abs(iTree.edXY) < 0.045):
            return 0, 'dZ'
        if not (abs(iTree.tEta) < 2.1):
            return 0, 'dZ'
        if sys == '' and iTree.tPt <= 20:
            return 0, 'tauPt'
        if sys == 'tauECUp' and (iTree.tES_up <= 20) and iTree.tIsTauh:
            return 0, 'tauPt'
        if sys == 'tauECUp' and (iTree.tPt <= 20) and (not iTree.tIsTauh):
            return 0, 'tauPt'
        if sys == 'tauECDown' and (iTree.tES_down <= 20) and iTree.tIsTauh:
            return 0, 'tauPt'
        if sys == 'tauECDown' and (iTree.tPt <= 20) and (not iTree.tIsTauh):
            return 0, 'tauPt'
        if not iTree.eMVANonTrigWP80:
            return 0, 'ID'
#         if not iTree.eMVATrigWP80:
#             return 0, 'ID'
#         if not iTree.eCBIDLoose:
#             return 0, 'ID'
#         if not iTree.eCBIDMedium:
#             return 0, 'ID'
#         if not iTree.eCBIDTight:
#             return 0, 'ID'
#         if not iTree.eHEEPIDD:
#             return 0, 'HEEPID'
        if not triggerMatch(iTree, FS, isData):
            return 0, 'triggerMatch'
        if iTree.ePassNumberOfHits == 0:
            return 0, 'eNHits'
        if hasattr(iTree, 'e_passConversionVeto'):
            if not iTree.e_passConversionVeto:
                return 0, 'e_passCov'
        if hasattr(iTree, 'ePassConversionVeto'):
            if not iTree.ePassConversionVeto:
                return 0, 'e_passCov'
        if (iTree.e_t_DR) <= 0.5:
            return 0, 'dR'
        if abs(iTree.tCharge) > 1:
            return 0, 'tauCharge'

########et
    elif FS == 'ee':
        if not (abs(iTree.e1dZ) < 0.2 and abs(iTree.e1dXY) < 0.045 and abs(iTree.e2dZ) < 0.2 and abs(iTree.e2dXY) < 0.045):
            return 0, 'dZ'
        if not (iTree.e1MVANonTrigWP80 and iTree.e2MVANonTrigWP80):
            return 0, 'ID'
#         if not iTree.eHEEPIDD:
#             return 0, 'HEEPID'
        if not triggerMatch(iTree, FS, isData):
            return 0, 'triggerMatch'
        if iTree.e1PassNumberOfHits == 0 or iTree.e2PassNumberOfHits == 0:
            return 0, 'eNHits'
        if not (iTree.e1_passConversionVeto and iTree.e2_passConversionVeto):
                return 0, 'e_passCov'
        if (iTree.e1_e2_DR) <= 0.3:
            return 0, 'dR'

########mt
    elif FS == 'mm':
        if not (abs(iTree.m1dZ) < 0.2 and abs(iTree.m2dZ) < 0.2 and abs(iTree.m1dXY) < 0.045 and abs(iTree.m2dXY) < 0.045):
            return 0, 'dZ'
        if not triggerMatch(iTree, FS, isData):
            return 0, 'triggerMatch'
        if not (iTree.m1_m2_DR > 0.3):
            return 0, 'dR'

########et
    elif FS == 'em':
        if not triggerMatch(iTree, FS, isData):
            return 0, 'triggerMatch'
        if not iTree.eMVANonTrigWP80:
            return 0, 'ID'
#         if not iTree.eMVATrigWP80:
#             return 0, 'ID'
#         if not iTree.ePt > 31:
#             return 0, 'ePt'
#         if not iTree.mPt > 31:
#             return 0, 'mPt'
#         if not iTree.eCBIDLoose:
#             return 0, 'ID'
#         if not iTree.eCBIDMedium:
#             return 0, 'ID'
#         if not iTree.eCBIDTight:
#             return 0, 'ID'
#         if not iTree.eHEEPIDD:
#             return 0, 'HEEPID'
        if not (abs(iTree.mdZ) < 0.2 and abs(iTree.edZ) < 0.2 and abs(iTree.edXY) < 0.045 and abs(iTree.mdXY) < 0.045):
            return 0, 'dZ'
        if iTree.ePassNumberOfHits == 0:
            return 0, 'eNHits'
        if hasattr(iTree, 'e_passConversionVeto'):
            if not iTree.e_passConversionVeto:
                return 0, 'e_passCov'
        if hasattr(iTree, 'ePassConversionVeto'):
            if not iTree.ePassConversionVeto:
                return 0, 'e_passCov'
        if not (iTree.e_m_DR > 0.3):
            return 0, 'dR'
        if not (iTree.mPt > 10):
            return 0, 'mPt'


########mt
    elif FS == 'mt':
        if not (abs(iTree.tdZ) < 0.2 and abs(iTree.mdZ) < 0.2 and abs(iTree.mdXY) < 0.045):
            return 0, 'dZ'
        if not triggerMatch(iTree, FS, isData):
            return 0, 'triggerMatch'
        if not (iTree.m_t_DR > 0.5):
            return 0, 'dR'
        if abs(iTree.tCharge) > 1:
            return 0, 'tauChage'
    return 1, 'passed'

def getCategory(iTree, FS):
    if FS == 'em':
        return 'ZTT'

    elif FS == 'tt':
        if iTree.nPromptTaus == 2:
#         if iTree.isZtautau:
            #require Z -> tau tau at gen level
            return 'ZTT'
        elif (iTree.t1MatchToGenMuPt > 8 and iTree.t2MatchToGenMuPt  > 8) or (iTree.t1MatchToGenElePt > 8 and iTree.t2MatchToGenElePt  > 8):
            #require both reco taus matching to gen Ele/Mu
            return 'ZL'
        else:
            #catch remaining events
            return 'ZJ'

    else: #mt/et case
        if iTree.nPromptTaus == 2 and (iTree.tGenVisPt > 18) and (iTree.tMatchToGenMuPt <= 8) and (iTree.tMatchToGenElePt <= 8):
#         if iTree.isZtautau and (iTree.tGenVisPt > 18) and (iTree.tMatchToGenMu == 0) and (iTree.tMatchToGenEle == 0):
            #require Z -> tau tau at gen level, reco tau matching to gen visTau and not gen Ele/Mu
            return 'ZTT'
        elif iTree.nPromptTaus == 2 and (iTree.tMatchToGenMuPt > 8 or iTree.tMatchToGenElePt > 8):
#         elif iTree.isZtautau and (iTree.tMatchToGenMu > 0 or iTree.tMatchToGenEle > 0):
            #require Z -> tau tau at gen level, reco tau matching to gen Ele/Mu
            return 'ZTT'
        elif (not iTree.nPromptTaus == 2) and ((iTree.tMatchToGenMuPt > 8) or (iTree.tMatchToGenElePt > 8)):
            #require not Z -> tau tau at gen level and reco tau matching to gen Ele/Mu
            return 'ZL'
        else:
            #catch remaining events
            return 'ZJ'

def passAdditionalCuts(iTree, FS, type = 'baseline', isData = False, sys = ''):
########tt
    if FS == 'tt':
        if type == 'inclusive':
#             if (iTree.t1ByTightCombinedIsolationDeltaBetaCorr3Hits < 0.5 or iTree.t2ByTightCombinedIsolationDeltaBetaCorr3Hits < 0.5):
            if (iTree.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits >= 1.0 or iTree.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits >= 1.0):

                return 0, 'iso'
        if type == 'antiIso':
            if (iTree.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1 or iTree.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1):
                return 0, 'antiIso'

        if type != 'baseline':
            if not (iTree.t1AgainstElectronTightMVA5 > 0.5 and iTree.t1AgainstMuonLoose3 > 0.5):
                return 0, 'againstTau1'
            if not (iTree.t2AgainstElectronTightMVA5 > 0.5 and iTree.t2AgainstMuonLoose3 > 0.5):
                return 0, 'againstTau2'
            if (iTree.extraelec_veto > 0 or iTree.extramuon_veto > 0):
                return 0, '3rdLepton'

        if type == 'BSM3G':
            if (iTree.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits >= 10 or iTree.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits >= 10):
                return 0, 'iso'
########et
    elif FS == 'et':
        if type == 'inclusive':
            if (iTree.tByMediumCombinedIsolationDeltaBetaCorr3Hits < 0.5 or iTree.eRelIso >= 0.1):
                return 0, 'iso'
        elif type == 'baseline':
            return 1, 'pass'
        elif type == 'antiIso':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits <= 2 or iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits >= 10 or iTree.eRelIso <= 0.2 or iTree.eRelIso >= 1):
                return 0, 'antiIso'
        elif type == 'notInclusive':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1.5 and iTree.eRelIso <= 0.1):
                return 0, 'notInclusive'
        elif type == 'BSM3G':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits >= 5 or iTree.eRelIso >= 0.15):
                return 0, 'iso'
            if abs(iTree.eEta) >= 2.1 or abs(iTree.tEta) >= 2.1:
                return 0, 'eta'# 
            if iTree.ePt <= 35:
                return 0, 'pt'
        else:
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits >= 10 or iTree.eRelIso >= 0.15):
                return 0, 'iso'
            if abs(iTree.eEta) >= 2.1 or abs(iTree.tEta) >= 2.1:
                return 0, 'eta'# 
            if iTree.ePt <= 35:
                return 0, 'pt'
            met = lvClass()
            l1.SetCoordinates(iTree.ePt, iTree.eEta, iTree.ePhi, iTree.eMass)
            l2.SetCoordinates(iTree.tPt, iTree.tEta, iTree.tPhi, iTree.tMass)

            if sys == 'tauECUp' and iTree.tIsTauh:
                l2.SetCoordinates(iTree.tES_up, iTree.tEta, iTree.tPhi, iTree.tMass)
            elif sys == 'tauECDown' and iTree.tIsTauh:
                l2.SetCoordinates(iTree.tES_down, iTree.tEta, iTree.tPhi, iTree.tMass)

            if sys == 'jetECUp' and not isData:
                met.SetCoordinates(iTree.pfMet_jesUp_Et, 0.0, iTree.pfMet_jesUp_Phi, 0)
            elif sys == 'jetECDown' and not isData:
                met.SetCoordinates(iTree.pfMet_jesDown_Et, 0.0, iTree.pfMet_jesDown_Phi, 0)
            elif (sys == 'tauECDown' or sys == 'tauECUp') and (not isData) and iTree.tIsTauh:
                met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)
                if l2.pt() - iTree.tPt > 0:
                    deltaTauES.SetCoordinates(abs(l2.pt() - iTree.tPt), 0.0, -iTree.tPhi, 0)
                else:
                    deltaTauES.SetCoordinates(abs(l2.pt() - iTree.tPt), 0.0, iTree.tPhi, 0)
                met = met + deltaTauES        
            else:
                met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)

            if type == 'signalRegion':
#                 if sys != '' and iTree.eCharge == iTree.tCharge:
#                         return 0, 'charge'
                if met.pt()  <= 30:
                    return 0, 'met'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'lowMET0B':
                if met.pt()  >= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'signalRegionNoMET':
#                 if met.pt()  <= 30:
#                     return 0, 'met'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'signalRegionNoZeta':
                if met.pt()  <= 30:
                    return 0, 'met'
#                 if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
#                     return 0, 'pZeta'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'signalRegionNoZetaNoCosPhi':
                if met.pt()  <= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'signalRegionNoCosPhi':
                if met.pt()  <= 30:
                    return 0, 'met'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
#                 if math.cos(l1.phi() - l2.phi()) >= -0.95:
#                     return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'signalRegionNoBTag':
                if met.pt()  <= 30:
                    return 0, 'met'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
#                 if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
#                     return 0, 'bTag'

            elif type == 'highMETlowPZeta':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
            elif type == 'highMETlowPZeta0B':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'lowPZeta':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'highMET0BNotSignal':
                if met.pt()  <= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
                if (pZetaCut(l1, l2, met) > -50) and (math.cos(l1.phi() - l2.phi()) < -0.95):#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
            elif type == 'bTagged':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) == 0:
                    return 0, 'bTag'
            elif type == 'cosPhi':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(l1.phi() - l2.phi()) < -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'signalRegionBTagged':
                if met.pt()  <= 30:
                    return 0, 'met'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if getNCSVLJets(iTree, sys, isData, l1, l2) == 0:
                    return 0, 'bTag'

            if type == 'signalRegionNoMETreversePZeta':
                if iTree.eCharge == iTree.tCharge:
                    return 0, 'charge'
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'lowMET0B':
                if met.pt()  >= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'WJetsControlRegion':
                if met.pt()  <= 30:
                    return 0, 'met'
                if (pZetaCut(l1, l2, met) >= -50) and (math.cos(iTree.ePhi - iTree.tPhi) <= -0.95):
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'

        if type != 'baseline' and type != 'notInclusive':
            if not (iTree.tAgainstElectronTightMVA5 > 0.5 and iTree.tAgainstMuonLoose3 > 0.5):
                return 0, 'tauAgainst'
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits >= 10):
                return 0, 'iso'
            if (iTree.extraelec_veto > 1 or iTree.extramuon_veto > 0 or iTree.diElectron_veto > 0):
                return 0, '3rdLepton'

########em
    elif FS == 'em':
        if type == 'inclusive':
            if (iTree.mRelIso >= 0.15 or iTree.eRelIso >= 0.15):
                return 0, 'iso'
        elif type == 'antiIso':
            if (iTree.mRelIso <= 0.2 or iTree.mRelIso >= 1 or iTree.eRelIso <= 0.2 or iTree.eRelIso >= 1):
                return 0, 'antiIso'
        elif type == 'antiEIso':
            if (iTree.mRelIso >= 0.15 or iTree.eRelIso <= 0.2 or iTree.eRelIso >= 1):
                return 0, 'antiEIso'
        elif type == 'antiMIso':
            if (iTree.mRelIso <= 0.2 or iTree.mRelIso >= 1 or iTree.eRelIso >= 0.15):
                return 0, 'antiMIso'
        elif type == 'notInclusive':
            if (iTree.mRelIso <= 0.15 and iTree.eRelIso <= 0.15):
                return 0, 'antiMIso'
        elif type == 'BSM3G':
            if (iTree.eRelIso >= 0.15 or iTree.mRelIso >= 1.0):
                return 0, 'iso'
            if abs(iTree.eEta) >= 2.1 or abs(iTree.mEta) >= 2.1:
                return 0, 'eta'
        else:
            if (iTree.eRelIso >= 0.15 or iTree.mRelIso >= 1.0):
                return 0, 'iso'
            if abs(iTree.eEta) >= 2.1 or abs(iTree.mEta) >= 2.1:
                return 0, 'eta'
            met = lvClass()
            if sys == 'jetECUp' and not isData:
                met.SetCoordinates(iTree.pfMet_jesUp_Et, 0.0, iTree.pfMet_jesUp_Phi, 0)
            elif sys == 'jetECDown' and not isData:
                met.SetCoordinates(iTree.pfMet_jesDown_Et, 0.0, iTree.pfMet_jesDown_Phi, 0)   
            else:
                met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)

            l1.SetCoordinates(iTree.ePt, iTree.eEta, iTree.ePhi, iTree.eMass)
            l2.SetCoordinates(iTree.mPt, iTree.mEta, iTree.mPhi, iTree.mMass)
            if type == 'signalRegion':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(iTree.mPhi - iTree.ePhi) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'lowMET0B':
                if met.pt()  >= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'signalRegionNoMET':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
#                 if met.pt()  <= 30:
#                     return 0, 'met'
                if math.cos(iTree.mPhi - iTree.ePhi) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'signalRegionNoZeta':
#                 if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
#                     return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(iTree.mPhi - iTree.ePhi) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'signalRegionNoZetaNoCosPhi':
                if met.pt()  <= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'signalRegionNoCosPhi':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
#                 if math.cos(iTree.mPhi - iTree.ePhi) >= -0.95:
#                     return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'signalRegionNoBTag':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(iTree.mPhi - iTree.ePhi) >= -0.95:
                    return 0, 'phi'
#                 if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
#                     return 0, 'bTag'


            elif type == 'highMETlowPZeta':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
            elif type == 'highMETlowPZeta0B':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'lowPZeta':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(iTree.mPhi - iTree.ePhi) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'lowMET':
                if met.pt()  >= 30:
                    return 0, 'met'
            elif type == 'bTagged':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(iTree.mPhi - iTree.ePhi) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) == 0:
                    return 0, 'bTag'
            elif type == 'cosPhi':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(iTree.mPhi - iTree.ePhi) < -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'signalRegionBTagged':
                if met.pt()  <= 30:
                    return 0, 'met'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if getNCSVLJets(iTree, sys, isData, l1, l2) == 0:
                    return 0, 'bTag'
        if type != 'baseline' and type != 'notInclusive':
            if (iTree.extraelec_veto > 1 or iTree.extramuon_veto > 1):
                return 0, '3rdLepton'

########em
    elif FS == 'ee':
        if type == 'inclusive':
            if (iTree.e1RelIso >= 0.10 or iTree.e2RelIso >= 0.1):
                return 0, 'iso'
            if (abs(iTree.e1Eta) >= 2.1 or abs(iTree.e2Eta) >= 2.1):
                return 0, 'eta'
        if type != 'baseline':
            if iTree.extramuon_veto > 1:
                return 0, '3rdLepton'

########em
    elif FS == 'mm':
        if type == 'inclusive':
            if (iTree.m1RelIso >= 0.15 or iTree.m1RelIso >= 0.15):
                return 0, 'iso'
        if type != 'baseline':
            if iTree.extraelec_veto > 1:
                return 0, '3rdLepton'

########mt
    elif FS == 'mt':
        if type == 'inclusive':
            if (iTree.tByMediumCombinedIsolationDeltaBetaCorr3Hits < 0.5 or iTree.mRelIso >= 0.1):
                return 0, 'iso'
        if type == 'antiIso':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1.5 or iTree.mRelIso <= 0.1):
                return 0, 'antiIso'
        if type == 'antiTauIso':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1.5 or iTree.mRelIso >= 0.1):
                return 0, 'antiTauIso'
        if type == 'signalRegion' or type == 'highMETlowPZeta' or type == 'lowPZeta' or type == 'bTagged' or type == 'cosPhi' or type == 'highMETlowPZeta0B' or type == 'signalRegionBTagged' or type == 'signalRegionNoMET' or type == 'signalRegionNoMETreversePZeta':
#             if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits >= 10 or iTree.mRelIso >= 0.15):
#                 return 0, 'iso'
            if abs(iTree.mEta) >= 2.1 or abs(iTree.tEta) >= 2.1:
                return 0, 'eta'# 
            if iTree.mPt <= 30:
                return 0, 'pt'
            if iTree.tPt <= 20:
                return 0, 'pt'
            met = lvClass()
            l1.SetCoordinates(iTree.mPt, iTree.mEta, iTree.mPhi, iTree.mMass)
            l2.SetCoordinates(iTree.tPt, iTree.tEta, iTree.tPhi, iTree.tMass)

            if sys == 'tauECUp' and iTree.tIsTauh:
                l2.SetCoordinates(iTree.tES_up, iTree.tEta, iTree.tPhi, iTree.tMass)
            elif sys == 'tauECDown' and iTree.tIsTauh:
                l2.SetCoordinates(iTree.tES_down, iTree.tEta, iTree.tPhi, iTree.tMass)

            if sys == 'jetECUp' and not isData:
                met.SetCoordinates(iTree.pfMet_jesUp_Et, 0.0, iTree.pfMet_jesUp_Phi, 0)
            elif sys == 'jetECDown' and not isData:
                met.SetCoordinates(iTree.pfMet_jesDown_Et, 0.0, iTree.pfMet_jesDown_Phi, 0)
            elif (sys == 'tauECDown' or sys == 'tauECUp') and (not isData) and iTree.tIsTauh:
                met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)
                if l2.pt() - iTree.tPt > 0:
                    deltaTauES.SetCoordinates(abs(l2.pt() - iTree.tPt), 0.0, -iTree.tPhi, 0)
                else:
                    deltaTauES.SetCoordinates(abs(l2.pt() - iTree.tPt), 0.0, iTree.tPhi, 0)
                met = met + deltaTauES        
            else:
                met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)

            if type == 'signalRegion':
                if sys != '' and iTree.mCharge == iTree.tCharge:
                        return 0, 'charge'
                if met.pt()  <= 30:
                    return 0, 'met'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'highMETlowPZeta':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
            elif type == 'highMETlowPZeta0B':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'lowPZeta':
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            elif type == 'bTagged':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(l1.phi() - l2.phi()) >= -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) == 0:
                    return 0, 'bTag'
            elif type == 'cosPhi':
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if met.pt()  <= 30:
                    return 0, 'met'
                if math.cos(l1.phi() - l2.phi()) < -0.95:
                    return 0, 'phi'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'signalRegionBTagged':
                if met.pt()  <= 30:
                    return 0, 'met'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if getNCSVLJets(iTree, sys, isData, l1, l2) == 0:
                    return 0, 'bTag'
            if type == 'signalRegionNoMET':
                if iTree.mCharge == iTree.tCharge:
                    return 0, 'charge'
                if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'
            if type == 'signalRegionNoMETreversePZeta':
                if iTree.mCharge == iTree.tCharge:
                    return 0, 'charge'
                if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                    return 0, 'pZeta'
                if getNCSVLJets(iTree, sys, isData, l1, l2) >= 1:
                    return 0, 'bTag'




        if type != 'baseline':
            if (iTree.tAgainstElectronVLooseMVA5 == 0 or iTree.tAgainstMuonTight3 == 0):
                return 0, 'tauAgainst'
            if ((iTree.extraelec_veto > 0) or (iTree.extramuon_veto > 1) or (iTree.diMuon_veto > 0)):
                return 0, '3rdLepton'
        if type == 'BSM3G':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits >= 10 or iTree.mRelIso >= 0.1):
                return 0, 'iso'
    return 1,'passed'


def passCatSelection(iTree, category, FS):
    if category == 'all':
        return 1
    if getCategory(iTree, FS) == category:
        return 1
    else:
        return 0

def setDPhiInRange(dPhi):
    if dPhi > 3.14:
        return 6.283-dPhi
    else:
        return dPhi

def calcdPhiMetValues(tau1Phi, tau2Phi, j1Phi, j2Phi, metPhi, tauTauPhi, jjPhi, svPhi):
    return setDPhiInRange(abs(tau1Phi - metPhi)), setDPhiInRange(abs(tau2Phi - metPhi)), setDPhiInRange(abs(j1Phi - metPhi)), setDPhiInRange(abs(j2Phi - metPhi)), setDPhiInRange(abs(tauTauPhi - metPhi)), setDPhiInRange(abs(jjPhi - metPhi)),  setDPhiInRange(abs(svPhi - metPhi)) 
