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


def buildDelta(data_pass, data_all, bkg_pass, bkg_all, bins, varName, unit, relErrMax):
    dataHist = r.TH1F("dataHist_%s" %varName, "", len(bins)-1, bins)
    dataHist.Add(data_pass)
    dataHist.Divide(data_all)
    bkgHist = r.TH1F("bkgHist_%s" %varName, "", len(bins)-1, bins)
    bkgHist.Add(bkg_pass)
    bkgHist.Divide(bkg_all)

    delta = ratioHistogram(num = dataHist, den = bkgHist, relErrMax=relErrMax)
    delta.SetTitle('; %s %s; data/MC' %(varName, unit))
    delta.SetMaximum(1.5)
    delta.SetMinimum(0.5)
    delta.GetXaxis().SetLabelSize(0.1)
    delta.GetXaxis().SetTitleSize(0.1)
    delta.GetYaxis().SetLabelSize(0.1)
    delta.GetYaxis().SetNdivisions(5,5,0)
    delta.GetYaxis().SetTitleSize(0.1)
    delta.GetYaxis().SetTitleOffset(0.43)
    delta.GetYaxis().CenterTitle()
    return delta

def loop_one_sample(iSample, varName, hist1, hist2, category = 'mt', isData = False):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    hist1.Sumw2()
    hist2.Sumw2()
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)

        if category == 'mt':
            if tree.mPt <= 25:
                continue
            if not (tree.singleMu24Pass and tree.mIsoMu24):
                continue
        elif category == 'et':
            if tree.ePt <= 33:
                continue
            if isData:
                if not (tree.singleETightPass and tree.eSingleEleTight):
                    continue
            else:
                if not (tree.singleEPass and tree.eSingleEle):
                    continue


        if tree.q_1 == tree.q_2:
            continue
        hist1.Fill(getattr(tree, varName))
        if category == 'mt':
            if tree.muTauPass and tree.mMuTau and tree.mMuTauOverlap and tree.tTau20AgainstMuon and tree.tTauOverlapMu:
                hist2.Fill(getattr(tree, varName))
        elif category == 'et':
            if isData:
                if tree.eTau_WPLoosePass and tree.eEle22Loose and tree.eOverlapEle22Loose and tree.tTau20 and tree.tTauOverlapEleLoose:
                    hist2.Fill(getattr(tree, varName))
            else:
                if tree.eTauPass and tree.eEle22 and tree.eOverlapEle22 and tree.tTau20 and tree.tTauOverlapEle:
                    hist2.Fill(getattr(tree, varName))
    print ''

def run(varName, bins, unit, cat = 'et'):

    append_name = 'inclusive'
    files_mc = [('WJets', '/nfs_scratch/zmao/13TeV_samples_25ns_noElectronIDCut/WJets_all_SYNC_%s_%s.root' %(cat, append_name), r.kRed),
                ('DY', '/nfs_scratch/zmao/13TeV_samples_25ns_noElectronIDCut/DY_all_SYNC_%s_%s.root' %(cat, append_name), r.kBlue),
#                 ('ttbar', '/nfs_scratch/zmao/13TeV_samples_25ns_Spring15_eletronID2/TTJets_all_SYNC_%s_%s.root' %(cat, append_name), r.kGreen)
                ]

    hist_mc_all = []
    hist_mc_pass = []
    file_data = '/nfs_scratch/zmao/13TeV_samples_25ns_noElectronIDCut/data_all_SYNC_%s_%s.root' %(cat, append_name)
    hist_data_all = r.TH1F('hist_data_all', '', len(bins)-1, bins)
    hist_data_pass = r.TH1F('hist_data_pass', '', len(bins)-1, bins)

    for iName, iSample, iColor in files_mc:
        hist_mc_all.append(r.TH1F("hist_%s_all" %iName, "", len(bins)-1, bins))
        hist_mc_pass.append(r.TH1F("hist_%s_pass" %iName, "", len(bins)-1, bins))
        loop_one_sample(iSample, varName, hist_mc_all[len(hist_mc_all)-1], hist_mc_pass[len(hist_mc_pass)-1], cat, False)

    loop_one_sample(file_data, varName, hist_data_all, hist_data_pass, cat, True)


    g_mc = []
    histList = []

    for i in range(len(hist_mc_all)):
        g_mc.append(r.TGraphAsymmErrors())
        g_mc[i].BayesDivide(hist_mc_pass[i], hist_mc_all[i])
        g_mc[i].SetMarkerStyle(8)
        g_mc[i].SetMarkerSize(0.9)
        g_mc[i].SetMarkerColor(files_mc[i][2])
        g_mc[i].SetLineColor(files_mc[i][2])
        histList.append((g_mc[i], files_mc[i][0], 'ep'))
    g_data = r.TGraphAsymmErrors()
    g_data.BayesDivide(hist_data_pass, hist_data_all)
    histList.append((g_data, 'Observed', 'ep'))

    g_data.SetMarkerStyle(8)
    g_data.SetMarkerSize(0.9)
    g_data.SetMarkerColor(r.kBlack)
    psfile = 'tauTrigTurnOnCurve_%s_%s.pdf' %(varName, cat)
    c = r.TCanvas("c","Test", 600, 800)


    null = r.TH2F("null","", len(bins)-1, bins, 1, 0, 1.1)
    null.SetMaximum(1.2)
    null.SetTitle("tau trigger turn-on curve; %s; Effeciency" %unit)
    null.SetStats(False)


    leg = tool.setMyLegend((0.65, 0.4 - 0.06*4, 0.92, 0.4), histList)

    delta = buildDelta(hist_data_pass, hist_data_all, hist_mc_pass[0], hist_mc_all[0], bins, varName, unit, 0.25)

    p = r.TPad("p", "p", 0., 1, 1., 0.3)
    p_ratio = r.TPad("p_r", "p_r", 0.,0.3,1.,0.06)
    p.SetMargin(1, 1, 0, 0.1)
    p_ratio.SetMargin(1, 1, 0.2, 0)
    p.Draw()
    p_ratio.Draw()
    p.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    null.Draw()
    for i in range(len(g_mc)):
        g_mc[i].Draw('same PE')
    g_data.Draw('same PE')
    leg.Draw('same')

    p_ratio.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    p_ratio.SetGridy(1)
    delta.Draw()

    c.Print('%s' %psfile)
    c.Close()


bins = array.array('d', range(0, 45, 5) + range(40, 70, 10)+[60,100,200])
bins2 = []
for i in range(21):
    bins2.append(-4 + i*0.4)
run('tPt', bins, "#tau pt")
# run('tEta',  array.array('d', bins2), "#tau eta")
