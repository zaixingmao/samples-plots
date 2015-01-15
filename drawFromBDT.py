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

defaultOrder = ['DY_Embed','DY_MC','DY+ttLep', 'VV', 'QCD', 't#bar{t}', 't#bar{t}-ttLep', 'signal', 'Electroweak', 'singleT']

defaultColor = {'VV': r.TColor.GetColor(222, 90,106),
                'singleT': r.TColor.GetColor(222, 90,106),
                'Electroweak': r.TColor.GetColor(222, 90,106),
                'DY_Embed': r.TColor.GetColor(248,206,104),
                'DY_MC': r.TColor.GetColor(248,206,104),
                'DY+ttLep': r.TColor.GetColor(248,206,104),
                't#bar{t}': r.TColor.GetColor(155,152,204),
                't#bar{t}-ttLep': r.TColor.GetColor(155,152,204),
                'QCD': r.TColor.GetColor(250,202,255),
                }
sampleNameList= {}
sampleNameList['Electroweak'] = []
sampleNameList['tt'] = []
tt_semi_InitEvents = 12011428.

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
    if 'DY_emb' in sampleName:
        return 'DY_embed'
    if 'dataOSRelax' in sampleName:
        return 'QCD'
    elif 'tt_emb' in sampleName:
        return 'tt_embed'
    elif 'tt' in sampleName:
        if sampleName not in sampleNameList['tt']:
            sampleNameList['tt'].append(sampleName)
        return 't#bar{t}'
    elif 'H2hh' in sampleName:
        if mass == '' and sampleName != 'H2hh300':
            return None
        else:
            return 'signal'
    elif 'DY' in sampleName and 'JetsToLL' in sampleName:
        return 'DY_MC'
    elif 'MCOSRelax' in sampleName:
        return 'MCOSRelax'
    elif 'OSTight' in sampleName:
        return 'Observed'
    elif sampleName == 't' or sampleName == 'tbar':
        return 'singleT'
    else:
        if sampleName not in sampleNameList['Electroweak']:
            sampleNameList['Electroweak'].append(sampleName)
        return 'Electroweak'

def passCut(tree, iso):
    if tree.iso1_1 > iso or tree.iso2_1 > iso:
        return 0
    else:
        return 1

def setDY(histDict, dyScale):
    total = histDict['DY_embed'].Integral(0, histDict['DY_embed'].GetNbinsX()+1) - histDict['tt_embed'].Integral(0, histDict['tt_embed'].GetNbinsX()+1)
    histDict['DY_embed'].Scale(dyScale/total)
    histDict['tt_embed'].Scale(dyScale/total)
    histDict['DY_Embed'].Add(histDict['DY_embed'],1.0)
    histDict['DY_Embed'].Add(histDict['tt_embed'], -1.0)
    return  histDict

def buildStackFromDict(histDict, region, unit, option, drawWhichDY = 'DY_MC'):
    stack = r.THStack()
    order = reversed(defaultOrder)
    for ikey in order:
        if ikey == 'signal' or ikey == 'Electroweak' or ikey == 'singleT':
            continue
        if 'DY' in ikey and ikey != drawWhichDY:
            continue
        if drawWhichDY == 'DY+ttLep':
            if ikey == 't#bar{t}':
                continue
        else:
            if ikey == 't#bar{t}-ttLep':
                continue
        histDict[ikey].Scale(1, option)
        stack.Add(histDict[ikey])
    stack.SetTitle('CMS Preliminary 19.7 fb^{-1} at 8 TeV  %s; ; events / %s' %(region, unit))
    return stack

def buildDelta(deltaName, histDict, observed, bins, varName, unit, drawWhichDY):
    bkg = r.TH1F('bkg', '', len(bins)-1, bins)
    delta = r.TH1F(deltaName, deltaName, len(bins)-1, bins)
    for ikey in defaultOrder:
        if ikey == 'signal' or ikey == 'Electroweak' or ikey == 'singleT':
            continue
        if 'DY' in ikey and ikey != drawWhichDY:
            continue
        if drawWhichDY == 'DY+ttLep':
            if ikey == 't#bar{t}':
                continue
        else:
            if ikey == 't#bar{t}-ttLep':
                continue
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

    histDict1['MCOSRelax'] = r.TH1F('MCOSRelax1M%s' %name, "", len(bins1)-1, bins1)
    histDict2['MCOSRelax'] = r.TH1F('MCOSRelax2M%s' %name, "", len(bins2)-1, bins2)

    histDict1['DY_embed'] = r.TH1F('DY_embed1M%s' %name, "", len(bins1)-1, bins1)
    histDict1['tt_embed'] = r.TH1F('tt_embed1M%s' %name, "", len(bins1)-1, bins1)
    histDict2['DY_embed'] = r.TH1F('DY_embed2M%s' %name, "", len(bins2)-1, bins2)
    histDict2['tt_embed'] = r.TH1F('tt_embed2M%s' %name, "", len(bins2)-1, bins2)

    histDict1['signal'].SetLineStyle(2)
    histDict2['signal'].SetLineStyle(2)
    histDict1['signal'].SetLineWidth(2)
    histDict2['signal'].SetLineWidth(2)

    return histDict1, histDict2

