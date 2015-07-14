#!/usr/bin/env python
from operator import itemgetter
import ROOT as r

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

def getCrossCleanJets(jetsList, lepList, type = 'jet', iChain = None):
    goodJets = []
    nPt20GoodJets = 0
    nPt30GoodJets = 0

    jetCuts = {}
    if type == 'jet':
        jetCuts['pt'] = 20.0
        jetCuts['bTag'] = -99999
        jetCuts['eta'] = 4.7

    else:
        jetCuts['pt'] = 20.0
        jetCuts['bTag'] = 0.814
        jetCuts['eta'] = 2.4

    for iCSV, iJet, iJetMVA, PFLoose in jetsList:
        if iJet.pt() > jetCuts['pt'] and abs(iJet.eta()) < jetCuts['eta'] and iCSV > jetCuts['bTag']:
            if r.Math.VectorUtil.DeltaR(iJet, lepList[0]) > 0.5 and r.Math.VectorUtil.DeltaR(iJet, lepList[1]) > 0.5:                
#                 if (not puJetId(abs(iJet.eta()), iJetMVA)) or 
                if (not PFLoose):
                    continue
                if iJet.pt() > 20:
                    nPt20GoodJets += 1
                if iJet.pt() > 30:
                    nPt30GoodJets += 1
                if type == 'jet':
                    goodJets.append((iJet.pt(), iJet, iJetMVA))
                else:
                    goodJets.append((iCSV, iJet, iJetMVA))
    while len(goodJets) < 8:
        goodJets.append((-9999.,emptyJets, -9999.))
    goodJets = sorted(goodJets, key=itemgetter(0), reverse=True)
    return goodJets, nPt20GoodJets, nPt30GoodJets



