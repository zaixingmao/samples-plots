#!/usr/bin/env python

import ROOT as r
import plots_cfg
import tool
import optparse
import array
import math
import cutSampleTools
from makeWholeTools2 import calcSysUnc
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
l_1 = lvClass()
l_2 = lvClass()
jet = lvClass()
met = lvClass()


lumi = 1263.89#552.67#654.39#209.2#16.86, 578.26
Lumi = lumi #3000.0

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--FS", dest="FS", default='mt', help="final state product, et, tt")
    parser.add_option("--option", dest="option", default='', help="width")
    parser.add_option("--PUWeight", dest="PUWeight", default=False, action="store_true", help="")
    parser.add_option("--unblind", dest="unblind", default=False, action="store_true", help="")
    parser.add_option("--unblindPartial", dest="unblindPartial", default=False, action="store_true", help="")
    parser.add_option("--antiIso", dest="antiIso", default=False, action="store_true", help="")
    parser.add_option("--antiEIso", dest="antiEIso", default=False, action="store_true", help="")
    parser.add_option("--antiMIso", dest="antiMIso", default=False, action="store_true", help="")
    parser.add_option("--saveHisto", dest="saveHisto", default=False, action="store_true", help="")
    parser.add_option("--noIso", dest="noIso", default=False, action="store_true", help="")
    parser.add_option("--ratio", dest="ratio", default=False, action="store_true", help="")

    options, args = parser.parse_args()
    return options
options = opts()

def getNCSVLJets(tree):
    n = 0
    for i in range(1, 9):                                                                                                                                                           
        if getattr(tree, "jet%iCSVBtag" %i) > 0.605 and getattr(tree, "jet%iPt" %i) > 20 and abs(getattr(tree, "jet%iEta" %i)) < 4.7:
            l_1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
            jet.SetCoordinates(getattr(tree, "jet%iPt" %i), 
                               getattr(tree, "jet%iEta" %i), 
                               getattr(tree, "jet%iPhi" %i), 
                               0)
            dR_1 = r.Math.VectorUtil.DeltaR(l_1, jet)
            if dR_1 <= 0.4:
                continue
            l_2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)
            dR_2 = r.Math.VectorUtil.DeltaR(l_2, jet)
            if dR_2 > 0.4:
                n += 1
    return n

position = (0.6, 0.9 - 0.06*6, 0.87, 0.9)
if plots_cfg.addIntegrals:
    position = (0.47, 0.9 - 0.06*6, 0.87, 0.9)

defaultOrder = [("Diboson", r.TColor.GetColor(222, 90,106)),
                ("WJets",  r.TColor.GetColor(100,182,232)),
                ('t#bar{t}', r.TColor.GetColor(155,152,204)),
                ('QCD', r.TColor.GetColor(250,202,255)),
                ("Z#rightarrow#tau#tau", r.TColor.GetColor(248,206,104)),
                ('h125#rightarrow#tau#tau', r.TColor.GetColor(106, 203,107)),
                ]

def passCut(tree, FS, isData):
#     onlyMuLead = True if (not (tree.Mu8e23Pass and tree.mMu8El23 and tree.mMu8El23)) else False
#     onlyEleLead = True if (not (tree.Mu23e12Pass and tree.mMu23El12 and tree.eMu23El12)) else False
#     both = True if (tree.Mu23e12Pass and tree.mMu23El12 and tree.eMu23El12) and (tree.Mu8e23Pass and tree.mMu8El23 and tree.mMu8El23) else False
    if getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:
        return False
    if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
        return False
    if tree.pfMetEt <= 30:
        return False
    if getNCSVLJets(tree) >= 1:
        return False

#     if (not (0.15 < tree.eRelIso < 0.3)) or (not (tree.mRelIso < 0.15)):
#         return False
#     if (tree.eRelIso < 0.15) and (0.2 < tree.mRelIso < 2):# or (tree.mRelIso < 0.15 and 0.15 < tree.eRelIso < 0.5):
#         return True
#     else:
#         return False
    if FS == 'et' and not isData:
        if tree.singleEPass and tree.eSingleEle and tree.ePt > 33.0:
            return True
        else:
            return False
    if FS == 'et' and isData:
        if tree.singleETightPass and tree.eSingleEleTight and tree.ePt > 33.0:
            return True
        else:
            return False
    return True

