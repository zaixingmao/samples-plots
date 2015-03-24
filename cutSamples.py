#!/usr/bin/env python

import ROOT as r
import tool
import os
import cProfile
from cfg import enVars
from array import array
import optparse
import kinfit
from cutSampleTools import *
import trigger
import data_certification
from makeWholeTools2 import findRightPair

r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000
r.gStyle.SetOptStat("e")

xLabels = ['processedEvents', 'initialEventsTT', 'extraEleVeto','extraMuVeto', 'AtLeastOneDiTau', 'ttPtEta1',
           'ttPtEta2','tau1Hadronic','tau2Hadronic','ttMuonVeto1', 'ttMuonVeto2', 'ttElectronVeto1', 'ttElectronVeto2', 
           'ttIsolation1', 'ttRelaxed2', 'myCut']

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
J1 = lvClass()
J2 = lvClass()
J3 = lvClass()
J4 = lvClass()
J5 = lvClass()
J6 = lvClass()

matchedGenJet = lvClass()
mGenJet1 = lvClass()
mGenJet2 = lvClass()
CSVJet1 = lvClass()
CSVJet2 = lvClass()
tau1 = lvClass()
tau2 = lvClass()
combinedJJ = lvClass()
sv4Vec = lvClass()

kinfit.setup()


def setUpFloatVarsDict():
    varDict = {}
    names = ['mJJ', 'ptJJ', 'etaJJ', 'phiJJ', 'CSVJ1','CSVJ1Pt','CSVJ1Eta','CSVJ1Phi', 'CSVJ1Mass',
             'CSVJ2', 'CSVJ2Pt', 'CSVJ2Eta', 'CSVJ2Phi', 'CSVJ2Mass', 'dRTauTau', 'dRJJ', 'dRhh', 'mTop1', 'mTop2',
             'pZ_new', 'pZV_new', 'pZ_new2', 'pZV_new2', 'triggerEff', 'triggerEff1', 'triggerEff2', 'metTau1DPhi', 'metTau2DPhi',
             'metJ1DPhi', 'metJ2DPhi', 'metTauPairDPhi', 'metJetPairDPhi', 'metSvTauPairDPhi', 'dRGenJet1Match', 'dRGenJet2Match',
             'matchGenJet1Pt', 'matchGenJet1Eta', 'matchGenJet1Phi', 'matchGenJet1Mass', 'matchGenJet2Pt', 'matchGenJet2Eta', 'matchGenJet2Phi', 'matchGenJet2Mass', 
             'matchGenMJJ', 'matchGenPtJJ', 'matchGendRJJ', 'CSVJ1PtUncorr', 'CSVJ1Et', 'CSVJ1Mt', 'CSVJ1ptLeadTrk', 'CSVJ1Vtx3dL', 
             'CSVJ1Vtx3deL', 'CSVJ1VtxPt', 'CSVJ1vtxMass', 'CSVJ1JECUnc', 'CSVJ1Ntot', 'CSVJ1SoftLeptPtRel', 'CSVJ1SoftLeptPt', 'CSVJ1SoftLeptdR', 
             'CSVJ2PtUncorr', 'CSVJ2Et', 'CSVJ2Mt', 'CSVJ2ptLeadTrk', 'CSVJ2Vtx3dL', 'CSVJ2Vtx3deL', 'CSVJ2VtxPt', 'CSVJ2JECUnc', 
             'CSVJ2Ntot', 'CSVJ2SoftLeptPtRel', 'CSVJ2SoftLeptPt', 'CSVJ2SoftLeptdR', 'chi2KinFit', 'chi2KinFit2', 'fMassKinFit', 'PUWeight', 
             'xs', 'decayModeWeight1', 'decayModeWeight2', 'decayModeWeight', 'fMass'
            ]
    for iName in names:
        varDict[iName] = array('f', [0.])
    return varDict

def setUpIntVarsDict():
    varDict = {}
    names = ['nElectrons', 'nMuons', 'initEvents', 'ZTT', 'ZLL']
    for iName in names:
        varDict[iName] = array('i', [0])
    return varDict

