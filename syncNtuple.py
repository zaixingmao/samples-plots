#!/usr/bin/env python

import ROOT as r
import tool
from array import array
from operator import itemgetter
import math
import optparse
import trigger
import makeWholeTools2
varList = [('run', 'RUN', 'I'),
           ('lumi', 'LUMI', 'I'),
           ('evt', 'EVENT', 'I'),
           ('npv', 'vertices', 'I'),

           ('rho', 'Rho', 'F'),

           ('mvis', 'mTauTau', 'F'),
           ('m_sv', 'svMass', 'F'),
           ('pt_sv', 'svPt', 'F'),
           ('eta_sv', 'svEta', 'F'),
           ('phi_sv', 'svPhi', 'F'),

           ('pt_1', 'pt1', 'F'),
           ('phi_1', 'phi1', 'F'),
           ('eta_1', 'eta1', 'F'),
           ('m_1', 'm1', 'F'),
           ('q_1', 'charge1', 'I'),
           ('mva_1', 0, 'I'),
           ('byCombinedIsolationDeltaBetaCorrRaw3Hits_1', 'iso1', 'F'),
           ('d0_1', 'd0_1', 'F'),
           ('dZ_1', 'l1dz', 'F'),
           ('mt_1', 'mt1', 'F'),

           ('pt_2', 'pt2', 'F'),
           ('phi_2', 'phi2', 'F'),
           ('eta_2', 'eta2', 'F'),
           ('m_2', 'm2', 'F'),
           ('q_2', 'charge2', 'I'),
           ('mva_2', 0, 'I'),
           ('byCombinedIsolationDeltaBetaCorrRaw3Hits_2', 'iso2', 'F'),
           ('d0_2', 'd0_2', 'I'),
           ('dZ_2', 'l2dz', 'F'),
           ('mt_2', 'mt2', 'F'),

           ('againstMuonLoose2_1', 'againstMuonLoose1', 'F'),
           ('againstMuonLoose2_2', 'againstMuonLoose2', 'F'),
           ('againstMuonMedium2_1', 'againstMuonMedium1', 'F'),
           ('againstMuonMedium2_2', 'againstMuonMedium2', 'F'),
           ('againstMuonTight2_1', 'againstMuonTight1', 'F'),
           ('againstMuonTight2_2', 'againstMuonTight2', 'F'),

           ('met', 'metUnc', 'F'),
           ('mvamet', 'met', 'F'),
           ('mvametphi', 'metphi', 'F'),


           ('jpt_1', 'J1Pt', 'F'),
           ('jeta_1', 'J1Eta', 'F'),
           ('jphi_1', 'J1Phi', 'F'),
           ('jptraw_1', 'J1PtUncorr', 'F'),
           ('jptunc_1', 'J1JECUnc', 'F'),
           ('jctm_1', 'J1Ntot', 'I'),

           ('jpt_2', 'J2Pt', 'F'),
           ('jeta_2', 'J2Eta', 'F'),
           ('jphi_2', 'J2Phi', 'F'),
           ('jptraw_2', 'J2PtUncorr', 'F'),
           ('jptunc_2', 'J2JECUnc', 'F'),
           ('jctm_2', 'J2Ntot', 'I'),
          ]

def findBestPair(iTree):
    nPairs = len(iTree.pt1)
    isoCom = 999
    bestPair = 0
    if nPairs == 1:
        return bestPair
    else:
        for iPair in range(nPairs):
            tmpIsoCom = iTree.iso1.at(iPair) + iTree.iso2.at(iPair)
            if tmpIsoCom < isoCom:
                isoCom = tmpIsoCom
                bestPair = iPair
    return bestPair

def passTrigger(tree):
    passTrigger = False
#     if tree.HLT_DoubleMediumIsoPFTau25_Trk5_eta2p1_Jet30_fired > 0:
#         passTrigger = True
#     if tree.HLT_DoubleMediumIsoPFTau30_Trk5_eta2p1_Jet30_fired > 0:
#         passTrigger = True
#     if tree.HLT_DoubleMediumIsoPFTau30_Trk1_eta2p1_Jet30_fired > 0:
#         passTrigger = True
#     if tree.HLT_DoubleMediumIsoPFTau35_Trk5_eta2p1_fired > 0:
#         passTrigger = True
#     if tree.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_fired > 0:
#         passTrigger = True
    if tree.HLT_Any > 0:
        passTrigger = True