def passUnblindPartial(varname, var):
    if varname == 'm_vis' and var <= 100:
        return True
    if varname == 'pZeta - 3.1pZetaVis' and var <=-50:
        return True
    if varname == 'pfMetEt' and var <= 30:
        return True
    return False

def getZPrimeXS(mass):
    xs = {'500': 9.33,
          '1000': 0.468,
          '1500': 0.0723,
          '2000': 0.0173,
          '2500': 0.00554,
          '3000': 0.00129,
          '3500': 0.00049,
          '4000': 0.000255, 
          '4500': 0.000108,
          '5000': 0.0000559
        }
    return xs[mass]

def fixNegativBins(hist):
    nBins = hist.GetNbinsX()
    for i in range(1, nBins+1):
        if hist.GetBinContent(i) < 0:
            hist.SetBinContent(i, 0.0)
    return hist

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

def getColor(cat):
    for iCat, iColor in defaultOrder:
        if iCat == cat:
            return iColor

def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates

def getWJetsScale(histDict, varName, varBins):
    intBin = 10
    if varName != 'mt_1':
        return 0
    else:
        print (histDict['Observed'].Integral(intBin, len(varBins)+1) - histDict['Diboson'].Integral(intBin, len(varBins)+1) - histDict['t#bar{t}'].Integral(intBin, len(varBins)+1) - histDict['Z#rightarrow#tau#tau'].Integral(intBin, len(varBins)+1))/histDict['WJets'].Integral(intBin, len(varBins)+1) + 1


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

def loop_one_sample(iSample, iCategory, histDict, varName, varBins, FS):
    if options.antiIso:
        iSample += "%s_antiIso.root" %FS
    elif options.antiEIso:
        iSample += "%s_antiEIso.root" %FS
    elif options.antiMIso:
        iSample += "%s_antiMIso.root" %FS
    elif options.noIso:
        iSample += "%s_noIso.root" %FS
    else:
        iSample += "%s_inclusive.root" %FS 
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    eventCount = file.Get('eventCount')
    eventCountWeighted = file.Get('eventCountWeighted')

    nEntries = tree.GetEntries()
    tmpHist = r.TH1F("tmp_%s_%s" %(iCategory, varName), '', len(varBins)-1, varBins)
    tmpHist_qcd = r.TH1F("tmp_qcd_%s_%s" %(iCategory, varName), '', len(varBins)-1, varBins)
    tmpHist_forROOTFile = r.TH1F("%s" %(varName), '', len(varBins)-1, varBins)

    isData = False
    if iCategory == 'Observed':
        isData = True
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        weight = 1.0

        if eventCount:
            initEvents = eventCount.GetBinContent(1)
        else:    
            initEvents = tree.initEvents
        if eventCountWeighted:
            sumWeights = eventCountWeighted.GetBinContent(1)
        else:    
            sumWeights = tree.initWeightedEvents
        if not passCut(tree, FS, isData):
            continue
        if not isData:
            weight = Lumi*tree.xs*tree.genEventWeight/(sumWeights+0.0)
            if options.PUWeight:
                weight = weight*cutSampleTools.getPUWeight(tree.nvtx)


        if 'WJets' in iSample:
            weight = 1.0*weight
        if 'ZPrime' in iSample:
            weight = getZPrimeXS(iCategory[7:])*weight
        if varName == 'm_withMET':
            l1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
            l2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)
            met.SetCoordinates(tree.pfMetEt, 0.0, tree.pfMetPhi, 0)
            value = (l1 + l2 + met).mass()
        elif varName == 'mVis':
            l1.SetCoordinates(tree.ePt, tree.eEta, tree.ePhi, 0.51100e-3)
            l2.SetCoordinates(tree.mPt, tree.mEta, tree.mPhi, tree.mMass)
            value = (l1 + l2).mass()
        elif varName == 'pZeta - 3.1pZetaVis':
            value = getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1]))

        elif varName == "nCSVL":
            value = getNCSVLJets(tree)
        elif varName == "cos_phi_tau1_tau2":
            value = math.cos(tree.phi_1 - tree.phi_2)
        elif varName == 'm_gen':
            if tree.eGenTauMass < 0  or tree.tGenMass < 0:
                continue

            l1.SetCoordinates(tree.eGenTauPt, tree.eGenTauEta, tree.eGenTauPhi, tree.eGenTauMass)
            l2.SetCoordinates(tree.tGenPt, tree.tGenEta, tree.tGenPhi, tree.tGenMass)
            value = (l1 + l2).mass()
        else:
            value = getattr(tree, varName)

        if tree.q_1 == tree.q_2:
            if not isData:
                tmpHist_qcd.Fill(value, -weight)
            else:
                tmpHist_qcd.Fill(value, weight)
        else:
            fill = True
            if isData:
                fill = False
                if options.unblind or (options.unblindPartial and passUnblindPartial(varName, value)):
                    fill = True
            if fill:
                tmpHist.Fill(value, weight)
                tmpHist_forROOTFile.Fill(value, weight)

    histDict['QCD'].Add(tmpHist_qcd)
    histDict[iCategory].Add(tmpHist)
    if 'WJets' in iSample and iCategory != 'WJets':
        histDict['WJets'].Add(tmpHist)
            

    del tmpHist_qcd
    del tmpHist

    if options.saveHisto:
        oFile = r.TFile('/user_data/zmao/ZPrimeHistos/%s/%s_%s.root' %(FS, iSample[iSample.rfind('/'): iSample.rfind('_SYNC')], varName),"recreate")
        oFile.cd()
        tmpHist_forROOTFile = fixNegativBins(tmpHist_forROOTFile)
        tmpHist_forROOTFile.Write()
        oFile.Close()
    del tmpHist_forROOTFile

    print ''

