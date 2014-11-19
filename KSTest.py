#!/usr/bin/env python
import ROOT as r
import optparse
import tool


r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def opts():
    parser = optparse.OptionParser()
    parser.add_option("-f", dest="file", default="", help="")
    options, args = parser.parse_args()
    return options

options = opts()

f = r.TFile(options.file)
testTree = f.Get("TestTree")
trainTree = f.Get("TrainTree")

nBins = 20
xMin = -1.0
xMax = 1.0

BDT_Sig_Train = r.TH1F('BDT_Sig_Train', 'BDT_Sig_Train', nBins, xMin, xMax)
BDT_Sig_Test = r.TH1F('BDT_Sig_Test', 'BDT_Sig_Test', nBins, xMin, xMax)
BDT_Bkg_Train = r.TH1F('BDT_Bkg_Train', 'BDT_Bkg_Train', nBins, xMin, xMax)
BDT_Bkg_Test = r.TH1F('BDT_Bkg_Test', 'BDT_Bkg_Test', nBins, xMin, xMax)

totalTest = testTree.GetEntries()
for i in range(totalTest):
    testTree.GetEntry(i)    
    if testTree.className == "Signal":
        BDT_Sig_Test.Fill(testTree.BDT, testTree.weight)
    else:
        BDT_Bkg_Test.Fill(testTree.BDT, testTree.weight)

totalTrain = trainTree.GetEntries()
for i in range(totalTrain):
    trainTree.GetEntry(i)    
    if trainTree.className == "Signal":
        BDT_Sig_Train.Fill(trainTree.BDT, trainTree.weight)
    else:
        BDT_Bkg_Train.Fill(trainTree.BDT, trainTree.weight)

BDT_Bkg_Train.Sumw2()
BDT_Sig_Train.Sumw2()

print 'signal: %.4f' %(BDT_Sig_Test.KolmogorovTest(BDT_Sig_Train))
print 'background: %.4f' %(BDT_Bkg_Test.KolmogorovTest(BDT_Bkg_Train))

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



c = r.TCanvas("c","Test", 800, 600)
BDT_Sig_Test.Draw()
BDT_Sig_Test.SetMaximum(0.5)
BDT_Sig_Train.Draw('sameE1P')
BDT_Bkg_Test.Draw('same')
BDT_Bkg_Train.Draw('sameE1P')
c.Print('KS.pdf')