#     if passTrigger == False:
#         print tree.HLT_DoubleMediumIsoPFTau25_Trk5_eta2p1_Jet30_fired
#         print tree.HLT_DoubleMediumIsoPFTau30_Trk5_eta2p1_Jet30_fired
#         print tree.HLT_DoubleMediumIsoPFTau30_Trk1_eta2p1_Jet30_fired
#         print tree.HLT_DoubleMediumIsoPFTau35_Trk5_eta2p1_fired
#         print tree.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_fired

    return passTrigger

def passIsoCut(iso1, iso2):
    if iso1 > 1.0 or iso2 > 1.0:
        return 0
    return 1

def passCut(iTree, track, iBestPair):
    if iTree.nElectrons > 0 or iTree.nMuons > 0:
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at 3rdLeptVeto: nEle %i nMu %i" %(iTree.EVENT, iTree.RUN, iTree.LUMI, iTree.nElectrons, iTree.nMuons)
        return 0
    if iTree.pt1.at(iBestPair)<45 or iTree.pt2.at(iBestPair)<45:
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at tauPt: pt1 %.2f pt2 %.2f" %(iTree.EVENT, iTree.RUN, iTree.LUMI, iTree.pt1.at(iBestPair), iTree.pt2.at(iBestPair))
        return 0
    if not passTrigger(iTree):
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at triggerPath" %(iTree.EVENT, iTree.RUN, iTree.LUMI)
        return 0

    if iTree.charge1.at(iBestPair) == iTree.charge2.at(iBestPair):
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at SS" %(iTree.EVENT, iTree.RUN, iTree.LUMI)
        return 0

    if not passIsoCut(iTree.iso1.at(iBestPair), iTree.iso2.at(iBestPair)):
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at iso: iso1 %.2f iso2 %.2f" %(iTree.EVENT, iTree.RUN, iTree.LUMI, iTree.iso1.at(iBestPair), iTree.iso2.at(iBestPair))
        return 0

    if iTree.CSVJ1 < 0:
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at 2jets" %(iTree.EVENT, iTree.RUN, iTree.LUMI)
        return 0

    if iTree.svMass.at(iBestPair) < 90 or iTree.svMass.at(iBestPair) > 150 :
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at svMass: %.2f" %(iTree.EVENT, iTree.RUN, iTree.LUMI, iTree.svMass.at(iBestPair))
        return 0

    if iTree.mJJ < 70 or iTree.mJJ > 150 :
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at mJJ: %.2f" %(iTree.EVENT, iTree.RUN, iTree.LUMI, iTree.mJJ)
        return 0

    if iTree.fMassKinFit < 10 :
        if track:
            print "Event: %i Run: %i Lumi: %i     failed at fMassKinFit: %.2f" %(iTree.EVENT, iTree.RUN, iTree.LUMI, iTree.fMassKinFit)
        return 0
    return 1

