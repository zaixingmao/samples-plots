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

lumi = 2153.0#2246.258005#2093.30#1546.91#1263.89#552.67#654.39#209.2#16.86, 578.26
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
    parser.add_option("--diffWJets", dest="diffWJets", default=False, action="store_true", help="")

    parser.add_option("--looseRegion", dest="looseRegion", default=False, action="store_true", help="")

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
                if hasattr(tree, "jet%iJES_Up" %i):
                    jetPt = getattr(tree, "jet%iJES_Up" %i)
                else:
                    jetPt = getattr(tree, "jet%iEC_up" %i)
            elif sys == 'jetECDown':
                if hasattr(tree, "jet%iJES_Down" %i):
                    jetPt = getattr(tree, "jet%iJES_Down" %i)
                else:
                    jetPt = getattr(tree, "jet%iEC_down" %i)
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
        if bound == 'VTight':
            value = tree.tByVTightIsolationMVArun2v1DBnewDMwLT
        elif bound == 'Tight':
#            value = tree.tByTightIsolationMVArun2v1DBnewDMwLT
            value = tree.tByTightCombinedIsolationDeltaBetaCorr3Hits
        elif bound == 'Medium':
            value = tree.tByMediumCombinedIsolationDeltaBetaCorr3Hits
        elif bound == 'Loose':
#             value = tree.tByLooseCombinedIsolationDeltaBetaCorr3Hits
            value = tree.tByLooseIsolationMVArun2v1DBnewDMwLT
        elif bound == 'VLoose':
            value = tree.tByVLooseIsolationMVArun2v1DBnewDMwLT
        else:
            value = True if tree.tByCombinedIsolationDeltaBetaCorrRaw3Hits < bound else False
    elif FS == 'em':
        value = True if tree.mRelIso < bound else False
    else:
        return False

    if side == 'lower' and (not value):
        return True
    elif side == 'upper' and value:
        return True
    else:
        return False

def regionSelection(tree, FS, region, method, lowerBound = 0, upperBound = 1):
    if method == 'SS':
#         if not (passBound(tree, FS, lowerBound, 'upper') and (tree.eRelIso < 0.15)):
        if not (passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper') and (tree.eRelIso < 0.15)):
            return False
        if tree.q_1 == tree.q_2 and region == 'control':
            return True
        if tree.q_1 == -tree.q_2 and region == 'signal':
            return True
        return False            
    if method == 'Loose':
        if FS == 'et':
#             if (tree.tByTightCombinedIsolationDeltaBetaCorr3Hits > 0.5) and (tree.eRelIso < 0.15) and region == 'signal':
            if passBound(tree, FS, lowerBound, 'upper') and (tree.eRelIso < 0.15) and region == 'signal':
                return True
            elif region == 'control' and tree.eRelIso < 0.15 and passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
                return True
        elif FS == 'em':
            if (tree.eRelIso < 0.15) and (tree.mRelIso < 0.15) and region == 'signal':
                return True
            elif region == 'control' and passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
                return True
        else:
            return False
    if method == 'LooseRegion':
        if region == 'control':
            return False
        if FS == 'et':
            if tree.eRelIso < 0.15 and passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
                return True
        elif FS == 'em':
            if passBound(tree, FS, lowerBound, 'lower') and passBound(tree, FS, upperBound, 'upper'):
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
            if math.cos(tree.phi_1 - tree.phi_2) > -0.8:
                return False
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
            if (l1 + l2 + met).mass() >= 125:
                return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False
        elif options.signalRegion:
            if met.pt()  <= 30:
                return False
#             if pZetaCut(l1, l2, met) <= -50:#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
#                 return False
#             if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
#                 return False
            if (pZetaCut(l1, l2, met) > -50) and (math.cos(tree.phi_1 - tree.phi_2) < -0.95):
                return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False
#             if tree.tEta > 1.479 or tree.tEta < -1.479:
#                 return False
#             if abs(tree.tEta) < 1.479:
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
            if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
                return False
            if getNCSVLJets(tree, sys, isData) == 0:
                return False
        elif options.signalRegionReversePZeta:
            if (pZetaCut(l1, l2, met) >= -50):# and (math.cos(tree.phi_1 - tree.phi_2) <= -0.95):
                return False#getattr(tree, "%s_%s_PZeta" %(FS[0], FS[1])) - 3.1*getattr(tree, "%s_%s_PZetaVis" %(FS[0], FS[1])) <= -50:# and tree.pfMetEt >= 30:
            if met.pt()  <= 30:
                return False
            if getNCSVLJets(tree, sys, isData) >= 1:
                return False
            if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
                return False
        elif options.signalRegionLowMET:
            if met.pt()  >= 30:
                return False
            if (l1 + l2 + met).mass() > 200:
                return False
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
        if options.method != 'SS':
            if options.OS and tree.q_1 == tree.q_2:
                return False
            elif (not options.OS) and tree.q_1 != tree.q_2:
                return False
#         else:
#             if FS == 'et' and (tree.eRelIso >= 0.15 or tree.tByTightCombinedIsolationDeltaBetaCorr3Hits < 0.5):
#                 return False
#             if FS == 'em' and (tree.eRelIso >= 0.15 or tree.mRelIso >= 0.15):
#                 return False
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
        if hasattr(tree, "tDecayMode"):
            if 4 < tree.tDecayMode < 8:
                return False
        if pZetaCut(l1, l2, met) <= -50:# and tree.pfMetEt >= 30:
            return False
        if met.pt() <= 30:
            return False
        if math.cos(tree.phi_1 - tree.phi_2) >= -0.95:
            return False
        if getNCSVLJets(tree, sys, isData) >= 1:
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
          '1500': 0.0723,
          '2000': 0.0173,
          '2500': 0.00554,
          '3000': 0.00129,
          '3500': 0.00049,
          '4000': 0.000255, 
          '4500': 0.000108,
          '5000': 0.0000559
        }
    if __name__ == "__main__":
        return xs[mass]
    else:
        return 1.0

