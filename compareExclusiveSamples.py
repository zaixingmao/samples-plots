#!/usr/bin/env python                                                                                                                                                                                                                                                     
import ROOT as r
import tool
import array
import cutSampleTools
import math

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
met = lvClass()
Lumi = 12891.5

def buildUncBand(varBins, listOfHist):
    uncBand = r.TH1F("uncBand", "", len(varBins)-1, varBins)
    for i in range(1, len(varBins)):
        binContent = 0
        binError = 0
        for iHist in listOfHist:
            binContent += iHist.GetBinContent(i)
            binError = math.sqrt(binError**2 + (iHist.GetBinError(i))**2)
        uncBand.SetBinContent(i, binContent)
        uncBand.SetBinError(i, binError)

    uncBand.SetFillColor(r.kGray+2)
    uncBand.SetLineColor(r.kGray+2)
    uncBand.SetFillStyle(3344)
    return uncBand

def passCut(tree, fs):
    if tree.q_1 == tree.q_2:
        return False

    if not (tree.cosDPhi_MEt_1 > 0.9 or (tree.cosDPhi_MEt_2 > 0.9 and tree.mt_1 > 150)):
        return False

    if fs == 'et':
        if not (tree.eRelIso < 0.15 and tree.tByTightIsolationMVArun2v1DBnewDMwLT):
            return False
    if fs == 'em':
        if not (tree.mRelIso < 0.15):
            return False
    if fs == 'mt':
        if not (tree.mRelIso < 0.15 and tree.tByTightIsolationMVArun2v1DBnewDMwLT):
            return False
    return True

def loopOneFile(iSample, varName, hist, fs, varBins = 0):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    sumWeights = file.Get('eventCountWeighted').GetBinContent(1)
    print sumWeights
    nEntries = tree.GetEntries()
    hist.Sumw2()
    counter = 0
    for i in range(nEntries):
        tree.GetEntry(i)
        wegiht = 1.0
        if passCut(tree, fs):
            value = -1
            weight = cutSampleTools.getPUWeight(tree.nTruePU)*Lumi*tree.xs*tree.genEventWeight*tree.trigweight_1*tree.trigweight_2/(sumWeights+0.0)
            value = getattr(tree, varName)
            if value > 1200:
                counter += 1
            if value < varBins[0]:
                value = (varBins[0]+varBins[1])/2.0
            elif value > varBins[len(varBins)-1]:
                value = (varBins[len(varBins)-1]+varBins[len(varBins)-2]+0.0)/2.0
            hist.Fill(value, weight)
    print 'nevents with m_eff > 1200: ', counter

def compareSamples(fs):

    varNameDict_et = {'m_eff': 'm(#tau_{e}, #tau_{h}, #slash{E}_{T}) [GeV]',
                      'ePt': 'Electron Pt [GeV]',
                      'tPt': 'Tau Pt [GeV]',
                      'nTruePU': 'nTruePU',
                      'genHT': 'gen HT [GeV]',
                      'X_to_ll': 'gen Mass [GeV]',
                    }
    varNameDict_em = {'m_eff': 'm(#tau_{e}, #tau_{#mu}, #slash{E}_{T}) [GeV]',
                      'ePt': 'Electron Pt [GeV]',
                      'mPt': 'Muon Pt [GeV]',
                      'nTruePU': 'nTruePU',
                    }
    varNameDict_mt = {'m_eff': 'm(#tau_{#mu}, #tau_{h}, #slash{E}_{T}) [GeV]',
                      'tPt': 'Tau Pt [GeV]',
                      'mPt': 'Muon Pt [GeV]',
                      'genHT': 'gen HT [GeV]',
                      'nTruePU': 'nTruePU',
                      'X_to_ll': 'gen Mass [GeV]',
                    }

    varName = 'X_to_ll'
    varBins = 0
    if varName == 'm_eff':
        varBins = array.array('d', [0,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600,900,1200, 1700])
    else:
        varBins = array.array('d', range(0, 1000, 10))
    hist1 = r.TH1F("hist_1", "", len(varBins)-1, varBins)
    hist2 = r.TH1F("hist_2", "", len(varBins)-1, varBins)
    hist3 = r.TH1F("hist_3", "", len(varBins)-1, varBins)
    hist4 = r.TH1F("hist_4", "", len(varBins)-1, varBins)
    hist5 = r.TH1F("hist_5", "", len(varBins)-1, varBins)
    hist6 = r.TH1F("hist_6", "", len(varBins)-1, varBins)

    dir = "/user_data/zmao/2016_signalRegionNoPZeta_fixMuon/"
