#!/usr/bin/env python

from collections import defaultdict
import os
import ROOT as r
from kinfit import setup, fit


def combineBinContentAndError(h, binToContainCombo, binToBeKilled):
    c = h.GetBinContent(binToContainCombo) + h.GetBinContent(binToBeKilled)
    e = h.GetBinError(binToContainCombo)**2 + h.GetBinError(binToBeKilled)**2
    e = e**0.5

    h.SetBinContent(binToBeKilled, 0.0)
    h.SetBinContent(binToContainCombo, c)

    h.SetBinError(binToBeKilled, 0.0)
    h.SetBinError(binToContainCombo, e)


def shift(h):
    n = h.GetNbinsX()
    combineBinContentAndError(h, n, n+1)  # overflows
    combineBinContentAndError(h, 1, 0)  # underflows


def loopMulti(fileNames=[], nEventsMax=None):
    out = defaultdict(list)

    for fileName, leg in fileNames:
        histos = loop(fileName, nEventsMax, suffix="_%s" % leg)
        for key, h in histos.iteritems():
            out[key].append(h)
    return out


def select(tree):
    if tree.charge1.at(0) == tree.charge2.at(0):
        return

    if 1.5 < tree.iso1.at(0):
        return

    if 1.5 < tree.iso2.at(0):
        return

    if tree.CSVJ1 < 0.679:
        return

    if tree.CSVJ2 < 0.244:
        return

    #if not (90.0 < tree.svMass.at(0) < 150.0):
    #    continue
    #if not (90.0 < tree.mJJ < 150.0):
    #    continue

    return True


def loop(fileName="", nEventsMax=None, suffix=""):
    #mbins = [120, -10.0, 590.0]
    mbins = [60, -10.0, 590.0]

    out = {}
    for var, title, bins in [("chi2", ";#chi^{2};events / bin", (40, -10.0, 190.0)),
                             #("chi2", ";chi2;events / bin", (240, -100.0, 1100.0)),
                             ("m", ";m_{fit} (GeV);events / bin", mbins),
                             ("fMass", ";m_{no fit} (GeV);events / bin", mbins),
                             ("svMass", ";svMass (GeV);events / bin", (40, 0.0, 200.0)),
                             ("mbb", ";m_{bb} (GeV);events / bin", (40, 0.0, 200.0)),
                             ("dRTauTau", ";#DeltaR_{#tau#tau};events / bin", (30, 0.0, 6.0)),
                             ("dRJJ", ";#DeltaR_{bb};events / bin", (30, 0.0, 6.0)),
                             ("status", ";status;events / bin", (10, -0.5, 9.5)),
                             ]:
        out[var] = r.TH1D("%s_%s" % (var, suffix), title, *bins)
        rateTitle = title.replace("events / bin", "fraction of events with  \chi^{2} < %d" % chi2Fail)
        out[var+"_rate"] = r.TEfficiency("%s_rate_%s" % (var, suffix), rateTitle, *bins)


    #out["m_vs_m"] = r.TH2D("h_m_vs_m%s" % suffix, ";m_{fit} (GeV);m_{no fit};events / bin", *(mbins+mbins))
    #out["m_vs_m_rate"] = r.TEfficiency("h_m_vs_m_rate_%s" % suffix, ";m_{fit} (GeV);m_{no fit};events / bin", *(mbins+mbins))

    f = r.TFile(fileName)
    tree = f.Get("eventTree")
    
    nEvents = tree.GetEntries()
    if nEventsMax is not None:
        nEvents = min([nEvents, nEventsMax])

    for iEvent in range(nEvents):
        tree.GetEntry(iEvent)

        if not select(tree):
            continue

        j1 = lvClass()
        j2 = lvClass()

        j1.SetCoordinates(tree.CSVJ1Pt, tree.CSVJ1Eta, tree.CSVJ1Phi, tree.CSVJ1Mass)
        j2.SetCoordinates(tree.CSVJ2Pt, tree.CSVJ2Eta, tree.CSVJ2Phi, tree.CSVJ2Mass)

        chi2, mh, status = fit(tree, j1, j2)

        out["chi2"].Fill(chi2)
        out["m"].Fill(mh)
        out["status"].Fill(status)

        out["fMass"].Fill(tree.fMass)
        #out["m_vs_m"].Fill(mh, tree.fMass)
        out["svMass"].Fill(tree.svMass.at(0))
        out["mbb"].Fill(tree.mJJ)
        out["dRTauTau"].Fill(tree.dRTauTau)
        out["dRJJ"].Fill(tree.dRJJ)

        passed = chi2 < chi2Fail
        out["chi2_rate"].Fill(passed, chi2)
        out["m_rate"].Fill(passed, mh)
        out["status_rate"].Fill(passed, status)
        out["fMass_rate"].Fill(passed, tree.fMass)
        #out["m_vs_m_rate"].Fill(passed, mh, tree.fMass)
        out["svMass_rate"].Fill(passed, tree.svMass.at(0))
        out["mbb_rate"].Fill(passed, tree.mJJ)
        out["dRTauTau_rate"].Fill(passed, tree.dRTauTau)
        out["dRJJ_rate"].Fill(passed, tree.dRJJ)

    f.Close()
    return out


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
            if h.ClassName().startswith("TH2"):
                continue

            th1 = h.ClassName().startswith("TH1")
            if th1:
                integral = h.Integral(0, 1 + h.GetNbinsX())
                if integral:
                    h.Scale(1.0 / integral)
                    h.GetYaxis().SetTitle("fraction of events / bin")
                    h.GetYaxis().SetTitleOffset(1.3)
                    shift(h)
                else:
                    continue

            if fillLeg:
                name = h.GetName().split("_")[-1]
                #text = "%s (%d)" % (name, integral)
                text = name
                leg.AddEntry(h, text, "lpe")

            if th1:
                h.SetMinimum(1.0e-6*logY)
                h.SetMaximum(1.0)
            if hasattr(h, "SetStats"):
                h.SetStats(False)

            h.SetLineColor(color)
            h.SetMarkerColor(color)

            color += 1
            if color == 5:
                color += 1

            if th1:
                gopts = "ehist"
            else:
                gopts = "zp"
                h.SetMarkerStyle(20)
                h.SetMarkerSize(0.4 * h.GetMarkerSize())

            if i:
                gopts += "same"
            elif not th1:
                gopts += "a"

            h.Draw(gopts)
            if not th1:
                r.gPad.Update()
                pg = h.GetPaintedGraph()
                pg.GetHistogram().GetYaxis().SetRangeUser(0.0, 1.5)

        r.gPad.SetTickx()
        r.gPad.SetTicky()
        if logY:
            r.gPad.SetLogy()
        leg.Draw()
        fillLeg = False
        can.Print(fileName)
    can.Print(fileName+"]")


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    #r.gStyle.SetOptStat("e")
    r.TH1.SetDefaultSumw2(True)

    chi2Fail = 900
    logY = False
    setup()
    lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
    histos = loopMulti(fileNames=[("v2/H2hh260_all.root",     "H260"),
                                  ("v2/H2hh300_all.root",     "H300"),
                                  ("v2/H2hh350_all.root",     "H350"),
                                  ("v2/tt_eff_all.root",      "tt-dilep"),
                                  #("v2/tt_semi_eff_all.root", "tt-semilep"),
                                  #("v2/ZZ_eff_all.root",      "ZZ"),
                                  ],
                       #nEventsMax=200,
                       )
    pdf(fileName="kinfit_v1.0.pdf", histos=histos)
