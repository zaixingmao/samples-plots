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
    names = ['genHMass', 'xs','fullMass', 'mJJ', 'ptJJ', 'etaJJ', 'phiJJ', 'CSVJ1','CSVJ1Pt','CSVJ1Eta','CSVJ1Phi', 'CSVJ1Mass',
             'CSVJ2', 'CSVJ2Pt', 'CSVJ2Eta', 'CSVJ2Phi', 'CSVJ2Mass', 'dRTauTau', 'dRJJ']
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
    parser.add_option("--pair", dest="pairChoice", default="pt", help="which pair")

    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    options, args = parser.parse_args()

    return options


def saveExtra(iChain, floatVarsDict):
    genTau1.SetCoordinates(iChain.t1GenPt, iChain.t1GenEta, iChain.t1GenPhi, iChain.t1GenMass)
    genTau2.SetCoordinates(iChain.t2GenPt, iChain.t2GenEta, iChain.t2GenPhi, iChain.t2GenMass)
    floatVarsDict['genHMass'][0] = (genTau1+genTau2).mass()

    jetsList = [(iChain.jet1CSVBtag, J1.SetCoordinates(iChain.jet1Pt, iChain.jet1Eta, iChain.jet1Phi, iChain.jet1Mass), 'J1'),
                (iChain.jet2CSVBtag, J2.SetCoordinates(iChain.jet2Pt, iChain.jet2Eta, iChain.jet2Phi, iChain.jet2Mass), 'J2'),
                (iChain.jet3CSVBtag, J3.SetCoordinates(iChain.jet3Pt, iChain.jet3Eta, iChain.jet3Phi, iChain.jet3Mass), 'J3'),
                (iChain.jet4CSVBtag, J4.SetCoordinates(iChain.jet4Pt, iChain.jet4Eta, iChain.jet4Phi, iChain.jet4Mass), 'J4'),
                (iChain.jet5CSVBtag, J5.SetCoordinates(iChain.jet5Pt, iChain.jet5Eta, iChain.jet5Phi, iChain.jet5Mass), 'J5'),
                (iChain.jet6CSVBtag, J6.SetCoordinates(iChain.jet6Pt, iChain.jet6Eta, iChain.jet6Phi, iChain.jet6Mass), 'J6')]

    floatVarsDict['CSVJ1'][0], floatVarsDict['CSVJ2'][0], CSVJet1, CSVJet2 = findJetPair(iTree = iChain, jetsList = jetsList, ptThreshold = enVars.jetPtThreshold)

    floatVarsDict['CSVJ1Pt'][0] = CSVJet1.pt()
    floatVarsDict['CSVJ1Eta'][0] = CSVJet1.eta()
    floatVarsDict['CSVJ2Pt'][0] = CSVJet2.pt()
    floatVarsDict['CSVJ2Eta'][0] = CSVJet2.eta()
    floatVarsDict['mJJ'][0] = (CSVJet1 + CSVJet2).mass()

#     sv4Vec.SetCoordinates(iChain.svPt.at(0), iChain.svEta.at(0), iChain.svPhi.at(0), iChain.svMass.at(0))
#     bb = lvClass()
#     bb, floatVarsDict['CSVJ1'][0], floatVarsDict['CSVJ2'][0], CSVJet1, CSVJet2, floatVarsDict['fullMass'][0], floatVarsDict['dRJJ'][0], j1Name, j2Name = findFullMass(jetsList=jetsList, sv4Vec=sv4Vec, ptThreshold = enVars.jetPtThreshold) 


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

    iChain.LoadTree(0)
    oTree = iChain.GetTree().CloneTree(0)
    iSample = iSample + '_%s' %('all' if options.nevents == "-1" else options.nevents)
    iFile = r.TFile("%s/%s.root" %(options.location,iSample),"recreate")

    #setup branches
    for iVar in charVarsDict.keys():
        oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
    for iVar in floatVarsDict.keys():
        oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
    for iVar in intVarsDict.keys():
        oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/I" %iVar)

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
            saveExtra(iChain, floatVarsDict)
            oTree.Fill()
            counter += 1

        if not passCut(iChain):
            continue
        if (preEvt == 0 and preLumi == 0 and preRun == 0) or (preEvt == iChain.evt and preLumi == iChain.lumi and preRun == iChain.run):
            bestPair, bestValue = findRightPair(iChain, iEntry, bestPair, bestValue, options.pairChoice)

        else:
            iChain.LoadTree(bestPair)
            iChain.GetEntry(bestPair)
            saveExtra(iChain, floatVarsDict)
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
