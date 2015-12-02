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

def make_MC_PUDistribution():
    dist = [4.8551E-07,
            1.74806E-06,
            3.30868E-06,
            1.62972E-05,
            4.95667E-05,
            0.000606966,
            0.003307249,
            0.010340741,
            0.022852296,
            0.041948781,
            0.058609363,
            0.067475755,
            0.072817826,
            0.075931405,
            0.076782504,
            0.076202319,
            0.074502547,
            0.072355135,
            0.069642102,
            0.064920999,
            0.05725576,
            0.047289348,
            0.036528446,
            0.026376131,
            0.017806872,
            0.011249422,
            0.006643385,
            0.003662904,
            0.001899681,
            0.00095614,
            0.00050028,
            0.000297353,
            0.000208717,
            0.000165856,
            0.000139974,
            0.000120481,
            0.000103826,
            8.88868E-05,
            7.53323E-05,
            6.30863E-05,
            5.21356E-05,
            4.24754E-05,
            3.40876E-05,
            2.69282E-05,
            2.09267E-05,
            1.5989E-05,
            4.8551E-06,
            2.42755E-06,
            4.8551E-07,
            2.42755E-07,
            1.21378E-07,
            4.8551E-08]
    pileup = r.TH1F('pileup', '', 50, 0, 50)
    outputFileName = "%s/MC_50bins.root" %(options.location)
    oFile = r.TFile(outputFileName,"recreate")
    for i in range(len(dist)):
        pileup.Fill(i, dist[i])
    oFile.cd()
    pileup.Write()
    oFile.Close()

def loop_one_sample(iSample, iLocation):
    print 'making sample [%s]' %(iSample)

    if 'data' in iSample:
        isData = True
    else:
        isData = False
        
    pileup = r.TH1F('pileup', '', 50, 0, 50)

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
#     go()
    make_MC_PUDistribution()
