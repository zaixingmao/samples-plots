#!/usr/bin/env python
import ROOT as r
import tool
from array import array

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs


def getScales(dir, fileNames):
    yieldsHist = {}
    xs = {}
    scales = {}
    iFiles = []
    iTrees = []
    for cat in fileNames.keys():
        iFiles.append(r.TFile("%s/%s" %(dir, fileNames[cat])))
        iTrees.append(iFiles[len(iFiles)-1].Get('eventTree'))
        yieldsHist[cat] = r.TH1F(cat, "", 6, 4, 10)
        iTrees[len(iTrees)-1].Draw("LHEProduct >> %s" %cat, "xs/initEvents")
        iTrees[len(iTrees)-1].GetEntry(0)
        xs[cat] = iTrees[len(iTrees)-1].xs
    for i in range(2,6,1):
        scales['%ijet' %(i-1)] = (yieldsHist['inclusive'].GetBinContent(i+1)+0.0)/(yieldsHist['%ijet' %(i-1)].GetBinContent(i+1)+0.0)

    return scales, xs

def merge(dir= "", type = "DY"):
    if type == 'DY':
        fileNames = {'inclusive': 'DYJetsToLL_all.root',
                     '1jet': 'DY1JetsToLL_all.root',
                     '2jet': 'DY2JetsToLL_all.root',
                     '3jet': 'DY3JetsToLL_all.root',
                     '4jet': 'DY4JetsToLL_all.root',
                    }
    else:
        fileNames = {'inclusive': 'WJetsToLNu_all.root',
                     '1jet': 'W1JetsToLNu_all.root',
                     '2jet': 'W2JetsToLNu_all.root',
                     '3jet': 'W3JetsToLNu_all.root',
                     '4jet': 'W4JetsToLNu_all.root',
                    }
    #first get the right ratios
    scales, xsDict = getScales(dir, fileNames)

    #fill the tree with fixed xs
    outName = dir
    if type == 'DY':
        outName += "dy.root"
    else:
        outName += "WJets.root"
    chain = r.TChain("eventTree")
    for cat in fileNames.keys():
        chain.Add("%s/%s" %(dir, fileNames[cat]), 0)
    chain.SetBranchStatus("*",1)
    chain.SetBranchStatus("xs",0)
    chain.LoadTree(0)
    oTree = chain.GetTree().CloneTree(0)
    xs = array('f', [0.])
    oTree.Branch("xs", xs, "xs/F")
    oFile = r.TFile(outName, 'recreate')
    nEntries = chain.GetEntries()
    for iEntry in range(nEntries):
        chain.LoadTree(iEntry)
        chain.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Combining multiple jet files %s' %outName, iEntry-1)
        if chain.sampleName == 'DYJetsToLL_all' or chain.sampleName == 'WJetsToLNu_all':
            if chain.LHEProduct != 5:
                continue
            xs[0] = xsDict['inclusive']
        else:
            cat = chain.sampleName[chain.sampleName.find("Jets") - 1: chain.sampleName.find("Jets")] + 'jet'
            xs[0] = xsDict[cat]*scales[cat]
        oTree.Fill()
    print xsDict, scales

    oFile.cd()
    oTree.Write()
    oFile.Close()

merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOn/", type = "DY")
