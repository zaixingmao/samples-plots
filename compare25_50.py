#!/usr/bin/env python

import ROOT as r
import plots_cfg
import tool
import optparse
import array
import math

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs


lumi = 40

position = (0.6, 0.9 - 0.06*2, 0.87, 0.9)

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


def loop_one_sample(iSample, hist, varName, varBins, FS, initEvents = 0):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    weight = 1.0
    nEntries = tree.GetEntries()
    nPass = 0.0
    nEvents_p_n = 0.0

    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)

        if initEvents == 0:
            initEvents = tree.initEvents
            
        weight = lumi*tree.xs/(initEvents+0.0)
        if tree.genEventWeight < 0:
            weight = -weight

        if tree.q_1 ==  tree.q_2:
            continue
        else:
            nPass += 1.0
            if tree.genEventWeight < 0:
                nEvents_p_n -= 1.0
            else:
                nEvents_p_n += 1.0
        hist.Fill(getattr(tree, varName), weight)

    if nEvents_p_n != 0:
        hist.Scale(nPass/nEvents_p_n)
    else:
        hist.Scale(0)
    print hist.Integral(0, len(varBins)+1)
    print ''


def buildDelta(deltaName, hist1, hist2, bins, varName, unit):
    delta = r.TH1F(deltaName, deltaName, len(bins)-1, bins)

    delta = ratioHistogram( num = hist1, den = hist2, relErrMax=0.25)
#     delta.Add(hist1)
#     delta.Divide(hist2)
    delta.SetTitle('; %s %s; 25ns/50ns' %(varName, unit))
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

def buildHists(varName, varBins, unit, FS, sample = 'DY'):
    hist_25 = r.TH1F("25_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    hist_50 = r.TH1F("50_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    hist_25.SetLineColor(r.kBlue)
    hist_50.SetLineColor(r.kRed)
    hist_50.SetLineStyle(2)

    sampleName = plots_cfg.sampleDict[sample][0]
    initEvents = plots_cfg.sampleDict[sample][1]

    loop_one_sample('/nfs_scratch/zmao/13TeV_samples_25ns/' + sampleName + FS + '_inclusive.root', hist_25, varName, varBins, FS, 0)
    loop_one_sample('/nfs_scratch/zmao/13TeV_samples/' + sampleName + FS + '.root', hist_50, varName, varBins, FS, initEvents)

    delta = buildDelta('%s_delta' %varName, hist_25, hist_50, varBins, varName, unit)
    return hist_25, hist_50, delta


def setLegend(position, hist25, hist50, bins):
    histList = []
    nbins = len(bins)

    histList.append((hist25, '25ns', 'L'))
    histList.append((hist50, '50ns', 'L'))

    return tool.setMyLegend(position, histList)

def multiPlots(FS, sample):
    psfile = 'compare_%s_%s.pdf' %(sample, FS)
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

        hist_25, hist_50, delta = buildHists(iVarName, iVarBins, iUnit, FS, sample)
        iMax = 1.2*hist_50.GetMaximum()
        hist_25.SetMaximum(iMax)
        iMin = 0
        hist_25.SetMinimum(iMin)        
        hist_25.Draw('')
        hist_25.GetYaxis().SetNdivisions(510)
        hist_25.GetYaxis().SetTitleOffset(1.2)
        hist_25.GetYaxis().SetLabelSize(0.035)
        hist_50.Draw('same')


        #final state    
        fsName = r.TLatex()
        fsName.DrawLatex(iVarBins[3], iMax*0.9, getFinalStateLatex(FS))

        legends.append(setLegend(position, hist_25, hist_50, iVarBins))
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

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--FS", dest="FS", default='tt', help="final state product, et, tt")
    parser.add_option("--sample", dest="sample", default='ZZ', help="")

    options, args = parser.parse_args()
    return options
options = opts()

finalStates = expandFinalStates(options.FS)
for iFS in finalStates:
    multiPlots(iFS, options.sample)