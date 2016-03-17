#!/usr/bin/env python

import ROOT as r
from operator import itemgetter
import optparse
import tool
import sys

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

printedEvN = []

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def color(a, b):
    if a == b:
        lineColor = bcolors.OKGREEN
    else:
        lineColor = bcolors.FAIL
    return lineColor


def printInfo(name1="", varsList1=[], name2="", varsList2=[]):
    p = "%0.2f"
    dashes = '------'
    title = 'Event: %i Difference: %s' %(varsList1[1], p)
    title = title % abs(varsList1[5] - varsList2[5])
    printedEvN.append(varsList1[1])
    nChar = max([len(x) for x in [name1, name2]])
    outline0 = ' ' * (nChar + 2)
    outline1 = '%s: ' % name1.rjust(nChar)
    outline2 = '%s: ' % name2.rjust(nChar)
    foundDifferent = False
    for i in range(2, len(varsList1)/2):
        if varsList1[i*2] == "lumi" or varsList1[i*2] == 'njets':
            p = "%0.0f"
        elif 'dZ' in varsList1[i*2]:
            p = "%0.10f"
        else:
            p = "%0.2f"
        value1 = varsList1[i*2+1]
        value2 = varsList2[i*2+1]
        lineColor = color(value1, value2)
        dashes += '--------'
    
        if value1 == -9999:
            if value2 == -9999:
                lineColor = bcolors.OKGREEN
            outline1 += '%snull\033[0m\t' %(lineColor)
        else:
            outline1 += '%s%s\033[0m\t' %(lineColor, p)
            outline1 = outline1 % value1
        if value2 == -9999:
            outline2 += '%snull\033[0m\t' %(lineColor)
        else:
            outline2 += '%s%s\033[0m\t' %(lineColor, p)
            outline2 = outline2 % value2
        if varsList1[i*2] != 'mvaMet':
            foundDifferent = True
        outline0 += '%s%s\033[0m\t' %(lineColor, varsList1[i*2])

    if foundDifferent:
        print title
        print outline0
        print outline1
        print outline2
        print dashes

def printSingleInfo(name, varsList):
    dashes = '--------'
    if varsList[1] in printedEvN:
        return 1
    else:
        printedEvN.append(varsList[1])

    title = 'Event: %i' %varsList[1]
    outline0 = '       '    
    outline1 = name
    for i in range(2, len(varsList)/2):
        value = varsList[i*2+1]
        lineColor = bcolors.FAIL
        if value == -9999:
            outline1 += '%snull\033[0m\t' %(lineColor)
        else:
            outline1 += '%s%.1f\033[0m\t' %(lineColor,value)
        outline0 += '%s%s\033[0m\t' %(lineColor, varsList[i*2])
        dashes += '--------'
    print title
    print outline0
    print outline1
    print dashes

def getVetoValue(veto):
    if veto > 1:
        return 1
    else:
        return int(veto)

    if isinstance(veto, float):
        if veto > 1:
            return 1
        else:
            return int(veto)
    else:
        out = ' '.join(format(ord(x), 'b') for x in veto)
        return int(out)


def addVars(iTree, a):
    tau1 = lvClass()
    tau2 = lvClass()
    jet2 = lvClass()
    tau1.SetCoordinates(iTree.pt_1, iTree.eta_1, iTree.phi_1, iTree.m_2)
    tau2.SetCoordinates(iTree.pt_2, iTree.eta_2, iTree.phi_2, iTree.m_2)
