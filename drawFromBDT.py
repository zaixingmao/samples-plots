#!/usr/bin/env python

import ROOT as r
import tool
from operator import itemgetter
import os
from cfg import enVars
import varsList
import optparse
import math
from array import array
import numpy
import random
from cfg import draw_BDT as draw_cfg
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

defaultOrder = ['DY', 'Electroweak', 'QCD', 't#bar{t}', 'signal']

defaultColor = {'Electroweak': r.TColor.GetColor(222, 90,106),
                'DY': r.TColor.GetColor(248,206,104),
                't#bar{t}': r.TColor.GetColor(155,152,204),
                'QCD': r.TColor.GetColor(250,202,255),
                }
sampleNameList= {}
sampleNameList['Electroweak'] = []

def getBinWdith(var, bins):
    for i in range(len(bins)):
        if bins[i] > var:
            return (bins[i]-bins[i-1])
    return len(bins)
    return 1
def varFromName(tree, varName):
    varsDict = {'svMass': tree.svMass,
                'BDT': tree.BDT,
                }
    return varsDict[varName]

def varFromName1(tree, varName):
    varsDict = {'svMass': tree.svMass1,
                'BDT': tree.BDT,
                }
    return varsDict[varName]

def findBKGCategory(sampleName, mass):
    if 'JetsToLNu' in sampleName:
        return 'QCD'
    if 'data' in sampleName:
        return 'QCD'
    elif 'DY' in sampleName:
        return 'DY'
    elif 'tt' in sampleName:
        return 't#bar{t}'
    elif 'H2hh' in sampleName:
        if mass == '' and sampleName != 'H2hh350':
            return None
        else:
            return 'signal'
    else:
        if sampleName not in sampleNameList['Electroweak']:
            sampleNameList['Electroweak'].append(sampleName)
        return 'Electroweak'
    
def passCut(tree, iso):
    if tree.iso1_1 > iso or tree.iso2_1 > iso:
        return 0
    else:
        return 1

def buildStackFromDict(histDict, region, unit, option):
    stack = r.THStack()
    order = reversed(defaultOrder)
    for ikey in order:
        if ikey != 'signal':
            histDict[ikey].Scale(1, option)
            stack.Add(histDict[ikey])
    stack.SetTitle('CMS Preliminary 19.7 fb^{-1} at 8 TeV  %s; ; events / %s' %(region, unit))
    return stack

def buildDelta(deltaName, histDict, observed, bins, varName, unit):
    bkg = r.TH1F('bkg', '', len(bins)-1, bins)
    delta = r.TH1F(deltaName, deltaName, len(bins)-1, bins)
    for ikey in defaultOrder:
        if ikey != 'signal':
            bkg.Add(histDict[ikey])
    delta.Add(observed)
    delta.Sumw2()
    bkg.Sumw2()
    delta.Divide(bkg)
    delta.SetTitle('; %s %s; ' %(varName, unit))
    delta.SetMaximum(1.5)
    delta.SetMinimum(0.5)
    delta.GetXaxis().SetLabelSize(0.07)
    delta.GetXaxis().SetTitleSize(0.07)
    delta.GetYaxis().SetLabelSize(0.07)
    delta.GetYaxis().SetNdivisions(5,5,0)

    return delta

def buildObserved(name, bins):
    observed = r.TH1F(name, '', len(bins)-1, bins)
    observed.SetMarkerStyle(8)
    observed.SetMarkerSize(0.9)
    return observed

def buildHistDicts(bins1, bins2, name = ''):
    histDict1 = {}
    histDict2 = {}
    for ikey in defaultOrder:
        histDict1[ikey] = r.TH1F(ikey+'1M%s' %name, "", len(bins1)-1, bins1)
        histDict2[ikey] = r.TH1F(ikey+'2M%s' %name, "", len(bins2)-1, bins2)
        if ikey != 'signal':
            histDict1[ikey].SetFillColor(defaultColor[ikey])
            histDict2[ikey].SetFillColor(defaultColor[ikey])

    histDict1['signal'].SetLineStyle(2)
    histDict2['signal'].SetLineStyle(2)
    histDict1['signal'].SetLineWidth(2)
    histDict2['signal'].SetLineWidth(2)

    return histDict1, histDict2

