#!/usr/bin/env python

import ROOT as r
import plots_cfg
import tool
import optparse
import array
import math
import cutSampleTools
import numpy as np
from scipy.optimize import fsolve
from makeWholeTools2 import calcSysUnc
from array import array
import cProfile

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
l_1 = lvClass()
l_2 = lvClass()
jet = lvClass()
met = lvClass()


lumi = 12891.5#5892.1#5939.2#3990.0#2093.30#1546.91#1263.89#552.67#654.39#209.2#16.86, 578.26
# lumi = 4353.4#2646.0
# lumi = 5892.1
Lumi = lumi #3000.0
signalScale = 10

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
    parser.add_option("--BSM3G", dest="BSM3G", default=False, action="store_true", help="")
    parser.add_option("--saveHisto", dest="saveHisto", default=False, action="store_true", help="")
    parser.add_option("--noIso", dest="noIso", default=False, action="store_true", help="")
    parser.add_option("--ratio", dest="ratio", default=False, action="store_true", help="")
    parser.add_option("--logY", dest="logY", default=False, action="store_true", help="")
    parser.add_option("--method", dest="method", default='SS', help="")
    parser.add_option("--chi2", dest="chi2", default=False, action="store_true", help="")
    parser.add_option("--KS", dest="KS", default=False, action="store_true", help="")
    parser.add_option("--noWJets", dest="noWJets", default=False, action="store_true", help="")
    parser.add_option("--overFlow", dest="overFlow", default=False, action="store_true", help="")
    parser.add_option("--highMETlowPZeta", dest="highMETlowPZeta", default=False, action="store_true", help="")
    parser.add_option("--highMETlowPZeta0NB", dest="highMETlowPZeta0NB", default=False, action="store_true", help="")
    parser.add_option("--lowMET", dest="lowMET", default=False, action="store_true", help="")
    parser.add_option("--lowMET0NB", dest="lowMET0NB", default=False, action="store_true", help="")
    parser.add_option("--signalRegion", dest="signalRegion", default=False, action="store_true", help="")
    parser.add_option("--signalRegionReverseNCSVJets", dest="signalRegionReverseNCSVJets", default=False, action="store_true", help="")
    parser.add_option("--signalRegionReverseCosPhi", dest="signalRegionReverseCosPhi", default=False, action="store_true", help="")
    parser.add_option("--signalRegionReversePZeta", dest="signalRegionReversePZeta", default=False, action="store_true", help="")
    parser.add_option("--signalRegionLowMET", dest="signalRegionLowMET", default=False, action="store_true", help="")
    parser.add_option("--prong2", dest="prong2", default=False, action="store_true", help="")
    parser.add_option("--prong1", dest="prong1", default=False, action="store_true", help="")
    parser.add_option("--prong3", dest="prong3", default=False, action="store_true", help="")
    parser.add_option("--prong1_3", dest="prong1_3", default=False, action="store_true", help="")
    parser.add_option("--sys", dest="sys", default="", help=", tauECUp, tauECDown, jetECUp, jetECDown, bScaleUp, bScaleDown")
    parser.add_option("--diffQCD", dest="diffQCD", default=False, action="store_true", help="")
    parser.add_option("--getWJetsSF", dest="getWJetsSF", default=False, action="store_true", help="")
    parser.add_option("--dynamicQCDSF", dest="dynamicQCDSF", default=False, action="store_true", help="")
    parser.add_option("--addRateUnc", dest="addRateUnc", default=False, action="store_true", help="")
    parser.add_option("--test", dest="test", default=False, action="store_true", help="")
    parser.add_option("--plotRegionC", dest="plotRegionC", default=False, action="store_true", help="")
    parser.add_option("--plotRegionF", dest="plotRegionF", default=False, action="store_true", help="")
    parser.add_option("--useMCWJetsSF", dest="useMCWJetsSF", default=False, action="store_true", help="")
    parser.add_option("--useMCWJetsYield", dest="useMCWJetsYield", default=False, action="store_true", help="")
    parser.add_option("--ignoreMCinEF", dest="ignoreMCinEF", default=False, action="store_true", help="")
    parser.add_option("--getQCDFromE", dest="getQCDFromE", default=False, action="store_true", help="")
    parser.add_option("--saveSignalHist", dest="saveSignalHist", default='', help="")
    parser.add_option("--saveHist", dest="saveHist", default='', help="")

    options, args = parser.parse_args()
    return options
if __name__ == "__main__":
    options = opts()


def getJets(tree):
    jets = []
    for i in range(1, 9):
        jetPt = getattr(tree, "jet%iPt" %i)
        jetEta = getattr(tree, "jet%iEta" %i)

        l_1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
        jet.SetCoordinates(jetPt, jetEta, getattr(tree, "jet%iPhi" %i), 0)
        dR_1 = r.Math.VectorUtil.DeltaR(l_1, jet)
        if dR_1 <= 0.4:
            continue
        l_2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)
        dR_2 = r.Math.VectorUtil.DeltaR(l_2, jet)
        if dR_2 > 0.4:
            jets.append(jet)
        if len(jets)>0:
            return jets
    return jets

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

def passBound(tree, FS, bound, side):
    if FS == 'et' or FS == 'mt':
        if bound == 'VTight':
            value = tree.tByVTightIsolationMVArun2v1DBnewDMwLT
        elif bound == 'Tight':
            value = tree.tByTightIsolationMVArun2v1DBnewDMwLT
        elif bound == 'Medium':
            value = tree.tByMediumIsolationMVArun2v1DBnewDMwLT
        elif bound == 'Loose':
            value = tree.tByLooseIsolationMVArun2v1DBnewDMwLT
        elif bound == 'VLoose':
            value = tree.tByVLooseIsolationMVArun2v1DBnewDMwLT
        else:
            value = True if tree.tByIsolationMVArun2v1DBnewDMwLTraw < bound else False
    elif FS == 'em':
        value = True if tree.mRelIso < bound else False
    else:
        return False
    if side == 'lower' and value == False:
        return True
    elif side == 'upper' and value == True:
        return True
    else:
        return False

