#!/usr/bin/env python
import ROOT as r
import optparse


r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--logY", dest="logY", default=False, action="store_true", help="")
    parser.add_option("--file1", dest="file1", default='', help="input file location 1")
    parser.add_option("--hist1", dest="hist1", default='', help="histo name of file 1")
    parser.add_option("--legend1", dest="legend1", default='', help="legend name of file 1")
    parser.add_option("--file2", dest="file2", default='', help="input file location 2")
    parser.add_option("--hist2", dest="hist2", default='', help="histo name of file 2")
    parser.add_option("--legend2", dest="legend2", default='', help="legend name of file 2")
    parser.add_option("--file3", dest="file3", default='', help="input file location 3")
    parser.add_option("--hist3", dest="hist3", default='', help="histo name of file 3")
    parser.add_option("--legend3", dest="legend3", default='', help="legend name of file 3")
    options, args = parser.parse_args()
    return options

# define the color scheme you prefer
def getColor(i):
    colors = [r.kBlue, r.kRed, 8]
    return colors[i]

# set the position of the legend
position = (0.7, 0.9 - 0.05*3, 0.9, 0.9)

# set the title
title = ""#"title; x-axis title; y-axis title"

def go():
    options = opts()
    histList = []
    fileList = []
    i = 1
    while hasattr(options, "file%i" %i):
        if getattr(options, "file%i" %i) != '':
            if getattr(options, "hist%i" %i) == '':
                print "ERROR!!! Missing info for hist%i" %i
            elif getattr(options, "legend%i" %i) == '':
                print "ERROR!!! Missing info for legend%i" %i
            else:
                fileList.append(r.TFile(getattr(options, "file%i" %i)))
                histList.append((getattr(options, "legend%i" %i), fileList[i-1].Get(getattr(options, "hist%i" %i))))
        i+=1
    iMax = -999
    iMin = 999
    legend = r.TLegend(position[0], position[1], position[2], position[3])
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    pdf_fileName = "compare"
    c = r.TCanvas("c","Test", 800, 800)
    firstKey = ""
    factor = 1.2
    if options.logY:
        r.gPad.SetLogy()
        factor = 5
    for i in range(len(histList)):
        pdf_fileName += "_%s" %histList[i][0]
        if i == 0:
            histList[i][1].Draw()
            histList[i][1].SetTitle(title)
        else:
            histList[i][1].Draw("same")
        if histList[i][1].GetMaximum() > iMax:
            iMax = histList[i][1].GetMaximum()
        if histList[i][1].GetMinimum() < iMin:
            iMin = histList[i][1].GetMinimum()
        histList[i][1].SetLineColor(getColor(i))
        legend.AddEntry(histList[i][1], histList[i][0], 'l')
    legend.Draw('same')
    histList[0][1].SetMaximum(iMax*factor)
    histList[0][1].SetMinimum(iMin)
    c.Print('%s.pdf' %pdf_fileName)

go()
