#!/usr/bin/env python
from array import array
import ROOT as r

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

# define the color scheme you prefer
def getColor(i):
    colors = [17, 2, 3, 4, 5, 6]
    return colors[i]

def getLabel_color_style(label):
    label_dict = {}
    label_dict['mt_mt_1_30'] = ['#mu#tau with m_{T} > 30 GeV', 2, 1]
    label_dict['mt'] = ['#mu#tau', 2, 2]
    label_dict['et_mt_1_30'] = ['e#tau with m_{T} > 30 GeV', 4, 1]
    label_dict['et'] = ['e#tau', 4, 2]
    return label_dict[label]

def buildHist(hist, hist2, points, label, legend):
    counter = 1
    for SF, err, purity in points:
        hist.SetBinContent(counter, SF)
        hist.SetBinError(counter, err)
        hist2.SetBinContent(counter, purity)
        counter += 1

    legend.AddEntry(hist, label, 'l')
    legend.AddEntry(hist2, label + ' W+Jets Purity', 'l')


def go():
    value_dict = {}
    #value_dict['mt'] = [(0.258, 0.034), (0.271, 0.041), (0.199, 0.031), (0.274, 0.042), (0.307, 0.028)]
    #value_dict['mt_mt_1_30'] = [(0.254, 0.032), (0.257, 0.040), (0.243, 0.034), (0.314, 0.060), (0.247, 0.064)]
    #value_dict['et'] = [(0.309, 0.050), (0.336, 0.046), (0.316, 0.054), (0.206, 0.057), (0.218, 0.032)]
    #value_dict['et_mt_1_30'] = [(0.289, 0.040), (0.272, 0.040), (0.216, 0.046), (0.155, 0.054), (0.227, 0.067)]

#     value_dict['mt'] = [(0.196, 0.033), (0.197, 0.046), (0.153, 0.055), (0.149, 0.040)]
#     value_dict['mt_mt_1_30'] = [(0.184, 0.033), (0.239, 0.028), (0.268, 0.056), (0.209, 0.036)]
#     value_dict['et'] = [(0.114, 0.052), (0.215, 0.051), (0.343, 0.072), (0.151, 0.040)]
#     value_dict['et_mt_1_30'] = [(0.103, 0.043), (0.149, 0.039), (0.295, 0.070), (0.205, 0.036)]

#     value_dict['mt'] = [(0.216, 0.036, 0.44), (0.240, 0.038, 0.44), (0.240, 0.039, 0.44), (0.306, 0.039, 0.58), (0.292, 0.041, 0.51), (0.227, 0.037, 0.46), (0.323, 0.046, 0.49), (0.183, 0.023, 0.46), (0.150, 0.033, 0.22)]
#     value_dict['mt_mt_1_30'] = [(0.216, 0.036, 0.43), (0.240, 0.038, 0.44), (0.240, 0.039, 0.44), (0.306, 0.039, 0.58), (0.292, 0.041, 0.51), (0.226, 0.037, 0.46), (0.307, 0.045, 0.52), (0.211, 0.022, 0.65), (0.195, 0.026, 0.65)]
    value_dict['et'] = [(0.302, 0.043, 0.62), (0.302, 0.047, 0.53), (0.228, 0.063, 0.32), (0.271, 0.075, 0.35), (0.191, 0.057, 0.27), (0.256, 0.061, 0.33), (0.431, 0.073, 0.55), (0.167, 0.036, 0.29), (0.230, 0.036, 0.35)]
    value_dict['et_mt_1_30'] = [(0.302, 0.043, 0.62), (0.302, 0.047, 0.53), (0.228, 0.063, 0.32), (0.271, 0.075, 0.35), (0.191, 0.057, 0.27), (0.257, 0.061, 0.33), (0.406, 0.069, 0.58), (0.125, 0.029, 0.35), (0.288, 0.046, 0.71)]

    hist_dict = {}
    bins = array('d', [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])

    legend = r.TLegend(0.15, 0.95 - 0.05*5, 0.5, 0.88)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    pdf_fileName = "WJets_SF.pdf"
    c = r.TCanvas("c","Test", 800, 800)
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    counter = 0
    for ikey in value_dict.keys():
        hist_dict[ikey] = r.TH1F(ikey, "", len(bins)-1, bins)
        hist_dict[ikey + '_purity'] = r.TH1F(ikey + '_purity', "", len(bins)-1, bins)

        label, color, style  = getLabel_color_style(ikey)
        hist_dict[ikey].SetLineColor(color)
        hist_dict[ikey].SetLineStyle(style)
        hist_dict[ikey + '_purity'].SetLineColor(color+2)
        hist_dict[ikey + '_purity'].SetLineStyle(style)

        buildHist(hist_dict[ikey], hist_dict[ikey + '_purity'], value_dict[ikey], label, legend)

        if counter == 0:
            hist_dict[ikey].SetTitle("WJets LooseToTight SF; cos#Delta#Phi(#slash{E}_{T}, e); WJets SF")
            hist_dict[ikey].GetXaxis().SetTitleFont(42)
            hist_dict[ikey].GetYaxis().SetTitleOffset(1.4)
            hist_dict[ikey].SetMaximum(0.8)
            hist_dict[ikey].SetMinimum(0.1)
            hist_dict[ikey].Draw()
            hist_dict[ikey + '_purity'].Draw('hist same')
        else:
            hist_dict[ikey].Draw('same')
            hist_dict[ikey + '_purity'].Draw('hist same')

        counter += 1
    legend.Draw('same')
    c.Print(pdf_fileName)


go()