def regionSelection(tree, FS, region, lowerBound = 0, upperBound = 1):
    if 'SS' in region and (tree.q_1 != tree.q_2):
        return False
    if 'OS' in region and (tree.q_1 == tree.q_2):
        return False
         
    if FS == 'et':
        if ('signal' in region) and passBound(tree, FS, lowerBound, 'upper') and (tree.eRelIso < 0.15):
            return True
        elif ('control_iso' in region) and (tree.eRelIso < 0.15) and passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
            return True
        elif ('control_anti_iso' in region) and (tree.eRelIso > 0.15) and passBound(tree, FS, lowerBound, 'lower'):
            return True
        else:
            return False
    if FS == 'mt':
        if ('signal' in region) and passBound(tree, FS, lowerBound, 'upper') and (tree.mRelIso < 0.15):
            return True
        elif ('control_iso' in region) and (tree.mRelIso < 0.15) and passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
            return True
        elif ('control_anti_iso' in region) and (tree.mRelIso > 0.15) and passBound(tree, FS, lowerBound, 'lower'):
            return True
        else:
            return False

    elif FS == 'em':
        if ('signal' in region) and (tree.eRelIso < 0.15) and (tree.mRelIso < 0.15):
            return True
        elif ('control_iso' in region) and (tree.eRelIso < 0.15) and passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
            return True
        else:
            return False
    return False

def passCut(tree, FS, isData, sys):

    if __name__ == "__main__":
        if not isData and options.ignoreMCinEF:
            if FS == 'et':
                if tree.eRelIso > 0.15:
                    return False
            if FS == 'mt':
                if tree.mRelIso > 0.15:
                    return False

        if tree.met < 10:
            return False

        if tree.nCSVL >= 1:
            return False

        if options.getWJetsSF:
            if not ( 0.5 < tree.cosDPhi_MEt_1 < 0.9 and 50 < tree.mt_1 < 120):
                return False
            if (tree.cosDPhi_MEt_2 > 0.9):
                return False
        else:
            if FS == 'mt' or FS == 'et':
                if not (tree.cosDPhi_MEt_1 > 0.9 or (tree.cosDPhi_MEt_2 > 0.9 and tree.mt_1 > 150)):
                    return False
            elif FS == 'em':
                if tree.pt_1 > tree.pt_2 and tree.cosDPhi_MEt_1 > -0.9:
                    return False
                if tree.pt_1 < tree.pt_2 and tree.cosDPhi_MEt_2 > -0.9:
                    return False
    else:
        if FS == 'mt' or FS == 'et':
            if not (tree.cosDPhi_MEt_1 > 0.9 or (tree.cosDPhi_MEt_2 > 0.9 and tree.mt_1 > 150)):
                return False
        elif FS == 'em':
            if tree.pt_1 > tree.pt_2 and tree.cosDPhi_MEt_1 > -0.9:
                return False
            if tree.pt_1 < tree.pt_2 and tree.cosDPhi_MEt_2 > -0.9:
                return False

    return True

def passUnblindPartial(varname, var):
    if varname == 'm_vis' and var <= 100:
        return True
    if varname == 'pZeta - 3.1pZetaVis' and var <=-50:
        return True
    if varname == 'pfMetEt' and var <= 30:
        return True
    if varname == 'mRelIso' and var > 0.15:
        return True
    return False

