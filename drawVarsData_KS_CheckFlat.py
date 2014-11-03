#!/usr/bin/env python

import ROOT as r
import tool
from operator import itemgetter
import os
from cfg import enVars
import varsList
import optparse
import math
from array import array
import numpy
import random
import draw_cfg

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--variable", dest="varName", default = 'test', help="")
    parser.add_option("--signal", dest="signal", default = '', help="")
    parser.add_option("--logY", dest="logy", default = True, help="")
    parser.add_option("--sigBoost", dest="sigBoost", default = 1.0, help="")
    parser.add_option("--nbins", dest="nbins", default = 0, help="")
    parser.add_option("--useData", dest="useData", default = 'True', help="")
    parser.add_option("--setMax", dest="max", default = 50, help="")
    parser.add_option("--setRangeMin", dest="rangeMin", default = 0, help="")
    parser.add_option("--setRangeMax", dest="rangeMax", default = 100, help="")
    parser.add_option("--location", dest="location", default = '.', help="")
    parser.add_option("--bTag", dest="bTag", default = 'True', help="")
    parser.add_option("--predict", dest="predict", default = 'False', help="")
    parser.add_option("--predictPtBin", dest="predictPtBin", default = 'False', help="")
    parser.add_option("--region", dest="region", default = 'LL', help="")


    options, args = parser.parse_args()
    return options

def conditions(selection):
    if selection == 1:
        return 'OS', 'tight'
    elif selection == 2:
        return 'SS', 'tight'
    elif selection == 3:
        return 'OS', 'relaxed'
    elif selection == 4:
        return 'SS', 'relaxed'
    elif selection == 5:
        return 'OS', 'cut-off with iso3'
    elif selection == 6:
        return 'SS', 'cut-off with iso3'

def getCombinedError(x, x_e, y, y_e):
    if x != 0:
        x_part = math.pow(x_e/x,2)
    else:
        x_part = 0
    if x_e == 0:
        return 0
    if y != 0:
        y_part = math.pow(y_e/y,2)
    else:
        y_part = 0
    return math.sqrt(x_part + y_part)

def bTagSelection(tree, bTag):
    passCut = 0        
    if bTag == 'True' and tree.CSVJ1 >= 0.68 and tree.CSVJ2 >= 0.24:
        passCut = 1
    if bTag == 'False':
        passCut = 1
    if bTag == 'Revert' and (tree.CSVJ1 < 0.68 and tree.CSVJ2 < 0.24):
        passCut = 1
    if bTag == 'Loose' and (tree.CSVJ1 >= 0.24 and tree.CSVJ2 >= 0.24):
        passCut = 1
    return passCut

def passCut(tree, bTag, region):
#     if tree.tauDecayMode1 != 10:
#         return 0
#         return 0
#     if tree.pt1.size() > 1:
#         return 0
    isoCut = 3
    iso_count = 3

    if region == 'LL':
        if  tree.iso1.at(0)>1.5  and tree.iso2.at(0)>1.5:
              iso_count = 2
        if  tree.iso1.at(0)>isoCut  and tree.iso2.at(0)<1.5:
              return 0
        if  tree.iso1.at(0)<1.5  and tree.iso2.at(0)>isoCut:
              return 0
    elif region == 'LT':
        if tree.iso1.at(0)>1.5  and tree.iso2.at(0)<1.5:
              iso_count = 2
        if tree.iso1.at(0)>isoCut  and tree.iso2.at(0)>isoCut:
            return 0
        if tree.iso1.at(0)<1.5  and tree.iso2.at(0)>isoCut:
            return 0
    elif region == 'TL':
        if tree.iso1.at(0)<1.5  and tree.iso2.at(0)>1.5:
              iso_count = 2
        if tree.iso1.at(0)>isoCut  and tree.iso2.at(0)>isoCut:
            return 0
        if tree.iso1.at(0)>isoCut  and tree.iso2.at(0)<1.5:
            return 0

    if bTagSelection(tree, bTag) and abs(tree.eta1.at(0))<2.1 and abs(tree.eta2.at(0))<2.1:
        sign_count = 0
        maxIso = 10
        if  tree.iso1.at(0) > maxIso  or tree.iso2.at(0) > maxIso:
            iso_count = 5
        elif tree.iso1.at(0)>isoCut and tree.iso2.at(0)>isoCut:
            iso_count = 1
        elif (tree.iso1.at(0)>isoCut and tree.iso2.at(0)<1.5) or (tree.iso2.at(0)>isoCut and tree.iso1.at(0)<1.5):
            iso_count = 1
            print iso_count<<1
        elif  tree.iso1.at(0)<1.5  and tree.iso2.at(0)<1.5:
            iso_count = 0
        if tree.charge1.at(0) -  tree.charge2.at(0) == 0:
            sign_count = 1

        return (iso_count<<1) + sign_count + 1
    else:
        return 0