def makeSyncNtuples(iLocation, cut, cutBTag, treepath, usePassJetTrigger):

    if '.root' in iLocation:
        iFile = r.TFile(iLocation)
        iTree = iFile.Get(treepath)
        nEntries = iTree.GetEntries()
        oFileName = iLocation[iLocation.rfind("/")+1:iLocation.rfind(".root")]
        oFileName += '_sync'
        oFileName += '%s_%s' %(cut, cutBTag)
        if usePassJetTrigger:
            oFileName += '_jetCut'
    else:
        iTree = r.TChain(treepath)
        nEntries = tool.addFiles(ch=iTree, dirName=iLocation, knownEventNumber=0, maxFileNumber=-1, printTotalEvents = True)
        oFileName = iLocation[iLocation.rfind("/")+1:iLocation.find("-SUB-TT")]

    iTree.SetBranchStatus("*",1)
    print iLocation


    oFile = r.TFile("/nfs_scratch/zmao/samples/sync/%s.root" %oFileName,"recreate")
    oTree = r.TTree('TauCheck', 'TauCheck')

    run  = array('i', [0])
    lumi = array('i', [0])
    evt = array('I', [0])
    nTauPairs  = array('i', [0])

    npv = array('i', [0])
    npu = array('i', [0])
    rho = array('f', [0.])

    mvis = array('f', [0.])
    m_sv = array('f', [0.])
    pt_sv = array('f', [0.])
    eta_sv = array('f', [0.])
    phi_sv = array('f', [0.])
    
    pt_1 = array('f', [0.])
    phi_1 = array('f', [0.])
    eta_1 = array('f', [0.])
    m_1 = array('f', [0.])
    q_1 = array('i', [0])
    iso_1 = array('f', [0.])
    mva_1 = array('f', [0.])
    byCombinedIsolationDeltaBetaCorrRaw3Hits_1 = array('f', [0.])
    d0_1 = array('f', [0.])
    dZ_1 = array('f', [0.])
    mt_1 = array('f', [0.])

    pt_2 = array('f', [0.])
    phi_2 = array('f', [0.])
    eta_2 = array('f', [0.])
    m_2 = array('f', [0.])
    q_2 = array('i', [0])
    iso_2 = array('f', [0.])
    mva_2 = array('f', [0.])
    byCombinedIsolationDeltaBetaCorrRaw3Hits_2 = array('f', [0.])
    d0_2 = array('f', [0.])
    dZ_2 = array('f', [0.])
    mt_2 = array('f', [0.])

    againstElectronMVA3raw_1 = array('f', [0.])
    againstElectronMVA3raw_2 = array('f', [0.])
    againstMuonLoose2_1 = array('f', [0.])
    againstMuonLoose2_2 = array('f', [0.])
    againstMuonMedium2_1 = array('f', [0.])
    againstMuonMedium2_2 = array('f', [0.])
    againstMuonTight2_1 = array('f', [0.])
    againstMuonTight2_2 = array('f', [0.])

    met = array('f', [0.])
    mvamet = array('f', [0.])
    mvametphi = array('f', [0.])
    mvacov00 = array('f', [0.])
    mvacov01 = array('f', [0.])
    mvacov10 = array('f', [0.])
    mvacov11 = array('f', [0.])

    pzetavis = array('f', [0.])
    pzetamiss = array('f', [0.])

    pt_tt = array('f', [0.])
    njets = array('i', [0])
    njetspt20 = array('i', [0])

    jpt_1 = array('f', [0.])
    jeta_1 = array('f', [0.])
    jphi_1 = array('f', [0.])
    jptraw_1 = array('f', [0.])
    jptunc_1 = array('f', [0.])
    jmva_1 = array('f', [0.])
    jlrm_1 = array('f', [0.])
    jctm_1 = array('f', [0.])
    jpass_1 = array('b', [0])

    jpt_2 = array('f', [0.])
    jeta_2 = array('f', [0.])
    jphi_2 = array('f', [0.])
    jptraw_2 = array('f', [0.])
    jptunc_2 = array('f', [0.])
    jmva_2 = array('f', [0.])
    jlrm_2 = array('f', [0.])
    jctm_2 = array('f', [0.])
    jpass_2 = array('b', [0])

    bpt_1 = array('f', [0.])
    beta_1 = array('f', [0.])
    bphi_1 = array('f', [0.])
    bcsv_1 = array('f', [0.])

    bpt_2 = array('f', [0.])
    beta_2 = array('f', [0.])
    bphi_2 = array('f', [0.])
    bcsv_2 = array('f', [0.])

    bpt_3 = array('f', [0.])
    beta_3 = array('f', [0.])
    bphi_3 = array('f', [0.])
    bcsv_3 = array('f', [0.])

    m_bb = array('f', [0.])
    m_ttbb = array('f', [0.])
    nbtag = array('i', [0])

    trigweight_1 = array('f', [0.])
    trigweight_2 = array('f', [0.])
    effweight = array('f', [0.])

    oTree.Branch("run", run, "run/I")
    oTree.Branch("lumi", lumi, "lumi/I")
    oTree.Branch("evt", evt, "evt/i")
    oTree.Branch("nTauPairs", nTauPairs, "nTauPairs/I")

    oTree.Branch("npv", npv, "npv/I")
    oTree.Branch("npu", npu, "npu/I")
    oTree.Branch("rho", rho, "rho/F")

    oTree.Branch("mvis", mvis, "mvis/F")
    oTree.Branch("m_sv", m_sv, "m_sv/F")
    oTree.Branch("pt_sv", pt_sv, "pt_sv/F")
    oTree.Branch("eta_sv", eta_sv, "eta_sv/F")
    oTree.Branch("phi_sv", phi_sv, "phi_sv/F")

    oTree.Branch("pt_1", pt_1, "pt_1/F")
    oTree.Branch("phi_1", phi_1, "phi_1/F")
    oTree.Branch("eta_1", eta_1, "eta_1/F")
    oTree.Branch("m_1", m_1, "m_1/F")
    oTree.Branch("q_1", q_1, "q_1/I")
    oTree.Branch("iso_1", iso_1, "iso_1/F")
    oTree.Branch("mva_1", mva_1, "mva_1/F")
    oTree.Branch("byCombinedIsolationDeltaBetaCorrRaw3Hits_1", byCombinedIsolationDeltaBetaCorrRaw3Hits_1, "byCombinedIsolationDeltaBetaCorrRaw3Hits_1/F")
    oTree.Branch("d0_1", d0_1, "d0_1/F")
    oTree.Branch("dZ_1", dZ_1, "dZ_1/F")
    oTree.Branch("mt_1", mt_1, "mt_1/F")

    oTree.Branch("pt_2", pt_2, "pt_2/F")
    oTree.Branch("phi_2", phi_2, "phi_2/F")
    oTree.Branch("eta_2", eta_2, "eta_2/F")
    oTree.Branch("m_2", m_2, "m_2/F")
    oTree.Branch("q_2", q_2, "q_2/I")
    oTree.Branch("iso_2", iso_2, "iso_2/F")
    oTree.Branch("mva_2", mva_2, "mva_2/F")
    oTree.Branch("byCombinedIsolationDeltaBetaCorrRaw3Hits_2", byCombinedIsolationDeltaBetaCorrRaw3Hits_2, "byCombinedIsolationDeltaBetaCorrRaw3Hits_2/F")
    oTree.Branch("d0_2", d0_2, "d0_2/F")
    oTree.Branch("dZ_2", dZ_2, "dZ_2/F")
    oTree.Branch("mt_2", mt_2, "mt_2/F")

    oTree.Branch("againstElectronMVA3raw_1", againstElectronMVA3raw_1, "againstElectronMVA3raw_1/F")
    oTree.Branch("againstElectronMVA3raw_2", againstElectronMVA3raw_2, "againstElectronMVA3raw_2/F")
    oTree.Branch("againstMuonLoose2_1", againstMuonLoose2_1, "againstMuonLoose2_1/F")
    oTree.Branch("againstMuonLoose2_2", againstMuonLoose2_2, "againstMuonLoose2_2/F")
    oTree.Branch("againstMuonMedium2_1", againstMuonMedium2_1, "againstMuonMedium2_1/F")
    oTree.Branch("againstMuonMedium2_2", againstMuonMedium2_2, "againstMuonMedium2_2/F")
    oTree.Branch("againstMuonTight2_1", againstMuonTight2_1, "againstMuonTight2_1/F")
    oTree.Branch("againstMuonTight2_2", againstMuonTight2_2, "againstMuonTight2_2/F")

    oTree.Branch("met", met, "met/F")
    oTree.Branch("mvamet", mvamet, "mvamet/F")
    oTree.Branch("mvametphi", mvametphi, "mvametphi/F")
    oTree.Branch("mvacov00", mvacov00, "mvacov00/F")
    oTree.Branch("mvacov01", mvacov01, "mvacov01/F")
    oTree.Branch("mvacov10", mvacov10, "mvacov10/F")
    oTree.Branch("mvacov11", mvacov11, "mvacov11/F")

    oTree.Branch("pzetavis", pzetavis, "pzetavis/F")
    oTree.Branch("pzetamiss", pzetamiss, "pzetamiss/F")

    oTree.Branch("pt_tt", pt_tt, "pt_tt/F")
    oTree.Branch("njets", njets, "njets/I")
    oTree.Branch("njetspt20", njetspt20, "njetspt20/I")
    oTree.Branch("nbtag", nbtag, "nbtag/I")

    oTree.Branch("jpt_1", jpt_1, "jpt_1/F")
    oTree.Branch("jeta_1", jeta_1, "jeta_1/F")
    oTree.Branch("jphi_1", jphi_1, "jphi_1/F")
    oTree.Branch("jptraw_1", jptraw_1, "jptraw_1/F")
    oTree.Branch("jptunc_1", jptunc_1, "jptunc_1/F")
    oTree.Branch("jmva_1", jmva_1, "jmva_1/F")
    oTree.Branch("jctm_1", jctm_1, "jctm_1/F")
    oTree.Branch("jpass_1", jpass_1, "jpass_1/B")    

    oTree.Branch("jpt_2", jpt_2, "jpt_2/F")
    oTree.Branch("jeta_2", jeta_2, "jeta_2/F")
    oTree.Branch("jphi_2", jphi_2, "jphi_2/F")
    oTree.Branch("jptraw_2", jptraw_2, "jptraw_2/F")
    oTree.Branch("jptunc_2", jptunc_2, "jptunc_2/F")
    oTree.Branch("jmva_2", jmva_2, "jmva_2/F")
    oTree.Branch("jctm_2", jctm_2, "jctm_2/F")
    oTree.Branch("jpass_2", jpass_2, "jpass_2/B")    

    oTree.Branch("bpt_1", bpt_1, "bpt_1/F")
    oTree.Branch("beta_1", beta_1, "beta_1/F")
    oTree.Branch("bphi_1", bphi_1, "bphi_1/F")
    oTree.Branch("bcsv_1", bcsv_1, "bcsv_1/F")
    oTree.Branch("bpt_2", bpt_2, "bpt_2/F")
    oTree.Branch("beta_2", beta_2, "beta_2/F")
    oTree.Branch("bphi_2", bphi_2, "bphi_2/F")
    oTree.Branch("bcsv_2", bcsv_2, "bcsv_2/F")
    oTree.Branch("bpt_3", bpt_3, "bpt_3/F")
    oTree.Branch("beta_3", beta_3, "beta_3/F")
    oTree.Branch("bphi_3", bphi_3, "bphi_3/F")
    oTree.Branch("bcsv_3", bcsv_3, "bcsv_3/F")

    oTree.Branch("m_bb", m_bb, "m_bb/F")    
    oTree.Branch("m_ttbb", m_ttbb, "m_ttbb/F")    

    oTree.Branch("trigweight_1", trigweight_1, "trigweight_1/F")    
    oTree.Branch("trigweight_2", trigweight_2, "trigweight_2/F")    
    oTree.Branch("effweight", effweight, "effweight/F")    

    counter = 0
    lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
    b1 = lvClass()
    b2 = lvClass()
    tau1 = lvClass()
    tau2 = lvClass()

    iBestPair = 0


    eventMask = [(194151, 365,  349335148),
(194897, 60,  108968509),
(195540, 242,  330355779),
(195774, 167,  313155930),
(196218, 602,  873479041),
(198372, 99,  70852927),
(198487, 912,  1001745316),
(198941, 186,  214469104),
(198955, 1537,  1513778727),
(199435, 1396,  1459617602),
(199608, 2133,  2018864579),
(199751, 119,  44726153),
(199804, 368,  427755387),
(199804, 594,  683424157),
(199812, 436,  520345518),
(199875, 106,  101837725),
(199967, 86,  63021254),
(199967, 129,  130023275),
(200091, 316,  383858323),
(200229, 236,  259139891),
(200473, 676,  732123594),
(200991, 580,  734298336),
(201168, 648,  703448949),
(201174, 428,  277084870),
(201278, 578,  780099013),
(201278, 1736,  1891196520),
(201613, 81,  139060604),
(201613, 451,  670507871),
(201624, 216,  293021679),
(201669, 77,  139262841),
(201678, 76,  68881519),
(201678, 111,  99728107),
(201679, 102,  86731515),
(201705, 111,  105406435),
(201707, 766,  927674406),
(201802, 235,  308762569),
(202016, 82,  94189905),
(202178, 138,  134685443),
(202237, 305,  476140228),
(202299, 505,  700039165),
(202305, 140,  131540972),
(202328, 452,  670695461),
(202504, 492,  656225868),
(202973, 498,  501843502),
(203834, 18,  13883648),
(204114, 184,  202790028),
(204553, 99,  86020028),
(204563, 523,  712514275),
(204564, 1099,  1135087262),
(204577, 1208,  1348064195),
(205158, 494,  684253208),
(205238, 40,  43256781),
(205344, 341,  385682370),
(205515, 109,  97053827),
(205526, 194,  178721945),
(205617, 165,  175483611),
(205694, 604,  591676916),
(205833, 89,  67729917),
(206088, 230,  314486221),
(206102, 207,  285425714),
(206207, 342,  511866527),
(206210, 305,  281280297),
(206210, 431,  385883083),
(206389, 241,  317955787),
(206401, 173,  232342170),
(206401, 387,  596081779),
(206446, 556,  798412205),
(206466, 317,  551862988),
(206594, 223,  319715951),
(206598, 461,  379286485),
(206745, 357,  389682970),
(206745, 434,  478670049),
(206866, 186,  194887530),
(206906, 76,  93622383),
(206940, 399,  509948850),
(207214, 332,  531426238),
(207217, 12,  11509910),
(207231, 662,  970247235),
(207269, 224,  289041330),
(207372, 426,  603356940),
(207454, 629,  926784153),
(207487, 183,  294836080),
(207515, 278,  427363837),
(207905, 213,  286127146),
(207905, 764,  1048252272),
(207920, 158,  203416421),
(207920, 172,  229795850),
(207920, 699,  1001056535),
(208307, 657,  887757961),
(208341, 412,  466131146),
(208427, 350,  554044639),
(208686, 400,  618537965),
                ]

    
    for iEntry in range(nEntries):
        track = False
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Saving to file %s.root' % (oFileName))
        iBestPair = 0#findBestPair(iTree)

        if (iTree.RUN,iTree.LUMI, iTree.EVENT,) in eventMask:
            print ''
            print 'Event: %i Lumi: %i run: %i' %(iTree.EVENT, iTree.LUMI, iTree.RUN)
            print 'pt1: %.2f pt2: %.2f CSVJ1: %.2f CSVJ2: %.2f J1Pt: %.2f J1Eta: %.2f J2Pt: %.2f J2Eta: %.2f' %(iTree.pt1.at(iBestPair), iTree.pt2.at(iBestPair), iTree.CSVJ1, iTree.CSVJ2, iTree.J1Pt, iTree.J1Eta, iTree.J2Pt, iTree.J2Eta)
            print 'iso1: %.2f iso2: %.2f charge: %.2f' %(iTree.iso1.at(iBestPair), iTree.iso2.at(iBestPair), iTree.charge1.at(iBestPair) + iTree.charge2.at(iBestPair))
            print 'svMass: %.2f mJJ: %.2f' %(iTree.svMass.at(iBestPair), iTree.mJJ)

            print 'tauTrigg1: %i' %iTree.HLT_DoubleMediumIsoPFTau35_Trk5_eta2p1_fired
            print 'tauTrigg2: %i' %iTree.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_fired
            track = True
        if not makeWholeTools2.passCut(iTree, 'pt'):
            continue

        signSelection, isoSelection, bTagSelection = makeWholeTools2.findCategory(tree = iTree,
                                                                                  iso = 1.0, 
                                                                                  option = 'pt', 
                                                                                  isData = True,
                                                                                  relaxedRegionOption = 'one1To4',
                                                                                  isEmbed = False, usePassJetTrigger = usePassJetTrigger)
        if signSelection == None  or isoSelection == None or bTagSelection == None:
            continue
        tmpSelect = signSelection+isoSelection
        if tmpSelect != cut:
            continue
        if not (cutBTag in bTagSelection):
            continue 

        trigweight_1[0] = iTree.triggerEff1
        trigweight_2[0] = iTree.triggerEff2

        effweight[0] = trigweight_1[0] * trigweight_2[0]
        nTauPairs[0] = len(iTree.pt1)
    
        run[0] = iTree.RUN
        evt[0] = iTree.EVENT
        npv[0] = iTree.vertices
        npu[0] = int(iTree.puTruth)
        lumi[0] = iTree.LUMI
        rho[0] = iTree.Rho
        mvis[0] = (tau1+tau2).mass()
        m_sv[0] = iTree.svMass.at(iBestPair)
        pt_sv[0] = iTree.svPt.at(iBestPair)
        eta_sv[0] = iTree.svEta.at(iBestPair)
        phi_sv[0] = iTree.svPhi.at(iBestPair)

        pt_1[0] = iTree.pt1.at(iBestPair)
        eta_1[0] = iTree.eta1.at(iBestPair)
        phi_1[0] = iTree.phi1.at(iBestPair)
        m_1[0] = iTree.m1.at(iBestPair)
        q_1[0] = int(iTree.charge1.at(iBestPair))
        iso_1[0] = iTree.tau1MVAIso
        mva_1[0] = 0
        byCombinedIsolationDeltaBetaCorrRaw3Hits_1[0] = iTree.iso1.at(iBestPair)
        d0_1[0] = iTree.d0_1
        dZ_1[0] = iTree.l1dz
        mt_1[0] = iTree.mt1

        pt_2[0] = iTree.pt2.at(iBestPair)
        eta_2[0] = iTree.eta2.at(iBestPair)
        phi_2[0] = iTree.phi2.at(iBestPair)
        m_2[0] = iTree.m2.at(iBestPair)
        q_2[0] = int(iTree.charge2.at(iBestPair))
        iso_2[0] = iTree.tau2MVAIso
        mva_2[0] = 0
        byCombinedIsolationDeltaBetaCorrRaw3Hits_2[0] = iTree.iso2.at(iBestPair)
        d0_2[0] = iTree.d0_2
        dZ_2[0] = iTree.l2dz
        mt_2[0] = iTree.mt2

        againstElectronMVA3raw_1[0] = iTree.againstElectronMVA3raw_1
        againstElectronMVA3raw_2[0] = iTree.againstElectronMVA3raw_2
        againstMuonLoose2_1[0] = iTree.againstMuonLoose1.at(iBestPair)
        againstMuonLoose2_2[0] = iTree.againstMuonLoose2.at(iBestPair)
        againstMuonMedium2_1[0] = iTree.againstMuonMedium2_1
        againstMuonMedium2_2[0] = iTree.againstMuonMedium2_2
        againstMuonTight2_1[0] = iTree.againstMuonTight2_1
        againstMuonTight2_2[0] = iTree.againstMuonTight2_2

        met[0] = iTree.metUnc
        mvamet[0] = iTree.met.at(iBestPair)
        mvametphi[0] = iTree.metOldphi
        mvacov00[0] = iTree.mvacov00
        mvacov01[0] = iTree.mvacov01
        mvacov10[0] = iTree.mvacov10
        mvacov11[0] = iTree.mvacov11
    
        pzetavis[0] = iTree.pZV
        pzetamiss[0] = iTree.pZetaMiss