#     jet2.SetCoordinates(iTree.bpt_2, iTree.beta_2, iTree.bphi_2, 0)
 

    a[(int(iTree.evt), int(iTree.lumi), iTree.run)] = ['evtNumber', int(iTree.evt), 
#             'mvaPhi', iTree.mvametphi, 
#             'muVeto', getVetoValue(iTree.extramuon_veto),
#             'iso2', iTree.iso_2, 
#               'cov00', iTree.metcov00,   #var to check
            'pt1', iTree.pt_1, 
              'lumi', int(iTree.lumi), 
              'run', iTree.run, 

#             'q1', iTree.q_1, 

#             'iso1', iTree.iso_1, 
#             'gen_match_1', iTree.gen_match_1, 
#             'gen_match_2', iTree.gen_match_2, 

#             'dZ_1', iTree.dZ_1, 

#             'iso1', iTree.byCombinedIsolationDeltaBetaCorrRaw3Hits_1, 
#             'tw_1', iTree.trigweight_1, 
            'pt1', iTree.pt_1, 
            'eta1', iTree.eta_1, 
#             'phi1', iTree.phi_1, 
#             'mass1', iTree1.m_1,
            'pt2', iTree.pt_2, 
            'eta2', iTree.eta_2, 
#             'iso2', iTree.iso_2,
#             'q2', iTree.q_2,  
#             'iso2', iTree.iso_2, 
#             'tw_2', iTree.trigweight_2, 

#             'phi2', iTree.phi_2, 
#             'dR', r.Math.VectorUtil.DeltaR(tau1, tau2),
            'met', iTree.met, 
#             'metphi', iTree.metphi, 
#             'mvamet', iTree.mvamet,
#             'mvametphi', iTree.mvametphi, 

#            'eleVeto', getVetoValue(iTree.extraelec_veto),
#            'muVeto', getVetoValue(iTree.extramuon_veto),

#             'muVeto', int(iTree.extramuon_veto), 

#             'njets', iTree.njets, 
#             'njets20', iTree.njetspt20, 
#             'nbtag', iTree.nbtag, 

#             'mass2', iTree1.m_2,
#             'jptraw1', iTree.jptraw_1,
#             'jpt_1', iTree.jpt_1, 
#             'jeta_1', iTree.jeta_1, 
#             'jphi_1', iTree.jphi_1, 
#             'jmva_1', iTree.jmva_1, 

#             'jptraw2', iTree.jptraw_2,
#             'jpt_2', iTree.jpt_2, 
#             'jeta_2', iTree.jeta_2, 
#             'jphi_2', iTree.jphi_2,
#             'jmva_2', iTree.jmva_2, 
# 
#             'npv', iTree.npv,
 #            'dZ_1', iTree.dZ_1, 
#             'dZ_2', iTree.dZ_2, 

# 
#             'bcsv_1', iTree.bcsv_1,
#             'bpt_1', iTree.bpt_1,
#             'beta_1', iTree.bjeta_1,
#             'bphi_1', iTree.bjphi_1,
#             'bcsv_2', iTree.bcsv_2,
#             'bpt_2', iTree.bpt_2,
#             'beta_2', iTree.bjeta_2,
#             'bphi_2', iTree.bjphi_2,
#             'dr2', r.Math.VectorUtil.DeltaR(tau2, jet2),
#             'bcsv_3', iTree.bcsv_3,
#             'bpt_3', iTree.bpt_3,
#             'beta_3', iTree.beta_3,
#             'NBTags', iTree.nbtag,
            'cov00', iTree.metcov00,
            'cov01', iTree.metcov01,
            'cov10', iTree.metcov10,
#             'mJJ', iTree.m_bb,
#             'svMass', iTree.m_sv
    ]
    return a

def addVars2(iTree):
    aList = addVars(iTree)
    aList.append('nPairs')
    aList.append(iTree.nTauPairs)
    return aList

def addVars3(iTree):
    aList = addVars(iTree)
    aList.append('nPairs')
    aList.append(1)
    return aList

def opts():
    desc = """This program loops over two .root files, counts the
events, and selects the set of common events.  For each of these
common events, it prints out the values of several variables.  If
--subset=same is passed, then printing is done only for events in
which the MVAMET agrees.  Likewise for --subset=diff.
"""
    parser = optparse.OptionParser(description=desc)
    parser.add_option("--f2", dest="location2", default='/nfs_scratch/zmao/test/SUSY-160_all_SYNC.root', help="location of file 1")
    parser.add_option("--f1", dest="location1", default='/nfs_scratch/zmao/test/SYNCFILE_SUSYGluGluToHToTauTau_M-160_tt_spring15.root', help="location of file 2")

    parser.add_option("--n2", dest="name2", default='Brown: ', help="inst name of file 1")
    parser.add_option("--n1", dest="name1", default='IC   : ', help="inst name of file 2")
    parser.add_option("--switch", dest="switch", default=False, action="store_true", help="")

    parser.add_option("--t2", dest="tree2", default='Ntuple', help="tree name of file 1")
    parser.add_option("--t1", dest="tree1", default='TauCheck', help="tree name of file 2")
    parser.add_option("--evN", dest="eventNumber", default=-1, help="look at specific event")
    parser.add_option("--subset", dest="style", default='diff', help="diff, same or all")
    parser.add_option("--nPair", dest="nTauPairs", default=0, help="Print number of tau pairs")
    
    options, args = parser.parse_args()
    return options


