#!/usr/bin/env python

import ROOT as r
import tool
import os
import cProfile
from cfg import enVars
from array import array
import optparse
# import kinfit
from cutSampleTools import *
import trigger
import data_certification
import syncTools

r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000
r.gStyle.SetOptStat("e")

xLabels = ['Topology', 'Leg0Pt', 'Leg0Eta','Leg1Pt', 'Leg1Eta', 't_UniqueByPt', 'myCut']

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

matchedGenJet = lvClass()
mGenJet1 = lvClass()
mGenJet2 = lvClass()
CSVJet1 = lvClass()
CSVJet2 = lvClass()
combinedJJ = lvClass()
sv4Vec = lvClass()

# kinfit.setup()

def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates
 
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
            'met', 'metphi', 'mvamet', 'mvametphi', 'pzetavis', 'pzetamiss',
            'jpt_1', 'jeta_1', 'jphi_1', 'jrawf_1', 'jmva_1', 'jpfid_1', 'jpuid_1', 'jcsv_1',
            'jpt_2', 'jeta_2', 'jphi_2', 'jrawf_2', 'jmva_2', 'jpfid_2', 'jpuid_2', 'jcsv_2',
            'dXY_1','dXY_2'
            ]

    for iName in names:
        varDict[iName] = array('f', [0.])

    return varDict

def setUpIntVarsDict():
    varDict = {}
    names = ['nElectrons', 'nMuons', 'initEvents', 'ZTT', 'ZLL', 'njets', 'nbtag', 'njetspt20', 'njetingap20', 'njetingap', 'sumWeights']
    for iName in names:
        varDict[iName] = array('l', [0])
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
    parser.add_option("--FS", dest="FS", default='tt', help="final state product, et, tt")
    parser.add_option("--inclusive", dest="inclusive", default=False, action="store_true", help="apply inclusive cut")
    parser.add_option("--antiIso", dest="antiIso", default=False, action="store_true", help="apply inclusive cut")
    parser.add_option("--antiTauIso", dest="antiTauIso", default=False, action="store_true", help="apply inclusive cut")
    parser.add_option("--cat", dest="category", default='all', help="apply category cut")

    options, args = parser.parse_args()

    return options

options = opts()

r.gStyle.SetOptStat(0)

