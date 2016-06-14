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

defaultOrder = ["type", "pt_1", "eta_1", "phi_1", 
                "pt_2", "eta_2", "phi_2", 
                "jpt_1", "jeta_1", "jphi_1", 
                "jpt_2", "jeta_2", "jphi_2", 
                "met", "met_phi", "pZetaCut", "m_eff"]

def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates
 

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    parser.add_option("--FS", dest="FS", default='em', help="final state product, et, tt")
    parser.add_option("--type", dest="type", default='train', help="")
    parser.add_option("--mass", dest="mass", default="2000", help="")
    parser.add_option("--l", dest="location", default="/user_data/zmao/TMVA/", help="")

    options, args = parser.parse_args()

    return options


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

def loop_one_sample(iCat, iLocation):
    print 'combininig sample [%s] for datacard' %(iCat)
    if 'obs' in iCat:
        isData = True
    else:
        isData = False

    if "signal" in iCat:
        isSignal = True
    else:
        isSignal = False

    iFile = r.TFile(iLocation)
    tail = "_train"
    if options.type == "train":
        iTree = iFile.Get("eventTree_train")
    else:
        iTree = iFile.Get("eventTree_test")
        tail = "_test"
    nEntries = iTree.GetEntries()
    iTree.SetBranchStatus("*",1)

    dicToFill = {}
    for iVar in defaultOrder:
        dicToFill[iVar] = 0

    if isSignal:
        dicToFill["type"] = 1

    outputName = "%s%s.csv" %(iCat, tail)
    oFile = open(outputName, 'w')

    for iEntry in range(nEntries):
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'looping over file %s' %(iCat), iEntry-1)
        
        for ikey in defaultOrder:
            if ikey == 'type':
                continue
            dicToFill[ikey] = getattr(iTree, ikey)        
        writeToFile(dicToFill, oFile)


def go():
    finalStates = expandFinalStates(options.FS)
    if not finalStates:
        return 0
    for fs in finalStates:
        tail = ''
        mass = options.mass
        inputFileDir = options.location
        sampleList = [
        #     ('WJets', '%s/WJets_LO_HT-0to100_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('WJets', '%s/WJets_LO_HT-100to200_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('WJets', '%s/WJets_LO_HT-200to400_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('WJets', '%s/WJets_LO_HT-400to600_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('WJets', '%s/WJets_LO_HT-600toInf_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        # 
        #     ('ZTT', '%s/DY-50to200_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('ZTT', '%s/DY-200to400_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('ZTT', '%s/DY-400to500_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('ZTT', '%s/DY-500to700_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('ZTT', '%s/DY-700to800_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('ZTT', '%s/DY-800to1000_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('ZTT', '%s/DY-1000to1500_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        # 
        #     ('VV', '%s/WZTo1L3Nu_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('VV', '%s/WWTo1L1Nu2Q_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('VV', '%s/WZTo1L1Nu2Q_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('VV', '%s/WZJets_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('VV', '%s/ZZTo2L2Q_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('VV', '%s/WZTo2L2Q_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('VV', '%s/VVTo2L2Nu_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('VV', '%s/ZZTo4L_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        # 
        #     ('TT', '%s/antiT_t-channel_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('TT', '%s/T_t-channel_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('TT', '%s/antiT_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
        #     ('TT', '%s/T_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
            ('TT', '%s/TTJets_LO_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
#             ('obs', '%s/data_Electron_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir,fs)),
            ('signal', '%s/ZPrime_%s_all_SYNC_%s_noIso_OSTight.root' %(inputFileDir, mass, fs)),
            ]

        
        print 'creating CSV for final state: %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' %fs
        for iCat, iLocation in sampleList:
            loop_one_sample(iCat, iLocation)
            print ''

if __name__ == "__main__":
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()

