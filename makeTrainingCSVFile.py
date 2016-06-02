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

defaultOrder = ["type", "met", "pZetaCut", "cosDPhi", "m_eff"]

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
 

def opts():
    parser = optparse.OptionParser()
    parser.add_option("-l", dest="location", default="/scratch/%s" % os.environ["USER"], help="location to be saved")
    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    parser.add_option("--FS", dest="FS", default='et', help="final state product, et, tt")
    parser.add_option("--method", dest="method", default='SS', help="")
    parser.add_option("--sys", dest="sys", default='', help="")
    parser.add_option("--trainnedMass", dest="trainnedMass", default="", help="")
    parser.add_option("--dataDrivenWJets", dest="dataDrivenWJets", default=False, action="store_true", help="")

    options, args = parser.parse_args()

    return options

def getBin(value, list):
    for i in range(1, len(list)):
        if list[i] > value:
            return i
    return len(list)-1


def writeToFile(dicToFill, ofile):
    output = ''
    for ikey in defaultOrder:
        if output == '':
            output += "%i" %dicToFill[ikey]
        else:
            output += ", %f" %dicToFill[ikey]
    output += "\n"
    ofile.write(output)

options = opts()

r.gStyle.SetOptStat(0)

controlRegionName = 'SS'
signalRegionName = 'OS'

if options.method == 'Loose':
    controlRegionName = 'Loose'
    signalRegionName = 'Tight'

def loop_one_sample(iSample, iLocation, iCat, iFS):
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

    dicToFill = {}
    for iVar in defaultOrder:
        dicToFill[iVar] = 0

    if isSignal:
        dicToFill["type"] = 1
    met = lvClass()

    outputName = "%s.csv" %iSample
    oFile = open(outputName, 'w')

    for iEntry in range(nEntries):
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'looping over file %s' %(iSample), iEntry-1)
        uncWeight = 1.0
        region = 'none'
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
        if options.method != 'SS' and iTree.q_1 == iTree.q_2 and (not options.dataDrivenWJets):
            continue

        if plots.regionSelection(iTree, iFS, "signal", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            if iTree.q_1 == iTree.q_2: #we don't need region B
                continue
            region = 'A'

        elif plots.regionSelection(iTree, iFS, "control", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            if isSignal:
                continue
            if options.dataDrivenWJets and iTree.q_1 == iTree.q_2: #D region
                region = 'D'

            elif options.dataDrivenWJets and iTree.q_1 == -iTree.q_2: #C region
                if "WJets" in iSample:
                    continue
                region = 'C'

            elif (not options.dataDrivenWJets) and iTree.q_1 == -iTree.q_2: #C region
                region = 'C'
            else:
                continue
        else:
            continue

        dicToFill["met"] = met.pt()
        dicToFill["pZetaCut"] = getattr(iTree, "%s_%s_PZeta" %(iFS[0], iFS[1])) - 3.1*getattr(iTree, "%s_%s_PZetaVis" %(iFS[0], iFS[1]))
        dicToFill["cosDPhi"] = math.cos(iTree.phi_1 - iTree.phi_2)
        dicToFill["m_eff"] = (l1 + l2 + met).mass()

        if region == 'none':
            print "ERROR!!!!!"

        if region == "A":
            writeToFile(dicToFill, oFile)
        if options.dataDrivenWJets and region == "D": #get QCD in C region
            writeToFile(dicToFill, oFile) 
        elif options.dataDrivenWJets and region == "C":
            writeToFile(dicToFill, oFile)
        elif (not options.dataDrivenWJets) and (region == 'C'):
            writeToFile(dicToFill, oFile)

def go():
    finalStates = expandFinalStates(options.FS)
    if not finalStates:
        return 0
    for iFS in finalStates:
        tail = ''
        totalQCD = 0.0

        
        print 'creating CSV for final state: %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' %iFS
        for iSample, iLocation, iCat in plots_cfg.sampleList:
            iLocation += '%s_noIso.root' %iFS
            if options.trainnedMass != "":
                iLocation = "%s/%s/%s" %(iLocation[:iLocation.find("normal") + 6], options.trainnedMass, iLocation[iLocation.find("normal") + 6:])
                print iLocation
            loop_one_sample(iSample, iLocation, iCat, iFS)
            print ''

if __name__ == "__main__":
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()

