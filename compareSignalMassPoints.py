#!/usr/bin/env python

import ROOT as r
import tool
import array

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
jet = lvClass()
met = lvClass()

def getVarValue(l1, l2, met, varName):
    if "m_eff" in varName:
        mass = (l1+l2+met).mass()
    elif "m_vis" in varName:
        mass = (l1+l2).mass()
    else:
        mass = 1.0
    if mass <= 0:
        return 0
    if "pt_1" in varName:
        return l1.pt()/mass
    elif "pt_2" in varName:
        return l2.pt()/mass
    elif "eta_1" in varName:
        return l1.eta()/mass
    elif "eta_2" in varName:
        return l2.eta()/mass
    elif "met" in varName:
        return met.pt()/mass

def getHist(file, hist, varName):
    tfile = r.TFile(file)    
    tree = tfile.Get('Ntuple')
    nEntries = tree.GetEntries()
    for i in range(nEntries):
        tree.GetEntry(i)
        tool.printProcessStatus(i, nEntries, 'Looping sample %s' %(file), i-1)
        met.SetCoordinates(tree.pfMetEt, 0.0, tree.pfMetPhi, 0)
        l1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
        l2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)
        hist.Fill(getVarValue(l1, l2, met, varName))
    print ''
    
    return hist


def go(fileList, varName):
    hists = []
    varBins = array.array('d', range(30, 110, 10) + range(125, 225, 25) + range(250, 450, 50))
    counter = 0
    histList = []
    for iFile, mass in fileList:
        hists.append(r.TH1F("hist%i" %counter, "", 20, 0, 1.0))
#         hists.append(r.TH1F("hist%i" %counter, "", 30, 0, 300))
#         hists.append(r.TH1F("hist%i" %counter, "", 44, -2.2, 2.2))
        hists[counter].Sumw2()
        hists[counter] = getHist(iFile, hists[counter], varName)
        hists[counter].SetLineColor(counter + 1)
        hists[counter].Scale(1/hists[counter].Integral(0, hists[counter].GetNbinsX()+1))
        histList.append((hists[counter], "Z'(%s)#rightarrow #tau#tau" %(mass), 'l'))
        counter += 1

    c = r.TCanvas("c","Test", 400, 300)
    max = hists[0].GetMaximum()
    hists[0].SetTitle("; %s; A.U." %varName)
    hists[0].GetYaxis().SetTitleOffset(1.1)

    hists[0].Draw("EH")

    for i in range(1, len(hists)):
        hists[i].Draw("sameEH")
        if hists[i].GetMaximum() > max:
            max = hists[i].GetMaximum()
    hists[0].SetMaximum(1.2*max)
    position  = (0.7, 0.85 - 0.06*4, 0.9, 0.85)
    legends = tool.setMyLegend(position, histList)
    legends.Draw('same')
    psfile = '%s.pdf' %varName
    c.Print('%s' %psfile)


fileList = []
dir = '/user_data/zmao/NoBTag_7_6_X/'
for iMass in range(500, 4500, 500):
    fileList.append(("%s/ZPrime_%i_all_SYNC_em_noIso.root" %(dir, iMass), "%i" %iMass))

go(fileList, "met_over_m_vis")
# go(fileList, "eta_2")


    