#!/usr/bin/env python
from operator import itemgetter
import ROOT as r
from cutSampleTools import *

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
lep1 = lvClass()
lep2 = lvClass()
J1 = lvClass()
J2 = lvClass()
J3 = lvClass()
J4 = lvClass()
J5 = lvClass()
J6 = lvClass()
J7 = lvClass()
J8 = lvClass()

emptyJets = lvClass()
emptyJets.SetCoordinates(-9999, -9999, -9999, -9999)

def getNJetinGap(jets):
    njetingap = 0
    if len(jets) <= 2:
        return njetingap

    etaMin = abs(jets[0].eta()) if abs(jets[0].eta()) < abs(jets[1].eta()) else abs(jets[1].eta())
    etaMax = abs(jets[0].eta()) if abs(jets[0].eta()) > abs(jets[1].eta()) else abs(jets[1].eta())
    for iJet in jets:
        if etaMin < abs(iJet.eta()) < etaMax:
            njetingap += 1
    return njetingap


def getCrossCleanJets(jetsList, lepList, type = 'jet', iChain = None):
    goodJets = []
    pt20GoodJets = []
    pt30GoodJets = []

    jetCuts = {}
    if type == 'jet':
        jetCuts['pt'] = 20.0
        jetCuts['bTag'] = -99999
        jetCuts['eta'] = 4.7

    else:
        jetCuts['pt'] = 20.0
        jetCuts['bTag'] = 0.89
        jetCuts['eta'] = 2.4

    for iCSV, iJet, iJetMVA, PFLoose in jetsList:
        if iJet.pt() > jetCuts['pt'] and abs(iJet.eta()) < jetCuts['eta'] and iCSV > jetCuts['bTag']:
            if r.Math.VectorUtil.DeltaR(iJet, lepList[0]) > 0.5 and r.Math.VectorUtil.DeltaR(iJet, lepList[1]) > 0.5:                
#                 if (not puJetId(abs(iJet.eta()), iJetMVA)) or 
                if (not PFLoose):
                    continue
                if iJet.pt() > 20:
                    pt20GoodJets.append(iJet)
                if iJet.pt() > 30:
                    pt30GoodJets.append(iJet)
                if type == 'jet':
                    goodJets.append((iJet.pt(), iJet, iJetMVA))
                else:
                    goodJets.append((iCSV, iJet, iJetMVA))
    while len(goodJets) < 8:
        goodJets.append((-9999.,emptyJets, -9999.))
    goodJets = sorted(goodJets, key=itemgetter(0), reverse=True)
    return goodJets, pt20GoodJets, pt30GoodJets

commonVarsDict = {"pt_": "Pt",
                 "eta_": "Eta",
                 'phi_': 'Phi',
                 'm_': 'Mass',
                 'q_': 'Charge',
                 'mt_': 'MtToPFMET',
                 'dZ_': 'dZ',
                 'dXY_': 'dXY',
                 'gen_match_': 'GenMatchCategory',
                }
tauVarsDict = {'iso_': 'ByCombinedIsolationDeltaBetaCorrRaw3Hits',
              'byCombinedIsolationDeltaBetaCorrRaw3Hits_': 'ByCombinedIsolationDeltaBetaCorrRaw3Hits',
              'chargedIsoPtSum_': 'ChargedIsoPtSum',
              'decayModeFinding_': 'DecayModeFinding',
              'decayModeFindingNewDMs_': 'DecayModeFindingNewDMs',
              'neutralIsoPtSum_': 'NeutralIsoPtSum',
              'puCorrPtSum_': 'PuCorrPtSum'
              }

eMuVarsDict = {'iso_': 'RelIso'}

