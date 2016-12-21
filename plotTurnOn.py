#!/usr/bin/env python

import ROOT as r
import plots_cfg
import tool
import optparse
import array
import math
import cutSampleTools
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def ratioHistogram( num, den, relErrMax=0.25) :
    def groupR(group) :
        N,D = [float(sum(hist.GetBinContent(i) for i in group)) for hist in [num,den]]
        return N/D if D else 0

    def groupErr(group) :
        N,D = [float(sum(hist.GetBinContent(i) for i in group)) for hist in [num,den]]
        ne2,de2 = [sum(hist.GetBinError(i)**2 for i in group) for hist in [num,den]]
        return math.sqrt( ne2/N**2 + de2/D**2 ) * N/D if N and D else 0

    def regroup(groups) :
        err,iG = max( (groupErr(g),groups.index(g)) for g in groups )
        if err < relErrMax or len(groups)<3 : return groups
        iH = max( [iG-1,iG+1], key = lambda i: groupErr(groups[i]) if 0<=i<len(groups) else -1 )
        iLo,iHi = sorted([iG,iH])
        return regroup(groups[:iLo] + [groups[iLo]+groups[iHi]] + groups[iHi+1:])

    try :
        groups = regroup( [(i,) for i in range(1,1+num.GetNbinsX())] )
    except :
        print 'Ratio failed:', num.GetName()
        groups = [(i,) for i in range(1,1+num.GetNbinsX()) ]
    ratio = r.TH1D("ratio"+num.GetName()+den.GetName(),"",len(groups), array.array('d', [num.GetBinLowEdge(min(g)) for g in groups ] + [num.GetXaxis().GetBinUpEdge(num.GetNbinsX())]) )
    for i,g in enumerate(groups) :
        ratio.SetBinContent(i+1,groupR(g))
        ratio.SetBinError(i+1,groupErr(g))
    return ratio


def dynamicBinning(iSample, Range = [46, 400], leg = "e"):
    file = r.TFile(iSample)   
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    hist_barrel = r.TH1F("hist_barrel", "", Range[1]-Range[0], Range[0], Range[1])
    hist_middle = r.TH1F("hist_middle", "", Range[1]-Range[0], Range[0], Range[1])
    hist_endcap = r.TH1F("hist_endcap", "", Range[1]-Range[0], Range[0], Range[1])
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'calculating dynamic binning %s' %(iSample), iEntry-1)
        if abs(tree.eEta) >= 2.1:
            continue
        if abs(tree.mEta) >= 2.1:
            continue
        if tree.q_1 == tree.q_2:
            continue
        if leg == "e":
            if abs(tree.eEta) >= 1.479:
                hist_endcap.Fill(tree.ePt)#, cutSampleTools.getPUWeight(tree.nTruePU))
            else:
                hist_barrel.Fill(tree.ePt)#, cutSampleTools.getPUWeight(tree.nTruePU))
        elif leg == 'mu':
            if abs(tree.mEta) >= 1.24:
                hist_endcap.Fill(tree.mPt)
            elif abs(tree.mEta) >= 0.8:
                hist_middle.Fill(tree.mPt)
            else:
                hist_barrel.Fill(tree.mPt)

    total_barrel = hist_barrel.Integral(1, Range[1]-Range[0])
    total_middle = hist_middle.Integral(1, Range[1]-Range[0])
    total_endcap = hist_endcap.Integral(1, Range[1]-Range[0])

    print total_barrel, total_middle, total_endcap
    mid_barrel = 0
    mid_middle = 0
    mid_endcap = 0
    #find half point
    for i in range(Range[1]-Range[0]):
        if total_barrel*0.48 <= hist_barrel.Integral(1, i+1) <= total_barrel*0.52:
            mid_barrel = i + Range[0]
        if total_middle*0.48 <= hist_middle.Integral(1, i+1) <= total_middle*0.52:
            mid_middle = i + Range[0]
        if total_endcap*0.48 <= hist_endcap.Integral(1, i+1) <= total_endcap*0.52:
            mid_endcap = i + Range[0]
    bins_barrel = array.array('d', [Range[0], mid_barrel, Range[1]])
    bins_middle = array.array('d', [Range[0], mid_middle, Range[1]])
    bins_endcap = array.array('d', [Range[0], mid_endcap, Range[1]])
    print bins_barrel, bins_middle, bins_endcap

    if leg == 'e':
        return bins_barrel, bins_endcap
    else:
        return bins_barrel, bins_middle, bins_endcap


