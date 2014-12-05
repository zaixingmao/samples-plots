#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
j1Reg = lvClass()
j2Reg = lvClass()

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--i", dest="inputFile", default = '', help="")
    parser.add_option("--tree", dest="tree", default = 'TauCheck', help="")
    parser.add_option("--c", dest="cut", default = 'none', help="")
    options, args = parser.parse_args()
    return options

def passCut(iTree, cut):
    if 'none' in cut:
        return True
    if 'tight' in cut:
        if iTree.byCombinedIsolationDeltaBetaCorrRaw3Hits_1 > 1 or iTree.byCombinedIsolationDeltaBetaCorrRaw3Hits_2 > 1:
            return False
    if 'same' in cut:
        if iTree.q_1 == -iTree.q_2:
            return False
    if 'opposite' in cut:
        if iTree.q_1 == iTree.q_2:
            return False
    if '1M' in cut:
        if iTree.bcsv_2 <= 0:
            return False
        if iTree.bpt_1 < 0.679 or iTree.bcsv_2 > 0.679:
            return False
        if abs(iTree.beta_1) > 2.4 or abs(iTree.beta_2) > 2.4:
            return False
    if '2M' in cut:
        if iTree.bcsv_2 <= 0:
            return False
        if iTree.bpt_1 < 0.679 or iTree.bcsv_2 < 0.679:
            return False
        if abs(iTree.beta_1) > 2.4 or abs(iTree.beta_2) > 2.4:
            return False
    return True

options = opts()
iFile = options.inputFile
ifile = r.TFile('%s.root' %iFile)
iTree = ifile.Get(options.tree)
oFile = r.TFile("%s_%s.root" %(options.inputFile, options.cut),"recreate")
oTree = iTree.CloneTree(0)
total = iTree.GetEntries()
sigYeild = 0
for i in range(total):
    r.gStyle.SetOptStat(0)
    tool.printProcessStatus(iCurrent=i, total=total, processName = 'Looping sample %s' %iFile)
    iTree.GetEntry(i)
    if iTree.bpt_1 < 20:
        continue
    if iTree.bpt_2 < 20:
        continue
    if passCut(iTree, options.cut):
        oTree.Fill()
        sigYeild += iTree.trigweight_1*iTree.trigweight_2
print ''

# print (sigYeild/457250.0)*19.7*1000
print (sigYeild/570356.0)*19.7*1000

# oFile.cd()
# oTree.Write()
# nSaved = oTree.GetEntries()
# oFile.Close()
# 
# print 'saved %i events out of %i at: %s_%s.root' %(nSaved,total,options.inputFile, options.cut)