def loop_one_sample(iSample, iLocation, iXS, finalState, chain = None, outPutFileName = None, histos = None):
    print 'Ntuplizing sample [%s] for channel [%s]' %(iSample, finalState)

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

    #histograms
    if not chain:        
        cutFlow = r.TH1D('cutFlow', '', len(xLabels), 0, len(xLabels))
        eventCount = r.TH1D('eventCount', '', 1, -0.5, 0.5)
        eventWeights = r.TH1D('eventWeights', '', 2, 0, 2)
        eventCountWeighted = r.TH1D('eventCountWeighted', '', 1, -0.5, 0.5)
        if not isData:
            tool.addHistFromFiles(dirName=iLocation, histName = "%s/eventCount" %finalState, hist = eventCount, xAxisLabels=['eventCount'])
            print 'initEvents: %i' %eventCount.GetBinContent(1)
            tool.addHistFromFiles(dirName=iLocation, histName = "%s/eventCountWeighted" %finalState, hist = eventCountWeighted, xAxisLabels=['eventCountWeighted'])
            print 'initWeightedEvents: %i' %eventCountWeighted.GetBinContent(1)
        folderName = options.folderName
        iChain = r.TChain("%s/final/Ntuple" %finalState)
    else:
        iChain = chain
    nEntries = tool.addFiles(ch=iChain, dirName=iLocation, knownEventNumber=0, printTotalEvents=True, blackList='')
    iChain.SetBranchStatus("*",1)

    #set up vars dict
    charVarsDict = setUpCharVarsDict()
    floatVarsDict = setUpFloatVarsDict()
    intVarsDict = setUpIntVarsDict()
    syncVarsDict = None

    type = 'baseline'
    if options.inclusive:
        type = 'inclusive'
    if options.antiIso:
        type = 'antiIso'
    if options.antiTauIso:
        type = 'antiTauIso'

    cat = ''
    if options.category != 'all':
        cat = '_%s' %options.category
    
    iChain.LoadTree(0)
    oTree = iChain.GetTree().CloneTree(0)
    iSample = iSample + '_%s' %('all' if options.nevents == "-1" else options.nevents)
    
    if outPutFileName:
        outputFileName = outPutFileName
    else:
        if sync:
            outputFileName = "%s/%s%s_SYNC_%s_%s.root" %(options.location, iSample, cat, finalState, type)
        else:
            outputFileName = "%s/%s%s_%s_%s.root" %(options.location, iSample, cat, finalState, type)
    iFile = r.TFile(outputFileName,"recreate")

    #setup branches
    for iVar in charVarsDict.keys():
        oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
    for iVar in floatVarsDict.keys():
        oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
    for iVar in intVarsDict.keys():
        oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/L" %iVar)
    
    if sync:
        syncVarsDict = setUpSyncVarsDict()
        for iVar in syncVarsDict.keys():
            oTree.Branch("%s" %iVar, syncVarsDict[iVar], "%s/F" %iVar)

    charVarsDict['sampleName'][:31] = iSample
    intVarsDict['initEvents'][0] = int(eventCount.GetBinContent(1))
    intVarsDict['sumWeights'][0] = int(eventCountWeighted.GetBinContent(1))

    floatVarsDict['xs'][0] = iXS
    
    counter = 0

    preEvt = -1
    preLumi = -1
    preRun = -1
    bestPair = -1
    ptValue = -1.0
    ptValue_1 = -1.0

    isoValue = 9999.0
    isoValue_1 = 9999.0

    preEvt = 0
    preLumi = 0
    preRun = 0
    weightedNEvents = 0

    cutCounter = {}

    for iEntry in range(nEntries):
        iChain.LoadTree(iEntry)
        iChain.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s' %(outputFileName), iEntry-1)

        if not isData:
            if iChain.genEventWeight < 0:
                weightedNEvents -= 1
            else:
                weightedNEvents += 1

        passSelection =  passCatSelection(iChain, options.category, finalState)
        passCuts, comment = passCut(iChain, finalState, isData)
        passCuts = passCuts*passSelection

        if comment not in cutCounter.keys():
            cutCounter[comment] = 1
        else:
            cutCounter[comment] += 1

        if iEntry == int(options.nevents):
            break

        if (not passCuts) and (iEntry != nEntries - 1):
            continue

        if (preEvt == 0 and preLumi == 0 and preRun == 0) or (preEvt == iChain.evt and preLumi == iChain.lumi and preRun == iChain.run):
            if passCuts:
                bestPair, isoValue_1, isoValue, ptValue_1, ptValue = findRightPair(iChain, iEntry, bestPair, isoValue_1, isoValue, ptValue_1, ptValue, options.pairChoice, finalState)

            if (iEntry == nEntries - 1): #save last event
                iChain.LoadTree(bestPair)
                iChain.GetEntry(bestPair)
                passAdditional, comments = passAdditionalCuts(iChain, finalState, type, isData)
                if passAdditional:
                    syncTools.saveExtra(iChain, floatVarsDict, syncVarsDict, intVarsDict, sync, finalState)
                    oTree.Fill()
                    counter += 1

        elif bestPair != -1:
            #store best pair
            iChain.LoadTree(bestPair)
            iChain.GetEntry(bestPair)
            passAdditional, comments = passAdditionalCuts(iChain, finalState, type, isData)
            if passAdditional:
                syncTools.saveExtra(iChain, floatVarsDict, syncVarsDict, intVarsDict, sync, finalState)
                oTree.Fill()
                counter += 1

            #reset best pair info
            bestPair = -1
            ptValue = -1.0
            isoValue = 999.0
            ptValue_1 = -1.0
            isoValue_1 = 999.0

            #reload to current entry
            iChain.LoadTree(iEntry)
            iChain.GetEntry(iEntry)
            bestPair, isoValue_1, isoValue, ptValue_1, ptValue = findRightPair(iChain, iEntry, bestPair, isoValue_1, isoValue, ptValue_1, ptValue, options.pairChoice, finalState)

            if (iEntry == nEntries - 1) and passCuts:  #save last event, it's already loaded with the current value
                passAdditional, comments = passAdditionalCuts(iChain, finalState, type, isData)
                if passAdditional:
                    syncTools.saveExtra(iChain, floatVarsDict, syncVarsDict, intVarsDict, sync, finalState)
                    oTree.Fill()
                    counter += 1

        preEvt = iChain.evt
        preLumi = iChain.lumi
        preRun = iChain.run

    print '  -- saved %d events' %(counter)
    print cutCounter
    tool.addEventsCount2Hist(hist = cutFlow, count = counter, labelName = 'myCut')
    iFile.cd()
    if not histos:
        eventWeights.Fill(0.5, nEntries)
        eventWeights.Fill(1.5, weightedNEvents)
        eventWeights.Write()
        eventCountWeighted.Write()
        eventCount.Write()
    else:
        for iHist in histos:
            iHist.Write()
    oTree.Write()
    iFile.Close()


def go():
#     setupLumiReWeight()
    finalStates = expandFinalStates(options.FS)
    if not finalStates:
        return 0

    for iSample, iLocation, xs, fs in enVars.sampleLocations:
        if fs != '':
            loop_one_sample(iSample, iLocation, float(xs), fs)
        else:
            for iFS in finalStates:
                loop_one_sample(iSample, iLocation, float(xs), iFS)
#     freeLumiReWeight()


if __name__ == "__main__":
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
