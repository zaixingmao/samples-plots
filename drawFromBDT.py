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

defaultOrder = ['DY_Embed','DY_MC','ZLL','DY+ttLep', 'VV', 'QCD', 't#bar{t}', 't#bar{t}-ttLep', 'signal', 'Electroweak', 'singleT']
defaultOrder0M = ['DY_Embed','DY_MC','ZLL','DY+ttLep', 'VV', 'QCD', 't#bar{t}', 't#bar{t}-ttLep','WJets', 'signal', 'Electroweak', 'singleT']

defaultColor = {'VV': r.TColor.GetColor(222, 90,106),
                'singleT': r.TColor.GetColor(222, 90,106),
                'Electroweak': r.TColor.GetColor(222, 90,106),
                'DY_Embed': r.TColor.GetColor(248,206,104),
                'ZLL': r.TColor.GetColor(100,182,232),
                'DY_MC': r.TColor.GetColor(248,206,104),
                'DY+ttLep': r.TColor.GetColor(248,206,104),
                't#bar{t}': r.TColor.GetColor(155,152,204),
                't#bar{t}-ttLep': r.TColor.GetColor(155,152,204),
                'QCD': r.TColor.GetColor(250,202,255),
                'WJets': r.kGreen,

                }
sampleNameList= {}
sampleNameList['Electroweak'] = []
sampleNameList['tt'] = []

def getNames(key):
    dictionary = {'DY_Embed': 'Z#rightarrow#tau#tau',
                  'ZLL': 'Z#rightarrowll',
                  }
    if key in dictionary.keys():
        return dictionary[key]
    else:
        return key

def getBinWdith(var, bins):
    for i in range(len(bins)):
        if bins[i] > var:
            return (bins[i]-bins[i-1])
    return len(bins)
    return 1
def varFromName(tree, varName):
    varsDict = {
#                 'pt1': tree.pt1,
#                 'pt2': tree.pt2,
#                 'CSVJ1Pt': tree.CSVJ1Pt,
#                 'CSVJ2Pt': tree.CSVJ2Pt,
                'svMass': tree.svMass,
#                 'mJJ': tree.mJJ,
#                 'fMassKinFit': tree.fMassKinFit,
#                 'chi2KinFit2': tree.chi2KinFit2,
#                 'met': tree.met,
#                 'dRTauTau': tree.dRTauTau,
#                 'dRJJ': tree.dRJJ,
#                 'BDT': tree.BDT,
                }
    return varsDict[varName]

def varFromName1(tree, varName):
    varsDict = {'svMass': tree.svMass1,
#                 'BDT': tree.BDT,
                }
    return varsDict[varName]

def findBKGCategory(sampleName, mass):
    if 'DY_emb' in sampleName:
        return 'DY_embed'
    if 'ZLL' in sampleName:
        return 'ZLL'
    if 'dataOSRelax' in sampleName:
        return 'QCD'
    elif 'tt_emb' in sampleName:
        return 'tt_embed'
    elif 'tt' in sampleName:
        if sampleName not in sampleNameList['tt']:
            sampleNameList['tt'].append(sampleName)
        return 't#bar{t}'
    elif 'H2hh' in sampleName:
        if mass == '' and sampleName != 'H2hh260':
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
    elif "JetsToLNu" in sampleName:
        return 'WJets'
    else:
        if sampleName not in sampleNameList['Electroweak']:
            sampleNameList['Electroweak'].append(sampleName)
        return 'Electroweak'

def passCut(tree, iso):
    if tree.iso1_1 > iso or tree.iso2_1 > iso:
        return 0
    else:
        return 1

