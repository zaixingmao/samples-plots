#!/usr/bin/env python                                                                                                                                           
import ROOT as r
import array
import tool

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

c = r.TCanvas("c","Test",600, 600)
c.Range(0,0,1,1)
c.SetFillColor(0)
x_unsliced  = array.array('d', [600, 1250, 1750, 2500])
ex_unsliced  = array.array('d', [100, 250, 250, 500])
x_sliced  = array.array('d', [525, 1025, 1525, 2025, 2500, 2900])
ex_sliced  = array.array('d', [25, 25, 25, 25, 50, 100])

y_unsliced = array.array('d', [0.4, 0.5, 0.9, 1.4])#[0.4, 0.5, 1.2, 5.2, 6.4])
#y_unsliced = array.array('d', [0.3, 0.4, 0.6, 1.1, 1.8])#[0.4, 0.5, 1.2, 5.2, 6.4])                                                                           
ey_unsliced = array.array('d', [0.0, .1, .1, .1])#[0., 0., 0.1, 0.7, 1.4])
#ey_unsliced = array.array('d', [0., 0., 0.0, .1, .3])#[0., 0., 0.1, 0.7, 1.4])                                                                                  

y_unsliced_pu = array.array('d', [0.7, 0.7, 1.2, 2.])#[0.6, 0.9, 1.2, 2.7, 4.4])
#y_unsliced_pu = array.array('d', [0.3, 0.6, 0.9, 1.3, 1.8])#[0.6, 0.9, 1.2, 2.7, 4.4])                                                                        
ey_unsliced_pu = array.array('d', [0.1, 0.1, 0.1, 0.2])#[0., 0., 0.1, 0.1, 0.9])
#ey_unsliced_pu = array.array('d', [0., 0.1, 0., 0.1, 0.3])#[0., 0., 0.1, 0.1, 0.9])                                                                           
ey_unsliced_fake = array.array('d', [0., 0., 0., 0.])

y_sliced_pu  = array.array('d', [0.7, 1.7, 2.5, 2.6, 7.1, 12.2])#[0.7, 1.7, 2.5, 3.3, 7.1, 12.1])
ey_sliced_pu  = array.array('d', [0.1, 0.2, 0.6, 0.9, 3.5, 3.0])#[0.1, 0.2, 0.6, 1.6, 3.5, 2.9])

y_sliced = array.array('d', [0.6, 1.0, 1.3, 1.7, 2.3, 7.1]) #[0.6, 1.0, 2.0, 17.9, 2.3, 8.5])
ey_sliced  = array.array('d', [0.1, 0.3, 0.6, 0.5, 0.6, 2.9]) #[0.1, 0.3, 0.6, 4.4, 0.6, 3.9])

gr_unsliced = r.TGraphErrors(len(x_unsliced), x_unsliced, y_unsliced, ex_unsliced, ey_unsliced)
gr_unsliced_pu = r.TGraphErrors(len(x_unsliced), x_unsliced, y_unsliced_pu, ex_unsliced, ey_unsliced_pu)
gr_unsliced2 = r.TGraphErrors(len(x_unsliced), x_unsliced, y_unsliced, ex_unsliced, ey_unsliced_fake)
gr_unsliced_pu2 = r.TGraphErrors(len(x_unsliced), x_unsliced, y_unsliced_pu, ex_unsliced, ey_unsliced_fake)
gr_sliced = r.TGraphErrors(len(x_sliced), x_sliced, y_sliced, ex_sliced, ey_sliced)
gr_sliced_pu = r.TGraphErrors(len(x_sliced), x_sliced, y_sliced_pu, ex_sliced, ey_sliced_pu)

r.gPad.SetTicky()
r.gPad.SetTickx()

fakeHist = r.TH1F('fakeHist',"", 5, 500, 3000)
fakeHist.SetTitle("PDF uncertainties; gen DY mass [GeV]; aceptence variation (%)")
fakeHist.SetMaximum(20)
fakeHist.Draw()

gr_unsliced.SetFillStyle(3345)
gr_unsliced.SetLineWidth(-802)
gr_unsliced.SetFillColor(r.kBlack)
gr_unsliced.SetLineColor(r.kBlack)
#gr_unsliced.Draw("same2")

gr_unsliced2.SetLineWidth(-802)
gr_unsliced2.SetLineColor(r.kBlack)
gr_unsliced2.SetMarkerColor(r.kBlack)
#gr_unsliced2.Draw("sameP")

gr_unsliced_pu.SetFillStyle(3354)
gr_unsliced_pu.SetLineWidth(-802)
gr_unsliced_pu.SetFillColor(r.kBlue)
gr_unsliced_pu.SetLineColor(r.kBlue)
gr_unsliced_pu.Draw("same2")

gr_unsliced_pu2.SetLineWidth(-802)
gr_unsliced_pu2.SetLineColor(r.kBlue)
gr_unsliced_pu2.SetMarkerColor(r.kBlue)
gr_unsliced_pu2.Draw("sameP")

gr_sliced.SetLineColor(r.kGreen)
gr_sliced.SetMarkerColor(r.kGreen)
#gr_sliced.Draw("sameLP")
gr_sliced_pu.SetLineColor(r.kRed)
gr_sliced_pu.SetMarkerColor(r.kRed)
gr_sliced_pu.Draw("sameLP")




position  = (0.15, 0.85 - 0.05*2, 0.55, 0.85)
histList = []
#histList.append((gr_unsliced, "wide mass bin without PU", 'f'))
histList.append((gr_unsliced_pu, "wide mass bin", 'f'))
#histList.append((gr_sliced, "narrow mass bin without PU", 'l'))
histList.append((gr_sliced_pu, "narrow mass bin", 'l'))

legends = tool.setMyLegend(position, histList)
legends.Draw("same")
c.Print('pdfSys_withUnc.pdf')

