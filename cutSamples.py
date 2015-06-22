#!/usr/bin/env python

import ROOT as r
import tool
import os
import cProfile
from cfg import enVars
from array import array
import optparse
import kinfit
from cutSampleTools import *
import trigger
import data_certification

r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000
r.gStyle.SetOptStat("e")

xLabels = ['Topology', 'Leg0Pt', 'Leg0Eta','Leg1Pt', 'Leg1Eta', 't_UniqueByPt', 'myCut']

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
J1 = lvClass()
J2 = lvClass()
J3 = lvClass()
J4 = lvClass()
J5 = lvClass()
J6 = lvClass()

matchedGenJet = lvClass()
mGenJet1 = lvClass()
mGenJet2 = lvClass()
CSVJet1 = lvClass()
CSVJet2 = lvClass()
genTau1 = lvClass()
genTau2 = lvClass()
combinedJJ = lvClass()
sv4Vec = lvClass()

kinfit.setup()


def setUpFloatVarsDict():
    varDict = {}
    names = ['genHMass', 'xs','fullMass', 'mJJ', 'ptJJ', 'etaJJ', 'phiJJ', 
            'bjcsv_1','bjpt_1','bjeta_1','bjphi_1', 'bjmass_1', 'bjrawf_1','bjmva_1','bjpfid_1', 'bjpuid_1',
            'bjcsv_2','bjpt_2','bjeta_2','bjphi_2', 'bjmass_2', 'bjrawf_2','bjmva_2','bjpfid_2', 'bjpuid_2','dRTauTau', 'dRJJ']

    for iName in names:
        varDict[iName] = array('f', [0.])
    return varDict

def setUpSyncVarsDict():
    varDict = {}
    names = ['weight', 'puweight','npv', 'npu',
            'pt_1', 'phi_1', 'eta_1','m_1','q_1','d0_1', 'dZ_1', 'mt_1', 'iso_1', 'id_m_loose_1', 'id_m_medium_1', 'id_m_tight_1', 'id_m_tightnovtx_1', 'id_m_highpt_1',
            'id_e_mva_nt_loose_1', 'id_e_mva_nt_loose_1', 'id_e_cut_veto_1', 'id_e_cut_loose_1', 'id_e_cut_medium_1', 'id_e_cut_tight_1', 'trigweight_1', 
            'againstElectronLooseMVA5_1','againstElectronMediumMVA5_1', 'againstElectronTightMVA5_1', 'againstElectronVLooseMVA5_1', 'againstElectronVTightMVA5_1', 'againstMuonLoose3_1', 'againstMuonTight3_1', 
            'byCombinedIsolationDeltaBetaCorrRaw3Hits_1', 'byIsolationMVA3newDMwoLTraw_1', 'byIsolationMVA3oldDMwoLTraw_1', 'byIsolationMVA3newDMwLTraw_1', 'byIsolationMVA3oldDMwLTraw_1',
            'chargedIsoPtSum_1', 'decayModeFinding_1', 'decayModeFindingNewDMs_1', 'neutralIsoPtSum_1', 'puCorrPtSum_1',
            'pt_2', 'phi_2', 'eta_2','m_2','q_2','d0_2', 'dZ_2', 'mt_2', 'iso_2', 'id_m_loose_2', 'id_m_medium_2', 'id_m_tight_2', 'id_m_tightnovtx_2', 'id_m_highpt_2',
            'id_e_mva_nt_loose_2', 'id_e_mva_nt_loose_2', 'id_e_cut_veto_2', 'id_e_cut_loose_2', 'id_e_cut_medium_2', 'id_e_cut_tight_2', 'trigweight_2', 'againstElectronLooseMVA5_2',
            'againstElectronMediumMVA5_2', 'againstElectronTightMVA5_2', 'againstElectronVLooseMVA5_2', 'againstElectronVTightMVA5_2', 'againstMuonLoose3_2', 'againstMuonTight3_2', 
            'byCombinedIsolationDeltaBetaCorrRaw3Hits_2', 'byIsolationMVA3newDMwoLTraw_2', 'byIsolationMVA3oldDMwoLTraw_2', 'byIsolationMVA3newDMwLTraw_2', 'byIsolationMVA3oldDMwLTraw_2',
            'chargedIsoPtSum_2', 'decayModeFinding_2', 'decayModeFindingNewDMs_2', 'neutralIsoPtSum_2', 'puCorrPtSum_2',
            'pth', 'm_vis', 'm_sv', 'pt_sv', 'eta_sv', 'phi_sv', 'met_sv',
            'jpt_1', 'jeta_1', 'jphi_1', 'jrawf_1', 'jmva_1', 'jpfid_1', 'jpuid_1', 'jcsv_1',
            'jpt_2', 'jeta_2', 'jphi_2', 'jrawf_2', 'jmva_2', 'jpfid_2', 'jpuid_2', 'jcsv_2']


    for iName in names:
        varDict[iName] = array('f', [0.])
    return varDict

