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


lumi = 2153.0#2093.30#1546.91#1263.89#552.67#654.39#209.2#16.86, 578.26
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
    parser.add_option("--BSM3G", dest="BSM3G", default=False, action="store_true", help="")
    parser.add_option("--saveHisto", dest="saveHisto", default=False, action="store_true", help="")
    parser.add_option("--noIso", dest="noIso", default=False, action="store_true", help="")
    parser.add_option("--ratio", dest="ratio", default=False, action="store_true", help="")
    parser.add_option("--logY", dest="logY", default=False, action="store_true", help="")
    parser.add_option("--method", dest="method", default='SS', help="")
    parser.add_option("--chi2", dest="chi2", default=False, action="store_true", help="")
    parser.add_option("--KS", dest="KS", default=False, action="store_true", help="")
    parser.add_option("--OS", dest="OS", default=False, action="store_true", help="")
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
    parser.add_option("--looseRegion", dest="looseRegion", default=False, action="store_true", help="")
    parser.add_option("--getWJetsSF", dest="getWJetsSF", default=False, action="store_true", help="")
    parser.add_option("--dynamicQCDSF", dest="dynamicQCDSF", default=False, action="store_true", help="")

    options, args = parser.parse_args()
    return options
if __name__ == "__main__":
    options = opts()

def getNCSVLJets(tree, sys, isData, full = False):
    n = 0
    for i in range(1, 9):
        CSVL = 0#getattr(tree, "jet%iCSVL" %i)
        jetPt = getattr(tree, "jet%iPt" %i)
        jetEta = getattr(tree, "jet%iEta" %i)
        if getattr(tree, "jet%iCSVBtag" %i) > 0.605:
            CSVL = 1
        CSVL_old = CSVL
        if not isData:
            if sys == 'bScaleUp':
                CSVL = getattr(tree, "jet%iCSVL_up" %i)
            elif sys == 'bScaleDown':
                CSVL = getattr(tree, "jet%iCSVL_down" %i)
            elif sys == 'jetECUp':
                jetPt = getattr(tree, "jet%iJES_Up" %i)
            elif sys == 'jetECDown':
                jetPt = getattr(tree, "jet%iJES_Down" %i)
        if CSVL and  jetPt > 30 and abs(jetEta) < 2.4 and abs(getattr(tree, "jet%iPFJetIDLoose" %i)):
            l_1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
            jet.SetCoordinates(jetPt, 
                               jetEta, 
                               getattr(tree, "jet%iPhi" %i), 
                               0)
            dR_1 = r.Math.VectorUtil.DeltaR(l_1, jet)
            if dR_1 <= 0.4:
                continue
            l_2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)
            dR_2 = r.Math.VectorUtil.DeltaR(l_2, jet)
            if dR_2 > 0.4:
                n += 1
        if not full and n >= 1:
            return 1
    return n

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


def pZetaCut(t1, t2, met):
    zetaX = math.cos(t1.phi()) + math.cos(t2.phi())
    zetaY = math.sin(t1.phi()) + math.sin(t2.phi())
    zetaR = math.sqrt(zetaX*zetaX + zetaY*zetaY)
    if zetaR > 0.0:
        zetaX /= zetaR
        zetaY /= zetaR
    pZeta = zetaX*(t1.px() + t2.px() + met.px()) + zetaY*(t1.py() + t2.py() + met.py()) 
    pZetaVis = zetaX*(t1.px() + t2.px()) + zetaY*(t1.py() + t2.py())
    return pZeta - 3.1*pZetaVis

def passBound(tree, FS, bound, side):
    if FS == 'et':
        if bound == 'Tight':
            value = tree.tByTightCombinedIsolationDeltaBetaCorr3Hits
        elif bound == 'Medium':
            value = tree.tByMediumCombinedIsolationDeltaBetaCorr3Hits
        elif bound == 'Loose':
            value = tree.tByLooseCombinedIsolationDeltaBetaCorr3Hits
        else:
            value = True if tree.tByCombinedIsolationDeltaBetaCorrRaw3Hits < bound else False
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
        if ('signal' in region) and (tree.tByTightCombinedIsolationDeltaBetaCorr3Hits > 0.5) and (tree.eRelIso < 0.15):
            return True
        elif ('control' in region) and (tree.eRelIso < 0.15) and passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
            return True
        else:
            return False
    elif FS == 'em':
        if ('signal' in region) and (tree.eRelIso < 0.15) and (tree.mRelIso < 0.15):
            return True
        elif ('control' in region) and passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
            return True
        else:
            return False
    return False