def buildDelta(data_pass, data_all, bkg_pass, bkg_all, bins, varName, unit, relErrMax):
    dataHist = r.TH1F("dataHist_%s" %varName, "", len(bins)-1, bins)
    dataHist.Add(data_pass)
    dataHist.Divide(data_all)
    bkgHist = r.TH1F("bkgHist_%s" %varName, "", len(bins)-1, bins)
    bkgHist.Add(bkg_pass)
    bkgHist.Divide(bkg_all)

    delta = ratioHistogram(num = dataHist, den = bkgHist, relErrMax=relErrMax)
    delta.SetTitle('; %s; data/MC' %(varName))
    delta.SetMaximum(1.5)
    delta.SetMinimum(0.5)
    delta.GetXaxis().SetLabelSize(0.1)
    delta.GetXaxis().SetTitleSize(0.1)
    delta.GetYaxis().SetLabelSize(0.1)
    delta.GetYaxis().SetNdivisions(5,5,0)
    delta.GetYaxis().SetTitleSize(0.1)
    delta.GetYaxis().SetTitleOffset(0.43)
    delta.GetYaxis().CenterTitle()
    return delta

def loop_one_sample(iSample, varName, hist1, hist2, category = 'mt', isData = False, region = 'barrel', triggerLeg = 'e'):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    hist1.Sumw2()
    hist2.Sumw2()
    eventCountWeighted = file.Get('eventCountWeighted')
#     if not isData and nEntries > 50000:
#         nEntries = 50000
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        weight = 1.0

        if not isData:
            puweight = cutSampleTools.getPUWeight(tree.nTruePU)
            sumWeights = eventCountWeighted.GetBinContent(1)
            weight = 10000*tree.xs*tree.genEventWeight*puweight/(sumWeights+0.0)

        if category == 'mt':
            if tree.mPt <= 25:
                continue
            if not (tree.singleMu24Pass and tree.mIsoMu24):
                continue
        elif category == 'et':
            if tree.ePt <= 33:
                continue
            if isData:
                if not (tree.singleETightPass and tree.eSingleEleTight):
                    continue
            else:
                if not (tree.singleEPass and tree.eSingleEle):
                    continue
        elif category == 'ee':
            if isData:
                if 'e2' in varName:
                    if tree.singleETightPass and tree.e1SingleEleTight:
                        if tree.e1Pt <= 34:
                            continue
                    else:
                        continue
                if 'e1' in varName:
                    if tree.singleETightPass and tree.e2SingleEleTight:
                        if tree.e2Pt <= 34:
                            continue
                    else:
                        continue
            else:
                if 'e2' in varName:    
                    if tree.singleEPass and tree.e1SingleEle:
                        if tree.e1Pt <= 34:
                            continue
                    else:
                        continue
                if 'e1' in varName:    
                    if tree.singleEPass and tree.e2SingleEle:             
                        if tree.e2Pt <= 34:
                            continue
                    else:
                        continue
        elif category == 'em':
            if abs(tree.eEta) >= 2.1:
                continue
            if abs(tree.mEta) >= 2.1:
                continue
            if triggerLeg == 'e':
                if tree.mPt <= 24:
                    continue
                if region == 'barrel' and abs(tree.eEta) > 1.479:
                    continue
                elif region == 'endcap' and abs(tree.eEta) <= 1.479:
                    continue
            else:
                if region == 'barrel' and abs(tree.mEta) > 0.8:
                    continue
                elif region == 'middle' and not (0.8 < abs(tree.mEta) < 1.24):
                    continue
                elif region == 'endcap' and not (1.24 < abs(tree.mEta) < 2.4):
                    continue
                if tree.ePt <= 28:
                    continue

        if tree.q_1 == tree.q_2:
            continue

        value = getattr(tree, varName)

        hist1.Fill(value)
        if category == 'mt':
            if tree.muTauPass and tree.mMuTau and tree.mMuTauOverlap and tree.tTau20AgainstMuon and tree.tTauOverlapMu:
                hist2.Fill(value)
        elif category == 'et':
            if isData:
                if tree.eTau_WPLoosePass and tree.eEle22Loose and tree.eOverlapEle22Loose and tree.tTau20 and tree.tTauOverlapEleLoose:
                    hist2.Fill(value)
            else:
                if tree.eTauPass and tree.eEle22 and tree.eOverlapEle22 and tree.tTau20 and tree.tTauOverlapEle:
                    hist2.Fill(value)
        elif category == 'ee':
            if isData:
                if tree.doubleE_WPLoosePass:
                    if (tree.e1DoubleE_WPLooseLeg1 and tree.e2DoubleE_WPLooseLeg2) or (tree.e1DoubleE_WPLooseLeg2 and tree.e2DoubleE_WPLooseLeg1):                
                        if tree.e2Pt > 25 and tree.e1Pt > 25:
                            hist2.Fill(value)
            else:
                if tree.doubleE_WP75Pass:
                    if (tree.e1DoubleE_WP75Leg1 and tree.e2DoubleE_WP75Leg2) or (tree.e1DoubleE_WP75Leg2 and tree.e2DoubleE_WP75Leg1):                
                        if tree.e2Pt > 25 and tree.e1Pt > 25:
                            hist2.Fill(value)
        elif category == 'em':
            if triggerLeg == 'e':
                if tree.singleE27_2p1_WPTightPass and tree.eSingleEle27_2p1_WPTight:
                    hist2.Fill(value)
            elif triggerLeg == 'mu':
                if tree.singleMu24Pass and tree.mIsoMu24:
                    hist2.Fill(value)

    print ''

