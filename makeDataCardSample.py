#!/usr/bin/env python2

import array, cProfile, math, optparse, os

import ROOT as r
r.PyConfig.IgnoreCommandLineOptions = True

import tool                      # progress
import plots_cfg                 # sample list; fake rates
import cutSampleTools            # PU
import plots                     # lumi; Z' xs
import plots_dataDrivenQCDandWJ  # analysis

def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates
 
def setUpFloatVarsDict():
    varDict = {}
    names = ['m_vis', 'm_svfit', 'm_effective', 'xs', 'pt_1', 'pt_2', 'eta_1', 'eta_2', 'genEventWeight', 'triggerEff', 'PUWeight', 'cosDPhi', 'pZetaCut', 'pfMEt', 'tauTightIso', 'eleRelIso', 'muRelIso', 'tauMediumIso', 'tauLooseIso', 'mt_1', 'genMass', 'npv', 'BDT', 'm_tt']
    for iName in names:
        varDict[iName] = array.array('f', [0.])
    return varDict

def setUpIntVarsDict():
    varDict = {}
    names = ['initEvents', 'initSumWeights', 'nCSVL', 'tauDecayMode']
    names += ['evt', 'lumi', 'run']
    for iName in names:
        varDict[iName] = array.array('l', [0])
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
    genEventWeight = array.array('f', [0.])
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
            "DYJets": ("DY_M-50to200", "DY_M-200to400", "DY_M-400to500", "DY_M-500to700", "DY_M-700to800", "DY_M-800to1000", "DY_M-1000to1500", "DY_M-1500to2000", "DY_M-2000to3000"),
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
    parser.add_option("--topPt", dest="topPt", default=False, action="store_true", help="")
    parser.add_option("--top8", dest="top8", default=False, action="store_true", help="")
    parser.add_option("--trainnedMass", dest="trainnedMass", default="", help="")
    parser.add_option("--againstLeptonSF", dest="againstLeptonSF", default=False, action="store_true", help="")

    options, args = parser.parse_args()

    return options

def getBin(value, lst):
    for i in range(1, len(lst)):
        if lst[i] > value:
            return i
    return len(lst)-1

def getPDFWeight(fs, iSample, iCat, variation, m_eff):
    bin = getBin(m_eff, plots_cfg.list)
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


def loop_one_sample(iSample, iLocation, iCat, oTree, oTree_tmp, 
                    floatVarsDict, intVarsDict, charVarsDict, 
                    iFS, yieldDict, histDict):
    print '\ncombining sample [%s] for datacard' %(iSample)

    isData = 'data' in iSample
    isSignal = "Z'" in iSample

    iFile = r.TFile(iLocation)
    iTree = iFile.Get("Ntuple")
    nEntries = iTree.GetEntries()
    iTree.SetBranchStatus("*",1)
    iTree.SetBranchStatus("sampleName",0)

    eventCount = iFile.Get('eventCount')
    eventCountWeighted = iFile.Get('eventCountWeighted')
    eventCountPtWeighted = iFile.Get('eventCountPtWeighted')

    l1 = lvClass()
    l2 = lvClass()
    met = lvClass()
    for iEntry in range(nEntries):
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'looping over file %s' %(iSample), iEntry-1)
        if not plots_dataDrivenQCDandWJ.passCut(iTree, iFS, isData, options.sys):
            continue

        met.SetCoordinates(iTree.met, 0.0, iTree.metphi, 0)
        l1.SetCoordinates(iTree.pt_1, iTree.eta_1, iTree.phi_1, iTree.m_1)
        l2.SetCoordinates(iTree.pt_2, iTree.eta_2, iTree.phi_2, iTree.m_2)

        region = one_event(iTree, iFS, iSample, isData, isSignal, intVarsDict, floatVarsDict, charVarsDict)

        if region is None:
            continue

        one_event_fill_stuff1(iTree, iFS, iSample, met, l1, l2, isData, isSignal,
                              intVarsDict, floatVarsDict, charVarsDict, eventCount, eventCountWeighted, eventCountPtWeighted)

        one_event_fill_stuff2(iTree, iFS, iSample, isData, isSignal,
                              intVarsDict, floatVarsDict, charVarsDict, region,
                              yieldDict, histDict, oTree, oTree_tmp)

    return yieldDict, histDict


