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

defaultOrder = {"VV": r.TColor.GetColor(222, 90,106),
                "W":  r.TColor.GetColor(100,182,232),
                'TT': r.TColor.GetColor(155,152,204),
                'QCD': r.TColor.GetColor(250,202,255),
                "ZTT": r.TColor.GetColor(248,206,104),
                }


stackOrder = ["VV", "W", 'TT', 'QCD', "ZTT"]


variations = {'et': ['_CMS_zp_scale_btag_13TeV', '_CMS_zp_scale_j_13TeV', '_CMS_zp_scale_t_13TeV', '_CMS_zp_pdf_13TeV'],
              'em': ['_CMS_zp_scale_btag_13TeV', '_CMS_zp_scale_j_13TeV', '_CMS_zp_pdf_13TeV', '_CMS_zp_topPt_13TeV'],
              'mt': [],
              'tt': [],

                }

additionalUnc = {'et': {'W': 0.014/0.146, 'QCD': 0.021/0.128, 'TT': 0.1, 'ZTT': 0.1, 'VV': 0.15},
                 'em': {'W': 0.030/0.073, 'QCD': 0.075/0.201, 'TT': 0.1, 'ZTT': 0.1, 'VV': 0.15},
                 'mt': {'W': 0., 'QCD': 0., 'TT': 0., 'ZTT': 0., 'VV': 0.},
                 'tt': {'W': 0., 'QCD': 0., 'TT': 0., 'ZTT': 0., 'VV': 0.},
                }

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

