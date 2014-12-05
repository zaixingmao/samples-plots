#!/usr/bin/env python
import ROOT as r
import optparse
import tool


r.gROOT.SetBatch(True)  # to suppress canvas pop-outs


def KSTest(ifile, ofile, name):

    f = r.TFile(ifile)
    testTree = f.Get("TestTree")
    trainTree = f.Get("TrainTree")

    nBins = 20
    nBins2 = 100000
    xMin = -1.0
    xMax = 1.0

    BDT_Sig_Train = r.TH1F('BDT_Sig_Train', 'BDT_Sig_Train', nBins, xMin, xMax)
    BDT_Sig_Test = r.TH1F('BDT_Sig_Test', 'Overtraining Check (%s)' %name, nBins, xMin, xMax)
    BDT_Bkg_Train = r.TH1F('BDT_Bkg_Train', 'BDT_Bkg_Train', nBins, xMin, xMax)
    BDT_Bkg_Test = r.TH1F('BDT_Bkg_Test', 'BDT_Bkg_Test', nBins, xMin, xMax)

    BDT_Sig_Train_4KS = r.TH1F('BDT_Sig_Train_4KS', 'BDT_Sig_Train_4KS', nBins2, xMin, xMax)
    BDT_Sig_Test_4KS = r.TH1F('BDT_Sig_Test_4KS', 'BDT_Sig_Test_4KS', nBins2, xMin, xMax)
    BDT_Bkg_Train_4KS = r.TH1F('BDT_Bkg_Train_4KS', 'BDT_Bkg_Train_4KS', nBins2, xMin, xMax)
    BDT_Bkg_Test_4KS = r.TH1F('BDT_Bkg_Test_4KS', 'BDT_Bkg_Test_4KS', nBins2, xMin, xMax)

    totalTest = testTree.GetEntries()
    for i in range(totalTest):
        testTree.GetEntry(i)    
        if testTree.className == "Signal":
            BDT_Sig_Test.Fill(testTree.BDT, testTree.weight)
            BDT_Sig_Test_4KS.Fill(testTree.BDT, testTree.weight)
        else:
            BDT_Bkg_Test.Fill(testTree.BDT, testTree.weight)
            BDT_Bkg_Test_4KS.Fill(testTree.BDT, testTree.weight)

    totalTrain = trainTree.GetEntries()
    for i in range(totalTrain):
        trainTree.GetEntry(i)    
        if trainTree.className == "Signal":
            BDT_Sig_Train.Fill(trainTree.BDT, trainTree.weight)
            BDT_Sig_Train_4KS.Fill(trainTree.BDT, trainTree.weight)
        else:
            BDT_Bkg_Train.Fill(trainTree.BDT, trainTree.weight)
            BDT_Bkg_Train_4KS.Fill(trainTree.BDT, trainTree.weight)

    BDT_Bkg_Train.Sumw2()
    BDT_Sig_Train.Sumw2()
    sigKS = BDT_Sig_Test_4KS.KolmogorovTest(BDT_Sig_Train_4KS)
    bkgKS = BDT_Bkg_Test_4KS.KolmogorovTest(BDT_Bkg_Train_4KS)
    print 'signal: %.4f' %sigKS
    print 'background: %.4f' %bkgKS

    BDT_Bkg_Train.Scale(1/BDT_Bkg_Train.Integral())
    BDT_Bkg_Train.SetMarkerColor(r.kRed)
    BDT_Bkg_Train.SetMarkerStyle(21)

    BDT_Bkg_Test.SetLineColor(r.kRed)
    BDT_Bkg_Test.SetFillColor(r.kRed)
    BDT_Bkg_Test.SetFillStyle(3354)
    BDT_Bkg_Test.Scale(1/BDT_Bkg_Test.Integral())

    BDT_Sig_Train.Scale(1/BDT_Sig_Train.Integral())
    BDT_Sig_Train.SetMarkerColor(r.kBlue)
    BDT_Sig_Train.SetMarkerStyle(21)

    BDT_Sig_Test.SetLineColor(r.kBlue)
    BDT_Sig_Test.SetFillColor(r.kBlue)
    BDT_Sig_Test.SetFillStyle(3001) 
    BDT_Sig_Test.Scale(1/BDT_Sig_Test.Integral())

    legendHistos1 = []
    legendHistos1.append((BDT_Bkg_Test, 'bkg test'))
    legendHistos1.append((BDT_Bkg_Train, 'bkg train'))
    legendHistos1.append((BDT_Bkg_Train, 'KS: %0.3f' %bkgKS))

    legendHistos2 = []
    legendHistos2.append((BDT_Sig_Test, 'sig test'))
    legendHistos2.append((BDT_Sig_Train, 'sig train'))
    legendHistos2.append((BDT_Sig_Train, 'KS: %0.3f' %sigKS))


    l1 = tool.setMyLegend(lPosition=(0.2, 0.67, 0.5, 0.82), lHistList=legendHistos1)
    l2 = tool.setMyLegend(lPosition=(0.6, 0.67, 0.9, 0.82), lHistList=legendHistos2)

    r.gStyle.SetOptStat(0)
    c = r.TCanvas("c","Test", 800, 600)
    BDT_Sig_Test.Draw()
    BDT_Sig_Test.SetMaximum(0.5)
    BDT_Sig_Train.Draw('sameE1P')
    BDT_Bkg_Test.Draw('same')
    BDT_Bkg_Train.Draw('sameE1P')
    l1.Draw('same')
    l2.Draw('same')

    c.Print('%s.pdf' %ofile)

# massPoints = ['260','270','280','290','300','310','320','330','340','350']
massPoints = ['260','300','350']

nTreesList = ['150']
for nTrees in nTreesList:
    for iMass in massPoints:
        postFix = '_7_n%s_mJJ_1M' %nTrees
        KSTest('/scratch/zmao/TMVA/newMethod/TMVA%s%s.root' %(iMass,postFix), '/scratch/zmao/TMVA/pdf/TMVA%s%s' %(iMass,postFix), 'H2hh%s_n%s' %(iMass, nTrees))