def setUpCharVarsDict():
    varDict = {}
    names = ['sampleName', 'category']
    for iName in names:
        varDict[iName] = bytearray(30)
    return varDict

def opts():
    parser = optparse.OptionParser()
    parser.add_option("-l", dest="location", default="/scratch/%s" % os.environ["USER"], help="location to be saved")
    parser.add_option("-n", dest="nevents", default="-1", help="amount of events to be saved")
    parser.add_option("-g", dest="genMatch", default="jet", help="gen particle for the reco-jet to match to")
    parser.add_option("-a", dest="addFiles", default="False", help="")
    parser.add_option("-t", dest="folderName", default="ttTreeBeforeChargeCut", help="")
    parser.add_option("-c", dest="cutLHEProduct", default=False, action="store_true", help="cut to 0 jet")
    parser.add_option("--pair", dest="pairChoice", default="pt", help="which pair")

    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    options, args = parser.parse_args()

    return options

options = opts()

r.gStyle.SetOptStat(0)

def loop_one_sample(iSample, iLocation, iXS):
    if 'data' in iSample:
        isData = True
#         varList = preVarList
    else:
        isData = False
#         varList = fullVarList
    if 'emb' in iSample:
        isEmbedded = True
    else:
        isEmbedded = False
    if 'H2hh' in iSample:
        isSignal = True
    else:
        isSignal = False
        
    cutFlow = r.TH1F('cutFlow', '', len(xLabels), 0, len(xLabels))
    if options.addFiles == 'True':
        tool.addHistFromFiles(dirName=iLocation, histName = "preselection", hist = cutFlow, xAxisLabels=xLabels)
    else:
        tool.addHistFromFiles(dirName=iLocation, histName = "TT/results", hist = cutFlow, xAxisLabels=xLabels)
    cutFlow.SetName('preselection')

    if options.addFiles == 'True':
        iChain = r.TChain("eventTree")
    else:
        folderName = options.folderName
        iChain = r.TChain("%s/eventTree" %folderName)
    nEntries = tool.addFiles(ch=iChain, dirName=iLocation, knownEventNumber=0, printTotalEvents=True, blackList=enVars.corruptedROOTfiles)
    iChain.SetBranchStatus("*",1)
#     iChain.SetBranchStatus("mJJ",0)

    #set up vars dict
    charVarsDict = setUpCharVarsDict()
    floatVarsDict = setUpFloatVarsDict()
    intVarsDict = setUpIntVarsDict()


    iChain.LoadTree(0)
    oTree = iChain.GetTree().CloneTree(0)
    iSample = iSample + '_%s' %('all' if options.nevents == "-1" else options.nevents)
    iFile = r.TFile("%s/%s.root" %(options.location,iSample),"recreate")

    #setup branches
    for iVar in charVarsDict.keys():
        oTree.Branch("%s" %iVar, charVarsDict[iVar], "%s[31]/C" %iVar)
    for iVar in floatVarsDict.keys():
        oTree.Branch("%s" %iVar, floatVarsDict[iVar], "%s/F" %iVar)
    for iVar in intVarsDict.keys():
        oTree.Branch("%s" %iVar, intVarsDict[iVar], "%s/I" %iVar)

    charVarsDict['sampleName'][:31] = iSample
    intVarsDict['initEvents'][0] = int(cutFlow.GetBinContent(1))
    floatVarsDict['xs'][0] = iXS
    counter = 0
    for iEntry in range(nEntries):
        iChain.LoadTree(iEntry)
        iChain.GetEntry(iEntry)

        if options.addFiles == 'True':
            oTree.Fill()
            counter += 1
            tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s/%s.root' % (options.location, iSample), iEntry-1)
            continue