#     dir = "/user_data/zmao/inclusive/"

    loopOneFile(iSample = '%s/DY-50_LO_all_SYNC_%s_noIso.root' %(dir, fs),
                varName = varName,
                hist = hist1,
                fs = fs,
                varBins = varBins)
    loopOneFile(iSample = '%s/DY-50to150_LO_all_SYNC_%s_noIso.root' %(dir, fs),
                varName = varName,
                hist = hist2,
                fs = fs,
                varBins = varBins)
    loopOneFile(iSample = '%s/DY-150_LO_all_SYNC_%s_noIso.root' %(dir, fs),
                varName = varName,
                hist = hist3,
                fs = fs,
                varBins = varBins)
#     loopOneFile(iSample = '%s/DY-50_LO_HT-200to400_all_SYNC_%s_noIso.root' %(dir, fs),
#                 varName = varName,
#                 hist = hist4,
#                 fs = fs,
#                 varBins = varBins)
#     loopOneFile(iSample = '%s/DY-50_LO_HT-400to600_all_SYNC_%s_noIso.root' %(dir, fs),
#                 varName = varName,
#                 hist = hist5,
#                 fs = fs,
#                 varBins = varBins)
#     loopOneFile(iSample = '%s/DY-50_LO_HT-600toInf_all_SYNC_%s_noIso.root' %(dir, fs),
#                 varName = varName,
#                 hist = hist6,
#                 fs = fs,
#                 varBins = varBins)
    position  = (0.7, 0.9 - 0.06*5, 0.9, 0.88)
    histList = []

    histList.append((hist1, 'Inclusive', 'lp'))
    histList.append((hist2, 'M-50to150', 'f'))
    histList.append((hist3, 'M-150', 'f'))
#     histList.append((hist4, 'HT-200to400', 'f'))
#     histList.append((hist5, 'HT-400to600', 'f'))
#     histList.append((hist6, 'HT-600toInf', 'f'))
    legend = tool.setMyLegend(position, histList)



    if fs == 'et':
        title = varNameDict_et[varName]
    elif fs == 'em':
        title = varNameDict_em[varName]
    elif fs == 'mt':
        title = varNameDict_mt[varName]

    colorList = [r.kBlack, 46, 41, 47, 30, 38]

    c = r.TCanvas("c","Test", 800, 600)
    hist1.SetMarkerSize(0.5)
    hist1.SetMarkerStyle(8)
    hist1.SetLineColor(colorList[0])
    hist1.SetMarkerColor(colorList[0])
    hist2.SetMarkerSize(0.5)
    hist2.SetLineColor(r.kBlack)
    hist2.SetFillColor(colorList[1])
    hist2.SetMarkerColor(colorList[1])

    hist3.SetMarkerSize(0.5)
    hist3.SetLineColor(r.kBlack)
    hist3.SetFillColor(colorList[2])
    hist3.SetMarkerColor(colorList[2])

    hist4.SetMarkerSize(0.5)
    hist4.SetLineColor(r.kBlack)
    hist4.SetFillColor(colorList[3])
    hist4.SetMarkerColor(colorList[3])

    hist5.SetMarkerSize(0.5)
    hist5.SetLineColor(r.kBlack)
    hist5.SetFillColor(colorList[4])
    hist5.SetMarkerColor(colorList[4])

    hist6.SetMarkerSize(0.5)
    hist6.SetLineColor(r.kBlack)
    hist6.SetFillColor(colorList[5])
    hist6.SetMarkerColor(colorList[5])
    if varName == 'm_eff':
        hist1.Scale(1, 'width')
        hist2.Scale(1, 'width')
        hist3.Scale(1, 'width')
        hist4.Scale(1, 'width')
        hist5.Scale(1, 'width')
        hist6.Scale(1, 'width')
        hist1.SetTitle("DY Inclusive/Exclusive Comparison; %s; Events/GeV" %title)
    else:
        hist1.SetTitle("DY Inclusive/Exclusive Comparison; %s; Events" %title)


    stack = r.THStack()
#     stack.Add(hist6)
#     stack.Add(hist5)
#     stack.Add(hist4)
    stack.Add(hist3)
    stack.Add(hist2)

    uncBand = buildUncBand(varBins, [hist2, hist3])

    hist1.SetMinimum(0.0001)


    hist1.Draw("E1")
    stack.Draw('hist H same')
    uncBand.Draw("E2 same")
    hist1.Draw("E1 same")

#     else:
#         hist2.Draw("E1same")
#         hist3.Draw("E1same")
#         hist4.Draw("E1same")
#         hist5.Draw("E1same")
#         hist6.Draw("E1same")

    legend.Draw('same')
    r.gPad.RedrawAxis()

    r.gPad.SetLogy()

    r.gPad.SetTicky()
    r.gPad.SetTickx()
    c.Print('sampleCheck_%s_%s.pdf' %(fs, varName))

cutSampleTools.setupLumiReWeight()
compareSamples('mt')
compareSamples('et')
# compareSamples('em')
cutSampleTools.freeLumiReWeight()