def setUpIntVarsDict():
    varDict = {}
    names = ['nElectrons', 'nMuons', 'initEvents', 'ZTT', 'ZLL']
    for iName in names:
        varDict[iName] = array('i', [0])
    return varDict

def setUpCharVarsDict():
    varDict = {}
    names = ['sampleName', 'category']
    for iName in names:
        varDict[iName] = bytearray(30)
    return varDict

def opts():
    parser = optparse.OptionParser()
    parser.add_option("-l", dest="location", default="/scratch/%s" % os.environ["USER"], help="location to be saved")
    parser.add_option("-n", dest="nevents", default="-1", help="amount of events to be saved")
    parser.add_option("-g", dest="genMatch", default="jet", help="gen particle for the reco-jet to match to")
    parser.add_option("-t", dest="folderName", default="ttTreeBeforeChargeCut", help="")
    parser.add_option("--pair", dest="pairChoice", default="iso", help="which pair")
    parser.add_option("--sync", dest="sync", default=False, action="store_true", help="which pair")
    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    options, args = parser.parse_args()

    return options


def saveExtra(iChain, floatVarsDict, syncVarsDict, sync):
    genTau1.SetCoordinates(iChain.t1GenPt, iChain.t1GenEta, iChain.t1GenPhi, iChain.t1GenMass)
    genTau2.SetCoordinates(iChain.t2GenPt, iChain.t2GenEta, iChain.t2GenPhi, iChain.t2GenMass)
    floatVarsDict['genHMass'][0] = (genTau1+genTau2).mass()

    jetsList = [(iChain.jet1CSVBtag, J1.SetCoordinates(iChain.jet1Pt, iChain.jet1Eta, iChain.jet1Phi, iChain.jet1Mass), iChain.jet1PUMVA),
                (iChain.jet2CSVBtag, J2.SetCoordinates(iChain.jet2Pt, iChain.jet2Eta, iChain.jet2Phi, iChain.jet2Mass), iChain.jet2PUMVA),
                (iChain.jet3CSVBtag, J3.SetCoordinates(iChain.jet3Pt, iChain.jet3Eta, iChain.jet3Phi, iChain.jet3Mass), iChain.jet3PUMVA),
                (iChain.jet4CSVBtag, J4.SetCoordinates(iChain.jet4Pt, iChain.jet4Eta, iChain.jet4Phi, iChain.jet4Mass), iChain.jet4PUMVA),
                (iChain.jet5CSVBtag, J5.SetCoordinates(iChain.jet5Pt, iChain.jet5Eta, iChain.jet5Phi, iChain.jet5Mass), iChain.jet5PUMVA),
                (iChain.jet6CSVBtag, J6.SetCoordinates(iChain.jet6Pt, iChain.jet6Eta, iChain.jet6Phi, iChain.jet6Mass), iChain.jet6PUMVA)]

    floatVarsDict['bjcsv_1'][0], floatVarsDict['bjcsv_2'][0], CSVJet1, CSVJet2, floatVarsDict['bjmva_1'][0], floatVarsDict['bjmva_2'][0] = findJetPair(iTree = iChain, jetsList = jetsList, ptThreshold = enVars.jetPtThreshold)

    floatVarsDict['bjpt_1'][0] = CSVJet1.pt()
    floatVarsDict['bjeta_1'][0] = CSVJet1.eta()
    floatVarsDict['bjpt_2'][0] = CSVJet2.pt()
    floatVarsDict['bjeta_2'][0] = CSVJet2.eta()
    floatVarsDict['mJJ'][0] = (CSVJet1 + CSVJet2).mass()

    if sync:
        syncVarsDict['npv'][0] = iChain.nvtx
        syncVarsDict['npu'][0] = iChain.nTruePU
        syncVarsDict['pt_1'][0] = iChain.t1Pt
        syncVarsDict['phi_1'][0] = iChain.t1Phi
        syncVarsDict['m_1'][0] = iChain.t1Mass
        syncVarsDict['q_1'][0] = iChain.t1Charge
        syncVarsDict['mt_1'][0] = iChain.t1MtToMET
        syncVarsDict['iso_1'][0] =  iChain.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits
        syncVarsDict['againstElectronLooseMVA5_1'][0] = iChain.t1AgainstElectronLooseMVA5
        syncVarsDict['againstElectronMediumMVA5_1'][0] = iChain.t1AgainstElectronMediumMVA5
        syncVarsDict['againstElectronTightMVA5_1'][0] = iChain.t1AgainstElectronTightMVA5
        syncVarsDict['againstElectronVLooseMVA5_1'][0] = iChain.t1AgainstElectronVLooseMVA5
        syncVarsDict['againstElectronVTightMVA5_1'][0] = iChain.t1AgainstElectronVTightMVA5
        syncVarsDict['againstMuonLoose3_1'][0] = iChain.t1AgainstMuonLoose3
        syncVarsDict['againstMuonTight3_1'][0] = iChain.t1AgainstMuonTight3
        syncVarsDict['byCombinedIsolationDeltaBetaCorrRaw3Hits_1'][0] = iChain.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits
        syncVarsDict['byIsolationMVA3newDMwoLTraw_1'][0] = iChain.t1ByIsolationMVA3newDMwoLTraw
        syncVarsDict['byIsolationMVA3oldDMwoLTraw_1'][0] = iChain.t1ByIsolationMVA3oldDMwoLTraw
        syncVarsDict['byIsolationMVA3newDMwLTraw_1'][0] = iChain.t1ByIsolationMVA3newDMwLTraw
        syncVarsDict['byIsolationMVA3oldDMwLTraw_1'][0] = iChain.t1ByIsolationMVA3oldDMwLTraw
        syncVarsDict['chargedIsoPtSum_1'][0] = iChain.t1ChargedIsoPtSum
        syncVarsDict['decayModeFinding_1'][0] = iChain.t1DecayModeFinding
        syncVarsDict['decayModeFindingNewDMs_1'][0] = iChain.t1DecayModeFindingNewDMs
        syncVarsDict['neutralIsoPtSum_1'][0] = iChain.t1NeutralIsoPtSum
        syncVarsDict['puCorrPtSum_1'][0] = iChain.t1PuCorrPtSum

        syncVarsDict['pt_2'][0] = iChain.t2Pt
        syncVarsDict['phi_2'][0] = iChain.t2Phi
        syncVarsDict['m_2'][0] = iChain.t2Mass
        syncVarsDict['q_2'][0] = iChain.t2Charge
        syncVarsDict['mt_2'][0] = iChain.t2MtToMET
        syncVarsDict['iso_2'][0] =  iChain.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits
        syncVarsDict['againstElectronLooseMVA5_2'][0] = iChain.t2AgainstElectronLooseMVA5
        syncVarsDict['againstElectronMediumMVA5_2'][0] = iChain.t2AgainstElectronMediumMVA5
        syncVarsDict['againstElectronTightMVA5_2'][0] = iChain.t2AgainstElectronTightMVA5
        syncVarsDict['againstElectronVLooseMVA5_2'][0] = iChain.t2AgainstElectronVLooseMVA5
        syncVarsDict['againstElectronVTightMVA5_2'][0] = iChain.t2AgainstElectronVTightMVA5
        syncVarsDict['againstMuonLoose3_2'][0] = iChain.t2AgainstMuonLoose3
        syncVarsDict['againstMuonTight3_2'][0] = iChain.t2AgainstMuonTight3
        syncVarsDict['byCombinedIsolationDeltaBetaCorrRaw3Hits_2'][0] = iChain.t2ByCombinedIsolationDeltaBetaCorrRaw3Hits
        syncVarsDict['byIsolationMVA3newDMwoLTraw_2'][0] = iChain.t2ByIsolationMVA3newDMwoLTraw
        syncVarsDict['byIsolationMVA3oldDMwoLTraw_2'][0] = iChain.t2ByIsolationMVA3oldDMwoLTraw
        syncVarsDict['byIsolationMVA3newDMwLTraw_2'][0] = iChain.t2ByIsolationMVA3newDMwLTraw
        syncVarsDict['byIsolationMVA3oldDMwLTraw_2'][0] = iChain.t2ByIsolationMVA3oldDMwLTraw
        syncVarsDict['chargedIsoPtSum_2'][0] = iChain.t2ChargedIsoPtSum
        syncVarsDict['decayModeFinding_2'][0] = iChain.t2DecayModeFinding
        syncVarsDict['decayModeFindingNewDMs_2'][0] = iChain.t2DecayModeFindingNewDMs
        syncVarsDict['neutralIsoPtSum_2'][0] = iChain.t2NeutralIsoPtSum
        syncVarsDict['puCorrPtSum_2'][0] = iChain.t2PuCorrPtSum

        syncVarsDict['m_vis'][0] = iChain.t1_t2_Mass
        syncVarsDict['m_sv'][0] = iChain.t1_t2_SVfitMass

        syncVarsDict['jpt_1'][0] = iChain.jet1Pt
        syncVarsDict['jeta_1'][0] = iChain.jet1Eta
        syncVarsDict['jphi_1'][0] = iChain.jet1Phi
        syncVarsDict['jmva_1'][0] = iChain.jet1PUMVA
        syncVarsDict['jpt_2'][0] = iChain.jet2Pt
        syncVarsDict['jeta_2'][0] = iChain.jet2Eta
        syncVarsDict['jphi_2'][0] = iChain.jet2Phi
        syncVarsDict['jmva_2'][0] = iChain.jet2PUMVA


