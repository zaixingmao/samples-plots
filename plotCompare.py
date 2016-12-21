#!/usr/bin/env python
import ROOT as r
import optparse


r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--logY", dest="logY", default=False, action="store_true", help="")
    options, args = parser.parse_args()
    return options

# define the color scheme you prefer
def getColor(i):
    colors = [r.kBlue, r.kRed, 8]
    return colors[i]

# set the position of the legend
position = (0.7, 0.9 - 0.05*3, 0.9, 0.9)

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


def go(fs, files, varName, bins):
    options = opts()
    histList = []
    fileList = []
    i = 1
    # set the title
    title = "comparison in %s channel; %s; A.U" %(getFinalStateLatex(fs), varName)#"title; x-axis title; y-axis title"


    for iName, iFile in files:
        fileList.append(r.TFile("%s_%s_noIso.root" %(iFile, fs)))
        legendName = iName
        histName = "%s_%i" %(varName, i)
        histList.append((legendName, r.TH1F(histName, "", bins[0], bins[1], bins[2])))
        histList[i-1][1].Sumw2()
        if not hasattr(fileList[i-1].Get("Ntuple"), varName):
            return 0
        fileList[i-1].Get("Ntuple").Draw("%s>>%s" %(varName, histName))
        i+=1

    iMax = -999
    iMin = 999
    legend = r.TLegend(position[0], position[1], position[2], position[3])
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)

    pdf_fileName = "compare_%s_%s.pdf" %(fs, varName)

    c = r.TCanvas("c","Test", 800, 800)
    firstKey = ""
    factor = 1.2
    if options.logY:
        r.gPad.SetLogy()
        factor = 5
    for i in range(len(histList)):
        histList[i][1].Scale(1./histList[i][1].Integral())

        if i == 0:
            histList[i][1].Draw()
            histList[i][1].SetTitle(title)
            histList[i][1].GetYaxis().SetTitleOffset(1.4)

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
    c.Print(pdf_fileName)

files = [# ("7_6_X", "ZPrime_2000_7_6_X_all_SYNC"),
#          ("8_0_X", "ZPrime_2000_all_SYNC"),
#          ("Anirban", "ZPrime_2000_test_all_SYNC")

           ("inclusive", "DY-50_LO_all_SYNC"),
         ("HT-0to100", "DY-50_LO_HT-0to100_all_SYNC"),
         ("HT-100to200", "DY-50_LO_HT-100to200_all_SYNC"),
         ("HT-200to400", "DY-50_LO_HT-200to400_all_SYNC"),
         ("HT-400to600", "DY-50_LO_HT-400to600_all_SYNC"),
         ("HT-600toInf", "DY-50_LO_HT-600toInf_all_SYNC"),

]
vars = [
        ("m_eff", [30, 0 ,3000]),
#         ("m_vis", [20, 0 ,2000]),
#         ("met", [15, 0 ,300]),
#         ("nCSVL", [4, 0 ,4]),
# 
#         ("mPt", [10, 0 ,500]),
#         ("ePt", [10, 0 ,500]),
#         ("tPt", [20, 0 ,800]),
#         ("t1Pt", [20, 0 ,1000]),
#         ("t2Pt", [20, 0 ,1000]),
#         ("eGenPt", [25, 0 ,500]),
#         ("mGenPt", [25, 0 ,500]),
#         ("tGenPt", [50, 0 ,1000]),
#         ("t1GenPt", [50, 0 ,1000]),
#         ("t2GenPt", [50, 0 ,1000]),

]

for iFS in ['mt']:#["et", 'mt', 'tt', 'em']:
    for iVarName, iBins in vars:
        go(iFS, files, iVarName, iBins)