def setFunc(sample):
    range = [24, 200]
#     if sample == "DY":
#         range = [30, 200]

    func = r.TF1(sample, "0.5*[0]*(1+TMath::Erf([2]*(x - [1])/TMath::Sqrt(2)))", range[0], range[1])
    func.SetParName(0, "plateau")
    func.SetParName(1, "halfpoint")
    func.SetParName(2, "slope")
    func.SetParameter(0, 0.9)
    func.SetParameter(1, 18)
    func.SetParameter(2, 0.04)

    return func

def getColor(sample):
    if sample == 'DY':
        return r.kBlue
    if sample == 'ttbar':
        return 38
    if sample == 'ttbar+DY+singleTop':
        return 30
    if sample == 'DY+singleTop':
        return 42
    if sample == 'ZPrime2000':
        return r.kRed
    if sample == 'ZPrime5000':
        return r.kCyan
    if sample == 'ZPrime3500':
        return r.kMagenta
    if sample == 'ZPrime1500':
        return r.kGreen
    if sample == 'ZPrime1000':
        return r.kOrange

def calRatio(num, num_err, denom, denom_err):
    ratio = num/denom
    error = ratio*math.sqrt(pow(num_err/num, 2) + pow(denom_err/denom, 2))
    return ratio, error

def calRatio2(num1, num1_err, num2, num2_err, denom1, denom1_err, denom2, denom2_err):
    ratio = (num1+num2)/(denom1+denom2)
    error = ratio*math.sqrt(pow(num1_err/(num1+num2), 2) + pow(num2_err/(num1+num2), 2) + pow(denom1_err/(denom1+denom2), 2)+ pow(denom2_err/(denom1+denom2), 2))
    return ratio, error

