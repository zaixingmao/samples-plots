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

    options, args = parser.parse_args()

    return options

options = opts()

dataLocations = {'em': '/hdfs/store/user/zmao/dataTake2_noSVFit/data_MuonEG_Run2015B_PromptReco_50ns/',
                'et':'/hdfs/store/user/zmao/dataTake2_noSVFit/data_Electron_Run2015B_PromptReco_50ns/',
                'mt':'/hdfs/store/user/zmao/dataTake2_noSVFit/data_Muon_Run2015B_PromptReco_50ns/',
                'tt':'/hdfs/store/user/zmao/dataTake2_t/data_Tau_Run2015B_PromptReco_50ns/'
                }


def loop_one_sample(iSample, iLocation):
    print 'making sample [%s]' %(iSample)

    if 'data' in iSample:
        isData = True
    else:
        isData = False
        
    pileup = r.TH1F('pileup', '', 60, 0, 60)

    if isData:
        outputFileName = "%s/data_600bins.root" %(options.location)
    else:
        outputFileName = "%s/MC_600bins.root" %(options.location)
    iFile = r.TFile(outputFileName,"recreate")

    for finalState in ['et', 'em', 'mt', 'tt']:
        iChain = r.TChain("%s/final/Ntuple" %finalState)
        if isData:
            iLocation = dataLocations[finalState]

        nEntries = tool.addFiles(ch=iChain, dirName=iLocation, knownEventNumber=0, printTotalEvents=True, blackList='')
        iChain.SetBranchStatus("*",0)
        iChain.SetBranchStatus("nvtx",1)

        iChain.LoadTree(0)

        for iEntry in range(nEntries):
            iChain.LoadTree(iEntry)
            iChain.GetEntry(iEntry)
            tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s' %(outputFileName), iEntry-1)
            pileup.Fill(iChain.nvtx)

    iFile.cd()

    pileup.Write()
    iFile.Close()


def go():
#     loop_one_sample('data', '')
    loop_one_sample('MC', '/hdfs/store/user/zmao/testProduction50ns_take2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/')


if __name__ == "__main__":
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
