#!/usr/bin/env python

import ROOT as r
import tool
import plotTurnOn

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

bins = plotTurnOn.bins
labels = ["eIsPromptElectron", "eIsPromptMuon", "eIsTau2Electron", "eIsTau2Muon", "eIsTauh", "other"]
m_labels = ["mIsPromptElectron", "mIsPromptMuon", "mIsTau2Electron", "mIsTau2Muon", "mIsTauh", "other"]

def loop(iSample, hist, m_hist, hist_eIsTau2E, hist_eIsTauh, hist_eIsTau2E_withTrigger, hist_eIsTauh_withTrigger):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        if abs(tree.eEta) >= 2.1:
            continue
        if abs(tree.mEta) >= 2.1:
            continue
        if tree.q_1 == tree.q_2:
            continue
        #electron
        if tree.eIsPromptElectron:
            hist.Fill(tree.ePt, 0)
            print "isPromptElectron: %i, %i, %.3f, %.3f, %.3f" %(tree.lumi, tree.evt, tree.ePt, tree.eEta, tree.ePhi)
        elif tree.eIsPromptMuon:
            hist.Fill(tree.ePt, 1)
        elif tree.eIsTau2Electron:
            hist.Fill(tree.ePt, 2)
            hist_eIsTau2E.Fill(tree.ePt)
            if tree.singleE27_2p1_WP75Pass and tree.eSingleEle27_2p1_WP75:
                hist_eIsTau2E_withTrigger.Fill(tree.ePt)
                
        elif tree.eIsTau2Muon:
            hist.Fill(tree.ePt, 3)
        elif tree.eIsTauh:
            hist.Fill(tree.ePt, 4)
            hist_eIsTauh.Fill(tree.ePt)
            if tree.singleE27_2p1_WP75Pass and tree.eSingleEle27_2p1_WP75:
                hist_eIsTauh_withTrigger.Fill(tree.ePt)

        else:
            hist.Fill(tree.ePt, 5)
        #muon
        if tree.mIsPromptElectron:
            m_hist.Fill(tree.mPt, 0)
        elif tree.mIsPromptMuon:
            m_hist.Fill(tree.mPt, 1)
        elif tree.mIsTau2Electron:
            m_hist.Fill(tree.mPt, 2)
        elif tree.mIsTau2Muon:
            m_hist.Fill(tree.mPt, 3)
        elif tree.mIsTauh:
            m_hist.Fill(tree.mPt, 4)
        else:
            m_hist.Fill(tree.mPt, 5)
    for i in range(len(labels)):
        hist.GetYaxis().SetBinLabel(i+1, labels[i])
        m_hist.GetYaxis().SetBinLabel(i+1, m_labels[i])

    return hist, m_hist, hist_eIsTau2E, hist_eIsTauh, hist_eIsTau2E_withTrigger, hist_eIsTauh_withTrigger

dir = "triggerStudy"
eID = 'CBTight'

fileList = {}

for iMass in [2000]:#[500, 2000, 5000]:#range(500, 5500, 500):
   fileList["Zprime%s" %iMass] = "/nfs_scratch/zmao/%s/%s/ZPrime_%s_all_SYNC_em_BSM3G.root" %(dir, eID, iMass)

# fileList = {"TTJets": "/nfs_scratch/zmao/%s/%s/TTJets_all_SYNC_em_BSM3G.root" %(dir, eID)}

for iName in fileList.keys():

    hist = r.TH2D("hist%s" %iName, "", len(bins)-1, bins, 6, 0, 6)
    hist.SetTitle("%s; e pt; " %iName)
    m_hist = r.TH2D("m_hist%s" %iName, "", len(bins)-1, bins, 6, 0, 6)
    m_hist.SetTitle("%s; m pt; " %iName)

    hist_eIsTau2E = r.TH1D("hist_eIsTau2E%s" %iName, "", len(bins)-1, bins)
    hist_eIsTauh = r.TH1D("hist_eIsTauh%s" %iName, "", len(bins)-1, bins)
    hist_eIsTau2E_withTrigger = r.TH1D("hist_eIsTau2E_withTrigger%s" %iName, "", len(bins)-1, bins)
    hist_eIsTauh_withTrigger = r.TH1D("hist_eIsTauh_withTrigger%s" %iName, "", len(bins)-1, bins)

    hist, m_hist, hist_eIsTau2E, hist_eIsTauh, hist_eIsTau2E_withTrigger, hist_eIsTauh_withTrigger = loop(fileList[iName],hist, m_hist, hist_eIsTau2E, hist_eIsTauh, hist_eIsTau2E_withTrigger, hist_eIsTauh_withTrigger)

    print hist_eIsTau2E.Integral(0, len(bins))
    print hist_eIsTauh.Integral(0, len(bins))

    g = r.TGraphAsymmErrors(hist_eIsTauh, hist_eIsTau2E+hist_eIsTauh)
    g.SetMarkerStyle(8)
    g.SetMarkerSize(0.9)

    g_withTrigger = r.TGraphAsymmErrors(hist_eIsTauh_withTrigger, hist_eIsTau2E_withTrigger+hist_eIsTauh_withTrigger)
    g_withTrigger.SetMarkerStyle(8)
    g_withTrigger.SetMarkerSize(0.9)
    g_withTrigger.SetMarkerColor(r.kRed)
    g_withTrigger.SetLineColor(r.kRed)

    psfile = 'eMuOrigin_%s_%s.pdf' %(iName, eID)
    c = r.TCanvas("c","Test", 1000, 800)
    hist.GetYaxis().SetLabelSize(0.02)
    hist.Draw("COLZ TEXT0")
    c.Print('%s(' %psfile)
    m_hist.GetYaxis().SetLabelSize(0.02)
    m_hist.Draw("COLZ TEXT0")
    c.Print('%s' %psfile)
    c.Clear()

    null = r.TH2F("null","", len(bins)-1, bins, 1, 0, 1.1)
    null.SetMaximum(1.2)
    null.SetTitle("eIsTauh/(eIsTau2Ele+eIsTauh); e pt; eIsTauh/(eIsTau2Ele+eIsTauh)")
    null.SetStats(False)
    null.Draw()

    leg = tool.setMyLegend((0.5, 0.8 - 0.06*3, 0.92, 0.8), [(g, 'before trigger selection', 'ep'), (g_withTrigger, 'after trigger selection', 'ep')])

    g.Draw('same PE')
    g_withTrigger.Draw('same PE')
    leg.Draw('same')
    c.Print('%s)' %psfile)