def findBin(x, nBins, xMin, xMax):
    bin =  int(nBins*(x-xMin)/(xMax-xMin))
    if bin >= nBins:
        return nBins-1
    else:
        return bin

def findPtScale(pt1, pt2, direction, region):
    scaleDictUp = {'LL': 0.051, #0.352, #1.690, #0.051, #0.038, #  
                   'LT': 0.248, #0.221,
                   'TL': 0.229, #0.201
                  }  
    if direction == 'up':
        return scaleDictUp[region]

    scale1 = 1.0
    scale2 = 1.0
    ptRange = [70, 120]
    scaleDictLeft = {'LL': [1.0, 1.0, 1.0],#[1.06, 0.97, 0.97],#[1.08, 0.93, 0.93], 
                     'LT': [1.0, 1.0, 1.0],#[1.29, 0.92, 1.30], #[1.3, 1.04, 1.0],
                     'TL': [1.0, 1.0, 1.0],#[1.24, 0.63, 2.15],#[1.21, 0.78, 2.05]
                    }

    scale = scaleDictLeft[region]

    if pt1 < ptRange[0]:
        scale1 = scale[0]
    elif ptRange[0] < pt1 < ptRange[1]:
        scale1 = scale[1]
    elif ptRange[1] < pt1:
        scale1 = scale[2]
    if pt2 < ptRange[0]:
        scale2 = scale[0]
    elif ptRange[0] < pt2 < ptRange[1]:
        scale2 = scale[1]
    elif ptRange[1] < pt2:
        scale2 = scale[2]

    if region == 'LL':
        return scale1*scale2
    elif region == 'LT':
        return scale1
    elif region == 'TL':
        return scale2

def getAccuDist(hist, xMin, xMax, name):
    nBins = hist.GetNbinsX()
    total = hist.Integral()
    accuDist = r.TH1F(name, '', nBins, xMin, xMax)
    for i in range(nBins):
        accuDist.SetBinContent(i+1, hist.Integral(1, i+1)/total)
    return accuDist