def saveExtra(iChain, floatVarsDict, syncVarsDict, intVarsDict, sync, FS, sys, isData):
    if FS == 'tt':
        if iChain.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits <= iChain.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits:
            object_1 = 't1'
            object_2 = 't2'
        else:
            object_1 = 't2'
            object_2 = 't1'
    elif FS[0] == FS[1]:
        if getattr(iChain, '%s1RelIso' %FS[0]) <= getattr(iChain, '%s2RelIso' %FS[0]):
            object_1 = '%s1' %FS[0]
            object_2 = '%s2' %FS[0]
        else:
            object_1 = '%s2' %FS[0]
            object_2 = '%s1' %FS[0]
    else:
        object_1 = FS[0]
        object_2 = FS[1]

    lep1.SetCoordinates(getattr(iChain, '%sPt' %object_1),
                        getattr(iChain, '%sEta' %object_1),
                        getattr(iChain, '%sPhi' %object_1),
                        getattr(iChain, '%sMass' %object_1))
    lep2.SetCoordinates(getattr(iChain, '%sPt' %object_2),
                        getattr(iChain, '%sEta' %object_2),
                        getattr(iChain, '%sPhi' %object_2),
                        getattr(iChain, '%sMass' %object_2))

    jetsList = [(iChain.jet1CSVBtag, J1.SetCoordinates(iChain.jet1Pt, iChain.jet1Eta, iChain.jet1Phi, iChain.jet1Mass), iChain.jet1PUMVA, iChain.jet1PFJetIDLoose),
                (iChain.jet2CSVBtag, J2.SetCoordinates(iChain.jet2Pt, iChain.jet2Eta, iChain.jet2Phi, iChain.jet2Mass), iChain.jet2PUMVA, iChain.jet2PFJetIDLoose),
                (iChain.jet3CSVBtag, J3.SetCoordinates(iChain.jet3Pt, iChain.jet3Eta, iChain.jet3Phi, iChain.jet3Mass), iChain.jet3PUMVA, iChain.jet3PFJetIDLoose),
                (iChain.jet4CSVBtag, J4.SetCoordinates(iChain.jet4Pt, iChain.jet4Eta, iChain.jet4Phi, iChain.jet4Mass), iChain.jet4PUMVA, iChain.jet4PFJetIDLoose),
                (iChain.jet5CSVBtag, J5.SetCoordinates(iChain.jet5Pt, iChain.jet5Eta, iChain.jet5Phi, iChain.jet5Mass), iChain.jet5PUMVA, iChain.jet5PFJetIDLoose),
                (iChain.jet6CSVBtag, J6.SetCoordinates(iChain.jet6Pt, iChain.jet6Eta, iChain.jet6Phi, iChain.jet6Mass), iChain.jet6PUMVA, iChain.jet6PFJetIDLoose),
                (iChain.jet7CSVBtag, J7.SetCoordinates(iChain.jet7Pt, iChain.jet7Eta, iChain.jet7Phi, iChain.jet7Mass), iChain.jet7PUMVA, iChain.jet7PFJetIDLoose),
                (iChain.jet8CSVBtag, J8.SetCoordinates(iChain.jet8Pt, iChain.jet8Eta, iChain.jet8Phi, iChain.jet8Mass), iChain.jet8PUMVA, iChain.jet8PFJetIDLoose)]


    bJets, pt20bjets, pt30bjets = getCrossCleanJets(jetsList = jetsList, lepList = [lep1, lep2], type = 'b', iChain = None)

    first = 0
    second = 1
    if bJets[0][1].pt() < bJets[1][1].pt():
        first = 1
        second = 0

    intVarsDict['nbtag'][0] = len(pt20bjets)
    floatVarsDict['bcsv_1'][0] = bJets[first][0]
    floatVarsDict['bmva_1'][0] = bJets[first][2]
    floatVarsDict['bpt_1'][0] = bJets[first][1].pt()
    floatVarsDict['beta_1'][0] =bJets[first][1].eta()

    floatVarsDict['bcsv_2'][0] = bJets[second][0] 
    floatVarsDict['bmva_2'][0] = bJets[second][2]
    floatVarsDict['bpt_2'][0] = bJets[second][1].pt()
    floatVarsDict['beta_2'][0] = bJets[second][1].eta()
    floatVarsDict['mJJ'][0] = (bJets[0][1] + bJets[1][1]).mass()

    if sync:
        syncVarsDict['npv'][0] = iChain.nvtx
        syncVarsDict['npu'][0] = iChain.nTruePU

        for ikey in commonVarsDict.keys():
            if (ikey == 'pt_') and ('t' in FS) and ('tau' in sys):
                syncVarsDict['%s1' %ikey][0] = getattr(iChain, '%s%s' %(object_1, commonVarsDict[ikey]))
                if sys == 'tauECUp' and iChain.tIsTauh:
                    syncVarsDict['%s2' %ikey][0] = getattr(iChain, '%s%s' %(object_2, 'ES_up'))
                elif sys == 'tauECDown' and iChain.tIsTauh:
                    syncVarsDict['%s2' %ikey][0] = getattr(iChain, '%s%s' %(object_2, 'ES_down'))
                else:
                    syncVarsDict['%s2' %ikey][0] = getattr(iChain, '%s%s' %(object_2, commonVarsDict[ikey]))
            else:
                if hasattr(iChain, '%s%s' %(object_1, commonVarsDict[ikey])):
                    syncVarsDict['%s1' %ikey][0] = getattr(iChain, '%s%s' %(object_1, commonVarsDict[ikey]))
                if hasattr(iChain, '%s%s' %(object_2, commonVarsDict[ikey])):
                    syncVarsDict['%s2' %ikey][0] = getattr(iChain, '%s%s' %(object_2, commonVarsDict[ikey]))

        if 't' in object_1:
            for ikey in tauVarsDict.keys():
                syncVarsDict['%s1' %ikey][0] = getattr(iChain, '%s%s' %(object_1, tauVarsDict[ikey]))
        else:
            for ikey in eMuVarsDict.keys():
                syncVarsDict['%s1' %ikey][0] = getattr(iChain, '%s%s' %(object_1, eMuVarsDict[ikey]))

        if 't' in object_2:
            for ikey in tauVarsDict.keys():
                syncVarsDict['%s2' %ikey][0] = getattr(iChain, '%s%s' %(object_2, tauVarsDict[ikey]))
        else:
            for ikey in eMuVarsDict.keys():
                syncVarsDict['%s2' %ikey][0] = getattr(iChain, '%s%s' %(object_2, eMuVarsDict[ikey]))

        if FS[0] == FS[1]:
            syncVarsDict['m_vis'][0] = getattr(iChain, '%s1_%s2_Mass' %(FS[0], FS[0]))
