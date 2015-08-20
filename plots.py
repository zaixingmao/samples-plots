#!/usr/bin/env python

import ROOT as r
import plots_cfg
import tool
import optparse
import array
import math
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs


lumi = 0.04

position = (0.6, 0.9 - 0.06*6, 0.87, 0.9)
if plots_cfg.addIntegrals:
    position = (0.47, 0.9 - 0.06*6, 0.87, 0.9)

defaultOrder = [("Electroweak", r.TColor.GetColor(222, 90,106)),
                ('t#bar{t}', r.TColor.GetColor(155,152,204)),
                ('QCD', r.TColor.GetColor(250,202,255)),
                ("Z#rightarrow#tau#tau", r.TColor.GetColor(248,206,104)),
                ]

def passCut(tree):
    if tree.eTau_WPLoosePass or tree.eTauPass:
#     if 1.5 < tree.tByCombinedIsolationDeltaBetaCorrRaw3Hits < 10.0:
        return True
    return False

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
        print (histDict['Observed'].Integral(intBin, len(varBins)+1) - histDict['Electroweak'].Integral(intBin, len(varBins)+1) - histDict['t#bar{t}'].Integral(intBin, len(varBins)+1) - histDict['Z#rightarrow#tau#tau'].Integral(intBin, len(varBins)+1))/histDict['WJets'].Integral(intBin, len(varBins)+1) + 1


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

def loop_one_sample(iSample, iCategory, histDict, varName, varBins, FS, initEvents = 0):
    iSample += "%s.root" %FS
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    weight = 1.0
    nEntries = tree.GetEntries()
    nPass_OS = 0.0
    nPass_SS = 0.0
    nEvents_p_n_SS = 0.0
    nEvents_p_n_OS = 0.0
    tmpHist = r.TH1F("tmp_%s_%s" %(iCategory, varName), '', len(varBins)-1, varBins)
    tmpHist_qcd = r.TH1F("tmp_qcd_%s_%s" %(iCategory, varName), '', len(varBins)-1, varBins)

    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)

#         if not passCut(tree):
#             continue
        if iCategory != 'Observed':
            weight = lumi*tree.xs/(initEvents+0.0)
            if tree.genEventWeight < 0:
                weight = -weight
#             if tree.singleEPass:
#                 weight = 0.7*weight
        if 'WJets' in iSample:
            weight = 1.0*weight

        if tree.q_1 ==  tree.q_2:
            if iCategory != 'Observed':
                tmpHist_qcd.Fill(getattr(tree, varName), -weight)
            else:
                tmpHist_qcd.Fill(getattr(tree, varName), weight)
        else:
            nPass += 1.0
            if iCategory != 'Observed':
                if tree.genEventWeight < 0:
                    nEvents_p_n -= 1.0
                else:
                    nEvents_p_n += 1.0
            tmpHist.Fill(getattr(tree, varName), weight)

    if iCategory != 'Observed':
        if nEvents_p_n != 0:
            tmpHist_qcd.Scale(nPass/nEvents_p_n)
            tmpHist.Scale(nPass/nEvents_p_n)
        else:
            tmpHist_qcd.Scale(0)
            tmpHist.Scale(0)
    histDict['QCD'].Add(tmpHist_qcd)
    histDict[iCategory].Add(tmpHist)
    if 'WJets' in iSample:
        histDict['WJets'].Add(tmpHist)
            

    del tmpHist_qcd
    del tmpHist

    print ''

def getQCDScale(histDict, varBins):
    OS_MC_Miss = histDict['Observed'].Integral(0, len(varBins)+1)
    for ikey, iColor in defaultOrder:
        if (ikey in histDict.keys()) and (ikey != 'QCD'):
            OS_MC_Miss -= histDict[ikey].Integral(0, len(varBins)+1)
    SS_MC_Miss = histDict['QCD'].Integral(0, len(varBins)+1)
    print 'OS/SS = %.1f/%.1f = %.3f' %(OS_MC_Miss, SS_MC_Miss, OS_MC_Miss/SS_MC_Miss)
    return OS_MC_Miss/SS_MC_Miss


def buildStackFromDict(histDict, FS, option = 'width'):
    stack = r.THStack()
    for ikey, iColor in defaultOrder:
        if ikey in histDict.keys():
            print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
            stack.Add(histDict[ikey])
        else:
            print 'missing samples for %s' %ikey
    stack.SetTitle('CMS Preliminary 40.0 pb^{-1} at 13 TeV; ; events / bin')
    return stack

def setQCD(hist, scale = 0.6): #force qcd to be non-negative
    hist.Scale(scale)
    for i in range(0, hist.GetNbinsX()+2):
        content = hist.GetBinContent(i)
        x = hist.GetBinCenter(i)
        if content < 0:
            hist.Fill(x, -content)

def buildDelta(deltaName, histDict, bins, varName, unit):
    bkg = r.TH1F('bkg_%s' %deltaName, '', len(bins)-1, bins)
    delta = r.TH1F(deltaName, deltaName, len(bins)-1, bins)
    for ikey, icolor in defaultOrder:
        if ikey in histDict.keys():
            bkg.Add(histDict[ikey].Clone())

    delta = ratioHistogram(num = histDict["Observed"], den = bkg, relErrMax=0.25)
