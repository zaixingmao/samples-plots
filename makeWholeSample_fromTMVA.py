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


lumi = 19.7


def makeWhole(iFileName, iLocation, weight0, weight1, weight2, sample):
    ifile = r.TFile(iLocation)
    iTestTree = ifile.Get('TestTree')
    iTrainTree = ifile.Get('TrainTree')
    sampleNames = []
    xsValues = {}
    initEvents = {}
    sampleNamesCounterTest_1 = {}
    sampleNamesCounterTest_2 = {}
    sampleNamesCounter_triggerEff1 = {}
    sampleNamesCounter_triggerEff2 = {}
    sampleNamesCounterTrain_1 = {}
    sampleNamesCounterTrain_2 = {}
    dataCounter1 = 0
    dataCounter2 = 0
    categories = []
    sampleName = bytearray(30)
    category_char = bytearray(30)
 
    validDict0 = {}
    validDict1 = {}
    validDict2 = {}

    mJJ = array('f', [0.])
    CSVJ2 = array('f', [0.])
    BDT = array('f', [0.])
    met = array('f', [0.])
    fMass = array('f', [0.])
    iso1 = array('f', [0.])
    iso2 = array('f', [0.])
    fMassKinFit = array('f', [0.])
    chi2KinFit = array('f', [0.])
    chi2KinFit2 = array('f', [0.])
    svMass = array('f', [0.])
    sampleName2 = array('I', [0])
    NBTags = array('I', [0])

    CSVJ2 = array('f', [0.])
    triggerEff = array('f', [0.])
    PUWeight = array('f', [0.])
    xs_value = array('f', [0.])
    initEvents_value = array('f', [0.])

    totalTest = iTestTree.GetEntries()
    totalTrain = iTrainTree.GetEntries()
    fracs0 = {}
    fracs1 = {}
    fracs2 = {}

    L_to_T_1M = r.TH1F('L_to_T_1M', 'L_to_T_1M', 1, 0, 1)
    L_to_T_2M = r.TH1F('L_to_T_2M', 'L_to_T_2M', 1, 0, 1)


    oFile = r.TFile('combined_%s.root' %iFileName, 'recreate')
    oTree = r.TTree('eventTree', '')

    oTree.Branch("sampleName", sampleName, "sampleName[31]/C")
    oTree.Branch("sampleName2", sampleName2, "sampleName2/I")
    oTree.Branch("Category", category_char, "Category[31]/C")
    oTree.Branch("NBTags", NBTags, "NBTags/I")
    oTree.Branch("iso1_1", iso1, "iso1_1/F")
    oTree.Branch("iso2_1", iso2, "iso2_1/F")

    oTree.Branch("mJJ", mJJ, "mJJ/F")
    oTree.Branch("PUWeight", PUWeight, "PUWeight/F")
    oTree.Branch("fMass", fMass, "fMass/F")
    oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
    oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
    oTree.Branch("chi2KinFit2", chi2KinFit2, "chi2KinFit2/F")
    oTree.Branch("svMass", svMass, "svMass/F")
    oTree.Branch("met", met, "met/F")
    oTree.Branch("BDT", BDT, "BDT/F")
    oTree.Branch("xs", xs_value, "xs_value/F")
    oTree.Branch("initEvents", initEvents_value, "initEvents/F")
    oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")

    oTree.Branch("triggerEff", triggerEff, "triggerEff/F")

    for i in range(totalTrain):
        tool.printProcessStatus(iCurrent=i+1, total=totalTest, processName = 'Looping sample [%s]' %iFileName)
        iTrainTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(iTrainTree.sampleName2, 'decode')
        sampleName2[0] = iTrainTree.sampleName2
        if tmpSampleName not in sampleNames:
            sampleNames.append(tmpSampleName)
            sampleNamesCounterTest_1[tmpSampleName] = 0.0
            sampleNamesCounterTest_2[tmpSampleName] = 0.0
            sampleNamesCounter_triggerEff1[tmpSampleName] = 0.0
            sampleNamesCounter_triggerEff2[tmpSampleName] = 0.0
            sampleNamesCounterTrain_1[tmpSampleName] = 0.0
            sampleNamesCounterTrain_2[tmpSampleName] = 0.0
            if iTrainTree.NBTags == 1:
                sampleNamesCounterTrain_1[tmpSampleName] = iTrainTree.triggerEff
            elif iTrainTree.NBTags > 1:
                sampleNamesCounterTrain_2[tmpSampleName] = iTrainTree.triggerEff
            initEvents[tmpSampleName] = iTrainTree.initEvents
            xsValues[tmpSampleName] = iTrainTree.xs
        else:
            if iTrainTree.NBTags == 1:
                sampleNamesCounterTrain_1[tmpSampleName] += iTrainTree.triggerEff
            elif iTrainTree.NBTags > 1:
                sampleNamesCounterTrain_2[tmpSampleName] += iTrainTree.triggerEff
        sampleName[:31] = tmpSampleName
        if tmpSampleName == 'data':
            sampleName[:31] = 'dataOSRelax'
        NBTags[0] = int(iTrainTree.NBTags)
        if iTrainTree.NBTags == 1:
            category_char[:31] = '1M'
        elif iTrainTree.NBTags > 1:
            category_char[:31] = '2M'
        else:
            category_char[:31] = 'None'
        PUWeight[0] = iTrainTree.PUWeight
        mJJ[0] = iTrainTree.mJJ
        CSVJ2[0] = iTrainTree.CSVJ2
        fMass[0] = iTrainTree.fMass
        fMassKinFit[0] = iTrainTree.fMassKinFit
        chi2KinFit[0] = iTrainTree.chi2KinFit
        chi2KinFit2[0] = iTrainTree.chi2KinFit2
        svMass[0] = iTrainTree.svMass
        triggerEff[0] = iTrainTree.triggerEff
        BDT[0] = iTrainTree.BDT
        xs_value[0] = iTrainTree.xs
        initEvents_value[0] = iTrainTree.initEvents
        iso1[0] = iTrainTree.iso1_1
        iso2[0] = iTrainTree.iso2_1

        if 'train' in sample:
            if iTrainTree.NBTags == 1:
                sampleNamesCounter_triggerEff1[tmpSampleName] += iTrainTree.triggerEff
            elif iTrainTree.NBTags > 1:
                sampleNamesCounter_triggerEff2[tmpSampleName] += iTrainTree.triggerEff
            oTree.Fill()         


    for i in range(totalTest):
        tool.printProcessStatus(iCurrent=i+1, total=totalTest, processName = 'Looping sample [%s]' %iFileName)
        iTestTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(iTestTree.sampleName2, 'decode')
        sampleName2[0] = iTestTree.sampleName2
        if tmpSampleName not in sampleNames:
            sampleNames.append(tmpSampleName)
            sampleNamesCounterTest_1[tmpSampleName] = 0.0
            sampleNamesCounterTest_2[tmpSampleName] = 0.0
            sampleNamesCounter_triggerEff1[tmpSampleName] = 0.0
            sampleNamesCounter_triggerEff2[tmpSampleName] = 0.0
            sampleNamesCounterTrain_1[tmpSampleName] = 0.0
            sampleNamesCounterTrain_2[tmpSampleName] = 0.0
            if iTestTree.NBTags == 1:
                sampleNamesCounterTest_1[tmpSampleName] = iTestTree.triggerEff
            elif iTestTree.NBTags > 1:
                sampleNamesCounterTest_2[tmpSampleName] = iTestTree.triggerEff
            initEvents[tmpSampleName] = iTestTree.initEvents
            xsValues[tmpSampleName] = iTestTree.xs

        else:
            if iTestTree.NBTags == 1:
                sampleNamesCounterTest_1[tmpSampleName] += iTestTree.triggerEff
            elif iTestTree.NBTags > 1:
                sampleNamesCounterTest_2[tmpSampleName] += iTestTree.triggerEff
        NBTags[0] = iTestTree.NBTags
        sampleName[:31] = tmpSampleName
        if tmpSampleName == 'data':
            sampleName[:31] = 'dataOSRelax'
        if iTestTree.NBTags == 1:
            category_char[:31] = '1M'
        elif iTestTree.NBTags > 1:
            category_char[:31] = '2M'
        else:
            category_char[:31] = 'None'
        BDT[0] = iTestTree.BDT
        PUWeight[0] = iTestTree.PUWeight
        mJJ[0] = iTestTree.mJJ
        CSVJ2[0] = iTestTree.CSVJ2
        fMass[0] = iTestTree.fMass
        fMassKinFit[0] = iTestTree.fMassKinFit
        chi2KinFit[0] = iTestTree.chi2KinFit
        chi2KinFit2[0] = iTestTree.chi2KinFit2
        met[0] = iTestTree.met
        xs_value[0] = iTestTree.xs
        initEvents_value[0] = iTestTree.initEvents
        iso1[0] = iTestTree.iso1_1
        iso2[0] = iTestTree.iso2_1
        svMass[0] = iTestTree.svMass
        triggerEff[0] = iTestTree.triggerEff
        if 'test' in sample:
            if iTestTree.NBTags == 1:
                sampleNamesCounter_triggerEff1[tmpSampleName] += iTestTree.triggerEff
            elif iTestTree.NBTags > 1:
                sampleNamesCounter_triggerEff2[tmpSampleName] += iTestTree.triggerEff
            oTree.Fill()

    print ''

    initEventsHist = r.TH1F('initEvents', 'initEvents', len(sampleNames), 0, len(sampleNames))
    initEvents_1tag = r.TH1F('initEvents_1tag', 'initEvents_1tag', len(sampleNames), 0, len(sampleNames))
    initEvents_2tag = r.TH1F('initEvents_2tag', 'initEvents_2tag', len(sampleNames), 0, len(sampleNames))
    initEvents_1tagDict = {}
    initEvents_2tagDict = {}
    xs = r.TH1F('xs', 'xs', len(sampleNames), 0, len(sampleNames))
    for iSample in sampleNames:
        if (sampleNamesCounterTest_1[iSample]+sampleNamesCounterTrain_1[iSample]+sampleNamesCounterTest_2[iSample]+sampleNamesCounterTrain_2[iSample]) != 0:
            fracs0[iSample] = (sampleNamesCounterTest_1[iSample]+sampleNamesCounterTest_2[iSample])/(sampleNamesCounterTest_1[iSample]+sampleNamesCounterTrain_1[iSample]+sampleNamesCounterTest_2[iSample]+sampleNamesCounterTrain_2[iSample])
        else:
            fracs0[iSample] = 0
        if fracs0[iSample] == 0:
            fracs0[iSample] = 0.5
        if (sampleNamesCounterTest_1[iSample]+sampleNamesCounterTrain_1[iSample]) != 0:
            fracs1[iSample] = (sampleNamesCounterTest_1[iSample])/(sampleNamesCounterTest_1[iSample]+sampleNamesCounterTrain_1[iSample])
        else:
            fracs1[iSample] = 0
        if fracs1[iSample] == 0:
            fracs1[iSample] = 0.5
        if (sampleNamesCounterTest_2[iSample]+sampleNamesCounterTrain_2[iSample]) != 0:
           fracs2[iSample] = (sampleNamesCounterTest_2[iSample])/(sampleNamesCounterTest_2[iSample]+sampleNamesCounterTrain_2[iSample])
        else:
            fracs2[iSample] = 0
        if fracs2[iSample] == 0:
            fracs2[iSample] = 0.5
        if ('train' in sample) and ('test' in sample):
            fracs0[iSample] = 1
        initEventsHist.Fill(iSample, initEvents[iSample]*fracs0[iSample])
        tmpInitEvents0 = initEvents[iSample]*fracs0[iSample]
        tmpInitEvents1 = initEvents[iSample]
        tmpInitEvents2 = initEvents[iSample]
        dataScale0 = 1.0
        dataScale1 = 1.0
        dataScale2 = 1.0

        if ('train' not in sample):
            initEvents_1tag.Fill(iSample, initEvents[iSample]*fracs1[iSample])
            initEvents_2tag.Fill(iSample, initEvents[iSample]*fracs2[iSample])
            initEvents_1tagDict[iSample] = initEvents[iSample]*fracs1[iSample]
            initEvents_2tagDict[iSample] = initEvents[iSample]*fracs2[iSample]
            tmpInitEvents1 = initEvents[iSample]*fracs1[iSample]
            tmpInitEvents2 = initEvents[iSample]*fracs2[iSample]
            if tmpInitEvents0 == 0:
                tmpInitEvents0 = 1
            if tmpInitEvents1 == 0:
                tmpInitEvents1 = 1
            if tmpInitEvents2 == 0:
                tmpInitEvents2 = 1        
            if fracs0[iSample] != 0:
                dataScale0 = 1.0/fracs0[iSample]
            if fracs1[iSample] != 0:
                dataScale1 = 1.0/fracs1[iSample]
            if fracs2[iSample] != 0:
                dataScale2 = 1.0/fracs2[iSample]

        if 'data' in iSample:
            xs.Fill(iSample, weight0)

        xs.Fill(iSample, xsValues[iSample])
        extraSpace = ''
        if len(iSample) < 8:
            extraSpace = '\t'

        
        if 'tt' in iSample:
            if 'tt' in validDict1.keys():
                validDict0['tt'] += (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
                validDict1['tt'] += sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
                validDict2['tt'] += sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]

            else:
                validDict0['tt'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
                validDict1['tt'] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
                validDict2['tt'] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]

        elif 'DY' in iSample:
            if 'DY' in validDict1.keys():
                validDict0['DY'] += (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
                validDict1['DY'] += sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
                validDict2['DY'] += sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]

            else:
                validDict0['DY'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
                validDict1['DY'] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
                validDict2['DY'] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]

        elif 'Z' in iSample:
            if 'Z' in validDict1.keys():
                validDict0['Z'] += (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
                validDict1['Z'] += sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
                validDict2['Z'] += sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]

            else:
                validDict0['Z'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
                validDict1['Z'] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
                validDict2['Z'] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]

        elif 'LNu' in iSample:
            if 'W' in validDict1.keys():
                validDict0['W'] += (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
                validDict1['W'] += sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
                validDict2['W'] += sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]

            else:
                validDict0['W'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
                validDict1['W'] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
                validDict2['W'] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]
        elif 'data' in iSample:
            validDict0['QCD'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])*weight0*dataScale0
            validDict1['QCD'] = sampleNamesCounter_triggerEff1[iSample]*weight1*dataScale1
            validDict2['QCD'] = sampleNamesCounter_triggerEff2[iSample]*weight2*dataScale2
            
        else:
            validDict0[iSample] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]
            validDict1[iSample] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]
            validDict2[iSample] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]
        extraSpace = ''
        extraSpace2 = ''
        if len(iSample) < 8:
            extraSpace = '\t'
        if initEvents[iSample] < 9999999:
            extraSpace2 = '\t'
        print 'cat1: %s%s\t%i%s\t%.3f' %(iSample,extraSpace, initEvents[iSample],extraSpace2, fracs1[iSample])
        print 'cat2: %s%s\t%i%s\t%.3f' %(iSample,extraSpace, initEvents[iSample],extraSpace2, fracs2[iSample])

    print "cat0"
    for iSample in validDict0.keys():
        print "%s\t%s%0.4f" %(iSample, extraSpace, validDict0[iSample])

    print "cat1"
    for iSample in validDict1.keys():
        print "%s\t%s%0.4f" %(iSample, extraSpace, validDict1[iSample])
    print ''
    print "cat2"
    for iSample in validDict2.keys():
        print "%s\t%s%0.4f" %(iSample,extraSpace, validDict2[iSample])
    print 1.0/fracs1['dataOSRelax']
    print 1.0/fracs2['dataOSRelax']
    L_to_T_1M.Fill(0.5, weight1/fracs1['dataOSRelax'])
    L_to_T_2M.Fill(0.5, weight2/fracs2['dataOSRelax'])

    oFile.cd()
    initEventsHist.Write()
    initEvents_1tag.Write()
    initEvents_2tag.Write()
    
    xs.Write()
    L_to_T_1M.Write()
    L_to_T_2M.Write()
    oTree.SetName('eventTree')
    oTree.Write()
    oFile.Close()

# weights = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012', 'tight', 'relaxed', True)
# massPoints = ['260','270','280','290','300','310','320','330','340','350']
massPoints = ['260', '300', '350']
nTreesList = ['150']
region = 'test'

for nTrees in nTreesList:
    postFix = '_7_n%s_mJJ' %nTrees
    for iMass in massPoints:
        makeWhole('H%s%s_%s' %(iMass,postFix,region), '/nfs_scratch/zmao/TMVA/TMVA%s%s.root' %(iMass,postFix), weights[0], weights[1], weights[2], region)
 #    postFix = '_8_n%s_mJJ_1M' %nTrees
#     for iMass in massPoints:
#         makeWhole('H%s%s_%s' %(iMass,postFix,region), '/scratch/zmao/TMVA/new3/TMVA%s%s.root' %(iMass,postFix), weights[0], weights[1], weights[2], region)