def setLegend(position, histDict, observed, bins, signalName, drawWhichDY = 'DY_MC'):
    histList = []
    histList.append((observed, 'Observed'))
    keyList = defaultOrder
    nbins = len(bins)
    for ikey in keyList:
        if ikey == 'signal':
            histList.append((histDict[ikey], '%s (%.2f)' %(signalName, histDict[ikey].Integral(0, nbins+1))))
        else:
            if (ikey == 'Electroweak' or ikey == 'singleT'):
                continue
            if 'DY' in ikey and ikey != drawWhichDY:
                continue
            if drawWhichDY == 'DY+ttLep':
                if ikey == 't#bar{t}':
                    continue
            else:
                if ikey == 't#bar{t}-ttLep':
                    continue
            histList.append((histDict[ikey], '%s (%.2f)' %(ikey, histDict[ikey].Integral(0, nbins+1))))

    return tool.setMyLegend(position, histList)


def dontUnblind(tree, varName):
    if 'svMass' in varName:
        if 90 < tree.svMass < 150:
            return True
    elif 'BDT' in varName:
        if tree.BDT > 0:
            return True
    return False

def passCutWindow(tree):
    if (90 < tree.svMass < 150) and (70 < tree.mJJ < 150) and (tree.fMassKinFit > 10):
        return True
    else:
        return False