#         if not (iChain.HLT_Any > 0):
#             continue
        if not data_certification.passes(iChain, isData):
            continue
        if options.cutLHEProduct:
            if iChain.LHEProduct != 5:
                continue
        if counter == int(options.nevents):
            break
        if iChain.svMass.size() == 0:
            continue
        rightPair = findRightPair(iChain, options.pairChoice)

        jetsList = [(iChain.J1CSVbtag, J1.SetCoordinates(iChain.J1Pt, iChain.J1Eta, iChain.J1Phi, iChain.J1Mass), 'J1'),
                    (iChain.J2CSVbtag, J2.SetCoordinates(iChain.J2Pt, iChain.J2Eta, iChain.J2Phi, iChain.J2Mass), 'J2'),
                    (iChain.J3CSVbtag, J3.SetCoordinates(iChain.J3Pt, iChain.J3Eta, iChain.J3Phi, iChain.J3Mass), 'J3'),
                    (iChain.J4CSVbtag, J4.SetCoordinates(iChain.J4Pt, iChain.J4Eta, iChain.J4Phi, iChain.J4Mass), 'J4'),
                    (iChain.J5CSVbtag, J5.SetCoordinates(iChain.J5Pt, iChain.J5Eta, iChain.J5Phi, iChain.J5Mass), 'J5'),
                    (iChain.J6CSVbtag, J6.SetCoordinates(iChain.J6Pt, iChain.J6Eta, iChain.J6Phi, iChain.J6Mass), 'J6')]
        sv4Vec.SetCoordinates(iChain.svPt.at(rightPair), iChain.svEta.at(rightPair), iChain.svPhi.at(rightPair), iChain.svMass.at(rightPair))
        bb = lvClass()
        bb, floatVarsDict['CSVJ1'][0], floatVarsDict['CSVJ2'][0], CSVJet1, CSVJet2, floatVarsDict['fMass'][0], floatVarsDict['dRJJ'][0], j1Name, j2Name = findFullMass(iTree = iChain, rightPair = rightPair, jetsList=jetsList, sv4Vec=sv4Vec, ptThreshold = enVars.jetPtThreshold) 

        charVarsDict['category'][:31] = findCategory(floatVarsDict['CSVJ1'][0], floatVarsDict['CSVJ2'][0])

        #Gen Matching
        floatVarsDict['matchGenJet1Pt'][0] = 0
        floatVarsDict['matchGenJet2Pt'][0] = 0
        if (not isData):
            floatVarsDict['PUWeight'][0] = getPUWeight(iChain.puTruth)
#             if options.genMatch == 'jet':
#                 dRGenJet1Match[0], mGenJet1, dRGenJet2Match[0], mGenJet2 = findGenJet(j1Name, CSVJet1, j2Name, CSVJet2, iChain)
#             else:
#                 dRGenJet1Match[0], mGenJet1, dRGenJet2Match[0], mGenJet2 = findGenBJet(CSVJet1, CSVJet2, iChain)                
#            
#             matchGenJet1Pt[0] = mGenJet1.pt()
#             matchGenJet1Eta[0] = mGenJet1.eta()
#             matchGenJet1Phi[0] = mGenJet1.phi()
#             matchGenJet1Mass[0] = mGenJet1.mass()
# 
#             matchGenJet2Pt[0] = mGenJet2.pt()
#             matchGenJet2Eta[0] = mGenJet2.eta()
#             matchGenJet2Phi[0] = mGenJet2.phi()
#             matchGenJet2Mass[0] = mGenJet2.mass()
# 
#             genJJ = mGenJet1 + mGenJet2
#             matchGenMJJ[0] = genJJ.mass()
#             matchGenPtJJ[0] = genJJ.pt()
#             matchGendRJJ[0] = r.Math.VectorUtil.DeltaR(mGenJet1, mGenJet2)
# 
#             if matchGenMJJ[0] < 0:
#                 matchGenMJJ[0] = 0
#                 matchGenPtJJ[0] = 0
        else:
            floatVarsDict['PUWeight'][0] = 1.0
        #Store values
        floatVarsDict['CSVJ1Pt'][0] = CSVJet1.pt()
        floatVarsDict['CSVJ1Eta'][0] = CSVJet1.eta()
        floatVarsDict['CSVJ1Phi'][0] = CSVJet1.phi()
        floatVarsDict['CSVJ1Mass'][0] = CSVJet1.mass()
        floatVarsDict['CSVJ2Pt'][0] = CSVJet2.pt()
        floatVarsDict['CSVJ2Eta'][0] = CSVJet2.eta()
        floatVarsDict['CSVJ2Phi'][0] = CSVJet2.phi()
        floatVarsDict['CSVJ2Mass'][0] = CSVJet2.mass()