def getZPrimeXS(mass):
    xs = {'500': 9.33,
          '750': 1.0,
          '1000': 0.468,
          '1500': 0.0723*10,
          '1750': 1.0,
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
            hist.SetBinError(i, abs(hist.GetBinContent(i)) + hist.GetBinError(i))
            hist.SetBinContent(i, 0.0)
    return hist


def fixNegativeWJetsFromQCD(hist, region):
    fixedHist = hist["WJets_%s" %region].Clone()
    fixedHist = fixNegativBins(fixedHist)
    for ikey in hist.keys():
        if "QCD_%s" %region in ikey:
            hist[ikey].Add(hist["WJets_%s" %region])
            hist[ikey].Add(fixedHist, -1)


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
    if 'QCD' in cat:
        cat = 'QCD'
    for iCat, iColor in defaultOrder:
        if iCat == cat:
            return iColor
    return r.kBlue

def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates


def ratioHistogram( num, den, relErrMax=0.25) :

    def groupR(group) :
        N,D = [float(sum(hist.GetBinContent(i) for i in group)) for hist in [num,den]]
        return N/D if D else 0

    def groupErr(group) :
        N,D = [float(sum(hist.GetBinContent(i) for i in group)) for hist in [num,den]]
        ne2,de2 = [sum(hist.GetBinError(i)**2 for i in group) for hist in [num,den]]
        return math.sqrt( ne2/N**2) * N/D if N and D else 0
#         return math.sqrt( ne2/N**2 + de2/D**2 ) * N/D if N and D else 0

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
    ratio = r.TH1D("ratio"+num.GetName()+den.GetName(),"",len(groups), array('d', [num.GetBinLowEdge(min(g)) for g in groups ] + [num.GetXaxis().GetBinUpEdge(num.GetNbinsX())]) )
    for i,g in enumerate(groups) :
        ratio.SetBinContent(i+1,groupR(g))
        ratio.SetBinError(i+1,groupErr(g))
    return ratio

def loop_one_sample(iSample, iCategory, histDict, varName, varBins, FS, scanPoints):
    if options.antiIso:
        iSample += "%s_antiIso.root" %FS
    elif options.antiEIso:
        iSample += "%s_antiEIso.root" %FS
    elif options.antiMIso:
        iSample += "%s_antiMIso.root" %FS
    elif options.noIso:
        iSample += "%s_noIso.root" %FS
    elif options.BSM3G:
        iSample += "%s_noIso.root" %FS 
    else:
        iSample += "%s_inclusive.root" %FS 
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    eventCount = file.Get('eventCount')
    eventCountWeighted = file.Get('eventCountWeighted')

    sumPtWeights = -1
    if "TT" in iSample and options.sys == 'topPt':
        sumPtWeights = file.Get('eventCountPtWeighted').GetBinContent(1)

    nEntries = tree.GetEntries()
    if options.test:
        if nEntries > 100:
            nEntries = 100
    
    if options.saveSignalHist != "":
        if not ("ZPrime" in iSample):
            if nEntries > 100:
                nEntries = 100

    tmpHist = r.TH1F("tmp_%s_%s" %(iCategory, varName), '', len(varBins)-1, varBins)
    tmpHist.Sumw2()
    tmpHist_forROOTFile = r.TH1F("%s" %(varName), '', len(varBins)-1, varBins)
    tmpHist_forROOTFile.Sumw2()
    isData = False
    isSignal = False
    tree.GetEntry(0)

    if eventCount:
        initEvents = eventCount.GetBinContent(1)
    else:    
        initEvents = tree.initEvents
    if eventCountWeighted:
        sumWeights = eventCountWeighted.GetBinContent(1)
    else:    
        sumWeights = tree.initWeightedEvents

    if iCategory == 'Observed':
        isData = True
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        weight = 1.0
        QCD_weight = 1.0

        if not passCut(tree, FS, isData, options.sys):
            continue
        if not isData:
            xs  = tree.xs
            if (80.94 < xs < 80.96) or (136.01 < xs < 136.03):
                xs = xs*0.108*3

#             if "TT" in iSample:
#                 if FS == 'mt' or FS == 'et':
#                     if (not tree.tIsTauh) and (not tree.tIsPromptElectron) and (not tree.tIsPromptMuon) and (not tree.tIsTau2Electron) and (not tree.tIsTau2Muon):
#                         continue
            if options.sys == 'topPt' and sumPtWeights != -1.0:
                sumWeights = sumPtWeights
                weight = Lumi*xs*tree.genEventWeight*tree.trigweight_1*tree.trigweight_2*tree.topPtWeight/(sumWeights+0.0)
            else:
                weight = Lumi*xs*tree.genEventWeight*tree.trigweight_1*tree.trigweight_2/(sumWeights+0.0)
            if options.PUWeight:
                weight = weight*cutSampleTools.getPUWeight(tree.nTruePU)
        if "TT" in iSample:
            weight = 0.8*weight
        if 'WJets' in iSample:
            weight = 1.0*weight
        if 'ZPrime' in iSample:
            weight = getZPrimeXS(iSample[iSample.rfind("/")+8:iSample.rfind("_all")])*weight
            isSignal =  True
#         if (not isData) and (FS == 'et' or FS == 'mt'):
#             if tree.tIsTauh:
#                 weight = weight*(0.8683 + 0.0001355*tree.tPt)
#             weight = weight*(1 - (0.06 + 0.5*tree.tPt/500))
        if varName == 'm_withMET':
            value = tree.m_eff
        elif varName == 'mVis':
            value = tree.m_vis
        elif varName == 'pZeta - 3.1pZetaVis':
            value = tree.ZetaCut
        elif varName == "nCSVL":
            value = tree.nCSVL
        elif varName == "cos_phi_tau1_tau2":
            value = math.cos(tree.phi_1 - tree.phi_2)
        elif varName == "j1Pt":
            jets = getJets(tree)
            if len(jets)>0:
                value = jets[0].pt()
            else:
                value = -1
        elif varName == 'm_gen':
            if tree.eGenTauMass < 0  or tree.tGenMass < 0:
                continue
            l1.SetCoordinates(tree.eGenTauPt, tree.eGenTauEta, tree.eGenTauPhi, tree.eGenTauMass)
            l2.SetCoordinates(tree.tGenPt, tree.tGenEta, tree.tGenPhi, tree.tGenMass)
            value = (l1 + l2).mass()
        else:
            if hasattr(tree, varName):
                value = getattr(tree, varName)
            else:
                value = -1

        if options.overFlow:
            if value > varBins[len(varBins)-1]:
                value = (varBins[len(varBins)-1]+varBins[len(varBins)-2]+0.0)/2.0
            if value < varBins[0]:
                value = (varBins[0]+varBins[1]+0.0)/2.0

        if regionSelection(tree, FS, "OSsignal", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            fill = True
            if isData:
                fill = False
                if options.unblind or (options.unblindPartial and passUnblindPartial(varName, value)):
                    fill = True
                    histDict['WJets_OSsignal'].Fill(value, weight)  

            if fill:
                tmpHist.Fill(value, weight)
                tmpHist_forROOTFile.Fill(value, weight)
                if iCategory != 'WJets' and (not isData) and (not isSignal):
                    histDict['WJets_OSsignal'].Fill(value, -weight)
        else:
            if isSignal:
                continue
            #region B (SS iso tau iso lep)
            if regionSelection(tree, FS, "SSsignal", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                if not isData:
                    histDict['QCD_B'].Fill(value, -weight*QCD_weight)
                else:
                    histDict['QCD_B'].Fill(value, weight*QCD_weight)  
            #region C (OS anti-iso tau iso lep)
            if regionSelection(tree, FS, "OScontrol_iso", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                if not isData:
                    histDict['QCD_C'].Fill(value, -weight*QCD_weight)
                    if iCategory != 'WJets':
                        histDict['WJets_OScontrol_iso'].Fill(value, -weight)
                    histDict["%s_C" %iCategory].Fill(value, weight)   
                else:
                    histDict["Observed_C"].Fill(value, weight)
                    histDict['QCD_C'].Fill(value, weight*QCD_weight)
                    histDict['WJets_OScontrol_iso'].Fill(value, weight)
            #region D (SS anti-iso tau iso lep)
            if regionSelection(tree, FS, "SScontrol_iso", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                if not isData:
                    histDict['QCD_D'].Fill(value, -weight*QCD_weight)
                else:
                    histDict['QCD_D'].Fill(value, weight*QCD_weight)
            #region E (OS anti-iso tau anti-iso lep)
            if regionSelection(tree, FS, "OScontrol_anti_iso", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                if not isData:
                    histDict['QCD_E'].Fill(value, -weight*QCD_weight)
                    if options.getQCDFromE:
                        histDict['QCD_F_for_C'].Fill(value, -weight*QCD_weight)
                        histDict['QCD_F_for_A'].Fill(value, -weight*QCD_weight)
                else:
                    histDict['QCD_E'].Fill(value, weight*QCD_weight)
                    if options.getQCDFromE:
                        histDict['QCD_F_for_C'].Fill(value, weight*QCD_weight)
                        histDict['QCD_F_for_A'].Fill(value, weight*QCD_weight)
            #region F (SS anti-iso tau anti-iso lep)
            if regionSelection(tree, FS, "SScontrol_anti_iso", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                if not isData:
                    histDict["%s_F" %iCategory].Fill(value, weight)
                    histDict['QCD_F'].Fill(value, -weight*QCD_weight)
                    if not options.getQCDFromE:
                        histDict['QCD_F_for_C'].Fill(value, -weight*QCD_weight)
                        histDict['QCD_F_for_A'].Fill(value, -weight*QCD_weight)
                else:
                    histDict["Observed_F"].Fill(value, weight)   
                    histDict['QCD_F'].Fill(value, weight*QCD_weight)
                    if not options.getQCDFromE:
                        histDict['QCD_F_for_C'].Fill(value, weight*QCD_weight)
                        histDict['QCD_F_for_A'].Fill(value, weight*QCD_weight)

    print iCategory, tmpHist.Integral(0, len(varBins)+1)
    histDict[iCategory].Add(tmpHist)            

    del tmpHist
    print ''

def getError(hist, startBin, endBins):
    error = 0.0
    for i in range(startBin, endBins+1):
        error += hist.GetBinError(i)**2
    return error

def getQCDScale(histDict, varBins, method):
    result = []
    bins = [1, len(varBins)+1]
    QCD_B = histDict['QCD_B'].Integral(0, len(varBins)+1)
    QCD_C = histDict['QCD_C'].Integral(0, len(varBins)+1)
    QCD_D = histDict['QCD_D'].Integral(0, len(varBins)+1)
    QCD_E = histDict['QCD_E'].Integral(0, len(varBins)+1)
    QCD_F = histDict['QCD_F'].Integral(0, len(varBins)+1)

    QCD_B_err = getError(histDict['QCD_B'], 0, len(varBins)+1)
    QCD_C_err = getError(histDict['QCD_C'], 0, len(varBins)+1)
    QCD_D_err = getError(histDict['QCD_D'], 0, len(varBins)+1)
    QCD_E_err = getError(histDict['QCD_E'], 0, len(varBins)+1)
    QCD_F_err = getError(histDict['QCD_F'], 0, len(varBins)+1)


    print 'QCD_B: %.2f +/- %.2f' %(QCD_B, math.sqrt(QCD_B_err))
    print 'QCD_C: %.2f +/- %.2f' %(QCD_C, math.sqrt(QCD_C_err))
    print 'QCD_D: %.2f +/- %.2f' %(QCD_D, math.sqrt(QCD_D_err))
    print 'QCD_E: %.2f +/- %.2f' %(QCD_E, math.sqrt(QCD_E_err))
    print 'QCD_F: %.2f +/- %.2f' %(QCD_F, math.sqrt(QCD_F_err))

    if QCD_B > 0 and QCD_D > 0:
        if options.dynamicQCDSF:
            unc_EF = calcSysUnc(QCD_E/QCD_F, QCD_E, QCD_F, math.sqrt(QCD_E_err), math.sqrt(QCD_F_err))
            SStoOS = QCD_E/QCD_F
        else:
            unc_EF = 0.03#0.116#0.067#0.17   
            SStoOS = 1.07#1.017#1.100#1.29

        if options.getQCDFromE:
            SStoOS = 1.0
            unc_EF = 0.0000000000001

        unc_DF = calcSysUnc(QCD_D/QCD_F, QCD_D, QCD_F, math.sqrt(QCD_D_err), math.sqrt(QCD_F_err))
        unc_CF = calcSysUnc((SStoOS*QCD_D)/QCD_F, SStoOS, QCD_D/QCD_F, unc_EF, unc_DF)
        unc_BF = calcSysUnc(QCD_B/QCD_F, QCD_B, QCD_F, math.sqrt(QCD_B_err), math.sqrt(QCD_F_err))
        unc_AF = calcSysUnc((SStoOS*QCD_B)/QCD_F, SStoOS, QCD_B/QCD_F, unc_EF, unc_BF)

        if method == 'SStoOS':
            result.append((SStoOS, unc_EF))
            print 'QCD SStoOS                (%.3f, %.3f),' %(SStoOS, unc_EF)
        elif method == "FtoC":
            result.append(((SStoOS*QCD_D)/QCD_F, unc_CF))
            print 'QCD FtoC                  (%.3f, %.3f),' %((SStoOS*QCD_D)/QCD_F, unc_CF)
        else:            
            result.append(((SStoOS*QCD_B)/QCD_F, unc_AF))
            print 'QCD SR                    (%.3f, %.3f),' %((SStoOS*QCD_B)/QCD_F, unc_AF)
    else:
        print 'QCD %s                    (0, 0),' %method
        result.append((0, 0))
    return result



def buildStackFromDict(histDict, FS, option = 'width', sf = 0.1, sf_error= 0.1):
    stack = r.THStack()
    for ikey, iColor in defaultOrder:
        if ikey == 'QCD':
            ikey = 'QCD_F_for_A'
            if options.plotRegionC:
                ikey = 'QCD_F_for'
            if options.plotRegionF:
                continue
        if options.plotRegionC:
            ikey += "_C"
            if ikey in histDict.keys():
                if 'WJets' in ikey:
                    continue
                print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
                stack.Add(histDict[ikey])
        elif options.plotRegionF:
            ikey += "_F"
            if ikey in histDict.keys():
                print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
                stack.Add(histDict[ikey])
        else:
            if ikey in histDict.keys():
                if ikey == 'WJets':
                    integral, unc = IntegralAndError(histDict['WJets_OScontrol_iso'], histDict[ikey].GetNbinsX()+2, 'WJets', 'et')
                    print '%s with %.1f +/- %.1f events' %(ikey, integral, unc)
                    print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
                    print 'WJets loose2tight = %.3f +/ %.3f' %(sf, sf_error)
                    histDict['WJets_OScontrol_iso'].SetFillColor(iColor)
                    histDict['WJets_OScontrol_iso'].SetMarkerColor(iColor)
                    histDict['WJets_OScontrol_iso'].SetMarkerStyle(21)
                    histDict['WJets_OScontrol_iso'].SetLineColor(r.kBlack)
                    tmpHist = histDict['WJets_OScontrol_iso'].Clone()
                    stack.Add(tmpHist)
                else:
                    print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
                    stack.Add(histDict[ikey])

    if options.plotRegionC:
        print 'Observed in region C with %.2f events' %(histDict["Observed_C"].Integral(0, histDict["Observed_C"].GetNbinsX()+2, option))
    elif options.plotRegionF:
        print 'Observed in region F with %.2f events' %(histDict["Observed_F"].Integral(0, histDict["Observed_F"].GetNbinsX()+2, option))

    if option == 'width':
        stack.SetTitle('CMS Preliminary %.1f fb^{-1} (13 TeV); ; events / GeV' %(lumi/1000.))
    else:
        stack.SetTitle('CMS Preliminary %.1f fb^{-1} (13 TeV); ; events' %(lumi/1000.))
    return stack

def setQCD(hist, scale = 0.6, binned = False, j = 0): #force qcd to be non-negative
    iScale = scale[j][0]*Lumi/lumi
    if iScale != 0:
        iUnc = scale[j][1]/scale[j][0]
    else:
        iUnc = 0.0
    hist.Scale(iScale)
    for i in range(1, hist.GetNbinsX()+2):
        content = hist.GetBinContent(i)
#             print 'uniScale', content
        error = hist.GetBinError(i)
        error = math.sqrt(error**2 + (iUnc*content)**2)
        x = hist.GetBinCenter(i)
        hist.SetBinError(i, error)
        if content < 0:
            hist.SetBinContent(i, 0)
    return hist

def getWJetsSF(hist_signal, hist_control, varBins):
    result = []
    W_signal = hist_signal.Integral(0, len(varBins)+1)
    W_control = hist_control.Integral(0, len(varBins)+1)

    W_signal_err = getError(hist_signal, 0, len(varBins)+1)
    W_control_err = getError(hist_control, 0, len(varBins)+1)

    print "Data - otherBKG (OST): %.2f" %W_signal_err
    print "Data - otherBKG (OSL): %.2f" %W_control

    if W_signal > 0 and W_control > 0:
        unc = calcSysUnc(W_signal/W_control, W_signal, W_control, math.sqrt(W_signal_err), math.sqrt(W_control_err))
        result.append((W_signal/W_control, unc))
        print 'WJets                    (%.3f, %.3f),' %(W_signal/W_control, unc)

    else:
        print 'WJets                    (0, 0),'
        result.append((0, 0))
    return result

def setWJetsLooseShape(hist, WJets_L2T, WJets_L2T_error, bins):
    hist.Scale(WJets_L2T)
    tmpHist = hist.Clone()
    tmpHist.Sumw2()
    for i in range(1, len(bins)):
        error1 = tmpHist.GetBinError(i)
        content = tmpHist.GetBinContent(i)
        if WJets_L2T != 0 and content != 0:
            tmpHist.SetBinError(i, content*math.sqrt((WJets_L2T_error/WJets_L2T)**2 + (error1/content)**2))
    return tmpHist

def addSysUnc(hist, sampleName, bins, fs):
    tmpHist = hist.Clone()
    tmpHist.Sumw2()
    unc = 0.0
    if sampleName == 'Z#rightarrow#tau#tau' or sampleName == 't#bar{t}' or sampleName == 'WJets' or sampleName == 'Diboson':
        unc = plots_cfg.sysUnc[fs][sampleName]
    for i in range(1, len(bins)):
        error = tmpHist.GetBinError(i)
        content = tmpHist.GetBinContent(i)
        tmpHist.SetBinError(i, math.sqrt((error)**2 + (unc*content)**2))
#         tmpHist.SetBinError(i, math.sqrt((error)**2 + (unc*content)**2 + content))
    return tmpHist


def IntegralAndError(hist, nbins, sampleName, fs):
    unc = 0.0
    content = 0.0
    for i in range(0, nbins+1):
        unc += hist.GetBinError(i)*hist.GetBinError(i)
        content += hist.GetBinContent(i)
    if options.addRateUnc:
        unc += content
    unc_addition = 0.0
#     if sampleName == 'Z#rightarrow#tau#tau' or sampleName == 't#bar{t}' or sampleName == 'WJets' or sampleName == 'Diboson':
#         unc_addition = plots_cfg.sysUnc[fs][sampleName]
    unc += (unc_addition*content)**2
    unc = math.sqrt(unc)
    return content, unc

def buildDelta(deltaName, histDict, bins, varName, unit, relErrMax, min = 0.5, max = 1.5,  WJets_L2T = 0.1, WJets_L2T_error = 0, fs = 'et'):
    bkg = r.TH1F('bkg_%s' %deltaName, '', len(bins)-1, bins)
    bkg.Sumw2()
    delta = r.TH1F(deltaName, deltaName, len(bins)-1, bins)
    delta.Sumw2()
    bkg_err = r.TH1F('bkg_err_%s' %deltaName, '', len(bins)-1, bins)
    bkg_err.Sumw2()
    bkg_err.SetFillColor(r.kGray)
    bkg_err.SetLineColor(r.kGray)
    bkg_err.SetFillStyle(3344)

    bkg_err2 = r.TH1F('bkg_err2_%s' %deltaName, '', len(bins)-1, bins)
    bkg_err2.Sumw2()
    bkg_err2.SetFillColor(r.kGray+2)
    bkg_err2.SetLineColor(r.kGray+2)
    bkg_err2.SetFillStyle(3344)

    histDict_withUnc = {}

    Observed = "Observed"

    for ikey, icolor in defaultOrder:
        if ikey == 'QCD':
            ikey = 'QCD_F_for_A'
        
        if options.plotRegionC:
            Observed = "Observed_C"
            if "QCD" in ikey:
                ikey = 'QCD_F_for_C'
            else:
                if "WJets" in ikey:
                    continue
                ikey += "_C"
            if ikey in histDict.keys():
                histDict_withUnc[ikey] = r.TH1F('%s_withUnc' %ikey, '', len(bins)-1, bins)
                histDict_withUnc[ikey].Sumw2()
                bkg.Add(addSysUnc(histDict[ikey], ikey, bins, fs))
                histDict_withUnc[ikey].Add(addSysUnc(histDict[ikey], ikey, bins, fs))
        elif options.plotRegionF:
            Observed = "Observed_F"
            if 'QCD' in ikey:
                continue
            else:
                ikey += "_F"
            if ikey in histDict.keys():
                histDict_withUnc[ikey] = r.TH1F('%s_withUnc' %ikey, '', len(bins)-1, bins)
                histDict_withUnc[ikey].Sumw2()
                bkg.Add(addSysUnc(histDict[ikey], ikey, bins, fs))
                histDict_withUnc[ikey].Add(addSysUnc(histDict[ikey], ikey, bins, fs))

        else:
            if ikey in histDict.keys():
                histDict_withUnc[ikey] = r.TH1F('%s_withUnc' %ikey, '', len(bins)-1, bins)
                histDict_withUnc[ikey].Sumw2()

                if ikey != "Observed" and "ZPrime" not in ikey:
                    histDict_withUnc[ikey].SetFillColor(getColor(ikey))
                    histDict_withUnc[ikey].SetMarkerColor(getColor(ikey))
                    histDict_withUnc[ikey].SetMarkerStyle(21)
                    histDict_withUnc[ikey].SetLineColor(r.kBlack)
                if ikey == 'WJets':
                    tmpHist = setWJetsLooseShape(histDict['WJets_OScontrol_iso'], WJets_L2T, WJets_L2T_error, bins)
                    integral, unc = IntegralAndError(tmpHist, len(bins), ikey, fs)
                    print "Data-driven WJets: %.3f +/- %.3f" %(integral, unc)
                    integral, unc = IntegralAndError(histDict['WJets'], len(bins), ikey, fs)
                    print "MC WJets: %.3f +/- %.3f" %(integral, unc)
                    bkg.Add(addSysUnc(tmpHist, ikey, bins, fs))
                    histDict_withUnc[ikey].Add(addSysUnc(tmpHist, ikey, bins, fs))
                else:
                    bkg.Add(addSysUnc(histDict[ikey], ikey, bins, fs))
                    histDict_withUnc[ikey].Add(addSysUnc(histDict[ikey], ikey, bins, fs))
    for ikey in histDict.keys():
        if "ZPrime" in ikey:
            histDict_withUnc[ikey] = r.TH1F('%s_withUnc' %ikey, '', len(bins)-1, bins)
            histDict_withUnc[ikey].Sumw2()
            histDict_withUnc[ikey].SetLineStyle(2)
            histDict_withUnc[ikey].SetLineColor(r.kBlue)
            histDict_withUnc[ikey].Add(addSysUnc(histDict[ikey], ikey, bins, fs))


    for i in range(len(bins)-1):
        bkg_err.SetBinContent(i+1, 1.0)
        bkg_err2.SetBinContent(i+1, bkg.GetBinContent(i+1))
        bkg_err2.SetBinError(i+1, bkg.GetBinError(i+1))
        if bkg.GetBinContent(i+1) != 0:
            bkg_err.SetBinError(i+1, bkg.GetBinError(i+1)/bkg.GetBinContent(i+1))

    delta = ratioHistogram(num = histDict[Observed], den = bkg, relErrMax=relErrMax)


    result = 0
    delta.SetTitle('; %s %s; obs / bkg ' %(varName, unit))
    delta.SetMaximum(1.49)
    delta.SetMinimum(0.49)

    delta.GetXaxis().SetLabelSize(0.1)
    delta.GetXaxis().SetTitleSize(0.1)
    delta.GetYaxis().SetLabelSize(0.1)
    delta.GetYaxis().SetNdivisions(5,5,0)
    delta.GetYaxis().SetTitleSize(0.1)
    delta.GetYaxis().SetTitleOffset(0.43)
    delta.GetYaxis().CenterTitle()
    return delta, result, bkg_err, bkg_err2, histDict_withUnc

def buildHists(varName, varBins, unit, FS, option, relErrMax):

    if len(plots_cfg.WJetsScanRange) == 1:
        scanPoints = len(plots_cfg.scanRange)*(len(plots_cfg.scanRange)-1)/2
    elif len(plots_cfg.scanRange) == 2:
        scanPoints = len(plots_cfg.WJetsScanRange)
    else:
        print "ERROR"
        return 0
    scaleFactors = []
    histDict = {}
    histDict["WJets_OScontrol_iso"] = r.TH1F("WJets_CR_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["WJets_OScontrol_iso"].Sumw2()
    histDict["WJets_OSsignal"] = r.TH1F("WJets_signal_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["WJets_OSsignal"].Sumw2()
    regions = ['B', 'C', 'D', 'E', 'F']
    for i in regions:
        histDict["QCD_%s" %i] = r.TH1F("QCD_%s_%s_%s" %(FS, varName, i), "", len(varBins)-1, varBins)
        histDict["QCD_%s" %i].Sumw2()

    regions = ["A", "C"]
    for i in regions:
        histDict["QCD_F_for_%s" %i] = r.TH1F("QCD_%s_%s_F_for_%s" %(FS, varName, i), "", len(varBins)-1, varBins)
        histDict["QCD_F_for_%s" %i].Sumw2()
        histDict["QCD_F_for_%s" %i].SetMarkerColor(getColor("QCD"))
        histDict["QCD_F_for_%s" %i].SetFillColor(getColor("QCD"))
        histDict["QCD_F_for_%s" %i].SetMarkerStyle(21)
        histDict["QCD_F_for_%s" %i].SetLineColor(r.kBlack)

    for iName, iSample, iCategory in plots_cfg.sampleList:
        iCategory_nominal = iCategory
        for iRegion in ["", "_C", "_F"]: 
            iCategory = iCategory_nominal + iRegion
            if not (iCategory in histDict.keys()):
                histDict["%s" %iCategory] = r.TH1F("%s_%s_%s" %(iCategory, FS, varName), "", len(varBins)-1, varBins)
                histDict["%s" %iCategory].Sumw2()
                if iCategory != "Observed" and "ZPrime" not in iCategory:
                    histDict["%s" %iCategory].SetFillColor(getColor(iCategory_nominal))
                    histDict["%s" %iCategory].SetMarkerColor(getColor(iCategory_nominal))
                    histDict["%s" %iCategory].SetMarkerStyle(21)
                    histDict["%s" %iCategory].SetLineColor(r.kBlack)
                if "ZPrime" in iCategory:
                    histDict["%s" %iCategory].SetLineStyle(2)
                    histDict["%s" %iCategory].SetLineColor(r.kBlue)
        iCategory = iCategory_nominal
        loop_one_sample(iSample, iCategory, histDict, varName, varBins, FS, scanPoints)
    if not ('Observed' in histDict.keys()):
        histDict['Observed'] = r.TH1F("Observed_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
        histDict['Observed'].Sumw2()

    fixNegativeWJetsFromQCD(histDict, "F")

    qcd_scale_SStoOS = getQCDScale(histDict, varBins, "SStoOS")
    qcd_scale_FtoC = getQCDScale(histDict, varBins, "FtoC")
    qcd_scale_SR = getQCDScale(histDict, varBins, "SR")

#     qcd_scale_FtoC = [(2.047, 0.259)]
#     qcd_scale_SR = [(0.650, 0.069)]

    print "before scale QCD_F: %.3f" %histDict['QCD_F_for_A'].Integral()

    setQCD(histDict['QCD_F_for_C'], qcd_scale_FtoC)
    setQCD(histDict['QCD_F_for_A'], qcd_scale_SR)
    print "after scale QCD_F_for_A: %.3f" %histDict['QCD_F_for_A'].Integral()
    print "before scale QCD_F_for_C: %.3f" %histDict['QCD_F_for_C'].Integral()

    print "WJets_OScontrol before QCD subtraction: %.2f" %histDict['WJets_OScontrol_iso'].Integral()
    print "WJets_OSsignal before QCD subtraction: %.2f" %histDict['WJets_OSsignal'].Integral()


    histDict['WJets_OScontrol_iso'].Add(histDict['QCD_F_for_C'], -1.0)
    histDict['WJets_OSsignal'].Add(histDict['QCD_F_for_A'], -1.0)
    print "WJets_OScontrol after QCD subtraction: %.2f" %histDict['WJets_OScontrol_iso'].Integral()
    print "WJets_OSsignal after QCD subtraction: %.2f" %histDict['WJets_OSsignal'].Integral()

    if options.getWJetsSF:
         wjets_scale = getWJetsSF(histDict['WJets_OSsignal'], histDict['WJets_OScontrol_iso'], varBins)
    else:
        wjets_scale = [(plots_cfg.WJetsLoose2Tight[0], plots_cfg.WJetsLoose2Tight[1])]

    print "MC WJets **********************"
    wjets_MC_scale = getWJetsSF(histDict['WJets'], histDict['WJets_C'], varBins)
    if options.useMCWJetsSF:
        wjets_scale = wjets_MC_scale
    if options.useMCWJetsYield:
        wjets_scale = getWJetsSF(histDict['WJets'], histDict['WJets_OScontrol_iso'], varBins)

    fixNegativBins(histDict['WJets_OScontrol_iso'])

    print "WJets_OScontrol with SF: %.2f" %(histDict['WJets_OScontrol_iso'].Integral()*wjets_scale[0][0])
#     print "WJets Purity: %.2f" %(histDict['WJets_OScontrol_iso'].Integral()*wjets_scale[0][0]/histDict['Observed'].Integral())

    if "ZPrime" in histDict.keys():
        histDict["ZPrime"].Scale(signalScale)

    deltas = []
    delta, result, error, error2, histDict_withError = buildDelta('%s_delta' %(varName), histDict, varBins, varName, unit, relErrMax, 0.5, 1.5, wjets_scale[0][0], wjets_scale[0][1], FS)
    deltas.append((delta, result, error, error2, histDict_withError))

    for iCat in histDict.keys():
        histDict[iCat].Scale(1, option)
    bkgStack = buildStackFromDict(histDict, FS, option, wjets_scale[0][0], wjets_scale[0][1])
    return histDict, bkgStack, deltas, scaleFactors


def setLegend(position, histDict, histDict2, bins, option = 'width', Observed = "Observed"):
    histList = []
    nbins = len(bins)

    if options.unblind:
        histList.append((histDict[Observed], 'Observed (%.2f)' %histDict[Observed].Integral(0, nbins+1, option), 'lep'))
    else:
        histList.append((histDict[Observed], 'Observed', 'lep'))

    for ikey, iColor in reversed(defaultOrder):
        name = ikey
        if options.plotRegionF:
            if "QCD" in ikey:
                continue
            ikey += "_F"
            if ikey in histDict.keys():
                histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)), 'f'))
        elif options.plotRegionC:
            if "WJets" in ikey:
                continue
            ikey += "_C"
            if "QCD" in ikey:
                ikey = "QCD_F_for_C"
            if ikey in histDict.keys():
                histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)), 'f'))
        else:
            if ikey == 'QCD':
                ikey = 'QCD_F_for_A'
            if ikey in histDict.keys():
                if plots_cfg.addIntegrals:
                    if ikey == 'WJets':
                        if plots_cfg.unc:
                            integral, unc = IntegralAndError(histDict['WJets_OScontrol_iso'], nbins, ikey, 'et')
                            histList.append((histDict[ikey], '%s (%.1f +/- %.1f)' %(name, integral, unc), 'f'))
                        else:
                            histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict['WJets_OScontrol_iso'].Integral(0, nbins+1, option)), 'f'))
                    else:
                        if plots_cfg.unc:
                            integral, unc = IntegralAndError(histDict2[ikey], nbins, ikey, 'et')
                            histList.append((histDict2[ikey], '%s (%.1f +/- %.1f)' %(ikey, integral, unc), 'f'))
                        else:
                            histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)), 'f'))
                else:
                    histList.append((histDict[ikey], '%s' %name, 'f'))

    if "ZPrime" in histDict.keys() and (not options.plotRegionC) and (not options.plotRegionF):
        for iName, iSample, iCategory in plots_cfg.sampleList:    
            if "Z'" in iName:
                signalName = iName
        if signalScale != 1:
            signalName += "x%i" %signalScale
        if plots_cfg.addIntegrals:
            if plots_cfg.unc:
                integral, unc = IntegralAndError(histDict2["ZPrime"], nbins)
                histList.append((histDict2["ZPrime"], "%s (%.1f +/- %.1f)" %(signalName, integral, unc), 'l'))
            else:
                histList.append((histDict["ZPrime"], "%s (%.2f)" %(signalName, histDict['ZPrime'].Integral(0, nbins+1, option)), 'l'))
        else:
            histList.append((histDict["ZPrime"], signalName, 'l'))

    return tool.setMyLegend(position, histList)

