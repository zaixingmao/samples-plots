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

defaultOrder = {# "VV": r.TColor.GetColor(222, 90,106),
#                 "WJets":  r.TColor.GetColor(100,182,232),
#                 'TT': r.TColor.GetColor(155,152,204),
#                 'QCD': r.TColor.GetColor(250,202,255),
                "ZTT": r.TColor.GetColor(248,206,104),
                }


stackOrder = ["VV", "WJets", 'TT', 'QCD', "ZTT"]
stackOrder = ["ZTT"]

def saveROCCurve(sigHist, bkgHist):
    roc = r.TGraph(3)
    nBins = sigHist.GetNbinsX()
    sigTotal = sigHist.Integral()
    bkgTotal = bkgHist.Integral()
    print "roc"
    for i in range(nBins+1):
        x = 1. - sigHist.Integral(0,nBins-i)/sigTotal
        y = bkgHist.Integral(0, nBins-i)/bkgTotal
        print "%.4f %.4f" %(x, y)
        roc.SetPoint(i, x, y)
    return roc

def varInfo(varName):
    bins = []
    for i in range(12+1):
        bins.append(-2.4 + 0.4*i)
    bins2 = []
    for i in range(10+1):
        bins2.append(-3.0 + 0.6*i)
    bins3 = []
    for i in range(36+1):
        bins3.append(-1. + 0.05*i)
    bins4 = []
    for i in range(20+1):
        bins4.append(0. + 0.05*i)

    if varName == 'pt_1':
        return "Electron Pt [GeV]", array.array('d', range(30, 110, 10) + range(125, 225, 25) + range(250, 450, 50))
    elif varName == 'eta_1':
        return "Electron Eta", array.array('d', bins)
    elif varName == 'phi_1':
        return "Electron Phi", array.array('d', bins2)
    elif varName == 'm_1':
        return "Electron Mass [GeV]", array.array('d', range(30, 110, 10) + range(125, 225, 25) + range(250, 450, 50))
    elif varName == 'pt_2':
        return "Muon Pt [GeV]", array.array('d', range(30, 110, 10) + range(125, 225, 25) + range(250, 450, 50))
    elif varName == 'eta_2':
        return "Muon Eta", array.array('d', bins)
    elif varName == 'phi_2':
        return "Muon Phi", array.array('d', bins2)
    elif varName == 'met':
        return "#slash{E}_{T} [GeV]", array.array('d', range(30, 110, 10) + range(125, 225, 25) + range(250, 450, 50))
    elif varName == 'met_phi':
        return " #slash{E}_{T} phi", array.array('d', bins2)
    elif varName == 'jpt_1':
        return "pt-leading jet Pt [GeV]", array.array('d', range(30, 110, 10) + range(125, 225, 25) + range(250, 450, 50))
    elif varName == 'jeta_1':
        return "pt-leading jet Eta", array.array('d', bins)
    elif varName == 'jphi_1':
        return "pt-leading jet Phi", array.array('d', bins2)
    elif varName == 'jcsv_1':
        return "pt-leading jet CSV", array.array('d', bins3)
    elif varName == 'jpt_2':
        return "sub-pt-leading jet Pt [GeV]", array.array('d', range(30, 110, 10) + range(125, 225, 25) + range(250, 450, 50))
    elif varName == 'jeta_2':
        return "sub-pt-leading jet Eta", array.array('d', bins)
    elif varName == 'jphi_2':
        return "sub-pt-leading jet Phi", array.array('d', bins2)
    elif varName == 'jcsv_2':
        return "sub-pt-leading jet CSV", array.array('d', bins3)
    elif varName == 'pZetaCut':
        return "#zeta - 3.1x#zeta_{vis} [GeV]", array.array('d',  range(-150, 0, 50) + range(-30, 300, 20))
    elif varName == 'm_eff':
        return "m(#tau_{e}, #tau_{#mu}, #slash{E}_{T}) [GeV]", array.array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600,900])
    elif varName == 'pt_1_over_m_eff':
        return "Electron Pt/m(#tau_{e}, #tau_{#mu}, #slash{E}_{T})", array.array('d', bins4)
    elif varName == 'pt_2_over_m_eff':
        return "Muon Pt/m(#tau_{e}, #tau_{#mu}, #slash{E}_{T})", array.array('d', bins4)
    elif varName == 'BDT':
        return "BDT", array.array('d', bins3)


