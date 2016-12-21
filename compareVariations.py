#!/usr/bin/env python
import ROOT as r
from array import array

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

bins = array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600, 900, 1200, 1700])
bkgList = ['TT', 'VV', 'SMHiggs', 'DYJets']


def setHist(fileName, nominalFile, name, color, histos,files,legend):
    files.append(r.TFile(fileName))

    histos.append(files[len(files)-1].Get('total_bkg'))

    if name != "nominal":
        histos[len(histos)-1].Add(files[len(files)-1].Get('WJets'), -1)
        histos[len(histos)-1].Add(files[len(files)-1].Get('QCD'), -1)
        histos[len(histos)-1].Add(nominalFile.Get('WJets'), 1)
        histos[len(histos)-1].Add(nominalFile.Get('QCD'), 1)

    histos[len(histos)-1].SetLineColor(color)
    histos[len(histos)-1].Scale(1, 'width')
    legend.AddEntry(histos[len(histos)-1], name, 'l')


def setRatioHist(hist, hist2,  var):
    hist.SetMaximum(hist.GetMaximum() + 0.1)
    hist.SetMinimum(hist2.GetMinimum() -0.1)
    hist.GetYaxis().SetNdivisions(5,5,0)
    hist.GetXaxis().SetLabelSize(0.1)
    hist.GetXaxis().SetTitleSize(0.1)
    hist.GetYaxis().SetLabelSize(0.1)
    hist.SetTitle("; %s; variation / nominal" %var)
    hist.GetYaxis().SetTitleSize(0.1)
    hist.GetYaxis().SetTitleOffset(0.5)
    hist.GetYaxis().CenterTitle()

def setPlotHist(hist, variation):
    #hist.GetXaxis().SetLabelSize(0.1)
    #hist.GetXaxis().SetTitleSize(0.1)
    #hist.GetYaxis().SetLabelSize(0.1)
    hist.GetYaxis().SetTitleOffset(1.3)
    hist.SetTitle("background variations of %s; ; events / GeV" %variation)



def run(var, variation, fs):
    histos = []
    files = []
    dir = "/user_data/zmao/datacard_histo_2016"

    legend = r.TLegend(0.55, 0.8 - 0.05*3, 0.8, 0.8)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    nominalFile = '/user_data/zmao/datacard_histo_2016/nominal/datacard_2016_%s_%s.root' %(var, fs)
    nominal_file = r.TFile(nominalFile)
    setHist(nominalFile, nominal_file,
            'nominal', r.kBlack, histos, files, legend)
    setHist('/user_data/zmao/datacard_histo_2016/%s/datacard_2016_%s_%s_%sUp.root' %(variation, var, fs, variation), 
            nominal_file,
            '%s up' %variation, r.kBlue, histos, files, legend)
    setHist('/user_data/zmao/datacard_histo_2016/%s/datacard_2016_%s_%s_%sDown.root' %(variation, var, fs, variation), 
            nominal_file,
            '%s down' %variation, r.kRed, histos, files, legend)

    c = r.TCanvas("c","Test", 600, 800)

    p = r.TPad("p","p", 0., 1, 1., 0.3)
    p_r = r.TPad("p_r","p_r", 0.,0.3,1.,0.06)
    p.SetMargin(1, 1, 0, 0.1)
    p_r.SetMargin(1, 1, 0.2, 0)
    p.Draw()
    p_r.Draw()
    p.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    r.gPad.SetLogy()
    setPlotHist(histos[0], variation)
    histos[0].Draw()                                                                                                                                                                        
    histos[1].Draw("same")
    histos[2].Draw("same")
    legend.Draw("same")
    p_r.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    
    ratio_up = histos[1].Clone()
    ratio_up.Divide(histos[0])
    ratio_down = histos[2].Clone()
    ratio_down.Divide(histos[0])
    setRatioHist(ratio_up, ratio_down, var)

    ratio_up.Draw("hist")
    ratio_down.Draw("same hist")

    line = r.TLine(85,1,1700,1)
    line.SetLineColor(r.kBlack)
    line.SetLineStyle(2)
    line.Draw("same")
    c.Print('systematicVariations_%s_%s_%s.pdf' %(var, variation, fs))
    c.Close()


runMap = {"tauEC": ["mt"],
          "tauUnc":["mt"],
          "jetEC": ["mt"]}

for iVariation in runMap.keys():
    for iFS in runMap[iVariation]:
        run("m_effective", iVariation, iFS)

