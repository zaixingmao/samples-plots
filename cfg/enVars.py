jetPtThreshold = 20
corruptedROOTfiles = []

preFix2 = '/hdfs/store/user/zmao/Spring15_eletronID2/'
preFix3 = '/hdfs/store/user/zmao/sync_combined_take3/'
preFix = '/hdfs/store/user/zmao/MC_25ns/'
preFix3 = '/hdfs/store/user/zmao/Spring15_eletronID/'
# preFix3 = '/hdfs/store/user/zmao/noElectronIDCut/'
preFix4 = '/hdfs/store/user/zmao/newSplitting_noChargeMatch/'



type = 'baseline'     #selection type (baseline, inclusive)
category = 'all'       #ZLL splitting (all, ZTT, ZL, ZJ)
pairChoice = 'iso'     #pair selection method (iso, pt)

sampleLocations = [
#                     ("VBF_H",     "%sVBF_HToTauTau_M-125_13TeV-powheg-pythia6" %(preFix), 1000),
#                    ("DY",     "%s/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix3), 6025, 'et'),
#                     ("DY-10to50",     "%s/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix), 18610),
#                     ("data_Tau",     "/hdfs/store/user/zmao/data_25ns_Spring15_eletronID2/data_Tau_Run2015C_PromptReco_25ns", 1, 'tt'),
#                     ("data_MuonEG",     "/hdfs/store/user/zmao/data_25ns_Spring15_eletronID2/data_MuonEG_Run2015C_PromptReco_25ns", 1, 'em'),
#                    ("data_Muon",     "/hdfs/store/user/zmao/data_25ns_Spring15_eletronID2/data_Muon_Run2015C_PromptReco_25ns", 1, 'mt'),
#                     ("data_Electron",     "/hdfs/store/user/zmao/noElectronIDCut/data_Electron_Run2015C_PromptReco_25ns", 1, 'et'),
#                     ("TTJets",     "%s/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix3), 831.76, ''),
#                     ("WJets",     "%s/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix3), 61526.7, 'et'),
#                     ("WW",     "%s/WW_TuneCUETP8M1_13TeV-pythia8" %(preFix3), 63.21, ''),
#                     ("WZ",     "%s/WZ_TuneCUETP8M1_13TeV-pythia8" %(preFix3), 22.82, ''),
#                     ("ZZ",     "%s/ZZ_TuneCUETP8M1_13TeV-pythia8" %(preFix3), 10.32, ''),
#                     ("T",     "%s/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix3), 35.6, ''),
#                     ("antiT",     "%s/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix3), 35.6, ''),
#                      ("T-tchannel",     "%s/ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 103.02),
#                      ("antiT-tchannel",     "%s/ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 80.95),
#                      ("SUSY", "/nfs_scratch/zmao/susy_1file/", 1, ''),

#                     ("ZPrime_500",     "%s/ZprimeToTauTau_M_500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_1000",     "%s/ZprimeToTauTau_M_1000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_1500",     "%s/ZprimeToTauTau_M_1500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_2000",     "%s/ZprimeToTauTau_M_2000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_2500",     "%s/ZprimeToTauTau_M_2500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_3000",     "%s/ZprimeToTauTau_M_3000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_3500",     "%s/ZprimeToTauTau_M_3500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_4000",     "%s/ZprimeToTauTau_M_4000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_4500",     "%s/ZprimeToTauTau_M_4500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),
#                     ("ZPrime_5000",     "%s/ZprimeToTauTau_M_5000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix2), 1, ''),


                     ("SUSY", "%sSUSYGluGluToHToTauTau_M-160_TuneCUETP8M1_13TeV-pythia8"  %(preFix4), 1, ''),
#                      ("VBF_H",     "/nfs_scratch/zmao/tmp/72x", 1000),
#                      ("VBF_H_74x",     "/nfs_scratch/zmao/tmp/74x", 1000),
#     ("TTJets",     "%sTTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola" %(preFix), 424500),
#                     ("DYJetsToLL",     "%sDYJetsToLL_M-50_13TeV-madgraph-pythia8-tauola_v2" %(preFix), 5482000),
#                     ("H2hh280%s" %postName,     "%sH2hh280%s" %(preFix, postFix), 1000),
#                     ("H2hh290%s" %postName,     "%sH2hh290%s" %(preFix, postFix), 1000),
#                     ("H2hh300%s" %postName,     "%sH2hh300%s" %(preFix, postFix), 1000),
#                     ("H2hh310%s" %postName,     "%sH2hh310%s" %(preFix, postFix), 1000),
#                     ("H2hh320%s" %postName,     "%sH2hh320%s" %(preFix, postFix), 1000),
#                     ("H2hh330%s" %postName,     "%sH2hh330%s" %(preFix, postFix), 1000),
#                     ("H2hh340%s" %postName,     "%sH2hh340%s" %(preFix, postFix), 1000),
#                     ("H2hh350%s" %postName,     "%sH2hh350%s" %(preFix, postFix), 1000),
#  #                    ("H2hh500%s" %postName,     "%sH2hh500_rad%s" %(preFix2, postFix), 1000),
#                     ("H2hh700%s" %postName,     "%sH2hh700_rad%s" %(preFix2, postFix), 1000),
#                     ("H2hh1000%s" %postName,     "%sH2hh1000_rad%s" %(preFix2, postFix), 1000),

#                     ('VBF_HToTauTau', "%svbf%s" %(preFix, postFix), 1000),
#                     ('GluGluToHToTauTau',  "%sggh%s" %(preFix, postFix), 1000),
#                     ('WH_ZH_TTH_HToTauTau', "%svh_tth%s" %(preFix, postFix), 1000),

#                    ("tt%s" %postName,      "%sttfull%s" %(preFix, postFix), 26197.5),
#                    ("tt_semi%s" %postName, "%sttsemi%s" %(preFix, postFix), 109281),
#                    ("tthad%s" %postName, "%stthad%s" %(preFix, postFix), 114021.5),
#                    ('tbar%s' %postName, "%stbar%s" %(preFix, postFix), 11100.0),
#                    ('t%s' %postName, "%st%s" %(preFix, postFix), 11100.0),

# 
#                    
#                     ('dataA2', '/hdfs/store/user/elaird/nt_tau_A_test_rerun_jets-SUB-TT-data/', 1),
# 
 #                    ('dataA', '/hdfs/store/user/zmao/nt_tau_A_triggerFix-SUB-TT-data/', 1),
#                     ('dataB', '/hdfs/store/user/zmao/nt_tauP_B_triggerFix-SUB-TT-data/', 1),
#                     ('dataC', '/hdfs/store/user/zmao/nt_tauP_C_triggerFix-SUB-TT-data/', 1),
#                     ('dataD', '/hdfs/store/user/zmao/nt_tauP_D_triggerFix-SUB-TT-data/', 1),

# 
#                     ('dataA_doublemu_emb', '%sdoublemu_emb_A%s-data' %(preFix,postFix), 1),
#                     ('dataB_doublemu_emb', '%sdoublemu_emb_B%s-data' %(preFix,postFix), 1),
#                     ('dataC_doublemu_emb', '%sdoublemu_emb_C%s-data' %(preFix,postFix), 1),
#                     ('dataD_doublemu_emb', '%sdoublemu_emb_D%s-data' %(preFix,postFix), 1),
#                     ('tt_embed', '/hdfs/store/user/zmao/nt_ttjets_fulllept_emb%s/' %(postFix), 26197.5),
# 
#                      ('DYJetsToLL%s' %postName, "%sdy%s" %(preFix, postFix), 3504000),
#                      ('DY1JetsToLL%s' %postName, "%sdy1%s" %(preFix, postFix), 561000),
#                      ('DY2JetsToLL%s' %postName, "%sdy2%s" %(preFix, postFix), 181000),
#                      ('DY3JetsToLL%s' %postName, "%sdy3%s" %(preFix, postFix), 51100),
#                      ('DY4JetsToLL%s' %postName, "%sdy4%s" %(preFix, postFix), 23000),
# # 
#                    ('WJetsToLNu%s' %postName, "%swjets%s" %(preFix, postFix), 36257000),
#                    ('W1JetsToLNu%s' %postName, "%sw1%s" %(preFix, postFix), 5400000),
#                    ('W2JetsToLNu%s' %postName, "%sw2%s" %(preFix, postFix), 1750000),
#                    ('W3JetsToLNu%s' %postName, "%sw3%s" %(preFix, postFix), 519000),
#                    ('W4JetsToLNu%s' %postName, "%sw4%s" %(preFix, postFix), 214000),

#                ("ZZ%s" %postName,      "%szz%s" %(preFix, postFix), 2500),
 #               ('WZJetsTo2L2Q%s' %postName, "%swz%s" %(preFix, postFix), 2207),
#                ('zzTo4L%s' %postName, "%szzTo4L%s" %(preFix, postFix), 181.0),
#                ('zzTo2L2Nu%s' %postName, "%szzTo2L2Nu%s" %(preFix, postFix), 716.0),
#                ('WW%s' %postName, "%sww%s" %(preFix, postFix), 5824.0),
#                ('WZ3L%s' %postName, "%swz3L%s" %(preFix, postFix), 1058.0),

#                     ('wbbj%s' %postName, "%swbbj%s" %(preFix2, postFix), 0),


# 


#                     ('QCD_Pt-30to50', '/hdfs/store/user/zmao/QCD_Pt-30to50_newMET-SUB-TT'),
#                     ('QCD_Pt-50to80', '/hdfs/store/user/zmao/QCD_Pt-50to80_newMET-SUB-TT'),
#                     ('QCD_Pt-80to120', '/hdfs/store/user/zmao/QCD_Pt-80to120_newMET-SUB-TT'),
#                     ('QCD-120to170', '/hdfs/store/user/zmao/QCD_Pt-120to170_newMET-SUB-TT'),
#                     ('QCD_Pt-30To50_bEnriched', '/hdfs/store/user/zmao/QCD_Pt-30To50_bEnriched_newMET-SUB-TT'),
#                     ('QCD_Pt-50To150_bEnriched', '/hdfs/store/user/zmao/QCD_Pt-50To150_bEnriched_newMET-SUB-TT'),
#                     ('QCD_Pt-150_bEnriched', '/hdfs/store/user/zmao/QCD_Pt-150_bEnriched_newMET-SUB-TT'),
#                     ('QCDtotal', '/scratch/zmao/QCD/qcd' ),
#                     ('QCDtotal_bEnriched', '/scratch/zmao/QCD/bEnriched' ),


#                       ('TTJets_MSDecays', '/hdfs/store/user/zmao/TTJets_MSDecays-SUB-TT'),
#                       ('WH_ZH_TTH_HToTauTau', '/hdfs/store/user/zmao/WH_ZH_TTH_HToTauTau-SUB-TT'),
#                     ("H2hh300",  "/hdfs/store/user/zmao/H2hh300_syncNew-SUB-TT"),
#                     ("H2hh300_newTauID", "/hdfs/store/user/zmao/H2hh300_newTauID-SUB-TT"),
                  ]
