#!/usr/bin/env python

import ROOT as r
import tool
from array import array

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs


def getGraph(points, color):
    x = []
    y = []
    ex = []
    ey = []

    for x_min, x_max, y_value, y_error in points:
        x.append((x_max + x_min)/2.0)
        y.append(y_value)
        ex.append((x_max - x_min)/2.0)
        ey.append(y_error)

    gr = r.TGraphErrors(len(x), array('d', x), array('d', y), array('d', ex), array('d', ey))
    gr.SetLineColor(color)
    gr.SetTitle("; relIso; OS/SS");

    return gr

def run(type = 'both'):

    points = {"both_antiIso":([(0.2, 0.5, 2.546, 0.115), (0.5, 1.0, 2.370, 0.233), (1.0, 10, 2.279, 0.671)], r.kBlue),
              "both_antiIso_MEt20":([(0.2, 0.5, 2.546, 0.151), (0.5, 1.0, 2.756,  0.360), (1.0, 10, 2.581, 0.895)], r.kRed),
              "e_antiIso":([(0.15, 0.2, 1.668, 0.216), (0.2, 0.5, 1.933, 0.138), (0.5, 1.0, 2.924,  0.475), (1.0, 10, 1.178, 0.491)], r.kRed),
              "e_antiIso_MEt20":([(0.15, 0.2, 1.596, 0.275), (0.2, 0.5, 1.508, 0.148), (0.5, 1.0, 2.976,  0.630), (1.0, 10, 3.118, 1.828)], r.kOrange),
              "m_antiIso":([(0.15, 0.2, 1.707, 0.232), (0.2, 0.5, 1.819, 0.093), (0.5, 1.0, 1.798,  0.102), (1.0, 10, 1.528, 0.095)], r.kBlue),
              "m_antiIso_MEt20":([(0.15, 0.2, 1.288, 0.237), (0.2, 0.5, 1.938, 0.133), (0.5, 1.0, 1.965,  0.145), (1.0, 10, 1.663, 0.126)], r.kCyan),
              }
    
    first = True
    if type != 'both':
        type = 'single'

    psfile = 'QCD_scales_%s.pdf' %type
    c = r.TCanvas("c","Test", 800, 600)
    grs = []
    histlist = []

    for iKey in points.keys():
        if type == 'both' and (not 'both' in iKey):
            continue
        elif type != 'both' and ('both' in iKey):
            continue
        grs.append(getGraph(points[iKey][0], points[iKey][1]))
        histlist.append((r.TH1F('dummy_%s' %iKey, '', 1, 0 ,1), iKey, 'L'))
        histlist[len(histlist)-1][0].SetLineColor(points[iKey][1])
        if first:        
            grs[0].Draw("AP")
            if type != 'both':
                grs[0].SetMaximum(3.5)
                grs[0].SetMinimum(0.8)

            first = False
        else:
            grs[len(grs)-1].Draw("sameP")

    r.gPad.SetTicky()
    r.gPad.SetTickx()
    r.gPad.SetLogx()
    leg = tool.setMyLegend((0.5, 0.8 - 0.07*(len(histlist)-1), 0.85, 0.8), histlist)
    leg.Draw("same")
    c.Print('%s' %psfile)
    c.Close()

run('single')