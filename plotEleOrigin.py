#!/usr/bin/env python

import ROOT as r
import tool
from array import array
import math
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

bins = array('d', range(0, 800, 50))#plotTurnOn.bins
labels = ["PromptElectron", "PromptMuon", "Tau2Electron", "Tau2Muon", "Tauh", "other"]
m_labels = ["mIsPromptElectron", "mIsPromptMuon", "mIsTau2Electron", "mIsTau2Muon", "mIsTauh", "other"]
t_labels = ["PromptElectron", "PromptMuon", "Tau2Electron", "Tau2Muon", "Tauh", "other"]

def loop(iSample, hist, t_hist):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    counter = 0
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)

        if not (tree.tByTightIsolationMVArun2v1DBnewDMwLT > 0.5):
            continue
#         if not ( 0. < tree.cosDPhi_MEt_1 < 0.9 and 70 < tree.mt_1):
#             continue
#         if (tree.cosDPhi_MEt_2 > 0.9):
#             continue

        if not ( tree.cosDPhi_MEt_1 > 0.9 or (tree.cosDPhi_MEt_2 > 0.9 and tree.mt_1 > 120)):
            continue
        if tree.q_1 == tree.q_2:
            continue

        electronVar = 'm_eff'#'mPt'
        #electron
        if tree.eIsPromptElectron:
            hist.Fill(getattr(tree, electronVar), 0)
        elif tree.eIsPromptMuon:
            hist.Fill(getattr(tree, electronVar), 1)
        elif tree.eIsTau2Electron:
            hist.Fill(getattr(tree, electronVar), 2)               
        elif tree.eIsTau2Muon:
            hist.Fill(getattr(tree, electronVar), 3)
        elif tree.eIsTauh:
            hist.Fill(getattr(tree, electronVar), 4)
        else:
            hist.Fill(getattr(tree, electronVar), 5)
#          if counter < 10:
#             print ''
#             print 'lumi: %i, event: %i' %(tree.lumi, tree.evt)
#             print "ePt: %.3f, eEta: %.3f, ePhi: %.3f" %(tree.ePt, tree.eEta, tree.ePhi)
#             print "tPt: %.3f, tEta: %.3f, tPhi: %.3f" %(tree.tPt, tree.tEta, tree.tPhi)
#             print "********************************"
#             counter += 1

        muonVar = 'm_eff'#'mPt'
#         muon
#         if tree.mIsPromptElectron:
#             hist.Fill(getattr(tree, muonVar), 0)
#         elif tree.mIsPromptMuon:
#             hist.Fill(getattr(tree, muonVar), 1)
#         elif tree.mIsTau2Electron:
#             hist.Fill(getattr(tree, muonVar), 2)
#         elif tree.mIsTau2Muon:
#             hist.Fill(getattr(tree, muonVar), 3)
#         elif tree.mIsTauh:
#             hist.Fill(getattr(tree, muonVar), 4)
#         else:
#             hist.Fill(getattr(tree, muonVar), 5)

        tauVar = 'm_eff'#'tPt'
#         tau
        if tree.tIsPromptElectron:
            t_hist.Fill(getattr(tree, tauVar), 0)
        elif tree.tIsPromptMuon:
            t_hist.Fill(getattr(tree, tauVar), 1)
        elif tree.tIsTau2Electron:
            t_hist.Fill(getattr(tree, tauVar), 2)
        elif tree.tIsTau2Muon:
            t_hist.Fill(getattr(tree, tauVar), 3)
        elif tree.tIsTauh:
            t_hist.Fill(getattr(tree, tauVar), 4)
        else:
            t_hist.Fill(getattr(tree, tauVar), 5)

    for i in range(len(labels)):
        hist.GetYaxis().SetBinLabel(i+1, labels[i])
        t_hist.GetYaxis().SetBinLabel(i+1, t_labels[i])

    return hist, t_hist#, hist_eIsTau2E, hist_eIsTauh, hist_eIsTau2E_withTrigger, hist_eIsTauh_withTrigger

dir = "triggerStudy"
eID = ''

fileList = {}

# for iMass in [2000]:#[500, 2000, 5000]:#range(500, 5500, 500):
#    fileList["Zprime%s" %iMass] = "/nfs_scratch/zmao/%s/%s/ZPrime_%s_all_SYNC_em_BSM3G.root" %(dir, eID, iMass)
dir = '/user_data/zmao/2016_signalRegionNoPZeta_Aug17/'
dir = '/user_data/zmao/2016_signalRegionNoPZeta_looseAntiLepton/'