def fixNegativBins(hist):
    nBins = hist.GetNbinsX()
    for i in range(1, nBins+1):
        if hist.GetBinContent(i) < 0:
            hist.SetBinError(i, abs(hist.GetBinContent(i)) + hist.GetBinError(i))
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

    sumPtWeights = -1.0
    if "TTJets" in iSample and options.sys == 'topPt':
        sumPtWeights = file.Get('eventCountPtWeighted').GetBinContent(1)
    nEntries = tree.GetEntries()
#     if not ("WJets" in iSample):
#         if nEntries > 100:
#             nEntries = 100
    
    tmpHist = r.TH1F("tmp_%s_%s" %(iCategory, varName), '', len(varBins)-1, varBins)
    tmpHist.Sumw2()
    tmpHist_qcds = []
    for iScanPoint in range(scanPoints):
        tmpHist_qcds.append(r.TH1F("tmp_qcd_%s_%s_%i" %(iCategory, varName, iScanPoint), '', len(varBins)-1, varBins))
        tmpHist_qcds[iScanPoint].Sumw2()
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
        elif options.sys == 'jetECDown' and not isData :
            met.SetCoordinates(tree.pfMet_jesDown_Et, 0.0, tree.pfMet_jesDown_Phi, 0)
        elif options.sys == 'tauECUp' and (not isData) and tree.tIsTauh:
            met.SetCoordinates(tree.pfMet_tesUp_Et, 0.0, tree.pfMet_tesUp_Phi, 0)
        elif options.sys == 'tauECDown' and (not isData) and tree.tIsTauh:
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
            if options.sys == 'topPt' and sumPtWeights != -1.0:
                sumWeights = sumPtWeights
                weight = Lumi*xs*tree.genEventWeight*tree.trigweight_1*tree.trigweight_2*tree.topPtWeight/(sumWeights+0.0)
            else:
                weight = Lumi*xs*tree.genEventWeight*tree.trigweight_1*tree.trigweight_2/(sumWeights+0.0)
            if options.PUWeight:
                weight = weight*cutSampleTools.getPUWeight(tree.nTruePU)

#             if tree.tEta < -1.479:
#                 weight = weight*1.5*1.2
#             if tree.tEta > 1.479:
#                 weight = weight*1.3*1.2
        WJets_weight = 1.0
        if options.diffQCD:
            if abs(tree.tEta) > 1.479:
                QCD_weight = plots_cfg.SF_endcap[0]
                WJets_weight = plots_cfg.SF_WJets_endcap[0]
            else:
                QCD_weight = plots_cfg.SF_barrel[0]
                WJets_weight = plots_cfg.SF_WJets_barrel[0]
        