def getHistos(varName, signalSelection, logY, sigBoost, nbins, useData, max, rangeMin, rangeMax, location, bTag, predict, predictPtBin, region):
    r.gStyle.SetOptStat(0)
    fileList = draw_cfg.MCFileList
    histList = []
    histList_4QCD = []
    QCDHistList = []
    QCDHistList_4KS = []
    QCDHistList_withScale = []
    varRange = [nbins, rangeMin, rangeMax]
    nBins = 10000
    Lumi = 19.0
    initNEventsList = []
    legendHistos = []
    var_background = []

    scaleMCPt = 1.0

    tmpFile = []
    tmpTree = []
    var_data_4KS = []
    var_data = []
    var_data_4QCD = []
    histList_4KS = []

    for i in range(5):
        var_data.append(r.TH1F('data_%i' %(i),"", varRange[0], varRange[1], varRange[2]))
        var_data_4KS.append(r.TH1F('data_4KS_%i' %(i),"", nBins, varRange[1], varRange[2]))
        if i < 5:
            var_data_4QCD.append(r.TH1F('data_4QCD_%i' %(i),"", varRange[0], varRange[1], varRange[2]))

    dataName = draw_cfg.dataFile
    fData = r.TFile(dataName)
    treeData = fData.Get('eventTree')
    print 'Adding events from: %s ...' %dataName
    for iEntry in range(treeData.GetEntries()):
        treeData.GetEntry(iEntry)
        select = passCut(treeData, bTag, region)
        if (select == 0) or (select == 1) or (select > 6):
            continue
        var_data[select-2].Fill(varsList.findVar(treeData, varName))
        var_data_4KS[select-2].Fill(varsList.findVar(treeData, varName))
        if select == 2:
            var_data_4QCD[0].Fill(varsList.findVar(treeData, varName), findPtScale(treeData.pt1.at(0),treeData.pt2.at(0), 'left', region))
        elif select == 3:
            var_data_4QCD[1].Fill(varsList.findVar(treeData, varName), findPtScale(treeData.pt1.at(0),treeData.pt2.at(0), 'up', region))
        elif select == 4:
            var_data_4QCD[2].Fill(varsList.findVar(treeData, varName), findPtScale(treeData.pt1.at(0),treeData.pt2.at(0), 'left', region))
            var_data_4QCD[3].Fill(varsList.findVar(treeData, varName), findPtScale(treeData.pt1.at(0),treeData.pt2.at(0), 'up', region))

    legendHistos.append([])
    for j in range(5):
        var_data[j].SetMarkerStyle(8)
        var_data[j].SetMarkerSize(0.9)
        legendHistos.append([])
        legendHistos[j+1].append((var_data[j], 'observed (%.0f)' %var_data[j].Integral()))

    for i in range(len(fileList)): 
        for j in range(6):
            histList_4KS.append(r.TH1F('%s_%i_KS' %(fileList[i][0],j),fileList[i][0], nBins, varRange[1], varRange[2]))
            histList.append(r.TH1F('%s_%i' %(fileList[i][0],j),fileList[i][0], varRange[0], varRange[1], varRange[2]))
            histList_4QCD.append(r.TH1F('%s_%i_2' %(fileList[i][0],j),fileList[i][0], varRange[0], varRange[1], varRange[2]))
        print 'Adding events from: %s ...' %(fileList[i][1])
        tmpFile.append(r.TFile(fileList[i][1]))
        tmpTree.append(tmpFile[i].Get('eventTree'))
        for iEntry in range(tmpTree[i].GetEntries()):
            tmpTree[i].GetEntry(iEntry)
            select = passCut(tmpTree[i], bTag, region)
            if (not select) or (select > 6):
                continue
            histList[6*i+select-1].Fill(varsList.findVar(tmpTree[i], varName)*scaleMCPt, tmpTree[i].triggerEff)
            histList_4KS[6*i+select-1].Fill(varsList.findVar(tmpTree[i], varName)*scaleMCPt, tmpTree[i].triggerEff)
            if select == 2:
                histList_4QCD[6*i].Fill(varsList.findVar(tmpTree[i], varName)*scaleMCPt, tmpTree[i].triggerEff*findPtScale(tmpTree[i].pt1.at(0), tmpTree[i].pt2.at(0), 'left', region))
            elif select == 3:
                histList_4QCD[6*i+1].Fill(varsList.findVar(tmpTree[i], varName)*scaleMCPt, tmpTree[i].triggerEff*findPtScale(tmpTree[i].pt1.at(0), tmpTree[i].pt2.at(0), 'up', region))
            elif select == 4:             
                histList_4QCD[6*i+2].Fill(varsList.findVar(tmpTree[i], varName)*scaleMCPt, tmpTree[i].triggerEff*findPtScale(tmpTree[i].pt1.at(0), tmpTree[i].pt2.at(0), 'left', region))
                histList_4QCD[6*i+3].Fill(varsList.findVar(tmpTree[i], varName)*scaleMCPt, tmpTree[i].triggerEff*findPtScale(tmpTree[i].pt1.at(0), tmpTree[i].pt2.at(0), 'up', region))

        initNEventsList.append(tmpFile[i].Get('preselection'))
        for j in range(6):
            var_background.append(r.THStack())
            histList[6*i+j].SetFillColor(fileList[i][3])
            histList[6*i+j].Scale(fileList[i][2]*Lumi/initNEventsList[i].GetBinContent(1))
            histList_4QCD[6*i+j].Scale(fileList[i][2]*Lumi/initNEventsList[i].GetBinContent(1))
            histList_4KS[6*i+j].Scale(fileList[i][2]*Lumi/initNEventsList[i].GetBinContent(1))   

            var_background[j].Add(histList[6*i+j])
            legendHistos[j].append((histList[6*i+j], '%s (%.2f)' %(fileList[i][0], histList[6*i+j].Integral())))

    data_i = []
    MC_i = []
    data_r = []
    MC_r = []
    e = []
    MC_List = []
    for i in range(3):
        QCDHistList.append(r.TH1F('QCD_%i' %(i),"", varRange[0], varRange[1], varRange[2]))
        QCDHistList_4KS.append(r.TH1F('QCD_%i_KS' %(i),"", nBins, varRange[1], varRange[2]))
        MC_List.append(r.TH1F('MC_total_%i' %(i),"", varRange[0], varRange[1], varRange[2]))

        for j in range(varRange[0]):
            dataValue = var_data[i].GetBinContent(j+1)
            dataError = var_data[i].GetBinError(j+1)
            MCValue = 0
            for k in range(len(fileList)):
                MCValue +=  histList[6*k+1+i].GetBinContent(j+1)
            if i == 0:
                data_i.append(dataValue)
                e.append(dataError)
                MC_i.append(MCValue)
            if i == 2:
                data_r.append(dataValue)
                MC_r.append(MCValue)
            MC_List[i].SetBinContent(j+1, MCValue)
            if dataValue - MCValue > 0:
                QCDHistList[i].SetBinContent(j+1, dataValue - MCValue)
                QCDHistList[i].SetBinError(j+1, dataError)
        MC_List[i].Sumw2()
        for j in range(nBins):
            dataValue4KS = var_data_4KS[i].GetBinContent(j+1)
            MCValue4KS = 0
            for k in range(len(fileList)):
                MCValue4KS += histList_4KS[6*k+1+i].GetBinContent(j+1)
            if dataValue4KS - MCValue4KS > 0:
                QCDHistList_4KS[i].SetBinContent(j+1, dataValue4KS - MCValue4KS)

    for i in range(4):
        QCDHistList_withScale.append(r.TH1F('QCD_withScale_%i' %(i),"", varRange[0], varRange[1], varRange[2]))
        for j in range(varRange[0]):
            dataValue = var_data_4QCD[i].GetBinContent(j+1)
            dataError = var_data_4QCD[i].GetBinError(j+1)
            MCValue = 0
            for k in range(len(fileList)):
                MCValue +=  histList_4QCD[6*k+i].GetBinContent(j+1)
            if dataValue - MCValue > 0:
                QCDHistList_withScale[i].SetBinContent(j+1, dataValue - MCValue)

    QCDDiff = r.TH1F('QCD_diff',"", varRange[0], varRange[1], varRange[2])
    QCDDiff2 = r.TH1F('QCD_diff2',"", varRange[0], varRange[1], varRange[2])
    QCDDiff_R2T = r.TH1F('QCDDiff_R2T',"", varRange[0], varRange[1], varRange[2])