def run(varName, bins, unit, cat = 'em', eID = 'MVANonTrig80_2', fit = False, region = 'barrel', triggerLeg = 'e'):

    dir = '2016_trigStudy'

    dataFunc = setFunc('dataFunc')

    append_name = ''
    files_mc = [# ("SUSY", '/nfs_scratch/zmao/13TeV_samples_25ns_newSplitting_noChargeMatch/SYNC_SUSY_HToTauTau_M-160_%s_%s.root' %(cat, append_name), r.kRed)
                ]

    hist_mc_all = {}
    hist_mc_pass = {}
    file_data = '/user_data/zmao/%s/%s/data_Electron_all_SYNC_em_noIso.root'  %(dir, eID)#'/nfs_scratch/zmao/supy-output//slice/ee//data_Electron_events.root'# %(cat, append_name)

    hist_data_all = r.TH1F('hist_data_all', '', len(bins)-1, bins)
    hist_data_pass = r.TH1F('hist_data_pass', '', len(bins)-1, bins)
    
    for iName, iSample, iColor in files_mc:
        if iName not in hist_mc_all.keys():
            hist_mc_all[iName] = r.TH1F("hist_%s_all" %iName, "", len(bins)-1, bins)
            hist_mc_pass[iName] = r.TH1F("hist_%s_pass" %iName, "", len(bins)-1, bins)
        loop_one_sample(iSample, varName, hist_mc_all[iName], hist_mc_pass[iName], cat, False, region, triggerLeg)

    if file_data != '':
        loop_one_sample(file_data, varName, hist_data_all, hist_data_pass, cat, True, region, triggerLeg)


    g_mc = []
    histList = []
    funcs = []
    i = 0
    for iKey in hist_mc_all.keys():
        g_mc.append(r.TGraphAsymmErrors())
        g_mc[i].BayesDivide(hist_mc_pass[iKey], hist_mc_all[iKey])
        g_mc[i].SetMarkerStyle(8)
        g_mc[i].SetMarkerSize(0.9)
        color = getColor(iKey)
        g_mc[i].SetMarkerColor(color)
        g_mc[i].SetLineColor(color)
        if iKey == 'ttbar' and fit:
            funcs.append(setFunc('%sFunc' %iKey))
            funcs[i].SetLineColor(color)
            funcs[i].SetLineStyle(2)
            g_mc[i].Fit('%sFunc' %iKey, "R")
            histList.append((g_mc[i], "%s, plateau: %.3f +- %.3f" %(iKey, funcs[i].GetParameter(0), funcs[i].GetParError(0)), 'ep'))
        else:
            funcs.append(None)
            if len(bins) == 3:
                x = r.Double(0.0)
                y1 = r.Double(0.0)
                y2 = r.Double(0.0)
                g_mc[i].GetPoint(0, x, y1)
                g_mc[i].GetPoint(1, x, y2)
                histList.append((g_mc[i], "%s (%.3f +/- %.3f, %.3f +/- %.3f)" %(iKey, y1, g_mc[i].GetErrorY(0), y2, g_mc[i].GetErrorY(1)), 'ep'))
            else:
                histList.append((g_mc[i], iKey, 'ep'))

        
        i += 1

    g_data = r.TGraphAsymmErrors()
    g_data.BayesDivide(hist_data_pass, hist_data_all)
    dataFunc.SetLineColor(r.kBlack)
    dataFunc.SetLineStyle(2)
    fakeHist = r.TH1F("fakeHist", "", 1, 0,1)
    fakeHist.SetLineColor(r.kWhite)
    if fit:
        g_data.Fit("dataFunc", "R"); 
        histList.append((g_data, 'Observed, plateau: %.3f +/- %.3f' %(dataFunc.GetParameter(0), dataFunc.GetParError(0)), "ep"))
        histList.append((fakeHist, '          halfpoint: %.1f +/- %.1f' %(dataFunc.GetParameter(1), dataFunc.GetParError(1)), "l"))
        histList.append((fakeHist, '          slope: %.3f +/- %.3f' %(dataFunc.GetParameter(2), dataFunc.GetParError(2)), "l"))
    else:
        if len(bins) == 3:
            x = r.Double(0.0)
            data_y1 = r.Double(0.0)
            data_y2 = r.Double(0.0)
            g_data.GetPoint(0, x, data_y1)
            g_data.GetPoint(1, x, data_y2)
            histList.append((g_data, "Observed (%.3f +/- %.3f, %.3f +/- %.3f)" %(data_y1, g_data.GetErrorY(0), data_y2, g_data.GetErrorY(1)), 'ep'))
        else:
            histList.append((g_data, 'Observed', 'ep'))
    
    fakeHist = r.TH1D("fakeHist", "", 1, 0, 1)
    fakeHist.SetLineColor(r.kWhite)

    g_data.SetMarkerStyle(8)
    g_data.SetMarkerSize(0.9)
    g_data.SetMarkerColor(r.kBlack)

    length = 800