#             if tree.tDecayMode < 4:
#                 QCD_weight = plots_cfg.SF_prong1[0]
#             elif tree.tDecayMode > 8:
#                 QCD_weight = plots_cfg.SF_prong3[0]

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

        if regionSelection(tree, FS, "signal", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            fill = True
            if isData:
                fill = False
                if options.unblind or (options.unblindPartial and passUnblindPartial(varName, value)):
                    fill = True
            if fill:
                tmpHist.Fill(value, weight)
                tmpHist_forROOTFile.Fill(value, weight)
        else:
            if isSignal:
                continue
            iScanPoint = 0
            if len(plots_cfg.WJetsScanRange) != 1:
                for iWJetScan in range(scanPoints):
                    if regionSelection(tree, FS, "control", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
                        if not isData:
                            if iCategory == 'WJets':
                                histDict['WJets_CR'].Fill(value, weight*WJets_weight)
                                tmpHist_qcds[iWJetScan].Fill(value, -weight*plots_cfg.WJetsScanRange[iWJetScan]*QCD_weight)
                            else:
                                tmpHist_qcds[iWJetScan].Fill(value, -weight*QCD_weight)
                        else:
                            tmpHist_qcds[iWJetScan].Fill(value, weight*QCD_weight)

            else:
                for iLower in range(len(plots_cfg.scanRange)):
                    for iUpper in range(len(plots_cfg.scanRange) - iLower - 1):
                        if regionSelection(tree, FS, "control", options.method, plots_cfg.scanRange[iLower], plots_cfg.scanRange[iLower + iUpper + 1]):
                            if not isData:
                                if iCategory == 'WJets':
                                    histDict['WJets_CR'].Fill(value, weight*WJets_weight)
                                    tmpHist_qcds[iScanPoint].Fill(value, -weight*plots_cfg.WJetsScanRange[0]*QCD_weight)
                                else:
                                    tmpHist_qcds[iScanPoint].Fill(value, -weight*QCD_weight)

                            else:
                                tmpHist_qcds[iScanPoint].Fill(value, weight*QCD_weight)
                        iScanPoint += 1
    for iScanPoint in range(scanPoints):        
        histDict['QCD_%i' %iScanPoint].Add(tmpHist_qcds[iScanPoint])
    print iCategory, tmpHist.Integral(0, len(varBins)+1), tmpHist.GetEntries()
    histDict[iCategory].Add(tmpHist)
#     if 'WJets' in iSample and iCategory != 'WJets':
#         histDict['WJets'].Add(tmpHist)
            

    del tmpHist_qcds
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

def getQCDScale(histDict, varBins, iQCD, W_SF = 1.0, binned = False):
    OS_MC_Miss = []
    SS_MC_Miss = []
    OS_MC_Miss_error = []
    SS_MC_Miss_error = []
    bins = []
    results = []
    nbins = 0
    if binned:
        for i in range(1, len(varBins)+1):
            bins.append(i)
        nbins = len(bins)
    else:
        bins = [1, len(varBins)+1]
        nbins = len(bins)-1
    print 'len(bins)', len(bins)
    for i in range(nbins):
        if binned:
            end = bins[i]
        else:
            end = bins[i+1]
        content = histDict['Observed'].Integral(bins[i], end)
        OS_MC_Miss.append(content)
        OS_MC_Miss_error.append(content)

        for ikey, iColor in defaultOrder:
            if (ikey in histDict.keys()) and (ikey != 'QCD'):
                if ikey == 'WJets':
                    OS_MC_Miss[i] -= histDict[ikey].Integral(bins[i], end)*W_SF
                    OS_MC_Miss_error[i] += getError(histDict[ikey], bins[i], end)*W_SF*W_SF

                else:
                    OS_MC_Miss[i] -= histDict[ikey].Integral(bins[i], end)
                    OS_MC_Miss_error[i] += getError(histDict[ikey], bins[i], end)

        SS_MC_Miss.append(histDict['QCD_%i' %iQCD].Integral(bins[i], end))
        SS_MC_Miss_error.append(getError(histDict['QCD_%i' %iQCD], bins[i], end))

        if SS_MC_Miss[i] > 0 and OS_MC_Miss[i] > 0:
            unc = calcSysUnc(OS_MC_Miss[i]/SS_MC_Miss[i], OS_MC_Miss[i], SS_MC_Miss[i], math.sqrt(OS_MC_Miss_error[i]), math.sqrt(SS_MC_Miss_error[i]))
#             print '(%.3f, %.3f),' %(histDict['QCD_%i' %iQCD].GetXaxis().GetBinLowEdge(bins[i]), histDict['QCD_%i' %iQCD].GetXaxis().GetBinLowEdge(end), OS_MC_Miss[i]/SS_MC_Miss[i], unc)
            print '                    (%.3f, %.3f),' %(OS_MC_Miss[i]/SS_MC_Miss[i], unc)
            results.append((OS_MC_Miss[i]/SS_MC_Miss[i], unc))
        else:
            print '                    (0, 0),'
            results.append((0, 0))
    return results


def getQCDandWJetsScaleFactor(histDict, varBins, i, MtCut = 80):
    binEdge = histDict['Observed'].FindBin(MtCut)
    print 'for Mt cut at: %.0f' %MtCut
    SR_MC_Miss_1 = histDict['Observed'].Integral(0, binEdge-1)
    SR_unc_1 = math.sqrt(SR_MC_Miss_1+0.0)
    SR_WJets_1 = histDict['WJets'].Integral(0, binEdge-1)
    CR_WJets_1 = histDict['WJets_CR'].Integral(0, binEdge-1)
    SR_MC_Miss_2 = histDict['Observed'].Integral(binEdge, len(varBins)+1)
    SR_unc_2 = math.sqrt(SR_MC_Miss_2+0.0)
    SR_WJets_2 = histDict['WJets'].Integral(binEdge, len(varBins)+1)
    CR_WJets_2 = histDict['WJets_CR'].Integral(binEdge, len(varBins)+1)
    
    for ikey, iColor in defaultOrder:
        if (ikey in histDict.keys()) and (ikey != 'QCD') and (ikey != 'WJets'):
            SR_MC_Miss_1 -= histDict[ikey].Integral(0, binEdge-1)
            SR_MC_Miss_2 -= histDict[ikey].Integral(binEdge, len(varBins)+1)
    CR_MC_Miss_1 = histDict['QCD_%i' %i].Integral(0, binEdge-1) + CR_WJets_1
    CR_MC_Miss_2 = histDict['QCD_%i' %i].Integral(binEdge, len(varBins)+1) + CR_WJets_2
    CR_unc_1 = math.sqrt(histDict['QCD_%i' %i].Integral(0, binEdge-1)+0.0)
    CR_unc_2 = math.sqrt(histDict['QCD_%i' %i].Integral(binEdge, len(varBins)+1)+0.0)

    print SR_MC_Miss_1, SR_WJets_1, CR_MC_Miss_1, CR_WJets_1
    print SR_MC_Miss_2, SR_WJets_2, CR_MC_Miss_2, CR_WJets_2
    f = lambda x: (SR_MC_Miss_1 - SR_WJets_1*x[0] - CR_MC_Miss_1*x[1] - CR_WJets_1*x[0]*x[1], SR_MC_Miss_2 - SR_WJets_2*x[0] - CR_MC_Miss_2*x[1] - CR_WJets_2*x[0]*x[1])
    f_up = lambda x: (SR_MC_Miss_1 + SR_unc_1 - SR_WJets_1*x[0] - (CR_MC_Miss_1 - CR_unc_1)*x[1] - CR_WJets_1*x[0]*x[1], SR_MC_Miss_2 + SR_unc_2 - SR_WJets_2*x[0] - (CR_MC_Miss_2 - CR_unc_2)*x[1] - CR_WJets_2*x[0]*x[1])
    f_down = lambda x: (SR_MC_Miss_1 - SR_unc_1 - SR_WJets_1*x[0] - (CR_MC_Miss_1 + CR_unc_1)*x[1] - CR_WJets_1*x[0]*x[1], SR_MC_Miss_2 - SR_unc_2 - SR_WJets_2*x[0] - (CR_MC_Miss_2 + CR_unc_2)*x[1] - CR_WJets_2*x[0]*x[1])

    func1 = r.TF2("func1", "[0] - [1]*x - [2]*y + [3]*x*y")
    func2 = r.TF2("func2", "[0] - [1]*x - [2]*y + [3]*x*y")
    func1.SetParameters(SR_MC_Miss_1, SR_WJets_1, CR_MC_Miss_1, CR_WJets_1)
    func2.SetParameters(SR_MC_Miss_2, SR_WJets_2, CR_MC_Miss_2, CR_WJets_2)
    rootFinder = r.Math.MultiRootFinder(0)
    g1 = r.Math.WrappedMultiTF1(func1,2)
    g2 = r.Math.WrappedMultiTF1(func2,2)

    rootFinder.AddFunction(g1)
    rootFinder.AddFunction(g2)
    rootFinder.SetPrintLevel(1)
    rootFinder.Solve(array('d', [1.0, 0.1]))
    print ''
#     SF_WJets, SF_QCD =  root(f, (1, 0.1))
#     SF_WJets_up, SF_QCD_up =  fsolve(f_up, (1, 0.1))
#     SF_WJets_down, SF_QCD_down =  fsolve(f_down, (1, 0.1))

#     print "SF_WJets = %.3f, SF_QCD = %.3f" %(SF_WJets, SF_QCD)
#     print "scaleUp: SF_WJets = %.3f, SF_QCD = %.3f" %(SF_WJets_up, SF_QCD_up)
#     print "scaleDown: SF_WJets = %.3f, SF_QCD = %.3f" %(SF_WJets_down, SF_QCD_down)

def buildStackFromDict(histDict, FS, option = 'width', iQCD = 0, SF_WJ = 1.0, sf = 0.1, sf_error= 0.1, looseRegion = False):
    stack = r.THStack()
    for ikey, iColor in defaultOrder:
        if ikey == 'QCD':
            ikey = 'QCD_%i' %iQCD
        if ikey in histDict.keys():
            if ikey == 'WJets':
                print '%s with %.2f events' %(ikey, SF_WJ*histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
                if looseRegion:
                    print 'WJets loose2tight = %.5f +/ %.5f' %(sf, sf_error)
                    histDict['WJets_CR'].SetFillColor(iColor)
                    histDict['WJets_CR'].SetMarkerColor(iColor)
                    histDict['WJets_CR'].SetMarkerStyle(21)
                    histDict['WJets_CR'].SetLineColor(r.kBlack)
                    tmpHist = histDict['WJets_CR'].Clone()
                    if not options.diffWJets:
                        tmpHist.Scale(SF_WJ*sf)
                    else:
                        tmpHist.Scale(SF_WJ)
                    stack.Add(tmpHist)

                else:
                    tmpHist = histDict[ikey].Clone()
                    tmpHist.Scale(SF_WJ)
                    stack.Add(tmpHist)
            else:
                print '%s with %.2f events' %(ikey, histDict[ikey].Integral(0, histDict[ikey].GetNbinsX()+2, option))
                stack.Add(histDict[ikey])
        else:
            print 'missing samples for %s' %ikey
    if option == 'width':
        stack.SetTitle('CMS Preliminary %.1f fb^{-1} (13 TeV); ; events / GeV' %(lumi/1000.))
#         stack.SetTitle('CMS Preliminary %.1f fb^{-1} (13 TeV); ; events / bin width' %(lumi/1000.))
    else:
        stack.SetTitle('CMS Preliminary %.1f fb^{-1} (13 TeV); ; events' %(lumi/1000.))
    return stack

def setQCD(hist, scale = 0.6, binned = False, j = 0): #force qcd to be non-negative
#     print scale
    if binned:
        print "hist.GetNbinsX()", hist.GetNbinsX()
        for i in range(1, hist.GetNbinsX()+2):
            content = hist.GetBinContent(i)
            error = hist.GetBinError(i)
            x = hist.GetBinCenter(i)
            iScale = scale[i][0]*Lumi/lumi
            if content < 0:
                hist.SetBinContent(i, 0)
                hist.SetBinError(i, iScale*error)
            else:
                hist.SetBinError(i, math.sqrt((iScale*error)**2 + (scale[i][1]*content)**2))
                hist.SetBinContent(i, iScale*content)
                print 'binned', iScale, iScale*content
                
    else:
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
                scaleUnc = scale[j][1]/scale[j][0]
                hist.SetBinError(i, math.sqrt(error*error))

def setWJetsLooseShape(hist, WJetSF, WJets_L2T, WJets_L2T_error, bins):
    tmpHist = hist.Clone()
    tmpHist.Sumw2()
    if options.diffWJets:
        WJets_L2T = 1.0
        WJets_L2T_error = 0.0
    tmpHist.Scale(WJets_L2T)
    for i in range(1, len(bins)):
        error1 = tmpHist.GetBinError(i)
        content = tmpHist.GetBinContent(i)
        if WJets_L2T != 0 and content != 0:
            tmpHist.SetBinError(i, content*math.sqrt((WJets_L2T_error/WJets_L2T)**2 + (error1/content)**2))
    tmpHist.Scale(WJetSF)
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
        unc += hist.GetBinError(i)*hist.GetBinError(i)
        content += hist.GetBinContent(i)
#     unc += content
    unc = math.sqrt(unc)
    return content, unc

def buildDelta(deltaName, histDict, bins, varName, unit, relErrMax, min = 0.5, max = 1.5, iQCD = 0, WJetSF = 1.0, WJets_L2T = 0.1, WJets_L2T_error = 0, fs = 'et'):
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
            ikey = 'QCD_%i' %iQCD
        if ikey in histDict.keys():
            histDict_withUnc[ikey] = r.TH1F('%s_withUnc' %ikey, '', len(bins)-1, bins)
            histDict_withUnc[ikey].Sumw2()

            if ikey != "Observed" and "ZPrime" not in ikey:
                histDict_withUnc[ikey].SetFillColor(getColor(ikey))
                histDict_withUnc[ikey].SetMarkerColor(getColor(ikey))
                histDict_withUnc[ikey].SetMarkerStyle(21)
                histDict_withUnc[ikey].SetLineColor(r.kBlack)
            if ikey == 'WJets':
                if options.looseRegion:
                    tmpHist = setWJetsLooseShape(histDict['WJets_CR'], WJetSF, WJets_L2T, WJets_L2T_error, bins)
                    bkg.Add(addSysUnc(tmpHist, ikey, bins, fs))
                    histDict_withUnc[ikey].Add(addSysUnc(tmpHist, ikey, bins, fs))
                else:
                    bkg.Add(addSysUnc(histDict[ikey], ikey, bins, fs), WJetSF)
                    histDict_withUnc[ikey].Add(addSysUnc(histDict['WJets'], ikey, bins, fs), WJetSF)
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

#     histDict['ZPrime_1000'].Scale(100)

    for i in range(len(bins)-1):
        bkg_err.SetBinContent(i+1, 1.0)
        bkg_err2.SetBinContent(i+1, bkg.GetBinContent(i+1))
        bkg_err2.SetBinError(i+1, bkg.GetBinError(i+1))
        if bkg.GetBinContent(i+1) != 0:
            bkg_err.SetBinError(i+1, bkg.GetBinError(i+1)/bkg.GetBinContent(i+1))
#         print i, bkg.GetBinError(i+1), bkg.GetBinContent(i+1)
#         print i, histDict['ZPrime_1000'].GetBinError(i+1), histDict['ZPrime_1000'].GetBinContent(i+1)


    if max != 1.5:
        delta = ratioHistogram(num = histDict["QCD"], den = bkg, relErrMax=relErrMax)
    else:
        delta = ratioHistogram(num = histDict["Observed"], den = bkg, relErrMax=relErrMax)


    result = 0
    if options.chi2:
#         result = histDict["Observed"].Chi2Test(bkg, "UWPOFUF")
        chi2 = r.Double(0)
        ndf = r.Long(0)
        igood = r.Long(0)
        result = histDict["Observed"].Chi2TestX(bkg, chi2, ndf, igood, "UWP")
        #'______calculate p-value______'
        if options.OS:
            result = r.TMath.Prob(chi2, ndf) 
        else:
            result = r.TMath.Prob(chi2, ndf-1)

    if options.KS:
        result = histDict["Observed"].KolmogorovTest(bkg, "OU")

#     delta.Add(histDict["Observed"])
#     delta.Sumw2()
#     bkg.Sumw2()
#     delta.Divide(bkg)
    if varName == 'mt_1':
        varName = "m_{T}(e, #slash{E}_{T})"
    if varName == 'mt_2':
        varName = "m_{T}(#mu, #slash{E}_{T})"
        
    delta.GetXaxis().SetTitleOffset(0.9)

    delta.SetTitle('; %s %s; observed/bkg' %(varName, unit))
    delta.SetMaximum(2.49)
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
    histDict["WJets_CR"] = r.TH1F("WJets_CR_%s_%s" %(FS, varName), "", len(varBins)-1, varBins)
    histDict["WJets_CR"].Sumw2()
    for i in range(scanPoints):
        histDict["QCD_%i" %i] = r.TH1F("QCD_%s_%s_%i" %(FS, varName, i), "", len(varBins)-1, varBins)
        histDict["QCD_%i" %i].Sumw2()
        histDict["QCD_%i" %i].SetFillColor(getColor("QCD"))
        histDict["QCD_%i" %i].SetMarkerColor(getColor("QCD"))
        histDict["QCD_%i" %i].SetMarkerStyle(21)
        histDict["QCD_%i" %i].SetLineColor(r.kBlack)

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

    if options.antiIso or options.antiEIso or options.antiMIso or options.noIso:
        for j in range(scanPoints):
            if len(plots_cfg.WJetsScanRange) == 1:
                WJetScale = plots_cfg.WJetsScanRange[0]
            else:
                WJetScale = plots_cfg.WJetsScanRange[j]
            if not options.method == 'LooseRegion':
                qcd_scale = getQCDScale(histDict, varBins, j, WJetScale, plots_cfg.binned)
    #                 getQCDandWJetsScaleFactor(histDict, varBins, i, 40)
            else:
                qcd_scale = []
                qcd_scale.append((0, 0))
            scaleFactors.append((qcd_scale[0][0], qcd_scale[0][1]))
            setQCD(histDict['QCD_%i' %j], qcd_scale, plots_cfg.binned)
    else:
        for j in range(scanPoints):
            if not options.method == 'LooseRegion':
                if not options.diffQCD:
                    scaleFactor = plots_cfg.QCD_scale[FS]                                                                                                                
                    setQCD(histDict['QCD_%i' %j], scaleFactor, plots_cfg.binned, j) 
                else:
                    setQCD(histDict['QCD_%i' %j], [(1.0, 0.0)]) 

                scaleFactors.append((plots_cfg.QCD_scale[FS][j][0], plots_cfg.QCD_scale[FS][j][1]))
            else:
                setQCD(histDict['QCD_%i' %j], [(0.0, 0.0)])                                                                                                       
                scaleFactors.append((0, 0))

#     if options.saveHisto:
#         oFile = r.TFile('/user_data/zmao/ZPrimeHistos/%s/QCD_all_%s.root' %(FS, varName),"recreate")
#         oFile.cd()
#         QCD_hist_tmp = r.TH1D("%s" %(varName), '', len(varBins)-1, varBins)
#         QCD_hist_tmp.Add(histDict['QCD'])
#         QCD_hist_tmp = fixNegativBins(QCD_hist_tmp)
#         QCD_hist_tmp.Write()
#         oFile.Close()
#         del QCD_hist_tmp

    histDict['Z#rightarrow#tau#tau'] = fixNegativBins(histDict['Z#rightarrow#tau#tau'])

    bkgStacks = []
    deltas = []
    endBin = histDict['WJets'].GetNbinsX()+2
    WJets_Integral = histDict['WJets'].Integral(0,endBin)
    WJets_CR_Integral = histDict['WJets_CR'].Integral(0,endBin)

    print 'WJets Isolated: %.3f +/- %.3f (%i)' %(WJets_Integral, math.sqrt(getError(histDict['WJets'], 0, endBin)), histDict['WJets'].GetEntries())
    print 'WJets Anti-Isolated: %.3f +/- %.3f (%i)' %(WJets_CR_Integral,  math.sqrt(getError(histDict['WJets_CR'], 0, endBin)), histDict['WJets_CR'].GetEntries())
    sf = 1.0
    sf_error = 0
    if WJets_CR_Integral > 0 and not options.diffWJets:
        sf = WJets_Integral/WJets_CR_Integral
        sf_error = calcSysUnc(sf, WJets_Integral, WJets_CR_Integral, math.sqrt(getError(histDict['WJets'], 0, endBin)), math.sqrt(getError(histDict['WJets_CR'], 0, endBin)))
#     sf = 0.07314
#     sf_error = 0.03038

    for i in range(scanPoints):
        if len(plots_cfg.WJetsScanRange) == 1:
            WJetScale = plots_cfg.WJetsScanRange[0]
        else:
            WJetScale = plots_cfg.WJetsScanRange[i]
        delta, result, error, error2, histDict_withError = buildDelta('%s_delta_%i' %(varName, i), histDict, varBins, varName, unit, relErrMax, 0.5, 1.5, i, WJetScale, sf, sf_error, FS)
        deltas.append((delta, result, error, error2, histDict_withError))

#     getWJetsScale(histDict, varName, start, end, sf)


    delta2 = None
    if options.ratio:
        if FS == 'et':
            delta2 = buildDelta('%s_delta_qcd' %varName, histDict, varBins, varName, unit, relErrMax, 0, 1.0, FS)
        else:
            delta2 = buildDelta('%s_delta_qcd' %varName, histDict, varBins, varName, unit, relErrMax, 0, 0.5, FS)
    for iCat in histDict.keys():
        histDict[iCat].Scale(1, option)
#     histDict['ZPrime_1000'].Scale(1, option)

    for i in range(scanPoints):
        if len(plots_cfg.WJetsScanRange) == 1:
            WJetScale = plots_cfg.WJetsScanRange[0]
        else:
            WJetScale = plots_cfg.WJetsScanRange[i]
        bkgStacks.append(buildStackFromDict(histDict, FS, option, i, WJetScale, sf, sf_error, options.looseRegion))


    return histDict, bkgStacks, deltas, delta2, scaleFactors


def setLegend(position, histDict, histDict2, bins, option = 'width', iQCD = 0):
    histList = []
    nbins = len(bins)

    if options.unblind:
        histList.append((histDict['Observed'], 'Observed (%.2f)' %histDict['Observed'].Integral(0, nbins+1, option), 'lep'))
    else:
        histList.append((histDict['Observed'], 'Observed', 'lep'))

    if plots_cfg.unc:
        for ikey in histDict2.keys():
            integral, unc = IntegralAndError(histDict2[ikey], nbins)
            print '%s (%.2f $\pm$ %.2f)' %(ikey, integral, unc)

    for ikey, iColor in reversed(defaultOrder):
        name = ikey
        if ikey == 'QCD':
            ikey = 'QCD_%i' %iQCD
        if ikey in histDict.keys():
            if plots_cfg.addIntegrals:
                if len(plots_cfg.WJetsScanRange) != 1 and ikey == 'WJets':
                    histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)*plots_cfg.WJetsScanRange[iQCD]), 'f'))
                elif ikey == 'WJets' and not (plots_cfg.unc):
                    histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)*plots_cfg.WJetsScanRange[0]), 'f'))
                elif plots_cfg.unc:
                    integral, unc = IntegralAndError(histDict2[ikey], nbins)
                    histList.append((histDict2[ikey], '%s (%.1f +/- %.1f)' %(name, integral, unc), 'f'))
                else:
                    histList.append((histDict[ikey], '%s (%.2f)' %(name, histDict[ikey].Integral(0, nbins+1, option)), 'f'))
            else:
                histList.append((histDict[ikey], '%s' %name, 'f'))
    if not (options.antiIso or options.antiEIso or options.antiMIso or options.noIso):
        signalSampleName = 'ZPrime_1000'
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

    p = []
    p_r = []
    legends = []
    counter = 0
    for iVarName, iVarBins, iUnit, relErrMax in plots_cfg.vars:
        histDict, bkgStacks, deltas, delta2, scaleFactors = buildHists(iVarName, iVarBins, iUnit, FS, option, relErrMax)
        iQCD = 0
        scanPoints = len(plots_cfg.scanRange)*(len(plots_cfg.scanRange)-1)/2
        WJetsScanPoints = len(plots_cfg.WJetsScanRange)
        if WJetsScanPoints > 1:
            scanPoints = WJetsScanPoints
        for iWJets in range (WJetsScanPoints):
            for iLower in range(len(plots_cfg.scanRange)):
                for iUpper in range(len(plots_cfg.scanRange) - iLower - 1):
                    bkgStack = bkgStacks[iQCD]
                    delta = deltas[iQCD][0]
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
                    
                    factor = 1.2
                    if options.logY:
                        r.gPad.SetLogy()
                        factor = 1.2#20
                    iMax = factor*max(bkgStack.GetMaximum(), histDict["Observed"].GetMaximum())
                    bkgStack.SetMaximum(iMax)
                    iMin = 0.0005#0.1
