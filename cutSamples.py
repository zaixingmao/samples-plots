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



def opts():
    parser = optparse.OptionParser()
    parser.add_option("-l", dest="location", default="/scratch/%s" % os.environ["USER"], help="location to be saved")
    parser.add_option("-n", dest="nevents", default="-1", help="amount of events to be saved")
    parser.add_option("-g", dest="genMatch", default="jet", help="gen particle for the reco-jet to match to")
    parser.add_option("-a", dest="addFiles", default="False", help="")
    parser.add_option("-t", dest="folderName", default="ttTreeBeforeChargeCut", help="")
    parser.add_option("-c", dest="cutLHEProduct", default=False, action="store_true", help="cut to 0 jet")

    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    options, args = parser.parse_args()

    return options

options = opts()

r.gStyle.SetOptStat(0)


# preVarList = ['EVENT', 'HMass', 'svMass', 'svPt', 'svEta', 'svPhi', 'J1Pt', 'J1Eta','J1Phi', 'J1Mass', 'NBTags', 'iso1', 'iso2', 'mJJ', 'J2Pt', 'J2Eta','J2Phi', 'J2Mass','pZeta', 'pZ', 'm1', 'm2',
#            'pZV', 'J3Pt', 'J3Eta','J3Phi', 'J3Mass', 'J4Pt', 'J4Eta','J4Phi', 'J4Mass', 'J5Pt', 'J5Eta','J5Phi', 'J5Mass', 'J6Pt', 'J6Eta','J6Phi', 'J6Mass', 
#            'J1CSVbtag', 'J2CSVbtag', 'J3CSVbtag', 'J4CSVbtag', 'J5CSVbtag', 'J6CSVbtag', 'pt1', 'eta1', 'phi1', 'pt2', 'eta2', 'phi2', 'met', 
#            'charge1', 'charge2',  'metphi',  
#            'J1PtUncorr', 'J1VtxPt', 'J1Vtx3dL', 'J1Vtx3deL', 'J1ptLeadTrk', 'J1vtxMass', 'J1vtxPt', 'J1Ntot', 
#            'J1SoftLepPt', 'J1SoftLepEta', 'J1SoftLepPhi', 'J1SoftLepPID', 'J1JECUnc', 'J1Et', 'J1Mt',
#            'J2PtUncorr', 'J2VtxPt', 'J2Vtx3dL', 'J2Vtx3deL', 'J2ptLeadTrk', 'J2vtxMass', 'J2vtxPt', 'J2Ntot', 
#            'J2SoftLepPt', 'J2SoftLepEta', 'J2SoftLepPhi', 'J2SoftLepPID', 'J2JECUnc', 'J2Et', 'J2Mt',
#            'J3PtUncorr', 'J3VtxPt', 'J3Vtx3dL', 'J3Vtx3deL', 'J3ptLeadTrk', 'J3vtxMass', 'J3vtxPt', 'J3Ntot', 
#            'J3SoftLepPt', 'J3SoftLepEta', 'J3SoftLepPhi', 'J3SoftLepPID', 'J3JECUnc', 'J3Et', 'J3Mt',
#            'J4PtUncorr', 'J4VtxPt', 'J4Vtx3dL', 'J4Vtx3deL', 'J4ptLeadTrk', 'J4vtxMass', 'J4vtxPt', 'J4Ntot', 
#            'J4SoftLepPt', 'J4SoftLepEta', 'J4SoftLepPhi', 'J4SoftLepPID', 'J4JECUnc', 'J4Et', 'J4Mt', 
#            'J5PtUncorr', 'J5VtxPt', 'J5Vtx3dL', 'J5Vtx3deL', 'J5ptLeadTrk', 'J5vtxMass', 'J5vtxPt', 'J5Ntot', 
#            'J5SoftLepPt', 'J5SoftLepEta', 'J5SoftLepPhi', 'J5SoftLepPID', 'J5JECUnc', 'J5Et', 'J5Mt', 
#            'J6PtUncorr', 'J6VtxPt', 'J6Vtx3dL', 'J6Vtx3deL', 'J6ptLeadTrk', 'J6vtxMass', 'J6vtxPt', 'J6Ntot', 
#            'J6SoftLepPt', 'J6SoftLepEta', 'J6SoftLepPhi', 'J6SoftLepPID', 'J6JECUnc', 'J6Et', 'J6Mt', 
#             'tauDecayMode1', 'tauDecayMode2',
#            'mvacov00','mvacov01','mvacov10','mvacov11', 'byIsolationMVA2raw_1', 'byIsolationMVA2raw_2'
#           ]
# genVarList = ['genBPt', 'genBEta', 'genBPhi','genBMass', 'genTauPt', 'genTauEta', 'genTauPhi', 'genElePt', 'genEleEta', 
#               'genElePhi', 'genMuPt', 'genMuEta', 'genMuPhi','J1GenPt', 'J1GenEta', 'J1GenPhi', 'J1GenMass',
#               'J2GenPt', 'J2GenEta', 'J2GenPhi', 'J2GenMass', 'J3GenPt', 'J3GenEta', 'J3GenPhi', 'J3GenMass',
#               'J4GenPt', 'J4GenEta', 'J4GenPhi', 'J4GenMass']
# 
# fullVarList = []
# for iVar in preVarList:
#     fullVarList.append(iVar)
# for iVar in genVarList:
#     fullVarList.append(iVar)


