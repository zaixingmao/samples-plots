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
reWeight = 1.0


loose_53X_WP = [
    (0, 2.5, -0.63),
    (2.5, 2.75, -0.60),
    (2.75, 3.0, -0.55),
    (3.0, 5.2, -0.45),
    ]

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
    reWeight = r.edm.LumiReWeighting("%sMC_75bins.root" %location,"%sdata_75bins_69200.root" %location,"pileup","pileup")
    
def getPUWeight(npu = 0):
#    if npu < 6:
#        npu = 6
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

    HLTandFilter['et'] = {'eTau': ['eEle22', 'eOverlapEle22', 'tTau20', 'tTauOverlapEle'],
                          'singleE': ['eSingleEle']}

    HLTandFilter['et_data'] = {'eTau_WPLoose': ['eEle22Loose', 'eOverlapEle22Loose', 'tTau20', 'tTauOverlapEleLoose'],
                                'singleETight': ['eSingleEleTight']}

    HLTandFilter['mt'] = {'muTau': ['mMuTau', 'mMuTauOverlap', 'tTau20AgainstMuon', 'tTauOverlapMu'],
                          'singleMu24': ['mIsoMu24'],
#                           'singleMu27': ['mIsoMu27']
                         }

    HLTandFilter['em'] = {'Mu23e12': ['mMu23El12', 'eMu23El12'],
                          'Mu8e23': ['mMu8El23', 'eMu8El23'],
#                           'singleMu24': ['mIsoMu24'],
#                           'singleMu27': ['mIsoMu27']
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
                    if iHLT == 'Mu23e12':
                        if iTree.mPt > 24:
                            return True
                    elif iHLT == 'Mu8e23':
                        if iTree.ePt > 24:
                            return True
                    else:
                        return True

    if passSingleTrigger: #if it only passed single lepton trigger
        if 'em' in channel:
            return 1 if iTree.mPt > 24.0 else 0
        if 'mt' in channel:
            return 1 if iTree.mPt > 25.0 else 0
        if 'et' in channel:
            return 1 if iTree.ePt > 33.0 else 0

    return 0

def passCut(iTree, FS, isData = False):
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
    elif FS == 'em':
        if not triggerMatch(iTree, FS, isData):
            return 0, 'triggerMatch'
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

#     for iCut in cuts.keys():
#         if not cuts[iCut]:
#             return False, iCut
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

def passAdditionalCuts(iTree, FS, type = 'baseline', isData = False):
########tt
    if FS == 'tt':
        if type == 'inclusive':
            if (iTree.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits >= 1 or iTree.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits >= 1):
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
########et
    elif FS == 'et':
        if type == 'inclusive':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits >= 1.5 or iTree.eRelIso >= 0.1):
                return 0, 'iso'
        if type == 'antiIso':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1.5 or iTree.eRelIso <= 0.1):
                return 0, 'antiIso'
        if type == 'antiTauIso':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1.5 or iTree.eRelIso >= 0.1):
                return 0, 'antiTauIso'

        if type != 'baseline':
#             if not (iTree.tAgainstElectronTightMVA5 > 0.5 and iTree.tAgainstMuonLoose3 > 0.5):
            if not (iTree.tAgainstElectronVLooseMVA5 > 0.5 and iTree.tAgainstMuonLoose3 > 0.5):
                return 0, 'tauAgainst'
            if (iTree.extraelec_veto > 1 or iTree.extramuon_veto > 0 or iTree.diElectron_veto > 0):
                return 0, '3rdLepton'

########et
    elif FS == 'em':
        if type == 'inclusive':
            if (iTree.mRelIso >= 0.15 or iTree.eRelIso >= 0.15):
                return 0, 'iso'
        if type == 'antiIso':
            if (iTree.mRelIso <= 0.15 or iTree.eRelIso <= 0.15):
                return 0, 'antiIso'
        if type != 'baseline':
            if (iTree.extraelec_veto > 1 or iTree.extramuon_veto > 1):
                return 0, '3rdLepton'

########mt
    elif FS == 'mt':
        if type == 'inclusive':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits >= 1.5 or iTree.mRelIso >= 0.1):
                return 0, 'iso'
        if type == 'antiIso':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1.5 or iTree.mRelIso <= 0.1):
                return 0, 'antiIso'
        if type == 'antiTauIso':
            if (iTree.tByCombinedIsolationDeltaBetaCorrRaw3Hits <= 1.5 or iTree.mRelIso >= 0.1):
                return 0, 'antiTauIso'
        if type != 'baseline':
#             if (iTree.tAgainstElectronVLooseMVA5 == 0 or iTree.tAgainstMuonTight3 == 0):
            if (iTree.tAgainstElectronVLooseMVA5 == 0 or iTree.tAgainstMuonLoose3 == 0):
                return 0, 'tauAgainst'
            if ((iTree.extraelec_veto > 0) or (iTree.extramuon_veto > 1) or (iTree.diMuon_veto > 0)):
                return 0, '3rdLepton'
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
