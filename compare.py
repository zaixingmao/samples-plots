#!/usr/bin/env python

import ROOT as r
import tool
import os
import math

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)

def passCut(tree, which):
    if which == '8TeV':
        if tree.charge1.at(0) == tree.charge2.at(0):
            return False
        if tree.iso1.at(0) > 1.5 or tree.iso2.at(0) > 1.5:
            return False
    if which == '13TeV':
        if tree.t1Charge == tree.t2Charge:
            return False
        if tree.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits > 1.5 or tree.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits > 1.5:
            return False

    if tree.CSVJ1 > 0.679 or tree.CSVJ1Pt < 20.0:
        return False
    if tree.CSVJ2 > 0.679 or tree.CSVJ2Pt < 20.0:
        return False
    return True


def getVarValue(tree, varName, which):

    if which == '8TeV':
        vars = {"tau1Pt": tree.pt1.at(0),
                "tau2Pt": tree.pt2.at(0),
                "tau1Eta": tree.eta1.at(0),
                "tau2Eta": tree.eta2.at(0),
                "tau1Iso": tree.iso1.at(0),
                "tau2Iso": tree.iso2.at(0),
                "J1Pt": tree.J1Pt,
                "J1Eta": tree.J1Eta,
                "J1CSVbTag": tree.J1CSVbtag,
                "J2Pt": tree.J2Pt,
                "J2Eta": tree.J2Eta,
                "J2CSVbTag": tree.J2CSVbtag,
                "svMass": tree.svMass.at(0),
                "mJJ": tree.mJJ,
                "met": tree.met.at(0),
                "CSVJ1": tree.CSVJ1,
                "CSVJ1Pt": tree.CSVJ1Pt,
                "CSVJ1Eta": tree.CSVJ1Eta,
                "CSVJ2": tree.CSVJ2,
                "CSVJ2Pt": tree.CSVJ2Pt,
                "CSVJ2Eta": tree.CSVJ2Eta,

}
    elif which == '13TeV':
        vars = {"tau1Pt": tree.t1Pt,
                "tau2Pt": tree.t2Pt,
                "tau1Eta": tree.t1Eta,
                "tau2Eta": tree.t2Eta,
                "tau1Iso": tree.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits,
                "tau2Iso": tree.t1ByCombinedIsolationDeltaBetaCorrRaw3Hits,
                "J1Pt": tree.jet1Pt,
                "J1Eta": tree.jet1Eta,
                "J1CSVbTag": tree.jet1CSVBtag,
                "J2Pt": tree.jet2Pt,
                "J2Eta": tree.jet2Eta,
                "J2CSVbTag": tree.jet2CSVBtag,
                "svMass": tree.t1_t2_SVfitMass,
                "met": tree.pfMetEt,
                "mJJ": tree.mJJ,
                "CSVJ1": tree.CSVJ1,
                "CSVJ1Pt": tree.CSVJ1Pt,
                "CSVJ1Eta": tree.CSVJ1Eta,
                "CSVJ2": tree.CSVJ2,
                "CSVJ2Pt": tree.CSVJ2Pt,
                "CSVJ2Eta": tree.CSVJ2Eta,
}
    return vars[varName]

def readFile(file, hist, varName, which): 
    f = r.TFile(file)
    if which == '8TeV':
        tree = f.Get('eventTree')
    else:
        tree = f.Get('Ntuple')

    nEntries = tree.GetEntries()

    if which == '13TeV':
        yields = 0.0
        scale = 0.0
    else:
        yields = 0.0
        scale = 0.0
        yields_had = 0.0
        scale_had = 0.0
        yields_semi = 0.0
        scale_semi = 0.0

    for i in range(nEntries):
        tool.printProcessStatus(i, nEntries, 'Looping file %s for %s' % (file, varName), i-1)
        tree.GetEntry(i)
        if not passCut(tree, which):
            continue
        if which == '13TeV':
            hist.Fill(getVarValue(tree, varName, which))
            yields += 1.0
            scale = (tree.xs + 0.0)/(tree.initEvents + 0.0)
        else:
            hist.Fill(getVarValue(tree, varName, which), tree.xs/(tree.initEvents+0.0))
            if tree.sampleName == "tt_all":
                yields += 1.0
                scale = (tree.xs + 0.0)/(tree.initEvents + 0.0)
            if tree.sampleName == "tthad_all":
                yields_had += 1.0
                scale_had = (tree.xs + 0.0)/(tree.initEvents + 0.0)
            if tree.sampleName == "ttsemi_all":
                yields_semi += 1.0
                scale_semi = (tree.xs + 0.0)/(tree.initEvents + 0.0)

    if which == '13TeV':
        hist.Sumw2()
        hist.Scale((tree.xs+0.0)/(tree.initEvents+0.0))
        unc = math.sqrt(yields+0.0)*scale
    else:
        unc = math.sqrt(yields+0.0)*scale + math.sqrt(yields_had+0.0)*scale_had + math.sqrt(yields_semi+0.0)*scale_semi

    print ''
    return unc