def getName(key):
    names = {"VV": 'VV',
             "W": 'W+Jets',
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

def buildHistos(file, fs):
    sumErrSquareUp = []
    sumErrSquareDown = []
    dir = 'eleTau_inclusive/'
    if fs == 'mt':
        dir = 'muTau_inclusive/'
    elif fs == 'em':
        dir = 'emu_inclusive/'
    elif fs == 'tt':
        dir = 'tauTau_inclusive/'
    tmpHists = {}
    tmpHists['sum_b'] = file.Get(dir+'VV').Clone()
    tmpHists['sum_b'].Sumw2()

#     tmpHists['sum_b'] = file.Get(dir+'sum_b').Clone()

    for iBKG in stackOrder:
        if iBKG != 'VV':
            tmpHists['sum_b'].Add(file.Get(dir+iBKG))

    tmpHists["data_obs"] = file.Get(dir+'data_obs').Clone()
    tmpHists["data_obs"].SetMarkerStyle(8)
    tmpHists["data_obs"].SetMarkerSize(0.7)
    tmpHists["data_obs"].SetLineColor(r.kBlack)

    for m in range(500, 3500, 500):
        tmpHists['ggH'+str(m)] = file.Get(dir+'ggH'+str(m)).Clone()
        tmpHists['ggH'+str(m)].Sumw2()
        tmpHists['ggH'+str(m)].Scale(getZPrimeXS(str(m))[0]*getZPrimeXS(str(m))[1])
        tmpHists['ggH'+str(m)].SetLineStyle(2)
        tmpHists['ggH'+str(m)].SetLineColor(r.kBlue)

    for ikey in defaultOrder.keys():
        print dir+ikey
        tmpHists[ikey] = file.Get(dir+ikey).Clone()
        nBins = tmpHists[ikey].GetNbinsX()
        tmpHists[ikey].SetFillColor(defaultOrder[ikey])
        tmpHists[ikey].SetMarkerColor(defaultOrder[ikey])
        tmpHists[ikey].SetMarkerStyle(21)
        tmpHists[ikey].SetLineColor(r.kBlack)
        addUnc = 0.0
        if ikey in additionalUnc[fs].keys():
            addUnc = additionalUnc[fs][ikey]

        if len(sumErrSquareUp) == 0:
            sumErrSquareUp = [0.0 for x in range(nBins)]
            sumErrSquareDown = [0.0 for x in range(nBins)]


        for iBin in range(1, nBins + 1):
            origError = tmpHists[ikey].GetBinError(iBin)
            origContent = tmpHists[ikey].GetBinContent(iBin)

            sumErrSquareUp[iBin-1] += origError*origError + (addUnc*origContent)**2
            sumErrSquareDown[iBin-1] += origError*origError + (addUnc*origContent)**2
            if options.addRateUnc:
                sumErrSquareUp[iBin-1] += origContent
                sumErrSquareDown[iBin-1] += origContent
            if ikey != "QCD" and ikey != 'W':
                for iVariation in variations[fs]:
                    tmpVarHistUp = file.Get(dir+ikey+iVariation+'Up').Clone()
                    tmpVarHistDown = file.Get(dir+ikey+iVariation+'Down').Clone()
                    varUpDiff = tmpVarHistUp.GetBinContent(iBin) - origContent
                    varDownDiff = tmpVarHistDown.GetBinContent(iBin) - origContent

                    if varUpDiff*varDownDiff > 0: #if they're the same direction
                        if varUpDiff > 0: #they both vary upwards
                            sumErrSquareUp[iBin-1] += varUpDiff > varDownDiff and varUpDiff**2 or varDownDiff**2
                        else: #they both vary downards:
                            sumErrSquareDown[iBin-1] += varUpDiff > varDownDiff and varDownDiff**2 or varUpDiff**2
                    else:   #different direction
                        sumErrSquareUp[iBin-1] += varUpDiff > 0 and varUpDiff**2 or varDownDiff**2
                        sumErrSquareDown[iBin-1] += varDownDiff < 0 and varDownDiff**2 or varUpDiff**2
    return tmpHists, sumErrSquareUp, sumErrSquareDown


def buildUnc(inputHist, sumErrSquareUp, sumErrSquareDown):
    hist = inputHist.Clone()
    hist.Sumw2()
    if options.width:
        hist.Scale(1, 'width')
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
        x.append(xValue)
        y.append(yValue)
        exl.append(xError)
        exh.append(xError)
        y_rel.append(1.0)
        if xError != 0 and yValue != 0:
            if options.width:
                eyl.append(math.sqrt(sumErrSquareDown[i-1])/(2.*xError))
                eyh.append(math.sqrt(sumErrSquareUp[i-1])/(2.*xError))
                eyl_rel.append(math.sqrt(sumErrSquareDown[i-1])/(2.*xError*yValue))
                eyh_rel.append(math.sqrt(sumErrSquareUp[i-1])/(2.*xError*yValue))
            else:
                eyl.append(math.sqrt(sumErrSquareDown[i-1]))
                eyh.append(math.sqrt(sumErrSquareUp[i-1]))
                eyl_rel.append(math.sqrt(sumErrSquareDown[i-1])/(yValue))
                eyh_rel.append(math.sqrt(sumErrSquareUp[i-1])/(yValue))
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


def setRatioCanvas(hist, fs):
    fakeHist = r.TH1F('fakeHist', '', hist.GetNbinsX(), hist.GetBinLowEdge(1), hist.GetBinLowEdge(hist.GetNbinsX()+1))
    fakeHist.SetMaximum(2.99)
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

def buildStack(histos):
    stack = r.THStack()
    for ikey in stackOrder:
        if options.width:
            histos[ikey].Scale(1, 'width')
        stack.Add(histos[ikey])
    return stack

def buildRatio(histDict):
    nbins = histDict['data_obs'].GetNbinsX()
    ratio = histDict['data_obs'].Clone()
    ratio.SetMarkerStyle(8)
    ratio.SetMarkerSize(0.7)
    ratio.SetLineColor(r.kBlack)
    for i in range(1, nbins+1):
        sum_b = histDict['sum_b'].GetBinContent(i)
        data_obs = histDict['data_obs'].GetBinContent(i)
        if sum_b > 0 and data_obs > 0:
            ratio.SetBinContent(i, data_obs/sum_b)
            ratio.SetBinError(i, histDict['data_obs'].GetBinError(i)/sum_b)
            if options.addRateUnc:
                ratio.SetBinError(i, 0.00001)
    return ratio

def changeUnc(hist):
    nbins = hist.GetNbinsX()
    for i in range(1, nbins+1):
        hist.SetBinError(i, 0.00000001)

def fixUnc(hist):
    nbins = hist.GetNbinsX()
    for i in range(1, nbins+1):
        if hist.GetBinError(i) < 0.000000001:
            hist.SetBinError(i, math.sqrt(hist.GetBinContent(i)))

def setLegend(position, histDict, option = 'width', mass = '500'):
    histList = []
    nbins = histDict['data_obs'].GetNbinsX()

    if options.unblind:
        if options.showIntegral:
            histList.append((histDict['data_obs'], 'Observed (%.2f)' %histDict['data_obs'].Integral(0, nbins+1, option), 'lep'))
        else:
            histList.append((histDict['data_obs'], 'Observed', 'lep'))
    else:
        histList.append((histDict['data_obs'], 'Observed', 'lep'))

    for ikey in reversed(stackOrder):
        name = getName(ikey)
        if options.showIntegral:
            histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)), 'f'))
        else:
            histList.append((histDict[ikey], '%s' %(name), 'f'))

    integral = histDict['ggH%s' %mass].Integral(0, nbins+1, option)
    multiplication = ''
    if getZPrimeXS(str(mass))[1] > 1:
        multiplication = '%i x ' %getZPrimeXS(str(mass))[1]
    
    if options.showIntegral:
        histList.append((histDict['ggH%s' %mass], '%sZPrime_%s (%.2f)' %(multiplication, mass, integral), 'l'))
    else:
        histList.append((histDict['ggH%s' %mass], "%sZ'(%s)#rightarrow #tau#tau" %(multiplication, mass), 'l'))

    return tool.setMyLegend(position, histList)