def passCut(tree, FS, isData, l1, l2, met, sys):
#     onlyMuLead = True if (not (tree.Mu8e23Pass and tree.mMu8El23 and tree.mMu8El23)) else False
#     onlyEleLead = True if (not (tree.Mu23e12Pass and tree.mMu23El12 and tree.eMu23El12)) else False
#     both = True if (tree.Mu23e12Pass and tree.mMu23El12 and tree.eMu23El12) and (tree.Mu8e23Pass and tree.mMu8El23 and tree.mMu8El23) else False
    if __name__ == "__main__":
        if tree.ePt <= 35:
            return False
        if FS == 'et':
            if options.prong2:
                if tree.tDecayMode < 4 or tree.tDecayMode > 8:
                    return False
            elif options.prong1 and tree.tDecayMode > 4:
                    return False
            elif options.prong3 and tree.tDecayMode < 8:
                    return False
            elif options.prong1_3 and 4 < tree.tDecayMode < 8:
                    return False
    #         else:
    #             if 4 < tree.tDecayMode < 8:
    #                 return False
#         if (l1+l2+met).mass() <= 200:
#             return False
        if options.highMETlowPZeta:
            if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) >= -50:# and tree.pfMetEt >= 30:
                return False
            if met.pt() <= 30:
                return False
        if options.highMETlowPZeta0NB:
#             if not (-0.6 < math.cos(tree.phi_1 - tree.phi_2) < 0):
#                 return False
            if pZetaCut(l1, l2, met) >= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) >= -50:# and tree.pfMetEt >= 30:
                return False
            if met.pt()  <= 30:
                return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False
        elif options.lowMET and met.pt()  >= 30:
                return False
        elif options.lowMET0NB:
            if met.pt()  >= 30:
                return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False
        elif options.signalRegion:
#             if not ( 300 < (l1 + l2 + met).mass() < 600):
#                 return False
            if met.pt()  <= 30:
                return False
            if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                return False
            if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
                return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False
#             if (pZetaCut(l1, l2, met) > -50) and (math.cos(tree.phi_1 - tree.phi_2) < -0.95):
#                 return False


        elif options.signalRegionReverseCosPhi:
            if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                return False
            if met.pt()  <= 30:
                return False
            if math.cos(tree.phi_1 - tree.phi_2) < -0.95:
                return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False
        elif options.signalRegionReverseNCSVJets:
            if met.pt()  <= 30:
                return False
            if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
                return False
#             if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
#                 return False
            if getNCSVLJets(tree, sys, isData) == 0:
                return False
        elif options.signalRegionReversePZeta:
            if (pZetaCut(l1, l2, met) >= -50) and (math.cos(tree.phi_1 - tree.phi_2) <= -0.95):
                return False#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
            if met.pt()  <= 30:
                return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False
        elif options.signalRegionLowMET:
            if met.pt()  >= 30:
                return False
#             if (l1 + l2 + met).mass() > 125:
#                 return False
#             if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
#                 return False
#             if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
#                 return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False



    #         if getNCSVLJets(tree, sys, isData) >= 1:
    #             return False
    # #     if tree.pfMetNoHFEt >= 30:
    # #         return False





    #     if (tree.eRelIso > 0.15):# and tree.tByTightCombinedIsolationDeltaBetaCorr3Hits > 0.5):# and (tree.mRelIso < 0.15)):
    #         return False

    #     if tree.mPt < 28:
    #         return False
    # 
    #     if FS == 'et':
    # #         if not (tree.tDecayMode < 5):
    # #         if not (4 < tree.tDecayMode < 10):
    #         if not (9 < tree.tDecayMode < 15):
    #             return False

    #     if FS == 'et' and not isData:
    #         if tree.singleEPass and tree.eSingleEle and tree.ePt > 33.0:
    #             return True
    #         else:
    #             return False
    #     if FS == 'et' and isData:
    #         if tree.singleETightPass and tree.eSingleEleTight and tree.ePt > 33.0:
    #             return True
    #         else:
    #             return False
        if FS == 'em':
            if abs(tree.eEta) >= 2.1 or abs(tree.mEta) >= 2.1:
                return False
    else: #signal region
        if pZetaCut(l1, l2, met) <= -50:# and tree.pfMetEt >= 30:
            return False
        if met.pt() <= 30:
            return False
        if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
            return False
        if getNCSVLJets(tree, sys, isData) >= 1:
            return False
        if tree.ePt <= 35:
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
          '1000': 0.468,
          '1500': 0.0723*10,
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

