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

r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000
r.gStyle.SetOptStat("e")

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
met = lvClass()

def getMEff(tree):
    l1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
    l2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)
    met.SetCoordinates(tree.pfMetEt, 0.0, tree.pfMetPhi, 0)
    return (l1 + l2 + met).mass()

def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates
 
def setUpFloatVarsDict():
    varDict = {}
    names = ['m_vis', 'm_svfit', 'm_effective', 'xs', 'pt_1', 'pt_2', 'genEventWeight', 'triggerEff', 'PUWeight', 'cosDPhi', 'pZetaCut', 'pfMEt', 'pfMEtNoHF', 'tauTightIso', 'eleRelIso', 'tauMediumIso', 'tauLooseIso']

    for iName in names:
        varDict[iName] = array('f', [0.])
    return varDict

def setUpIntVarsDict():
    varDict = {}
    names = ['initEvents', 'initSumWeights', 'nCSVL']
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

    options, args = parser.parse_args()

    return options

options = opts()

r.gStyle.SetOptStat(0)

controlRegionName = 'SS'
signalRegionName = 'OS'

if options.method == 'Loose':
    controlRegionName = 'Loose'
    signalRegionName = 'Tight'

def loop_one_sample(iSample, iLocation, oTree, floatVarsDict, intVarsDict, charVarsDict, iFS):
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

    for iEntry in range(nEntries):
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'looping over file %s' %(iSample), iEntry-1)

        if not plots.passCut(iTree, iFS, isData):
            continue

        if plots.regionSelection(iTree, "control", options.method):
            if isData:
                charVarsDict['sampleName'][:31] = 'data' + controlRegionName
            elif isSignal:
                continue
            else:
                charVarsDict['sampleName'][:31] = 'MC' + controlRegionName

        if plots.regionSelection(iTree, "signal", options.method):
           if isData:
                charVarsDict['sampleName'][:31] = 'data' + signalRegionName
           else:
               charVarsDict['sampleName'][:31] = iSample

        charVarsDict['Category'][:31] = iFS

        floatVarsDict['xs'][0] = iTree.xs
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


        floatVarsDict['m_vis'][0] = iTree.m_vis
        floatVarsDict['pt_1'][0] = iTree.pt_1
        floatVarsDict['pt_2'][0] = iTree.pt_2
        floatVarsDict['triggerEff'][0] = iTree.trigweight_1*iTree.trigweight_2
        floatVarsDict['m_svfit'][0] = iTree.pfmet_svmc_mass
        floatVarsDict['m_effective'][0] = getMEff(iTree)
        intVarsDict['nCSVL'][0] = plots.getNCSVLJets(iTree)
        floatVarsDict['cosDPhi'][0] =  math.cos(iTree.phi_1 - iTree.phi_2)
        floatVarsDict['pZetaCut'][0] =  getattr(iTree, "%s_%s_PZeta" %(iFS[0], iFS[1])) - 3.1*getattr(iTree, "%s_%s_PZetaVis" %(iFS[0], iFS[1]))
        floatVarsDict['pfMEt'][0] = iTree.pfMetEt
        floatVarsDict['pfMEtNoHF'][0] = iTree.pfMetNoHFEt
        floatVarsDict['tauTightIso'][0] = iTree.tByTightCombinedIsolationDeltaBetaCorr3Hits
        floatVarsDict['tauMediumIso'][0] = iTree.tByMediumCombinedIsolationDeltaBetaCorr3Hits
        floatVarsDict['tauLooseIso'][0] = iTree.tByLooseCombinedIsolationDeltaBetaCorr3Hits
        floatVarsDict['eleRelIso'][0] = iTree.eRelIso

        if options.PUWeight and not isData:
            floatVarsDict['PUWeight'][0] = cutSampleTools.getPUWeight(iTree.nTruePU)
        else:
            floatVarsDict['PUWeight'][0] = 1.0

        if isData:
            floatVarsDict['genEventWeight'][0] = 1.0
        else:
            floatVarsDict['genEventWeight'][0] = iTree.genEventWeight

        oTree.Fill()
        if plots.regionSelection(iTree, "control", options.method) and isData:
            yieldEstimator_SS += 1.0
        elif plots.regionSelection(iTree, "control", options.method) and not isData:
            yieldEstimator_SS -= floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)
        elif plots.regionSelection(iTree, "signal", options.method) and not isData:
            yieldEstimator_OS += floatVarsDict['triggerEff'][0]*floatVarsDict['PUWeight'][0]*floatVarsDict['genEventWeight'][0]*floatVarsDict['xs'][0]*plots.lumi/(intVarsDict['initSumWeights'][0]+ 0.0)

    print '  :total yield at %.2f/pb = %.2f (OS)' %(plots.lumi, yieldEstimator_OS)
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
            totalQCD += loop_one_sample(iSample, iLocation, oTree, floatVarsDict, intVarsDict, charVarsDict, iFS)

        oFile.cd()
        QCDScale = r.TH1F('%s_to_%s_%s' %(controlRegionName, signalRegionName, iFS), '', 1, 0, 1)
        QCDScale.Fill(0.5, plots_cfg.QCD_scale[iFS])
        QCDScale.Write()
        oTree.Write()
        oFile.Close()
        print 'total QCD: %.2f' %(totalQCD*plots_cfg.QCD_scale[iFS])


if __name__ == "__main__":
    if options.PUWeight:
        cutSampleTools.setupLumiReWeight()
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
    if options.PUWeight:
        cutSampleTools.freeLumiReWeight()