#     QCDDiff2.Sumw2()

    fit1 = r.TF1("fit1","[0]", varRange[1],varRange[2])
    fit1.SetParName(0,'scale')
    fit1.FixParameter(0,1.0)

    QCDDiff.Fit('fit1', '0EM')
    fit1.SetLineStyle(2)
    fit1.SetLineColor(r.kRed)
    fit2 = r.TF1("fit2","[0]", varRange[1],varRange[2])
    fit2.SetParName(0,'scale')
    fit2.FixParameter(0,1.0)
    QCDDiff2.Fit('fit2', '0EM')
    fit2.SetLineStyle(2)
    fit2.SetLineColor(r.kRed)


    DrawSignal = False
    if signalSelection != '':
        var_signal = []
        var_signal_4KS = []
        for i in range(6):
            var_signal.append(r.TH1F('%s_%i' %(signalSelection,i),"", varRange[0], varRange[1], varRange[2]))
            var_signal_4KS.append(r.TH1F('%s_%i_4KS' %(signalSelection,i),"", nBins, varRange[1], varRange[2]))
        signalDict = draw_cfg.signalDict
        if signalSelection in signalDict:
            fSignal = r.TFile(signalDict[signalSelection][0])
            treeSignal = fSignal.Get('eventTree')
            print 'Adding events from: %s ...' %(signalDict[signalSelection][0])
            for iEntry in range(treeSignal.GetEntries()):
                treeSignal.GetEntry(iEntry)
                select = passCut(treeSignal, bTag, region)
                if (not select) or (select > 6):
                    continue
                var_signal[select-1].Fill(varsList.findVar(treeSignal, varName), treeSignal.triggerEff)
                var_signal_4KS[select-1].Fill(varsList.findVar(treeSignal, varName), treeSignal.triggerEff)
            initNEventsSignal = fSignal.Get('preselection')
            for i in range(6):
                var_signal[i].SetLineStyle(7)
                var_signal[i].SetLineWidth(4)
                var_signal[i].Scale(signalDict[signalSelection][1]*sigBoost*Lumi/initNEventsSignal.GetBinContent(1))
                if sigBoost != 1:
                    sum = var_signal[i].Integral(0, var_signal[i].GetNbinsX()+1)
                    legendHistos[i].append((var_signal[i], '%sx%0.f (%.2f)' %(signalSelection, sigBoost, var_signal[i].Integral())))
                else:
                    legendHistos[i].append((var_signal[i], '%s (%.2f)' %(signalSelection, var_signal[i].Integral())))
            DrawSignal = True
        else:
            print '%s not supported, please use H260, H300 or H350' %signalSelection

    if predict == 'True':

        scale_SS2OS = fit1.GetParameter(0)
        scale_er_SS2OS = fit1.GetParError(0)
        scale_relaxed2Tight = fit2.GetParameter(0)
        scale_er_relaxed2Tight = fit2.GetParError(0)

        QCDHistList_withScale[0].Scale(scale_SS2OS)
        QCDHistList_withScale[1].Scale(scale_relaxed2Tight)
        QCDHistList_withScale[2].Scale(scale_SS2OS)
        QCDHistList_withScale[3].Scale(scale_relaxed2Tight)

        QCDHistList_withScale[3].SetFillColor(r.kSpring+1)
        QCDHistList_withScale[2].SetFillColor(r.kOrange-4)
        QCDHistList_withScale[0].SetLineColor(r.kSpring+1)
        QCDHistList_withScale[0].SetLineWidth(2)
        QCDHistList_withScale[1].SetLineStyle(2)
        QCDHistList_withScale[1].SetLineColor(r.kOrange-4)
        QCDHistList_withScale[1].SetLineWidth(2)

        legendHistos[0].append((QCDHistList_withScale[0], 'From SS/Tight (%.0f)' %QCDHistList_withScale[0].Integral()))
        legendHistos[0].append((QCDHistList_withScale[1], 'From OS/Relax (%.0f)' %QCDHistList_withScale[1].Integral()))

        var_background[1].Add(QCDHistList_withScale[3])
        var_background[2].Add(QCDHistList_withScale[2])
        legendHistos[1].append((QCDHistList_withScale[3], 'From SS/Relax (%.0f)' %QCDHistList_withScale[3].Integral()))
        legendHistos[2].append((QCDHistList_withScale[2], 'From SS/Relax (%.0f)' %QCDHistList_withScale[2].Integral()))
        QCDHistList_withScale[1] = tool.addFakeTHStack(QCDHistList_withScale[1],var_background[0])
        QCDHistList_withScale[0] = tool.addFakeTHStack(QCDHistList_withScale[0],var_background[0])

