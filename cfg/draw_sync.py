import ROOT as r

signal = '350'

drawConfigs = {'script': 'drawVarsData_KS_CheckFlat_sync.py',
               'sampleLocation': '/scratch/zmao/forPlots/',
#                'sampleLocation': '/scratch/zmao/newKinFit/8/350/ClassApp_both_TMVARegApp_',
               'signal': 'H%s' %signal}

SamplePreFix = drawConfigs['sampleLocation']

MCFileList = [('Electroweak', SamplePreFix + 'Electroweak.root', r.kRed-6),
              ('DYJetsToLL', SamplePreFix + 'DYJetsToLL_all.root', r.kOrange),
              ('t#bar{t}',SamplePreFix + 'tt.root', r.kBlue-8)]

singalPreFix = SamplePreFix
signalDict = {'H260': (singalPreFix + 'H2hh260_all.root'),
              'H270': (singalPreFix + 'H2hh270_all.root'),
              'H280': (singalPreFix + 'H2hh280_all.root'),
              'H290': (singalPreFix + 'H2hh290_all.root'),
              'H300': (singalPreFix + 'H2hh300_all.root'),
              'H310': (singalPreFix + 'H2hh310_all.root'),
              'H320': (singalPreFix + 'H2hh320_all.root'),
              'H330': (singalPreFix + 'H2hh330_all.root'),
              'H340': (singalPreFix + 'H2hh340_all.root'),
              'H350': (singalPreFix + 'H2hh350_all.root')}

dataFile = SamplePreFix + 'dataTotal_all.root'

varsRange = { 
    #varName: (nbins, minX, maxX, yMax, signalBoostFactor, logY, predict)
#             'fMass': (10, 200, 800, 30, 100, False, True),
#            'nPairs': (5, 0, 5, 10000, 100, True, True, ''),

            'pt1': (20, 30, 150, 500000, 1, True, True, 'GeV'),
#             'pt2': (20, 30, 150, 50000, 100, True, True, 'GeV'),
#              'tightPt': (20, 0, 400, 10000, 100, True, True),
#              'relaxPt': (20, 0, 400, 10000, 100, True, True),
#             'pt1pt2': (20, 0, 500, 10000, 100, True, True),
#             'iso1':(25, 0, 10, 20000, 600, True, True),
#             'iso2':(25, 0, 10, 20000, 600, True, True),
#             'eta1': (30, -3.14, 3.14, 50000, 100, True, True), 
#             'eta2': (30, -3.14, 3.14, 50000, 100, True, True), 
#             'phi1': (20, -3.14, 3.14, 50000, 100, True, True, 'rad'), 
#             'phi2': (20, -3.14, 3.14, 50000, 100, True, True, 'rad'), 
#             'NBTags': (6, 0, 5, 2000, 100, True, True), 
#             'J1CSVbtag': (12, 0, 1.2, 100000, 100, True, True),
#             'CSVJ1Eta': (30, -3.14, 3.14, 50000, 100, True, True),
            'CSVJ1Pt': (20, 0, 400, 500000, 1, True, True),
#             'J2CSVbtag': (12, 0, 1.2, 100000, 100, True, True),
#             'CSVJ2Eta': (30, -3.14, 3.14, 50000, 100, True, True),
#             'CSVJ2Pt': (20, 0, 250, 50000, 100, True, True),
#             'J3CSVbtag':(12, 0, 1.2, 50000, 100, True, True),
#            'J3Eta': (20, -3.14, 3.14, 50000, 100, True, True),
#             'J3Pt': (15, 0, 250, 5000, 100, True, True),
#             'J4CSVbtag':(12, 0, 1.2, 50000, 100, True, True),
#             'J4Eta': (20, -3.14, 3.14, 10000, 100, True, True),
#             'J4Pt': (15, 0, 250, 5000, 100, True, True),
             'svMass': (30, 0, 450, 500000, 1, True, True),
#             'svPt': (10, 0, 600, 50, 100, False, True),
             'mJJ': (20, 0, 300, 300000, 1, True, True),
#              'mJJReg': (10, 50, 200, 20, 100, False, True),
             'met': (20, 0, 150, 500000, 1, True, True),
#             'ptJJ': (15, 0, 600, 5000, 100, True, True),
#             'etaJJ': (20, -3.14, 3.14, 50000, 100, True, True),
#             'dPhiMetTau1': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetTau2': (8, 0, 3.14, 20, 100, False, True),
#             'dPhiMetJet1': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetJet2': (8, 0, 3.14, 30, 100, False, True),
#             'dPhiMetTauPair': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetJetPair': (8, 0, 3.14, 60, 100, False, True),
#             'dPhiMetSVTauPair': (8, 0, 3.14, 60, 100, False, True),
#             'dRTauTau': (10, 0, r.TMath.Pi(), 35, 100, False, True), 
#             'dPhiTauTau': (20, 0, r.TMath.Pi(), 5000, 500, True, True), 
#             'dEtaTauTau': (20, 0, r.TMath.Pi(), 5000, 500, True, True), 
#             'dRJJ': (10, 0, 2*r.TMath.Pi(), 10000, 100, True, True),
#             'dRhh': (10, 0, 6.28, 60, 100, False, True),
#             'BDT_EWK': (20, -1., 1., 10000, 100, True, True),
#             'BDT_QCD': (20, -1., 1., 10000, 100, True, True),
#             'BDT_both': (10, -1., 1., 500000, 300, True, True, 'binWidth'),
#             'nTauPairs': (5, 0, 5, 10000, 100, True, True),
#             'CSVJ1': (20, 0.5, 1.0, 50000, 100, True, True),
#             'CSVJ2': (20, 0.0, 1.0, 50000, 100, True, True),
#             'fMass': (15, 100, 1000, 20000, 100, True, True),
#              'fMassKinFit': (21, -30, 600, 50, 100, False, True),
#              'chi2KinFit2': (11, 0, 220, 50, 100, False, True),

#            'byIsolationMVA2raw_1': (20, -1., 1., 20, 100, False, True),
#            'byIsolationMVA2raw_2': (20, -1., 1., 20, 100, False, True),
            }