def draw(varName, bins1, bins2, unit, yMax1, yMax2, option, iso, predictLocation, mass, massWindowCut, drawWhichDY, Lumi = 19.7):
    predictFile = r.TFile(predictLocation)    
    predictTree = predictFile.Get('eventTree')

    predictTotal = predictTree.GetEntries()
    signalName = ''
    histDict1M, histDict2M = buildHistDicts(bins1, bins2)
    histDict1M_plot, histDict2M_plot = buildHistDicts(bins1, bins2, '_plot')
    observed1M = buildObserved('observed1M', bins1)
    observed2M = buildObserved('observed2M', bins2)
    observed1M_plot = buildObserved('observed1M_plot', bins1)
    observed2M_plot = buildObserved('observed2M_plot', bins2)

    for iEvent in range(predictTotal):
        tool.printProcessStatus(iEvent, predictTotal, 'Looping file [%s]' % (predictLocation))
        predictTree.GetEntry(iEvent)
        if massWindowCut and (not passCutWindow(predictTree)):
            continue
        sampleCat = findBKGCategory(predictTree.sampleName, mass)
        if sampleCat == 'Observed':
            if dontUnblind(predictTree, varName):
                continue
            if predictTree.NBTags == 1:
                observed1M.Fill(varFromName(predictTree, varName))
                observed1M_plot.Fill(varFromName(predictTree, varName))

            elif predictTree.NBTags > 1:
                observed2M.Fill(varFromName(predictTree, varName))
                observed2M_plot.Fill(varFromName(predictTree, varName))
            continue

        if sampleCat == None:
            continue
        if sampleCat == 'QCD' and ('OSRelax' in predictTree.sampleName):
            weight1 = 1.0
            weight2 = 1.0
        elif sampleCat == 'DY_embed':
            weight1 = predictTree.triggerEff
            weight2 = weight1
        elif sampleCat == 'tt_embed':
            xs = predictTree.xs
            weight1 = (xs/tt_semi_InitEvents)*predictTree.triggerEff*Lumi
            weight2 = weight1
        else:
            if sampleCat == 'signal':
                signalName = predictTree.sampleName
            xs = predictTree.xs
            weight1 = (xs/predictTree.initEvents)*predictTree.triggerEff*predictTree.PUWeight*Lumi
            weight2 = weight1
        if predictTree.Category == '1M':
            histDict1M[sampleCat].Fill(varFromName(predictTree, varName), weight1)
            histDict1M_plot[sampleCat].Fill(varFromName(predictTree, varName), weight1)
            if (sampleCat == 't#bar{t}') and (predictTree.sampleName != 'tt'):
                histDict1M['t#bar{t}-ttLep'].Fill(varFromName(predictTree, varName), weight1)
                histDict1M_plot['t#bar{t}-ttLep'].Fill(varFromName(predictTree, varName), weight1)
        elif predictTree.Category == '2M':
            histDict2M[sampleCat].Fill(varFromName(predictTree, varName), weight2)
            histDict2M_plot[sampleCat].Fill(varFromName(predictTree, varName), weight2)
            if (sampleCat == 't#bar{t}') and (predictTree.sampleName != 'tt'):
                histDict2M['t#bar{t}-ttLep'].Fill(varFromName(predictTree, varName), weight2)
                histDict2M_plot['t#bar{t}-ttLep'].Fill(varFromName(predictTree, varName), weight2)
        if draw_cfg.method == 'method1' and sampleCat == 'DY_embed':
            if predictTree.NBTags > 1:
                histDict2M['DY+ttLep'].Fill(varFromName(predictTree, varName), weight2/0.9)
                histDict2M_plot['DY+ttLep'].Fill(varFromName(predictTree, varName), weight2/0.9)
            if predictTree.NBTags == 1:
                histDict1M['DY+ttLep'].Fill(varFromName(predictTree, varName), weight1/0.9)
                histDict1M_plot['DY+ttLep'].Fill(varFromName(predictTree, varName), weight1/0.9)

    #Set DY + tt_lep    
    if draw_cfg.method != 'method1':
        dyWithTT1M_scale = predictFile.Get('DYwithTTScale_1M')
        dyWithTT2M_scale = predictFile.Get('DYwithTTScale_2M')
        dyWithTT1M = dyWithTT1M_scale.GetBinContent(1)
        dyWithTT2M = dyWithTT2M_scale.GetBinContent(1)
        histDict1M['DY+ttLep'].Add(histDict1M['DY_embed'], dyWithTT1M/histDict1M['DY_embed'].Integral(0, len(bins1)))
        histDict1M_plot['DY+ttLep'].Add(histDict1M_plot['DY_embed'], dyWithTT1M/histDict1M_plot['DY_embed'].Integral(0, len(bins1)))
        histDict2M['DY+ttLep'].Add(histDict2M['DY_embed'], dyWithTT2M/histDict2M['DY_embed'].Integral(0, len(bins2)))
        histDict2M_plot['DY+ttLep'].Add(histDict2M_plot['DY_embed'], dyWithTT2M/histDict2M_plot['DY_embed'].Integral(0, len(bins2)))

    #Set DY
    dy1M_scale = predictFile.Get('MC2Embed2Cat_1M')
    dy2M_scale = predictFile.Get('MC2Embed2Cat_2M')
    dyScale1M = dy1M_scale.GetBinContent(1)
    dyScale2M = dy2M_scale.GetBinContent(1)

    histDict1M_plot = setDY(histDict1M_plot, dyScale1M)
    histDict2M_plot = setDY(histDict2M_plot, dyScale2M)
    histDict1M = setDY(histDict1M, dyScale1M)
    histDict2M = setDY(histDict2M, dyScale2M)

    #Set QCD
    predictSF1MHist_weight = predictFile.Get('L_to_T_1M')
    predictSF1MHist = predictFile.Get('L_to_T_SF_1M')

    predictSF2MHist_weight = predictFile.Get('L_to_T_2M')
    predictSF2MHist = predictFile.Get('L_to_T_SF_2M')

    SF_1M = predictSF1MHist.GetBinContent(1)
    SF_2M = predictSF2MHist.GetBinContent(1)
    weight_1M = predictSF1MHist_weight.GetBinContent(1)
    weight_2M = predictSF2MHist_weight.GetBinContent(1)

    #Set VV
    electroweakWeightHist1M = predictFile.Get('VV_1M')
    electroweakWeightHist2M = predictFile.Get('VV_2M')
    eScale1M = electroweakWeightHist1M.GetBinContent(1)
    eScale2M = electroweakWeightHist2M.GetBinContent(1)

    singleTWeightHist1M = predictFile.Get('singleT_1M')
    singleTWeightHist2M = predictFile.Get('singleT_2M')
    sScale1M = singleTWeightHist1M.GetBinContent(1)
    sScale2M = singleTWeightHist2M.GetBinContent(1)

    tmpElectroIntegral = histDict1M_plot['Electroweak'].Integral(0, len(bins1))
    tmpSingleTIntegral = histDict1M_plot['singleT'].Integral(0, len(bins1))
    histDict1M_plot['Electroweak'].Scale(eScale1M/tmpElectroIntegral)
    histDict1M['Electroweak'].Scale(eScale1M/tmpElectroIntegral)
    histDict1M_plot['singleT'].Scale(sScale1M/tmpSingleTIntegral)
    histDict1M['singleT'].Scale(sScale1M/tmpSingleTIntegral)
    tmpElectroIntegral = histDict2M_plot['Electroweak'].Integral(0, len(bins2))
    tmpSingleTIntegral = histDict2M_plot['singleT'].Integral(0, len(bins2))
    histDict2M_plot['Electroweak'].Scale(eScale2M/tmpElectroIntegral)
    histDict2M_plot['singleT'].Scale(sScale2M/tmpSingleTIntegral)
    histDict2M['Electroweak'].Scale(eScale2M/tmpElectroIntegral)
    histDict2M['singleT'].Scale(sScale2M/tmpSingleTIntegral)
    histDict1M['VV'].Add(histDict1M['Electroweak'], histDict1M['singleT'])
    histDict2M['VV'].Add(histDict2M['Electroweak'], histDict2M['singleT'])
    histDict1M_plot['VV'].Add(histDict1M_plot['Electroweak'], histDict1M_plot['singleT'])
    histDict2M_plot['VV'].Add(histDict2M_plot['Electroweak'], histDict2M_plot['singleT'])

    print histDict1M['QCD'].Integral(0, len(bins1))
    print ''
    print SF_1M, SF_2M
    print weight_1M, weight_2M
    print (histDict1M['QCD'].Integral(0, len(bins1))-histDict1M['MCOSRelax'].Integral(0, len(bins1)))*SF_1M, (histDict2M['QCD'].Integral(0, len(bins2))-histDict2M['MCOSRelax'].Integral(0, len(bins2)))*SF_2M
    print histDict1M['QCD'].Integral(0, len(bins1))*weight_1M, histDict2M['QCD'].Integral(0, len(bins2))*weight_2M
    print '1M: ', histDict1M['QCD'].Integral(0, len(bins1)), histDict1M['MCOSRelax'].Integral(0, len(bins1))
    print '2M: ', histDict2M['QCD'].Integral(0, len(bins2)), histDict2M['MCOSRelax'].Integral(0, len(bins2))

