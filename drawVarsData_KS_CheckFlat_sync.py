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
from cfg import draw_sync as draw_cfg

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
    parser.add_option("--thirdLeptonVeto", dest="thirdLeptonVeto", default = 'False', help="")
    parser.add_option("--weight", dest="weight", default = "0.05", help="")
    parser.add_option("--yMax", dest="yMax", default = 300, help="")



    options, args = parser.parse_args()
    return options

def conditions(selection, region):
    if selection == 1:
        return 'OS', region
    elif selection == 2:
        return 'SS', region
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
    if bTag == 'True' and tree.CSVJ1 >= 0.679 and tree.CSVJ2 >= 0.244:
        passCut = 1
    if bTag == 'False':
        passCut = 1
    if bTag == 'None' and (tree.CSVJ1 < 0.679 and tree.CSVJ2 < 0.679):
        passCut = 1
    if bTag == '2M' and (tree.CSVJ1 >= 0.679 and tree.CSVJ2 >= 0.679):
        passCut = 1
    if bTag == '1M1NonM' and (tree.CSVJ1 >= 0.679 and tree.CSVJ2 < 0.679):
        passCut = 1
    if bTag == '1M' and (tree.CSVJ1 > 0.679):
        passCut = 1
    return passCut

def getIntegralFromString(info):
    integral = info[info.find('(')+1:info.find(')')]
    return float(integral)

def passCut(tree, bTag, region, thirdLeptonVeto):
    isoCut = 3
    iso_count = 3
    if thirdLeptonVeto == 'True':
        if tree.nElectrons > 0 or tree.nMuons>0:
            return 0
    if bTagSelection(tree, bTag) and abs(tree.eta1.at(0))<2.1 and abs(tree.eta2.at(0))<2.1:
        sign_count = 0
        maxIso = 10
        if  tree.iso1.at(0) > maxIso  or tree.iso2.at(0) > maxIso:
            return 0
        elif tree.iso1.at(0)>isoCut and tree.iso2.at(0)>isoCut:
            iso_count = 1

        elif  tree.iso1.at(0)<1.5:
            if 'tight' in region and tree.iso2.at(0)<1.5:
                iso_count = 0
            if 'semiTight' in region and tree.iso2.at(0)>3:
                iso_count = 0
        elif tree.iso2.at(0)<1.5:
            if 'semiTight' in region and tree.iso1.at(0)>3:
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

def dontUnblind(tree):
#     if 90 < tree.svMass.at(0) < 150:
#         return True
#     if 70 < tree.mJJ < 150:
#         return True
#     if tree.BDT > 0:
#         return True
    return False
    

def getAccuDist(hist, xMin, xMax, name):
    nBins = hist.GetNbinsX()
    total = hist.Integral()
    accuDist = r.TH1F(name, '', nBins, xMin, xMax)
    for i in range(nBins):
        accuDist.SetBinContent(i+1, hist.Integral(1, i+1)/total)
    return accuDist