#         pt_tt[0] = iTree.fullPt

        njets[0] = int(iTree.njets)
        njetspt20[0] = int(iTree.njetspt20)
        nbtag[0] = int(iTree.NBTags)

        bcsv_1[0] = iTree.CSVJ1
        bpt_1[0] = iTree.CSVJ1Pt
        beta_1[0] = iTree.CSVJ1Eta
        bphi_1[0] = iTree.CSVJ1Phi
        bcsv_2[0] = iTree.CSVJ2
        bpt_2[0] = iTree.CSVJ2Pt
        beta_2[0] = iTree.CSVJ2Eta
        bphi_2[0] = iTree.CSVJ2Phi

        jpt_1[0] = iTree.J1Pt
        jeta_1[0] = iTree.J1Eta
        jphi_1[0] = iTree.J1Phi
        jptraw_1[0] = iTree.J1PtUncorr
        jptunc_1[0] = iTree.J1JECUnc
        jmva_1[0] = iTree.jmva_1
        jctm_1[0] = iTree.J1Ntot
        jpass_1[0] = bool(iTree.jpass_1) 

        jpt_2[0] = iTree.J2Pt
        jeta_2[0] = iTree.J2Eta
        jphi_2[0] = iTree.J2Phi
        jptraw_2[0] = iTree.J2PtUncorr
        jptunc_2[0] = iTree.J2JECUnc
        jmva_2[0] = iTree.jmva_2
        jctm_2[0] = iTree.J2Ntot
        jpass_2[0] = bool(iTree.jpass_2)

        m_bb[0] = iTree.mJJ
