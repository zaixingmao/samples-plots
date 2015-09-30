#!/usr/bin/env python

import ROOT as r
import plots_cfg
import tool
import optparse
import array
import math
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def ratioHistogram( num, den, relErrMax=0.25) :
    def groupR(group) :
        N,D = [float(sum(hist.GetBinContent(i) for i in group)) for hist in [num,den]]
        return N/D if D else 0

    def groupErr(group) :
        N,D = [float(sum(hist.GetBinContent(i) for i in group)) for hist in [num,den]]
        ne2,de2 = [sum(hist.GetBinError(i)**2 for i in group) for hist in [num,den]]
        return math.sqrt( ne2/N**2 + de2/D**2 ) * N/D if N and D else 0

    def regroup(groups) :
        err,iG = max( (groupErr(g),groups.index(g)) for g in groups )
        if err < relErrMax or len(groups)<3 : return groups
        iH = max( [iG-1,iG+1], key = lambda i: groupErr(groups[i]) if 0<=i<len(groups) else -1 )
        iLo,iHi = sorted([iG,iH])
        return regroup(groups[:iLo] + [groups[iLo]+groups[iHi]] + groups[iHi+1:])

    try :
        groups = regroup( [(i,) for i in range(1,1+num.GetNbinsX())] )
    except :
        print 'Ratio failed:', num.GetName()
        groups = [(i,) for i in range(1,1+num.GetNbinsX()) ]
    ratio = r.TH1D("ratio"+num.GetName()+den.GetName(),"",len(groups), array.array('d', [num.GetBinLowEdge(min(g)) for g in groups ] + [num.GetXaxis().GetBinUpEdge(num.GetNbinsX())]) )
    for i,g in enumerate(groups) :
        ratio.SetBinContent(i+1,groupR(g))
        ratio.SetBinError(i+1,groupErr(g))
    return ratio



def loop_one_sample(iSample, hist, hist_match_gen0, hist_match_gen1, hist_no_match_gen0, hist_no_match_gen1, hist_pt_vs_eta, eleID):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    hist.Sumw2()
    if nEntries > 100000:
        nEntries = 100000
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        if tree.eGenPt > 0:
            hist_match_gen0.Fill(tree.ePt)
        else:
            hist_no_match_gen0.Fill(tree.ePt)

        if 'HEEP' in eleID and (not tree.eHEEPIDD):
            continue
        if 'WP80' in eleID and (not tree.eMVANonTrigWP80):
            continue
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        hist.Fill(tree.eGenPt, tree.eGenPt/tree.ePt)
        hist_pt_vs_eta.Fill(tree.ePt, abs(tree.eEta))
        if tree.eGenPt > 0:
            hist_match_gen1.Fill(tree.ePt)
        else:
            hist_no_match_gen1.Fill(tree.ePt)

    print ''

def run(eleIDs, cat = 'et', sampleMass = '5000'):

    append_name = ''
    files_mc = [#("SUSY", '/nfs_scratch/zmao/13TeV_samples_25ns_newSplitting_noChargeMatch/SYNC_SUSY_HToTauTau_M-160_%s_%s.root' %(cat, append_name), r.kRed)
#                 ('WJets', '/nfs_scratch/zmao/13TeV_samples_25ns_noElectronIDCut/WJets_all_SYNC_%s_%s.root' %(cat, append_name), r.kRed),
#                 ('/nfs_scratch/zmao/noEleIDCut/SUSY_all_SYNC_%s_inclusive.root' %cat),
                ('/nfs_scratch/zmao/noEleIDCut/ZPrime_%s_all_SYNC_%s_inclusive.root' %(sampleMass, cat)),
#                 ('ttbar', '/nfs_scratch/zmao/13TeV_samples_25ns_noElectronIDCut/TTJets_all_SYNC_%s_%s.root' %(cat, append_name), r.kGreen)
                ]

    hists = []
    hists_gen_match0 = []
    hists_gen_match = []
    hists_no_gen_match0 = []
    hists_no_gen_match = []
    hists_pt_vs_eta = []

    bins = array.array('d', range(0, 110, 10) + range(100, 425, 25) + range(400, 2100, 100))
    bins2 = array.array('d', range(0, 2100, 100))

    for iEleID in eleIDs:
#         hists.append(r.TH2D('hist_%s' %iEleID, '', len(bins)-1, bins, 20, 0, 2))
        hists.append(r.TProfile('hist_%s' %iEleID, '', len(bins)-1, bins, 's'))
        hists_gen_match.append(r.TH1D('hist_gen_match_%s' %iEleID,'',  len(bins2)-1, bins2))
        hists_no_gen_match.append(r.TH1D('hist_no_gen_match_%s' %iEleID,'',  len(bins2)-1, bins2))
        hists_gen_match0.append(r.TH1D('hist_gen_match0_%s' %iEleID,'',  len(bins2)-1, bins2))
        hists_no_gen_match0.append(r.TH1D('hist_no_gen_match0_%s' %iEleID,'',  len(bins2)-1, bins2))
        hists_pt_vs_eta.append(r.TProfile('hist_pt_vs_eta_%s' %iEleID,'',  50, 0, 50, 's'))


    for iSample in files_mc:
        counter = 0
        for iEleID in eleIDs:
            loop_one_sample(iSample, hists[counter], hists_gen_match0[counter], hists_gen_match[counter], hists_no_gen_match0[counter], hists_no_gen_match[counter], hists_pt_vs_eta[counter], iEleID)
            counter += 1

    psfile = 'eleID_ZPrime%s.pdf' %sampleMass 
    c = r.TCanvas("c","Test", 800, 600)
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    hists[0].SetTitle("ZPrime %s; gen e pt;  reco e pt/gen e pt" %sampleMass)
    hists[0].Draw()
    hists[1].SetLineColor(r.kRed)
    hists[1].Draw('same')
    hists[1].SetLineStyle(2)

    leg = tool.setMyLegend((0.65, 0.6 - 0.06*2, 0.92, 0.6), [(hists[0], eleIDs[0], "L"), (hists[1], eleIDs[1], "L")])
    leg.Draw("same")

    c.Print('%s(' %psfile)
    c.Clear()
    hists_pt_vs_eta[0].SetTitle("%s; reco e pt; reco e eta" %eleIDs[0])
    hists_pt_vs_eta[0].Draw("COLZ")
    c.Print('%s' %psfile)
    c.Clear()
    hists_pt_vs_eta[1].SetTitle("%s; reco e pt; reco e eta" %eleIDs[1])
    hists_pt_vs_eta[1].Draw("COLZ")
    c.Print('%s' %psfile)
    c.Clear()

    delta_genMatch_HEEP = ratioHistogram(num = hists_gen_match[0], den = hists_gen_match0[0], relErrMax=0.25)
    delta_genMatch_WP80 = ratioHistogram(num = hists_gen_match[1], den = hists_gen_match0[1], relErrMax=0.25)
    delta_genMatch_WP80.SetLineColor(r.kRed)
    delta_genMatch_WP80.SetLineStyle(2)
    delta_genMatch_HEEP.SetTitle("ZPrime %s gen-matched; electron ID effeciency;  reco e pt" %sampleMass)

    delta_genMatch_HEEP.Draw()
    delta_genMatch_WP80.Draw("same")
    leg.Draw("same")

    c.Print('%s' %psfile)
    c.Clear()
    delta_no_genMatch_HEEP = ratioHistogram(num = hists_no_gen_match[0], den = hists_no_gen_match0[0], relErrMax=0.25)
    delta_no_genMatch_WP80 = ratioHistogram(num = hists_no_gen_match[1], den = hists_no_gen_match0[1], relErrMax=0.25)
    delta_no_genMatch_WP80.SetLineColor(r.kRed)
    delta_no_genMatch_WP80.SetLineStyle(2)
    delta_no_genMatch_HEEP.SetTitle("ZPrime %s no gen-matched; electron ID effeciency;  reco e pt" %sampleMass)
    delta_no_genMatch_HEEP.Draw()
    delta_no_genMatch_WP80.Draw("same")
    leg.Draw("same")

    c.Print('%s)' %psfile)

#     for i in range(len(eleIDs)):
#         hists[i].SetTitle("%s; gen e pt;  reco e pt/gen e pt" %eleIDs[i])
#         type = ''
#         if i != 0:
#             type = "same"
#             hists[i].SetLineColor(r.kRed)
#         hists[i].Draw(type)
#         if i == 0 and len(eleIDs) != 1:
#             c.Print('%s(' %psfile)
#         elif i == len(eleIDs) - 1 and len(eleIDs) != 1:
#             c.Print('%s)' %psfile)
#         else:
#             c.Print('%s' %psfile)
    c.Close()

run(["HEEP", "WP80"], 'et', '500')
run(["HEEP", "WP80"], 'et', '2000')
run(["HEEP", "WP80"], 'et', '5000')