def loop_one_sample(iSample, iLocation, iXS):
    if 'data' in iSample:
        isData = True
#         varList = preVarList
    else:
        isData = False
#         varList = fullVarList

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
#     for iVar in range(len(varList)):
#         iChain.SetBranchStatus(varList[iVar],1)
    fullMass = array('f', [0.])
    mJJ = array('f', [0.])
    ptJJ = array('f', [0.])
    etaJJ = array('f', [0.])
    phiJJ = array('f', [0.])
    CSVJ1 = array('f', [0.])
    CSVJ1Pt = array('f', [0.])
    CSVJ1Eta = array('f', [0.])
    CSVJ1Phi = array('f', [0.])
    CSVJ1Mass = array('f', [0.])
    CSVJ2 = array('f', [0.])
    CSVJ2Pt = array('f', [0.])
    CSVJ2Eta = array('f', [0.])
    CSVJ2Phi = array('f', [0.])
    CSVJ2Mass = array('f', [0.])
    dRTauTau = array('f', [0.])
    dRJJ = array('f', [0.])
    dRhh = array('f', [0.])
    mTop1 = array('f', [0.])
    mTop2 = array('f', [0.])
    pZ_new = array('f', [0.])
    pZV_new = array('f', [0.])
    pZ_new2 = array('f', [0.])
    pZV_new2 = array('f', [0.])
    triggerEff = array('f', [0.])
    triggerEff1 = array('f', [0.])
    triggerEff2 = array('f', [0.])
    metTau1DPhi = array('f', [0.])
    metTau2DPhi = array('f', [0.])
    metJ1DPhi = array('f', [0.])
    metJ2DPhi = array('f', [0.])
    metTauPairDPhi = array('f', [0.])
    metJetPairDPhi = array('f', [0.])
    metSvTauPairDPhi = array('f', [0.])
    dRGenJet1Match = array('f', [0.])
    dRGenJet2Match = array('f', [0.])
    matchGenJet1Pt = array('f', [0.])
    matchGenJet1Eta = array('f', [0.])
    matchGenJet1Phi = array('f', [0.])
    matchGenJet1Mass = array('f', [0.])
    matchGenJet2Pt = array('f', [0.])
    matchGenJet2Eta = array('f', [0.])
    matchGenJet2Phi = array('f', [0.])
    matchGenJet2Mass = array('f', [0.])
    matchGenMJJ = array('f', [0.])
    matchGenPtJJ = array('f', [0.])
    matchGendRJJ = array('f', [0.])

    CSVJ1PtUncorr = array('f', [0.])
    CSVJ1Et = array('f', [0.])
    CSVJ1Mt = array('f', [0.])
    CSVJ1ptLeadTrk = array('f', [0.])
    CSVJ1Vtx3dL  = array('f', [0.])
    CSVJ1Vtx3deL  = array('f', [0.])
    CSVJ1vtxMass  = array('f', [0.])
    CSVJ1VtxPt = array('f', [0.])
    CSVJ1JECUnc = array('f', [0.])
    CSVJ1Ntot = array('f', [0.])
    CSVJ1SoftLeptPtRel = array('f', [0.])
    CSVJ1SoftLeptPt = array('f', [0.])
    CSVJ1SoftLeptdR = array('f', [0.])

    CSVJ2PtUncorr = array('f', [0.])
    CSVJ2Et = array('f', [0.])
    CSVJ2Mt = array('f', [0.])
    CSVJ2ptLeadTrk = array('f', [0.])
    CSVJ2Vtx3dL  = array('f', [0.])
    CSVJ2Vtx3deL  = array('f', [0.])
    CSVJ2vtxMass  = array('f', [0.])
    CSVJ2VtxPt = array('f', [0.])
    CSVJ2JECUnc = array('f', [0.])
    CSVJ2Ntot = array('f', [0.])
    CSVJ2SoftLeptPtRel = array('f', [0.])
    CSVJ2SoftLeptPt = array('f', [0.])
    CSVJ2SoftLeptdR = array('f', [0.])

    chi2KinFit = array('f', [0.])
    chi2KinFit2 = array('f', [0.])
    fMassKinFit = array('f', [0.])
    nElectrons = array('i', [0])
    nMuons = array('i', [0])
    sampleName = bytearray(30)
    category = bytearray(30)
    PUWeight = array('f', [0.])
    initEvents = array('i', [0])
    xs = array('f', [0.])

    iChain.LoadTree(0)
    oTree = iChain.GetTree().CloneTree(0)
    iSample = iSample + '_%s' %('all' if options.nevents == "-1" else options.nevents)
    iFile = r.TFile("%s/%s.root" %(options.location,iSample),"recreate")
    oTree.Branch("fMass", fullMass, "fMass/F")
    oTree.Branch("mJJ", mJJ, "mJJ/F")
    oTree.Branch("etaJJ", etaJJ, "etaJJ/F")
    oTree.Branch("phiJJ", phiJJ, "phiJJ/F")
    oTree.Branch("ptJJ", ptJJ, "ptJJ/F")
    oTree.Branch("CSVJ1", CSVJ1, "CSVJ1/F")
    oTree.Branch("CSVJ1Pt", CSVJ1Pt, "CSVJ1Pt/F")
    oTree.Branch("CSVJ1Eta", CSVJ1Eta, "CSVJ1Eta/F")
    oTree.Branch("CSVJ1Phi", CSVJ1Phi, "CSVJ1Phi/F")
    oTree.Branch("CSVJ1Mass", CSVJ1Mass, "CSVJ1Mass/F")
    oTree.Branch("CSVJ2", CSVJ2, "CSVJ2/F")
    oTree.Branch("CSVJ2Pt", CSVJ2Pt, "CSVJ2Pt/F")
    oTree.Branch("CSVJ2Eta", CSVJ2Eta, "CSVJ2Eta/F")
    oTree.Branch("CSVJ2Phi", CSVJ2Phi, "CSVJ2Phi/F")
    oTree.Branch("CSVJ2Mass", CSVJ2Mass, "CSVJ2Mass/F")
    oTree.Branch("dRTauTau", dRTauTau, "dRTauTau/F")
    oTree.Branch("dRJJ", dRJJ, "dRJJ/F")
    oTree.Branch("dRhh", dRhh, "dRhh/F")
    oTree.Branch("mTop1", mTop1, "mTop1/F")
    oTree.Branch("mTop2", mTop2, "mTop2/F")
    oTree.Branch("pZ_new", pZ_new, "pZ_new/F")
    oTree.Branch("pZV_new", pZV_new, "pZV_new/F")
    oTree.Branch("pZ_new2", pZ_new2, "pZ_new2/F")
    oTree.Branch("pZV_new2", pZV_new2, "pZV_new2/F")
    oTree.Branch("triggerEff", triggerEff, "triggerEff/F")
    oTree.Branch("triggerEff1", triggerEff1, "triggerEff1/F")
    oTree.Branch("triggerEff2", triggerEff2, "triggerEff2/F")
    oTree.Branch("metTau1DPhi", metTau1DPhi, "metTau1DPhi/F")
    oTree.Branch("metTau2DPhi", metTau2DPhi, "metTau2DPhi/F")
    oTree.Branch("metJ1DPhi", metJ1DPhi, "metJ1DPhi/F")
    oTree.Branch("metJ2DPhi", metJ2DPhi, "metJ2DPhi/F")
    oTree.Branch("metTauPairDPhi", metTauPairDPhi, "metTauPairDPhi/F")
    oTree.Branch("metJetPairDPhi", metJetPairDPhi, "metJetPairDPhi/F")
    oTree.Branch("metSvTauPairDPhi", metSvTauPairDPhi, "metSvTauPairDPhi/F")
    oTree.Branch("chi2KinFit", chi2KinFit, "chi2KinFit/F")
    oTree.Branch("chi2KinFit2", chi2KinFit2, "chi2KinFit2/F")

    oTree.Branch("fMassKinFit", fMassKinFit, "fMassKinFit/F")
    oTree.Branch("nElectrons", nElectrons, "nElectrons/I")
    oTree.Branch("nMuons", nMuons, "nMuons/I")
    oTree.Branch("sampleName", sampleName, "sampleName[31]/C")
    oTree.Branch("category", category, "category[31]/C")
    oTree.Branch("PUWeight", PUWeight, "PUWeight/F")

    if not isData:
        oTree.Branch("dRGenJet1Match", dRGenJet1Match, "dRGenJet1Match/F")
        oTree.Branch("dRGenJet2Match", dRGenJet2Match, "dRGenJet2Match/F")
        oTree.Branch("matchGenJet1Pt", matchGenJet1Pt, "matchGenJet1Pt/F")
        oTree.Branch("matchGenJet1Eta", matchGenJet1Eta, "matchGenJet1Eta/F")
        oTree.Branch("matchGenJet1Phi", matchGenJet1Phi, "matchGenJet1Phi/F")
        oTree.Branch("matchGenJet1Mass", matchGenJet1Mass, "matchGenJet1Mass/F")
        oTree.Branch("matchGenJet2Pt", matchGenJet2Pt, "matchGenJet2Pt/F")
        oTree.Branch("matchGenJet2Eta", matchGenJet2Eta, "matchGenJet2Eta/F")
        oTree.Branch("matchGenJet2Phi", matchGenJet2Phi, "matchGenJet2Phi/F")
        oTree.Branch("matchGenJet2Mass", matchGenJet2Mass, "matchGenJet2Mass/F")
        oTree.Branch("matchGenMJJ", matchGenMJJ, "matchGenMJJ/F")
        oTree.Branch("matchGenPtJJ", matchGenPtJJ, "matchGenPtJJ/F")
        oTree.Branch("matchGendRJJ", matchGendRJJ, "matchGendRJJ/F")


    oTree.Branch("CSVJ1PtUncorr",CSVJ1PtUncorr,"CSVJ1PtUncorr/F")
    oTree.Branch("CSVJ1Et",CSVJ1Et,"CSVJ1Et/F")
    oTree.Branch("CSVJ1Mt",CSVJ1Mt,"CSVJ1Mt/F")
    oTree.Branch("CSVJ1ptLeadTrk",CSVJ1ptLeadTrk,"CSVJ1ptLeadTrk/F")
    oTree.Branch("CSVJ1Vtx3dL",CSVJ1Vtx3dL,"CSVJ1Vtx3dL/F")
    oTree.Branch("CSVJ1Vtx3deL",CSVJ1Vtx3deL,"CSVJ1Vtx3deL/F")
    oTree.Branch("CSVJ1vtxMass",CSVJ1vtxMass,"CSVJ1vtxMass/F")
    oTree.Branch("CSVJ1VtxPt",CSVJ1VtxPt,"CSVJ1VtxPt/F")
    oTree.Branch("CSVJ1JECUnc",CSVJ1JECUnc,"CSVJ1JECUnc/F")
    oTree.Branch("CSVJ1Ntot",CSVJ1Ntot,"CSVJ1Ntot/F")
    oTree.Branch("CSVJ1SoftLeptPtRel",CSVJ1SoftLeptPtRel,"CSVJ1SoftLeptPtRel/F")
    oTree.Branch("CSVJ1SoftLeptPt",CSVJ1SoftLeptPt,"CSVJ1SoftLeptPt/F")
    oTree.Branch("CSVJ1SoftLeptdR",CSVJ1SoftLeptdR,"CSVJ1SoftLeptdR/F")

    oTree.Branch("CSVJ2PtUncorr",CSVJ2PtUncorr,"CSVJ2PtUncorr/F")
    oTree.Branch("CSVJ2Et",CSVJ2Et,"CSVJ2Et/F")
    oTree.Branch("CSVJ2Mt",CSVJ2Mt,"CSVJ2Mt/F")
    oTree.Branch("CSVJ2ptLeadTrk",CSVJ2ptLeadTrk,"CSVJ2ptLeadTrk/F")
    oTree.Branch("CSVJ2Vtx3dL",CSVJ2Vtx3dL,"CSVJ2Vtx3dL/F")
    oTree.Branch("CSVJ2Vtx3deL",CSVJ2Vtx3deL,"CSVJ2Vtx3deL/F")
    oTree.Branch("CSVJ2vtxMass",CSVJ2vtxMass,"CSVJ2vtxMass/F")
    oTree.Branch("CSVJ2VtxPt",CSVJ2VtxPt,"CSVJ2VtxPt/F")
    oTree.Branch("CSVJ2JECUnc",CSVJ2JECUnc,"CSVJ2JECUnc/F")
    oTree.Branch("CSVJ2Ntot",CSVJ2Ntot,"CSVJ2Ntot/F")
    oTree.Branch("CSVJ2SoftLeptPtRel",CSVJ2SoftLeptPtRel,"CSVJ2SoftLeptPtRel/F")
    oTree.Branch("CSVJ2SoftLeptPt",CSVJ2SoftLeptPt,"CSVJ2SoftLeptPt/F")
    oTree.Branch("CSVJ2SoftLeptdR",CSVJ2SoftLeptdR,"CSVJ2SoftLeptdR/F")

    oTree.Branch("initEvents",initEvents,"initEvents/I")
    oTree.Branch("xs",xs,"xs/F")
    sampleName[:31] = iSample
    initEvents[0] = int(cutFlow.GetBinContent(1))
    xs[0] = iXS
    counter = 0
    for iEntry in range(nEntries):
        iChain.LoadTree(iEntry)
        iChain.GetEntry(iEntry)

        if options.addFiles == 'True':
            oTree.Fill()
            counter += 1
            tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s/%s.root' % (options.location, iSample))
            continue

        if options.cutLHEProduct:
            if iChain.LHEProduct != 5:
                continue
        if counter == int(options.nevents):
            break
        if iChain.svMass.size() == 0:
            continue
        if iChain.pt2.at(0) < 45:
            continue