def getHistos(varName, signalSelection, logY, sigBoost, nbins, useData, max, rangeMin, rangeMax, location, bTag, predict, predictPtBin, region, thirdLeptonVeto, SF, yMax):
    r.gStyle.SetOptStat(0)
    SF = float(SF)
    fileList = draw_cfg.MCFileList
    histList = []
    histList_4QCD = []
    QCDHistList = []
    QCDHistList_4KS = []
    QCDHistList_withScale = []
    varRange = [nbins, rangeMin, rangeMax]
    nBins = 10000
    Lumi = 19.7
    legendHistos = []
    var_background = []

    scaleMCPt = 1.0

    tmpFile = []
    tmpTree = []
    var_data_4KS = []
    var_data = []
    var_data_4QCD = []
    histList_4KS = []

    for i in range(6):
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
        select = passCut(treeData, bTag, region, thirdLeptonVeto)
        if (select == 0) or (select > 6):
            continue
        if (select == 1) and dontUnblind(treeData):
            continue
        var_data[select-1].Fill(varsList.findVar(treeData, varName))
        if (select != 1):
            var_data_4KS[select-2].Fill(varsList.findVar(treeData, varName))
        if select == 2:
            var_data_4QCD[0].Fill(varsList.findVar(treeData, varName), 1.0)
        elif select == 3:
            var_data_4QCD[1].Fill(varsList.findVar(treeData, varName), SF)
        elif select == 4:
            var_data_4QCD[2].Fill(varsList.findVar(treeData, varName), 1.0)
            var_data_4QCD[3].Fill(varsList.findVar(treeData, varName), SF)

    legendHistos.append([])
    for j in range(6):
        var_data[j].SetMarkerStyle(8)
        var_data[j].SetMarkerSize(0.9)
        legendHistos.append([])
        integral = 'observed'
        if j != 0 or ((region != 'tight') and (bTag != 'None')):
            integral = 'observed (%.0f)' %var_data[j].Integral()
        legendHistos[j].append((var_data[j], integral))

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
            select = passCut(tmpTree[i], bTag, region, thirdLeptonVeto)
            if (not select) or (select > 6):
                continue
            histList[6*i+select-1].Fill(varsList.findVar(tmpTree[i], varName), tmpTree[i].triggerEff*tmpTree[i].xs/(tmpTree[i].initEvents))
            histList_4KS[6*i+select-1].Fill(varsList.findVar(tmpTree[i], varName), tmpTree[i].triggerEff*tmpTree[i].xs/(tmpTree[i].initEvents))
            if select == 2:
                histList_4QCD[6*i].Fill(varsList.findVar(tmpTree[i], varName), tmpTree[i].triggerEff*1.0*tmpTree[i].xs/(tmpTree[i].initEvents))
            elif select == 3:
                histList_4QCD[6*i+1].Fill(varsList.findVar(tmpTree[i], varName), tmpTree[i].triggerEff*SF*tmpTree[i].xs/(tmpTree[i].initEvents))
            elif select == 4:             
                histList_4QCD[6*i+2].Fill(varsList.findVar(tmpTree[i], varName), tmpTree[i].triggerEff*1.0*tmpTree[i].xs/(tmpTree[i].initEvents))
                histList_4QCD[6*i+3].Fill(varsList.findVar(tmpTree[i], varName), tmpTree[i].triggerEff*SF*tmpTree[i].xs/(tmpTree[i].initEvents))

        for j in range(6):
            var_background.append(r.THStack())
            histList[6*i+j].SetFillColor(fileList[i][2])
            histList[6*i+j].Scale(Lumi)
            histList_4QCD[6*i+j].Scale(Lumi)
            histList_4KS[6*i+j].Scale(Lumi)   

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
            dataValue = var_data[i+1].GetBinContent(j+1)
            dataError = var_data[i+1].GetBinError(j+1)
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
    ss_t = QCDHistList[0].Integral()
    ss_l = QCDHistList[2].Integral()

    os_l = QCDHistList[1].Integral()
    os_l_data = var_data[2].Integral()
    print "QCD in SS_T: %.4f" %ss_t
    print "QCD in SS_L: %.4f" %ss_l

    print "QCD in OS_L: %.4f" %os_l
    print "Data in OS_L:%.4f" %os_l_data

    print "SF: %.4f" %(ss_t/ss_l)
    print "SF qcd/data: %.4f" %(os_l/os_l_data)


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
            fSignal = r.TFile(signalDict[signalSelection])
            treeSignal = fSignal.Get('eventTree')
            print 'Adding events from: %s ...' %(signalDict[signalSelection])
            for iEntry in range(treeSignal.GetEntries()):
                treeSignal.GetEntry(iEntry)
                select = passCut(treeSignal, bTag, region, thirdLeptonVeto)
                if (not select) or (select > 6):
                    continue
                var_signal[select-1].Fill(varsList.findVar(treeSignal, varName), treeSignal.triggerEff*treeSignal.xs/(treeSignal.initEvents))
                var_signal_4KS[select-1].Fill(varsList.findVar(treeSignal, varName), treeSignal.triggerEff*treeSignal.xs/(treeSignal.initEvents))
            initNEventsSignal = fSignal.Get('preselection')
            for i in range(6):
                var_signal[i].SetLineStyle(7)
                var_signal[i].SetLineWidth(4)
                var_signal[i].Scale(sigBoost*Lumi)
                if sigBoost != 1:
                    sum = var_signal[i].Integral(0, var_signal[i].GetNbinsX()+1)
                    legendHistos[i].append((var_signal[i], '%sx%0.f (%.2f)' %(signalSelection, sigBoost, var_signal[i].Integral())))
                else:
                    legendHistos[i].append((var_signal[i], '%s (%.2f)' %(signalSelection, var_signal[i].Integral())))
            DrawSignal = True
        else:
            print '%s not supported, please use H260, H300 or H350' %signalSelection

    scale_SS2OS = fit1.GetParameter(0)
    scale_er_SS2OS = fit1.GetParError(0)
    scale_relaxed2Tight = fit2.GetParameter(0)
    scale_er_relaxed2Tight = fit2.GetParError(0)

    QCDHistList_withScale[0].Scale(scale_SS2OS)
    QCDHistList_withScale[1].Scale(scale_relaxed2Tight)
    QCDHistList_withScale[2].Scale(scale_SS2OS)
    QCDHistList_withScale[3].Scale(scale_relaxed2Tight)

    QCDHistList_withScale[3].SetFillColor(r.kRed-10)
    QCDHistList_withScale[2].SetFillColor(r.kRed-10)
    QCDHistList_withScale[0].SetLineColor(r.kRed-10)
    QCDHistList_withScale[0].SetLineWidth(2)
    QCDHistList_withScale[1].SetLineStyle(2)
    QCDHistList_withScale[1].SetLineColor(r.kRed-10)
    QCDHistList_withScale[1].SetLineWidth(2)

