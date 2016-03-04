#!/usr/bin/env python

import ROOT as r
import tool
from array import array

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

bins = array('d', range(0, 400, 25))#plotTurnOn.bins
labels = ["eIsPromptElectron", "eIsPromptMuon", "eIsTau2Electron", "eIsTau2Muon", "eIsTauh", "other"]
m_labels = ["mIsPromptElectron", "mIsPromptMuon", "mIsTau2Electron", "mIsTau2Muon", "mIsTauh", "other"]
t_labels = ["tIsPromptElectron", "tIsPromptMuon", "tIsTau2Electron", "tIsTau2Muon", "tIsTauh", "other"]

def loop(iSample, hist, t_hist):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    counter = 0
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        if abs(tree.eEta) >= 2.1:
            continue
        if abs(tree.ePt) < 35:
            continue
#         if abs(tree.mEta) >= 2.1:
#             continue
        if not ((tree.tByTightCombinedIsolationDeltaBetaCorr3Hits > 0.5) and (tree.eRelIso < 0.15)):
            continue
        if tree.q_1 == tree.q_2:
            continue
        #electron
        if tree.eIsPromptElectron:
            hist.Fill(tree.ePt, 0)
        elif tree.eIsPromptMuon:
            hist.Fill(tree.ePt, 1)
        elif tree.eIsTau2Electron:
            hist.Fill(tree.ePt, 2)               
        elif tree.eIsTau2Muon:
            hist.Fill(tree.ePt, 3)
        elif tree.eIsTauh:
            hist.Fill(tree.ePt, 4)
        else:
            hist.Fill(tree.ePt, 5)
        if counter < 10:
            print ''
            print 'lumi: %i, event: %i' %(tree.lumi, tree.evt)
            print "ePt: %.3f, eEta: %.3f, ePhi: %.3f" %(tree.ePt, tree.eEta, tree.ePhi)
            print "tPt: %.3f, tEta: %.3f, tPhi: %.3f" %(tree.tPt, tree.tEta, tree.tPhi)
            print "********************************"
            counter += 1
#         muon
#         if tree.mIsPromptElectron:
#             m_hist.Fill(tree.mPt, 0)
#         elif tree.mIsPromptMuon:
#             m_hist.Fill(tree.mPt, 1)
#         elif tree.mIsTau2Electron:
#             m_hist.Fill(tree.mPt, 2)
#         elif tree.mIsTau2Muon:
#             m_hist.Fill(tree.mPt, 3)
#         elif tree.mIsTauh:
#             m_hist.Fill(tree.mPt, 4)
#         else:
#             m_hist.Fill(tree.mPt, 5)

        #tau
        if tree.tIsPromptElectron:
            t_hist.Fill(tree.tPt, 0)
        elif tree.tIsPromptMuon:
            t_hist.Fill(tree.tPt, 1)
        elif tree.tIsTau2Electron:
            t_hist.Fill(tree.tPt, 2)
        elif tree.tIsTau2Muon:
            t_hist.Fill(tree.tPt, 3)
        elif tree.tIsTauh:
            t_hist.Fill(tree.tPt, 4)
        else:
            t_hist.Fill(tree.tPt, 5)

    for i in range(len(labels)):
        hist.GetYaxis().SetBinLabel(i+1, labels[i])
        t_hist.GetYaxis().SetBinLabel(i+1, t_labels[i])

    return hist, t_hist#, hist_eIsTau2E, hist_eIsTauh, hist_eIsTau2E_withTrigger, hist_eIsTauh_withTrigger

dir = "triggerStudy"
eID = 'OS'

fileList = {}

# for iMass in [2000]:#[500, 2000, 5000]:#range(500, 5500, 500):
#    fileList["Zprime%s" %iMass] = "/nfs_scratch/zmao/%s/%s/ZPrime_%s_all_SYNC_em_BSM3G.root" %(dir, eID, iMass)
dir = '/user_data/zmao/Nov18Prodruction_ntuple_noIso/MVANonTrigWP80/'
# fileList["WJets_HT-0to100"] = "%s/WJets_LO_HT-0to100_all_SYNC_et_noIso.root" %(dir)
# fileList["WJets_HT-100to200"] = "%s/WJets_LO_HT-100to200_all_SYNC_et_noIso.root" %(dir)
# fileList["WJets_HT-200to400"] = "%s/WJets_LO_HT-200to400_all_SYNC_et_noIso.root" %(dir)
# fileList["WJets_HT-400to600"] = "%s/WJets_LO_HT-400to600_all_SYNC_et_noIso.root" %(dir)
fileList["WJets_HT-600toInf"] = "%s/WJets_LO_HT-600toInf_all_SYNC_et_noIso.root" %(dir)


# fileList = {"TTJets": "/nfs_scratch/zmao/%s/%s/TTJets_all_SYNC_em_BSM3G.root" %(dir, eID)}

for iName in fileList.keys():

    hist = r.TH2D("hist%s" %iName, "", len(bins)-1, bins, 6, 0, 6)
    hist.SetTitle("%s; e pt; " %iName)
    t_hist = r.TH2D("t_hist%s" %iName, "", len(bins)-1, bins, 6, 0, 6)
    t_hist.SetTitle("%s; t pt; " %iName)


    hist, t_hist = loop(fileList[iName], hist, t_hist)

    print 'total: %.2f' %(hist.Integral(0, len(bins)+1, 0, 7))

    psfile = 'eTauOrigin_%s_%s.pdf' %(iName, eID)
    c = r.TCanvas("c","Test", 1000, 800)
    hist.GetYaxis().SetLabelSize(0.02)
    hist.Draw("COLZ TEXT0")
    c.Print('%s(' %psfile)
    t_hist.GetYaxis().SetLabelSize(0.02)
    t_hist.Draw("COLZ TEXT0")
    c.Print('%s)' %psfile)
    c.Clear()

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