#         if not tool.calc(iChain):
#             continue
#         if iChain.charge1.at(0) - iChain.charge2.at(0) == 0: #sign requirement
#             continue
#         if iChain.pt1.at(0)<45 or iChain.pt2.at(0)<45: #pt cut
#             continue        
#         if abs(iChain.eta1.at(0))>2.1 or abs(iChain.eta2.at(0))>2.1: #pt cut
#             continue
#         if iChain.iso1.at(0)<1.5 or iChain.iso2.at(0)<1.5: #iso cut
#             continue 

        jetsList = [(iChain.J1CSVbtag, J1.SetCoordinates(iChain.J1Pt, iChain.J1Eta, iChain.J1Phi, iChain.J1Mass), 'J1'),
                    (iChain.J2CSVbtag, J2.SetCoordinates(iChain.J2Pt, iChain.J2Eta, iChain.J2Phi, iChain.J2Mass), 'J2'),
                    (iChain.J3CSVbtag, J3.SetCoordinates(iChain.J3Pt, iChain.J3Eta, iChain.J3Phi, iChain.J3Mass), 'J3'),
                    (iChain.J4CSVbtag, J4.SetCoordinates(iChain.J4Pt, iChain.J4Eta, iChain.J4Phi, iChain.J4Mass), 'J4'),
                    (iChain.J5CSVbtag, J5.SetCoordinates(iChain.J5Pt, iChain.J5Eta, iChain.J5Phi, iChain.J5Mass), 'J5'),
                    (iChain.J6CSVbtag, J6.SetCoordinates(iChain.J6Pt, iChain.J6Eta, iChain.J6Phi, iChain.J6Mass), 'J6')]
        sv4Vec.SetCoordinates(iChain.svPt.at(0), iChain.svEta.at(0), iChain.svPhi.at(0), iChain.svMass.at(0))
        bb = lvClass()
        bb, CSVJ1[0], CSVJ2[0], CSVJet1, CSVJet2, fullMass[0], dRJJ[0], j1Name, j2Name = findFullMass(jetsList=jetsList, sv4Vec=sv4Vec, ptThreshold = enVars.jetPtThreshold) 
        if bb == -1:
            continue

        category[:31] = findCategory(CSVJ1[0], CSVJ2[0])