#     histDict1M['QCD'].Add(histDict1M['MCOSRelax'],-1.0)
#     histDict1M['QCD'].Scale(SF_1M)
#     histDict2M['QCD'].Add(histDict2M['MCOSRelax'],-1.0)
#     histDict2M['QCD'].Scale(SF_2M)

#     histDict1M_plot['QCD'].Add(histDict1M_plot['MCOSRelax'],-1.0)
#     histDict1M_plot['QCD'].Scale(SF_1M)
#     histDict2M_plot['QCD'].Add(histDict2M_plot['MCOSRelax'],-1.0)
#     histDict2M_plot['QCD'].Scale(SF_2M)

    histDict1M['QCD'].Scale(weight_1M)
    histDict2M['QCD'].Scale(weight_2M)
    histDict1M_plot['QCD'].Scale(weight_1M)
    histDict2M_plot['QCD'].Scale(weight_2M)

    bkgStack1M = buildStackFromDict(histDict1M_plot, '1M', unit, option, drawWhichDY)
    bkgStack2M = buildStackFromDict(histDict2M_plot, '2M', unit, option, drawWhichDY)
    
    print ''

    position = (0.47, 0.9 - 0.06*6, 0.87, 0.9)

    legend1M = setLegend(position, histDict1M, observed1M, bins1, signalName, drawWhichDY)
    legend2M = setLegend(position, histDict2M, observed2M, bins2, signalName, drawWhichDY)

    psfile = '%s_%s_%s_%s_%s.pdf' %(varName, mass, iso, drawWhichDY, draw_cfg.method)
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
    delta1M = buildDelta('delta1M', histDict1M, observed1M, bins1, varName, unit, drawWhichDY)
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
    delta2M = buildDelta('delta2M', histDict2M, observed2M, bins2, varName, unit, drawWhichDY)
    delta2M.Draw()    
    c.Print('%s)' %psfile)
    print "Plot saved at %s" %(psfile)
    c.Close()
    print sampleNameList
varsDict = draw_cfg.varsRange

scaleWeight_1M = 1.0
scaleWeight_2M = 1.0

# masses = [str(int(x)) for x in range(260, 360, 10)]

masses = ['']

for iMass in masses:
    predictLocation = '%s%s%s' %(draw_cfg.predictLocation_front, iMass, draw_cfg.predictLocation_back)
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
             mass = iMass,
             massWindowCut = draw_cfg.massWindowCut,
             drawWhichDY = draw_cfg.drawWhichDY,
             Lumi = 19.7)