def saveExtra(iChain, floatVarsDict, syncVarsDict, intVarsDict, sync, FS):
    if FS == 'tt':
        if iChain.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits <= iChain.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits:
            object_1 = 't1'
            object_2 = 't2'
        else:
            object_1 = 't2'
            object_2 = 't1'
    elif FS == 'et':
        object_1 = 'e'
        object_2 = 't'
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


    bJets, intVarsDict['nbtag'][0], nPt30bjets = getCrossCleanJets(jetsList = jetsList, lepList = [lep1, lep2], type = 'b', iChain = None)

    floatVarsDict['bjcsv_1'][0] = bJets[0][0]
    floatVarsDict['bjcsv_2'][0] = bJets[1][0] 
    floatVarsDict['bjmva_1'][0] = bJets[0][2]
    floatVarsDict['bjmva_2'][0] = bJets[1][2]

    floatVarsDict['bjpt_1'][0] = bJets[0][1].pt()
    floatVarsDict['bjeta_1'][0] =bJets[0][1].eta()
    floatVarsDict['bjpt_2'][0] = bJets[1][1].pt()
    floatVarsDict['bjeta_2'][0] = bJets[1][1].eta()
    floatVarsDict['mJJ'][0] = (bJets[0][1] + bJets[1][1]).mass()

    if sync:
        syncVarsDict['npv'][0] = iChain.nvtx
        syncVarsDict['npu'][0] = iChain.nTruePU

        syncVarsDict['pt_1'][0] = getattr(iChain, '%sPt' %object_1)
        syncVarsDict['eta_1'][0] = getattr(iChain, '%sEta' %object_1)
        syncVarsDict['phi_1'][0] = getattr(iChain, '%sPhi' %object_1)
        syncVarsDict['m_1'][0] = getattr(iChain, '%sMass' %object_1)
        syncVarsDict['q_1'][0] = getattr(iChain, '%sCharge' %object_1)
        syncVarsDict['mt_1'][0] = getattr(iChain, '%sMtToPFMET' %object_1)
        syncVarsDict['dZ_1'][0] = getattr(iChain, '%sdZ' %object_1)
        if FS == 'tt':    
            syncVarsDict['iso_1'][0] = getattr(iChain, '%sByCombinedIsolationDeltaBetaCorrRaw3Hits' %object_1)
            syncVarsDict['againstElectronLooseMVA5_1'][0] = getattr(iChain, '%sAgainstElectronLooseMVA5' %object_1)
            syncVarsDict['againstElectronMediumMVA5_1'][0] = getattr(iChain, '%sAgainstElectronMediumMVA5' %object_1)
            syncVarsDict['againstElectronTightMVA5_1'][0] = getattr(iChain, '%sAgainstElectronTightMVA5' %object_1)
            syncVarsDict['againstElectronVLooseMVA5_1'][0] = getattr(iChain, '%sAgainstElectronVLooseMVA5' %object_1)
            syncVarsDict['againstElectronVTightMVA5_1'][0] = getattr(iChain, '%sAgainstElectronVTightMVA5' %object_1)
            syncVarsDict['againstMuonLoose3_1'][0] = getattr(iChain, '%sAgainstMuonLoose3' %object_1)
            syncVarsDict['againstMuonTight3_1'][0] = getattr(iChain, '%sAgainstMuonTight3' %object_1)
            syncVarsDict['byCombinedIsolationDeltaBetaCorrRaw3Hits_1'][0] = getattr(iChain, '%sByCombinedIsolationDeltaBetaCorrRaw3Hits' %object_1)
            syncVarsDict['byIsolationMVA3newDMwoLTraw_1'][0] = getattr(iChain, '%sByIsolationMVA3newDMwoLTraw' %object_1)
            syncVarsDict['byIsolationMVA3oldDMwoLTraw_1'][0] = getattr(iChain, '%sByIsolationMVA3oldDMwoLTraw' %object_1)
            syncVarsDict['byIsolationMVA3newDMwLTraw_1'][0] = getattr(iChain, '%sByIsolationMVA3newDMwLTraw' %object_1)
            syncVarsDict['byIsolationMVA3oldDMwLTraw_1'][0] = getattr(iChain, '%sByIsolationMVA3oldDMwLTraw' %object_1)
            syncVarsDict['chargedIsoPtSum_1'][0] = getattr(iChain, '%sChargedIsoPtSum' %object_1)
            syncVarsDict['decayModeFinding_1'][0] = getattr(iChain, '%sDecayModeFinding' %object_1)
            syncVarsDict['decayModeFindingNewDMs_1'][0] = getattr(iChain, '%sDecayModeFindingNewDMs' %object_1)
            syncVarsDict['neutralIsoPtSum_1'][0] = getattr(iChain, '%sNeutralIsoPtSum' %object_1)
            syncVarsDict['puCorrPtSum_1'][0] = getattr(iChain, '%sPuCorrPtSum' %object_1)
            syncVarsDict['m_vis'][0] = getattr(iChain, 't1_t2_Mass')

        elif FS == 'et':
            syncVarsDict['iso_1'][0] = getattr(iChain, '%sRelIso' %object_1)
            syncVarsDict['m_vis'][0] = getattr(iChain, '%s_%s_Mass' %(object_1, object_2))

        syncVarsDict['pt_2'][0] = getattr(iChain, '%sPt' %object_2)
        syncVarsDict['eta_2'][0] = getattr(iChain, '%sEta' %object_2)
        syncVarsDict['phi_2'][0] = getattr(iChain, '%sPhi' %object_2)
        syncVarsDict['m_2'][0] = getattr(iChain, '%sMass' %object_2)
        syncVarsDict['q_2'][0] = getattr(iChain, '%sCharge' %object_2)
        syncVarsDict['mt_2'][0] = getattr(iChain, '%sMtToPFMET' %object_2)
        syncVarsDict['dZ_2'][0] = getattr(iChain, '%sdZ' %object_2)
        syncVarsDict['iso_2'][0] =  getattr(iChain, '%sByCombinedIsolationDeltaBetaCorrRaw3Hits' %object_2)
        syncVarsDict['againstElectronLooseMVA5_2'][0] = getattr(iChain, '%sAgainstElectronLooseMVA5' %object_2)
        syncVarsDict['againstElectronMediumMVA5_2'][0] = getattr(iChain, '%sAgainstElectronMediumMVA5' %object_2)
        syncVarsDict['againstElectronTightMVA5_2'][0] = getattr(iChain, '%sAgainstElectronTightMVA5' %object_2)
        syncVarsDict['againstElectronVLooseMVA5_2'][0] = getattr(iChain, '%sAgainstElectronVLooseMVA5' %object_2)
        syncVarsDict['againstElectronVTightMVA5_2'][0] = getattr(iChain, '%sAgainstElectronVTightMVA5' %object_2)
        syncVarsDict['againstMuonLoose3_2'][0] = getattr(iChain, '%sAgainstMuonLoose3' %object_2)
        syncVarsDict['againstMuonTight3_2'][0] = getattr(iChain, '%sAgainstMuonTight3' %object_2)
        syncVarsDict['byCombinedIsolationDeltaBetaCorrRaw3Hits_2'][0] = getattr(iChain, '%sByCombinedIsolationDeltaBetaCorrRaw3Hits' %object_2)
        syncVarsDict['byIsolationMVA3newDMwoLTraw_2'][0] = getattr(iChain, '%sByIsolationMVA3newDMwoLTraw' %object_2)
        syncVarsDict['byIsolationMVA3oldDMwoLTraw_2'][0] = getattr(iChain, '%sByIsolationMVA3oldDMwoLTraw' %object_2)
        syncVarsDict['byIsolationMVA3newDMwLTraw_2'][0] = getattr(iChain, '%sByIsolationMVA3newDMwLTraw' %object_2)
        syncVarsDict['byIsolationMVA3oldDMwLTraw_2'][0] = getattr(iChain, '%sByIsolationMVA3oldDMwLTraw' %object_2)
        syncVarsDict['chargedIsoPtSum_2'][0] = getattr(iChain, '%sChargedIsoPtSum' %object_2)
        syncVarsDict['decayModeFinding_2'][0] = getattr(iChain, '%sDecayModeFinding' %object_2)
        syncVarsDict['decayModeFindingNewDMs_2'][0] = getattr(iChain, '%sDecayModeFindingNewDMs' %object_2)
        syncVarsDict['neutralIsoPtSum_2'][0] = getattr(iChain, '%sNeutralIsoPtSum' %object_2)
        syncVarsDict['puCorrPtSum_2'][0] = getattr(iChain, '%sPuCorrPtSum' %object_2)

        syncVarsDict['met'][0] = iChain.pfMetEt
        syncVarsDict['metphi'][0] = iChain.pfMetPhi
#         syncVarsDict['mvamet'][0] = iChain.mvametEt
#         syncVarsDict['mvametphi'][0] = iChain.mvametPhi

        goodJets, intVarsDict['njetspt20'][0], intVarsDict['njets'][0] = getCrossCleanJets(jetsList = jetsList, lepList = [lep1, lep2], type = 'jet', iChain = iChain)
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