def multiPlots(FS, option):
    print option
    if options.PUWeight:
        psfile = '13TeV_%s_puweight.pdf' %(FS)
    else:
        psfile = '13TeV_%s.pdf' %(FS)
    if options.chi2:
        psfile = psfile[:psfile.rfind('.')] + '_chi2.pdf'
    if options.KS:
        psfile = psfile[:psfile.rfind('.')] + '_KS.pdf'
    if options.noWJets:
        psfile = psfile[:psfile.rfind('.')] + '_noWJets.pdf'
    if options.highMETlowPZeta:
        psfile = psfile[:psfile.rfind('.')] + '_highMETlowPZeta.pdf'
    elif options.lowMET:
        psfile = psfile[:psfile.rfind('.')] + '_lowMET.pdf'
    elif options.signalRegion:
        psfile = psfile[:psfile.rfind('.')] + '_signalRegion.pdf'
    elif options.method == 'LooseRegion':
        psfile = psfile[:psfile.rfind('.')] + '_LooseRegion.pdf'
    elif options.signalRegionReversePZeta:
        psfile = psfile[:psfile.rfind('.')] + '_signalRegionReversePZeta.pdf'
    elif options.signalRegionReverseNCSVJets:
        psfile = psfile[:psfile.rfind('.')] + '_signalRegionReverseNCSVJets.pdf'
    elif options.signalRegionReverseCosPhi:
        psfile = psfile[:psfile.rfind('.')] + '_signalRegionReverseCosPhi.pdf'
    elif options.highMETlowPZeta0NB:
        psfile = psfile[:psfile.rfind('.')] + '_highMETlowPZeta0NB.pdf'
    elif options.signalRegionLowMET:
        psfile = psfile[:psfile.rfind('.')] + '_signalRegionLowMET.pdf'
    if options.prong2:
        psfile = psfile[:psfile.rfind('.')] + '_2prong.pdf'
    elif options.prong1:
        psfile = psfile[:psfile.rfind('.')] + '_1prong.pdf'
    elif options.prong3:
        psfile = psfile[:psfile.rfind('.')] + '_3prong.pdf'
    elif options.prong1_3:
        psfile = psfile[:psfile.rfind('.')] + '_1and3prong.pdf'

    else:
        psfile = psfile[:psfile.rfind('.')] + '_123prong.pdf'

    Observed = "Observed"

    if options.plotRegionC:
        psfile = psfile[:psfile.rfind('.')] + '_regionC.pdf'
        Observed = "Observed_C"

    elif options.plotRegionF:
        Observed = "Observed_F"
        psfile = psfile[:psfile.rfind('.')] + '_regionF.pdf'

    p_coords = [0., 1, 1., 0.3]
    p_r_coords = [0.,0.3,1.,0.06]
    c_ratio = [600, 800]
    if options.plotRegionC or options.plotRegionF:
        p_coords = [0., 1, 1., 0.0]
        p_r_coords = [0.,0.0,1.,0.0]
        c_ratio = [600, 500]

    c = r.TCanvas("c","Test", c_ratio[0], c_ratio[1])
    counter = 0
    for iVarName, iVarBins, iUnit, relErrMax in plots_cfg.vars:
        histDict, bkgStack, deltas, scaleFactors = buildHists(iVarName, iVarBins, iUnit, FS, option, relErrMax)
        delta = deltas[0][0]

        p = r.TPad("p_%s" %iVarName,"p_%s" %iVarName, p_coords[0], p_coords[1], p_coords[2], p_coords[3])
        p_r = r.TPad("p_%s_r" %iVarName,"p_%s_r" %iVarName, p_r_coords[0], p_r_coords[1], p_r_coords[2], p_r_coords[3])
        p.SetMargin(1, 1, 0, 0.1)
        p_r.SetMargin(1, 1, 0.2, 0)
        if options.plotRegionC or options.plotRegionF:
            p.SetMargin(1, 1, 1, 1)
            p_r.SetMargin(0, 0, 0, 0)

        p.Draw()
        p_r.Draw()
        p.cd()
        r.gPad.SetTicky()
        r.gPad.SetTickx()
                
        factor = 1.2
        if options.logY:
            r.gPad.SetLogy()
            factor = 1.2#20
        iMax = factor*max(bkgStack.GetMaximum(), histDict[Observed].GetMaximum())
        iMax = factor*max(iMax, histDict["ZPrime"].GetMaximum())
        bkgStack.SetMaximum(iMax)
        iMin = 0.01#0.01

        if options.plotRegionF:
            iMin = 0.001
        bkgStack.SetMinimum(iMin)   
     
        bkgStack.Draw('hist H')
        bkgStack.GetYaxis().SetNdivisions(510)
        bkgStack.GetYaxis().SetTitleOffset(1.2)
        bkgStack.GetYaxis().SetLabelSize(0.035)

        deltas[0][3].Scale(1, option)
        deltas[0][3].Draw('E2 same')

        histDict[Observed].SetMarkerStyle(8)
        histDict[Observed].SetMarkerSize(0.9)
        histDict[Observed].SetMarkerColor(r.kBlack)

        if options.unblind or options.unblindPartial:
            histDict[Observed].Draw('PE same')
        if "ZPrime" in histDict.keys() and (not options.plotRegionC) and (not options.plotRegionF):
            histDict["ZPrime"].SetLineWidth(2)
            histDict["ZPrime"].Draw('H same')

        if options.saveHist != "":
            outFile = r.TFile(options.saveHist, 'recreate')
            outFile.cd()
            deltas[0][3].Write()
            outFile.Close()
            
        if options.saveSignalHist != "":
            outFile = r.TFile(options.saveSignalHist, 'recreate')
            outFile.cd()
            histDict["ZPrime"].Write()
            outFile.Close()

        #final state    
        latex = r.TLatex()
        latex.SetTextSize(0.03)

        if options.logY:
            h0 = iMax*0.01
            h1 = iMax*0.01*0.5
            h2 = iMax*0.01*0.5*0.5
            h3 = iMax*0.01*0.5*0.5*0.5
        else:
            h1 = iMax*0.35
            h2 = iMax*0.15
            h3 = iMax*0.05


        position  = (0.6, 0.9 - 0.06*6, 0.87, 0.9)
        latex.DrawLatex(iVarBins[0], iMax*0.98, getFinalStateLatex(FS))
        legend = setLegend(position, histDict, deltas[0][4], iVarBins, option, Observed)
        legend.Draw('same')


        p_r.cd()
        r.gPad.SetTicky()
        r.gPad.SetTickx()
        delta.Draw()
        deltas[0][2].Draw('E2 same')
        p_r.SetGridy(1)
        delta.Draw('same')
        r.gPad.Update()
        r.gPad.RedrawAxis()
        c.Update()

        totalPages = len(plots_cfg.vars) - 1

        if (counter == totalPages) and (counter == 0):
            c.Print('%s' %psfile)
        elif counter == 0:
            c.Print('%s(' %psfile)
        elif counter == totalPages:
            c.Print('%s)' %psfile)
        else:
            c.Print('%s' %psfile)
        c.Clear()
        counter += 1

    print "Plot saved at %s" %(psfile)
    c.Close()

def go():
    for iFS in finalStates:
        multiPlots(iFS, options.option)

if __name__ == "__main__":
    finalStates = expandFinalStates(options.FS)
    if options.PUWeight:
        cutSampleTools.setupLumiReWeight()
    go()
#     cProfile.run("go()", sort="time")
    if options.PUWeight:
        cutSampleTools.freeLumiReWeight()
