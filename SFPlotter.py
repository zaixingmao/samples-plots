#!/usr/bin/env python
from array import array


import ROOT as r



points = [                    (0.136, 0.074),
                    (0.319, 0.381),
                    (0.359, 0.419),
                    (0.811, 0.641),
                    (0, 0),
                    (0, 0),
                    (0, 0),
                    (0.836, 1.379),
                    (0.184, 0.503),
                    (0.225, 0.400),
                    (0, 0),]

bins2 = []
nBins = 10
for i in range(nBins+1):
    bins2.append(-1.0 + (2*i+0.0)/nBins)
varBins = array('d', bins2)
tmpHist = r.TH1F("tmp", '', len(varBins)-1, varBins)

i = 1
for iP, iE in points:
    tmpHist.SetBinContent(i, iP)
    tmpHist.SetBinError(i, iE)
    i+=1

psfile = 'sf.pdf'
c = r.TCanvas("c","Test", 800, 600)
tmpHist.Draw('E')
c.Print('%s' %psfile)