#         CSVJ1PtUncorr[0], CSVJ1Et[0], CSVJ1Mt[0], CSVJ1ptLeadTrk[0], CSVJ1Vtx3dL[0], CSVJ1Vtx3deL[0], CSVJ1vtxMass[0], CSVJ1VtxPt[0], CSVJ1JECUnc[0], CSVJ1Ntot[0], CSVJ1SoftLeptPtRel[0], CSVJ1SoftLeptPt[0], CSVJ1SoftLeptdR[0], CSVJ2PtUncorr[0], CSVJ2Et[0], CSVJ2Mt[0], CSVJ2ptLeadTrk[0], CSVJ2Vtx3dL[0], CSVJ2Vtx3deL[0], CSVJ2vtxMass[0], CSVJ2VtxPt[0], CSVJ2JECUnc[0], CSVJ2Ntot[0], CSVJ2SoftLeptPtRel[0], CSVJ2SoftLeptPt[0], CSVJ2SoftLeptdR[0] = getRegVars(j1Name, j2Name, iChain)

        if floatVarsDict['CSVJ1Vtx3dL'][0] == -10:
            floatVarsDict['CSVJ1Vtx3dL'][0] = 0
            floatVarsDict['CSVJ1Vtx3deL'][0] = 0
            floatVarsDict['CSVJ1vtxMass'][0] = 0
            floatVarsDict['CSVJ1VtxPt'][0] = 0
        if floatVarsDict['CSVJ1ptLeadTrk'][0] < 0:
            floatVarsDict['CSVJ1ptLeadTrk'][0] = 0

        if floatVarsDict['CSVJ2Vtx3dL'][0] == -10:
            floatVarsDict['CSVJ2Vtx3dL'][0] = 0
            floatVarsDict['CSVJ2Vtx3deL'][0] = 0
            floatVarsDict['CSVJ2vtxMass'][0] = 0
            floatVarsDict['CSVJ2VtxPt'][0] = 0
        if floatVarsDict['CSVJ2ptLeadTrk'][0] < 0:
            floatVarsDict['CSVJ2ptLeadTrk'][0] = 0

        if floatVarsDict['CSVJ1SoftLeptPtRel'][0] == -10:
            floatVarsDict['CSVJ1SoftLeptPtRel'][0] == 0
            floatVarsDict['CSVJ1SoftLeptPt'][0] == 0
        if floatVarsDict['CSVJ2SoftLeptPtRel'][0] == -10:
            floatVarsDict['CSVJ2SoftLeptPtRel'][0] == 0
            floatVarsDict['CSVJ2SoftLeptPt'][0] == 0

        floatVarsDict['ptJJ'][0] = bb.pt()
        floatVarsDict['etaJJ'][0] = bb.eta()
        floatVarsDict['phiJJ'][0] = bb.phi()
        floatVarsDict['mJJ'][0] = bb.mass()

        #separate sample into ZLL and ZTT category:
        intVarsDict['ZTT'][0] = 0
        intVarsDict['ZLL'][0] = 0
        if isEmbedded or ('DY' in iSample) or ('dy' in iSample):
            if passCategory(iChain, 'ZTT', options.pairChoice):
                intVarsDict['ZTT'][0] = 1
            if passCategory(iChain, 'ZLL', options.pairChoice):
                intVarsDict['ZLL'][0] = 1

        tau1.SetCoordinates(iChain.pt1.at(rightPair), iChain.eta1.at(rightPair), iChain.phi1.at(rightPair), iChain.m1.at(rightPair))
        tau2.SetCoordinates(iChain.pt2.at(rightPair), iChain.eta2.at(rightPair), iChain.phi2.at(rightPair), iChain.m2.at(rightPair))