def setDY(histDict, dyScale, is0Tag = False):
    print ''
    print "DY_emebed: %.2f" %histDict['DY_embed'].Integral(0, histDict['DY_embed'].GetNbinsX()+1)
    print "tt_emebed: %.2f" %histDict['tt_embed'].Integral(0, histDict['tt_embed'].GetNbinsX()+1)
    if is0Tag:
        total = 1.0
    else:
        total = histDict['DY_embed'].Integral(0, histDict['DY_embed'].GetNbinsX()+1) - histDict['tt_embed'].Integral(0, histDict['tt_embed'].GetNbinsX()+1)
    histDict['DY_embed'].Scale(dyScale/total)
    histDict['tt_embed'].Scale(dyScale/total)
    histDict['DY_Embed'].Add(histDict['DY_embed'],1.0)
    histDict['DY_Embed'].Add(histDict['tt_embed'], -1.0)
    return  histDict

def buildStackFromDict(histDict, region, unit, option, drawWhichDY = 'DY_MC', category = '1M'):
    stack = r.THStack()
    if category == '0M':
        order = reversed(defaultOrder0M)
    else:
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

def buildHistDicts(bins0, bins1, bins2, name = ''):
    histDict0 = {}
    histDict1 = {}
    histDict2 = {}

    for ikey in defaultOrder0M:
        histDict0[ikey] = r.TH1F(ikey+'0M%s' %name, "", len(bins0)-1, bins0)
        histDict1[ikey] = r.TH1F(ikey+'1M%s' %name, "", len(bins1)-1, bins1)
        histDict2[ikey] = r.TH1F(ikey+'2M%s' %name, "", len(bins2)-1, bins2)
        if ikey != 'signal':
            histDict0[ikey].SetFillColor(defaultColor[ikey])
            histDict1[ikey].SetFillColor(defaultColor[ikey])
            histDict2[ikey].SetFillColor(defaultColor[ikey])

    histDict0['MCOSRelax'] = r.TH1F('MCOSRelax0M%s' %name, "", len(bins0)-1, bins0)
    histDict1['MCOSRelax'] = r.TH1F('MCOSRelax1M%s' %name, "", len(bins1)-1, bins1)
    histDict2['MCOSRelax'] = r.TH1F('MCOSRelax2M%s' %name, "", len(bins2)-1, bins2)

    histDict0['DY_embed'] = r.TH1F('DY_embed0M%s' %name, "", len(bins1)-1, bins0)
    histDict0['tt_embed'] = r.TH1F('tt_embed0M%s' %name, "", len(bins1)-1, bins0)
    histDict1['DY_embed'] = r.TH1F('DY_embed1M%s' %name, "", len(bins1)-1, bins1)
    histDict1['tt_embed'] = r.TH1F('tt_embed1M%s' %name, "", len(bins1)-1, bins1)
    histDict2['DY_embed'] = r.TH1F('DY_embed2M%s' %name, "", len(bins2)-1, bins2)
    histDict2['tt_embed'] = r.TH1F('tt_embed2M%s' %name, "", len(bins2)-1, bins2)

    histDict0['signal'].SetLineStyle(2)
    histDict0['signal'].SetLineWidth(2)
    histDict1['signal'].SetLineStyle(2)
    histDict1['signal'].SetLineWidth(2)
    histDict2['signal'].SetLineWidth(2)
    histDict2['signal'].SetLineStyle(2)

    return histDict0, histDict1, histDict2

def setLegend(position, histDict, observed, bins, signalName, drawWhichDY = 'DY_MC', category = '1M'):
    histList = []
    histList.append((observed, 'Observed'))
    keyList = defaultOrder
    if category == '0M':        
        keyList = defaultOrder0M
    nbins = len(bins)
    for ikey in keyList:
        if ikey == 'signal':
            if draw_cfg.addIntegrals:
                histList.append((histDict[ikey], '%s (%.2f)' %(signalName, histDict[ikey].Integral(0, nbins+1))))
            else:
                histList.append((histDict[ikey], '%s' %signalName))

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
            if draw_cfg.addIntegrals:
                histList.append((histDict[ikey], '%s (%.2f)' %(getNames(ikey), histDict[ikey].Integral(0, nbins+1))))
            else:
                histList.append((histDict[ikey], '%s' %getNames(ikey)))

    return tool.setMyLegend(position, histList)