#         m_ttbb[0] = iTree.HMass

        oTree.Fill()
        if track:
            print 'saved'
        counter += 1
        tool.printProcessStatus(iEntry, nEntries, 'Saving to file ')
    
    print ''
    print '%i events saved' %counter
    oFile.cd()
    oTree.Write()
    oFile.Close()
    print 'Saved file: %s.root' %oFileName

# def opts():
#     parser = optparse.OptionParser("Usage: %prog /path/to/ntuples/ [options]")
#     parser.add_option("--cut", dest="cut", default=False, action="store_true", help="apply cuts")
#     defTree = "ttTreeBeforeChargeCut/eventTree"
#     parser.add_option("--treepath", dest="treepath", default=defTree, help="TDirectory/name of TTree (default is %s)" % defTree)
#     options, args = parser.parse_args()
# 
#     if len(args) != 1:
#         parser.print_help()
#         exit()
#     return args[0], options
# location, options = opts()


# makeSyncNtuples('/hdfs/store/user/zmao/H2hh300_NoType1-SUB-TT')
# makeSyncNtuples('/hdfs/store/user/zmao/H2hh300_syncNew-SUB-TT')
# makeSyncNtuples('/hdfs/store/user/zmao/H2hh300_newCalibMet-SUB-TT')
# makeSyncNtuples('/hdfs/store/user/zmao/H2hh300_newMET-SUB-TT')
# makeSyncNtuples('/hdfs/store/user/zmao/H2hh300_newPhilHMetCalib-SUB-TT', True, "TauCheck/eventTree")
# makeSyncNtuples('/hdfs/store/user/zmao/nt_H2hh300_up-SUB-TT', False, "ttTreeBeforeChargeCut/eventTree")
# makeSyncNtuples('/nfs_scratch/zmao/fromLogin05/embedSync/DY_embed_v9.root', False, "eventTree")
# makeSyncNtuples('/nfs_scratch/zmao/fromLogin05/looseCSV2/tt_embed_v11_all.root', False, "eventTree")
# makeSyncNtuples('/nfs_scratch/zmao/fromLogin05/looseCSV2/DY_embed_v12.root', False, "eventTree")