#     var_data[1].Sumw2()
#     MC_List[1].Sumw2()
    for i in range(varRange[0]):
        oldValue = var_data[1].GetBinContent(i+1)
        mcValue = MC_List[1].GetBinContent(i+1)
        if oldValue - mcValue > 0:
            QCDDiff2.SetBinContent(i+1, (oldValue - mcValue)/oldValue)
            QCDDiff2.SetBinError(i+1, MC_List[1].GetBinError(i+1)/oldValue)
    print QCDDiff2.Integral()


    QCDDiff = var_data[1].Clone()
    QCDDiff_sub = QCDHistList_withScale[2].Clone() + MC_List[1].Clone()
    QCDDiff.Divide(QCDDiff_sub)

    QCDDiff_R2T = var_data[0].Clone()
    QCDDiff_R2T_sub = QCDHistList_withScale[3].Clone() + MC_List[0].Clone()
    QCDDiff_R2T.Divide(QCDDiff_R2T_sub)



    legendPosition = (0.6, 0.7, 0.90, 0.88)
    l = []
    r.gROOT.SetBatch(True)  # to suppress canvas pop-outs
    if bTag == 'True':
        titleName = '1 Medium 1 Loose b-tag'
        fileName = 'bTag'
    elif bTag == 'False':
        titleName = ''
        fileName = 'all'
    elif bTag == 'Revert':
        titleName = 'Revert b-tag'
        fileName = 'revert_bTag'
    elif bTag == 'Loose':
        titleName = 'Loose b-tag'
        fileName = 'loose_bTag'

    KS1 = QCDHistList_4KS[0].KolmogorovTest(QCDHistList_4KS[2])
    KS2 = QCDHistList_4KS[1].KolmogorovTest(QCDHistList_4KS[2])

    ks_values = []
    tmpHists = []
    ks_values2 = []
    tmpHists2 = []
    nTimes = 10000
