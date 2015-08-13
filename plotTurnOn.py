#!/usr/bin/env python

import ROOT as r
import plots_cfg
import tool
import optparse
from array import array

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs


def loop_one_sample(iSample, varName, hist1, hist2):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        if tree.mPt < 26:
            continue
        if tree.q_1 == tree.q_2:
            continue
        hist1.Fill(getattr(tree, varName))
        if tree.muTauPass and tree.mMuTau and tree.mMuTauOverlap and tree.tTau20AgainstMuon and tree.tTauOverlapMu:
            hist2.Fill(getattr(tree, varName))


    print ''

def run(varName, bins):
    files_mc = ['/nfs_scratch/zmao/13TeV_samples//DY_all_SYNC_mt_inclusive.root']
    hist_mc_all = r.TH1F("hist_mc_all", "", len(bins)-1, bins)
    hist_mc_pass = r.TH1F('hist_mc_pass', '', len(bins)-1, bins)
    file_data = '/nfs_scratch/zmao/13TeV_samples//data_all_SYNC_mt_inclusive.root'
    hist_data_all = r.TH1F('hist_data_all', '', len(bins)-1, bins)
    hist_data_pass = r.TH1F('hist_data_pass', '', len(bins)-1, bins)

    for iSample in files_mc:
        loop_one_sample(iSample, varName, hist_mc_all, hist_mc_pass)
#     hist_mc_all.Sumw2()
#     hist_mc_pass.Sumw2()

    loop_one_sample(file_data, varName, hist_data_all, hist_data_pass)
#     hist_data_all.Sumw2()
#     hist_data_pass.Sumw2()


    g_mc = r.TGraphAsymmErrors()
    g_mc.BayesDivide(hist_mc_pass, hist_mc_all)
    g_data = r.TGraphAsymmErrors()
    g_data.BayesDivide(hist_data_pass, hist_data_all)

    histList = [(g_mc, 'DY_MC', 'ep'), (g_data, 'Observed', 'ep')]
    g_data.SetMarkerStyle(8)
    g_data.SetMarkerSize(0.9)
    g_data.SetMarkerColor(r.kBlack)
    psfile = 'tauTrigTurnOnCurve_%s.pdf' %varName
    c = r.TCanvas("c","Test", 800, 600)
    g_mc.SetMaximum(1.0)

    g_mc.SetTitle("tau trigger turn-on curve; #tau pt; Effeciency")
    g_mc.SetMarkerStyle(8)
    g_mc.SetMarkerSize(0.9)
    g_mc.SetMarkerColor(r.kBlue)

    null = r.TH2F("null","", len(bins)-1, bins, 1, 0, 1.1)
    null.SetStats(False)
    null.Draw()
    g_mc.Draw('same PE')
    g_data.Draw('same PE')


    leg = tool.setMyLegend((0.6, 0.9 - 0.06*2, 0.87, 0.9), histList)
    leg.Draw('same')
    c.Print('%s' %psfile)
    c.Close()


bins = array('d', range(0, 45, 5) + range(40, 70, 10)+[60,100,200])
bins2 = []
for i in range(21):
    bins2.append(-4 + i*0.4)
run('tPt', bins)
run('tEta',  array('d', bins2))