#                     iMin = 0.1#0.01

                    bkgStack.SetMinimum(iMin)   
     
                    bkgStack.Draw('hist H')
                    bkgStack.GetYaxis().SetNdivisions(510)
                    bkgStack.GetYaxis().SetTitleOffset(1.2)
                    bkgStack.GetYaxis().SetLabelSize(0.035)

                    deltas[iQCD][3].Scale(1, option)
                    deltas[iQCD][3].Draw('E2 same')


                    histDict["Observed"].SetMarkerStyle(8)
                    histDict["Observed"].SetMarkerSize(0.9)
                    if options.unblind or options.unblindPartial:
                        histDict["Observed"].Draw('PE same')
                    if not (options.antiIso or options.antiEIso or options.antiMIso or options.noIso):
                        histDict["ZPrime_1000"].Draw('H same')

                    #final state    
                    latex = r.TLatex()
                    latex.SetTextSize(0.03)

                    if options.logY:
                        h0 = iMax*0.01
                        h1 = iMax*0.01*0.5
                        h2 = iMax*0.01*0.5*0.5
                        h3 = iMax*0.01*0.5*0.5*0.5

                    else:
                        h0 = iMax*0.5
                        h1 = iMax*0.35
                        h2 = iMax*0.15
                        h3 = iMax*0.05

                    if 'pZeta' in iVarName:
                        position  = (0.2, 0.9 - 0.06*6, 0.47, 0.9)
                        latex.DrawLatex(iVarBins[7], iMax*0.98, getFinalStateLatex(FS))
                        if options.method == 'LooseRegion' and plots_cfg.showRegion:
                            latex.DrawLatex(iVarBins[7], h0, 'antiIso (%s, %s)' %(str(len(plots_cfg.scanRange[iLower])), str(len(plots_cfg.scanRange[iLower + iUpper + 1]))))
