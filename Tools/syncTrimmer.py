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
        if iTree.iso_1 > 1.0 or iTree.iso_2 > 1.0:
            return False
    if 'relaxed' in cut:
        if not (iTree.iso_1 > 3 and iTree.iso_2 > 3):
            return False
    if 'same' in cut:
        if iTree.q_1 == -iTree.q_2:
            return False
    if 'opposite' in cut:
        if iTree.q_1 == iTree.q_2:
            return False
    if 'bTag' in cut:
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
for i in range(total):
    r.gStyle.SetOptStat(0)
    tool.printProcessStatus(iCurrent=i, total=total, processName = 'Looping sample %s' %iFile)
    iTree.GetEntry(i)
    if passCut(iTree, options.cut):
        oTree.Fill()
print ''

oFile.cd()
oTree.Write()
nSaved = oTree.GetEntries()
oFile.Close()

print 'saved %i events out of %i at: %s_%s.root' %(nSaved,total,options.inputFile, options.cut)