#     for i in range(nTimes):
#         tool.printProcessStatus(i, nTimes, processName = 'Making Sample Histograms')
#         tmpHists.append(r.TH1F('tmpHist_%i' %(i),"", nBins, varRange[1], varRange[2]))
#         tmpHists[i].FillRandom(QCDHistList_4KS[2], 100)
#         ks_values.append(QCDHistList_4KS[0].KolmogorovTest(tmpHists[i]))
#         tmpHists2.append(r.TH1F('tmpHist2_%i' %(i),"", nBins, varRange[1], varRange[2]))
#         tmpHists2[i].FillRandom(QCDHistList_4KS[2], 100)
#         ks_values2.append(QCDHistList_4KS[2].KolmogorovTest(tmpHists[i]))
    print ''
    print 'KS Test 1: %.3f' %KS1
    print 'KS Test 2: %.3f' %KS2

    psfile = '%s_%s_all.pdf' %(varName, fileName)
    c = r.TCanvas("c","Test", 800, 900)
    #ps = r.TPDF(psfile,112)
    c.Divide(2,3)
    drawOpt = ''
    QCDDiff.SetTitle('Data/Background OS Relaxed Events %s (%.1f fb^{-1}); %s; Data/Background' %(titleName, Lumi,varName))
    QCDDiff.SetMarkerStyle(8)
    QCDDiff.SetMarkerSize(0.9)
    QCDDiff.SetMaximum(4)
    QCDDiff.SetMinimum(0)
    QCDDiff_R2T.SetTitle('Data/Background OS Relaxed Events %s (%.1f fb^{-1}); %s; Data/Background' %(titleName, Lumi,varName))
    QCDDiff_R2T.SetMarkerStyle(8)
    QCDDiff_R2T.SetMarkerSize(0.9)
    QCDDiff_R2T.SetMaximum(4)
    QCDDiff_R2T.SetMinimum(0)

    for k in range(6):
        c.cd(k+1)
        r.gPad.SetTicky()
        if logY == 'True':
            r.gPad.SetLogy()
        signSelection, iso = conditions(k+1)
        var_background[k].SetTitle('%s %s Events %s (%.1f fb^{-1}); %s; events / bin' %(signSelection, iso, titleName, Lumi,varName))
        var_background[k].SetMaximum(max)
        var_background[k].SetMinimum(0.01)
        var_background[k].Draw()
        if predict == 'True' and k == 0:
            QCDHistList_withScale[0].Draw('same')
            QCDHistList_withScale[1].Draw('same')
        if k != 0 and useData == 'True':
            var_data[k-1].Draw('PE same')
        legendPosition = (0.63, 0.93 - 0.03*len(legendHistos[k]), 0.93, 0.9)
        l.append(tool.setMyLegend(lPosition=legendPosition, lHistList=legendHistos[k]))
        if k == 1:
            ksLegend1 = tool.setMyLegend((0.3, 0.8, 0.6, 0.9), [(QCDHistList_withScale[3], 'KS Test: %.3f' %KS1)])
            ksLegend1.Draw('same')
        if k == 2:
            ksLegend2 = tool.setMyLegend((0.3, 0.8, 0.6, 0.9), [(QCDHistList_withScale[2], 'KS Test: %.3f' %KS2)])
            ksLegend2.Draw('same')
        l[k].Draw('same')
        var_signal[k].Draw('same')

    c.Update()
    c.cd(5)
    r.gPad.SetLogy(0)
    QCDDiff.Draw('PE')
    fit1.Draw('same')
    c.cd(6)
    r.gPad.SetLogy(0)
    QCDDiff_R2T.Draw('PE')
    fit2.Draw('same')
    c.Update()
    c.Print('%s(' %psfile)
    c.cd(1)
    r.gPad.SetLogy(0)
    QCDDiff.Draw('PE')

    fit1.Draw('same')
    lFit1 = tool.setMyLegend((0.15, 0.7, 0.9, 0.85),[(fit1,'Scale between OS/SS in relaxed region: %.2f \pm %.2f' %(fit1.GetParameter(0), fit1.GetParError(0)))])
    lFit1.Draw('same')
    for k in range(3):
        c.cd(k+2)
        if logY == 'True':
            r.gPad.SetLogy()
        signSelection, iso = conditions(k+2)
        QCDHistList_withScale[k+1].SetTitle('%s %s Data - MC Events %s (%.1f fb^{-1}); %s; events / bin' %(signSelection, iso, titleName, Lumi,varName))
        QCDHistList_withScale[k+1].SetMarkerStyle(8)
        QCDHistList_withScale[k+1].SetMarkerSize(0.9)
        QCDHistList_withScale[k+1].SetMaximum(max)
        QCDHistList_withScale[k+1].SetMinimum(1)
        QCDHistList_withScale[k+1].Draw('PE')
    c.Update()
    c.Print('%s' %psfile)
    c.cd(1)
    r.gPad.SetLogy(0)
    QCDDiff2.SetTitle('QCD/Data OS Relaxed Events %s (%.1f fb^{-1}); %s; QCD/Data' %(titleName, Lumi,varName))
    QCDDiff2.SetMarkerStyle(8)
    QCDDiff2.SetMarkerSize(0.9)
    QCDDiff2.SetMinimum(0.0)
    QCDDiff2.SetMaximum(1.0)
    QCDDiff2.Draw('PE')
    fit2.Draw('same')
    lFit2 = tool.setMyLegend((0.15, 0.7, 0.9, 0.85),[(fit2,'Scale between relaxed/tight in SS region: %.3f \pm %.3f' %(fit2.GetParameter(0), fit2.GetParError(0)))])
    lFit2.Draw('same')
    c.Update()
    c.Print('%s' %psfile)
