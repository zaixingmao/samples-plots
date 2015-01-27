#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array
import makeWholeSample_cfg
import makeWholeTools2
lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
import embedDYYieldCalculator
import cProfile

dR_tauEleMu_max = 0.5
dR_b_max = 0.5
lumi = 19.7
tt_semi_InitEvents = 12011428.

def findDR(genPt, genEta, genPhi, pt, eta, phi, genPtThreshold):
    tmpGen = lvClass()
    tmpParticle = lvClass()
    tmpParticle.SetCoordinates(pt, eta, phi, 0)
    dR = 999999.0
    for i in range(len(genPt)):
        if genPt.at(i) < genPtThreshold:
            continue
        tmpGen.SetCoordinates(genPt.at(i), genEta.at(i), genPhi.at(i), 0)
        tmpDR = r.Math.VectorUtil.DeltaR(tmpParticle, tmpGen)
        if tmpDR < dR:
            dR = tmpDR
    return dR

def findRightPair(tree, option):
    if option == 'iso':
        isoMin = 999.9
        bestPair = 0
        for iPair in range(len(tree.pt1)):
            if (tree.iso1.at(iPair) + tree.iso2.at(iPair)) < isoMin:
                isoMin = tree.iso1.at(iPair) + tree.iso2.at(iPair)
                bestPair = iPair
        return iPair
    else:
        return 0

def findGenMatch(dR1_tau, dR2_tau, dR1_ele, dR2_ele, dR1_mu, dR2_mu, option = ''):
    #for leg1
    leg1 = sorted([('t',dR1_tau), ('e',dR1_ele), ('m',dR1_mu)], key=itemgetter(1))    
    #for leg2
    leg2 = sorted([('t',dR2_tau), ('e',dR2_ele), ('m',dR2_mu)], key=itemgetter(1))

    if (leg1[0][0] == 't') and (leg1[1][1] > dR_tauEleMu_max):
        leg1Match = leg1[0][0]
    if (leg2[0][0] == 't') and (leg2[1][1] > dR_tauEleMu_max):
        leg2Match = leg2[0][0]

    

    if leg1[0][1] > dR_tauEleMu_max:
        leg1Match = 'x'
    if leg2[0][1] > dR_tauEleMu_max:
        leg2Match = 'x'

    

#     if 'e(tau)' in option:
#         if leg1Match == 'e' and leg1[1][0] == 't' and leg1[1][1] < dR_tauEleMu_max:
#             leg1Match = 'e(t)'
#         if leg2Match == 'e' and leg2[1][0] == 't' and leg2[1][1] < dR_tauEleMu_max:
#             leg2Match = 'e(t)'
    
#     if 'e(b)' in option:
#         if leg1Match == 'e' and leg1[1][0] == 'b' and leg1[1][1] < dR_b_max:
#             leg1Match = 'e(b)'
#         if leg2Match == 'e' and leg2[1][0] == 'b' and leg2[1][1] < dR_b_max:
#             leg2Match = 'e(b)'
#         if 'e(tau)' in option:
#             if leg1Match == 'e' and leg1[1][0] == 't' and leg1[1][1] < dR_tauEleMu_max:
#                 leg1Match = 'e(t)'
#             if leg2Match == 'e' and leg2[1][0] == 't' and leg2[1][1] < dR_tauEleMu_max:
#                 leg2Match = 'e(t)'
#     
#     if 'tau(b)' in option:
#         if leg1Match == 'tau':
#             if leg1[1][0] == 'b' and leg1[1][1] < dR_b_max:
#                 leg1Match = 't(b)'
#         if leg2Match == 'tau':
#             if leg2[1][0] == 'b' and leg2[1][1] < dR_b_max:
#                 leg2Match = 't(b)'

    stringList = [leg1Match, leg2Match]
    stringList.sort()
    return '%s%s' %(stringList[0], stringList[1])

