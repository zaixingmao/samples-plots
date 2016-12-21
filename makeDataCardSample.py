#!/usr/bin/env python

import ROOT as r
import tool
import os
import cProfile
from array import array
import optparse
import plots_cfg
import cutSampleTools
import plots
import plots_dataDrivenQCDandWJ
import math


r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000
r.gStyle.SetOptStat("e")
vec = r.vector('double')()

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
met = lvClass()
deltaTauES = lvClass()

list = plots_cfg.list

def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates
 
def setUpFloatVarsDict():
    varDict = {}
    names = ['m_vis', 'm_svfit', 'm_effective', 'xs', 'pt_1', 'pt_2', 'eta_1', 'eta_2', 'genEventWeight', 'triggerEff', 'PUWeight', 'cosDPhi', 'pZetaCut', 'pfMEt', 'tauTightIso', 'eleRelIso', 'tauMediumIso', 'tauLooseIso', 'mt_1', 'genMass', 'npv', 'BDT', 'm_tt']
    for iName in names:
        varDict[iName] = array('f', [0.])
    return varDict

def setUpIntVarsDict():
    varDict = {}
    names = ['initEvents', 'initSumWeights', 'nCSVL', 'tauDecayMode']
    for iName in names:
        varDict[iName] = array('l', [0])
    return varDict

def setUpCharVarsDict():
    varDict = {}
    names = ['sampleName', 'Category']
    for iName in names:
        varDict[iName] = bytearray(30)
    return varDict

def setUpYieldDict():
    yieldDict = {}
    histDict = {}
    names = ["QCD_in_B", "QCD_in_D", "QCDLoose", "QCD_in_F", "WJetsOSTight_MC", "WJetsOSLoose_MC", 'WJetsLoose']
    for iName in names:
        yieldDict[iName] = 0.0
        histDict[iName] = r.TH1F(iName, "", 1, 0., 2)
        histDict[iName].Sumw2()
    return yieldDict, histDict

def combineTree(inputFile, SF):
    sampleName = bytearray(30)
    genEventWeight = array('f', [0.])
    file = r.TFile(inputFile)
    oFileName_tmp = inputFile[:inputFile.find("_tmp")]+"_tmp3.root"
    oFileName_final = inputFile[:inputFile.find("_tmp")]+".root"
    newfile = r.TFile(oFileName_tmp,"recreate");

    eventTree_tmp = file.Get("eventTree_tmp")
    eventTree_tmp.SetBranchStatus("*",1)
    eventTree_tmp.SetBranchStatus("sampleName",0)
    eventTree_tmp.SetBranchStatus("genEventWeight",0)
    eventTree_tmp.Branch("sampleName" , sampleName, "sampleName[31]/C")
    eventTree_tmp.Branch("genEventWeight" , genEventWeight, "genEventWeight/F")
    genEventWeight[0] = -SF
    sampleName[:31] = "WJetsLoose"
    newTree = eventTree_tmp.CloneTree()
    newfile.cd()
    newTree.SetName("eventTree")
    newTree.Write()
    newfile.Close()

    os.system("hadd %s %s %s" %(oFileName_final, inputFile, oFileName_tmp))
    os.system("rm %s %s" %(inputFile, oFileName_tmp))