def dontUnblind(tree, varName, bins):
    if tree.Category == '0M':
        return False
    if 'svMass' in varName:
        if 90 < tree.svMass < 150:
            return True
    elif 'mJJ' in varName:
        if 70 < tree.mJJ < 150:
            return True
    elif 'fMassKinFit' in varName:
        if tree.fMassKinFit < 400:
            return True
    elif 'BDT' in varName:
        if tree.BDT > bins[len(bins)-3]:
            return True
    elif 'chi2KinFit2' in varName:
        if tree.chi2KinFit2 <= 30:
            return True
    elif 'met' in varName:
        if tree.met <= 40:
            return True

#     elif 'pt1' in varName:
#         if tree.pt1 <= 75 and tree.Category == '2M':
#             return True
#     elif 'pt2' in varName:
#         if tree.pt2 <= 60 and tree.Category == '2M':
#             return True
#     elif 'dRJJ' in varName:
#         if 2 < tree.dRJJ < 3.5:
#             return True
#     elif 'dRTauTau' in varName:
#         if 2 < tree.dRTauTau < 3.5:
#             return True
    return False

def passCutWindow(tree):
    if (90 < tree.svMass < 150) and (70 < tree.mJJ < 150) and (tree.fMassKinFit > 10):
        return True
    else:
        return False