def getName(key):
    names = {"VV": 'VV',
             "WJets": 'W+Jets',
             "TT": 't#bar{t}',
             "QCD": 'QCD',
             "ZTT": 'Z/#gamma*#rightarrow#it{ll}'}
    return names[key]

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--logY", dest="logY", default=False, action="store_true", help="")
    parser.add_option("--width", dest="width", default=False, action="store_true", help="")
    parser.add_option("--unblind", dest="unblind", default=False, action="store_true", help="")
    parser.add_option("--addRateUnc", dest="addRateUnc", default=False, action="store_true", help="")
    parser.add_option("--showIntegral", dest="showIntegral", default=False, action="store_true", help="")
    parser.add_option("--FS", dest="FS", default='et', help="")

    options, args = parser.parse_args()
    return options

options = opts()

def getZPrimeXS(mass):
    xs = {'500': (9.33, 1),
          '1000': (0.468, 10),
          '1500': (0.0723*1.3, 10),
          '2000': (0.0173, 100),
          '2500': (0.00554, 100),
          '3000': (0.00129, 1000),
          '3500': (0.00049, 1000),
          '4000': (0.000255, 1000),
          '4500': (0.000108, 10000),
          '5000': (0.0000559, 10000),
        }
    return xs[mass]

def getLatex(name):
    if name == 't':
        return '#tau_{h}'
    elif name == 'm':
        return '#tau_{#mu}'
    elif name == 'e':
        return '#tau_{e}'
    else:
        return '%s, not supported' %name

def getFinalStateLatex(FS):
    return (getLatex(FS[0]) + getLatex(FS[1]))

def setRatioCanvas(hist, fs, varText):
    fakeHist = r.TH1F('fakeHist', '', hist.GetNbinsX(), hist.GetBinLowEdge(1), hist.GetBinLowEdge(hist.GetNbinsX()+1))
    fakeHist.SetMaximum(1.99)
    fakeHist.SetMinimum(0)
    secondLeg = '#tau_{h}'
    if fs == 'em':
        secondLeg = '#tau_{#mu}'
        fakeHist.SetTitle(' ;m(#tau_{e}, %s, #slash{E}_{T}) [GeV]; Obs / Bkg' %secondLeg)

    elif fs == 'mt':
        fakeHist.SetTitle(' ;m(#tau_{#mu}, %s, #slash{E}_{T}) [GeV]; Obs / Bkg' %secondLeg)
    elif fs == 'et':
        fakeHist.SetTitle(' ;m(#tau_{e}, %s, #slash{E}_{T}) [GeV]; Obs / Bkg' %secondLeg)
    else:
        fakeHist.SetTitle(' ;m(#tau_{h} #tau_{h}, #slash{E}_{T}) [GeV]; Obs / Bkg')

    fakeHist.SetTitle(' ; %s; Obs / Bkg' %varText)


    fakeHist.GetXaxis().SetLabelFont(42)
    fakeHist.GetXaxis().SetTitleFont(42)
    fakeHist.GetXaxis().SetLabelSize(0.11)
    fakeHist.GetXaxis().SetTitleSize(0.12)
    fakeHist.GetXaxis().SetTitleOffset(0.9)
    fakeHist.GetXaxis().SetLabelOffset(0.007)

    fakeHist.GetYaxis().SetTitleFont(42)
    fakeHist.GetYaxis().SetLabelFont(42)
    fakeHist.GetYaxis().SetLabelSize(0.11)
    fakeHist.GetYaxis().SetNdivisions(5,5,0)
    fakeHist.GetYaxis().SetTitleSize(0.13)
    fakeHist.GetYaxis().SetTitleOffset(0.44)
    fakeHist.GetYaxis().SetLabelOffset(0.012)

    fakeHist.GetYaxis().CenterTitle()

    return fakeHist


