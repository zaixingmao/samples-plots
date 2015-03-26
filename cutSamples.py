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
    names = ['genHMass', 'xs']
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
    if options.pairChoice == 'iso':
        bestValue = 999.0

    for iEntry in range(nEntries):
        iChain.LoadTree(iEntry)
        iChain.GetEntry(iEntry)

        if counter == int(options.nevents):
            break

        bestPair, bestValue = findRightPair(iChain, iEntry, bestPair, bestValue, options.pairChoice)


        if not passCut(iChain):
            continue

        #check if the next entry is the same event
        curEvt = iChain.evt
        curLumi = iChain.lumi
        curRun = iChain.run
        if iEntry == nEntries - 1:
            iChain.LoadTree(bestPair)
            iChain.GetEntry(bestPair)

            genTau1.SetCoordinates(iChain.t1GenPt, iChain.t1GenEta, iChain.t1GenPhi, iChain.t1GenMass)
            genTau2.SetCoordinates(iChain.t2GenPt, iChain.t2GenEta, iChain.t2GenPhi, iChain.t2GenMass)
            floatVarsDict['genHMass'][0] = (genTau1+genTau2).mass()
            oTree.Fill()
            counter += 1
            tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s/%s.root' % (options.location, iSample), iEntry-1)

        else:
            iChain.LoadTree(iEntry+1)
            iChain.GetEntry(iEntry+1)
            if (iChain.evt != curEvt) or (iChain.lumi != curLumi) or (iChain.run != curRun):
                iChain.LoadTree(bestPair)
                iChain.GetEntry(bestPair)
                genTau1.SetCoordinates(iChain.t1GenPt, iChain.t1GenEta, iChain.t1GenPhi, iChain.t1GenMass)
                genTau2.SetCoordinates(iChain.t2GenPt, iChain.t2GenEta, iChain.t2GenPhi, iChain.t2GenMass)
                floatVarsDict['genHMass'][0] = (genTau1+genTau2).mass()

                oTree.Fill()
                counter += 1
                tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s/%s.root' % (options.location, iSample), iEntry-1)
                bestPair = -1
                bestValue = -1.0
                if options.pairChoice == 'iso':
                    bestValue = 999.0

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