def checkSyncDev(options):
    location1 = options.location1
    tree1 = options.tree1
    name1 = options.name1
    location2 = options.location2
    tree2 = options.tree2
    name2 = options.name2

    if options.switch:
        location2 = options.location1
        tree2 = options.tree1
        name2 = options.name1
        location1 = options.location2
        tree1 = options.tree2
        name1 = options.name2

    eventNumber = int(options.eventNumber)

    iFile1 = r.TFile(location1)
    iTree1 = iFile1.Get(tree1)
    if not iTree1:
        sys.exit("FATAL: could not find %s:%s" % (location1, tree1))
    total1 = iTree1.GetEntries()

    iFile2 = r.TFile(location2)
    iTree2 = iFile2.Get(tree2)
    if not iTree2:
        msg = "\n".join(["FATAL: could not find %s:%s" % (location2, tree2),
                         "(%s:%s has %d entries)" % (location1, tree1, total1),
                         ])
        sys.exit(msg)
    total2 = iTree2.GetEntries()

    mvaMet1 = r.TH1F('mvaMet1', '',60, 0, 6)
    mvaMet2 = r.TH1F('mvaMet2', '',60, 0, 6)


    varsDict1 = {}
    varsDict2 = {}

    for i in range(total1):
        tool.printProcessStatus(i, total1, 'reading file1', i-1)
        iTree1.GetEntry(i)
        if int(options.nTauPairs):
            varsDict1 = addVars2(iTree1, varsDict1)
        else:
            varsDict1 = addVars(iTree1, varsDict1)
    print ''
    for i in range(total2):
        tool.printProcessStatus(i, total2, 'reading file2', i-1)
        iTree2.GetEntry(i)
        if int(options.nTauPairs):
            varsDict2 = addVars2(iTree2, varsDict2)
        else:
            varsDict2 = addVars(iTree2, varsDict2)
    print ''
    indexNotFound1 = []
    indexFound2 = 0
    matchedEvents = 0
    sameEvents = 0
    differentEvents = 0
    counter = 0
    for iKey in varsDict1.keys():
        tool.printProcessStatus(counter, total1, 'looping through', counter-1)

        if iKey in varsDict2 and iKey[0] == eventNumber:
            diff = (varsDict1[iKey][3]+1.0) - (varsDict2[iKey][3]+1.0)
            printInfo(name1, varsDict1[iKey], name2, varsDict2[iKey])
        elif iKey in varsDict2 and eventNumber == -1:
            matchedEvents += 1
            diff = (varsDict1[iKey][3]+1.0) - (varsDict2[iKey][3]+1.0)
            indexFound2 += 1
            if diff != 0.0 and (options.style == 'diff' or options.style == 'all'):
                printInfo(name1, varsDict1[iKey], name2, varsDict2[iKey])
                differentEvents += 1
            elif diff == 0 and (options.style == 'same' or options.style == 'all'):
                printInfo(name1, varsDict1[iKey], name2, varsDict2[iKey])
                sameEvents += 1

            else:
                indexNotFound1.append(iKey)
        elif iKey not in varsDict2:
            printSingleInfo(name1, varsDict1[iKey])
        counter += 1
    print ''
#     if options.style == 'all' or options.style == 'miss':
#         print 'Extra events in %s **********' %name1
#         for iKey in indexNotFound1:
#             printSingleInfo(name1, varsDict1[iKey])
#         print ' '
#         print 'Extra events in %s **********' %options.name2
#         for i_2 in range(total2):
#             if i_2 not in indexFound2:
#                 printSingleInfo(options.name2, varsList2[i_2])

    print '%s %i events' %(name1, total1)
    print '%s %i events' %(name2, total2)
    if options.style == 'diff' and not differentEvents:
        sameEvents = matchedEvents - differentEvents
    if options.style == 'same' and not sameEvents:
        differentEvents = matchedEvents - sameEvents
    if options.style == 'same' or options.style == 'diff':
        print "Out of %i matching events, %s%i\033[0m events with same MVAMet, %s%i\033[0m events with different MVAMet" %(matchedEvents, bcolors.OKGREEN, sameEvents, bcolors.FAIL, differentEvents)
    if options.style == 'miss':
        print "%s has an extra of %i events" %(name1, len(indexNotFound1))
        print "%s has an extra of %i events" %(name2, total2 - indexFound2)
    
    if eventNumber == -1:   
        return 1
    else:
        print "Event %i not found!" %eventNumber
        return 0


    c.Print('%s' %psfile)
    c.Close()

options = opts()
checkSyncDev(options)