#         mTop1[0] = (CSVJet1 + tau1).mass()
#         mTop2[0] = (CSVJet2 + tau2).mass()

        intVarsDict['nElectrons'][0] = iChain.nElectrons
        intVarsDict['nMuons'][0] = iChain.nMuons
#         pZ_new[0] = iChain.pZ/iChain.svPt.at(0)
#         pZV_new[0] = iChain.pZV/iChain.svPt.at(0)
#         pZ_new2[0] = iChain.pZ/fullMass[0]
#         pZV_new2[0] = iChain.pZV/fullMass[0]

        floatVarsDict['dRTauTau'][0] = r.Math.VectorUtil.DeltaR(tau1, tau2)
#         dRhh[0] = r.Math.VectorUtil.DeltaR(bb, sv4Vec)

        #Trigger Calc MetDPhiValues
#         metTau1DPhi[0], metTau2DPhi[0], metJ1DPhi[0], metJ2DPhi[0], metTauPairDPhi[0], metJetPairDPhi[0], metSvTauPairDPhi[0] = calcdPhiMetValues(iChain.phi1.at(0), iChain.phi2.at(0), CSVJet1.phi(), CSVJet2.phi(), iChain.metphi.at(0), (tau1+tau2).phi(), bb.phi(), iChain.svPhi.at(0))

        #Trigger Eff
        if isEmbedded:
            eff1 = trigger.dataEff_leg1(iChain, rightPair)
            eff2 = trigger.dataEff_leg2(iChain, rightPair)
        else:
            eff1 = trigger.correction_leg1(iChain, rightPair)
            eff2 = trigger.correction_leg2(iChain, rightPair)

        floatVarsDict['triggerEff1'][0] = eff1
        floatVarsDict['triggerEff2'][0] = eff2        
        floatVarsDict['triggerEff'][0] = eff1*eff2
        if isData and not isEmbedded:
            floatVarsDict['triggerEff'][0] = 1
            floatVarsDict['triggerEff1'][0] = 1
            floatVarsDict['triggerEff2'][0] = 1

        #Kinematic Fit
        if not floatVarsDict['CSVJ1'][0] == -1.0:
            floatVarsDict['chi2KinFit'][0], floatVarsDict['fMassKinFit'][0], status = kinfit.fit(iChain, CSVJet1, CSVJet2, rightPair)
            floatVarsDict['chi2KinFit2'][0] = floatVarsDict['chi2KinFit'][0]
            if floatVarsDict['chi2KinFit2'][0] > 200:
                floatVarsDict['chi2KinFit2'][0] = 200

        #decayModeWeight
        if (isData and isEmbedded) or (isSignal) or ('DY' in iSample):
            floatVarsDict['decayModeWeight1'][0], floatVarsDict['decayModeWeight2'][0] = getDecayModeWeight(iChain, rightPair)
        else:
            floatVarsDict['decayModeWeight1'][0] = 1.0
            floatVarsDict['decayModeWeight2'][0] = 1.0
        floatVarsDict['decayModeWeight'][0] = floatVarsDict['decayModeWeight1'][0]*floatVarsDict['decayModeWeight2'][0]

        oTree.Fill()
        counter += 1
        tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s/%s.root' % (options.location, iSample))
    print '  -- saved %d events' %(counter)
    tool.addEventsCount2Hist(hist = cutFlow, count = counter, labelName = 'myCut')
    iFile.cd()
    cutFlow.Write()
    oTree.Write()
    iFile.Close()


def go():
    setupLumiReWeight()
    for iSample, iLocation, xs in enVars.sampleLocations:
        loop_one_sample(iSample, iLocation, float(xs))
    freeLumiReWeight()


if __name__ == "__main__":
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