#     c.Clear()
#     c.Divide(1,2)
#     c.cd(1)
#     graph = r.TH1F('graph', '', 20, 0, 1.0)
#     graph2 = r.TH1F('graph2', '', 20, 0, 1.0)

#     for i in range(nTimes):
#         tool.printProcessStatus(i, nTimes, processName = 'Plotting Sample Histograms')
#         graph.Fill(ks_values[i])
#         graph2.Fill(ks_values2[i])
#     print ''
#     graph.SetTitle('KS Tests Between SS Tight and Relaxed; KS; ')
#     graph.SetMarkerStyle(8)
#     graph.Draw('PE')
#     c.cd(2)
#     graph2.SetTitle('KS Self-test in SS Relaxed; KS; ')
#     graph2.SetMarkerStyle(8)
#     graph2.Draw('PE')
#     c.Update()
#     c.Print('%s' %psfile)
#     c.Clear()
# 
#     a1 = getAccuDist(QCDHistList_4KS[0], varRange[1], varRange[2], 'SS Tight')
#     a2 = getAccuDist(QCDHistList_4KS[2], varRange[1], varRange[2], 'SS Relax')
#     a1.SetLineColor(r.kRed)
#     l3 = tool.setMyLegend((0.15, 0.75, 0.3, 0.85),[(a1,'SS Tight'),
#                                                   (a2,'SS Relax')])
# 
#     a1.SetTitle('Cumulative Distribution; %s;' %varName)
#     a1.Draw()
#     a2.Draw('same')
#     l3.Draw('same')
    c.Print('%s)' %psfile)
    #ps.Close()
    print "Plot saved at %s" %(psfile)
    c.Close()

op = opts()
if op.varName != 'test':
    getHistos(op.varName, op.signal, op.logy, float(op.sigBoost), int(op.nbins),
           op.useData, float(op.max), float(op.rangeMin), float(op.rangeMax), op.location, op.bTag, op.predict, 'False', op.region)