#         if iChain.LHEProduct != 5:
#             continue
        #Gen Matching
        matchGenJet1Pt[0] = 0
        matchGenJet2Pt[0] = 0
        if not isData:
            PUWeight[0] = getPUWeight(iChain.puTruth)
            if options.genMatch == 'jet':
                dRGenJet1Match[0], mGenJet1, dRGenJet2Match[0], mGenJet2 = findGenJet(j1Name, CSVJet1, j2Name, CSVJet2, iChain)
            else:
                dRGenJet1Match[0], mGenJet1, dRGenJet2Match[0], mGenJet2 = findGenBJet(CSVJet1, CSVJet2, iChain)                
           
            matchGenJet1Pt[0] = mGenJet1.pt()
            matchGenJet1Eta[0] = mGenJet1.eta()
            matchGenJet1Phi[0] = mGenJet1.phi()
            matchGenJet1Mass[0] = mGenJet1.mass()

            matchGenJet2Pt[0] = mGenJet2.pt()
            matchGenJet2Eta[0] = mGenJet2.eta()
            matchGenJet2Phi[0] = mGenJet2.phi()
            matchGenJet2Mass[0] = mGenJet2.mass()

            genJJ = mGenJet1 + mGenJet2
            matchGenMJJ[0] = genJJ.mass()
            matchGenPtJJ[0] = genJJ.pt()
            matchGendRJJ[0] = r.Math.VectorUtil.DeltaR(mGenJet1, mGenJet2)

            if matchGenMJJ[0] < 0:
                matchGenMJJ[0] = 0
                matchGenPtJJ[0] = 0
        else:
            PUWeight[0] = 1.0
        #Store values
        CSVJ1Pt[0] = CSVJet1.pt()
        CSVJ1Eta[0] = CSVJet1.eta()
        CSVJ1Phi[0] = CSVJet1.phi()
        CSVJ1Mass[0] = CSVJet1.mass()
        CSVJ2Pt[0] = CSVJet2.pt()
        CSVJ2Eta[0] = CSVJet2.eta()
        CSVJ2Phi[0] = CSVJet2.phi()
        CSVJ2Mass[0] = CSVJet2.mass()

        CSVJ1PtUncorr[0], CSVJ1Et[0], CSVJ1Mt[0], CSVJ1ptLeadTrk[0], CSVJ1Vtx3dL[0], CSVJ1Vtx3deL[0], CSVJ1vtxMass[0], CSVJ1VtxPt[0], CSVJ1JECUnc[0], CSVJ1Ntot[0], CSVJ1SoftLeptPtRel[0], CSVJ1SoftLeptPt[0], CSVJ1SoftLeptdR[0], CSVJ2PtUncorr[0], CSVJ2Et[0], CSVJ2Mt[0], CSVJ2ptLeadTrk[0], CSVJ2Vtx3dL[0], CSVJ2Vtx3deL[0], CSVJ2vtxMass[0], CSVJ2VtxPt[0], CSVJ2JECUnc[0], CSVJ2Ntot[0], CSVJ2SoftLeptPtRel[0], CSVJ2SoftLeptPt[0], CSVJ2SoftLeptdR[0] = getRegVars(j1Name, j2Name, iChain)

        if CSVJ1Vtx3dL[0] == -10:
            CSVJ1Vtx3dL[0] = 0
            CSVJ1Vtx3deL[0] = 0
            CSVJ1vtxMass[0] = 0
            CSVJ1VtxPt[0] = 0
        if CSVJ1ptLeadTrk[0] < 0:
            CSVJ1ptLeadTrk[0] = 0

        if CSVJ2Vtx3dL[0] == -10:
            CSVJ2Vtx3dL[0] = 0
            CSVJ2Vtx3deL[0] = 0
            CSVJ2vtxMass[0] = 0
            CSVJ2VtxPt[0] = 0
        if CSVJ2ptLeadTrk[0] < 0:
            CSVJ2ptLeadTrk[0] = 0

        if CSVJ1SoftLeptPtRel[0] == -10:
            CSVJ1SoftLeptPtRel[0] == 0
            CSVJ1SoftLeptPt[0] == 0
        if CSVJ2SoftLeptPtRel[0] == -10:
            CSVJ2SoftLeptPtRel[0] == 0
            CSVJ2SoftLeptPt[0] == 0

        ptJJ[0] = bb.pt()
        etaJJ[0] = bb.eta()
        phiJJ[0] = bb.phi()
        mJJ[0] = bb.mass()
        tau1.SetCoordinates(iChain.pt1.at(0), iChain.eta1.at(0), iChain.phi1.at(0), iChain.m1.at(0))
        tau2.SetCoordinates(iChain.pt2.at(0), iChain.eta2.at(0), iChain.phi2.at(0), iChain.m2.at(0))
        mTop1[0] = (CSVJet1 + tau1).mass()
        mTop2[0] = (CSVJet2 + tau2).mass()

        nElectrons[0] = iChain.nElectrons
        nMuons[0] = iChain.nMuons
