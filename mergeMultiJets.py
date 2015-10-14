#!/usr/bin/env python
import ROOT as r
import tool
from array import array
import makeWholeSample_cfg
import makeWholeTools2

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

def getScalesWithCut(dir, fileNames, cut='OSTight', massWindow=True, type = 'DY'):
    yieldsHist = {}
    xs = {}
    scales = {}
    iFiles = []
    iTrees = []
    for cat in fileNames.keys():
        iFiles.append(r.TFile("%s/%s" %(dir, fileNames[cat])))
        iTrees.append(iFiles[len(iFiles)-1].Get('eventTree'))
        yieldsHist[cat] = r.TH1F(cat, "", 6, 4, 10)
        nEntries = iTrees[len(iTrees)-1].GetEntries()
        iTrees[len(iTrees)-1].GetEntry(0)
        xs[cat] = iTrees[len(iTrees)-1].xs

        for i in range(nEntries):
            iTrees[len(iTrees)-1].GetEntry(i)
            signSelection, isoSelection, bTagSelection = makeWholeTools2.findCategory(tree = iTrees[len(iTrees)-1], 
                                                                                      iso = 1.0, 
                                                                                      option = 'iso',
                                                                                      isData = False,
                                                                                      relaxedRegionOption = makeWholeSample_cfg.Relax,
                                                                                      isEmbed = False,
                                                                                      usePassJetTrigger = makeWholeSample_cfg.usePassJetTrigger,
                                                                                      nBtag = '')
            if signSelection == None or isoSelection == None:
                continue
            if iTrees[len(iTrees)-1].HLT_Any == 0:
                continue
            if type == 'DY' and iTrees[len(iTrees)-1].ZTT == 0:
                continue
            if type == 'ZLL' and iTrees[len(iTrees)-1].ZLL == 0:
                continue
            if  massWindow and not makeWholeTools2.passCut(iTrees[len(iTrees)-1], 'iso'):
                continue
            if cut != signSelection+isoSelection:
                continue
            yieldsHist[cat].Fill(iTrees[len(iTrees)-1].LHEProduct, iTrees[len(iTrees)-1].xs/(iTrees[len(iTrees)-1].initEvents+0.0))

    for i in range(2,6,1):
        scales['%ijet' %(i-1)] = (yieldsHist['inclusive'].GetBinContent(i+1)+0.0)/(yieldsHist['%ijet' %(i-1)].GetBinContent(i+1)+0.0)

    return scales, xs


def merge(dir= "", type = "DY", cut = '', massWindow = False):
    if type == 'DY' or type == 'ZLL':
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
    if cut == '':
        scales, xsDict = getScales(dir, fileNames)
    else:
        scales, xsDict = getScalesWithCut(dir, fileNames, cut, massWindow, type)

    #fill the tree with fixed xs
    outName = dir
    appendName = ''
    if cut != '':
        appendName += "_%s" %cut
    if massWindow:
        appendName += "_massWindow"

    if type == 'DY':
        outName += "dy%s.root" %appendName
    elif type == 'ZLL':
        outName += "ZLL%s.root" %appendName
    else:
        outName += "WJets%s.root" %appendName

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
        if ('DYJetsToLL' in chain.sampleName) or ('WJetsToLNu' in chain.sampleName):
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

variations = ['bMis']#'tauUp', 'tauDown', 'jetUp', 'jetDown']
for iVar in variations:
    merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOn/%s/" %iVar, type = "DY", cut= "", massWindow = False)
    merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOn/%s/" %iVar, type = "DY", cut= "OSTight", massWindow = False)
#     merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOff/%s/" %iVar, type = "WJets", cut= "OSTight", massWindow = False)

# 
# merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOn/bMis/", type = "DY", cut= "", massWindow = False)
# merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOn/bMis/", type = "DY", cut= "OSTight", massWindow = False)
# merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOn/bSys/", type = "DY", cut= "", massWindow = False)
# merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOn/bSys/", type = "DY", cut= "OSTight", massWindow = False)

# merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOff/bMis/", type = "WJets", cut= "OSTight", massWindow = False)
# merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOff/bSys/", type = "WJets", cut= "OSTight", massWindow = False)


# merge(dir= "/nfs_scratch/zmao/samples_Iso/tauESOff/bMis/", type = "W")