def setLegend(position, histDict, observed, bins, signalName):
    histList = []
    histList.append((observed, 'Observed'))
    keyList = defaultOrder
    nbins = len(bins)
    for ikey in keyList:
        if ikey == 'signal':
            histList.append((histDict[ikey], '%s (%.2f)' %(signalName, histDict[ikey].Integral(0, nbins+1))))
        else:
            histList.append((histDict[ikey], '%s (%.2f)' %(ikey, histDict[ikey].Integral(0, nbins+1))))

    return tool.setMyLegend(position, histList)


def dontUnblind(tree, varName):
    if 'svMass' in varName:
        if 90 < tree.svMass1 < 150:
            return True
    elif 'BDT' in varName:
        if tree.BDT > 0:
            return True
    return False
    

def draw(varName, bins1, bins2, unit, yMax1, yMax2, option, iso, predictLocation, observedLocation, mass, Lumi = 19.7):
    predictFile = r.TFile(predictLocation)
    observedFile = r.TFile(observedLocation)
    
    predictTree = predictFile.Get('eventTree')
    observedTree = observedFile.Get('eventTree')

    predictSF1MHist = predictFile.Get('L_to_T_1M')
    predictSF2MHist = predictFile.Get('L_to_T_2M')

    SF_1M = predictSF1MHist.GetBinContent(1)
    SF_2M = predictSF2MHist.GetBinContent(1)
    predictTotal = predictTree.GetEntries()
    observedTotal = observedTree.GetEntries()
    signalName = ''
    histDict1M, histDict2M = buildHistDicts(bins1, bins2)
    histDict1M_plot, histDict2M_plot = buildHistDicts(bins1, bins2, '_plot')

    for iEvent in range(predictTotal):
        tool.printProcessStatus(iEvent, predictTotal, 'Looping file [%s]' % (predictLocation))
        predictTree.GetEntry(iEvent)
        sampleCat = findBKGCategory(predictTree.sampleName, mass)
        if sampleCat == None:
            continue
        if sampleCat == 'QCD' and 'OSRelax' in predictTree.sampleName:
            weight1 = SF_1M
            weight2 = SF_2M
        else:
            if sampleCat == 'signal':
                signalName = predictTree.sampleName
            xs = predictTree.xs
            weight1 = (xs/predictTree.initEvents)*predictTree.triggerEff*predictTree.PUWeight*Lumi
            weight2 = weight1
        if predictTree.NBTags == 1:
            histDict1M[sampleCat].Fill(varFromName(predictTree, varName), weight1)
            histDict1M_plot[sampleCat].Fill(varFromName(predictTree, varName), weight1)
        elif predictTree.NBTags > 1:
            histDict2M[sampleCat].Fill(varFromName(predictTree, varName), weight2)
            histDict2M_plot[sampleCat].Fill(varFromName(predictTree, varName), weight2)
            
    bkgStack1M = buildStackFromDict(histDict1M_plot, '1M', unit, option)
    bkgStack2M = buildStackFromDict(histDict2M_plot, '2M', unit, option)
    
    observed1M = buildObserved('observed1M', bins1)
    observed2M = buildObserved('observed2M', bins2)
    observed1M_plot = buildObserved('observed1M_plot', bins1)
    observed2M_plot = buildObserved('observed2M_plot', bins2)

    print ''
    for iEvent in range(observedTotal):
        tool.printProcessStatus(iEvent, observedTotal, 'Looping file [%s]' % (observedLocation))
        observedTree.GetEntry(iEvent)
        if dontUnblind(observedTree, varName):
            continue
        if not passCut(observedTree, iso):
            continue
        if observedTree.NBTags == 1:
            observed1M.Fill(varFromName1(observedTree, varName))
            observed1M_plot.Fill(varFromName1(observedTree, varName))

        elif observedTree.NBTags > 1:
            observed2M.Fill(varFromName1(observedTree, varName))
            observed2M_plot.Fill(varFromName1(observedTree, varName))
    print ''
    position = (0.47, 0.9 - 0.06*6, 0.87, 0.9)

    legend1M = setLegend(position, histDict1M, observed1M, bins1, signalName)
    legend2M = setLegend(position, histDict2M, observed2M, bins2, signalName)

    psfile = '%s_%s_%s.pdf' %(varName, mass, iso)
    c = r.TCanvas("c","Test", 600, 800)

    p1 = r.TPad("p1","p1",0.,1,1.,0.4)
    p1_r = r.TPad("p1_r","p1_r",0.,0.39,1.,0.06)
    p1.SetMargin(1, 1, 0, 1)
    p1_r.SetMargin(1, 1, 0.2, 1)
    p1.Draw()
    p1_r.Draw()
    p1.cd()
    r.gPad.SetTicky()
    bkgStack1M.SetMaximum(yMax1)
    bkgStack1M.Draw()
    observed1M_plot.Sumw2()
    observed1M_plot.Scale(1, option)
    observed1M_plot.Draw('PE same')
    legend1M.Draw('same')
    histDict1M_plot['signal'].Scale(1, option)
    histDict1M_plot['signal'].Draw('same')
    p1_r.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    p1_r.SetGridy(1)
    delta1M = buildDelta('delta1M', histDict1M, observed1M, bins1, varName, unit)
    delta1M.Draw()
    c.Update()
    c.Print('%s(' %psfile)
    c.Clear()
    p2 = r.TPad("p2","p2",0.,1,1.,0.4)
    p2_r = r.TPad("p2_r","p2_r",0.,0.39,1.,0.06)
    p2.SetMargin(1, 1, 0, 1)
    p2_r.SetMargin(1, 1, 0.2, 0.1)
    p2.Draw()
    p2_r.Draw()
    p2.cd()
    r.gPad.SetTicky()
    bkgStack2M.SetMaximum(yMax2)
    bkgStack2M.Draw()
    observed2M_plot.Sumw2()
    observed2M_plot.Scale(1, option)
    observed2M_plot.Draw('PE same')
    legend2M.Draw('same')
    histDict2M_plot['signal'].Scale(1, option)
    histDict2M_plot['signal'].Draw('same')
    p2_r.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    p2_r.SetGridy(1)
    delta2M = buildDelta('delta2M', histDict2M, observed2M, bins2, varName, unit)
    delta2M.Draw()    
    c.Print('%s)' %psfile)
    print "Plot saved at %s" %(psfile)
    c.Close()
    print sampleNameList

varsDict = draw_cfg.varsRange

scaleWeight_1M = 1.0
scaleWeight_2M = 1.0

masses = [str(int(x)) for x in range(260, 360, 10)]

# masses = ['']

for iMass in masses:
    predictLocation = '%s%s%s' %(draw_cfg.predictLocation_front, iMass, draw_cfg.predictLocation_back)
    observedLocation = '%s%s%s' %(draw_cfg.observedLocation_front, iMass, draw_cfg.observedLocation_back)
    for ikey in varsDict:
        configs = varsDict[ikey]
        draw(varName = ikey,
             bins1 = configs[0], 
             bins2 = configs[1], 
             unit = configs[2], 
             yMax1 = configs[3],
             yMax2 = configs[4],
             option = configs[5],
             iso = draw_cfg.iso, 
             predictLocation = predictLocation, 
             observedLocation = observedLocation, 
             mass = iMass,
             Lumi = 19.7)