def passMassWindow(svMass, mJJ, fMassKinFit):
    if 90.0 < svMass < 150.0:
        if 70.0 < mJJ < 150.0:
            if fMassKinFit > 10.0:
                return 1
    return 0

def passCut(option, signSelection, isoSelection, looseTag, mediumTag):
    if 'L' in option and looseTag != '0L':
        check = signSelection+isoSelection+'L'
        if option == check:
            return True, looseTag[0:1]+'M'
        else:
            return False, looseTag[0:1]+'M'
    if 'M' in option and mediumTag != '0M':
        check = signSelection+isoSelection+'M'
        if option == check:
            return True, mediumTag
        else:
            return False, mediumTag
    return False, mediumTag

def findMatch(iTree, isData, rightPair):
    if isData:
        return 'ff'

    matchTuple1 = [iTree.pt1.at(rightPair), iTree.eta1.at(rightPair), iTree.phi1.at(rightPair)]
    matchTuple2 = [iTree.pt2.at(rightPair), iTree.eta2.at(rightPair), iTree.phi2.at(rightPair)]

    dR1_tau = findDR(iTree.genTauPt,iTree.genTauEta,iTree.genTauPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2], 18.0)
    dR2_tau = findDR(iTree.genTauPt,iTree.genTauEta,iTree.genTauPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2], 18.0)
#     dR1_b = findDR(iTree.genBPt,iTree.genBEta,iTree.genBPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2], 18.0)
#     dR2_b = findDR(iTree.genBPt,iTree.genBEta,iTree.genBPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2], 18.0)
    dR1_ele = findDR(iTree.genElePt,iTree.genEleEta,iTree.genElePhi,matchTuple1[0],matchTuple1[1],matchTuple1[2], 8.0)
    dR2_ele = findDR(iTree.genElePt,iTree.genEleEta,iTree.genElePhi,matchTuple2[0],matchTuple2[1],matchTuple2[2], 8.0)
    dR1_mu = findDR(iTree.genMuPt,iTree.genMuEta,iTree.genMuPhi,matchTuple1[0],matchTuple1[1],matchTuple1[2], 8.0)
    dR2_mu = findDR(iTree.genMuPt,iTree.genMuEta,iTree.genMuPhi,matchTuple2[0],matchTuple2[1],matchTuple2[2], 8.0)
    genMatch = findGenMatch(dR1_tau, dR2_tau, dR1_ele, dR2_ele, dR1_mu, dR2_mu)
#     genMatch = findGenMatch(dR1_tau, dR2_tau, dR1_b, dR2_b, dR1_ele, dR2_ele, dR1_mu, dR2_mu)

    return genMatch

def getRightBTagCatName(bTagSelection):
    if bTagSelection == None:
        return '0L', '0M'
    return bTagSelection[0:2], bTagSelection[2:4]