def draw(varName, bins0, bins1, bins2, unit, yMax0, yMax1, yMax2, option, iso, predictLocation, mass, massWindowCut, drawWhichDY, Lumi = 19.7):
    predictFile = r.TFile(predictLocation)    
    predictTree = predictFile.Get('eventTree')

    predictTotal = predictTree.GetEntries()
    signalName = ''
    histDict0M, histDict1M, histDict2M = buildHistDicts(bins0, bins1, bins2)
    histDict0M_plot, histDict1M_plot, histDict2M_plot = buildHistDicts(bins0, bins1, bins2, '_plot')
    observed0M = buildObserved('observed0M', bins0)
    observed1M = buildObserved('observed1M', bins1)
    observed2M = buildObserved('observed2M', bins2)
    observed0M_plot = buildObserved('observed0M_plot', bins0)
    observed1M_plot = buildObserved('observed1M_plot', bins1)
    observed2M_plot = buildObserved('observed2M_plot', bins2)

    for iEvent in range(predictTotal):
        tool.printProcessStatus(iEvent, predictTotal, 'Looping file [%s]' % (predictLocation))
        predictTree.GetEntry(iEvent)
        if massWindowCut and (not passCutWindow(predictTree)):
            continue
        sampleCat = findBKGCategory(predictTree.sampleName, mass)
        fillValue = varFromName(predictTree, varName)
        if predictTree.Category == '0M':
            #hack
            if fillValue >= bins0[len(bins0)-1]:
                fillValue = (bins0[len(bins0)-1] + bins0[len(bins0)-2])/2
        elif predictTree.Category == '1M':
            #hack
            if fillValue >= bins1[len(bins1)-1]:
                fillValue = (bins1[len(bins1)-1] + bins1[len(bins1)-2])/2
        elif predictTree.Category == '2M':
            #hack
            if fillValue >= bins2[len(bins2)-1]:
                fillValue = (bins2[len(bins2)-1] + bins2[len(bins2)-2])/2

        if sampleCat == 'Observed':
            if dontUnblind(predictTree, varName, bins2):
                continue
            if predictTree.Category == '0M':
                observed0M.Fill(fillValue)
                observed0M_plot.Fill(fillValue)

            if predictTree.Category == '1M':
                observed1M.Fill(fillValue)
                observed1M_plot.Fill(fillValue)

            elif predictTree.Category == '2M':
                observed2M.Fill(fillValue)
                observed2M_plot.Fill(fillValue)
            continue

        if sampleCat == None:
            continue
        if sampleCat == 'QCD' and ('OSRelax' in predictTree.sampleName):
            weight1 = 1.0
            weight2 = 1.0
        elif sampleCat == 'DY_embed':
            weight1 = predictTree.triggerEff*predictTree.decayModeWeight*predictTree.embeddedWeight
            weight2 = weight1
        elif sampleCat == 'tt_embed':
            xs = predictTree.xs
            weight1 = (xs/predictTree.initEvents)*predictTree.triggerEff*Lumi*predictTree.embeddedWeight*predictTree.PUWeight
            weight2 = weight1
        else:
            xs = predictTree.xs
            weight1 = (xs/predictTree.initEvents)*predictTree.triggerEff*predictTree.PUWeight*Lumi
            if sampleCat == 'signal':
                signalName = predictTree.sampleName
                weight1 = (xs/predictTree.initEvents)*predictTree.triggerEff*predictTree.PUWeight*Lumi*predictTree.decayModeWeight
            weight2 = weight1

        if predictTree.Category == '0M':
            histDict0M[sampleCat].Fill(fillValue, weight1)
            histDict0M_plot[sampleCat].Fill(fillValue, weight1)
            if (sampleCat == 't#bar{t}') and (predictTree.sampleName != 'tt'):
                histDict0M['t#bar{t}-ttLep'].Fill(fillValue, weight1)
                histDict0M_plot['t#bar{t}-ttLep'].Fill(fillValue, weight1) 
        elif predictTree.Category == '1M':
            histDict1M[sampleCat].Fill(fillValue, weight1)
            histDict1M_plot[sampleCat].Fill(fillValue, weight1)
            if (sampleCat == 't#bar{t}') and (predictTree.sampleName != 'tt'):
                histDict1M['t#bar{t}-ttLep'].Fill(fillValue, weight1)
                histDict1M_plot['t#bar{t}-ttLep'].Fill(fillValue, weight1)
        elif predictTree.Category == '2M':
            histDict2M[sampleCat].Fill(fillValue, weight2)
            histDict2M_plot[sampleCat].Fill(fillValue, weight2)
            if (sampleCat == 't#bar{t}') and (predictTree.sampleName != 'tt'):
                histDict2M['t#bar{t}-ttLep'].Fill(fillValue, weight2)
                histDict2M_plot['t#bar{t}-ttLep'].Fill(fillValue, weight2)
        if draw_cfg.method == 'method1' and sampleCat == 'DY_embed':
            if predictTree.NBTags > 1:
                histDict2M['DY+ttLep'].Fill(fillValue, weight2/0.9)
                histDict2M_plot['DY+ttLep'].Fill(fillValue, weight2/0.9)
            if predictTree.NBTags == 1:
                histDict1M['DY+ttLep'].Fill(fillValue, weight1/0.9)
                histDict1M_plot['DY+ttLep'].Fill(fillValue, weight1/0.9)

    #Set DY + tt_lep    
    if draw_cfg.method != 'method1' and 'method' in draw_cfg.method:
        dyWithTT1M_scale = predictFile.Get('DYwithTTScale_1M')
        dyWithTT2M_scale = predictFile.Get('DYwithTTScale_2M')
        dyWithTT1M = dyWithTT1M_scale.GetBinContent(1)
        dyWithTT2M = dyWithTT2M_scale.GetBinContent(1)
        histDict1M['DY+ttLep'].Add(histDict1M['DY_embed'], dyWithTT1M/histDict1M['DY_embed'].Integral(0, len(bins1)))
        histDict1M_plot['DY+ttLep'].Add(histDict1M_plot['DY_embed'], dyWithTT1M/histDict1M_plot['DY_embed'].Integral(0, len(bins1)))
        histDict2M['DY+ttLep'].Add(histDict2M['DY_embed'], dyWithTT2M/histDict2M['DY_embed'].Integral(0, len(bins2)))
        histDict2M_plot['DY+ttLep'].Add(histDict2M_plot['DY_embed'], dyWithTT2M/histDict2M_plot['DY_embed'].Integral(0, len(bins2)))

    #Set DY
    dy0M_scale = predictFile.Get('MC2Embed2Cat_0M')
    dy1M_scale = predictFile.Get('MC2Embed2Cat_1M')
    dy2M_scale = predictFile.Get('MC2Embed2Cat_2M')
    dyScale0M = dy0M_scale.GetBinContent(1)
    dyScale1M = dy1M_scale.GetBinContent(1)
    dyScale2M = dy2M_scale.GetBinContent(1)

    histDict0M_plot = setDY(histDict0M_plot, dyScale0M, True)
    histDict1M_plot = setDY(histDict1M_plot, dyScale1M)
    histDict2M_plot = setDY(histDict2M_plot, dyScale2M)
    histDict0M = setDY(histDict0M, dyScale0M, True)
    histDict1M = setDY(histDict1M, dyScale1M)
    histDict2M = setDY(histDict2M, dyScale2M)

    #Set QCD
    predictSF0MHist = predictFile.Get('L_to_T_SF_0M')

    predictSF1MHist_weight = predictFile.Get('L_to_T_1M')
    predictSF1MHist = predictFile.Get('L_to_T_SF_1M')

    predictSF2MHist_weight = predictFile.Get('L_to_T_2M')
    predictSF2MHist = predictFile.Get('L_to_T_SF_2M')

    SF_0M = predictSF0MHist.GetBinContent(1)
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
    histDict0M['VV'].Add(histDict0M['Electroweak'], histDict0M['singleT'])
    histDict1M['VV'].Add(histDict1M['Electroweak'], histDict1M['singleT'])
    histDict2M['VV'].Add(histDict2M['Electroweak'], histDict2M['singleT'])
    histDict0M_plot['VV'].Add(histDict0M_plot['Electroweak'], histDict0M_plot['singleT'])
    histDict1M_plot['VV'].Add(histDict1M_plot['Electroweak'], histDict1M_plot['singleT'])
    histDict2M_plot['VV'].Add(histDict2M_plot['Electroweak'], histDict2M_plot['singleT'])

    #Set ZLL
    ZLLWeightHist1M = predictFile.Get('ZLL_1M')
    ZLLWeightHist2M = predictFile.Get('ZLL_2M')
    ZLLScale1M = ZLLWeightHist1M.GetBinContent(1)
    ZLLScale2M = ZLLWeightHist2M.GetBinContent(1)
    tmpIntegral = histDict1M_plot['ZLL'].Integral(0, len(bins1))
    histDict1M_plot['ZLL'].Scale(ZLLScale1M/tmpIntegral)
    histDict1M['ZLL'].Scale(ZLLScale1M/tmpIntegral)
    tmpIntegral = histDict2M_plot['ZLL'].Integral(0, len(bins2))
    histDict2M_plot['ZLL'].Scale(ZLLScale2M/tmpIntegral)
    histDict2M['ZLL'].Scale(ZLLScale2M/tmpIntegral)


    print histDict1M['QCD'].Integral(0, len(bins1))
    print ''
    print SF_1M, SF_2M
    print weight_1M, weight_2M
    print (histDict1M['QCD'].Integral(0, len(bins1))-histDict1M['MCOSRelax'].Integral(0, len(bins1)))*SF_1M, (histDict2M['QCD'].Integral(0, len(bins2))-histDict2M['MCOSRelax'].Integral(0, len(bins2)))*SF_2M
    print histDict1M['QCD'].Integral(0, len(bins1))*weight_1M, histDict2M['QCD'].Integral(0, len(bins2))*weight_2M
    print '0M: ', histDict0M['QCD'].Integral(0, len(bins0)), histDict0M['MCOSRelax'].Integral(0, len(bins0))
    print '1M: ', histDict1M['QCD'].Integral(0, len(bins1)), histDict1M['MCOSRelax'].Integral(0, len(bins1))
    print '2M: ', histDict2M['QCD'].Integral(0, len(bins2)), histDict2M['MCOSRelax'].Integral(0, len(bins2))

    histDict0M['QCD'].Add(histDict0M['MCOSRelax'],-1.0)
    histDict0M['QCD'].Scale(SF_0M)
    histDict0M_plot['QCD'].Add(histDict0M_plot['MCOSRelax'],-1.0)
    histDict0M_plot['QCD'].Scale(SF_0M)

    histDict1M['QCD'].Add(histDict1M['MCOSRelax'],-1.0)
    histDict1M['QCD'].Scale(SF_1M)
    histDict2M['QCD'].Add(histDict2M['MCOSRelax'],-1.0)
    histDict2M['QCD'].Scale(SF_2M)

    histDict1M_plot['QCD'].Add(histDict1M_plot['MCOSRelax'],-1.0)
    histDict1M_plot['QCD'].Scale(SF_1M)
    histDict2M_plot['QCD'].Add(histDict2M_plot['MCOSRelax'],-1.0)
    histDict2M_plot['QCD'].Scale(SF_2M)