def getWJetsScale(histDict, varName, start, end, sf = 1):
    intBin = histDict['Observed'].FindBin(start)
    endBin = histDict['Observed'].FindBin(end)
    if varName != 'mt_1':
        return 0
    else:
        if options.looseRegion:
            print (histDict['Observed'].Integral(intBin, endBin) - histDict['Diboson'].Integral(intBin, endBin) - histDict['t#bar{t}'].Integral(intBin, endBin) - histDict['Z#rightarrow#tau#tau'].Integral(intBin, endBin))/(histDict['WJets_CR'].Integral(intBin, endBin)*sf)

        else:
            print (histDict['Observed'].Integral(intBin, endBin) - histDict['Diboson'].Integral(intBin, endBin) - histDict['t#bar{t}'].Integral(intBin, endBin) - histDict['Z#rightarrow#tau#tau'].Integral(intBin, endBin))/histDict['WJets'].Integral(intBin, endBin)

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

    nEntries = tree.GetEntries()
#     if nEntries > 100:
#         nEntries = 100
    
    tmpHist = r.TH1F("tmp_%s_%s" %(iCategory, varName), '', len(varBins)-1, varBins)
    tmpHist.Sumw2()
    tmpHist_forROOTFile = r.TH1F("%s" %(varName), '', len(varBins)-1, varBins)
    tmpHist_forROOTFile.Sumw2()
    isData = False
    isSignal = False
    if iCategory == 'Observed':
        isData = True
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(iSample), iEntry-1)
        weight = 1.0
        QCD_weight = 1.0

        if options.sys == 'jetECUp' and not isData:
            met.SetCoordinates(tree.pfMet_jesUp_Et, 0.0, tree.pfMet_jesUp_Phi, 0)
        elif options.sys == 'jetECDown' and not isData:
            met.SetCoordinates(tree.pfMet_jesDown_Et, 0.0, tree.pfMet_jesDown_Phi, 0)
        elif options.sys == 'tauECUp' and not isData:
            met.SetCoordinates(tree.pfMet_tesUp_Et, 0.0, tree.pfMet_tesUp_Phi, 0)
        elif options.sys == 'tauECDown' and not isData:
            met.SetCoordinates(tree.pfMet_tesDown_Et, 0.0, tree.pfMet_tesDown_Phi, 0)
        else:
            met.SetCoordinates(tree.pfMetEt, 0.0, tree.pfMetPhi, 0)

        l1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
        l2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)

        if eventCount:
            initEvents = eventCount.GetBinContent(1)
        else:    
            initEvents = tree.initEvents
        if eventCountWeighted:
            sumWeights = eventCountWeighted.GetBinContent(1)
        else:    
            sumWeights = tree.initWeightedEvents
        if not passCut(tree, FS, isData, l1, l2, met, options.sys):
            continue
        if not isData:
            xs  = tree.xs
            if (80.94 < xs < 80.96) or (136.01 < xs < 136.03):
                xs = xs*0.108*3
            weight = Lumi*xs*tree.genEventWeight*tree.trigweight_1*tree.trigweight_2/(sumWeights+0.0)
            if options.PUWeight:
                weight = weight*cutSampleTools.getPUWeight(tree.nTruePU)
        if options.diffQCD:
            if tree.tDecayMode < 4:
                QCD_weight = plots_cfg.SF_prong1[0]
            elif tree.tDecayMode > 8:
                QCD_weight = plots_cfg.SF_prong3[0]

        if 'WJets' in iSample:
            weight = 1.0*weight
        if 'ZPrime' in iSample:
            weight = getZPrimeXS(iCategory[7:])*weight
            isSignal =  True
        if varName == 'm_withMET':
            value = (l1 + l2 + met).mass()
        elif varName == 'mVis':
            value = (l1 + l2).mass()
        elif varName == 'pZeta - 3.1pZetaVis':
            value = pZetaCut(l1, l2, met)
        elif varName == "nCSVL":
            value = getNCSVLJets(tree, options.sys, isData, True)
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
            #region B
            if regionSelection(tree, FS, "SSsignal", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                if not isData:
                    histDict['QCD_B'].Fill(value, -weight*QCD_weight)
                else:
                    histDict['QCD_B'].Fill(value, weight*QCD_weight)  
            #region C
            if regionSelection(tree, FS, "OScontrol", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                if not isData:
                    histDict['QCD_C'].Fill(value, -weight*QCD_weight)
                    if iCategory != 'WJets':
                        histDict['WJets_OScontrol'].Fill(value, -weight)  
                else:
                    histDict['QCD_C'].Fill(value, weight*QCD_weight)
                    histDict['WJets_OScontrol'].Fill(value, weight)
            #region D
            if regionSelection(tree, FS, "SScontrol", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                if not isData:
                    histDict['QCD_D'].Fill(value, -weight*QCD_weight)
                    histDict['QCD_D_for_C'].Fill(value, -weight*QCD_weight)
                    histDict['QCD_D_for_A'].Fill(value, -weight*QCD_weight)
                else:
                    histDict['QCD_D'].Fill(value, weight*QCD_weight)
                    histDict['QCD_D_for_C'].Fill(value, weight*QCD_weight)
                    histDict['QCD_D_for_A'].Fill(value, weight*QCD_weight)


    print iCategory, tmpHist.Integral(0, len(varBins)+1)
    histDict[iCategory].Add(tmpHist)            

    del tmpHist

    if options.saveHisto:
        oFile = r.TFile('/user_data/zmao/ZPrimeHistos/%s/%s_%s.root' %(FS, iSample[iSample.rfind('/'): iSample.rfind('_SYNC')], varName),"recreate")
        oFile.cd()
        tmpHist_forROOTFile = fixNegativBins(tmpHist_forROOTFile)
        tmpHist_forROOTFile.Write()
        oFile.Close()
    del tmpHist_forROOTFile

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
    QCD_B_err = getError(histDict['QCD_B'], 0, len(varBins)+1)
    QCD_C_err = getError(histDict['QCD_C'], 0, len(varBins)+1)
    QCD_D_err = getError(histDict['QCD_D'], 0, len(varBins)+1)

    print 'QCD_B: %.2f' %QCD_B
    print 'QCD_C: %.2f' %QCD_C
    print 'QCD_D: %.2f' %QCD_D

    if QCD_B > 0 and QCD_C > 0 and QCD_D > 0:
        if options.dynamicQCDSF:
            unc_CD = calcSysUnc(QCD_C/QCD_D, QCD_C, QCD_D, math.sqrt(QCD_C_err), math.sqrt(QCD_D_err))
            SStoOS = QCD_C/QCD_D
        else:
            unc_CD = 0.05   
            SStoOS = 1.07
#             SStoOS = 0.891   
#             unc_CD = 0.111
#             SStoOS = 1.002 
#             unc_CD = 0.204
#             SStoOS = 0.961
#             unc_CD = 0.047

        unc_BD = calcSysUnc(QCD_B/QCD_D, QCD_B, QCD_D, math.sqrt(QCD_B_err), math.sqrt(QCD_D_err))
        unc = calcSysUnc((SStoOS*QCD_B)/QCD_D, SStoOS, QCD_B/QCD_D, unc_CD, unc_BD)

        if method == 'CD':
            result.append((SStoOS, unc_CD))
            print 'QCD CD                    (%.3f, %.3f),' %(SStoOS, unc_CD)
        else:
            result.append((QCD_C*QCD_B/(QCD_D*QCD_D), unc))
            print 'QCD SR                    (%.3f, %.3f),' %((SStoOS*QCD_B)/QCD_D, unc)
    else:
        print 'QCD %s                    (0, 0),' %method
        result.append((0, 0))
    return result



def buildStackFromDict(histDict, FS, option = 'width', sf = 0.1, sf_error= 0.1):
    stack = r.THStack()
    for ikey, iColor in defaultOrder:
        if ikey == 'QCD':
            ikey = 'QCD_D_for_A'
        if ikey in histDict.keys():
            if ikey == 'WJets':
                print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
                print 'WJets loose2tight = %.3f +/ %.3f' %(sf, sf_error)
                histDict['WJets_OScontrol'].SetFillColor(iColor)
                histDict['WJets_OScontrol'].SetMarkerColor(iColor)
                histDict['WJets_OScontrol'].SetMarkerStyle(21)
                histDict['WJets_OScontrol'].SetLineColor(r.kBlack)
                tmpHist = histDict['WJets_OScontrol'].Clone()
                stack.Add(tmpHist)
            else:
                print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
                stack.Add(histDict[ikey])
        else:
            print 'missing samples for %s' %ikey
    if option == 'width':
        stack.SetTitle('CMS Preliminary %.1f fb^{-1} (13 TeV); ; events / GeV' %(lumi/1000.))
    else:
        stack.SetTitle('CMS Preliminary %.1f fb^{-1} (13 TeV); ; events' %(lumi/1000.))
    return stack

def setQCD(hist, scale = 0.6, binned = False, j = 0): #force qcd to be non-negative
    iScale = scale[j][0]*Lumi/lumi
    hist.Scale(iScale)
    for i in range(1, hist.GetNbinsX()+2):
        content = hist.GetBinContent(i)
#             print 'uniScale', content
        error = hist.GetBinError(i)
        x = hist.GetBinCenter(i)
        if content < 0:
            hist.SetBinContent(i, 0)
            hist.SetBinError(i, error)
        else:
            hist.SetBinError(i, math.sqrt(error*error + scale[j][1]*content*scale[j][1]*content))
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

def IntegralAndError(hist, nbins):
    unc = 0.0
    content = 0.0
    for i in range(0, nbins+1):
        unc += hist.GetBinError(i)
        content += hist.GetBinContent(i)
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

    for ikey, icolor in defaultOrder:
        if ikey == 'QCD':
            ikey = 'QCD_D_for_A'
        if ikey in histDict.keys():
            histDict_withUnc[ikey] = r.TH1F('%s_withUnc' %ikey, '', len(bins)-1, bins)
            histDict_withUnc[ikey].Sumw2()

            if ikey != "Observed" and "ZPrime" not in ikey:
                histDict_withUnc[ikey].SetFillColor(getColor(ikey))
                histDict_withUnc[ikey].SetMarkerColor(getColor(ikey))
                histDict_withUnc[ikey].SetMarkerStyle(21)
                histDict_withUnc[ikey].SetLineColor(r.kBlack)
            if ikey == 'WJets':
                tmpHist = setWJetsLooseShape(histDict['WJets_OScontrol'], WJets_L2T, WJets_L2T_error, bins)
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

#     histDict['ZPrime_500'].Scale(100)

    for i in range(len(bins)-1):
        bkg_err.SetBinContent(i+1, 1.0)
        bkg_err2.SetBinContent(i+1, bkg.GetBinContent(i+1))
        bkg_err2.SetBinError(i+1, bkg.GetBinError(i+1))
        if bkg.GetBinContent(i+1) != 0:
            bkg_err.SetBinError(i+1, bkg.GetBinError(i+1)/bkg.GetBinContent(i+1))
#         print i, bkg.GetBinError(i+1), bkg.GetBinContent(i+1)
#         print i, histDict['ZPrime_500'].GetBinError(i+1), histDict['ZPrime_500'].GetBinContent(i+1)


    delta = ratioHistogram(num = histDict["Observed"], den = bkg, relErrMax=relErrMax)


    result = 0
    delta.SetTitle('; %s %s; obs / bkg ' %(varName, unit))
    delta.SetMaximum(2.5)
    delta.SetMinimum(0.0)

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
    histDict["WJets_OScontrol"] = r.TH1F("WJets_CR_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["WJets_OScontrol"].Sumw2()
    histDict["WJets_OSsignal"] = r.TH1F("WJets_signal_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["WJets_OSsignal"].Sumw2()
    histDict["QCD_B"] = r.TH1F("QCD_%s_%s_B" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["QCD_B"].Sumw2()
    histDict["QCD_C"] = r.TH1F("QCD_%s_%s_C" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["QCD_C"].Sumw2()
    histDict["QCD_D"] = r.TH1F("QCD_%s_%s_D" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["QCD_D"].Sumw2()
    histDict["QCD_D_for_C"] = r.TH1F("QCD_%s_%s_D_for_B" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["QCD_D_for_C"].Sumw2()
    histDict["QCD_D_for_A"] = r.TH1F("QCD_%s_%s_D_for_A" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["QCD_D_for_A"].Sumw2()
    histDict["QCD_D_for_A"].SetFillColor(getColor("QCD"))
    histDict["QCD_D_for_A"].SetMarkerColor(getColor("QCD"))
    histDict["QCD_D_for_A"].SetMarkerStyle(21)
    histDict["QCD_D_for_A"].SetLineColor(r.kBlack)

#     histDict["WJets"] = r.TH1F("WJets_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    for iName, iSample, iCategory in plots_cfg.sampleList:    
        if not (iCategory in histDict.keys()):
            histDict[iCategory] = r.TH1F("%s_%s_%s" %(iCategory, FS, varName), "", len(varBins)-1, varBins)
            histDict[iCategory].Sumw2()
            if iCategory != "Observed" and "ZPrime" not in iCategory:
                histDict[iCategory].SetFillColor(getColor(iCategory))
                histDict[iCategory].SetMarkerColor(getColor(iCategory))
                histDict[iCategory].SetMarkerStyle(21)
                histDict[iCategory].SetLineColor(r.kBlack)
            if "ZPrime" in iCategory:
                histDict[iCategory].SetLineStyle(2)
                histDict[iCategory].SetLineColor(r.kBlue)
#                 histDict[iCategory].Sumw2()


        loop_one_sample(iSample, iCategory, histDict, varName, varBins, FS, scanPoints)
    if not ('Observed' in histDict.keys()):
        histDict['Observed'] = r.TH1F("Observed_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
        histDict['Observed'].Sumw2()


    qcd_scale_B_D = getQCDScale(histDict, varBins, "CD")
    qcd_scale_SR = getQCDScale(histDict, varBins, "SR")
    setQCD(histDict['QCD_D_for_C'], qcd_scale_B_D)
    setQCD(histDict['QCD_D_for_A'], qcd_scale_SR)
    print "WJets_OScontrol before QCD subtraction: %.2f" %histDict['WJets_OScontrol'].Integral()
    print "WJets_OSsignal before QCD subtraction: %.2f" %histDict['WJets_OSsignal'].Integral()

    histDict['WJets_OScontrol'].Add(histDict['QCD_D_for_C'], -1.0)
    histDict['WJets_OSsignal'].Add(histDict['QCD_D_for_A'], -1.0)
    print "WJets_OScontrol after QCD subtraction: %.2f" %histDict['WJets_OScontrol'].Integral()
    print "WJets_OSsignal after QCD subtraction: %.2f" %histDict['WJets_OSsignal'].Integral()

    if options.getWJetsSF:
         wjets_scale = getWJetsSF(histDict['WJets_OSsignal'], histDict['WJets_OScontrol'], varBins)
    else:
        wjets_scale = [(plots_cfg.WJetsLoose2Tight[0], plots_cfg.WJetsLoose2Tight[1])]
    print "WJets_OScontrol with SF: %.2f" %(histDict['WJets_OScontrol'].Integral()*wjets_scale[0][0])

    fixNegativBins(histDict['WJets_OScontrol'])

    deltas = []

    delta, result, error, error2, histDict_withError = buildDelta('%s_delta' %(varName), histDict, varBins, varName, unit, relErrMax, 0.5, 1.5, wjets_scale[0][0], wjets_scale[0][1], FS)
    deltas.append((delta, result, error, error2, histDict_withError))

#     getWJetsScale(histDict, varName, start, end, sf)


    delta2 = None
    for iCat in histDict.keys():
        histDict[iCat].Scale(1, option)
    bkgStack = buildStackFromDict(histDict, FS, option, wjets_scale[0][0], wjets_scale[0][1])
    return histDict, bkgStack, deltas, delta2, scaleFactors


def setLegend(position, histDict, histDict2, bins, option = 'width'):
    histList = []
    nbins = len(bins)

    if options.unblind:
        histList.append((histDict['Observed'], 'Observed (%.2f)' %histDict['Observed'].Integral(0, nbins+1, option), 'lep'))
    else:
        histList.append((histDict['Observed'], 'Observed', 'lep'))

    for ikey, iColor in reversed(defaultOrder):
        name = ikey
        if ikey == 'QCD':
            ikey = 'QCD_D_for_A'
        if ikey in histDict.keys():
            if plots_cfg.addIntegrals:
                if ikey == 'WJets':
                    histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict['WJets_OScontrol'].Integral(0, nbins+1, option)), 'f'))
#                 if plots_cfg.unc:
#                     integral, unc = IntegralAndError(histDict2[ikey], nbins)
#                     histList.append((histDict2[ikey], '%s (%.2f +/- %.2f)' %(name, integral, unc), 'f'))
                else:
                    histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)), 'f'))
            else:
                histList.append((histDict[ikey], '%s' %name, 'f'))
    if not (options.antiIso or options.antiEIso or options.antiMIso or options.noIso):
        signalSampleName = 'ZPrime_500'
        if plots_cfg.addIntegrals:
            if plots_cfg.unc:
                integral, unc = IntegralAndError(histDict2[signalSampleName], nbins)
                histList.append((histDict2[signalSampleName], '%s (%.2f +/- %.2f)' %(signalSampleName, integral, unc), 'l'))
            else:
                histList.append((histDict[signalSampleName], '%s (%.2f)' %(signalSampleName, histDict[signalSampleName].Integral(0, nbins+1, option)), 'l'))
        else:
            histList.append((histDict[signalSampleName], signalSampleName, 'l'))

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
    if options.method != 'SS':
        if options.OS:
            psfile = psfile[:psfile.rfind('.')] + '_OS.pdf'
        else:
            psfile = psfile[:psfile.rfind('.')] + '_SS.pdf'
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

    c = r.TCanvas("c","Test", 600, 800)
    counter = 0
    for iVarName, iVarBins, iUnit, relErrMax in plots_cfg.vars:
        histDict, bkgStack, deltas, delta2, scaleFactors = buildHists(iVarName, iVarBins, iUnit, FS, option, relErrMax)
        delta = deltas[0][0]
        p = r.TPad("p_%s" %iVarName,"p_%s" %iVarName, 0., 1, 1., 0.3)
        p_r = r.TPad("p_%s_r" %iVarName,"p_%s_r" %iVarName, 0.,0.3,1.,0.06)
        p.SetMargin(1, 1, 0, 0.1)
        p_r.SetMargin(1, 1, 0.2, 0)
        p.Draw()
        p_r.Draw()
        p.cd()
        r.gPad.SetTicky()
        r.gPad.SetTickx()
                
        factor = 1.2
        if options.logY:
            r.gPad.SetLogy()
            factor = 1.2#20
        iMax = factor*max(bkgStack.GetMaximum(), histDict["Observed"].GetMaximum())
        bkgStack.SetMaximum(iMax)
        iMin = 0.001
        bkgStack.SetMinimum(iMin)   
     
        bkgStack.Draw('hist H')
        bkgStack.GetYaxis().SetNdivisions(510)
        bkgStack.GetYaxis().SetTitleOffset(1.2)
        bkgStack.GetYaxis().SetLabelSize(0.035)

        deltas[0][3].Scale(1, option)
        deltas[0][3].Draw('E2 same')

        histDict["Observed"].SetMarkerStyle(8)
        histDict["Observed"].SetMarkerSize(0.9)
        if options.unblind or options.unblindPartial:
            histDict["Observed"].Draw('PE same')
        histDict["ZPrime_500"].Draw('H same')
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

        if 'pZeta' in iVarName:
            position  = (0.2, 0.9 - 0.06*6, 0.47, 0.9)
            latex.DrawLatex(iVarBins[7], iMax*0.98, getFinalStateLatex(FS))
            if options.method == 'LooseRegion' and plots_cfg.showRegion:
                latex.DrawLatex(iVarBins[7], h0, 'antiIso (%s, %s)' %(str(len(plots_cfg.scanRange[iLower])), str(len(plots_cfg.scanRange[iLower + iUpper + 1]))))

        else:
            position  = (0.6, 0.9 - 0.06*6, 0.87, 0.9)
            latex.DrawLatex(iVarBins[0], iMax*0.98, getFinalStateLatex(FS))
        legend = setLegend(position, histDict, deltas[0][4], iVarBins, option)
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
        c.cd()
        yaxis =  r.TGaxis(0.1, 0.3, 0.1, 0.9, iMin, iMax, 505,"G")
        yaxis.SetLabelSize(0.03)
        yaxis.SetTitle("events / bin")
        yaxis.SetTitleOffset(1.2)
        yaxis.SetTitleSize(0.035)

        totalPages = len(plots_cfg.vars) - 1

        c.Update()
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