#     legendHistos[0].append((QCDHistList_withScale[0], 'From SS/Tight (%.0f)' %QCDHistList_withScale[0].Integral()))

    var_background[1].Add(QCDHistList_withScale[3])
    var_background[2].Add(QCDHistList_withScale[2])
    legendHistos[1].append((QCDHistList_withScale[3], 'QCD (%.0f)' %QCDHistList_withScale[3].Integral()))
    legendHistos[2].append((QCDHistList_withScale[2], 'QCD (%.0f)' %QCDHistList_withScale[2].Integral()))
    allStacked = var_background[0].Clone()
    QCDPredict = QCDHistList_withScale[1].Clone()
    QCDPredict.SetLineStyle(1)
    QCDPredict.SetLineWidth(1)

    QCDPredict.SetLineColor(r.kBlack)
    legendHistos[0].append((QCDPredict, 'QCD (%.0f, SF = %.3f)' %(QCDPredict.Integral(), SF)))

    QCDPredict.SetFillColor(r.kRed-10)
    allStacked.Add(QCDPredict)

    QCDHistList_withScale[1] = tool.addFakeTHStack(QCDHistList_withScale[1],var_background[0])
    QCDHistList_withScale[0] = tool.addFakeTHStack(QCDHistList_withScale[0],var_background[0])
