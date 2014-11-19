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
    category2 = bytearray(30)
 
    validDict0 = {}
    validDict1 = {}
    validDict2 = {}

    mJJReg = array('f', [0.])
    mJJ = array('f', [0.])
    CSVJ2 = array('f', [0.])
    BDT = array('f', [0.])
    met = array('f', [0.])
    fMass = array('f', [0.])
    fMassKinFit = array('f', [0.])
    chi2KinFit = array('f', [0.])
    chi2KinFit2 = array('f', [0.])
    svMass = array('f', [0.])
    CSVJ2 = array('f', [0.])
    triggerEff = array('f', [0.])

    totalTest = iTestTree.GetEntries()
    totalTrain = iTrainTree.GetEntries()
    fracs0 = {}
    fracs1 = {}
    fracs2 = {}

    L_to_T_1M = r.TH1F('L_to_T_1M', 'L_to_T_1M', 1, 0, 1)
    L_to_T_2M = r.TH1F('L_to_T_2M', 'L_to_T_2M', 1, 0, 1)
    L_to_T_1M.Fill(0.5, weight1)
    L_to_T_2M.Fill(0.5, weight2)

    oFile = r.TFile('combined_%s.root' %iFileName, 'recreate')
    oTree = r.TTree('eventTree', '')

    oTree.Branch("sampleName", sampleName, "sampleName[31]/C")
    oTree.Branch("Category", category2, "Category[31]/C")

    oTree.Branch("mJJReg", mJJReg, "mJJReg/F")
    oTree.Branch("mJJ", mJJ, "mJJ/F")
    oTree.Branch("fMass", fMass, "fMass/F")
    oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
    oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
    oTree.Branch("chi2KinFit2", chi2KinFit2, "chi2KinFit2/F")
    oTree.Branch("svMass", svMass, "svMass/F")
    oTree.Branch("met", met, "met/F")
    oTree.Branch("BDT", BDT, "BDT/F")

    oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")

    oTree.Branch("triggerEff", triggerEff, "triggerEff/F")

    for i in range(totalTrain):
        tool.printProcessStatus(iCurrent=i+1, total=totalTest, processName = 'Looping sample [%s]' %iFileName)
        iTrainTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(iTrainTree.sampleName2, 'decode')
        if tmpSampleName not in sampleNames:
            sampleNames.append(tmpSampleName)
            sampleNamesCounterTest_1[tmpSampleName] = 0.0
            sampleNamesCounterTest_2[tmpSampleName] = 0.0
            sampleNamesCounter_triggerEff1[tmpSampleName] = 0.0
            sampleNamesCounter_triggerEff2[tmpSampleName] = 0.0
            sampleNamesCounterTrain_1[tmpSampleName] = 0.0
            sampleNamesCounterTrain_2[tmpSampleName] = 0.0
            if iTrainTree.category == 1:
                sampleNamesCounterTrain_1[tmpSampleName] = iTrainTree.triggerEff
            elif iTrainTree.category == 2:
                sampleNamesCounterTrain_2[tmpSampleName] = iTrainTree.triggerEff
            initEvents[tmpSampleName] = iTrainTree.initEvents
            xsValues[tmpSampleName] = iTrainTree.xs
        else:
            if iTrainTree.category == 1:
                sampleNamesCounterTrain_1[tmpSampleName] += iTrainTree.triggerEff
            elif iTrainTree.category == 2:
                sampleNamesCounterTrain_2[tmpSampleName] += iTrainTree.triggerEff
        sampleName[:31] = tmpSampleName
        if tmpSampleName == 'tt':
            sampleName[:31] = 'tt_full'
        if tmpSampleName == 'data':
            sampleName[:31] = 'dataOSRelax'
        if iTrainTree.category == 1:
            category2[:31] = '1M'
        elif iTrainTree.category == 2:
            category2[:31] = '2M'
        else:
            category2[:31] = 'None'
        mJJReg[0] = iTrainTree.mJJReg
        mJJ[0] = iTrainTree.mJJ
        CSVJ2[0] = iTrainTree.CSVJ2
        fMass[0] = iTrainTree.fMass
        fMassKinFit[0] = iTrainTree.fMassKinFit
        chi2KinFit[0] = iTrainTree.chi2KinFit
        chi2KinFit2[0] = iTrainTree.chi2KinFit2
        svMass[0] = iTrainTree.svMass
        triggerEff[0] = iTrainTree.triggerEff
        BDT[0] = iTrainTree.BDT

        if 'train' in sample:
            if iTrainTree.category == 1:
                sampleNamesCounter_triggerEff1[tmpSampleName] += iTrainTree.triggerEff
            elif iTrainTree.category == 2:
                sampleNamesCounter_triggerEff2[tmpSampleName] += iTrainTree.triggerEff
            oTree.Fill()         


    for i in range(totalTest):
        tool.printProcessStatus(iCurrent=i+1, total=totalTest, processName = 'Looping sample [%s]' %iFileName)
        iTestTree.GetEntry(i)
        tmpSampleName = tool.nameEnDecoder(iTestTree.sampleName2, 'decode')
        if tmpSampleName not in sampleNames:
            sampleNames.append(tmpSampleName)
            sampleNamesCounterTest_1[tmpSampleName] = 0.0
            sampleNamesCounterTest_2[tmpSampleName] = 0.0
            sampleNamesCounter_triggerEff1[tmpSampleName] = 0.0
            sampleNamesCounter_triggerEff2[tmpSampleName] = 0.0
            sampleNamesCounterTrain_1[tmpSampleName] = 0.0
            sampleNamesCounterTrain_2[tmpSampleName] = 0.0
            if iTestTree.category == 1:
                sampleNamesCounterTest_1[tmpSampleName] = iTestTree.triggerEff
            elif iTestTree.category == 2:
                sampleNamesCounterTest_2[tmpSampleName] = iTestTree.triggerEff
            initEvents[tmpSampleName] = iTestTree.initEvents
            xsValues[tmpSampleName] = iTestTree.xs

        else:
            if iTestTree.category == 1:
                sampleNamesCounterTest_1[tmpSampleName] += iTestTree.triggerEff
            elif iTestTree.category == 2:
                sampleNamesCounterTest_2[tmpSampleName] += iTestTree.triggerEff

        sampleName[:31] = tmpSampleName
        if tmpSampleName == 'tt':
            sampleName[:31] = 'tt_full'
        if tmpSampleName == 'data':
            sampleName[:31] = 'dataOSRelax'
        if iTestTree.category == 1:
            category2[:31] = '1M'
        elif iTestTree.category == 2:
            category2[:31] = '2M'
        else:
            category2[:31] = 'None'
        mJJReg[0] = iTestTree.mJJReg
        BDT[0] = iTestTree.BDT

        mJJ[0] = iTestTree.mJJ
        CSVJ2[0] = iTestTree.CSVJ2
        fMass[0] = iTestTree.fMass
        fMassKinFit[0] = iTestTree.fMassKinFit
        chi2KinFit[0] = iTestTree.chi2KinFit
        chi2KinFit2[0] = iTestTree.chi2KinFit2
        met[0] = iTestTree.met

        svMass[0] = iTestTree.svMass
        triggerEff[0] = iTestTree.triggerEff
        if 'test' in sample:
            if iTestTree.category == 1:
                sampleNamesCounter_triggerEff1[tmpSampleName] += iTestTree.triggerEff
            elif iTestTree.category == 2:
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
        if (sampleNamesCounterTest_1[iSample]+sampleNamesCounterTrain_1[iSample]) != 0:
            fracs1[iSample] = (sampleNamesCounterTest_1[iSample])/(sampleNamesCounterTest_1[iSample]+sampleNamesCounterTrain_1[iSample])
        else:
            fracs1[iSample] = 0
        if (sampleNamesCounterTest_2[iSample]+sampleNamesCounterTrain_2[iSample]) != 0:
           fracs2[iSample] = (sampleNamesCounterTest_2[iSample])/(sampleNamesCounterTest_2[iSample]+sampleNamesCounterTrain_2[iSample])
        else:
            fracs2[iSample] = 0
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
                dataScale0 = 1/fracs0[iSample]
            if fracs1[iSample] != 0:
                dataScale1 = 1/fracs1[iSample]
            if fracs2[iSample] != 0:
                dataScale2 = 1/fracs2[iSample]

        if 'data' in iSample:
            xs.Fill(iSample, weight0)

        xs.Fill(iSample, xsValues[iSample])
        extraSpace = ''
        if len(iSample) < 8:
            extraSpace = '\t'

        

        if 'tt' in iSample:
            if 'tt' in validDict1.keys():
                validDict0['tt'] += (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
                validDict1['tt'] += sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
                validDict2['tt'] += sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000

            else:
                validDict0['tt'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
                validDict1['tt'] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
                validDict2['tt'] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000

        elif 'DY' in iSample:
            if 'DY' in validDict1.keys():
                validDict0['DY'] += (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
                validDict1['DY'] += sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
                validDict2['DY'] += sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000

            else:
                validDict0['DY'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
                validDict1['DY'] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
                validDict2['DY'] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000

        elif 'Z' in iSample:
            if 'Z' in validDict1.keys():
                validDict0['Z'] += (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
                validDict1['Z'] += sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
                validDict2['Z'] += sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000

            else:
                validDict0['Z'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
                validDict1['Z'] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
                validDict2['Z'] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000

        elif 'LNu' in iSample:
            if 'W' in validDict1.keys():
                validDict0['W'] += (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
                validDict1['W'] += sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
                validDict2['W'] += sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000

            else:
                validDict0['W'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
                validDict1['W'] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
                validDict2['W'] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000
        elif 'data' in iSample:
            validDict0['QCD'] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])*weight0*dataScale0
            validDict1['QCD'] = sampleNamesCounter_triggerEff1[iSample]*weight1*dataScale1
            validDict2['QCD'] = sampleNamesCounter_triggerEff2[iSample]*weight2*dataScale2
            
        else:
            validDict0[iSample] = (sampleNamesCounter_triggerEff1[iSample]+sampleNamesCounter_triggerEff2[iSample])/tmpInitEvents0*lumi*xsValues[iSample]*1000
            validDict1[iSample] = sampleNamesCounter_triggerEff1[iSample]/tmpInitEvents1*lumi*xsValues[iSample]*1000
            validDict2[iSample] = sampleNamesCounter_triggerEff2[iSample]/tmpInitEvents2*lumi*xsValues[iSample]*1000
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

weights = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigs, makeWholeSample_cfg.preFixTools, 'veto012')

massPoints = ['260', '300', '350']
postFix = '_8_n150_1M'
region = 'test'

for iMass in massPoints:
    makeWhole('H%s%s_%s' %(iMass,postFix,region), '/scratch/zmao/TMVA/new3/TMVA%s%s.root' %(iMass,postFix), weights[0], weights[1], weights[2], region)
