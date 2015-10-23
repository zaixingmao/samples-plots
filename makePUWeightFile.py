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
    options, args = parser.parse_args()

    return options

options = opts()

dataLocations = {'em': '/hdfs/store/user/zmao/data_25ns_Spring15_eletronID/data_MuonEG_Run2015C_PromptReco_25ns/',
                'et':'/hdfs/store/user/zmao/data_25ns_Spring15_eletronID/data_Electron_Run2015C_PromptReco_25ns/',
                'mt':'/hdfs/store/user/zmao/nfs_scratch/zmao/data_25ns_Spring15_eletronID/data_Muon_Run2015C_PromptReco_25ns/',
                'tt':'/hdfs/store/user/zmao/data_25ns_Spring15_eletronID/data_Tau_Run2015C_PromptReco_25ns/'
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

    for finalState in ['et', 'em']:#, 'mt', 'tt']:
        print 'running final state: %s' %finalState
        iChain = r.TChain("Ntuple")
        match2 = ''
        if isData:
#             iLocation = dataLocations[finalState]
            match2 = 'data'
        nEntries = tool.addFiles(ch=iChain, dirName=iLocation, knownEventNumber=0, printTotalEvents=True, blackList='', match1 = finalState, match2 = match2)
        iChain.SetBranchStatus("*",0)
        iChain.SetBranchStatus("nvtx",1)

        iChain.LoadTree(0)

        for iEntry in range(nEntries):
            iChain.LoadTree(iEntry)
            iChain.GetEntry(iEntry)
            tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s' %(outputFileName), iEntry-1)
            weight = 1.0
            if not isData:
                if hasattr(iChain, 'genEventWeight'):
                    if iChain.genEventWeight < 0:
                        weight = -1.0
                    pileup.Fill(iChain.nvtx, weight)

            else:
                pileup.Fill(iChain.nvtx, weight)
        print ''
    iFile.cd()

    pileup.Write()
    iFile.Close()


def go():
    loop_one_sample('data', '/user_data/zmao/forPU_Data/')
    loop_one_sample('MC', '/user_data/zmao/forPU_MC')


if __name__ == "__main__":
    go()
