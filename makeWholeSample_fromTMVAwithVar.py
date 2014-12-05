#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array
import makeWholeSample_cfg
import makeWholeTools

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

def checkName(name):
    if 'DY' in name:
        return 'DY'
    elif ('tt' in name) or (name == 't') or (name == 'tbar'):
        return 'tt'
    elif 'H2hh' in name:
        return 'signal'
    elif 'data' in name:
        return 'data'
    else:
        return 'Electroweak'

def getIsoShift(iso):
    scaleWeight_1M = 1.0
    scaleWeight_2M = 1.0
    if iso == 1.0:
        weights_1_5 = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012', 'tight', 'relaxed', True, True, 1.5)
        weights_1_0 = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012', 'tight', 'relaxed', True, True, 1.0)
        scaleWeight_1M = weights_1_0[1]/weights_1_5[1]
        scaleWeight_2M = weights_1_0[2]/weights_1_5[2]
    return scaleWeight_1M, scaleWeight_2M

def formDictFromHist(hist):
    nBins = hist.GetNbinsX()
    dict = {}
    for i in range(nBins):
        dict[hist.GetXaxis().GetBinLabel(i+1)] = hist.GetBinContent(i+1)
    return dict

def passCut(tree, iso, name):
    if 'OSRelax' in name:
        return 1
    elif (tree.iso1_1 > iso) or (tree.iso2_1 > iso):
        return 0
    else:
        return 1

def makeTestOnly(shift, iLocation, iso, isoShift_1M, isoShift_2M, signal = None, tt = None, DY = None, Electroweak = None):
    ifile = r.TFile(iLocation)

    iChain = r.TChain("eventTree")
    iChain.Add(iLocation)
    if signal != None:
        iChain.Add(signal)
    if tt != None:
        iChain.Add(tt)
    if DY != None:
        iChain.Add(DY)
    if Electroweak != None:
        iChain.Add(Electroweak)

    mJJ = array('f', [0.])
    CSVJ2 = array('f', [0.])
    BDT = array('f', [0.])
    met = array('f', [0.])
    fMass = array('f', [0.])
    fMassKinFit = array('f', [0.])
    iso1 = array('f', [0.])
    iso2 = array('f', [0.])
    NBTags = array('i', [0])

    chi2KinFit = array('f', [0.])
    chi2KinFit2 = array('f', [0.])
    svMass = array('f', [0.])
    triggerEff = array('f', [0.])
    PUWeight = array('f', [0.])
    xs_value = array('f', [0.])
    initEvents_value = array('i', [0])
    category_char = bytearray(30)

    iTree = ifile.Get('eventTree')
    total_old = iTree.GetEntries()

    oFileName = iLocation[0:iLocation.find('.root')]
    oFileName += '_%s_%.1f.root' %(shift, iso)
    oFile = r.TFile(oFileName,'recreate')
    L2T1 = ifile.Get('L_to_T_1M')
    L2T1.Scale(isoShift_1M)
    L2T2 = ifile.Get('L_to_T_2M')
    L2T2.Scale(isoShift_2M)
    initEventsHist = ifile.Get('initEvents')
    initEventsDict = formDictFromHist(initEventsHist)
    initEvents = array('f', [0.])
    sampleName = bytearray(30)

    iChain.LoadTree(0)

    oTree = r.TTree('eventTree', '')
    oTree.Branch("sampleName", sampleName, "sampleName[31]/C")
    oTree.Branch("Category", category_char, "Category[31]/C")
    oTree.Branch("mJJ", mJJ, "mJJ/F")
    oTree.Branch("BDT", BDT, "BDT/F")
    oTree.Branch("iso1_1", iso1, "iso1_1/F")
    oTree.Branch("iso2_1", iso2, "iso2_1/F")
    oTree.Branch("NBTags", NBTags, "NBTags/I")

    oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")
    oTree.Branch("met", met, "met/F")
    oTree.Branch("fMass", fMass, "fMass/F")
    oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
    oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
    oTree.Branch("chi2KinFit2", chi2KinFit2, "chi2KinFit2/F")
    oTree.Branch("svMass", svMass, "svMass/F")
    oTree.Branch("triggerEff", triggerEff, "triggerEff/F")
    oTree.Branch("PUWeight", PUWeight, "PUWeight/F")
    oTree.Branch("xs", xs_value, "xs/F")
    oTree.Branch("initEvents", initEvents_value, "initEvents/I")

    total = iChain.GetEntries()

    for i in range(total):
        tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample %s' %iLocation)
        iChain.LoadTree(i)
        iChain.GetEntry(i)
        tmpName = tool.nameEnDecoder(iChain.sampleName2, 'decode')
        if (tmpName not in initEventsDict.keys()) and ('H2hh' in tmpName):
            continue
        initEvents_value[0] = int(initEventsDict[tmpName])
        sampleName[:31] = tmpName
        checkedName = checkName(tmpName)
        mJJ[0] = iChain.mJJ
        CSVJ2[0] = iChain.CSVJ2
        fMass[0] = iChain.fMass
        fMassKinFit[0] = iChain.fMassKinFit
        chi2KinFit[0] = iChain.chi2KinFit
        chi2KinFit2[0] = iChain.chi2KinFit2
        triggerEff[0] = iChain.triggerEff
        PUWeight[0] = iChain.PUWeight
        xs_value[0] = iChain.xs
        NBTags[0] = iChain.NBTags
        iso1[0] = iChain.iso1_1
        iso2[0] = iChain.iso2_1
        if not passCut(iChain, iso, tmpName):
            continue
        if iChain.NBTags == 1:
            category_char[:31] = '1M'
        elif iChain.NBTags > 1:
            category_char[:31] = '2M'
        else:
            category_char[:31] = 'None'
        if i < total_old:
            met[0] = iChain.met
            svMass[0] = iChain.svMass
            BDT[0] = iChain.BDT
            if checkedName == 'data':
                oTree.Fill()
            if (Electroweak == None) and (checkedName == 'Electroweak'):
                oTree.Fill()
            if (signal == None) and (checkedName == 'signal'):
                oTree.Fill()
            if (tt == None) and (checkedName == 'tt'):
                oTree.Fill()
            if (DY == None) and (checkedName == 'DY'):
                oTree.Fill()
        else:
            met[0] = iChain.met.at(0)
            svMass[0] = iChain.svMass.at(0)
            BDT[0] = iChain.BDT_both

            oTree.Fill()
    print

    oFile.cd()
    L2T1.Write()
    L2T2.Write()
    oTree.Write()
    oFile.Close()