# makeSyncNtuples('/nfs_scratch/zmao/fromLogin05/looseCSV2/tt_all.root', False, "eventTree")
# makeSyncNtuples('/nfs_scratch/zmao/fromLogin05/looseCSV2/dataA_doublemu_emb_v12_tauShift_all.root', False, "eventTree")
# makeSyncNtuples('/nfs_scratch/zmao/samples/data_embed/DY_embed.root', False, "eventTree")
# makeSyncNtuples('/nfs_scratch/zmao/samples/tauESOff/normal/tt_embed_all.root', False, "eventTree")
usePassJetTrigger = True
# makeSyncNtuples('/nfs_scratch/zmao/samples/data/data.root', 'OSRelax','1M', "eventTree", usePassJetTrigger)
# makeSyncNtuples('/nfs_scratch/zmao/samples/data/data.root', 'OSRelax','2M', "eventTree", usePassJetTrigger)
makeSyncNtuples('/nfs_scratch/zmao/samples/data_new/data.root', 'SSRelax','1L', "eventTree", usePassJetTrigger)
# makeSyncNtuples('/nfs_scratch/zmao/samples/data/data.root', 'SSRelax','2L', "eventTree", usePassJetTrigger)
# makeSyncNtuples('/nfs_scratch/zmao/samples/data/data.root', 'SSTight','1L', "eventTree", usePassJetTrigger)
# makeSyncNtuples('/nfs_scratch/zmao/samples/data/data.root', 'SSTight','2L', "eventTree", usePassJetTrigger)
# makeSyncNtuples('/nfs_scratch/zmao/samples/tauESOff/normal/tthad_all.root', False, "eventTree")
# makeSyncNtuples('/nfs_scratch/zmao/samples/tauESOff/normal/tt_all.root', False, "eventTree")

# makeSyncNtuples('/hdfs/store/user/zmao/nt_tauP_D_v7-SUB-TT-data', False, "ttTreeBeforeChargeCut/eventTree")
# makeSyncNtuples('/hdfs/store/user/elaird/nt_tauP_C_v3-SUB-TT-data', False, "ttTreeBeforeChargeCut/eventTree")

# makeSyncNtuples(location, options.cut, options.treepath)
