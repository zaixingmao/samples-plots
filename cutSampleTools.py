#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import varsList
import math

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
combinedJJ = lvClass()


def calcTrigOneTauEff(eta, pt, data = True, fitStart=25):
        le14_da = {20: (0.898, 44.3, 1.02),
                  25: (0.866, 43.1, 0.86),
                  30: (0.839, 42.3, 0.73),
                  35: (0.846, 42.4, 0.78),
                  }
        le14_mc = {20: (0.837, 43.6, 1.09),
                   25: (0.832, 40.4, 0.80),
                   30: (0.829, 40.4, 0.74),
                   35: (0.833, 40.1, 0.86),
                   }
        ge16_da = {20: (0.81, 43.6, 1.09),
                   25: (0.76, 41.8, 0.86),
                   30: (0.74, 41.2, 0.75),
                   35: (0.74, 41.2, 0.79),
                   }
        ge16_mc = {20: (0.70, 39.7, 0.95),
                   25: (0.69, 38.6, 0.74),
                   30: (0.69, 38.7, 0.61),
                   35: (0.69, 38.8, 0.61),
                   }
        le14 = le14_da if data else le14_mc
        ge16 = ge16_da if data else ge16_mc
        if abs(eta) < 1.4:
            d = le14
        else:
            d = ge16
        e, x0, sigma = d[fitStart]
        y = r.TMath.Erf((pt-x0)/2.0/sigma/math.sqrt(pt))  # https://github.com/rmanzoni/HTT/blob/master/CMGTools/H2TauTau/interface/TriggerEfficiency.h
        #y = r.TMath.Erf((pt-x0)/sigma/math.sqrt(2.0))
        return (1+y)*e/2.0


def findFullMass(jetsList = [], sv4Vec = ''):
    newList = []
    for i in range(len(jetsList)):
        if jetsList[i][1].pt() > 20 and abs(jetsList[i][1].eta()) < 2.4:
            newList.append(jetsList[i])
    newList = sorted(newList, key=itemgetter(0), reverse=True)
    if len(newList) < 2:
        return -1, -1, -1, -1, -1, -1, -1, -1, -1
    if newList[1][0] > 0:
        combinedJJ = newList[0][1]+newList[1][1]
        return combinedJJ, newList[0][0], newList[1][0], newList[0][1], newList[1][1], (combinedJJ+sv4Vec).mass(), r.Math.VectorUtil.DeltaR(newList[0][1], newList[1][1]), newList[0][2], newList[1][2]
    else:
        return -1, -1, -1, -1, -1, -1, -1, -1, -1


def findGenJet(j1Name, jet1, j2Name, jet2, tChain):
    genJet1 = lvClass()
    genJet2 = lvClass()
    genJet1.SetCoordinates(0,0,0,0)
    genJet2.SetCoordinates(0,0,0,0)
    pt1, eta1, phi1, mass1 = varsList.findVarInChain_GenJet_speed(tChain, '%s' %j1Name)
    pt2, eta2, phi2, mass2 = varsList.findVarInChain_GenJet_speed(tChain, '%s' %j2Name)

    if pt1 > 0 and mass1 > 0:
        genJet1.SetCoordinates(pt1, eta1, phi1, mass1)
    if pt2 > 0 and mass2 > 0:
        genJet2.SetCoordinates(pt2, eta1, phi2, mass2)

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

def getRegVars(jName, tChain):
    jet = lvClass()
    SoftLep = 0
    PtUncorr, VtxPt, Vtx3dL, Vtx3deL, ptLeadTrk, vtxMass, vtxPt, Ntot, SoftLepPt, SoftLepEta, SoftLepPhi, SoftLepPID, JECUnc, Et, Mt, Pt, Eta, Phi, Mass = varsList.findVarInChain_Data_speed(tChain,'%s' %jName)

    jet.SetCoordinates(Pt, Eta, Phi, 0)
    if SoftLepPID == 0:
        SoftLepPtRel = 0
        SoftLepdR = 0
    else:
        SoftLepPtRel = Pt - SoftLepPt
        softLept = lvClass()
        softLept.SetCoordinates(SoftLepPt, SoftLepEta, SoftLepPhi, 0)
        SoftLepdR = r.Math.VectorUtil.DeltaR(softLept, jet)
        SoftLepPt = SoftLepPt
    if SoftLepPt < 0:
        SoftLepPt = 0
    return PtUncorr, Et, Mt, ptLeadTrk, Vtx3dL,Vtx3deL, vtxMass, VtxPt, JECUnc, float(Ntot), SoftLepPtRel, SoftLepPt, SoftLepdR


def setDPhiInRange(dPhi):
    if dPhi > 3.14:
        return 6.283-dPhi
    else:
        return dPhi

def calcdPhiMetValues(tau1Phi, tau2Phi, j1Phi, j2Phi, metPhi, tauTauPhi, jjPhi, svPhi):
    return setDPhiInRange(abs(tau1Phi - metPhi)), setDPhiInRange(abs(tau2Phi - metPhi)), setDPhiInRange(abs(j1Phi - metPhi)), setDPhiInRange(abs(j2Phi - metPhi)), setDPhiInRange(abs(tauTauPhi - metPhi)), setDPhiInRange(abs(jjPhi - metPhi)),  setDPhiInRange(abs(svPhi - metPhi)) 