# masses = ['260', '300', '350']
masses = ['260', '270', '280', '290', '300', '310', '320', '330', '340', '350']
# shifts = ['', 'tauUp', 'tauDown']
shifts = ['']

postfix = 'tightopposite1M3rdLepVeto'
storedLocation = '/nfs_scratch/zmao/fromLogin05/BDT/'
iso = 1.5

isoShift_1M, isoShift_2M = getIsoShift(iso)

for iShift in shifts:
    location = '/scratch/zmao/forPlots/%s/ClassApp_both' %iShift
    for iMass in masses:
        signal = '%s_signal_%s_%s_testOnly.root' %(location,postfix, iMass)
        tt = '%s_tt_%s_%s_testOnly.root' %(location,postfix, iMass)
        DY = '%s_DYJetsToLL_all_%s_%s_testOnly.root' %(location,postfix, iMass)
        Electroweak = '%s_Electroweak_%s_%s_testOnly.root' %(location,postfix, iMass)
        if iShift == '':
            makeTestOnly(iShift, '%scombined_H%s_7_n150_mJJ_test.root' %(storedLocation,iMass), iso, isoShift_1M, isoShift_2M)
        elif 'tau' in iShift:
            makeTestOnly(iShift, '%scombined_H%s_7_n150_mJJ_test.root' %(storedLocation,iMass), iso, isoShift_1M, isoShift_2M, signal, tt, DY)
        elif 'jet' in iShift:
            makeTestOnly(iShift, '%scombined_H%s_7_n150_mJJ_test.root' %(storedLocation,iMass), iso, isoShift_1M, isoShift_2M, signal, tt, DY, Electroweak)
        