#     var_data[1].Sumw2()
#     MC_List[1].Sumw2()
    for i in range(varRange[0]):
        oldValue = var_data[2].GetBinContent(i+1)
        mcValue = MC_List[1].GetBinContent(i+1)
        if oldValue - mcValue > 0:
            QCDDiff2.SetBinContent(i+1, (oldValue - mcValue)/oldValue)
            QCDDiff2.SetBinError(i+1, MC_List[1].GetBinError(i+1)/oldValue)
    print QCDDiff2.Integral()


    QCDDiff = var_data[2].Clone()
    QCDDiff_sub = QCDHistList_withScale[2].Clone() + MC_List[1].Clone()
    QCDDiff.Divide(QCDDiff_sub)

    QCDDiff_R2T = var_data[1].Clone()
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
    elif bTag == '2M':
        titleName = '2 Medium b-tags'
        fileName = '2MbTag'
    elif bTag == '1M':
        titleName = '1 Medium b-tag'
        fileName = '1MbTag'
    elif bTag == '1M1NonM':
        titleName = '1 Medium 1 Anti-Medium b-tag'
        fileName = '1M1NonMbTag'
    elif bTag == 'None':
        titleName = '0 b-tag'
        fileName = '0bTag'

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

    psfile = '%s_%s_%s.pdf' %(varName, fileName, signalSelection)
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

    pl_1 = r.TPad("pl_1","pl_1",0.,1,0.5,0.65)
    pl_1_delta = r.TPad("pl_1_delta","pl_1_delta",0.,0.65,0.5,0.45)
    pl_2 = r.TPad("pl_2","pl_2",0.,0.45,0.5,0.0)
    pl_1.SetMargin(1, 1, 0, 1)
    pl_1_delta.SetMargin(1, 1, 0.2, 0.05)

    pr_1 = r.TPad("pr_1","pr_1",0.5,1,1.,0.65)
    pr_1_delta = r.TPad("pr_1_delta","pr_1_delta",0.5,0.65,1.0,0.45)
    pr_2 = r.TPad("pr_2","pr_2",0.5,0.45,1.0,0.0)
    pr_1.SetMargin(1, 1, 0, 1)
    pr_1_delta.SetMargin(1, 1, 0.2, 0.05)

    pl_1.Draw()
    pl_1_delta.Draw()
    pl_2.Draw()
    pr_1.Draw()
    pr_1_delta.Draw()
    pr_2.Draw()

    pl_1.cd()
    r.gPad.SetTicky()
    signSelection, iso = conditions(1, region)
    allStacked.SetMaximum(int(yMax))
    allStacked.SetTitle('CMS Preliminary %.1f fb^{-1} at 8 TeV; %s; events / bin' %(Lumi,varName))
    allStacked.Draw()
    var_data[0].Draw('PE same')
    legendPosition = (0.47, 0.9 - 0.06*len(legendHistos[0]), 0.87, 0.9)
    l.append(tool.setMyLegend(lPosition=legendPosition, lHistList=legendHistos[0]))
    l[0].Draw('same')
    var_signal[0].Draw('same')

    pl_1_delta.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    pl_1_delta.SetGridy(1)
    bkgEst = QCDHistList_withScale[1].Clone()
    delta = var_data[0].Clone()
    delta.Sumw2()
    bkgEst.Sumw2()
    delta.Divide(bkgEst)
    delta.SetMinimum(0.5)
    delta.SetMaximum(1.5)
    delta.GetXaxis().SetTitle(varName)
    delta.GetXaxis().SetLabelSize(0.07)
    delta.GetXaxis().SetTitleSize(0.07)
    delta.GetYaxis().SetLabelSize(0.07)
    delta.GetYaxis().SetNdivisions(5,5,0)
    delta.Draw()

    pList = [pr_1, pl_2, pr_2]

    for k in range(1, len(pList)+1):
        pList[k-1].cd()
        r.gPad.SetTicky()
        if k > 1 and logY == 'True':
            r.gPad.SetLogy()
        signSelection, iso = conditions(k+1, region)
        var_background[k].SetTitle('%s %s Events %s (%.1f fb^{-1}); %s; events / bin' %(signSelection, iso, titleName, Lumi,varName))
        if k < 2:
            var_background[k].SetMaximum(int(yMax))
        else:
            var_background[k].SetMaximum(max)
        var_background[k].SetMinimum(0.01)
        var_background[k].Draw()
        if useData == 'True':
            var_data[k].Draw('PE same')
        legendPosition = (0.47, 0.9 - 0.06*len(legendHistos[k]), 0.87, 0.9)
        l.append(tool.setMyLegend(lPosition=legendPosition, lHistList=legendHistos[k]))
        if k == 1:
            ksLegend1 = tool.setMyLegend((0.2, 0.8, 0.5, 0.9), [(QCDHistList_withScale[3], 'KS Test: %.3f' %KS1)])
            ksLegend1.Draw('same')
        if k == 2:
            ksLegend2 = tool.setMyLegend((0.2, 0.8, 0.5, 0.9), [(QCDHistList_withScale[2], 'KS Test: %.3f' %KS2)])
            ksLegend2.Draw('same')
        l[k].Draw('same')
        var_signal[k].Draw('same')

    pr_1_delta.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    pr_1_delta.SetGridy(1)
    bkgEst2 = QCDHistList_withScale[3].Clone()
    delta2 = var_data[1].Clone()
    delta2.Sumw2()
    bkgEst2.Sumw2()
    delta2.Divide(bkgEst2)
    delta2.SetMinimum(0.5)
    delta2.SetMaximum(1.5)
    delta2.GetXaxis().SetTitle(varName)
    delta2.GetXaxis().SetLabelSize(0.07)
    delta2.GetXaxis().SetTitleSize(0.07)
    delta2.GetYaxis().SetLabelSize(0.07)
    delta2.GetYaxis().SetNdivisions(5,5,0)
    delta2.Draw()

    c.Update()
    c.Print('%s(' %psfile)

    c.Clear()

    p1 = r.TPad("p1","p1",0.,1,1.,0.4)
    p1_r = r.TPad("p1_r","p1_r",0.,0.39,1.,0.06)
    p1.SetMargin(1, 1, 0, 1)
    p1_r.SetMargin(1, 1, 0.2, 1)

    p1.Draw()
    p1_r.Draw()
    p1.cd()
    r.gPad.SetTicky()
    allStacked.Draw()

    var_data[0].Draw('PE same')
    l[0].Draw('same')
    var_signal[0].Draw('same')

    p1_r.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    p1_r.SetGridy(1)

    delta.Draw()
    c.Print('%s)' %psfile)

    print "Plot saved at %s" %(psfile)
    c.Close()

op = opts()
if op.varName != 'test':
    getHistos(op.varName, op.signal, op.logy, float(op.sigBoost), int(op.nbins),
           op.useData, float(op.max), float(op.rangeMin), float(op.rangeMax), op.location, op.bTag, op.predict, 'False', op.region, op.thirdLeptonVeto, op.weight, op.yMax)

