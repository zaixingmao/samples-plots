#!/usr/bin/env python

import ROOT as r
from array import array

r.gSystem.Load("libFWCoreFWLite.so")
r.AutoLibraryLoader.enable()

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

def setBins(binsCenters):
    binsCenters.sort()
    bins = []
    bins.append(0.0)

    for i in range(len(binsCenters)):
        if i != len(binsCenters) - 1:
            bins.append((binsCenters[i] + binsCenters[i+1])/2.0)
        else:
            bins.append(binsCenters[i] + 5.0)
    return bins

def findL1Match(tree, pt, eta, phi):
    tau = lvClass()
    tmpl1 = lvClass()
    tau.SetCoordinates(pt, eta, phi, 0)
    matched = lvClass()

    nTaus = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).size()
    dR = 99999.9
    if nTaus == 0:
        return -1, -1
    else:
        for i in range(nTaus):
            tmpl1.SetCoordinates((tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(i).pt(), 
                                 (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(i).eta(),
                                 (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(i).phi(), 0)
            tmp_dR = r.Math.VectorUtil.DeltaR(tmpl1, tau)
            if tmp_dR < dR:
                dR = tmp_dR
                matchedPt = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(i).pt()
                matchedEta = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(i).eta()
                matchedPhi = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(i).phi()
        return dR, matchedPt


def plot(file):
    f = r.TFile(file)
    tree = f.Get("Events")
    nEntries = tree.GetEntries()

    binsCenters = []

    for i in range(500):
        tree.GetEntry(i)

        #loop over pat taus in an event
        nTaus = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).size()
        for j in range(nTaus):
            l1_pt = (tree.l1extraL1JetParticles_l1extraParticles_Tau_RECO).at(j).pt()
            if l1_pt not in binsCenters:
                binsCenters.append(l1_pt)

    binsCenters.sort()
    bins = setBins(binsCenters)
    bins_array = array('d', bins)
    patvsl1Pt_1 =  r.TH2F('patvsl1Pt_1', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)
    patvsl1Pt_2 =  r.TH2F('patvsl1Pt_2', "", len(bins_array)-1, bins_array,len(bins_array)-1, bins_array)

    l1Pt =  r.TH1F('l1Pt', "", len(bins_array)-1, bins_array)
    dR_hist =  r.TH1F('dR_hist', "", 1000, 0, 5)
    
    for i in range(nEntries):
        tree.GetEntry(i)
        #loop over pat taus in an event
        nTaus = (tree.patTaus_slimmedTaus__PAT).size()
        for j in range(nTaus):
            dR, matchedPt = findL1Match(tree = tree,
                                        pt = (tree.patTaus_slimmedTaus__PAT).at(j).pt(),
                                        eta = (tree.patTaus_slimmedTaus__PAT).at(j).eta(),
                                        phi = (tree.patTaus_slimmedTaus__PAT).at(j).phi())
            dR_hist.Fill(dR)
            if dR < 0.5 and dR != -1:
                if j == 0:
                    patvsl1Pt_1.Fill((tree.patTaus_slimmedTaus__PAT).at(j).pt(), matchedPt)
                if j == 1:
                    patvsl1Pt_2.Fill((tree.patTaus_slimmedTaus__PAT).at(j).pt(), matchedPt)


    psfile = 'test.pdf'
    c = r.TCanvas("c","Test", 600, 600)
#     l1Pt.SetLineColor(r.kRed)

    l = r.TLine(0,0,250,250)
    l.SetLineColor(r.kRed)
    patvsl1Pt_1.Draw('COLZ')
    patvsl1Pt_1.SetTitle('; Leading PAT #tau Pt; L1 #tau Pt')
    patvsl1Pt_1.GetYaxis().SetTitleOffset(1.2)
    l.Draw('same')
#     patPt.Draw('same')
    c.Print('%s(' %psfile)
    c.Clear()
    patvsl1Pt_2.Draw('COLZ')
    patvsl1Pt_2.SetTitle('; Sub-leading PAT #tau Pt; L1 #tau Pt')
    patvsl1Pt_2.GetYaxis().SetTitleOffset(1.2)
    l.Draw('same')
    c.Print('%s' %psfile)
    c.Clear()
    dR_hist.Draw()
    l2 = r.TLine(0.5,0,0.5,300)
    l2.SetLineColor(r.kRed)
    dR_hist.SetTitle('; dR;')
    l2.Draw('same')
    c.Print('%s)' %psfile)    

plot("/home/zmao/3E56199D-1D70-E411-B425-7845C4FC36CB.root")