#     delta.Add(histDict["Observed"])
#     delta.Sumw2()
#     bkg.Sumw2()
#     delta.Divide(bkg)
    delta.SetTitle('; %s %s; data/MC' %(varName, unit))
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

def buildHists(varName, varBins, unit, FS, option = "width"):
    histDict = {}
    histDict["QCD"] = r.TH1F("QCD_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["QCD"].SetFillColor(getColor("QCD"))
    histDict["QCD"].SetMarkerColor(getColor("QCD"))
    histDict["QCD"].SetMarkerStyle(21)
    histDict["QCD"].SetLineColor(r.kBlack)
    histDict["WJets"] = r.TH1F("WJets_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    for iSample, iCategory, iInitEvents in plots_cfg.sampleList:
    
        if not (iCategory in histDict.keys()):
            histDict[iCategory] = r.TH1F("%s_%s_%s" %(iCategory, FS, varName), "", len(varBins)-1, varBins)
            if iCategory != "Observed":
                histDict[iCategory].SetFillColor(getColor(iCategory))
                histDict[iCategory].SetMarkerColor(getColor(iCategory))
                histDict[iCategory].SetMarkerStyle(21)
                histDict[iCategory].SetLineColor(r.kBlack)

        loop_one_sample(iSample, iCategory, histDict, varName, varBins, FS, iInitEvents)
    if not ('Observed' in histDict.keys()):
        histDict['Observed'] = r.TH1F("Observed_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)

    qcd_scale = getQCDScale(histDict, varBins)
    setQCD(histDict['QCD'], plots_cfg.QCD_scale[FS])
    getWJetsScale(histDict, varName, varBins)


    for iCat in histDict.keys():
        histDict[iCat].Sumw2()
        histDict[iCat].Scale(1, option)

    bkgStack = buildStackFromDict(histDict, FS, option)
    delta = buildDelta('%s_delta' %varName, histDict, varBins, varName, unit)
    return histDict, bkgStack, delta


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
    return tool.setMyLegend(position, histList)

def multiPlots(FS, option):
    psfile = '13TeV_%s.pdf' %(FS)
    c = r.TCanvas("c","Test", 600, 800)

    p = []
    p_r = []
    legends = []
    counter = 0
    for iVarName, iVarBins, iUnit, iMax in plots_cfg.vars:
        p.append(r.TPad("p_%s" %iVarName,"p_%s" %iVarName, 0., 1, 1., 0.3))
        p_r.append(r.TPad("p_%s_r" %iVarName,"p_%s_r" %iVarName, 0.,0.3,1.,0.06))
        p[len(p)-1].SetMargin(1, 1, 0, 0.1)
        p_r[len(p_r)-1].SetMargin(1, 1, 0.2, 0)
        p[len(p)-1].Draw()
        p_r[len(p_r)-1].Draw()
        p[len(p)-1].cd()
        r.gPad.SetTicky()

        histDict, bkgStack, delta = buildHists(iVarName, iVarBins, iUnit, FS, option)
        iMax = 1.2*bkgStack.GetMaximum()
        bkgStack.SetMaximum(iMax)
        iMin = 0
        bkgStack.SetMinimum(iMin)        
        bkgStack.Draw('hist AH')
        bkgStack.GetYaxis().SetNdivisions(510)
        bkgStack.GetYaxis().SetTitleOffset(1.2)
        bkgStack.GetYaxis().SetLabelSize(0.035)
        #final state    
        fsName = r.TLatex()
        fsName.DrawLatex(iVarBins[3], iMax*0.98, getFinalStateLatex(FS))

        histDict["Observed"].Sumw2()
        histDict["Observed"].SetMarkerStyle(8)
        histDict["Observed"].SetMarkerSize(0.9)
        histDict["Observed"].Draw('PE same')
        legends.append(setLegend(position, histDict, iVarBins, option))
        legends[len(legends)-1].Draw('same')
        
        p_r[len(p)-1].cd()
        r.gPad.SetTicky()
        r.gPad.SetTickx()
        p_r[len(p)-1].SetGridy(1)
        delta.Draw()
        r.gPad.Update()
        r.gPad.RedrawAxis()
        c.cd()
        yaxis =  r.TGaxis(0.1, 0.3, 0.1, 0.9, iMin, iMax, 505,"")
        yaxis.SetLabelSize(0.03)
        yaxis.SetTitle("events / bin")
        yaxis.SetTitleOffset(1.2)
        yaxis.SetTitleSize(0.035)

        yaxis.Draw("A")
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

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--FS", dest="FS", default='tt', help="final state product, et, tt")
    parser.add_option("--option", dest="option", default='', help="width")

    options, args = parser.parse_args()
    return options
options = opts()

finalStates = expandFinalStates(options.FS)
for iFS in finalStates:
    multiPlots(iFS, options.option)