def printYield(yieldDict, WJets_SF, QCD_SF, QCD_D_F_SF, iFS):
    cats = {"VV": ("ZZTo2L2Q", "VVTo2L2Nu", "WZTo1L1Nu2Q", "WZTo1L3Nu", "ZZTo4L", "WWTo1L1Nu2Q", "WZTo2L2Q", "WZTo3LNu"),
            "TT": ("ST_antiTop_tW", "ST_top_tW", "ST_s-channel", "ST_t-channel_antiTop_tW", "ST_t-channel_top_tW", "TTJets"),
            "WJets": ("WJetsLoose",),
            "DYJets": ("DY_M-50to150", "DY_M-150"),
            "QCD": ("QCDLoose",),
            "Observed": ("dataTight",),
            }
    if iFS != 'em':
        cats["WJets"] = ("WJetsLoose", "-%f*QCDLoose" %QCD_D_F_SF)

    for ikey in yieldDict.keys():
        print ikey, yieldDict[ikey]

    print "***************************"

    for ikey in cats:
        tmp_yield = 0.0
        for iSample in cats[ikey]:
            sign = 1.0
            if iSample[0] == '-':
                sign = -1.0
                iSample = iSample[1:]
            if "*" in iSample:
                sign = sign*float(iSample[:iSample.find("*")])
                iSample = iSample[iSample.find("*")+1:]
            if iSample not in yieldDict.keys():
                print "missing sample", iSample
            else:
                tmp_yield += sign*yieldDict[iSample]
        if ikey == 'WJets':
            tmp_yield = tmp_yield*WJets_SF
        elif ikey == "QCD":
            tmp_yield = tmp_yield*QCD_SF
        print "%s: %.2f" %(ikey, tmp_yield)

def opts():
    parser = optparse.OptionParser()
    parser.add_option("-l", dest="location", default="/scratch/%s" % os.environ["USER"], help="location to be saved")
    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    parser.add_option("--FS", dest="FS", default='mt', help="final state product, et, tt")
    parser.add_option("--PUWeight", dest="PUWeight", default=False, action="store_true", help="")
    parser.add_option("--method", dest="method", default='Loose', help="")
    parser.add_option("--sys", dest="sys", default='', help="")
    parser.add_option("--pdf", dest="pdf", default=False, action="store_true", help="")
    parser.add_option("--trainnedMass", dest="trainnedMass", default="", help="")
    parser.add_option("--dataDrivenWJets", dest="dataDrivenWJets", default=False, action="store_true", help="")

    options, args = parser.parse_args()

    return options

def getBin(value, list):
    for i in range(1, len(list)):
        if list[i] > value:
            return i
    return len(list)-1

def getPDFWeight(fs, iSample, iCat, variation, m_eff):
    bin = getBin(m_eff, list)
    pdfCats = ["WJets", "Z#rightarrow#tau#tau", "t#bar{t}"]
#     pdfCats = ["WJets", "Z#rightarrow#tau#tau"]
    weight = 1.0
    if "Zprime" in iSample:
        massPoint = int(iSample[7:])
        if massPoint != 3000 and massPoint != 2500:
            weight = LUT_et_withPUWeight_signal.luts["DY_M-%ito%i_%s" %(massPoint, massPoint+50, variation)][0]
        elif massPoint == 2500:
            weight = LUT_et_withPUWeight_signal.luts["DY_M-%ito%i_%s" %(massPoint-50, massPoint+50, variation)][0]
        else:
            weight = LUT_et_withPUWeight_signal.luts["DY_M-%ito%i_%s" %(massPoint-200, massPoint, variation)][0]

    elif iCat in pdfCats and ("ST" not in iSample):
        if fs == 'et' or fs == 'mt':
            weight = LUT_et_withPUWeight.luts["%s_%s" %(iSample, variation)][bin-1]
        if fs == 'em':
            weight = LUT_em_withPUWeight.luts["%s_%s" %(iSample, variation)][bin-1]
    return weight

options = opts()

r.gStyle.SetOptStat(0)

controlRegionName = 'SS'
signalRegionName = 'OS'

QCD_SStoOS = 1.34


if options.method == 'Loose':
    controlRegionName = 'Loose'
    signalRegionName = 'Tight'

def loop_one_sample(iSample, iLocation, iCat, oTree, oTree_tmp, 
                    floatVarsDict, intVarsDict, charVarsDict, 
                    iFS, yieldDict, histDict):
    print 'combininig sample [%s] for datacard' %(iSample)
    if 'data' in iSample:
        isData = True
    else:
        isData = False
    if 'emb' in iSample:
        isEmbedded = True
    else:
        isEmbedded = False
    if ("Z'" in iSample):
        isSignal = True
    else:
        isSignal = False

    iFile = r.TFile(iLocation)
    iTree = iFile.Get("Ntuple")
    nEntries = iTree.GetEntries()
    iTree.SetBranchStatus("*",1)
    iTree.SetBranchStatus("sampleName",0)

    eventCount = iFile.Get('eventCount')
    eventCountWeighted = iFile.Get('eventCountWeighted')

    sumPtWeights = -1.0
