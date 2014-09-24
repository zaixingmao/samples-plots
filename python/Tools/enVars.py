signalEntries = 0
ttEntries = 0
ZZEntries = 0


sampleLocations = [
#                     ("H2hh260",  "/hdfs/store/user/zmao/H2hh260_newMET-SUB-TT"), 
                    ("H2hh300",  "/hdfs/store/user/zmao/H2hh300_newMET-SUB-TT"),
#                     ("H2hh350",  "/hdfs/store/user/zmao/H2hh350_newMET-SUB-TT"),
#                     ("tt_eff", "/hdfs/store/user/zmao/tt_newMET-SUB-TT"),
#                     ("ZZ_eff", "/hdfs/store/user/zmao/ZZ_newMET-SUB-TT"),
#                     ("tt_semi_eff", "/hdfs/store/user/zmao/tt_SemiLep_newMET-SUB-TT"),
#                     ('QCD_Pt-30to50', '/hdfs/store/user/zmao/QCD_Pt-30to50_newMET-SUB-TT'),
#                     ('QCD_Pt-50to80', '/hdfs/store/user/zmao/QCD_Pt-50to80_newMET-SUB-TT'),
#                     ('QCD_Pt-80to120', '/hdfs/store/user/zmao/QCD_Pt-80to120_newMET-SUB-TT'),
#                     ('QCD-120to170', '/hdfs/store/user/zmao/QCD_Pt-120to170_newMET-SUB-TT'),
#                     ('QCD_Pt-30To50_bEnriched', '/hdfs/store/user/zmao/QCD_Pt-30To50_bEnriched_newMET-SUB-TT'),
#                     ('QCD_Pt-50To150_bEnriched', '/hdfs/store/user/zmao/QCD_Pt-50To150_bEnriched_newMET-SUB-TT'),
#                     ('QCD_Pt-150_bEnriched', '/hdfs/store/user/zmao/QCD_Pt-150_bEnriched_newMET-SUB-TT'),
#                     ('dataA', '/hdfs/store/user/zmao/Tau_Run2012A_newMET2-SUB-TT-data/'),
#                     ('dataB', '/hdfs/store/user/zmao/TauParked_Run2012B_newMET2-SUB-TT-data/'),
#                     ('dataC', '/hdfs/store/user/zmao/TauParked_Run2012C_newMET3-SUB-TT-data/'),
#                     ('dataD', '/hdfs/store/user/zmao/TauParked_Run2012D_newMET3-SUB-TT-data/'),
#                     ('dataTotal', '/scratch/zmao/relaxed_regression4/data' ),
#                     ('QCDtotal', '/scratch/zmao/QCD/qcd' ),
#                     ('QCDtotal_bEnriched', '/scratch/zmao/QCD/bEnriched' ),
#                     ('DYJetsToLL_eff', '/hdfs/store/user/zmao/DYJetsToLL_newMET-SUB-TT'),
#                     ('DY1JetsToLL_eff2', '/hdfs/store/user/zmao/DY1JetsToLL_newMET2-SUB-TT'),
#                     ('DY2JetsToLL_eff2', '/hdfs/store/user/zmao/DY2JetsToLL_newMET2-SUB-TT'),
#                     ('DY3JetsToLL_eff2', '/hdfs/store/user/zmao/DY3JetsToLL_newMET2-SUB-TT'),
#                     ('W1JetsToLNu_eff2', '/hdfs/store/user/zmao/W1JetsToLNu_newMET2-SUB-TT'),
#                     ('W2JetsToLNu_eff2', '/hdfs/store/user/zmao/W2JetsToLNu_newMET-SUB-TT'),
#                     ('W3JetsToLNu_eff2', '/hdfs/store/user/zmao/W3JetsToLNu_newMET-SUB-TT'),
#                     ('WZJetsTo2L2Q_eff', '/hdfs/store/user/zmao/WZJetsTo2L2Q_newMET-SUB-TT'),
#                     ('H2hh300', '/hdfs/store/user/zmao/H2hh300_pt20WithInit-SUB-TT'),
#                       ('VBF_HToTauTau', '/hdfs/store/user/zmao/VBF_HToTauTau-SUB-TT'),
#                       ('TTJets_MSDecays', '/hdfs/store/user/zmao/TTJets_MSDecays-SUB-TT'),
#                       ('GluGluToHToTauTau', '/hdfs/store/user/zmao/GluGluToHToTauTau-SUB-TT'),
#                       ('WH_ZH_TTH_HToTauTau', '/hdfs/store/user/zmao/WH_ZH_TTH_HToTauTau-SUB-TT'),
#                     ("H2hh300",  "/hdfs/store/user/zmao/H2hh300_syncNew-SUB-TT"),
#                     ("H2hh300_newTauID", "/hdfs/store/user/zmao/H2hh300_newTauID-SUB-TT"),
                  ]


vecVarList = ['pt1', 'pt2', 'iso1', 'iso2', 'eta1', 'eta2', 'phi1', 'phi2', 'svEta', 'svMass', 'svPhi', 'svPt']

corruptedROOTfiles = []
