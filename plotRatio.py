#!/usr/bin/env python
import ROOT as r

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs


mt_svfit = [115., 225., 0.4]
mt_mtt = [103., 142., 0.43]
mt_meff = [100., 246., 0.57]


et_svfit = [105., 160., 0.31]
et_mtt = [95., 116., 0.43]
et_meff = [86., 230., 0.6]

em_svfit = [26.8, 41.6, 0.095]
em_mtt = [24.8, 29.8, 0.105]
em_meff = [23., 39., 0.16]

fakeHist = r.TH1F("fakeHist", "", 160, 0, 4000)

svfit = r.TProfile("svfit", "", 160, 0, 4000, 0, 2)
mtt = r.TProfile("mtt", "", 160, 0, 4000, 0, 2)

counter = 0

svfitList = em_svfit
mttList = em_mtt
meffList = em_meff

for i in [750, 1750, 3000]:
    svfit.Fill(i, svfitList[counter]/meffList[counter], 1)
    mtt.Fill(i, mttList[counter]/meffList[counter], 1)
    counter += 1

svfit_line_1 = r.TLine(750, svfitList[0]/meffList[0], 1750, svfitList[1]/meffList[1])
svfit_line_2 = r.TLine(1750, svfitList[1]/meffList[1], 3000, svfitList[2]/meffList[2])
mtt_line_1 = r.TLine(750, mttList[0]/meffList[0], 1750, mttList[1]/meffList[1])
mtt_line_2 = r.TLine(1750, mttList[1]/meffList[1], 3000, mttList[2]/meffList[2])


svfit.SetMarkerColor(6)
svfit.SetMarkerSize(2)
svfit_line_1.SetLineColor(6)
svfit_line_1.SetLineWidth(2)
svfit_line_2.SetLineColor(6)
svfit_line_2.SetLineWidth(2)

mtt.SetMarkerColor(7)
mtt.SetMarkerSize(2)
mtt_line_1.SetLineColor(7)
mtt_line_1.SetLineWidth(2)
mtt_line_2.SetLineColor(7)
mtt_line_2.SetLineWidth(2)

svfit.SetMarkerStyle(20)
mtt.SetMarkerStyle(20)


pdf_fileName = "ratio.pdf"

c = r.TCanvas("c","Test", 800, 800)
fakeHist.SetTitle("sig/#sqrt{bkg} sensitivity comparison; Z' mass; mass reco sensitivity / m_eff sensitivity")
fakeHist.GetYaxis().SetTitleOffset(1.2)
fakeHist.SetMaximum(1.3)
fakeHist.SetMinimum(.4)
fakeHist.Draw()
one = r.TLine(0, 1, 4000, 1)
one.SetLineStyle(2)
one.SetLineWidth(2)

one.Draw("same")
svfit.Draw("sameP")
svfit_line_1.Draw("same")
svfit_line_2.Draw("same")
mtt.Draw("sameP")
mtt_line_1.Draw("same")
mtt_line_2.Draw("same")

legend = r.TLegend(0.6, 0.85 - 0.05*3, 0.8, 0.85)
legend.SetFillStyle(0)
legend.SetBorderSize(0)
legend.AddEntry(svfit, 'SVFit', 'p')
legend.AddEntry(mtt, 'm_tt', 'p')
legend.Draw("same")
c.Print(pdf_fileName)