#                         elif options.method != 'SS' and plots_cfg.showRegion:
#                             latex.DrawLatex(iVarBins[7], h1, 'antiIso (%s, %s), scale = %.3f +/- %.3f' %(str(plots_cfg.scanRange[iLower]), str(plots_cfg.scanRange[iLower + iUpper + 1]), scaleFactors[iQCD][0], scaleFactors[iQCD][1]))
                        if options.chi2:
                            latex.DrawLatex(iVarBins[7], h2, '#chi^{2} = %.3f' %deltas[iQCD][1])
                        if options.KS:
                            latex.DrawLatex(iVarBins[7], h2, 'KS = %.3f' %deltas[iQCD][1])
                        if len(plots_cfg.WJetsScanRange) != 1:
                            latex.DrawLatex(iVarBins[7], h0, 'WJets Scale = %.2f' %plots_cfg.WJetsScanRange[iQCD])

                    else:
#                         position  = (0.2, 0.9 - 0.06*6, 0.47, 0.9)

                        position  = (0.6, 0.9 - 0.06*6, 0.87, 0.9)
#                         latex.DrawLatex(iVarBins[0], iMax*0.98, getFinalStateLatex(FS))
                        latex.DrawLatex(iVarBins[2], iMax*0.98, getFinalStateLatex(FS))
                        print iQCD
                        if options.method == 'LooseRegion' and plots_cfg.showRegion:
                            latex.DrawLatex(iVarBins[2], iMax*0.88, 'antiIso (%s, %s)' %(str(plots_cfg.scanRange[iLower]), str(plots_cfg.scanRange[iLower + iUpper + 1])))
