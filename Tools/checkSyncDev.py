#!/usr/bin/env python

import ROOT as r
from operator import itemgetter
import optparse


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
    title = 'Event: %i Difference: %s' %(varsList1[1], p)
    title = title % abs(varsList1[3] - varsList2[3])
    printedEvN.append(varsList1[1])
    nChar = max([len(x) for x in [name1, name2]])
    outline0 = ' ' * (nChar + 2)
    outline1 = '%s: ' % name1.rjust(nChar)
    outline2 = '%s: ' % name2.rjust(nChar)
    foundDifferent = False
    for i in range(2, len(varsList1)/2):
        value1 = varsList1[i*2+1]
        value2 = varsList2[i*2+1]
        lineColor = color(value1, value2)
#         if lineColor == bcolors.OKGREEN:
#             continue        
        if value1 == 0:
            if value2 == -10000:
                lineColor = bcolors.OKGREEN
            outline1 += '%snull\033[0m\t' %(lineColor)
        else:
            outline1 += '%s%s\033[0m\t' %(lineColor, p)
            outline1 = outline1 % value1
        if value2 == -10000:
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
        print '-------------------------------------------------------------------------------------------------------------------------------------------------------'

def printSingleInfo(name, varsList):
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
        outline1 += '%s%0.3f\033[0m\t' %(lineColor,value)
        outline0 += '%s%s\033[0m\t' %(lineColor, varsList[i*2])
    print title
    print outline0
    print outline1
    print '-------------------------------------------------------------------------------------------------------------------------------------------------------'



def addVars(iTree):
    a = ['evtNumber', iTree.evt, 
            'mvaMet', iTree.mvamet, 
            'mvaMet', iTree.mvamet, 
            'mvaPhi', iTree.mvametphi, 
            'pt1', iTree.pt_1, 
#             'eta1', iTree.eta_1, 
            'iso1', iTree.iso_1, 
#             'phi1', iTree.phi_1, 
#             'mass1', iTree1.m_1,
            'pt2', iTree.pt_2, 
#             'eta2', iTree.eta_2, 
            'iso2', iTree.iso_2, 
#             'phi2', iTree.phi_2, 
#             'mass2', iTree1.m_2,
#             'jptraw1', iTree.jptraw_1,
            'jpt_1', iTree.jpt_1, 
#             'jeta_1', iTree.jeta_1, 
#             'jphi_1', iTree.jphi_1, 

#             'jptraw2', iTree.jptraw_2,
            'jpt_2', iTree.jpt_2, 
#             'jeta_2', iTree.jeta_2, 
#             'jphi_2', iTree.jphi_2,
# 
#             'npv', iTree.npv,
# 
#             'bcsv_1', iTree.bcsv_1,
            'bpt_1', iTree.bpt_1,
#             'beta_1', iTree.beta_1,
#             'bphi_1', iTree.bphi_1,
#             'bcsv_2', iTree.bcsv_2,
            'bpt_2', iTree.bpt_2,
#             'beta_2', iTree.beta_2,
#             'bphi_2', iTree.bphi_2,
#             'bcsv_3', iTree.bcsv_3,
#             'bpt_3', iTree.bpt_3,
#             'beta_3', iTree.beta_3,
#             'bphi_3', iTree.bphi_3,
            'cov00', iTree.mvacov00,
            'cov01', iTree.mvacov01,
            'cov10', iTree.mvacov10,
            'cov11', iTree.mvacov11]
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
    parser.add_option("--f1", dest="location1", default='/scratch/zmao/sync/H2hh300_newPhilHMetCalib.root', help="location of file 1")
    parser.add_option("--f2", dest="location2", default='/afs/cern.ch/user/k/kandroso/public/HTohhSync/sync_GGH_hh_bbtt_tautau.root', help="location of file 2")
    parser.add_option("--n1", dest="name1", default='Brown: ', help="inst name of file 1")
    parser.add_option("--n2", dest="name2", default='INFN:  ', help="inst name of file 2")

    parser.add_option("--t1", dest="tree1", default='TauCheck', help="tree name of file 1")
    parser.add_option("--t2", dest="tree2", default='syncTree', help="tree name of file 2")
    parser.add_option("--evN", dest="eventNumber", default=-1, help="look at specific event")
    parser.add_option("--subset", dest="style", default='diff', help="diff, same or all")
    parser.add_option("--nPair", dest="nTauPairs", default=0, help="Print number of tau pairs")
    
    options, args = parser.parse_args()
    return options


