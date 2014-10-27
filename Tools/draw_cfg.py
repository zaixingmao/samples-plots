import ROOT as r


drawConfigs = {'script': 'drawVarsData_KS_CheckFlat.py',
               #'sampleLocation': '/scratch/zmao/relaxed_regression4/TMVARegApp_',
               'sampleLocation': '/nfs_scratch/elaird/zm-old/',
               'signal': 'H260'}

SamplePreFix = drawConfigs['sampleLocation']

MCFileList = [#('ZZ', SamplePreFix + 'ZZ_eff_all.root', 2500, 5),
              #('WZJetsTo2L2Q', SamplePreFix + 'WZJetsTo2L2Q_eff_all.root', 2207, 5),
              #('W1JetsToLNu', SamplePreFix + 'W1JetsToLNu_eff2_all.root', 5400000, r.kMagenta-9),
              #('W2JetsToLNu', SamplePreFix + 'W2JetsToLNu_eff2_all.root', 1750000, r.kMagenta-9),
              #('W3JetsToLNu', SamplePreFix + 'W3JetsToLNu_eff2_all.root', 519000, r.kMagenta-9),
              ##('DYJetsToLL', 'TMVARegApp_DYJetsToLL_eff_all.root', 3504000, r.kGreen-7),
              #('DY1JetsToLL', SamplePreFix + 'DY1JetsToLL_eff2_all.root', 561000, r.kGreen-7),
              #('DY2JetsToLL', SamplePreFix + 'DY2JetsToLL_eff2_all.root', 181000, r.kGreen-7),
              #('DY3JetsToLL', SamplePreFix + 'DY3JetsToLL_eff2_all.root', 51100, r.kGreen-7),
              ('tt_full_lep',SamplePreFix + 'tt_eff_all.root', 26197.5, r.kRed-7),
              ('tt_semi_lep',SamplePreFix + 'tt_semi_eff_all.root', 109281, r.kAzure+7),]

singalPreFix = SamplePreFix
signalDict = {'H260': (singalPreFix + 'H2hh260_all.root', 14.76),
              'H300': (singalPreFix + 'H2hh300_all.root', 15.9),
              'H350': (singalPreFix + 'H2hh350_all.root', 8.57)}

dataFile = SamplePreFix + 'dataTotal_all.root'

varsRange = { 
    #varName: (nbins, minX, maxX, yMax, signalBoostFactor, logY, predict)
#             'fMass': (10, 200, 800, 30, 100, False, True),
#             'pt2': (12, 30, 150, 10000, 100, True, True, 'GeV'),
#              'tightPt': (20, 0, 400, 10000, 100, True, True),
#              'relaxPt': (20, 0, 400, 10000, 100, True, True),
#             'pt1pt2': (20, 0, 500, 10000, 100, True, True),
#             'iso1':(25, 0, 10, 20000, 600, True, True),
#             'iso2':(25, 0, 10, 20000, 600, True, True),
#             'eta1': (20, -3.14, 3.14, 50000, 100, True, True), 
#             'eta2': (20, -3.14, 3.14, 50000, 100, True, True), 
#             'phi1': (20, -3.14, 3.14, 50000, 100, True, True, 'rad'), 
#             'phi2': (20, -3.14, 3.14, 50000, 100, True, True, 'rad'), 
#             'NBTags': (6, 0, 5, 2000, 100, True, True), 
#             'J1CSVbtag': (12, 0, 1.2, 100000, 100, True, True),
#             'J1Eta': (20, -3.14, 3.14, 50000, 100, True, True),
#             'J1Pt': (20, 0, 400, 30000, 100, True, True),
#             'J2CSVbtag': (12, 0, 1.2, 100000, 100, True, True),
#             'J2Eta': (20, -3.14, 3.14, 50000, 100, True, True),
#             'J2Pt': (15, 0, 250, 10000, 100, True, True),
#             'J3CSVbtag':(12, 0, 1.2, 50000, 100, True, True),
#            'J3Eta': (20, -3.14, 3.14, 50000, 100, True, True),
#             'J3Pt': (15, 0, 250, 5000, 100, True, True),
#             'J4CSVbtag':(12, 0, 1.2, 50000, 100, True, True),
#             'J4Eta': (20, -3.14, 3.14, 10000, 100, True, True),
#             'J4Pt': (15, 0, 250, 5000, 100, True, True),
#             'svMass': (10, 0, 400, 40, 100, False, True),
#             'svPt': (10, 0, 600, 50, 100, False, True),
#              'mJJ': (15, 80, 150, 30000, 100, True, True),
#              'mJJReg': (10, 50, 200, 20, 100, False, True),
#              'met': (10, 0, 150, 30, 100, False, True),
#             'ptJJ': (15, 0, 600, 5000, 100, True, True),
#             'etaJJ': (20, -3.14, 3.14, 50000, 100, True, True),
#             'dPhiMetTau1': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetTau2': (8, 0, 3.14, 20, 100, False, True),
#             'dPhiMetJet1': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetJet2': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetTauPair': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetJetPair': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetSVTauPair': (8, 0, 3.14, 60, 100, False, True),
#             'dRTauTau': (10, 0, r.TMath.Pi(), 60, 100, False, True), 
#             'dPhiTauTau': (20, 0, r.TMath.Pi(), 5000, 500, True, True), 
#             'dEtaTauTau': (20, 0, r.TMath.Pi(), 5000, 500, True, True), 
#             'dRJJ': (10, 0, 6.28, 60, 100, False, True),
#             'dRhh': (10, 0, 6.28, 60, 100, False, True),
#             'BDT_EWK': (20, -1., 1., 10000, 100, True, True),
#             'BDT_QCD': (20, -1., 1., 10000, 100, True, True),
#             'BDT_both': (20, -1., 1., 30, 100, False, True, 'binWidth'),
#             'nTauPairs': (5, 0, 5, 10000, 100, True, True),
#             'CSVJ1': (10, 0.6, 1.2, 60, 100, False, True),
#             'CSVJ2': (10, 0.2, 1.2, 30, 100, False, True),
#             'fMass': (20, 150, 550, 20, 100, False, True),
             'fMassKinFit': (20, 150, 550, 20, 100, False, True),
#            'byIsolationMVA2raw_1': (20, -1., 1., 20, 100, False, True),
#            'byIsolationMVA2raw_2': (20, -1., 1., 20, 100, False, True),
            }