#                         elif options.method != 'SS' and not options.diffQCD and plots_cfg.showRegion and not plots_cfg.binned:
#                             latex.DrawLatex(iVarBins[2], h1, 'antiIso range (%s, %s), scale = %.3f +/- %.3f' %(str(plots_cfg.scanRange[iLower]),
#                                                                                                     str(plots_cfg.scanRange[iLower + iUpper + 1]), 
#                                                                                                     scaleFactors[iQCD][0], scaleFactors[iQCD][1]))
                        if options.chi2:
                            latex.DrawLatex(iVarBins[2], h2, '#chi^{2} p-value = %.3f' %deltas[iQCD][1])
                        if options.KS:
                            latex.DrawLatex(iVarBins[2], h2, 'KS = %.3f' %deltas[iQCD][1])
                        if len(plots_cfg.WJetsScanRange) != 1:
                            latex.DrawLatex(iVarBins[2], h0, 'WJets Scale = %.2f' %plots_cfg.WJetsScanRange[iQCD])


#                     histDict['ZPrime_1000'].Scale(1000)
                    legends.append(setLegend(position, histDict, deltas[iQCD][4], iVarBins, option, iQCD))
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
                    delta.Draw()
                    deltas[iQCD][2].Draw('E2 same')
                    p_r[len(p)-1].SetGridy(1)

                    delta.Draw('same')

                    r.gPad.Update()
                    r.gPad.RedrawAxis()
                    c.cd()
                    yaxis =  r.TGaxis(0.1, 0.3, 0.1, 0.9, iMin, iMax, 505,"G")
                    yaxis.SetLabelSize(0.03)
                    yaxis.SetTitle("events / bin")
                    yaxis.SetTitleOffset(1.2)
                    yaxis.SetTitleSize(0.035)

                    totalPages = (len(plots_cfg.vars))*scanPoints - 1
                    if options.chi2 or options.KS:
                        totalPages += len(plots_cfg.vars)

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
                    iQCD += 1

            #plot scan plots
        if (options.chi2 or options.KS) and (iLower == len(plots_cfg.scanRange) - 1):
            counter2 = 0
            if options.chi2:
                yTitle = '#chi^{2} p-value'
            else:
                yTitle = 'KS Test result'
            drawOptions = ''
            r.gPad.SetTicky()
            r.gPad.SetTickx()
            if WJetsScanPoints <= 1:
                scan = r.TH2D("scan", "", len(plots_cfg.scanRange), 0, len(plots_cfg.scanRange), len(plots_cfg.scanRange), 0, len(plots_cfg.scanRange))
                scan_scale = r.TH2D("scan_scale", "", len(plots_cfg.scanRange), 0, len(plots_cfg.scanRange), len(plots_cfg.scanRange), 0, len(plots_cfg.scanRange))

                for i in range(len(plots_cfg.scanRange)):
                    scan.GetYaxis().SetBinLabel(i+1, str(plots_cfg.scanRange[i]))
                    scan.GetXaxis().SetBinLabel(i+1, str(plots_cfg.scanRange[i]))
                    for j in range(len(plots_cfg.scanRange)-i-1):
                        newValue = np.round(deltas[counter2][1]/0.001)*0.001
                        scan.Fill(i, j+i+1, newValue)
                        newValue_scale = np.round(scaleFactors[counter2][0]/0.001)*0.001
                        scan_scale.Fill(i, j+i+1, newValue_scale)
                        counter2 += 1

                scan.Draw('COLZ TEXT')
                c.Update()
                c.Print('%s' %psfile)
                c.Clear()
                r.gPad.SetTicky()
                r.gPad.SetTickx()
                scan.Draw('COLZ')
                scan_scale.Draw('TEXT SAME')
                c.Update()
            else:
                x = []
                results = []
                scales = []

                scan = r.TGraph(len(plots_cfg.WJetsScanRange))
                scan_scale = r.TGraph(len(plots_cfg.WJetsScanRange))
                for i in range(scanPoints):
                    scan.SetPoint(i, plots_cfg.WJetsScanRange[i], deltas[i][1])
                    scan_scale.SetPoint(i, plots_cfg.WJetsScanRange[i], scaleFactors[i][0])


                drawOptions = 'AEP'
                scan.SetTitle("scan; WJets Scale; %s" %yTitle)
                scan_scale.SetTitle("scan; WJets Scale; %s" %yTitle)
                scan_scale.SetMarkerStyle(2)
                scan.SetMarkerStyle(2)

#                 scan = r.TH1D("scan", "", len(plots_cfg.WJetsScanRange), 0, len(plots_cfg.WJetsScanRange))
#                 scan.SetTitle("scan; WJets Scale; %s" %yTitle)
#                 scan_scale = r.TH1D("scan_scale", "", len(plots_cfg.WJetsScanRange), 0, len(plots_cfg.WJetsScanRange))
#                 scan_scale.SetTitle("scan; WJets Scale; QCD L2T Scale Factor")
#                     
#                     scan.GetXaxis().SetBinLabel(i+1, str(plots_cfg.WJetsScanRange[i]))
#                     scan_scale.GetXaxis().SetBinLabel(i+1, str(plots_cfg.WJetsScanRange[i]))
#                     scan.Fill(i, deltas[counter2][1])
#                     scan_scale.Fill(i, scaleFactors[counter2][0])
#                     counter2 += 1
                scan.Draw(drawOptions)
                c.Update()
                c.Print('%s' %psfile)
                c.Clear()
                r.gPad.SetTicky()
                r.gPad.SetTickx()
                scan_scale.Draw(drawOptions)
                c.Update()
            print counter, totalPages
            if counter == totalPages:
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