def plot(inputFile, fs, mass = '500'):
    file = r.TFile(inputFile)

    histos, sumErrSquareUp, sumErrSquareDown = buildHistos(file, fs)

    if options.addRateUnc:
        changeUnc(histos['data_obs'])
    else:
        fixUnc(histos['data_obs'])

    ratio = buildRatio(histos)

    uncShape, uncShape_rel = buildUnc(histos['sum_b'], sumErrSquareUp, sumErrSquareDown)
    stack = buildStack(histos)
    stack.SetTitle(';  ;Events')

    option = ''
    if options.width:
        option = 'width'
        stack.SetTitle(';  ;Events / GeV')
        histos['data_obs'].Scale(1, 'width')
        histos['ggH%s' %mass].Scale(1, 'width')

    psfile = 'bkgTemplate_ZPrime%s_%s.pdf' %(mass, fs)
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

    iMax = 100#= 1.2*max(stack.GetMaximum(), histos["data_obs"].GetMaximum())
    iMin = 0.005
    iMax = iMax/(1+0.2*r.TMath.Log10(iMax/iMin))
    iMin = iMin/(1+0.5*r.TMath.Log10(iMax/iMin))
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
    histos['ggH%s' %mass].Draw('same hist')    
    if options.unblind:
        histos['data_obs'].Draw('same e1p')    


    cmsText     = "CMS";
    cmsTextFont   = 61  
    extraText   = ''#"Preliminary"
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
    legends = setLegend(position, histos, option, mass)
    legends.Draw('same')

    latex = r.TLatex()
    latex.SetTextSize(0.05)
    latex.DrawLatex(180, iMax*0.98, getFinalStateLatex(fs))

    c_low.cd()
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    fakeHist = setRatioCanvas(histos["data_obs"], fs)
    fakeHist.Draw()
    
    line = r.TLine(histos["data_obs"].GetBinLowEdge(1), 1.0, histos["data_obs"].GetBinLowEdge(histos["data_obs"].GetNbinsX()+1), 1)
    line.Draw('same')
    line.SetLineColor(r.kRed)

#     c_low.SetGridy(1)
    uncShape_rel.Draw('2')
    if options.unblind:
        ratio.Draw('same e1p')
    c.Print('%s' %psfile)
print options.FS
m = 1500
# plot("/home/zmao/CMSSW_7_2_4/src/samples-plots/htt_%s.inputs-Zp-13TeV.root" %(options.FS), options.FS, str(m))

plot("/home/elaird/CMSSW_7_1_5/src/auxiliaries/shapes/Brown/htt_%s.inputs-Zp-13TeV.root" %(options.FS), options.FS, str(m))
# for m in range(500, 5500, 500):
#     plot("/home/elaird/htt_%s.inputs-Zp-13TeV_v2.root" %(options.FS), options.FS, str(m))
