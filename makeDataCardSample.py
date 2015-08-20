#!/usr/bin/env python

import ROOT as r
import tool
import os
import cProfile
from array import array
import optparse
import plots_cfg


r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000
r.gStyle.SetOptStat("e")


def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates
 
def setUpFloatVarsDict():
    varDict = {}
    names = ['m_vis', 'xs', 'pt_1', 'pt_2', 'genEventWeight', 'triggerEff', 'PUWeight']

    for iName in names:
        varDict[iName] = array('f', [0.])
    return varDict

def setUpIntVarsDict():
    varDict = {}
    names = ['initEvents']
    for iName in names:
        varDict[iName] = array('i', [0])
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
    parser.add_option("--FS", dest="FS", default='tt', help="final state product, et, tt")

    options, args = parser.parse_args()

    return options

options = opts()

r.gStyle.SetOptStat(0)

def loop_one_sample(iSample, iLocation, oTree, floatVarsDict, intVarsDict, charVarsDict, iFS, initEvents = 0):
    print 'combininig sample [%s] for datacard' %(iSample)

    if 'data' in iSample:
        isData = True
    else:
        isData = False
    if 'emb' in iSample:
        isEmbedded = True
    else:
        isEmbedded = False
    if 'H2hh' in iSample:
        isSignal = True
    else:
        isSignal = False

    iFile = r.TFile(iLocation)
    iTree = iFile.Get("Ntuple")
    nEntries = iTree.GetEntries()
    iTree.SetBranchStatus("*",1)
    iTree.SetBranchStatus("sampleName",0)

    for iEntry in range(nEntries):
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'looping over file %s' %(iSample), iEntry-1)

        if iTree.q_1 == iTree.q_2:
            if isData:
                charVarsDict['sampleName'][:31] = 'dataSS'
            else:
                charVarsDict['sampleName'][:31] = 'MCSS'
        else:
           if isData:
                charVarsDict['sampleName'][:31] = 'dataOS'
           else:
               charVarsDict['sampleName'][:31] = iSample

        charVarsDict['Category'][:31] = iFS

        floatVarsDict['xs'][0] = iTree.xs*1000.0
        if initEvents != 0:
            intVarsDict['initEvents'][0] = initEvents
        else:
            intVarsDict['initEvents'][0] = iTree.initEvents
        floatVarsDict['m_vis'][0] = iTree.m_vis
        floatVarsDict['pt_1'][0] = iTree.pt_1
        floatVarsDict['pt_2'][0] = iTree.pt_2
        floatVarsDict['triggerEff'][0] = 1.0
        floatVarsDict['PUWeight'][0] = 1.0

        if isData:
            floatVarsDict['genEventWeight'][0] = 1.0
        else:
            floatVarsDict['genEventWeight'][0] = iTree.genEventWeight

        oTree.Fill()

    print '  '


def go():
    finalStates = expandFinalStates(options.FS)
    floatVarsDict = setUpFloatVarsDict()
    intVarsDict = setUpIntVarsDict()
    charVarsDict = setUpCharVarsDict()

    if not finalStates:
        return 0
    for iFS in finalStates:
        oFile = r.TFile('%s/combined_%s.root' %(options.location, iFS),"recreate")

        oTree = r.TTree('eventTree','')
        for iVar in floatVarsDict.keys():
            oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
        for iVar in intVarsDict.keys():
            oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/I" %iVar)
        for iVar in intVarsDict.keys():
            oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/I" %iVar)
        for iVar in charVarsDict.keys():
            oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
        for iSample, iLocation, initEvents in plots_cfg.dataCardSamplesList:
            iLocation += '_%s_inclusive.root' %iFS
            loop_one_sample(iSample, iLocation, oTree, floatVarsDict, intVarsDict, charVarsDict, iFS, initEvents)

        oFile.cd()
        QCDScale = r.TH1F('SS_to_OS_%s' %iFS, '', 1, 0, 1)

        QCDScale.Fill(0.5, plots_cfg.QCD_scale[iFS])
        QCDScale.Write()
        oTree.Write()
        oFile.Close()


if __name__ == "__main__":
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
