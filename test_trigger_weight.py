#!/usr/bin/env python

import ROOT as r
import trigger


def curve(func=None, eta=1.0, ptMin=0.0, ptMax=100.0, nSamples=100):
    g = r.TGraph()
    for i in range(nSamples):
        pt = ptMin + (ptMax - ptMin) * (i + 0.0) / nSamples
        g.SetPoint(i, pt, func(pt, eta))
    return g


def go(canvas=None, pdf="", xTitle="", yTitle="", funcNames=[]):
    ptMin = 20.0
    ptMax = 220.0
    nSamples = 100

    h = r.TH2D("null", ";%s;%s" % (xTitle, yTitle), 1, ptMin, ptMax, 1, 0.0, 1.5)
    h.SetStats(False)
    h.Draw()
    leg = r.TLegend(0.45, 0.30, 0.85, 0.15)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)

    keep = []
    i = 0
    for funcName in funcNames:
        for eta in [1.0, 1.8]:
            func = getattr(trigger, "__%s" % funcName)
            g = curve(func, eta=eta, ptMin=ptMin, ptMax=ptMax, nSamples=nSamples)

            i += 1

            g.SetLineColor(i)
            g.SetLineStyle(i)
            g.SetMarkerColor(i)
            g.Draw("lpsame")
            keep.append(g)
            if "Weight" in funcName:
                title = funcName[:funcName.find("Weight")]
            else:
                title = funcName

            title += " (barrel)" if abs(eta) < 1.4 else " (endcap)"
            leg.AddEntry(g, title, "lp")

    leg.Draw()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    canvas.Print(pdf)


if __name__ == "__main__":
    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000

    canvas = r.TCanvas()
    pdf = "trigger.pdf"
    canvas.Print(pdf + "[")

    go(canvas,
       pdf,
       xTitle="#tau_{h} p_{T} (GeV)",
       yTitle="(data / MC)   correction to simulated efficiency",
       funcNames=["DiTau_correction_one_leg", "DiTauJet_correction_one_leg"],
       )

    go(canvas,
       pdf,
       xTitle="#tau_{h} p_{T} (GeV)",
       yTitle="measured trigger efficiency",
       funcNames=["DiTau_eff_tau_mc", "DiTau_eff_tau_data"],
       )

    go(canvas,
       pdf,
       xTitle="#tau_{h} p_{T} (GeV)",
       yTitle="measured trigger efficiency",
       funcNames=["DiTauJet_eff_tau_mc", "DiTauJet_eff_tau_data"],
       )

    go(canvas,
       pdf,
       xTitle="jet p_{T} (GeV)",
       yTitle="measured trigger efficiency",
       funcNames=["DiTauJet_eff_jet_data"],
       )

    canvas.Print(pdf + "]")