#     histDict1M['QCD'].Scale(weight_1M)
#     histDict2M['QCD'].Scale(weight_2M)
#     histDict1M_plot['QCD'].Scale(weight_1M)
#     histDict2M_plot['QCD'].Scale(weight_2M)

    bkgStack0M = buildStackFromDict(histDict0M_plot, '0M', unit, option, drawWhichDY, '0M')
    bkgStack1M = buildStackFromDict(histDict1M_plot, '1M', unit, option, drawWhichDY)
    bkgStack2M = buildStackFromDict(histDict2M_plot, '2M', unit, option, drawWhichDY)
    
    print ''
    position = (0.6, 0.9 - 0.06*6, 0.87, 0.9)

    if draw_cfg.addIntegrals:
        position = (0.47, 0.9 - 0.06*6, 0.87, 0.9)

    legend0M = setLegend(position, histDict0M, observed0M, bins0, signalName, drawWhichDY, '0M')
    legend1M = setLegend(position, histDict1M, observed1M, bins1, signalName, drawWhichDY)
    legend2M = setLegend(position, histDict2M, observed2M, bins2, signalName, drawWhichDY)

    psfile = '%s_%s_%s_%s.pdf' %(varName, mass, drawWhichDY, draw_cfg.method)
    c = r.TCanvas("c","Test", 600, 800)

    p0 = r.TPad("p0","p0",0.,1,1.,0.4)
    p0_r = r.TPad("p0_r","p0_r",0.,0.39,1.,0.06)
    p0.SetMargin(1, 1, 0, 1)
    p0_r.SetMargin(1, 1, 0.2, 1)
    p0.Draw()
    p0_r.Draw()
    p0.cd()
    r.gPad.SetTicky()
    bkgStack0M.SetMaximum(yMax0)
    bkgStack0M.Draw()
    observed0M_plot.Sumw2()
    observed0M_plot.Scale(1, option)
    observed0M_plot.Draw('PE same')
    legend0M.Draw('same')
    histDict0M_plot['signal'].Scale(1, option)
    histDict0M_plot['signal'].Draw('same')
    p0_r.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    p0_r.SetGridy(1)
    delta0M = buildDelta('delta0M', histDict0M, observed0M, bins0, varName, unit, drawWhichDY)
    delta0M.Draw()
    c.Update()
    c.Print('%s(' %psfile)
    c.Clear()

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
    c.Print('%s' %psfile)
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
    print 'data in 0M %i' %observed0M.Integral(0, len(bins0))
    print 'data in 1M %i' %observed1M.Integral(0, len(bins1))
    print 'data in 2M %i' %observed2M.Integral(0, len(bins2))


