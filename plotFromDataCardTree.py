#!/usr/bin/env python

import ROOT as r
import math
from array import array


lumi = 12891.5

def getCat(sampleName):
    cats = {"VV": ("ZZTo2L2Q", "VVTo2L2Nu", "WZTo1L1Nu2Q", "WZTo1L3Nu", "ZZTo4L", "WWTo1L1Nu2Q", "WZTo2L2Q", "WZTo3LNu"),
            "TT": ("ST_antiTop_tW", "ST_top_tW", "ST_s-channel", "ST_t-channel_antiTop_tW", "ST_t-channel_top_tW", "TTJets"),
            "WJets": ("WJetsLoose",),
            "DYJets": ("DY_M-50to150", "DY_M-150"),
            "QCD": ("QCDLoose",),
            "Observed": ("dataTight",),
            }
    for iKey in cats.keys():
        for iSample in cats[iKey]:
            if iSample in sampleName:
                return iKey
    return ""


def scaleHist(hist, SF, SF_unc):
    hist.Scale(SF)
    for i in range(1, hist.GetNbinsX()+1):
        bin_unc = hist.GetBinError(i)
        add_unc = hist.GetBinContent(i)*SF_unc/SF
        hist.SetBinError(i, math.sqrt(bin_unc**2 + add_unc**2))

def setUpHistDict(bins):
    cats = ["VV", "TT", "WJets", "DYJets", "QCD", "Observed"]
    histDict = {}
    for i in cats:
        histDict[i] = r.TH1F(i, "", len(bins)-1, bins)
    return histDict

def run(inputFile, FS, varName):
    iFile = r.TFile(inputFile)
    QCD_SF_name = "QCD_Loose_to_Tight"
    WJets_SF_name = "WJets_Loose_to_Tight"
    if FS != 'em':
        QCD_SF_name += "_%s_1prong_3prong" %FS
        WJets_SF_name += "_%s_1prong_3prong" %FS
    else:
        QCD_SF_name += "_%s" %FS
        WJets_SF_name += "_%s" %FS

    QCD_SF = (iFile.Get(QCD_SF_name)).GetBinContent(1)
    QCD_SF_unc = iFile.Get(QCD_SF_name).GetBinError(1)
    WJets_SF = (iFile.Get(WJets_SF_name)).GetBinContent(1)
    WJets_SF_unc = iFile.Get(WJets_SF_name).GetBinError(1)

    tree = iFile.Get("eventTree")
    nEntries = tree.GetEntries()
    
    bins = array('d', range(0, 5000, 5))

    histDict = setUpHistDict(bins)
    totalBKG = r.TH1F('total_bkg', "", len(bins)-1, bins)

    oFile = r.TFile("datacard_2016_%s_%s.root" %(varName, FS), 'recreate')

    for i in range(nEntries):
        tree.GetEntry(i)
        weight = tree.xs*lumi*tree.triggerEff*tree.PUWeight*tree.genEventWeight/tree.initSumWeights
        value = getattr(tree, varName)
        if value >= bins[len(bins)-1]:
            value = (bins[len(bins)-1] + bins[len(bins)-2])/2.
        sampleName = getCat(tree.sampleName)
        if sampleName != '':
            histDict[sampleName].Fill(value, weight)
        elif "Z'" in tree.sampleName:
            sampleName = (tree.sampleName)[:tree.sampleName.rfind(")")+1]
            if sampleName not in histDict.keys():
                histDict[sampleName] = r.TH1F(sampleName, "", len(bins)-1, bins)
            histDict[sampleName].Fill(value, weight)
    scaleHist(histDict["WJets"], WJets_SF, WJets_SF_unc)
    scaleHist(histDict["QCD"], QCD_SF, QCD_SF_unc)

    oFile.cd()
    for ikey in histDict.keys():
        if ikey != "Observed":
            if "Z'" not in ikey:
                totalBKG.Add(histDict[ikey])
            print "%s: %.2f" %(ikey, histDict[ikey].Integral()) 
            histDict[ikey].Write()
    totalBKG.Write()
    oFile.Close()    

FS = 'et'
# run("/user_data/zmao/datacard_2016/combined_%s_withPUWeight.root" %FS, FS, 'm_effective')
run("/user_data/zmao/datacard_2016/combined_%s_withPUWeight.root" %FS, FS, 'm_svfit') 