#!/usr/bin/env python

import os
import ROOT as r
from kinfit import setup, fit


def loopMulti(fileNames=[], nEventsMax=None):
    out = {"chi2": [],
           "m_fit": [],
           "m_no_fit": [],
           "m_vs_m": [],
           }

    for fileName, leg in fileNames:
        chi2, m, mNo, mm = loop(fileName, nEventsMax, suffix="_%s" % leg)
        out["chi2"].append(chi2)
        out["m_fit"].append(m)
        out["m_no_fit"].append(mNo)
        out["m_vs_m"].append(mm)
    return out


def loop(fileName="", nEventsMax=None, suffix=""):
    h_chi2 = r.TH1D("h_chi2%s" % suffix, ";chi2;events / bin", 120, -10.0, 390.0)
    #bins = [120, -10.0, 590.0]
    bins = [60, -10.0, 590.0]
    h_m = r.TH1D("h_m%s" % suffix, ";m_{fit} (GeV);events / bin", *bins)
    h_fMass = r.TH1D("h_fMass%s" % suffix, ";m_{no fit} (GeV);events / bin", *bins)

    bins2 = bins + bins
    h_m_vs_m = r.TH2D("h_m_vs_m%s" % suffix, ";m_{fit} (GeV);m_{no fit};events / bin", *bins2)

    f = r.TFile(fileName)
    tree = f.Get("eventTree")
    
    nEvents = tree.GetEntries()
    if nEventsMax is not None:
        nEvents = min([nEvents, nEventsMax])

    for iEvent in range(nEvents):
        tree.GetEntry(iEvent)
        
        if tree.charge1.at(0) == tree.charge2.at(0):
            continue

        if 1.5 < tree.iso1.at(0):
            continue
            
        if 1.5 < tree.iso2.at(0):
            continue
            
        if tree.CSVJ1 < 0.679:
            continue
            
        if tree.CSVJ2 < 0.244:
            continue

        j1 = lvClass()
        j2 = lvClass()

        j1.SetCoordinates(tree.CSVJ1Pt, tree.CSVJ1Eta, tree.CSVJ1Phi, tree.CSVJ1Mass)
        j2.SetCoordinates(tree.CSVJ2Pt, tree.CSVJ2Eta, tree.CSVJ2Phi, tree.CSVJ2Mass)

        chi2, mh = fit(tree, j1, j2)
        h_chi2.Fill(chi2)
        h_m.Fill(mh)
        h_fMass.Fill(tree.fMass)
        h_m_vs_m.Fill(mh, tree.fMass)

    f.Close()
    return [h_chi2, h_m, h_fMass, h_m_vs_m]


def pdf(fileName="", histos={}):
    can = r.TCanvas("can", "", 2)
    
    can.Print(fileName+"[")

    leg = r.TLegend(0.65, 0.65, 0.85, 0.85)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    fillLeg = True

    for key, lst in sorted(histos.iteritems()):
        color = 1
        for i, h in enumerate(lst):
            th1 = h.ClassName().startswith("TH1")
            if th1:
                integral = h.Integral(0, 1 + h.GetNbinsX())
                if integral:
                    h.Scale(1.0 / integral)
                    h.GetYaxis().SetTitle("fraction of events / bin")
                    h.GetYaxis().SetTitleOffset(1.3)
                else:
                    continue

            if fillLeg:
                name = h.GetName().split("_")[-1]
                #text = "%s (%d)" % (name, integral)
                text = name
                leg.AddEntry(h, text, "le")
            h.SetStats(False)
            h.SetLineColor(color)
            h.SetMarkerColor(color)

            color += 1
            if color == 5:
                color += 1

            gopts = "ehist" if th1 else ""
            if i:
                h.Draw("%ssame" % gopts)
            else:
                h.Draw(gopts)

        r.gPad.SetTickx()
        r.gPad.SetTicky()
        leg.Draw()
        fillLeg = False
        can.Print(fileName)
    can.Print(fileName+"]")


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    #r.gStyle.SetOptStat("e")
    r.TH1.SetDefaultSumw2(True)

    setup()
    lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
    histos = loopMulti(fileNames=[("v2/H2hh260_all.root",     "H260"),
                                  ("v2/H2hh300_all.root",     "H300"),
                                  ("v2/H2hh350_all.root",     "H350"),
                                  #("v2/tt_eff_all.root",      "tt-dilep"),
                                  #("v2/tt_semi_eff_all.root", "tt-semilep"),
                                  #("v2/ZZ_eff_all.root",      "ZZ"),
                                  ],
                       #nEventsMax=200,
                       )
    pdf(fileName="kinfit_v1.0.pdf", histos=histos)