def one_event(iTree, iFS, iSample, isData, isSignal, intVarsDict, floatVarsDict, charVarsDict):
    region = None

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
                return
            region = 'B'

    elif plots_dataDrivenQCDandWJ.regionSelection(iTree, iFS, "control_iso", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
        if isSignal:
            return
        if iTree.q_1 == -iTree.q_2: #C region
            if iFS != "em":
                if "WJets" in iSample:
                    return
            region = 'C'
        else: #D region
            charVarsDict['sampleName'][:31] = 'QCD_in_D'
            region = 'D'

    elif iFS != 'em' and plots_dataDrivenQCDandWJ.regionSelection(iTree, iFS, "control_anti_iso", plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
        if isSignal:
            return
        if not isData:
            return
        if iTree.q_1 == -iTree.q_2: #E region
            charVarsDict['sampleName'][:31] = 'QCDLoose'
            region = 'E'
        else:
            charVarsDict['sampleName'][:31] = 'QCD_in_F'
            region = 'F'
    else:
        return

    return region


def one_event_fill_stuff1(iTree, iFS, iSample, met, l1, l2, isData, isSignal,
                         intVarsDict, floatVarsDict, charVarsDict,
                          eventCount, eventCountWeighted, eventCountPtWeighted):

    uncWeight = 1.0
    intVarsDict['evt'][0] = iTree.evt
    intVarsDict['lumi'][0] = iTree.lumi
    intVarsDict['run'][0] = iTree.run

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

    if options.top8 and 'TT' in iSample:
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

    # floatVarsDict['m_svfit'][0] = iTree.pfmet_svmc_mass
    floatVarsDict['m_effective'][0] = (l1 + l2 + met).mass()
    floatVarsDict['m_vis'][0] = (l1 + l2).mass()
    # floatVarsDict['m_tt'][0] = iTree.m_tt

    if (options.sys == 'up' or options.sys == 'down') and (not isData):
        floatVarsDict['xs'][0] = floatVarsDict['xs'][0]*getPDFWeight(iFS, iSample, iCat, options.sys, floatVarsDict['m_effective'][0])

    intVarsDict['nCSVL'][0] = int(iTree.nCSVL)
    if iFS == 'et' or iFS == "mt":
        intVarsDict['tauDecayMode'][0] = int(iTree.tDecayMode)
        floatVarsDict['tauTightIso'][0] = iTree.tByTightCombinedIsolationDeltaBetaCorr3Hits
        floatVarsDict['tauMediumIso'][0] = iTree.tByMediumCombinedIsolationDeltaBetaCorr3Hits
        floatVarsDict['tauLooseIso'][0] = iTree.tByLooseCombinedIsolationDeltaBetaCorr3Hits
        if options.sys == 'tauUncUp':
            uncWeight += 0.05*iTree.pt_2/1000.
        if options.sys == 'tauUncDown':
            uncWeight -= 0.35*iTree.pt_2/1000.
    floatVarsDict['cosDPhi'][0] =  math.cos(iTree.phi_1 - iTree.phi_2)
    floatVarsDict['pZetaCut'][0] =  getattr(iTree, "%s_%s_PZeta" %(iFS[0], iFS[1])) - 3.1*getattr(iTree, "%s_%s_PZetaVis" %(iFS[0], iFS[1]))

    floatVarsDict['pfMEt'][0] = iTree.met
    if iFS == "et":
        floatVarsDict['eleRelIso'][0] = iTree.eRelIso
    if iFS == "mt":
        floatVarsDict['muRelIso'][0] = iTree.mRelIso

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
        if options.topPt and ("TTJets" in iSample):
            intVarsDict['initSumWeights'][0] = int(eventCountPtWeighted.GetBinContent(1))
            floatVarsDict['genEventWeight'][0] = iTree.topPtWeight*floatVarsDict['genEventWeight'][0]
        if (iFS == 'et' or iFS == 'mt') and not isData:
            floatVarsDict['genEventWeight'][0] = floatVarsDict['genEventWeight'][0]*0.95 #tauID

        if options.againstLeptonSF:
            if iFS == 'et':
                if (iTree.tIsPromptElectron):
                    floatVarsDict['genEventWeight'][0] = floatVarsDict['genEventWeight'][0]*plots_dataDrivenQCDandWJ.getAgainstLeptonSF('electron', 'Tight', abs(iTree.eta_2))
                if (iTree.tIsPromptMuon):
                    floatVarsDict['genEventWeight'][0] = floatVarsDict['genEventWeight'][0]*plots_dataDrivenQCDandWJ.getAgainstLeptonSF('muon', 'Loose', abs(iTree.eta_2))
            if iFS == 'mt':
                if (iTree.tIsPromptElectron):
                    floatVarsDict['genEventWeight'][0] = floatVarsDict['genEventWeight'][0]*plots_dataDrivenQCDandWJ.getAgainstLeptonSF('electron', 'VLoose', abs(iTree.eta_2))
                if (iTree.tIsPromptMuon):
                    floatVarsDict['genEventWeight'][0] = floatVarsDict['genEventWeight'][0]*plots_dataDrivenQCDandWJ.getAgainstLeptonSF('muon', 'Tight', abs(iTree.eta_2))


def one_event_fill_stuff2(iTree, iFS, iSample, isData, isSignal,
                          intVarsDict, floatVarsDict, charVarsDict, region,
                          yieldDict, histDict, oTree, oTree_tmp):

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

        WJetsL2T = plots_cfg.WJetsLoose2Tight[iFS][0]
        WJetsL2T_unc = plots_cfg.WJetsLoose2Tight[iFS][1]
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
    options = opts()
    lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

    r.gROOT.SetBatch(True)
    r.gErrorIgnoreLevel = 2000
    r.gStyle.SetOptStat("e")
    r.gStyle.SetOptStat(0)

    QCD_SStoOS = 1.34

    if options.method == 'Loose':
        controlRegionName = 'Loose'
        signalRegionName = 'Tight'
    else:
        controlRegionName = 'SS'
        signalRegionName = 'OS'

    if options.PUWeight:
        cutSampleTools.setupLumiReWeight()
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
    if options.PUWeight:
        cutSampleTools.freeLumiReWeight()

