#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import varsList
import FWCore.ParameterSet.Config as cms
import math
import os

r.gSystem.Load("libFWCoreFWLite.so")
r.AutoLibraryLoader.enable()
# r.gSystem.Load("libPhysicsToolsUtilities.so")

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
combinedJJ = lvClass()
reWeight = 1.0

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
    reWeight = r.edm.LumiReWeighting("%sMC_Summer12_PU_S10-600bins.root" %location,"%sData_Pileup_2012_ReReco-600bins.root" %location,"pileup","pileup")
    
def getPUWeight(npu = 0):
    return reWeight.weight(npu)

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

def findMinDR(genPt, genEta, genPhi, pt, eta, phi, genPtThreshold):
    minDR = 99999.9
    for iGen in range(len(genPt)):
        tmpDR = findDR(genPt.at(iGen), genEta.at(iGen), genPhi.at(iGen), pt, eta, phi, genPtThreshold)
        if tmpDR < minDR:
            minDR = tmpDR
    return minDR

def findBestPair(iChain):
    iPair = 0
    minIso = 9999.
    for i in range(len(iChain.iso1)):
        if iChain.iso1.at(i) + iChain.iso2.at(i) < minIso:
            minIso = iChain.iso1.at(i) + iChain.iso2.at(i)
            iPair = i
    return iPair

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

def getDRs(iChain):
    bestPair = findBestPair(iChain)
    dR_tau_leg1 = findDR(genPt = iChain.genVisPt1.at(bestPair),
                         genEta = iChain.genVisEta1.at(bestPair),
                         genPhi = iChain.genVisPhi1.at(bestPair),
                         pt = iChain.pt1.at(bestPair),
                         eta = iChain.eta1.at(bestPair),
                         phi = iChain.phi1.at(bestPair),
                         genPtThreshold = 18.0)

    dR_ele_leg1, dR_mu_leg1 = dR_genLept(genElePt = iChain.genElePt, 
                                         genEleEta = iChain.genEleEta,
                                         genElePhi = iChain.genElePhi, 
                                         genMuPt = iChain.genMuPt,
                                         genMuEta = iChain.genMuEta,
                                         genMuPhi = iChain.genMuPhi,
                                         pt = iChain.pt1.at(bestPair),
                                         eta = iChain.eta1.at(bestPair),
                                         phi = iChain.phi1.at(bestPair))

    dR_tau_leg2 = findDR(genPt = iChain.genVisPt2.at(bestPair),
                         genEta = iChain.genVisEta2.at(bestPair),
                         genPhi = iChain.genVisPhi2.at(bestPair),
                         pt = iChain.pt2.at(bestPair),
                         eta = iChain.eta2.at(bestPair),
                         phi = iChain.phi2.at(bestPair),
                         genPtThreshold = 18.0)

    dR_ele_leg2, dR_mu_leg2 = dR_genLept(genElePt = iChain.genElePt, 
                                         genEleEta = iChain.genEleEta,
                                         genElePhi = iChain.genElePhi, 
                                         genMuPt = iChain.genMuPt,
                                         genMuEta = iChain.genMuEta,
                                         genMuPhi = iChain.genMuPhi,
                                         pt = iChain.pt2.at(bestPair),
                                         eta = iChain.eta2.at(bestPair),
                                         phi = iChain.phi2.at(bestPair))

    return dR_tau_leg1, dR_ele_leg1, dR_mu_leg1, dR_tau_leg2, dR_ele_leg2, dR_mu_leg2



def passCategory(iChain, separate):
    if separate == 'all':
        return True
    elif separate == 'ZTT' and iChain.genTausFromZ < 2:
        return False
    dR_tau_leg1, dR_ele_leg1, dR_mu_leg1, dR_tau_leg2, dR_ele_leg2, dR_mu_leg2 = getDRs(iChain)
    #check if any of the gen particles are within dR < 0.5
    dRs = [dR_tau_leg1, dR_ele_leg1, dR_mu_leg1, dR_tau_leg2, dR_ele_leg2, dR_mu_leg2]
    dRs.sort()
    if dRs[0] < 0.5 and separate == 'ZTT':
        return True
    elif dRs[0] >= 0.5 and separate == 'ZTT':
        return False
    elif dRs[0] >= 0.5 and separate == 'ZLL':
        return True
    if separate == 'ZLL':
        if iChain.genTausFromZ < 2:
            return True
        else:
            return False
    print 'If it got to this point, check separate option: %s' %separate


def findFullMass(jetsList = [], sv4Vec = '', ptThreshold = 20):
    newList = []
    emptyV4 = lvClass()
    emptyV4.SetCoordinates(0,0,0,0)
    for i in range(len(jetsList)):
        if jetsList[i][1].pt() > ptThreshold and abs(jetsList[i][1].eta()) < 2.4:
            newList.append(jetsList[i])
    newList = sorted(newList, key=itemgetter(0), reverse=True)
    if len(newList) < 2:
        return emptyV4, -1.0, -1.0, emptyV4, emptyV4, 0.0, -1.0, 'J1', 'J1'
#     if newList[1][0] > 0:
    combinedJJ = newList[0][1]+newList[1][1]
    return combinedJJ, newList[0][0], newList[1][0], newList[0][1], newList[1][1], (combinedJJ+sv4Vec).mass(), r.Math.VectorUtil.DeltaR(newList[0][1], newList[1][1]), newList[0][2], newList[1][2]
#     else:
#         return emptyV4, -1.0, -1.0, emptyV4, emptyV4, 0.0, -1.0, 'J1', 'J1'


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


def setDPhiInRange(dPhi):
    if dPhi > 3.14:
        return 6.283-dPhi
    else:
        return dPhi

def calcdPhiMetValues(tau1Phi, tau2Phi, j1Phi, j2Phi, metPhi, tauTauPhi, jjPhi, svPhi):
    return setDPhiInRange(abs(tau1Phi - metPhi)), setDPhiInRange(abs(tau2Phi - metPhi)), setDPhiInRange(abs(j1Phi - metPhi)), setDPhiInRange(abs(j2Phi - metPhi)), setDPhiInRange(abs(tauTauPhi - metPhi)), setDPhiInRange(abs(jjPhi - metPhi)),  setDPhiInRange(abs(svPhi - metPhi)) 
