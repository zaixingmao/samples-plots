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
import math
import LUT_et_withPUWeight
import LUT_em_withPUWeight
import LUT_et_withPUWeight_signal
import LUT_em_withPUWeight_signal

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
    names = ['m_vis', 'm_svfit', 'm_effective', 'xs', 'pt_1', 'pt_2', 'eta_1', 'eta_2', 'genEventWeight', 'triggerEff', 'PUWeight', 'cosDPhi', 'pZetaCut', 'pfMEt', 'tauTightIso', 'eleRelIso', 'tauMediumIso', 'tauLooseIso', 'mt_1', 'genMass', 'npv', 'BDT']
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

def opts():
    parser = optparse.OptionParser()
    parser.add_option("-l", dest="location", default="/scratch/%s" % os.environ["USER"], help="location to be saved")
    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    parser.add_option("--FS", dest="FS", default='mt', help="final state product, et, tt")
    parser.add_option("--PUWeight", dest="PUWeight", default=False, action="store_true", help="")
    parser.add_option("--method", dest="method", default='SS', help="")
    parser.add_option("--sys", dest="sys", default='', help="")
    parser.add_option("--pdf", dest="pdf", default=False, action="store_true", help="")
    parser.add_option("--trainnedMass", dest="trainnedMass", default="", help="")

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
        if fs == 'et':
            weight = LUT_et_withPUWeight.luts["%s_%s" %(iSample, variation)][bin-1]
        if fs == 'em':
            weight = LUT_em_withPUWeight.luts["%s_%s" %(iSample, variation)][bin-1]
    return weight

options = opts()

r.gStyle.SetOptStat(0)

controlRegionName = 'SS'
signalRegionName = 'OS'

if options.method == 'Loose':
    controlRegionName = 'Loose'
    signalRegionName = 'Tight'

def loop_one_sample(iSample, iLocation, iCat, oTree, floatVarsDict, intVarsDict, charVarsDict, iFS):
    print 'combininig sample [%s] for datacard' %(iSample)
    if 'data' in iSample:
        isData = True
    else:
        isData = False
    if 'emb' in iSample:
        isEmbedded = True
    else:
        isEmbedded = False
    if ('H2hh' in iSample) or ('ggH' in iSample) or ('Zprime' in iSample):
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

    yieldEstimator_OS = 0.0
    yieldEstimator_SS = 0.0
    fillcounter=0
    met = lvClass()
    for iEntry in range(nEntries):
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'looping over file %s' %(iSample), iEntry-1)
        uncWeight = 1.0

        if options.sys == 'jetECUp' and not isData:
            met.SetCoordinates(iTree.pfMet_jesUp_Et, 0.0, iTree.pfMet_jesUp_Phi, 0)
        elif options.sys == 'jetECDown' and not isData:
            met.SetCoordinates(iTree.pfMet_jesDown_Et, 0.0, iTree.pfMet_jesDown_Phi, 0)
        elif (options.sys == 'tauECUp' or options.sys == 'tauECDown') and (not isData) and iTree.tIsTauh:
            met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)
            if iTree.pt_2 - iTree.tPt > 0:
                deltaTauES.SetCoordinates(abs(iTree.pt_2 - iTree.tPt), 0.0, -iTree.tPhi, 0)
            else:
                deltaTauES.SetCoordinates(abs(iTree.pt_2 - iTree.tPt), 0.0, iTree.tPhi, 0)
            met = met + deltaTauES
        else:
            met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)

        l1.SetCoordinates(iTree.pt_1, iTree.eta_1, iTree.phi_1, iTree.m_1)
        l2.SetCoordinates(iTree.pt_2, iTree.eta_2, iTree.phi_2, iTree.m_2)

        if not plots.passCut(iTree, iFS, isData, l1, l2, met, options.sys):
            continue
        if options.method != 'SS' and iTree.q_1 == iTree.q_2:
            continue

        if plots.regionSelection(iTree, iFS, "control", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            if isData:
                charVarsDict['sampleName'][:31] = 'data' + controlRegionName
            elif isSignal:
                continue
            else:
                charVarsDict['sampleName'][:31] = 'MC' + controlRegionName
        elif plots.regionSelection(iTree, iFS, "signal", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
           if isData:
                charVarsDict['sampleName'][:31] = 'data' + signalRegionName
           else:
               charVarsDict['sampleName'][:31] = iSample
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

#         floatVarsDict['m_svfit'][0] = iTree.pfmet_svmc_mass
        floatVarsDict['m_effective'][0] = (l1 + l2 + met).mass()
        floatVarsDict['m_vis'][0] = (l1 + l2).mass()

        if (options.sys == 'up' or options.sys == 'down') and (not isData):
            floatVarsDict['xs'][0] = floatVarsDict['xs'][0]*getPDFWeight(iFS, iSample, iCat, options.sys, floatVarsDict['m_effective'][0])

        intVarsDict['nCSVL'][0] = plots.getNCSVLJets(iTree, options.sys, isData)
        if iFS == 'et':
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
        if options.sys == 'jetECUp' and not isData:
            floatVarsDict['pfMEt'][0] = iTree.pfMet_jesUp_Et
        elif options.sys == 'jetECDown' and not isData:
            floatVarsDict['pfMEt'][0] = iTree.pfMet_jesDown_Et
        else:
            floatVarsDict['pfMEt'][0] = iTree.pfMetEt
        floatVarsDict['eleRelIso'][0] = iTree.eRelIso

        if options.PUWeight and not isData:
            floatVarsDict['PUWeight'][0] = cutSampleTools.getPUWeight(iTree.nTruePU)
            floatVarsDict['npv'][0] = iTree.nTruePU

        else:
            floatVarsDict['PUWeight'][0] = 1.0
            floatVarsDict['npv'][0] = 0

        if isData:
            floatVarsDict['genEventWeight'][0] = 1.0
        else:
            floatVarsDict['genEventWeight'][0] = uncWeight*iTree.genEventWeight

        oTree.Fill()
        if (charVarsDict['sampleName'][:31] == 'MC' + controlRegionName) and ("WJets" in iSample):
            charVarsDict['sampleName'][:31] = 'WJets' + controlRegionName
            oTree.Fill()
            

        if plots.regionSelection(iTree, iFS, "control", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]) and isData:
            yieldEstimator_SS += 1.0
        elif plots.regionSelection(iTree, iFS, "control", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]) and not isData:
            yieldEstimator_SS -= floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
        elif plots.regionSelection(iTree, iFS, "signal", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]) and not isData:
            yieldEstimator_OS += floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
            fillcounter += 1
    print '  :total yield at %.2f/pb = %.2f (OS)' %(plots.lumi, yieldEstimator_OS), fillcounter
    return yieldEstimator_SS