#             syncVarsDict['m_sv'][0] = getattr(iChain, 't1_t2_SVfit').Pt()
#             syncVarsDict['pt_sv'][0] = getattr(iChain, 't1_t2_SVfit').Eta()
#             syncVarsDict['eta_sv'][0] = getattr(iChain, 't1_t2_SVfit').Phi()
#             syncVarsDict['phi_sv'][0] = getattr(iChain, 't1_t2_SVfit').M()

        else:
            syncVarsDict['m_vis'][0] = getattr(iChain, '%s_%s_Mass' %(object_1, object_2))

        syncVarsDict['met'][0] = iChain.pfMetEt
        syncVarsDict['metphi'][0] = iChain.pfMetPhi
        syncVarsDict['metcov00'][0] = iChain.pfmetCovariance_00
        syncVarsDict['metcov01'][0] = iChain.pfmetCovariance_01
        syncVarsDict['metcov10'][0] = iChain.pfmetCovariance_10
        syncVarsDict['metcov11'][0] = iChain.pfmetCovariance_11

#         syncVarsDict['mvamet'][0] = iChain.mvametEt
#         syncVarsDict['mvametphi'][0] = iChain.mvametPhi
        met = lvClass()
        met.SetCoordinates(iChain.pfMetEt, 0.0, iChain.pfMetPhi, 0)
        if FS == 'et':
            if sys == 'tauECUp' and iChain.tIsTauh:
                lep2.SetCoordinates(iChain.tES_up, iChain.tEta, iChain.tPhi, iChain.tMass)
            elif sys == 'tauECDown' and iChain.tIsTauh:
                lep2.SetCoordinates(iChain.tES_down, iChain.tEta, iChain.tPhi, iChain.tMass)
            if (sys == 'tauECDown' or sys == 'tauECUp') and (not isData) and iChain.tIsTauh:
                if lep2.pt() - iChain.tPt > 0:
                    deltaTauES.SetCoordinates(abs(lep2.pt() - iChain.tPt), 0.0, -iChain.tPhi, 0)
                else:
                    deltaTauES.SetCoordinates(abs(lep2.pt() - iChain.tPt), 0.0, iChain.tPhi, 0)
                met = met + deltaTauES        

        if sys == 'jetECUp' and not isData:
            met.SetCoordinates(iChain.pfMet_jesUp_Et, 0.0, iChain.pfMet_jesUp_Phi, 0)
        elif sys == 'jetECDown' and not isData:
            met.SetCoordinates(iChain.pfMet_jesDown_Et, 0.0, iChain.pfMet_jesDown_Phi, 0)

        floatVarsDict['cosDPhi'][0] = math.cos(lep1.phi() - lep2.phi())
        floatVarsDict['pZetaCut'][0] = pZetaCut(lep1, lep2, met)
        floatVarsDict['m_eff'][0] = (lep1 + lep2 + met).mass()

        goodJets, pt20jets, pt30jets = getCrossCleanJets(jetsList = jetsList, lepList = [lep1, lep2], type = 'jet', iChain = iChain)

        intVarsDict['njetspt20'][0] = len(pt20jets)
        intVarsDict['njets'][0] = len(pt30jets)
        intVarsDict['njetingap20'][0] = getNJetinGap(pt20jets)
        intVarsDict['njetingap'][0] = getNJetinGap(pt30jets)

        syncVarsDict['jcsv_1'][0] = goodJets[0][0]
        syncVarsDict['jpt_1'][0] = goodJets[0][1].pt()
        syncVarsDict['jeta_1'][0] = goodJets[0][1].eta()
        syncVarsDict['jphi_1'][0] = goodJets[0][1].phi()
        syncVarsDict['jmva_1'][0] = goodJets[0][2]

        syncVarsDict['jcsv_2'][0] = goodJets[1][0]
        syncVarsDict['jpt_2'][0] = goodJets[1][1].pt()
        syncVarsDict['jeta_2'][0] = goodJets[1][1].eta()
        syncVarsDict['jphi_2'][0] = goodJets[1][1].phi()
        syncVarsDict['jmva_2'][0] = goodJets[1][2]

        #trigger weight
        syncVarsDict['trigweight_1'][0] = 1.0
        syncVarsDict['trigweight_2'][0] = 1.0
        if FS == 'et':
            syncVarsDict['trigweight_1'][0] = eleTrigEff(abs(iChain.eEta))

#         syncVarsDict['puweight'][0] = getPUWeight(iChain.nTruePU)