def getQCDScale(histDict, varBins):
    OS_MC_Miss = histDict['Observed'].Integral(0, len(varBins)+1)
    for ikey, iColor in defaultOrder:
        if (ikey in histDict.keys()) and (ikey != 'QCD'):
            OS_MC_Miss -= histDict[ikey].Integral(0, len(varBins)+1)
    SS_MC_Miss = histDict['QCD'].Integral(0, len(varBins)+1)
    print 'OS/SS = %.1f/%.1f = %.3f +- %.3f' %(OS_MC_Miss, SS_MC_Miss, OS_MC_Miss/SS_MC_Miss, calcSysUnc(OS_MC_Miss/SS_MC_Miss, OS_MC_Miss, SS_MC_Miss))
#     print 'OS/SS = %.1f/%.1f = %.3f' %(OS_MC_Miss, SS_MC_Miss, OS_MC_Miss/SS_MC_Miss)

    return OS_MC_Miss/SS_MC_Miss


def buildStackFromDict(histDict, FS, option = 'width'):
    stack = r.THStack()
    for ikey, iColor in defaultOrder:
        if ikey in histDict.keys():
            print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
#            histDict[ikey].Scale(1)
            stack.Add(histDict[ikey])
        else:
            print 'missing samples for %s' %ikey
    if option == 'width':
        stack.SetTitle('CMS Preliminary %.2f pb^{-1} at 13 TeV; ; events / bin width' %Lumi)
    else:
        stack.SetTitle('CMS Preliminary %.2f pb^{-1} at 13 TeV; ; events' %Lumi)
    return stack

def setQCD(hist, scale = 0.6): #force qcd to be non-negative
    hist.Scale(scale)
    for i in range(0, hist.GetNbinsX()+2):
        content = hist.GetBinContent(i)
        x = hist.GetBinCenter(i)
        if content < 0:
            hist.Fill(x, -content)

def buildDelta(deltaName, histDict, bins, varName, unit, relErrMax, min = 0.5, max = 1.5):
    bkg = r.TH1F('bkg_%s' %deltaName, '', len(bins)-1, bins)
    delta = r.TH1F(deltaName, deltaName, len(bins)-1, bins)
    for ikey, icolor in defaultOrder:
        if ikey in histDict.keys():
            bkg.Add(histDict[ikey].Clone())
    if max != 1.5:
        delta = ratioHistogram(num = histDict["QCD"], den = bkg, relErrMax=relErrMax)
    else:
        delta = ratioHistogram(num = histDict["Observed"], den = bkg, relErrMax=relErrMax)

#     delta.Add(histDict["Observed"])
#     delta.Sumw2()
#     bkg.Sumw2()
#     delta.Divide(bkg)
    delta.SetTitle('; %s %s; data/MC' %(varName, unit))
    delta.SetMaximum(max)
    delta.SetMinimum(min)

    delta.GetXaxis().SetLabelSize(0.1)
    delta.GetXaxis().SetTitleSize(0.1)
    delta.GetYaxis().SetLabelSize(0.1)
    delta.GetYaxis().SetNdivisions(5,5,0)
    delta.GetYaxis().SetTitleSize(0.1)
    delta.GetYaxis().SetTitleOffset(0.43)
    delta.GetYaxis().CenterTitle()

    return delta