def checkSyncDev(options):
    eventNumber = int(options.eventNumber)
    iFile1 = r.TFile(options.location1)

    iTree1 = iFile1.Get(options.tree1)
    total1 = iTree1.GetEntries()

    iFile2 = r.TFile(options.location2)
    iTree2 = iFile2.Get(options.tree2)
    total2 = iTree2.GetEntries()

    mvaMet1 = r.TH1F('mvaMet1', '',60, 0, 6)
    mvaMet2 = r.TH1F('mvaMet2', '',60, 0, 6)


    varsList1 = []
    varsList2 = []

    for i in range(total1):
        iTree1.GetEntry(i)
        if int(options.nTauPairs):
            varsList1.append(addVars2(iTree1))
        else:
            varsList1.append(addVars(iTree1))

    for i in range(total2):
        iTree2.GetEntry(i)
        if int(options.nTauPairs):
            varsList2.append(addVars3(iTree2))
        else:
            varsList2.append(addVars(iTree2))

    varsList1 = sorted(varsList1, key=itemgetter(1), reverse=False)
    varsList2 = sorted(varsList2, key=itemgetter(1), reverse=False)

    evt2Last = varsList2[total2-1][1]

    indexNotFound1 = []
    indexFound2 = []
    matchedEvents = 0
    sameEvents = 0
    differentEvents = 0

    for i in range(total1):
        for j in range(total2):
            if varsList1[i][1] == varsList2[j][1] and varsList1[i][1] == eventNumber:
                diff = varsList1[i][3]/varsList2[j][3]
                printInfo(varsList1[i], varsList2[j])
                return 1
            elif varsList1[i][1] == varsList2[j][1] and eventNumber == -1:
    #             mvaMet1.Fill(varsList1[i][1]/varsList2[j][1])
                matchedEvents += 1
                diff = varsList1[i][3]/varsList2[j][3]
                mvaMet2.Fill(diff)
                indexFound2.append(j)
                if diff != 1 and (options.style == 'diff' or options.style == 'all'):
                    printInfo(options.name1, varsList1[i], options.name2, varsList2[j])
                    differentEvents += 1
                elif diff == 1 and (options.style == 'same' or options.style == 'all'):
                    printInfo(options.name1, varsList1[i], options.name2, varsList2[j])
                    sameEvents += 1
                break
            elif varsList1[i][1] < varsList2[j][1]:
                indexNotFound1.append(i)
                break
        if varsList1[i][1] > evt2Last:
            break

    if options.style == 'all':
        for i_1 in indexNotFound1:
            printSingleInfo(options.name1, varsList1[i_1])
        for i_2 in range(total2):
            if i_2 not in indexFound2:
                printSingleInfo(options.name2, varsList1[i_2])

    print '%s %i events' %(options.name1, total1)
    print '%s %i events' %(options.name2, total2)
    if options.style == 'diff' and not differentEvents:
        sameEvents = matchedEvents - differentEvents
    if options.style == 'same' and not sameEvents:
        differentEvents = matchedEvents - sameEvents

    print "Out of %i matching events, %s%i\033[0m events with same MVAMet, %s%i\033[0m events with different MVAMet" %(matchedEvents, bcolors.OKGREEN, sameEvents, bcolors.FAIL, differentEvents)

    if eventNumber == -1:   
        return 1
    else:
        print "Event %i not found!" %eventNumber
        return 0


    psfile = 'syncTest.pdf'
    c = r.TCanvas("c","Test", 800, 600)
    mvaMet2.SetLineColor(r.kRed)
    mvaMet2.Draw()
    # mvaMet1.Draw('same')

    c.Print('%s' %psfile)
    c.Close()

options = opts()
checkSyncDev(options)
