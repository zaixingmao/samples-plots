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
#import data_certification
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
    dist = [0.000829312873542,
            0.00124276120498,
            0.00339329181587,
            0.00408224735376,
            0.00383036590008,
            0.00659159288946,
            0.00816022734493,
            0.00943640833116,
            0.0137777376066,
            0.017059392038,
            0.0213193035468,
            0.0247343174676,
            0.0280848773878,
            0.0323308476564,
            0.0370394341409,
            0.0456917721191,
            0.0558762890594,
            0.0576956187107,
            0.0625325287017,
            0.0591603758776,
            0.0656650815128,
            0.0678329011676,
            0.0625142146389,
            0.0548068448797,
            0.0503893295063,
            0.040209818868,
            0.0374446988111,
            0.0299661572042,
            0.0272024759921,
            0.0219328403791,
            0.0179586571619,
            0.0142926728247,
            0.00839941654725,
            0.00522366397213,
            0.00224457976761,
            0.000779274977993,
            0.000197066585944,
            7.16031761328e-05,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
            ]
    dist = [1.78653e-05 ,2.56602e-05 ,5.27857e-05 ,8.88954e-05 ,0.000109362 ,0.000140973 ,0.000240998 ,0.00071209 ,0.00130121 ,0.00245255 ,0.00502589 ,0.00919534 ,0.0146697 ,0.0204126 ,0.0267586 ,0.0337697 ,0.0401478 ,0.0450159 ,0.0490577 ,0.0524855 ,0.0548159 ,0.0559937 ,0.0554468 ,0.0537687 ,0.0512055 ,0.0476713 ,0.0435312 ,0.0393107 ,0.0349812 ,0.0307413 ,0.0272425 ,0.0237115 ,0.0208329 ,0.0182459 ,0.0160712 ,0.0142498 ,0.012804 ,0.011571 ,0.010547 ,0.00959489 ,0.00891718 ,0.00829292 ,0.0076195 ,0.0069806 ,0.0062025 ,0.00546581 ,0.00484127 ,0.00407168 ,0.00337681 ,0.00269893 ,0.00212473 ,0.00160208 ,0.00117884 ,0.000859662 ,0.000569085 ,0.000365431 ,0.000243565 ,0.00015688 ,9.88128e-05 ,6.53783e-05 ,3.73924e-05 ,2.61382e-05 ,2.0307e-05 ,1.73032e-05 ,1.435e-05 ,1.36486e-05 ,1.35555e-05 ,1.37491e-05 ,1.34255e-05 ,1.33987e-05 ,1.34061e-05 ,1.34211e-05 ,1.34177e-05 ,1.32959e-05 ,1.33287e-05] #https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_20_patchX/SimGeneral/MixingModule/python/mix_2016_25ns_Moriond17MC_PoissonOOTPU_cfi.py
    pileup = r.TH1F('pileup', '', 75, 0, 75)
    pileup.Sumw2()
    outputFileName = "%s/MC_75bins.root" %(options.location)
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