def buildHists(varName, varBins, unit, FS, option, relErrMax):
    histDict = {}
    histDict["QCD"] = r.TH1F("QCD_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["QCD"].SetFillColor(getColor("QCD"))
    histDict["QCD"].SetMarkerColor(getColor("QCD"))
    histDict["QCD"].SetMarkerStyle(21)
    histDict["QCD"].SetLineColor(r.kBlack)
    histDict["WJets"] = r.TH1F("WJets_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    for iName, iSample, iCategory in plots_cfg.sampleList:
    
        if not (iCategory in histDict.keys()) or iCategory == "WJets":
            histDict[iCategory] = r.TH1F("%s_%s_%s" %(iCategory, FS, varName), "", len(varBins)-1, varBins)
            if iCategory != "Observed" and "ZPrime" not in iCategory:
                histDict[iCategory].SetFillColor(getColor(iCategory))
                histDict[iCategory].SetMarkerColor(getColor(iCategory))
                histDict[iCategory].SetMarkerStyle(21)
                histDict[iCategory].SetLineColor(r.kBlack)
            if "ZPrime" in iCategory:
                histDict[iCategory].SetLineStyle(2)
                histDict[iCategory].SetLineColor(r.kBlue)

        loop_one_sample(iSample, iCategory, histDict, varName, varBins, FS)
    if not ('Observed' in histDict.keys()):
        histDict['Observed'] = r.TH1F("Observed_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)

    if options.antiIso or options.antiEIso or options.antiMIso or options.noIso:
        qcd_scale = getQCDScale(histDict, varBins)
        setQCD(histDict['QCD'], qcd_scale)
    else:
        setQCD(histDict['QCD'], plots_cfg.QCD_scale[FS]*Lumi/lumi)                                                                                                       
    getWJetsScale(histDict, varName, varBins)

    if options.saveHisto:
        oFile = r.TFile('/user_data/zmao/ZPrimeHistos/%s/QCD_all_%s.root' %(FS, varName),"recreate")
        oFile.cd()
        QCD_hist_tmp = r.TH1D("%s" %(varName), '', len(varBins)-1, varBins)
        QCD_hist_tmp.Add(histDict['QCD'])
        QCD_hist_tmp = fixNegativBins(QCD_hist_tmp)
        QCD_hist_tmp.Write()
        oFile.Close()
        del QCD_hist_tmp

    for iCat in histDict.keys():
        histDict[iCat].Sumw2()
        histDict[iCat].Scale(1, option)

    bkgStack = buildStackFromDict(histDict, FS, option)
    delta = buildDelta('%s_delta' %varName, histDict, varBins, varName, unit, relErrMax)
    if FS == 'et':
        delta2 = buildDelta('%s_delta_qcd' %varName, histDict, varBins, varName, unit, relErrMax, 0, 1.0)
    else:
        delta2 = buildDelta('%s_delta_qcd' %varName, histDict, varBins, varName, unit, relErrMax, 0, 0.5)
    return histDict, bkgStack, delta, delta2


def setLegend(position, histDict, bins, option = 'width'):
    histList = []
    histList.append((histDict['Observed'], 'Observed', 'lep'))

    nbins = len(bins)
    for ikey, iColor in reversed(defaultOrder):
        if ikey in histDict.keys():
            if plots_cfg.addIntegrals:
                histList.append((histDict[ikey], '%s (%.2f)' %(ikey, histDict[ikey].Integral(0, nbins+1, option)), 'f'))
            else:
                histList.append((histDict[ikey], '%s' %ikey, 'f'))
    if not (options.antiIso or options.antiEIso or options.antiMIso or options.noIso):
        histList.append((histDict['ZPrime_2000'], 'ZPrime_2000 (%.2f)' %(histDict['ZPrime_2000'].Integral(0, nbins+1, option)), 'l'))

    return tool.setMyLegend(position, histList)

def multiPlots(FS, option):
    if options.PUWeight:
        psfile = '13TeV_%s_puweight.pdf' %(FS)
    else:
        psfile = '13TeV_%s.pdf' %(FS)
    c = r.TCanvas("c","Test", 600, 800)

    p = []
    p_r = []
    legends = []
    counter = 0
    for iVarName, iVarBins, iUnit, relErrMax in plots_cfg.vars:
        p.append(r.TPad("p_%s" %iVarName,"p_%s" %iVarName, 0., 1, 1., 0.3))
        p_r.append(r.TPad("p_%s_r" %iVarName,"p_%s_r" %iVarName, 0.,0.3,1.,0.06))
        p[len(p)-1].SetMargin(1, 1, 0, 0.1)
        p_r[len(p_r)-1].SetMargin(1, 1, 0.2, 0)
        p[len(p)-1].Draw()
        p_r[len(p_r)-1].Draw()
        p[len(p)-1].cd()
        if not options.ratio:
            r.gPad.SetTicky()
        r.gPad.SetTickx()

#         r.gPad.SetLogy()

        histDict, bkgStack, delta, delta2 = buildHists(iVarName, iVarBins, iUnit, FS, option, relErrMax)
        iMax = 1.2*max(bkgStack.GetMaximum(), histDict["Observed"].GetMaximum())
        bkgStack.SetMaximum(iMax)
        iMin = 0.01
        bkgStack.SetMinimum(iMin)   
     
        bkgStack.Draw('hist H')
        bkgStack.GetYaxis().SetNdivisions(510)
        bkgStack.GetYaxis().SetTitleOffset(1.2)
        bkgStack.GetYaxis().SetLabelSize(0.035)
        #final state    
        fsName = r.TLatex()
        fsName.DrawLatex(iVarBins[3], iMax*0.98, getFinalStateLatex(FS))

        histDict["Observed"].Sumw2()

        histDict["Observed"].SetMarkerStyle(8)
        histDict["Observed"].SetMarkerSize(0.9)
        if options.unblind or options.unblindPartial:
            histDict["Observed"].Draw('PE same')
        if not (options.antiIso or options.antiEIso or options.antiMIso or options.noIso):
            histDict["ZPrime_2000"].Draw('H same')

        legends.append(setLegend(position, histDict, iVarBins, option))
        legends[len(legends)-1].Draw('same')
        
        if options.ratio:
            rightmax = 1.1*delta2.GetMaximum()
            scale = r.gPad.GetUymax()/rightmax
            delta2.SetLineColor(r.kRed)
            delta2.Scale(scale)
            delta2.Draw("sameHist")
            axis = r.TGaxis(r.gPad.GetUxmax(), r.gPad.GetUymin(), r.gPad.GetUxmax(), r.gPad.GetUymax(),0,rightmax,510,"+L")
            axis.SetLineColor(r.kRed)
            delta2.SetLineStyle(2)
            delta2.SetLineWidth(2)
            axis.SetTextColor(r.kRed)
            axis.SetTitle("QCD/bkg")
            axis.SetLabelColor(r.kRed)
            axis.SetTitleOffset(1.5)
            axis.SetTitleSize(0.025)
            axis.Draw()

        p_r[len(p)-1].cd()
        r.gPad.SetTicky()
        r.gPad.SetTickx()
        p_r[len(p)-1].SetGridy(1)

        delta.Draw()

        r.gPad.Update()
        r.gPad.RedrawAxis()
        c.cd()
        yaxis =  r.TGaxis(0.1, 0.3, 0.1, 0.9, iMin, iMax, 505,"G")
        yaxis.SetLabelSize(0.03)
        yaxis.SetTitle("events / bin")
        yaxis.SetTitleOffset(1.2)
        yaxis.SetTitleSize(0.035)

#         yaxis.Draw("A")
        c.Update()
        if (counter == len(plots_cfg.vars)-1) and (counter == 0):
            c.Print('%s' %psfile)
        elif counter == 0:
            c.Print('%s(' %psfile)
        elif counter == len(plots_cfg.vars)-1:
            c.Print('%s)' %psfile)
        else:
            c.Print('%s' %psfile)
        c.Clear()
        counter += 1
    print "Plot saved at %s" %(psfile)
    c.Close()

finalStates = expandFinalStates(options.FS)
if options.PUWeight:
    cutSampleTools.setupLumiReWeight()
for iFS in finalStates:
    multiPlots(iFS, options.option)
if options.PUWeight:
    cutSampleTools.freeLumiReWeight()