def run():
    fileList = []
    for i in range(len(makeWholeSample_cfg.sampleConfigs)):
        #configs name, location, selection, useMediumForYield
        fileList.append((makeWholeSample_cfg.sampleConfigs[i][0], 
                        makeWholeSample_cfg.sampleConfigs[i][1], 
                        makeWholeSample_cfg.sampleConfigs[i][2],
                        makeWholeSample_cfg.sampleConfigs[i][3]))

    oFileName = makeWholeSample_cfg.oFileName
    oFile = r.TFile(oFileName, 'RECREATE')
    oTree = r.TTree('eventTree', '')
    iso = makeWholeSample_cfg.iso
    nSamples = len(fileList)

    mJJ = array('f', [0.])
    svMass = array('f', [0.])
    fMass = array('f', [0.])
    fMassKinFit = array('f', [0.])
    chi2KinFit = array('f', [0.])
    chi2KinFit2 = array('f', [0.])
    PUWeight = array('f', [0.])
    iso1 = array('f', [0.])
    iso2 = array('f', [0.])
    pt1 = array('f', [0.])
    pt2 = array('f', [0.])
    CSVJ1Pt = array('f', [0.])
    CSVJ2Pt = array('f', [0.])
    CSVJ2 = array('f', [0.])
    NBTags = array('i', [0])
    triggerEff = array('f', [0.])
    sampleName = bytearray(20)
    genMatchName = bytearray(3)
    xs = array('f', [0.])
    initEvents = array('f', [0.])
    Category = bytearray(5)

    xsValues = {}
    initEventsValues = {}
    eventsSaved = {}


    yieldForMediumCat = {}
    inclusiveYields = {}

    inclusiveYields = {}
    catYields = {}
    svMassRange = [20, 0, 400]
    L2T_value = 0


    oTree.Branch("mJJ", mJJ, "mJJ/F")
    oTree.Branch("fMass", fMass, "fMass/F")
    oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
    oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
    oTree.Branch("chi2KinFit2", chi2KinFit2, "chi2KinFit2/F")
    oTree.Branch("xs", xs, "xs/F")
    oTree.Branch("initEvents", initEvents, "initEvents/F")
    oTree.Branch("NBTags", NBTags, "NBTags/I")
    oTree.Branch("Category", Category, "Category[21]/C")

    oTree.Branch("svMass", svMass, "svMass/F")
    oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")
    oTree.Branch("iso1", iso1, "iso1/F")
    oTree.Branch("iso2", iso2, "iso2/F")
    oTree.Branch("pt1", pt1, "pt1/F")
    oTree.Branch("pt2", pt2, "pt2/F")
    oTree.Branch("CSVJ1Pt", CSVJ1Pt, "CSVJ1Pt/F")
    oTree.Branch("CSVJ2Pt", CSVJ2Pt, "CSVJ2Pt/F")

    oTree.Branch("triggerEff", triggerEff, "triggerEff/F")
    oTree.Branch("PUWeight", PUWeight, "PUWeight/F")

    oTree.Branch("sampleName", sampleName, "sampleName[21]/C")
    oTree.Branch("genMatchName", genMatchName, "genMatchName[21]/C")

    for indexFile in range(nSamples):
        eventsSavedCounter_1M = 0.0
        eventsSavedCounter_2M = 0.0

        name = fileList[indexFile][0]
        option = fileList[indexFile][2]
        iFile =  r.TFile(fileList[indexFile][1])
        iTree = iFile.Get('eventTree')
        useMediumCat4Yield = fileList[indexFile][3]
        if useMediumCat4Yield:
            yieldForMediumCat[name+'_1M'] = 0.0
            yieldForMediumCat[name+'_2M'] = 0.0

        total = iTree.GetEntries()
        isData = False
        if ('data' in name) or ('DY_embed' in name):
            isData = True
        if 'emb' in name:
            isEmbed = True
            inclusiveYields[name] = 0.0
        else:
            isEmbed = False
        if 'inclusive' in name:
            isInclusive = True
            inclusiveYields[name] = 0.0
        else:
            isInclusive = False
        cat = ''
        region = 'bTag'
        if '1M' in option:
            region = '1M'
        elif '2M' in option:
            region = '2M'
        elif '1L' in option:
            region = '1L'
            cat = '1M'
        elif '2L' in option:
            region = '2L'
            cat = '2M'

        for i in range(0, total):
            tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %name, iPrevious=i)
            #Fill Histograms
            iTree.GetEntry(i)

            #get the right pair of taus based on isoMin or ptMax
            rightPair = findRightPair(iTree, makeWholeSample_cfg.pairOption)

            if makeWholeSample_cfg.thirdLeptonVeto and (iTree.nElectrons > 0 or iTree.nMuons > 0):
                continue
            if iTree.HLT_Any == 0:
                continue

            #get event category
            signSelection, isoSelection, bTagSelection = makeWholeTools2.findCategory(tree = iTree, 
                                                                                      iso = makeWholeSample_cfg.iso, 
                                                                                      option = makeWholeSample_cfg.pairOption,
                                                                                      isData = isData,
                                                                                      relaxedRegionOption = makeWholeSample_cfg.Relax,
                                                                                      isEmbed = isEmbed,
                                                                                      usePassJetTrigger = makeWholeSample_cfg.usePassJetTrigger,
                                                                                      nBtag = makeWholeSample_cfg.bTagShift)

            if signSelection == None or isoSelection == None:
                continue
            looseTag, mediumTag = getRightBTagCatName(bTagSelection)

            if isEmbed and iTree.ZTT == 0:
                continue
            if name == 'ZLL' and iTree.ZLL == 0:
                continue
            if name == 'ZTT' and iTree.ZTT == 0:
                continue
            #calculate category yield
            if useMediumCat4Yield:
                if (not makeWholeSample_cfg.massWindow) or (makeWholeSample_cfg.massWindow and passMassWindow(iTree.svMass.at(rightPair),iTree.mJJ, iTree.fMassKinFit)):
                    if (signSelection == "OS") and (isoSelection == "Tight") and (mediumTag != '0M'):
                        if isEmbed:
                            if 'data' in iTree.sampleName:
                                yieldForMediumCat["%s_%s" %(name, mediumTag)] += iTree.triggerEff
                            else:
                                yieldForMediumCat["%s_%s" %(name, mediumTag)] += iTree.triggerEff*iTree.xs*0.983*lumi/tt_semi_InitEvents
                        else:
                            yieldForMediumCat["%s_%s" %(name, mediumTag)] += iTree.triggerEff*iTree.xs*lumi*iTree.PUWeight/iTree.initEvents
        

            passSelection, bRegion = passCut(option, signSelection, isoSelection, looseTag, mediumTag)

            if option[:len(option)-1] != signSelection+isoSelection:
                continue
            mJJ[0] = iTree.mJJ
            fMass[0] = iTree.fMass
            fMassKinFit[0] = iTree.fMassKinFit
            chi2KinFit[0] = iTree.chi2KinFit
            chi2KinFit2[0] = iTree.chi2KinFit2
            svMass[0] = iTree.svMass.at(rightPair)
            iso1[0] = iTree.iso1.at(rightPair)
            iso2[0] = iTree.iso2.at(rightPair)
            CSVJ2[0] = iTree.CSVJ2
            NBTags[0] = int(iTree.NBTags)
            triggerEff[0] = iTree.triggerEff
            pt1[0] = iTree.pt1.at(rightPair)
            pt2[0] = iTree.pt2.at(rightPair)
            CSVJ1Pt[0] = iTree.CSVJ1Pt
            CSVJ2Pt[0] = iTree.CSVJ2Pt

            if '_semi' not in iTree.sampleName:
                tmpSampleName = iTree.sampleName[0:iTree.sampleName.find('_')]
            else:
                tmpSampleName = iTree.sampleName[0:iTree.sampleName.find('_semi')+5]
            if 'data' in tmpSampleName and (not isEmbed):
                sampleName[:21] = name
                initEvents[0] = 1.0
                xs[0] = 1.0           
            elif ('data' in tmpSampleName) and isEmbed:
                sampleName[:21] = 'DY_embed'
                initEvents[0] = 19.7
                xs[0] = 1.0            
            elif not isEmbed:
                initEvents[0] = iTree.initEvents
                xs[0] = iTree.xs
                sampleName[:21] = tmpSampleName
                if name == 'MCOSRelax':
                    sampleName[:21] = 'MCOSRelax'
                elif name == 'ZLL':
                    sampleName[:21] = 'ZLL'
                elif name == 'ZTT':
                    sampleName[:21] = 'ZTT'
            else:
                initEvents[0] = tt_semi_InitEvents
                xs[0] = iTree.xs*0.983
                sampleName[:21] = 'tt_embed'
            
            if str(sampleName) not in initEventsValues.keys():
                if 'data' not in str(sampleName):
                    initEventsValues[str(sampleName)] = iTree.initEvents
                    xsValues[str(sampleName)] = iTree.xs
                eventsSaved[str(sampleName)] = 0.0
    #         genMatchName[:3] = findMatch(iTree, isData, rightPair)
            if isData:
                PUWeight[0] = 1.0
            else:
                PUWeight[0] = iTree.PUWeight

            if mediumTag == '0M':
                Category[:21] = '0M'
                oTree.Fill()
            if passSelection:
                Category[:21] = bRegion
                oTree.Fill()
            else:
                continue

            if makeWholeSample_cfg.massWindow and (not passMassWindow(iTree.svMass.at(rightPair), iTree.mJJ, iTree.fMassKinFit)):
                continue
            if isData:
                eventsSaved[str(sampleName)] += 1
                if bRegion == '1M':
                    eventsSavedCounter_1M += 1
                elif bRegion == '2M':
                    eventsSavedCounter_2M += 1
            elif not isEmbed:
                eventsSaved[str(sampleName)] += triggerEff[0]
                if bRegion == '1M':
                    eventsSavedCounter_1M += triggerEff[0]*xsValues[str(sampleName)]/initEventsValues[str(sampleName)]*PUWeight[0]*lumi
                elif bRegion == '2M':
                    eventsSavedCounter_2M += triggerEff[0]*xsValues[str(sampleName)]/initEventsValues[str(sampleName)]*PUWeight[0]*lumi

        print ' --- Events Saved: (1M) %.2f    (2M) %.2f' %(eventsSavedCounter_1M, eventsSavedCounter_2M)
        if isEmbed:
            print name
            print 'inclusive yield for %s: %.2f' %(name, inclusiveYields[name])
            print '1-Medium category yield for %s: %.2f' %(name, yieldForMediumCat[name+'_1M'])
            print '2-Medium category yield for %s: %.2f' %(name, yieldForMediumCat[name+'_2M'])

        elif isInclusive:
            print 'inclusive yield for %s: %.2f' %(name, inclusiveYields[name])



    nSamples = len(initEventsValues.keys())
    initEvents = r.TH1F('initEvents', '', nSamples, 0, nSamples)
    xsHist = r.TH1F('xs', '', nSamples, 0, nSamples)

    for iKey in initEventsValues.keys():
        if 'data' not in iKey:
            initEvents.Fill(iKey, initEventsValues[iKey])
            xsHist.Fill(iKey, xsValues[iKey])

    weights = makeWholeTools2.calculateSF(fileList = makeWholeSample_cfg.sampleConfigsTools,
                                          sigRegionOption = 'Tight', 
                                          relaxedRegionOption = makeWholeSample_cfg.Relax, 
                                          verbose = True,
                                          isoTight = 1.0, 
                                          pairOption = makeWholeSample_cfg.pairOption,
                                          massWindow = makeWholeSample_cfg.massWindow,
                                          usePassJetTrigger = makeWholeSample_cfg.usePassJetTrigger,
                                          nBtag = '')

    scaleFactor_1M, scaleFactor_2M, scaleFactor_1M2, scaleFactor_2M2, preScaleFactor = embedDYYieldCalculator.yieldCalculator(dy_mc = '%s/dy.root' %makeWholeSample_cfg.preFixTauESOn, 
                                                                            tt_full_mc = '%s/tt_all.root' %makeWholeSample_cfg.preFixTauESOff,
                                                                            dy_embed = '%s/DY_embed.root' %makeWholeSample_cfg.preFixTauESOnDYEmbed, 
                                                                            tt_embed = '%s/tt_embed_all.root' %makeWholeSample_cfg.preFixTauESOff, 
                                                                            massWindow = makeWholeSample_cfg.massWindow,
                                                                            pairOption = makeWholeSample_cfg.pairOption)


    print weights

    #define histograms
    L_to_T_SF_0M = r.TH1F('L_to_T_SF_0M', '', 1, 0, 1)
    MC2Embed2Cat_0M = r.TH1F('MC2Embed2Cat_0M', '', 1, 0, 1)

    L_to_T_1M = r.TH1F('L_to_T_1M', '', 1, 0, 1)
    L_to_T_SF_1M = r.TH1F('L_to_T_SF_1M', '', 1, 0, 1)
    MC2Embed2Cat_1M = r.TH1F('MC2Embed2Cat_1M', '', 1, 0, 1)
    EmbedWithTTLep_1M = r.TH1F('EmbedWithTTLep_1M', '', 1, 0, 1)
    DYwithTTScale_1M = r.TH1F('DYwithTTScale_1M', '', 1, 0, 1)

    L_to_T_2M = r.TH1F('L_to_T_2M', '', 1, 0, 1)
    L_to_T_SF_2M = r.TH1F('L_to_T_SF_2M', '', 1, 0, 1)
    MC2Embed2Cat_2M = r.TH1F('MC2Embed2Cat_2M', '', 1, 0, 1)
    EmbedWithTTLep_2M = r.TH1F('EmbedWithTTLep_2M', '', 1, 0, 1)
    DYwithTTScale_2M = r.TH1F('DYwithTTScale_2M', '', 1, 0, 1)

    yieldForMediumCatHists = {}


    #save histograms
    L_to_T_1M.Fill(0.5, weights[0])
    L_to_T_2M.Fill(0.5, weights[1])
    L_to_T_SF_1M.Fill(0.5, weights[2])
    L_to_T_SF_2M.Fill(0.5, weights[3])
    L_to_T_SF_0M.Fill(0.5, weights[4])

    # preScaleFactor = inclusiveYields['DY_inclusive']/(inclusiveYields['DY_embed'] - inclusiveYields['tt_embed'])
    # scaleFactor_1M = preScaleFactor*(yieldForMediumCat['DY_embed_1M']-yieldForMediumCat['tt_embed_1M'])
    # scaleFactor_2M = preScaleFactor*(yieldForMediumCat['DY_embed_2M']-yieldForMediumCat['tt_embed_2M'])
    MC2Embed2Cat_0M.Fill(0.5, preScaleFactor)
    MC2Embed2Cat_1M.Fill(0.5, scaleFactor_1M)
    MC2Embed2Cat_2M.Fill(0.5, scaleFactor_2M)
    DYwithTTScale_1M.Fill(0.5, scaleFactor_1M2)
    DYwithTTScale_2M.Fill(0.5, scaleFactor_2M2)

    print 'Embed DY prediction (1M): %.2f' %scaleFactor_1M
    print 'Embed DY prediction (2M): %.2f' %scaleFactor_2M

    oFile.cd()

    initEvents.Write()
    xsHist.Write()
    L_to_T_1M.Write()
    L_to_T_SF_1M.Write()
    L_to_T_2M.Write()
    L_to_T_SF_2M.Write()
    L_to_T_SF_0M.Write()
    MC2Embed2Cat_0M.Write()
    MC2Embed2Cat_1M.Write()
    MC2Embed2Cat_2M.Write()
    DYwithTTScale_1M.Write()
    DYwithTTScale_2M.Write()

    for iKey in yieldForMediumCat.keys():
        yieldForMediumCatHists[iKey] = r.TH1F(iKey, '', 1, 0, 1)
        yieldForMediumCatHists[iKey].Fill(0.5, yieldForMediumCat[iKey])
        print '%s prediction: %.2f' %(iKey, yieldForMediumCat[iKey])
        yieldForMediumCatHists[iKey].Write()
    oTree.Write()
    oFile.Close()

    print 'Combined event saved at: %s' %oFileName


if __name__ == "__main__":
    if makeWholeSample_cfg.checkSpeed:
        cProfile.run("run()", sort="time")
    else:
        run()