def go():
    finalStates = expandFinalStates(options.FS)
    floatVarsDict = setUpFloatVarsDict()
    intVarsDict = setUpIntVarsDict()
    charVarsDict = setUpCharVarsDict()
    if not finalStates:
        return 0
    for iFS in finalStates:
        tail = ''
        totalQCD = 0.0

        if options.PUWeight:
            tail = '_withPUWeight'
        if options.sys:
            tail += "_%s" %options.sys
        if options.trainnedMass != "":
            tail += "_%s" %options.trainnedMass

        oFile = r.TFile('%s/combined_%s%s.root' %(options.location, iFS, tail),"recreate")
        
        print 'creating datacard for final state: %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' %iFS
        oTree = r.TTree('eventTree','')
        for iVar in floatVarsDict.keys():
            oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
        for iVar in intVarsDict.keys():
            oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/L" %iVar)
        for iVar in charVarsDict.keys():
            oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
        for iSample, iLocation, iCat in plots_cfg.sampleList:
            iLocation += '%s_noIso.root' %iFS
            if options.trainnedMass != "":
                iLocation = "%s/%s/%s" %(iLocation[:iLocation.find("normal") + 6], options.trainnedMass, iLocation[iLocation.find("normal") + 6:])
                print iLocation
            totalQCD += loop_one_sample(iSample, iLocation, iCat, oTree, floatVarsDict, intVarsDict, charVarsDict, iFS)

        oFile.cd()
        QCDScale = r.TH1F('QCD_%s_to_%s_%s' %(controlRegionName, signalRegionName, iFS), '', 1, 0, 1)
        QCDScale.Fill(0.5, plots_cfg.QCD_scale[iFS][0][0])
        QCDScale.SetBinError(1, plots_cfg.QCD_scale[iFS][0][1])
        QCDScale.Write()
        if iFS == 'et':
            QCDScale_1prong_3prong = r.TH1F('QCD_%s_to_%s_%s_1prong_3prong' %(controlRegionName, signalRegionName, iFS), '', 1, 0, 1)
            QCDScale_1prong_3prong.Fill(0.5, plots_cfg.QCD_scale_1prong_3prong[0])
            QCDScale_1prong_3prong.SetBinError(1, plots_cfg.QCD_scale_1prong_3prong[1])
            QCDScale_1prong_3prong.Write()
            WJetsLoose2Tight_1prong_3prong = r.TH1F('WJets_%s_to_%s_%s_1prong_3prong' %(controlRegionName, signalRegionName, iFS), '', 1, 0, 1)
            WJetsLoose2Tight_1prong_3prong.Fill(0.5, plots_cfg.WJetsLoose2Tigh_1prong_3prong[0])
            WJetsLoose2Tight_1prong_3prong.SetBinError(1, plots_cfg.WJetsLoose2Tigh_1prong_3prong[1])
            WJetsLoose2Tight_1prong_3prong.Write()
        WJetsLoose2Tight = r.TH1F('WJets_%s_to_%s_%s' %(controlRegionName, signalRegionName, iFS), '', 1, 0, 1)
        WJetsLoose2Tight.Fill(0.5, plots_cfg.WJetsLoose2Tight[0])
        WJetsLoose2Tight.SetBinError(1, plots_cfg.WJetsLoose2Tight[1])
        WJetsLoose2Tight.Write()
        WJetsScale = r.TH1F('WJetsScale', '', 1, 0, 1)
        WJetsScale.Fill(0.5, plots_cfg.WJetsScanRange[0])
        WJetsScale.Write()

        oTree.Write()
        oFile.Close()
        print 'total QCD: %.2f' %(totalQCD*plots_cfg.QCD_scale[iFS][0][0])


if __name__ == "__main__":
    if options.PUWeight:
        cutSampleTools.setupLumiReWeight()
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
    if options.PUWeight:
        cutSampleTools.freeLumiReWeight()

