#!/usr/bin/env python

import ROOT as r
import os
from array import array

r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def getXSEff(tree, nInit):
    genHTDistribution = r.TH1D("genHTDistribution", "", 700, 0, 700)
    tree.Draw("genHT >> genHTDistribution")
#     print nInit
    result = {}
    tree.GetEntry(0)
    xs = tree.xs
    result['100to200'] = xs*(genHTDistribution.Integral(100, 200)+0.0)/nInit
    result['200to400'] = xs*(genHTDistribution.Integral(200, 400)+0.0)/nInit
    result['400to600'] = xs*(genHTDistribution.Integral(400, 600)+0.0)/nInit
    result['600toInf'] = xs*(genHTDistribution.Integral(600, 702)+0.0)/nInit
    return result


def combineSamples(location, fileList, method):
    #store HT-0to100
    oName = ''
    for iFile in fileList:
        if 'DY' not in iFile:
            oName = iFile[:iFile.find("_all")] + '_HT-0to100' + iFile[iFile.find("_all"):]
            iName = iFile
        else:
            oName = iFile[:iFile.find("-50")] + '-50to150' + iFile[iFile.find("-50")+3:]

            iName = iFile
    ifile = r.TFile("%s/%s" %(location, iName))    
    iTree = ifile.Get("Ntuple")
    eventWeights = ifile.Get("eventWeights")
    eventCountWeighted = ifile.Get("eventCountWeighted")
    eventCount = ifile.Get("eventCount")
    pdfInits = []

    oFile = r.TFile("%s/%s" %(location, oName), 'recreate')
    oTree = iTree.CloneTree(0)
    iTree.SetBranchStatus("*",1)
    nEntries = iTree.GetEntries()
    for i in range(nEntries):
        iTree.GetEntry(i)
        if 'DY' not in iFile:
            if iTree.genHT < 100:
                oTree.Fill()
        else:
            if iTree.X_to_ll < 150:
                oTree.Fill()
    oFile.cd()
    eventWeights.Write()
    eventCountWeighted.Write()
    eventCount.Write()
#     for i in range(100):
#         pdfInits.append(ifile.Get("eventCountWeightedPDF_%i" %i))
#         pdfInits[i].Write()

    oTree.Write()
    oFile.Close()

#     xs_eff = getXSEff(iTree, ifile.Get("eventCount").GetBinContent(1))
#     print xs_eff


    if method != 'LO':
        oFile = r.TFile("%s/%s" %(location, oName), 'recreate')
        inputFile = []
        inputTree = []
        outputFile = []
        outputTree = []
        xs = array('f', [0.])

        for iFile in fileList:
            if 'HT' in iFile:
                inputFile = r.TFile("%s/%s" %(location, iFile))
                inputTree = inputFile.Get('Ntuple')
                inputTree.SetBranchStatus("*",1)
                inputTree.SetBranchStatus("xs",0)
                outputFile = r.TFile("%s/%s_xs_eff.root" %(location, iFile[:iFile.find('.root')]), 'recreate')
                outputTree = inputTree.CloneTree(0)
                nEntries = inputTree.GetEntries()
                outputTree.Branch("xs", xs, "xs/F")
                xs[0] = xs_eff[iFile[iFile.find('HT') + 3:iFile.find('_all')]]*(inputFile.Get("eventCount").GetBinContent(1)+0.0)/nEntries
                print "for sample %s the effective xs is: %.2f" %(iFile[iFile.find('HT') + 3:iFile.find('_all')], xs[0])

                for i in range(nEntries):
                    inputTree.GetEntry(i)
                    outputTree.Fill()
                outputFile.cd()
                outputTree.Write()
                outputFile.Close()
                inputFile.Close()
                


process = ['DY-50_LO', 'WJets']#]
# process = ['DY-50_LO']#]

# process = []#, 'WJets_LO']#'DY-50']#, 'DY-50_LO']#]

FS = ['em']
binned = ['']#, '_HT-100to200', '_HT-200to400', '_HT-600toInf']#'_HT-400to600',
tail = 'noIso'
location = '/uscms/home/zmao/nobackup/2016_signalRegion/'
#location = '/nfs_scratch/zmao/Nov18Prodruction_ntuple/MVANonTrigWP80_singleEforEMu/'
method = 'LO'
for iProcess in process:
    for iFS in FS:
        print 'final state: [%s]' %iFS
        fileList = []
        for iBin in binned:
            fileList.append("%s%s_all_SYNC_%s_%s.root" %(iProcess, iBin, iFS, tail))
        combineSamples(location, fileList, method)