options = opts()

r.gStyle.SetOptStat(0)

def loop_one_sample(iSample, iLocation, iXS):
    if 'data' in iSample:
        isData = True
    else:
        isData = False
    if 'emb' in iSample:
        isEmbedded = True
    else:
        isEmbedded = False
    if 'H2hh' in iSample:
        isSignal = True
    else:
        isSignal = False

    sync = options.sync
        
    cutFlow = r.TH1F('cutFlow', '', len(xLabels), 0, len(xLabels))
    tool.addHistFromFiles(dirName=iLocation, histName = "tt/cutFlow", hist = cutFlow, xAxisLabels=xLabels)
    cutFlow.SetName('preselection')

    folderName = options.folderName
    iChain = r.TChain("tt/final/Ntuple")
    nEntries = tool.addFiles(ch=iChain, dirName=iLocation, knownEventNumber=0, printTotalEvents=True, blackList='')
    iChain.SetBranchStatus("*",1)
    #set up vars dict
    charVarsDict = setUpCharVarsDict()
    floatVarsDict = setUpFloatVarsDict()
    intVarsDict = setUpIntVarsDict()
    syncVarsDict = None

    iChain.LoadTree(0)
    oTree = iChain.GetTree().CloneTree(0)
    iSample = iSample + '_%s' %('all' if options.nevents == "-1" else options.nevents)
    if sync:
        iFile = r.TFile("%s/%s_SYNC.root" %(options.location,iSample),"recreate")
    else:
        iFile = r.TFile("%s/%s.root" %(options.location,iSample),"recreate")

    #setup branches
    for iVar in charVarsDict.keys():
        oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
    for iVar in floatVarsDict.keys():
        oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
    for iVar in intVarsDict.keys():
        oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/I" %iVar)
    
    if sync:
        syncVarsDict = setUpSyncVarsDict()
        for iVar in syncVarsDict.keys():
            oTree.Branch("%s" %iVar, syncVarsDict[iVar], "%s/F" %iVar)

    charVarsDict['sampleName'][:31] = iSample
    intVarsDict['initEvents'][0] = int(cutFlow.GetBinContent(1))
    floatVarsDict['xs'][0] = iXS
    counter = 0

    preEvt = -1
    preLumi = -1
    preRun = -1
    bestPair = -1
    bestValue = -1.0

    preEvt = 0
    preLumi = 0
    preRun = 0

    if options.pairChoice == 'iso':
        bestValue = 999.0

    for iEntry in range(nEntries):
        iChain.LoadTree(iEntry)
        iChain.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s/%s.root' % (options.location, iSample), iEntry-1)

        if counter == int(options.nevents):
            break

        #save last event
        if iEntry == nEntries - 1:
            iChain.LoadTree(bestPair)
            iChain.GetEntry(bestPair)
            saveExtra(iChain, floatVarsDict, syncVarsDict, sync)
            oTree.Fill()
            counter += 1

        if not passCut(iChain):
            continue
        if (preEvt == 0 and preLumi == 0 and preRun == 0) or (preEvt == iChain.evt and preLumi == iChain.lumi and preRun == iChain.run):
            bestPair, bestValue = findRightPair(iChain, iEntry, bestPair, bestValue, options.pairChoice)

        else:
            iChain.LoadTree(bestPair)
            iChain.GetEntry(bestPair)
            saveExtra(iChain, floatVarsDict, syncVarsDict, sync)
            oTree.Fill()
            counter += 1
            bestPair = -1
            bestValue = -1.0
            if options.pairChoice == 'iso':
                bestValue = 999.0
        preEvt = iChain.evt
        preLumi = iChain.lumi
        preRun = iChain.run

    print '  -- saved %d events' %(counter)
    tool.addEventsCount2Hist(hist = cutFlow, count = counter, labelName = 'myCut')
    iFile.cd()
    cutFlow.Write()
    oTree.Write()
    iFile.Close()


def go():
#     setupLumiReWeight()
    for iSample, iLocation, xs in enVars.sampleLocations:
        loop_one_sample(iSample, iLocation, float(xs))
#     freeLumiReWeight()


if __name__ == "__main__":
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