# fileList["WJets_HT-0to100"] = "%s/WJets_LO_HT-0to100_all_SYNC_et_noIso.root" %(dir)
# fileList["WJets_HT-100to200"] = "%s/WJets_LO_HT-100to200_all_SYNC_et_noIso.root" %(dir)
# fileList["WJets_HT-200to400"] = "%s/WJets_LO_HT-200to400_all_SYNC_et_noIso.root" %(dir)
# fileList["WJets_HT-400to600"] = "%s/WJets_LO_HT-400to600_all_SYNC_et_noIso.root" %(dir)
# fileList["WJets_HT-600toInf"] = "%s/WJets_LO_HT-600toInf_all_SYNC_et_noIso.root" %(dir)

# fileList["DY-50to200"] = "%s/DY-50to200_all_SYNC_et_noIso.root" %(dir)
# fileList["DY-200to400"] = "%s/DY-200to400_all_SYNC_et_noIso.root" %(dir)
# fileList["DY-400to500"] = "%s/DY-400to500_all_SYNC_et_noIso.root" %(dir)
# fileList["DY-500to700"] = "%s/DY-500to700_all_SYNC_et_noIso.root" %(dir)
# fileList["DY-700to800"] = "%s/DY-700to800_all_SYNC_et_noIso.root" %(dir)
# fileList["DY-800to1000"] = "%s/DY-800to1000_all_SYNC_et_noIso.root" %(dir)
# fileList["DY-1000to1500"] = "%s/DY-1000to1500_all_SYNC_et_noIso.root" %(dir)



# fileList = {"TTJets": "%s/TT_all_SYNC_mt_noIso.root" %(dir)}
fileList = {"DY-50": "%s/DY-50_LO_all_SYNC_et_noIso.root" %(dir)}

for iName in fileList.keys():

    hist = r.TH2D("hist%s" %iName, "", len(bins)-1, bins, 6, 0, 6)
    hist.SetTitle("%s; m_eff [GeV]; " %iName)
    t_hist = r.TH2D("t_hist%s" %iName, "", len(bins)-1, bins, 6, 0, 6)
    t_hist.SetTitle("%s; m_eff [GeV]; " %iName)


    hist, t_hist = loop(fileList[iName], hist, t_hist)

    print 'total: %.2f' %(hist.Integral(0, len(bins)+1, 0, 7))

    psfile = 'eTauOrigin_%s_%s.pdf' %(iName, eID)
    c = r.TCanvas("c","Test", 1000, 500)
#     hist.GetYaxis().SetLabelSize(0.02)
#     hist.Draw("COLZ TEXT0")
#     c.Print('%s(' %psfile)
    c.SetLeftMargin(0.2)
    c.SetRightMargin(0.1)
    c.SetBottomMargin(0.15)

    hist.GetYaxis().SetLabelSize(0.08)
    hist.GetYaxis().SetTitleSize(0.08)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.SetMarkerSize(2)
    hist.Draw("COLZ TEXT0")
    c.Print('%s(' %psfile)
    c.Clear()

    t_hist.GetYaxis().SetLabelSize(0.08)
    t_hist.GetYaxis().SetTitleSize(0.08)
    t_hist.GetXaxis().SetLabelSize(0.05)
    t_hist.GetXaxis().SetTitleSize(0.05)
    t_hist.SetMarkerSize(2)
    t_hist.Draw("COLZ TEXT0")
    c.Print('%s)' %psfile)

#     null = r.TH2F("null","", len(bins)-1, bins, 1, 0, 1.1)
#     null.SetMaximum(1.2)
#     null.SetTitle("eIsTauh/(eIsTau2Ele+eIsTauh); e pt; eIsTauh/(eIsTau2Ele+eIsTauh)")
#     null.SetStats(False)
#     null.Draw()
# 
#     leg = tool.setMyLegend((0.5, 0.8 - 0.06*3, 0.92, 0.8), [(g, 'before trigger selection', 'ep'), (g_withTrigger, 'after trigger selection', 'ep')])
# 
#     g.Draw('same PE')
#     g_withTrigger.Draw('same PE')
#     leg.Draw('same')
#     c.Print('%s)' %psfile)

