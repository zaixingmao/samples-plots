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
    runRanges = {'A': (0,193621),
                'B': (193621,196531),
                'C': (196531,203742),
                'D': (203742,208686)}
    if runRanges[cut][0] < iTree.run <= runRanges[cut][1]:
        return True
    else:
        return False

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
    if passCut(iTree, options.cut):
        oTree.Fill()
print ''

oFile.cd()
oTree.Write()
nSaved = oTree.GetEntries()
oFile.Close()

print 'saved %i events out of %i at: %s_%s.root' %(nSaved,total,options.inputFile, options.cut)