#     if "TTJets" in iSample:
#         sumPtWeights = iFile.Get('eventCountPtWeighted').GetBinContent(1)

    yieldEstimator_OS = 0.0
    yieldEstimator_SS = 0.0
    fillcounter=0
    met = lvClass()
    for iEntry in range(nEntries):
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'looping over file %s' %(iSample), iEntry-1)
        uncWeight = 1.0
        region = 'none'
        met.SetCoordinates(iTree.met, 0.0, iTree.metphi, 0)

        l1.SetCoordinates(iTree.pt_1, iTree.eta_1, iTree.phi_1, iTree.m_1)
        l2.SetCoordinates(iTree.pt_2, iTree.eta_2, iTree.phi_2, iTree.m_2)

        if not plots_dataDrivenQCDandWJ.passCut(iTree, iFS, isData, options.sys):
            continue

        if plots_dataDrivenQCDandWJ.regionSelection(iTree, iFS, "signal", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            if isData:
                charVarsDict['sampleName'][:31] = 'data' + signalRegionName
            else:
                charVarsDict['sampleName'][:31] = iSample
                if isSignal:
                    charVarsDict['sampleName'][:31] = "Zprime_%s" %iSample[iSample.find("(")+1: iSample.find(")")]
            if iTree.q_1 != iTree.q_2:
                region = 'A'
            else:
                if isSignal:
                    continue
                region = 'B'

        elif plots_dataDrivenQCDandWJ.regionSelection(iTree, iFS, "control_iso", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            if isSignal:
                continue
            if iTree.q_1 == -iTree.q_2: #C region
                if iFS != "em":
                    if "WJets" in iSample:
                        continue
                region = 'C'
            else: #D region
                charVarsDict['sampleName'][:31] = 'QCD_in_D'
                region = 'D'
        elif iFS != 'em' and plots_dataDrivenQCDandWJ.regionSelection(iTree, iFS, "control_anti_iso", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            if isSignal:
                continue
            if not isData:
                continue
            if iTree.q_1 == -iTree.q_2: #E region
                charVarsDict['sampleName'][:31] = 'QCDLoose'
                region = 'E'
            else:
                charVarsDict['sampleName'][:31] = 'QCD_in_F'
                region = 'F'
        else:
            continue

        floatVarsDict['pt_1'][0] = iTree.pt_1
        floatVarsDict['pt_2'][0] = iTree.pt_2
        floatVarsDict['eta_1'][0] = iTree.eta_1
        floatVarsDict['eta_2'][0] = iTree.eta_2
        floatVarsDict['mt_1'][0] = iTree.mt_1

        floatVarsDict['genMass'][0] = 0.0
        if hasattr(iTree, 'X_to_ll'):
            floatVarsDict['genMass'][0] = iTree.X_to_ll

        if hasattr(iTree, 'BDT_both'):
            floatVarsDict['BDT'][0] = iTree.BDT_both
        else:
            floatVarsDict['BDT'][0] = -999

        floatVarsDict['triggerEff'][0] = iTree.trigweight_1*iTree.trigweight_2
        charVarsDict['Category'][:31] = iFS

        floatVarsDict['xs'][0] = iTree.xs

        if (80.94 < iTree.xs < 80.96) or (136.01 < iTree.xs < 136.03):
            floatVarsDict['xs'][0] = iTree.xs*0.108*3

        if 'TT' in iSample:
            floatVarsDict['xs'][0] = iTree.xs*0.8

        if 'WJets' in iSample:
            floatVarsDict['xs'][0] = floatVarsDict['xs'][0]*plots_cfg.WJetsScanRange[0]
        if "Zprime" in iSample:
            floatVarsDict['xs'][0] = plots.getZPrimeXS(iSample[7:])

        if eventCount:
            intVarsDict['initEvents'][0] = int(eventCount.GetBinContent(1))
        else:    
            intVarsDict['initEvents'][0] = int(iTree.initEvents)
        if eventCountWeighted:
            intVarsDict['initSumWeights'][0] = int(eventCountWeighted.GetBinContent(1))
        else:    
            intVarsDict['initSumWeights'][0] = int(iTree.initWeightedEvents)

        floatVarsDict['m_svfit'][0] = iTree.pfmet_svmc_mass
        floatVarsDict['m_effective'][0] = (l1 + l2 + met).mass()
        floatVarsDict['m_vis'][0] = (l1 + l2).mass()
        floatVarsDict['m_tt'][0] = iTree.m_tt

        if (options.sys == 'up' or options.sys == 'down') and (not isData):
            floatVarsDict['xs'][0] = floatVarsDict['xs'][0]*getPDFWeight(iFS, iSample, iCat, options.sys, floatVarsDict['m_effective'][0])

        intVarsDict['nCSVL'][0] = int(iTree.nCSVL)
        if iFS == 'et' or iFS == "mt":
            intVarsDict['tauDecayMode'][0] = int(iTree.tDecayMode)
            floatVarsDict['tauTightIso'][0] = iTree.tByTightCombinedIsolationDeltaBetaCorr3Hits
            floatVarsDict['tauMediumIso'][0] = iTree.tByMediumCombinedIsolationDeltaBetaCorr3Hits
            floatVarsDict['tauLooseIso'][0] = iTree.tByLooseCombinedIsolationDeltaBetaCorr3Hits
            if options.sys == 'tauUncUp':
                uncWeight += 0.2*iTree.pt_2/1000.
            if options.sys == 'tauUncDown':
                uncWeight -= 0.2*iTree.pt_2/1000.
        floatVarsDict['cosDPhi'][0] =  math.cos(iTree.phi_1 - iTree.phi_2)
        floatVarsDict['pZetaCut'][0] =  getattr(iTree, "%s_%s_PZeta" %(iFS[0], iFS[1])) - 3.1*getattr(iTree, "%s_%s_PZetaVis" %(iFS[0], iFS[1]))

        floatVarsDict['pfMEt'][0] = iTree.met
#         floatVarsDict['eleRelIso'][0] = iTree.eRelIso

        if options.PUWeight and not isData:
            floatVarsDict['PUWeight'][0] = cutSampleTools.getPUWeight(iTree.nTruePU)
            floatVarsDict['npv'][0] = iTree.nTruePU

        else:
            floatVarsDict['PUWeight'][0] = 1.0
            floatVarsDict['npv'][0] = 0

        if isData:
            floatVarsDict['genEventWeight'][0] = 1.0
            intVarsDict['initSumWeights'][0] = 1
            floatVarsDict['xs'][0] = 1.0/plots.lumi
            floatVarsDict['triggerEff'][0] = 1.0
        else:
            floatVarsDict['genEventWeight'][0] = uncWeight*iTree.genEventWeight
            if options.sys == 'topPt' and sumPtWeights != -1.0:
                intVarsDict['initSumWeights'][0] = int(sumPtWeights)
                floatVarsDict['genEventWeight'][0] = iTree.topPtWeight*floatVarsDict['genEventWeight'][0]

        if region == 'none':
            print "ERROR!!!!!"

        if region == "A":
            if charVarsDict['sampleName'][:31] in yieldDict.keys():
                yieldDict[str(charVarsDict['sampleName'][:31])] += floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
            else:
                yieldDict[str(charVarsDict['sampleName'][:31])] = floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
            if "WJets" in iSample:
                histDict["WJetsOSTight_MC"].Fill(1, floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0))
                yieldDict["WJetsOSTight_MC"] += floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
            oTree.Fill()

        elif region == "B":
            weight = 1
            if not isData:
                weight = -floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
            yieldDict["QCD_in_B"] += weight
            histDict["QCD_in_B"].Fill(1, weight)

        elif region == "C":
            if iFS == "em":
                charVarsDict['sampleName'][:31] = 'QCDLoose'
                if isData:
                    yieldDict["QCDLoose"] += 1
                else:
                    yieldDict["QCDLoose"] -= floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
                    floatVarsDict['genEventWeight'][0] = -1.0*floatVarsDict['genEventWeight'][0]
                oTree.Fill()
                if "WJets" in iSample:
                    floatVarsDict['genEventWeight'][0] = -1.0*floatVarsDict['genEventWeight'][0]
                    yieldDict['WJets' + controlRegionName] += floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
                    histDict["WJetsOSLoose_MC"].Fill(1, floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0))
                    charVarsDict['sampleName'][:31] = 'WJets' + controlRegionName
                    oTree.Fill()
            else:
                charVarsDict['sampleName'][:31] = 'WJetsLoose'
                if isData:
                    yieldDict['WJetsLoose'] += 1
                else:
                    floatVarsDict['genEventWeight'][0] = -1.0*floatVarsDict['genEventWeight'][0]
                    yieldDict['WJetsLoose'] += floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
                oTree.Fill()

        elif region == "D":
            weight = 1
            if not isData:
                weight = -floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
            yieldDict["QCD_in_D"] += weight
            histDict["QCD_in_D"].Fill(1, weight)

        elif region == "E" and iFS != 'em' and isData:
            yieldDict["QCDLoose"] += 1
            oTree_tmp.Fill()
            oTree.Fill()

        elif region == "F" and iFS != 'em' and isData:
            yieldDict["QCD_in_F"] += 1
            histDict["QCD_in_F"].Fill(1, 1)

    return yieldDict, histDict

def go():
    finalStates = expandFinalStates(options.FS)
    floatVarsDict = setUpFloatVarsDict()
    intVarsDict = setUpIntVarsDict()
    charVarsDict = setUpCharVarsDict()
    yieldDict, histDict = setUpYieldDict()
    if not finalStates:
        return 0
    for iFS in finalStates:
        tail = ''
        tail2 = ''
        totalQCD = 0.0

        if options.PUWeight:
            tail = '_withPUWeight'
        if options.sys:
            tail += "_%s" %options.sys
        if options.trainnedMass != "":
            tail += "_%s" %options.trainnedMass
        if iFS != 'em':
            tail += "_tmp"
            tail2 = tail + "2"
        oFileName = '%s/combined_%s%s.root' %(options.location, iFS, tail)
        oFileName2 = '%s/combined_%s%s.root' %(options.location, iFS, tail2)

        oFile = r.TFile(oFileName,"recreate")
        
        print 'creating datacard for final state: %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' %iFS
        oTree = r.TTree('eventTree','')
        oTree_tmp = r.TTree('eventTree_tmp','')

        for iVar in floatVarsDict.keys():
            oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
            oTree_tmp.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
        for iVar in intVarsDict.keys():
            oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/L" %iVar)
            oTree_tmp.Branch("%s" %iVar, intVarsDict[iVar], "%s/L" %iVar)
        for iVar in charVarsDict.keys():
            oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
            oTree_tmp.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
        for iSample, iLocation, iCat in plots_cfg.sampleList:
            iLocation += '%s_noIso.root' %iFS
            if options.trainnedMass != "":
                iLocation = "%s/%s/%s" %(iLocation[:iLocation.find("normal") + 6], options.trainnedMass, iLocation[iLocation.find("normal") + 6:])
                print iLocation
            yieldDict, histDict = loop_one_sample(iSample, iLocation, iCat, oTree, oTree_tmp, floatVarsDict, intVarsDict, charVarsDict, iFS, yieldDict, histDict)

        oFile.cd()

        tailName = "%s_1prong_3prong" %iFS
        if iFS == "em":
            tailName = "em"

        QCDScale = r.TH1F('QCD_%s_to_%s_%s' %(controlRegionName, signalRegionName, tailName), '', 1, 0, 1)
        QCDScale_D_F = r.TH1F('QCD_D_to_F_%s' %(tailName), '', 1, 0, 1)

        if iFS == "em":
            QCD_denum = "QCD_in_D"
        else:
            QCD_denum = "QCD_in_F"

        QCD_SF = histDict["QCD_in_B"].GetBinContent(1)/histDict[QCD_denum].GetBinContent(1)
        QCD_SF_unc = plots_dataDrivenQCDandWJ.calcSysUnc(QCD_SF, 
                                histDict["QCD_in_B"].GetBinContent(1), 
                                histDict[QCD_denum].GetBinContent(1), 
                                histDict["QCD_in_B"].GetBinError(1), 
                                histDict[QCD_denum].GetBinError(1))
        print "QCD SF: %.3f +/- %.3f" %(QCD_SF, QCD_SF_unc)
        QCDScale.Fill(0.5, QCD_SF)
        QCDScale.SetBinError(1, QCD_SF_unc)
        QCDScale.Write()
        QCD_D_F_SF = 0
        if iFS != "em":
            QCD_D_F_SF = histDict["QCD_in_D"].GetBinContent(1)/histDict[QCD_denum].GetBinContent(1)
            QCD_D_F_SF_unc = plots_dataDrivenQCDandWJ.calcSysUnc(QCD_SF, 
                                                                histDict["QCD_in_D"].GetBinContent(1), 
                                                                histDict[QCD_denum].GetBinContent(1), 
                                                                histDict["QCD_in_D"].GetBinError(1), 
                                                                histDict[QCD_denum].GetBinError(1))
            QCDScale_D_F.Fill(0.5, QCD_D_F_SF)
            QCDScale_D_F.SetBinError(1, QCD_D_F_SF_unc)
            QCDScale_D_F.Write()
        
        WJetsScale = r.TH1F('WJetsScale', '', 1, 0, 1)
        WJetsScale.Fill(0.5, plots_cfg.WJetsScanRange[0])
        WJetsScale.Write()

        WJetsLoose2Tight = r.TH1F('WJets_%s_to_%s_%s' %(controlRegionName, signalRegionName, tailName), '', 1, 0, 1)

        WJetsL2T = plots_cfg.WJetsLoose2Tight[0]
        WJetsL2T_unc = plots_cfg.WJetsLoose2Tight[1]
        print histDict["WJetsOSTight_MC"].GetEntries()
        if iFS == "em":
            WJetsL2T = histDict["WJetsOSTight_MC"].GetBinContent(1)/histDict["WJetsOSLoose_MC"].GetBinContent(1)
            WJetsL2T_unc = plots_dataDrivenQCDandWJ.calcSysUnc(WJetsL2T,
                                                                histDict["WJetsOSTight_MC"].GetBinContent(1),
                                                                histDict["WJetsOSLoose_MC"].GetBinContent(1),
                                                                histDict["WJetsOSTight_MC"].GetBinError(1),
                                                                histDict["WJetsOSLoose_MC"].GetBinError(1))

        WJetsLoose2Tight.Fill(0.5, WJetsL2T)
        WJetsLoose2Tight.SetBinError(1, WJetsL2T_unc)
        WJetsLoose2Tight.Write()

        oTree.Write()
        if iFS != 'em':
            oTree_tmp.Write()
        oFile.Close()

        printYield(yieldDict, WJetsL2T, QCD_SF, QCD_D_F_SF, iFS)
        if iFS != 'em':
            print "running combineTree(inputFile, %f)" %QCD_D_F_SF
            combineTree(oFileName, QCD_D_F_SF)

if __name__ == "__main__":
    if options.PUWeight:
        cutSampleTools.setupLumiReWeight()
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
    if options.PUWeight:
        cutSampleTools.freeLumiReWeight()