varsDict = draw_cfg.varsRange

masses = [str(int(x)) for x in range(260, 360, 10)]
masses = ['260']
binnings = {'260': array('d', [-0.628, -0.528, -0.42799999999999994, -0.32799999999999996, -0.22799999999999998, -0.128, -0.028000000000000025, 0.07200000000000006, 0.17200000000000007]),
            '270': array('d', [-0.782, -0.6819999999999999, -0.5800000000000001, -0.48, -0.38, -0.28, -0.17999999999999994, -0.07999999999999996, 0.020000000000000018, 0.1280000000000001, 0.22800000000000012] ),
            '280': array('d', [-0.768, -0.6679999999999999, -0.5660000000000001, -0.46599999999999997, -0.366, -0.266, -0.16600000000000004, -0.06599999999999995, 0.03400000000000003, 0.13400000000000012, 0.23400000000000012]),
            '290': array('d', [-0.714, -0.614, -0.514, -0.41400000000000003, -0.31399999999999995, -0.21399999999999997, -0.11399999999999999, -0.014000000000000012, 0.08600000000000008, 0.18799999999999994, 0.2879999999999999]),
            '300': array('d', [-0.6659999999999999, -0.5640000000000001, -0.46399999999999997, -0.364, -0.264, -0.16400000000000003, -0.06399999999999995, 0.03600000000000003, 0.13600000000000012, 0.23600000000000013]),
            '310': array('d', [-0.73, -0.63, -0.53, -0.42999999999999994, -0.32999999999999996, -0.22999999999999998, -0.13, -0.030000000000000027, 0.07000000000000006, 0.17599999999999993, 0.2759999999999999]),
            '320': array('d', [-0.744, -0.644, -0.544, -0.44399999999999995, -0.344, -0.244, -0.14400000000000002, -0.04399999999999993, 0.05600000000000005, 0.15799999999999992, 0.2579999999999999]),
            '330': array('d', [-0.64, -0.54, -0.43999999999999995, -0.33999999999999997, -0.24, -0.14, -0.040000000000000036, 0.06000000000000005, 0.16199999999999992, 0.2619999999999999]),
            '340': array('d', [-0.774, -0.6739999999999999, -0.5720000000000001, -0.472, -0.372, -0.272, -0.17199999999999993, -0.07199999999999995, 0.028000000000000025, 0.1280000000000001, 0.22800000000000012]),
            '350': array('d', [-0.768, -0.6679999999999999, -0.5660000000000001, -0.46599999999999997, -0.366, -0.266, -0.16600000000000004, -0.06599999999999995, 0.03400000000000003, 0.16599999999999993, 0.2659999999999999]),
}


for iMass in masses:
    predictLocation = '%s%s%s' %(draw_cfg.predictLocation_front, iMass, draw_cfg.predictLocation_back)
#     predictLocation = '%s%s' %(draw_cfg.predictLocation_front, draw_cfg.predictLocation_back)
    for ikey in varsDict:
        configs = varsDict[ikey]
        if ikey == 'BDT':
            bins0 = binnings[iMass]
            bins1 = binnings[iMass]
            bins2 = binnings[iMass]
        else:
            bins0 = configs[0]
            bins1 = configs[1]
            bins2 = configs[2]

        draw(varName = ikey,
             bins0 = bins0, 
             bins1 = bins1, 
             bins2 = bins2, 
             unit = configs[3], 
             yMax0 = configs[4],
             yMax1 = configs[5],
             yMax2 = configs[6],
             option = configs[7],
             iso = draw_cfg.iso, 
             predictLocation = predictLocation, 
             mass = iMass,
             massWindowCut = draw_cfg.massWindowCut,
             drawWhichDY = draw_cfg.drawWhichDY,
             Lumi = 19.7)