#         pZ_new[0] = iChain.pZ/iChain.svPt.at(0)
#         pZV_new[0] = iChain.pZV/iChain.svPt.at(0)
#         pZ_new2[0] = iChain.pZ/fullMass[0]
#         pZV_new2[0] = iChain.pZV/fullMass[0]

        dRTauTau[0] = r.Math.VectorUtil.DeltaR(tau1, tau2)
        dRhh[0] = r.Math.VectorUtil.DeltaR(bb, sv4Vec)

        #Trigger Calc MetDPhiValues
        metTau1DPhi[0], metTau2DPhi[0], metJ1DPhi[0], metJ2DPhi[0], metTauPairDPhi[0], metJetPairDPhi[0], metSvTauPairDPhi[0] = calcdPhiMetValues(iChain.phi1.at(0), iChain.phi2.at(0), CSVJet1.phi(), CSVJet2.phi(), iChain.metphi.at(0), (tau1+tau2).phi(), bb.phi(), iChain.svPhi.at(0))

        #Trigger Eff
        eff1 = trigger.correction_leg1(iChain, 0)
        eff2 = trigger.correction_leg2(iChain, 0)

        triggerEff1[0] = eff1
        triggerEff2[0] = eff2        
        triggerEff[0] = eff1*eff2
        if isData:
            triggerEff[0] = 1
            triggerEff1[0] = 1
            triggerEff2[0] = 1

        #Kinematic Fit
        chi2KinFit[0], fMassKinFit[0], status = kinfit.fit(iChain, CSVJet1, CSVJet2)
        chi2KinFit2[0] = chi2KinFit[0]
        if chi2KinFit2[0] > 200:
            chi2KinFit2[0] = 200

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


if __name__ == "__main__":
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