def buildHistDict(vars2compare):
    dict = {}
    for i, Range in vars2compare:
        dict[i] = {}
        dict[i]['8TeV'] = r.TH1F("hist_8TeV_%s" %i, "", Range[0], Range[1], Range[2])
        dict[i]['13TeV'] = r.TH1F("hist_13TeV_%s" %i, "", Range[0], Range[1], Range[2])

    return dict

def main():
    file_13TeV = '/nfs_scratch/zmao/test/DYJetsToLL_all.root'#'/nfs_scratch/zmao/test/TTJets_all.root'#
    file_8TeV = '/nfs_scratch/zmao/samples_Iso/tauESOn/normal/dy.root'#'/nfs_scratch/zmao/samples_Iso/tauESOff/normal/TT.root'#

    vars2compare = [("tau1Pt", [50, 30, 230]),
#                     ("tau2Pt", [50, 30, 230]),
#                     ("tau1Eta", [25, -2.5, 2.5]),
#                     ("tau2Eta", [25, -2.5, 2.5]),
#                     ("tau1Iso", [40, 0, 2.]),
#                     ("tau2Iso", [40, 0, 2.]),
#                     ("J1Pt", [50, 30, 230]),
#                     ("J2Pt", [50, 30, 230]),
#                     ("J1Eta", [40, -4, 4]),
#                     ("J2Eta", [40, -4, 4]),
#                     ("J1CSVbTag", [50, 0, 1]),
#                     ("J2CSVbTag", [50, 0, 1]),
# 
#                     ("CSVJ1Pt", [50, 30, 230]),
#                     ("CSVJ2Pt", [50, 30, 230]),
#                     ("CSVJ1Eta", [40, -4, 4]),
#                     ("CSVJ2Eta", [40, -4, 4]),
#                     ("CSVJ1", [50, 0, 1]),
#                     ("CSVJ2", [50, 0, 1]),
# 
#                     ("svMass", [35, 0, 350]),
#                     ("met", [25, 0, 200]),
#                     ("mJJ", [50, 0, 500])

]

    histDicts = buildHistDict(vars2compare)


    psfile = 'out.pdf'
    c = r.TCanvas("c","Test", 800, 600)

    counter = 0
    for iVar, Range in vars2compare:
        unc13TeV = readFile(file = file_13TeV, hist = histDicts[iVar]['13TeV'], varName = iVar, which = '13TeV')
        unc8TeV = readFile(file = file_8TeV, hist = histDicts[iVar]['8TeV'], varName = iVar, which = '8TeV')

        #normalization
#         histDicts[iVar]['13TeV'].Scale(1.0/histDicts[iVar]['13TeV'].Integral(0, histDicts[iVar]['13TeV'].GetNbinsX()+1))
#         histDicts[iVar]['8TeV'].Scale(1.0/histDicts[iVar]['8TeV'].Integral(0, histDicts[iVar]['8TeV'].GetNbinsX()+1))

        counter += 1
        c.Clear()
        histDicts[iVar]['13TeV'].SetTitle("13 TeV vs 8 TeV; %s; a.u" %iVar)
        histDicts[iVar]['8TeV'].SetTitle("13 TeV vs 8 TeV; %s; a.u" %iVar)
        histDicts[iVar]['8TeV'].SetLineColor(r.kRed)

        if histDicts[iVar]['13TeV'].GetMaximum() >= histDicts[iVar]['8TeV'].GetMaximum():
            histDicts[iVar]['13TeV'].Draw()
            histDicts[iVar]['8TeV'].Draw('same')
        else:
            histDicts[iVar]['8TeV'].Draw()
            histDicts[iVar]['13TeV'].Draw('same')
        if counter == 1:
            l = tool.setMyLegend(lPosition = [0.7, 0.85, 0.9, 0.7], lHistList = [(histDicts[iVar]['13TeV'], '13TeV'), (histDicts[iVar]['8TeV'], '8TeV')])
            l.Draw('same')
            c.Print('%s(' %psfile)
        if counter == len(vars2compare):
            l.Draw('same')
            c.Print('%s)' %psfile)
        else:
            l.Draw('same')
            c.Print('%s' %psfile)

        print "13TeV Integral: %.2f +- %.2f (fb)" %(histDicts[iVar]['13TeV'].Integral(0, histDicts[iVar]['13TeV'].GetNbinsX()+1), unc13TeV) 
        print "8TeV Integral : %.2f +- %.2f (fb)" %(histDicts[iVar]['8TeV'].Integral(0, histDicts[iVar]['8TeV'].GetNbinsX()+1), unc8TeV) 

    c.Close()

main()