def buildHisto(file, hist, sum_b, varName):
    tfile = r.TFile(file)    
    tree = tfile.Get('eventTree_test')
    nEntries = tree.GetEntries()
    nBins = hist.GetNbinsX()
    for i in range(nEntries):
        tree.GetEntry(i)
        tool.printProcessStatus(i, nEntries, 'Looping sample %s' %(file), i-1)
        if varName == 'pt_1_over_m_eff':
            if getattr(tree, 'm_eff') <= 0:
                value = 0
            else:
                value = getattr(tree, 'pt_1')/getattr(tree, 'm_eff')
        elif varName == 'pt_2_over_m_eff':
            if getattr(tree, 'm_eff') <= 0:
                value = 0
            else:
                value = getattr(tree, 'pt_2')/getattr(tree, 'm_eff')
        else:
            value = getattr(tree, varName)
        if value < hist.GetBinLowEdge(1):
            value = (hist.GetBinLowEdge(1) + hist.GetBinLowEdge(2))/2.0
        elif value > hist.GetBinLowEdge(nBins+1):
            value = (hist.GetBinLowEdge(nBins) + hist.GetBinLowEdge(nBins+1))/2.0
        hist.Fill(value, tree.weightWithPU)
        if sum_b != 0:
            sum_b.Fill(value, tree.weightWithPU)
    print ''
    return hist, sum_b


def buildStack(histDict):
    stack = r.THStack()
    for ikey in stackOrder:
        if options.width:
            histDict[ikey].Scale(1, 'width')
        stack.Add(histDict[ikey])
    return stack


def buildUnc(inputHist):
    hist = inputHist.Clone()
    hist.Sumw2()
#     if options.width:
#         hist.Scale(1, 'width')
    n = hist.GetNbinsX()
    x = array.array('d')
    y = array.array('d')
    exl = array.array('d')
    exh = array.array('d')
    eyl = array.array('d')
    eyh = array.array('d')
    y_rel = array.array('d')
    eyl_rel = array.array('d')
    eyh_rel = array.array('d')
    for i in range(1, n+1):
        xValue = hist.GetBinCenter(i)
        xError = xValue - hist.GetBinLowEdge(i)
        yValue = hist.GetBinContent(i)
        yError = hist.GetBinError(i)
        x.append(xValue)
        y.append(yValue)
        exl.append(xError)
        exh.append(xError)
        y_rel.append(1.0)
        if xError != 0 and yValue != 0:
            eyl.append(yError)
            eyh.append(yError)
            eyl_rel.append(yError/yValue)
            eyh_rel.append(yError/yValue)
        else:
            eyl.append(0.0)
            eyh.append(0.0)
            eyl_rel.append(0.0)
            eyh_rel.append(0.0)

    gr = r.TGraphAsymmErrors(n,x,y,exl,exh,eyl,eyh)
    gr.SetFillColor(r.kGray+2)
    gr.SetLineColor(r.kGray+2)
    gr.SetFillStyle(3344)
    gr_rel = r.TGraphAsymmErrors(n,x,y_rel,exl,exh,eyl_rel,eyh_rel)
    gr_rel.SetFillColor(r.kGray)
    gr_rel.SetLineColor(r.kGray)
    gr_rel.SetFillStyle(3344)

    return gr, gr_rel

def buildRatio(histDict):
    nbins = histDict['obs'].GetNbinsX()
    ratio = histDict['obs'].Clone()
    ratio.SetMarkerStyle(8)
    ratio.SetMarkerSize(0.7)
    ratio.SetLineColor(r.kBlack)
    for i in range(1, nbins+1):
        sum_b = histDict['sum_b'].GetBinContent(i)
        obs = histDict['obs'].GetBinContent(i)
        if sum_b > 0 and obs > 0:
            ratio.SetBinContent(i, obs/sum_b)
            ratio.SetBinError(i, histDict['obs'].GetBinError(i)/sum_b)
            if options.addRateUnc:
                ratio.SetBinError(i, 0.00001)
    return ratio



