#!/usr/bin/env python

import ROOT as r
import math
from array import array
from plots_dataDrivenQCDandWJ import getZPrimeXS


lumi = 35867

def getCat(sampleName):
    cats = {"VV": ("ZZTo2L2Q", "VVTo2L2Nu", "WZTo1L1Nu2Q", "WZTo1L3Nu", "ZZTo4L", "WWTo1L1Nu2Q", "WZTo2L2Q", "WZTo3LNu"),
            "TT": ("ST_antiTop_tW", "ST_top_tW", "ST_s-channel", "ST_t-channel_antiTop_tW", "ST_t-channel_top_tW", "TTJets"),
            "WJets": ("WJetsLoose",),
            "DYJets": ("DY_M-50to200", "DY_M-200to400", "DY_M-400to500", "DY_M-500to700", "DY_M-700to800", "DY_M-800to1000", "DY_M-1000to1500", "DY_M-1500to2000", "DY_M-2000to3000"),
            "QCD": ("QCDLoose",),
#             "SMHiggs": ("vbfH","ggH"),
            "Observed": ("dataTight",),
            }
    for iKey in cats.keys():
        for iSample in cats[iKey]:
            if iSample in sampleName:
                return iKey
    return ''

def cleanEmptyBin(hist):
    nBins = hist.GetNbinsX()
    for i in range(1, nBins+1):
        content = hist.GetBinContent(i)
        error = hist.GetBinError(i)
        if content < 0:
            hist.SetBinContent(i, 0)
            hist.SetBinError(i, math.sqrt(content**2 + error**2))


def scaleHist(hist, SF, SF_unc):
    hist.Scale(SF)
    for i in range(1, hist.GetNbinsX()+1):
        bin_unc = hist.GetBinError(i)
        add_unc = hist.GetBinContent(i)*SF_unc/SF
        hist.SetBinError(i, math.sqrt(bin_unc**2 + add_unc**2))

def setUpHistDict(bins):
    cats = ["VV", "TT", "WJets", "DYJets", "QCD", "Observed"]#, "SMHiggs"]
    histDict = {}
    for i in cats:
        histDict[i] = r.TH1F(i, "", len(bins)-1, bins)
    return histDict

def run(inputFile, FS, sys, varName):
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
    bins = array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600, 900, 1200, 1700])

    histDict = setUpHistDict(bins)
    totalBKG = r.TH1F('total_bkg', "", len(bins)-1, bins)
    oFile = r.TFile("/user_data/zmao/datacard_histo_2016/%s/datacard_2016_%s_%s%s.root" %(FS, varName, FS, sys), 'recreate')

    for i in range(nEntries):
        tree.GetEntry(i)
        weight = tree.xs*lumi*tree.triggerEff*tree.PUWeight*tree.genEventWeight/tree.initSumWeights
        value = getattr(tree, varName)
        if value >= bins[len(bins)-1]:
            value = (bins[len(bins)-1] + bins[len(bins)-2])/2.
        if value < bins[0]:
            value = (bins[0] + bins[1])/2.
        sampleName = getCat(tree.sampleName)
        if sampleName != '':
            histDict[sampleName].Fill(value, weight)
        elif "Zprime" in tree.sampleName:
            mass = (tree.sampleName)[tree.sampleName.find("_")+1:tree.sampleName.rfind("0")+1]
            weight = weight*getZPrimeXS(mass)
            sampleName = (tree.sampleName)[:tree.sampleName.rfind("0")+1]
            if sampleName not in histDict.keys():
                histDict[sampleName] = r.TH1F(sampleName, "", len(bins)-1, bins)
            histDict[sampleName].Fill(value, weight)
    scaleHist(histDict["WJets"], WJets_SF, WJets_SF_unc)
    scaleHist(histDict["QCD"], QCD_SF, QCD_SF_unc)

    oFile.cd()
    for ikey in histDict.keys():
        cleanEmptyBin(histDict[ikey])
        if ikey != "Observed":
            if "Zprime" not in ikey:
                totalBKG.Add(histDict[ikey])
            print "%s: %.2f" %(ikey, histDict[ikey].Integral()) 
            histDict[ikey].Write()
    totalBKG.Write()
    oFile.Close()    

sys = '_tauECDown'

FS = ['mt', 'et']
vars = ['m_effective']
for iFS in FS:
    for iVar in vars:
        run("/user_data/zmao/datacard_2016/Lumi36p8_reMiniAOD_new/combined_%s_withPUWeight%s.root" %(iFS,sys), iFS, sys, iVar) 
