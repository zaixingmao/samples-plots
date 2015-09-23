#!/usr/bin/env python

import ROOT as r
from array import array
import tool
import math

r.gSystem.Load("libFWCoreFWLite.so")
r.AutoLibraryLoader.enable()

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))


def getPtDistribution(file, hist, hist2 = None, hist3 = None, jetPt = 0, type ='central', Print = False, counter = False):
    f = r.TFile(file)
    tree = f.Get("Events")
    nEntries = tree.GetEntries()

    if Print:
        output = open('evtDump.txt', "w")  #opens & write the file
        output2 = open('matched.txt', "w")  #opens & write the file

    totalTaus = 0
    foundMatch = 0
    if counter:
        passed_30 = 0.0
        passed_35 = 0.0
        total = 0.0

    for i in range(nEntries):
#     for i in range(500):
        tool.printProcessStatus(i, nEntries, processName = 'Looping %s' %file, iPrevious = i-1)
        tree.GetEntry(i)

        #loop over pat taus in an event
        nTaus = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).size()
        nJet = (tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).size()

        totalTaus += nTaus

        if Print and i < 20:
            output.writelines('nTaus: %i ----------------\n' %nTaus)
            for j in range(nTaus):
                output.writelines('pt: %.2f, eta: %.2f, phi: %.2f\n' %((tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(j).pt(),
                                                                    (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(j).eta(),
                                                                    (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(j).phi()))

            output.writelines('nJets: %i ----------------\n' %nJet)
            for j in range(nJet):
                output.writelines('pt: %.2f, eta: %.2f, phi: %.2f\n' %((tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).pt(),
                                                                     (tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).eta(),
                                                                     (tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).phi()))
            output.writelines('-------------------------------------\n')
            
        failed = False
        Found = False
        foundJetPt = 0.0

        if jetPt > 5.0:
            failed = True
            if type == 'central':
                if nJet != 0:
                    for j in range(nJet):
                        pt = (tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).pt()
                        eta = (tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).eta()
                        phi = (tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).phi()
                        found = False
                        if nTaus != 0:
                            for k in range(nTaus):
                                if eta == (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(k).eta():
                                    if phi == (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(k).phi():
                                        found = True
                        if not found and (pt > jetPt):
                            failed = False
                            foundJetPt = pt
                            break
                        if found:
                            foundMatch += 1
                            Found = True

        if Found and Print:
            output2.writelines('nTaus: %i ----------------\n' %nTaus)
            for j in range(nTaus):
                output2.writelines('pt: %.2f, eta: %.2f, phi: %.2f\n' %((tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(j).pt(),
                                                                    (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(j).eta(),
                                                                    (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(j).phi()))

            output2.writelines('nJets: %i ----------------\n' %nJet)
            for j in range(nJet):
                output2.writelines('pt: %.2f, eta: %.2f, phi: %.2f\n' %((tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).pt(),
                                                                     (tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).eta(),
                                                                     (tree.l1extraL1JetParticles_l1extraParticles_Central_RECO).at(j).phi()))
            output2.writelines('-------------------------------------\n')

        weight = (tree.GenEventInfoProduct_generator__SIM).weights()[0]
        if hist2 != None:
            if (tree.GenEventInfoProduct_generator__SIM).hasBinningValues():
                hist2.Fill(200000.0*math.pow((tree.GenEventInfoProduct_generator__SIM).binningValues()[0], -4.5), (tree.GenEventInfoProduct_generator__SIM).weights()[0])
                if hist3 != None:
                    hist3.Fill((tree.GenEventInfoProduct_generator__SIM).binningValues()[0], (tree.GenEventInfoProduct_generator__SIM).weights()[0])

        xValue = foundJetPt            
        if (nTaus != 0):
            xValue = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(0).pt()
        else:
            xValue = -1
        if nTaus < 2:
            yValue = -1
        else:
            yValue = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(1).pt()

#             print xValue, yValue, weight
        if not failed:
            hist.Fill(xValue, yValue, weight)
        else:
            hist.Fill(-1, -1, weight)

        if counter:
            total += weight
            if (yValue >= 40.0) or ((yValue > 35.0) and (foundJetPt > 30.0)):
                passed_35 += weight
            if (yValue >= 40.0) or ((yValue > 30.0) and (foundJetPt > 30.0)):
                passed_30 += weight

    if Print:
        output.close()
        output2.writelines('totalTaus: %i, foundMatch: %i' %(totalTaus,foundMatch))
        output2.close()


    if counter:
        if hist2 != None:
            print ''
            print 'pass_30: %.8f, %.8f' %(1.0 - passed_30/total, passed_30/total)
            print 'pass_35: %.8f, %.8f' %(1.0 - passed_35/total, passed_35/total)
        else:
            print ''
            print 'pass_30: %.8f' %(passed_30/total)
            print 'pass_35: %.8f' %(passed_35/total)

    print ''

    if hist2 == None:
        return hist
    elif hist3 == None:
        return hist, hist2
    else:
        return hist, hist2, hist3



def getBothDistribution(sigHist, bkgHist, graph, graph2, diff = 0, tauPtCut = 40.5):
    nBins = sigHist.GetNbinsX()
    sigTotal = sigHist.Integral(0, nBins+1, 0, nBins+1)
    if not (bkgHist == None):
        bkgTotal = bkgHist.Integral(0, nBins+1, 0, nBins+1)
        print bkgTotal
    for i in range(1, nBins+1, 1):
        tool.printProcessStatus(i, nBins+1, processName = 'running bothDistribution', iPrevious = i-1)
        if i + diff < nBins+1:
            sigValue = sigHist.Integral(i+diff, nBins+1, i, nBins+1)
            if not (bkgHist == None):
                bkgValue = bkgHist.Integral(i+diff, nBins+1, i, nBins+1)
        else:
            bkgValue = 0.
            sigValue = 0.
        if (sigHist.GetXaxis().GetBinCenter(i) == tauPtCut):
            print sigHist.GetXaxis().GetBinCenter(i), 1 - bkgValue/bkgTotal, sigValue/sigTotal
            if not (bkgHist == None):
                graph2.SetPoint(i, 1 - bkgValue/bkgTotal, sigValue/sigTotal)
        if not (bkgHist == None):
            graph.SetPoint(i, 1 - bkgValue/bkgTotal, sigValue/sigTotal)
        else:
            graph.SetPoint(i, sigHist.GetXaxis().GetBinCenter(i), sigValue/sigTotal)

    print ''
    return graph

def getDistribution2(sigHist, bkgHist, distHist, distHist2):
    nBins = distHist.GetNbinsX()
    for i in range(1, nBins+1, 1):
        tool.printProcessStatus(i, nBins, processName = 'running getDistribution2', iPrevious = i-1)
        for j in range(1, nBins+1, 1):
            sigValue = sigHist.Integral(i, nBins+1, j, nBins+1)
            bkgValue = bkgHist.Integral(i, nBins+1, j, nBins+1)
            if bkgValue != 0:
                distHist2.Fill(distHist.GetBinCenter(i), distHist.GetBinCenter(j), (sigValue+0.0)/(bkgValue+ 0.0))
    print ''
    return distHist2

def go(sig, bkg):

    bins_array = array('d', range(20,151,1))
    sigHist = r.TH2F('sigHist', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)
    bkgHist = r.TH2F('bkgHist', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)
    sigHistJet1 = r.TH2F('sigHistJet1', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)
    bkgHistJet1 = r.TH2F('bkgHistJet1', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)
    sigHistJet2 = r.TH2F('sigHistJet2', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)
    bkgHistJet2 = r.TH2F('bkgHistJet2', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)
    sigHistJet3 = r.TH2F('sigHistJet3', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)
    bkgHistJet3 = r.TH2F('bkgHistJet3', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)

    bkgHist2 = r.TH2F('bkgHist2', "", 10000, 0, 1.0, 10000, 0, 1.0)
    bkgHistJet = r.TH2F('bkgHistJet', "", 10000, 0, 1.0, 10000, 0, 1.0)

    distHist3 = r.TH1F('distHist3', "", len(bins_array)-1, bins_array)

    distHist = r.TGraph()
    distHist_2 = r.TGraph()
    distHist2 = r.TGraph()
    distHist2_2 = r.TGraph()
    distHist4 = r.TGraph()
    distHist4_2 = r.TGraph()
    distHist5 = r.TGraph()
    distHist5_2 = r.TGraph()

    distHist3.SetTitle('; PtHat; weight')

#     distHist2 = r.TH2F('distHist2', "", len(bins_array)-1, bins_array, len(bins_array)-1, bins_array)

    sigHist = getPtDistribution(sig, sigHist, None, None, 0.0, 'central', False, True)
    sigHistJet1 = getPtDistribution(sig, sigHistJet1, None, None, 30.0, 'central', False, True)
    sigHistJet2 = getPtDistribution(sig, sigHistJet2, None, None, 40.0)
    sigHistJet3 = getPtDistribution(sig, sigHistJet3, None, None, 50.0)

    sigHist.SetTitle('h2#tau#tau; Leading jet Pt; Leading #tau Pt')

    bkgHist, bkgHist2, distHist3 = getPtDistribution(bkg, bkgHist, bkgHist2, distHist3, 0.0, 'central', False, True)
    bkgHistJet1, bkgHistJet = getPtDistribution(bkg, bkgHistJet1, bkgHistJet, None, 30.0, 'central', False, True)
    bkgHistJet2, bkgHistJet = getPtDistribution(bkg, bkgHistJet2, bkgHistJet, None, 40.0)
    bkgHistJet3, bkgHistJet = getPtDistribution(bkg, bkgHistJet3, bkgHistJet, None, 50.0)

    bkgHist.SetTitle('QCD; Leading jet Pt; Leading #tau Pt')
    bkgHist2.SetTitle('QCD; 200000*PtHat^{-4.5}; weight')

    getBothDistribution(sigHist, bkgHist, distHist, distHist_2)
    getBothDistribution(sigHist, bkgHist, distHist5, distHist5_2, 5)
    getBothDistribution(sigHist, bkgHist, distHist2, distHist2_2, 10)
    getBothDistribution(sigHist, bkgHist, distHist4, distHist4_2, 15)

    jet1 = r.TGraph()
    jet1_2 = r.TGraph()
    jet2 = r.TGraph()
    jet2_2 = r.TGraph()
    jet3 = r.TGraph()
    jet3_2 = r.TGraph()



    getBothDistribution(sigHistJet1, bkgHistJet1, jet1, jet1_2, 0, 30.5)
    getBothDistribution(sigHistJet2, bkgHistJet2, jet2, jet2_2, 0, 30.5)
    getBothDistribution(sigHistJet3, bkgHistJet3, jet3, jet3_2, 0, 30.5)


    fakeHist1 = r.TH1F()
    fakeHist1.SetMarkerStyle(5)
    fakeHist2 = r.TH1F()
    fakeHist2.SetMarkerStyle(2)
    fakeHist2.SetMarkerColor(r.kBlue)
    fakeHist3 = r.TH1F()
    fakeHist3.SetMarkerStyle(25)
    fakeHist3.SetMarkerColor(r.kRed)
    fakeHist4 = r.TH1F()
    fakeHist4.SetMarkerStyle(32)
    fakeHist4.SetMarkerColor(r.kGreen)
    fakeHist5 = r.TH1F()
    fakeHist5.SetMarkerStyle(5)
    fakeHist5.SetMarkerColor(r.kBlue)
    fakeHist6 = r.TH1F()
    fakeHist6.SetMarkerStyle(5)
    fakeHist6.SetMarkerColor(r.kRed)
    fakeHist7 = r.TH1F()
    fakeHist7.SetMarkerStyle(5)
    fakeHist7.SetMarkerColor(r.kGreen)


    psfile = 'test2.pdf'
    c = r.TCanvas("c","Test", 600, 600)
    c.SetGrid()
    c.SetFillStyle(4000)
#     distHist.GetXaxis().SetLimits(0.998,1.00001)
    distHist.GetXaxis().SetLimits(0.999,1.00001)

    distHist.SetMinimum(0.001)
    distHist.SetMaximum(0.8)

    c.SetLogy()
    distHist.GetXaxis().SetNdivisions(210)
    distHist.Draw("AP")

    distHist.SetMarkerStyle(7)
    distHist.GetYaxis().SetTitleOffset(1.4)
    distHist5.SetMarkerStyle(7)
    distHist5_2.SetMarkerColor(r.kBlue)
    distHist5.SetMarkerColor(r.kBlue)
#     distHist5.Draw('PSame')

    distHist2.SetMarkerStyle(7)
    distHist2_2.SetMarkerColor(r.kRed)

    distHist2.SetMarkerColor(r.kRed)
#     distHist2.Draw('PSame')
    distHist4.SetMarkerStyle(7)
    distHist4_2.SetMarkerColor(r.kGreen)
    distHist4.SetMarkerColor(r.kGreen)
#     distHist4.Draw('PSame')

    distHist_2.SetMarkerStyle(5)
    distHist5_2.SetMarkerStyle(2)
    distHist2_2.SetMarkerStyle(25)
    distHist4_2.SetMarkerStyle(32)

#     distHist2_2.Draw('PSame')
#     distHist5_2.Draw('PSame')
    distHist_2.Draw('PSame')
#     distHist4_2.Draw('PSame')

    jet1.SetMarkerStyle(7)
    jet1.SetMarkerColor(r.kBlue)
    jet1_2.SetMarkerStyle(5)
    jet1_2.SetMarkerColor(r.kBlue)
    jet2.SetMarkerStyle(7)
    jet2.SetMarkerColor(r.kRed)
    jet2_2.SetMarkerStyle(5)
    jet2_2.SetMarkerColor(r.kRed)
    jet3.SetMarkerStyle(7)
    jet3.SetMarkerColor(r.kGreen)
    jet3_2.SetMarkerStyle(5)
    jet3_2.SetMarkerColor(r.kGreen)

    jet1.Draw('PSame')

    jet1_2.Draw('PSame')
    jet2.Draw('PSame')
    jet2_2.Draw('PSame')
    jet3.Draw('PSame')
    jet3_2.Draw('PSame')

    l = tool.setMyLegend(lPosition = [0.2, 0.45, 0.5, 0.25], lHistList = [(fakeHist1, 'same pt cut (tau pt 40)'), 
#                                                                         (fakeHist2, 'leading + 5 (35, 40, 45)'),
#                                                                         (fakeHist3, 'leading + 10 (35, 40, 45)'),
#                                                                         (fakeHist4, 'leading + 15 (35, 40, 45)'),
                                                                        (fakeHist5, 'same with jet pt 30 (tau pt 30)'),
                                                                        (fakeHist6, 'same with jet pt 40 (tau pt 30)'),
                                                                        (fakeHist7, 'same with jet pt 50 (tau pt 30)'),
])
    l.Draw('same')
    c.Print('%s(' %psfile)
    c.SetLogy(0)

    c.Clear()
    distHist3.Draw()
    c.Print('%s' %psfile)
    c.Clear()

#     p1 = r.TPad("p1","p1",0.,1,1.,0.0)
#     p1.SetMargin(0.13, 0.13, 0.13, 0.13)
#     p1.SetGrid()
    p2 = r.TPad("p1","p1",0.,1,1.,0.0)
    p2.SetMargin(0.13, 0.13, 0.13, 0.13)
    p2.SetGrid()
# 
# #     p1.Draw()
# #     p1.cd()
# #     distHist2.GetXaxis().SetNdivisions(216)
# #     distHist2.GetYaxis().SetNdivisions(216)
# #     distHist2.GetYaxis().SetTitleOffset(1.2)
# #     distHist2.Draw('COLZ')
# #     c.Print('%s' %psfile) 
# #     c.Clear()
    p2.Draw()
    p2.cd()
    sigHist.Draw('COLZ')
    sigHist.GetYaxis().SetTitleOffset(1.2)
    sigHist.GetXaxis().SetNdivisions(216)
    sigHist.GetYaxis().SetNdivisions(216)
    c.Print('%s' %psfile)
    c.Clear()
    p3 = r.TPad("p1","p1",0.,1,1.,0.0)
    p3.SetMargin(0.13, 0.13, 0.13, 0.13)
    p3.SetGrid()

    p3.Draw()
    p3.cd()
    bkgHist.Draw('COLZ')
    bkgHist.GetYaxis().SetTitleOffset(1.2)
    bkgHist.GetXaxis().SetNdivisions(216)
    bkgHist.GetYaxis().SetNdivisions(216)
    c.Print('%s' %psfile) 
    c.Clear()
    bkgHistJet2.Draw('COLZ')
    bkgHistJet2.GetYaxis().SetTitleOffset(1.2)
    bkgHistJet2.GetXaxis().SetNdivisions(216)
    bkgHistJet2.GetYaxis().SetNdivisions(216)
    c.Print('%s' %psfile) 
    c.Clear()
    sigHistJet2.Draw('COLZ')
    sigHistJet2.GetYaxis().SetTitleOffset(1.2)
    sigHistJet2.GetXaxis().SetNdivisions(216)
    sigHistJet2.GetYaxis().SetNdivisions(216)

    c.Print('%s)' %psfile) 


    c.Close()
 
go(sig = "/home/zmao/3E56199D-1D70-E411-B425-7845C4FC36CB.root",
   bkg = "/home/zmao/EE72ECF8-996B-E411-B541-20CF305B057C.root")