#     length = 1800

    c = r.TCanvas("c","Test", length, 800)

    null = r.TH2F("null","", len(bins)-1, bins, 1, 0, 1.1)
    null.SetMaximum(1.2)
    if triggerLeg == 'e':
        psfile = 'eleTrigTurnOnCurve_%s_%s_%s_%s.pdf' %(varName, cat, eID, region)
        null.SetTitle("electron trigger turn-on curve; %s; Effeciency" %unit)
    else:
        psfile = 'muonTrigTurnOnCurve_%s_%s_%s_%s.pdf' %(varName, cat, eID, region)
        null.SetTitle("muon trigger turn-on curve; %s; Effeciency" %unit)
    null.SetStats(False)

    if len(bins) == 3:
        leg = tool.setMyLegend((0.1, 0.4 - 0.06*4, 0.95, 0.4), histList)
    else:
        leg = tool.setMyLegend((0.45, 0.4 - 0.06*4, 0.9, 0.4), histList)


    r.gPad.SetTicky()
    r.gPad.SetTickx()
    r.gPad.SetTicky()
    null.Draw()
    for i in range(len(hist_mc_all.keys())):
        g_mc[i].Draw('same PE')
    g_data.Draw('same PE')
    leg.Draw('same')

    c.Print('%s' %psfile)
    c.Close()


bins = array.array('d', range(10, 51, 2) + range(50, 85, 5) + range(100, 210, 20))# + range(200, 800, 150))# + [60,100, 150, 200, 250, 300, 400, 500, 600, 700, 800])
bins_e = array.array('d', range(10, 51, 2) + range(50, 105, 10) + range(100, 210, 20))# + range(200, 800, 200))# + [60,100, 150, 200, 250, 300, 400, 500, 600, 700, 800])


# bins = array.array('d', range(0, 60, 5) + [60,100, 150, 200, 250, 300, 400, 500, 600, 700, 800])

bins2 = []
for i in range(21):
    bins2.append(-4 + i*0.4)
if __name__ == "__main__":
    cutSampleTools.setupLumiReWeight()

    bins_barrel = bins
    bins_endcap = bins_e
    bins_middle = bins_e

    triggerLeg = 'mu'
#     bins_barrel, bins_endcap, bins_middle = dynamicBinning('/user_data/zmao/2016_trigStudy/runBCDEFGH/data_Electron_all_SYNC_em_noIso.root', [200, 800], "mu")
    run('mPt', bins_barrel, "mu pt", 'em', 'runBCDEFGH', True, 'barrel', triggerLeg)
    run('mPt', bins_middle, "mu pt", 'em', 'runBCDEFGH', True, 'middle', triggerLeg)
    run('mPt', bins_endcap, "mu pt", 'em', 'runBCDEFGH', True, 'endcap', triggerLeg)

#     bins_barrel, bins_endcap = dynamicBinning('/user_data/zmao/2016_trigStudy/runBCDEFGH/data_Muon_all_SYNC_em_noIso.root', [200, 600])
#     run('ePt', bins_barrel, "e pt", 'em', 'runBCDEFGH', True, 'barrel', triggerLeg)
#     run('ePt', bins_endcap, "e pt", 'em', 'runBCDEFGH', True, 'endcap', triggerLeg)

#     bins_barrel, bins_endcap = dynamicBinning('/nfs_scratch/zmao/triggerStudy/MVATrigWP80/data_Muon_all_SYNC_em_inclusive.root', [35, 400])
#     run('ePt', bins_barrel, "e pt", 'em', 'MVATrigWP80', False, 'barrel', triggerLeg)
#     run('ePt', bins_endcap, "e pt", 'em', 'MVATrigWP80', False, 'endcap', triggerLeg)

#     run('ePt', bins_endcap, "e pt", 'em', 'HEEP2', False, 'endcap')
# 
#     bins_barrel, bins_endcap = dynamicBinning('/nfs_scratch/zmao/triggerStudy/MVANonTrig80_2/data_Muon_all_SYNC_em_inclusive.root', [50, 400])
# 
#     run('ePt', bins_endcap, "e pt", 'em', 'MVANonTrig80_2', False, 'endcap')

#     run('ePt', bins, "e pt", 'em', 'CBTight', False, 'endcap')
#     run('ePt', bins, "e pt", 'em', 'CBTight', False, 'barrel')


    cutSampleTools.freeLumiReWeight()

