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

def getEffCurve(num, denom):
    g = r.TGraphAsymmErrors()
    g.BayesDivide(num, denom)
    return g

def loop_one_sample(iSample, hist):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    initEvents = file.Get('eventCount').GetBinContent(1)
    nEntries = tree.GetEntries()
    hist.Sumw2()
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)

        if tree.eGenPt < 0:
            continue
        if tree.q_1 == tree.q_2:
            continue
        hist.Fill(tree.ePt)
    print ''
    return initEvents

def run(cat = 'et', sampleMass = '5000'):

    append_name = ''
    files = [("denom2",r.kWhite, "/nfs_scratch/zmao/denom2//ZPrime_%s_all_SYNC_%s_inclusive.root" %(sampleMass, cat)),
             ("CBIDLoose", r.kGreen, "/nfs_scratch/zmao/CutBasedLoose//ZPrime_%s_all_SYNC_%s_inclusive.root" %(sampleMass, cat)),
             ("WP80", r.kRed, "/nfs_scratch/zmao/WP80//ZPrime_%s_all_SYNC_%s_inclusive.root" %(sampleMass, cat)),
             ("HEEP", r.kBlue, "/nfs_scratch/zmao/HEEP//ZPrime_%s_all_SYNC_%s_inclusive.root" %(sampleMass, cat)),
             ("CBIDMedium", r.kMagenta, "/nfs_scratch/zmao/CutBasedMedium//ZPrime_%s_all_SYNC_%s_inclusive.root" %(sampleMass, cat)),
             ("CBIDTight", r.kCyan, "/nfs_scratch/zmao/CutBasedTight//ZPrime_%s_all_SYNC_%s_inclusive.root" %(sampleMass, cat)),
            ]
    hists = []
    if sampleMass == '500':
        bins = array.array('d', range(0, 110, 10) + range(100, 425, 25))
    elif sampleMass == '2000':
        bins = array.array('d', range(0, 110, 10) + range(100, 425, 25) + range(400, 1200, 100))
    else:
        bins = array.array('d', range(0, 425, 25) + range(400, 2100, 100))

    bins2 = array.array('d', range(0, 2100, 100))
    for i in range(len(files)):
        hists.append(r.TH1D('hist_%s' %files[i][0], '', len(bins)-1, bins))
        hists[i].SetMarkerColor(files[i][1])
        hists[i].SetMarkerStyle(8)
        hists[i].SetMarkerSize(0.9)
        hists[i].SetLineColor(files[i][1])
        initEvents = loop_one_sample(files[i][2], hists[i])

    psfile = 'eleID_comapre_ZPrime%s_%s.pdf' %(sampleMass, cat) 
    c = r.TCanvas("c","Test", 800, 600)
    r.gPad.SetTicky()
    r.gPad.SetTickx()
#     r.gPad.SetLogx()

    graphs = []
    histList = []
    histList.append((hists[0], "denominator/initEvents = %.4f" %((hists[0].Integral(0, len(bins)+1)+0.0)/(initEvents + 0.0)), 'ep'))

    null = r.TH2F("null","", len(bins)-1, bins, 1, 0, 1.0)
    null.SetTitle("ZPrime %s; e pt;  eff" %sampleMass)

    null.Draw()
    for i in range(1, len(files)):
        graphs.append(getEffCurve(num = hists[i], denom = hists[0]))
        graphs[i-1].SetMarkerStyle(8)
        graphs[i-1].SetMarkerSize(0.9)
        graphs[i-1].SetMarkerColor(files[i][1])
        graphs[i-1].SetLineColor(files[i][1])
        if files[0][0] == 'denom':
            histList.append((hists[i], files[i][0] + " + trigger + iso", 'ep'))
        else:
            histList.append((hists[i], files[i][0] + " + iso", 'ep'))

        graphs[i-1].Draw("same pe")


    leg = tool.setMyLegend((0.2, 0.5 - 0.07*(len(files)-1), 0.5, 0.5), histList)
    leg.Draw("same")

    c.Print('%s' %psfile)
    c.Close()

run('et', '500')
run('et', '2000')
run('et', '5000')
