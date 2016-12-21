#!/usr/bin/env python
import ROOT as r
import optparse
import math

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--logY", dest="logY", default=False, action="store_true", help="")
    parser.add_option("--plotRatio", dest="plotRatio", default=False, action="store_true", help="")
    parser.add_option("--norm", dest="norm", default=False, action="store_true", help="")
    parser.add_option("--sig", dest="sig", default=False, action="store_true", help="")

    options, args = parser.parse_args()
    return options

# define the color scheme you prefer
def getColor(i):
    colors = [17, 2, 3, 4, 6, 7]
    return colors[i]

def getLineStyle(i):
    return 1
    if i % 2 == 0:
        return 2
    else:
        return 3

# set the position of the legend
position = (0.15, 0.88 - 0.05*4, 0.5, 0.88)
position = (0.55, 0.9 - 0.05*4, 0.9, 0.9)

def getLatex(name):
    if name == 't':
        return '#tau'
    elif name == 'm':
        return '#mu'
    elif name == 'e':
        return 'e'
    else:
        return '%s, not supported' %name

def getFinalStateLatex(FS):
    return (getLatex(FS[0]) + getLatex(FS[1]))


def go(fs, files, tail):
    options = opts()
    histList = []
    hist_denum_List = []
    fileList = []
    file_denum_List = []
    i = 1
    # set the title

    denum_tail = '_delta'

    for iName, iFile in files:
        if iName == 'm_eff':
            varName = 'ZPrime_%s_m_eff' %iFS
            vaName_denum = 'bkg_err2_m_eff%s' %denum_tail
        elif iName == 'm_vis':
            varName = 'ZPrime_%s_m_vis' %iFS
            vaName_denum = 'bkg_err2_m_vis%s' %denum_tail
        elif iName == 'svfit':
            varName = 'ZPrime_%s_pfmet_svmc_mass' %iFS
            vaName_denum = 'bkg_err2_pfmet_svmc_mass%s' %denum_tail
        elif iName == 'm_tt':
            varName = 'ZPrime_%s_m_tt' %iFS
            vaName_denum = 'bkg_err2_m_tt%s' %denum_tail
        else:
            varName = 'ZPrime_%s_%s' %(iFS, iName)
            vaName_denum = 'bkg_err2_%s%s' %(iName, denum_tail)

        fileList.append(r.TFile("%s%s_%s.root" %(iFile, tail, fs)))
#         print "%s_%s.root" %(iFile, fs)
#         print varName
#         print vaName_denum
        histList.append((iName, fileList[i-1].Get(varName)))
        print varName
        histList[i-1][1].Sumw2()
        histList[i-1][1].Scale(1./10)

        if vaName_denum != "":
            file_denum_List.append(r.TFile("%s_%s.root" %(iFile, fs)))
            hist_denum_List.append((iName, file_denum_List[i-1].Get(vaName_denum)))
            print vaName_denum
            hist_denum_List[i-1][1].Sumw2()
        i+=1

    iMax = -999
    iMin = 999
    legend = r.TLegend(position[0], position[1], position[2], position[3])
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    pdf_fileName = "compare_%s_%s.pdf" %(fs, varName)

    c = r.TCanvas("c","Test", 800, 800)
    firstKey = ""
    scale = 1.8
    if options.logY:
        r.gPad.SetLogy()
        scale = 10.0
    r.gPad.SetTickx()
    r.gPad.SetTicky()

    if options.plotRatio:
        histList[0][1].Divide(histList[1][1])
        histList[0][1].Draw()
        histList[0][1].SetTitle("comparison in %s channel; m_eff; bkg after cosDPhi cut / bkg after Zeta cut" %getFinalStateLatex(fs))
        histList[0][1].GetYaxis().SetTitleOffset(1.2)

    else:
        for i in range(len(histList)):
            histList[i][1].SetLineColor(getColor(i))
            histList[i][1].SetLineStyle(getLineStyle(i))
            histList[i][1].SetLineWidth(2)
            if options.norm:
                histList[i][1].Scale(1./histList[i][1].Integral())
            legend.AddEntry(histList[i][1], histList[i][0], 'l')
            if options.sig and vaName_denum != '':
                nBins = histList[i][1].GetNbinsX()
                for j in range(1, nBins+1, 1):
                    num = histList[i][1].GetBinContent(j)
                    denum = hist_denum_List[i][1].GetBinContent(j)
                    num_err = histList[i][1].GetBinError(j)
                    denum_err = hist_denum_List[i][1].GetBinError(j)
                    if num == 0 or denum <= 0:
                        histList[i][1].SetBinContent(j, 0)
                        histList[i][1].SetBinError(j, 0)
                    else:
                        histList[i][1].SetBinContent(j, num/math.sqrt(denum))
                        histList[i][1].SetBinError(j, (num/math.sqrt(denum))*math.sqrt((num_err/num)**2 + (denum_err/denum)**2))
 #                        histList[i][1].SetBinContent(j, num*math.sqrt(histList[i][1].GetBinWidth(j))/math.sqrt(denum))
#                         histList[i][1].SetBinError(j, (num*math.sqrt(histList[i][1].GetBinWidth(j))/math.sqrt(denum))*math.sqrt((num_err/num)**2 + (denum_err/denum)**2))

        maximum = 0
        for i in range(len(histList)):
            if histList[i][1].GetMaximum() > maximum:
                maximum = histList[1][1].GetMaximum()

        which = 0

        histList[which][1].SetMaximum(maximum*scale)
        histList[which][1].SetMinimum(0.0001)
        histList[which][1].SetTitle("comparison in %s channel; m_eff; sig / #sqrt{bkg}" %getFinalStateLatex(fs))
        histList[which][1].GetYaxis().SetTitleOffset(1.5)
        histList[which][1].Draw()

        for i in range(len(histList)):
            if i == 0:
                histList[0][1].SetFillColor(17)
                histList[0][1].SetFillStyle(1001)
                histList[0][1].SetMarkerColor(r.kBlack)
                histList[0][1].SetMarkerStyle(5)
                histList[0][1].Draw("E2same")
            else:
                histList[i][1].Draw("same")

#         histList[0][1].SetTitle("comparison in %s channel; m_eff; events / GeV" %getFinalStateLatex(fs))

        legend.Draw('same')
    c.Print(pdf_fileName)

tail = "_3000"
# tail = ""

dir = tail[tail.find("_") + 1:] + "/"

files = [
         ("m_eff", "%sm_eff" %dir),
#          ("m_eff_sumPt", "m_eff_sumPt"),
#          ("true_mass", "true_mass"),
#          ("total_transverse_mass", "total_transverse_mass"),
#          ("m_vis", "m_vis"),
         ("svfit", "%ssvfit" %dir),
         ("m_tt", "%sm_tt" %dir),
]

# files = [("Z' (750)", "750"),
#         ("Z' (1750)", "1750"),
#         ("Z' (3000)", "3000")]

for iFS in ['et']:
    go(iFS, files, tail)
#     go(iFS, files, tail, 'bkg_err2_m_withMET_delta_0')