def setLegend(position, histDict, option = 'width', mass = '500'):
    histList = []
    nbins = histDict['obs'].GetNbinsX()

    if options.unblind:
        if options.showIntegral:
            histList.append((histDict['obs'], 'Observed (%.2f)' %histDict['obs'].Integral(0, nbins+1, option), 'lep'))
        else:
            histList.append((histDict['obs'], 'Observed', 'lep'))
    else:
        histList.append((histDict['obs'], 'Observed', 'lep'))

    for ikey in reversed(stackOrder):
        name = getName(ikey)
        if options.showIntegral:
            histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)), 'f'))
        else:
            histList.append((histDict[ikey], '%s' %(name), 'f'))

    integral = histDict['signal'].Integral(0, nbins+1, option)
    multiplication = ''
    if getZPrimeXS(str(mass))[1] > 1:
        multiplication = '%i x ' %getZPrimeXS(str(mass))[1]
    
    if options.showIntegral:
        histList.append((histDict['signal'], '%sZPrime_%s (%.2f)' %(multiplication, mass, integral), 'l'))
    else:
        histList.append((histDict['signal'], "%sZ'(%s)#rightarrow #tau#tau" %(multiplication, mass), 'l'))

    return tool.setMyLegend(position, histList)

def plot(inputFileDir, fs, mass, varName):
    varText, varBins = varInfo(varName)

    sampleCats = [
#     ('WJets', '%s/WJets_LO_HT-0to100_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('WJets', '%s/WJets_LO_HT-100to200_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('WJets', '%s/WJets_LO_HT-200to400_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('WJets', '%s/WJets_LO_HT-400to600_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('WJets', '%s/WJets_LO_HT-600toInf_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
# 
#     ('ZTT', '%s/DY-50to200_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('ZTT', '%s/DY-200to400_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('ZTT', '%s/DY-400to500_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
    ('ZTT', '%s/DY-500to700_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
    ('ZTT', '%s/DY-700to800_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
    ('ZTT', '%s/DY-800to1000_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
    ('ZTT', '%s/DY-1000to1500_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
# 
#     ('VV', '%s/WZTo1L3Nu_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('VV', '%s/WWTo1L1Nu2Q_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('VV', '%s/WZTo1L1Nu2Q_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('VV', '%s/WZJets_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('VV', '%s/ZZTo2L2Q_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('VV', '%s/WZTo2L2Q_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('VV', '%s/VVTo2L2Nu_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('VV', '%s/ZZTo4L_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
# 
#     ('TT', '%s/antiT_t-channel_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('TT', '%s/T_t-channel_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('TT', '%s/antiT_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('TT', '%s/T_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#     ('TT', '%s/TTJets_LO_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
    ('obs', '%s/data_Electron_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
    ('signal', '%s/ZPrime_%s_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir, mass, fs)),
    ]

    histDict = {}
    for iCat in stackOrder:
        histDict[iCat] = r.TH1F("%s_%s" %(iCat, varName), "", len(varBins)-1, varBins)
        histDict[iCat].SetFillColor(defaultOrder[iCat])
        histDict[iCat].SetMarkerColor(defaultOrder[iCat])
        histDict[iCat].SetMarkerStyle(21)
        histDict[iCat].SetLineColor(r.kBlack)
        histDict[iCat].Sumw2()
    histDict['signal'] = r.TH1F("signal_%s" %(varName), "", len(varBins)-1, varBins)
    histDict['signal'].SetLineStyle(2)
    histDict['signal'].SetLineColor(r.kBlue)
    histDict['signal'].Sumw2()
    histDict['obs'] = r.TH1F("obs_%s" %(varName), "", len(varBins)-1, varBins)
    histDict["obs"].SetMarkerStyle(8)
    histDict["obs"].SetMarkerSize(0.7)
    histDict["obs"].SetLineColor(r.kBlack)
    histDict["obs"].Sumw2()

    histDict['sum_b'] = r.TH1F("sum_b_%s" %(varName), "", len(varBins)-1, varBins)
    histDict['sum_b'].Sumw2()

    for iCat, iFile in sampleCats:
        if iCat == 'obs' or iCat == "signal":
            histDict[iCat], fake = buildHisto(iFile, histDict[iCat], 0, varName)
        else:
            histDict[iCat], histDict['sum_b'] = buildHisto(iFile, histDict[iCat], histDict['sum_b'], varName)

    histDict['signal'].Scale(getZPrimeXS(mass)[0]*getZPrimeXS(mass)[1])

    ratio = buildRatio(histDict)
    if options.width:
        histDict['sum_b'].Scale(1, 'width')
    uncShape, uncShape_rel = buildUnc(histDict['sum_b'])
    stack = buildStack(histDict)
    stack.SetTitle(';  ;Events')

    option = ''
    if options.width:
        option = 'width'
        stack.SetTitle(';  ;Events / GeV')
        histDict['obs'].Scale(1, 'width')
        histDict['signal'].Scale(1, 'width')

    psfile = '%s_ZPrime%s_%s.pdf' %(varName, mass, fs)
    if options.addRateUnc:
        psfile = psfile[:psfile.rfind('.')] + '_withRateUnc.pdf'
#     c = r.TCanvas("c","Test", 600, 800)

#     c_up = r.TPad("c_up","c_up", 0., 1, 1., 0.3)
#     c_low = r.TPad("c_down","c_down", 0.,0.3,1.,0.06)
# 
#     c_up.SetMargin(1, 1, 0, 0.1)
#     c_low.SetMargin(1, 1, 0.2, 0)
#################
    c = r.TCanvas("c","Test",600, 600)
    c.Range(0,0,1,1)
    c.SetFillColor(0)

    c.SetBorderMode(0)
    c.SetBorderSize(3)
    c.SetTickx(1)
    c.SetTicky(1)
    c.SetLeftMargin(0.15)
    c.SetRightMargin(0.05)
    c.SetTopMargin(0.05)
    c.SetBottomMargin(0.15)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)

    c_low = r.TPad("c1_1", "newpad",0.01,0,0.99,0.32)
    c_low.Range(-200,-2.720435,1133.333,3.047681)
    c_low.SetFillColor(0)
    c_low.SetFillStyle(4000)
    c_low.SetBorderMode(0)
    c_low.SetBorderSize(2)
    c_low.SetTickx(1)
    c_low.SetTicky(1)
    c_low.SetLeftMargin(0.15)
    c_low.SetTopMargin(0.01)
    c_low.SetBottomMargin(0.3)
    c_low.SetFrameFillStyle(0)
    c_low.SetFrameBorderMode(0)
    c_low.SetFrameFillStyle(0)
    c_low.SetFrameBorderMode(0)


    c_up = r.TPad("c1_2", "newpad",0.01,0.33,0.99,0.99)
    c_up.Range(-200,-13.87376,1133.333,1389.866)
    c_up.SetFillColor(0)
    c_up.SetBorderMode(0)
    c_up.SetBorderSize(2)
    c_up.SetTickx(1)
    c_up.SetTicky(1)
    c_up.SetLeftMargin(0.15)
    c_up.SetBottomMargin(0.01)
    c_up.SetFrameFillStyle(0)
    c_up.SetFrameBorderMode(0)
    c_up.SetFrameFillStyle(0)
    c_up.SetFrameBorderMode(0)


#################
    c_up.Draw()
    c_low.Draw()
    c_up.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    if options.logY:
        r.gPad.SetLogy()
        iMax = 100*stack.GetMaximum()
    else:
        iMax = stack.GetMaximum()
    iMin = 0.005
    stack.SetMaximum(iMax)
    stack.SetMinimum(iMin)
    stack.Draw('hist H')

    stack.GetYaxis().SetLabelFont(42)
    stack.GetYaxis().SetLabelOffset(0.007)

    stack.GetYaxis().SetNdivisions(510)
    stack.GetYaxis().SetTitleOffset(0.8)
    stack.GetYaxis().SetTitleSize(0.075)
    stack.GetYaxis().SetLabelSize(0.05)
    stack.GetXaxis().SetNdivisions(510)
    stack.GetXaxis().SetLabelOffset(10)


    uncShape.Draw('2 same')
    histDict['signal'].Draw('same hist')    
    if options.unblind:
        histDict['obs'].Draw('same e1p')    


    cmsText     = "CMS";
    cmsTextFont   = 61  
    extraText   = "Preliminary"
    extraTextFont = 52 
    lumiText = "2.2 fb^{-1} (13 TeV)"
    lumiTextSize     = 0.6
    lumiTextOffset   = 0.2
    cmsTextSize      = 0.75
    cmsTextOffset    = 0.1
    relPosX    = 0.045
    relPosY    = 0.035
    relExtraDY = 1.2
    t = c_up.GetTopMargin()
    l = c_up.GetLeftMargin()
    ri = c_up.GetRightMargin()
    b = c_up.GetBottomMargin()

    extraOverCmsTextSize  = 0.76
    latex = r.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(r.kBlack)    
    extraTextSize = extraOverCmsTextSize*cmsTextSize

    latex.SetTextFont(42)
    latex.SetTextAlign(31) 
    latex.SetTextSize(lumiTextSize*t)    
    latex.DrawLatex(1-ri,1-t+lumiTextOffset*t,lumiText)
    latex.SetTextFont(cmsTextFont)
    latex.SetTextAlign(11) 
    latex.SetTextSize(cmsTextSize*t)   
    latex.DrawLatex(l,1-t+lumiTextOffset*t,cmsText)
    posX_ =  l +  relPosX*(2.7-l-ri)
    posY_ = 1-t+lumiTextOffset*t
    align_ = 11
    latex.SetTextFont(extraTextFont)
    latex.SetTextSize(extraTextSize*t)
    latex.SetTextAlign(align_)
    latex.DrawLatex(posX_, posY_, extraText)  


    #Draw Legend
    position  = (0.55, 0.85 - 0.06*6, 0.87, 0.85)
    legends = setLegend(position, histDict, option, mass)
    legends.Draw('same')

    latex = r.TLatex()
    latex.SetTextSize(0.05)
#     latex.DrawLatex(180, iMax*0.98, getFinalStateLatex(fs))

    c_low.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    fakeHist = setRatioCanvas(histDict["obs"], fs, varText)
    fakeHist.Draw()
    
    line = r.TLine(histDict["obs"].GetBinLowEdge(1), 1.0, histDict["obs"].GetBinLowEdge(histDict["obs"].GetNbinsX()+1), 1)
    line.Draw('same')
    line.SetLineColor(r.kRed)

#     c_low.SetGridy(1)
    uncShape_rel.Draw('2')
    if options.unblind:
        ratio.Draw('same e1p')
    c.Print('%s(' %psfile)

    #ROC Curve
    c.Clear()
    roc = saveROCCurve(histDict["signal"], histDict["sum_b"])
    fakeHist2 = r.TH1F("fake", "", 1, 0, 1.05)
    fakeHist2.SetMaximum(1.05)
    fakeHist2.GetYaxis().SetTitleOffset(1.1)

    fakeHist2.SetTitle("ROC; signal effeciency; background rejection")
    fakeHist2.Draw()
    roc.Draw("PLsame")
    c.Print('%s)' %psfile)
    

print options.FS

m = 2000
varName = "pZetaCut"
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), varName)
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'pt_1')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'pt_2')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'jpt_1')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'jpt_2')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'met')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'm_eff')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'pZetaCut')
plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'pt_1_over_m_eff')

# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'eta_1')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'phi_1')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'eta_2')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'phi_2')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'jeta_1')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'jphi_1')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'jeta_2')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'jphi_2')
# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'met_phi')

# plot("/user_data/zmao/TMVA/normal/2000/", options.FS, str(m), 'BDT')
