jetPtThreshold = 20
corruptedROOTfiles = []

preFix = '/hdfs/store/user/zmao/nt_'
preFix2 = '/hdfs/store/user/elaird/nt_'

# postFix = '_shift-SUB-TT'
# postFix = '_tauESOff_tauShift-SUB-TT'
postFix = '_tauESOn_tauShift-SUB-TT'

postName = ""
wScale = 36257.0/30400.0
dyScale = 3504.0/2950.0

dyScale1 = 1.14624922102
dyScale2 = 1.19530260886
dyScale3 = 1.25041471383
dyScale4 = 1.27550090492

sampleLocations = [# ("H2hh260%s" %postName,     "%sH2hh260%s" %(preFix, postFix), 1000),
#                     ("H2hh270%s" %postName,     "%sH2hh270%s" %(preFix, postFix), 1000),
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
#                     ("tt%s" %postName,      "%sttfull%s" %(preFix, postFix), 26197.5),
#                     ("tt_semi%s" %postName, "%sttsemi%s" %(preFix, postFix), 109281),
#                     ("tthad%s" %postName, "%stthad%s" %(preFix, postFix), 114021.5),
#                     ('tbar%s' %postName, "%stbar%s" %(preFix, postFix), 11100.0),
#                     ('t%s' %postName, "%st%s" %(preFix, postFix), 11100.0),

# 
#                    
#                     ('dataA2', '/hdfs/store/user/elaird/nt_tau_A_test_rerun_jets-SUB-TT-data/', 1),
# 
                    ('dataA', '/hdfs/store/user/zmao/nt_tau_A_triggerFix-SUB-TT-data/', 1),
#                     ('dataB', '/hdfs/store/user/zmao/nt_tauP_B_rightJetMVA-SUB-TT-data/', 1),
#                     ('dataC', '/hdfs/store/user/zmao/nt_tauP_C_rightJetMVA-SUB-TT-data/', 1),
#                     ('dataD', '/hdfs/store/user/zmao/nt_tauP_D_rightJetMVA2-SUB-TT-data/', 1),

# 
#                     ('dataA_doublemu_emb', '%sdoublemu_emb_A%s-data' %(preFix,postFix), 1),
#                     ('dataB_doublemu_emb', '%sdoublemu_emb_B%s-data' %(preFix,postFix), 1),
#                     ('dataC_doublemu_emb', '%sdoublemu_emb_C%s-data' %(preFix,postFix), 1),
#                     ('dataD_doublemu_emb', '%sdoublemu_emb_D%s-data' %(preFix,postFix), 1),
#                     ('tt_embed', '/hdfs/store/user/zmao/nt_ttjets_fulllept_emb%s/' %(postFix), 26197.5),

#                     ('dataA_doublemu_emb_rerun', '/hdfs/store/user/elaird/nt_doublemu_emb_A_emb_v4_rerun-SUB-TT-data/', 1),
#                     ('dataB_doublemu_emb_rerun', '/hdfs/store/user/elaird/nt_doublemu_emb_B_emb_v4_rerun-SUB-TT-data/', 1),
#                     ('dataC_doublemu_emb_rerun', '/hdfs/store/user/elaird/nt_doublemu_emb_C_emb_v4_rerun-SUB-TT-data/', 1),
#                     ('dataD_doublemu_emb_rerun', '/hdfs/store/user/elaird/nt_doublemu_emb_D_emb_v4_rerun-SUB-TT-data/', 1),

#                    ('dataTotal', '/nfs_scratch/zmao/fromLogin05/dataWithLumiMask/data/', 1),
#                    ('doublemu_emb_noRerun', '/nfs_scratch/zmao/fromLogin05/dataWithLumiMask/doublemu_emb_noRerun/', 1),
#                    ('doublemu_emb_rerun', '/nfs_scratch/zmao/fromLogin05/dataWithLumiMask/doublemu_emb_rerun/', 1),

#                     ('DYJetsToLL%s' %postName, "%sdy%s" %(preFix, postFix), 3504000),
#                     ('DY1JetsToLL%s' %postName, "%sdy1%s" %(preFix, postFix), 561000*dyScale1),
#                     ('DY2JetsToLL%s' %postName, "%sdy2%s" %(preFix, postFix), 181000*dyScale2),
#                     ('DY3JetsToLL%s' %postName, "%sdy3%s" %(preFix, postFix), 51100*dyScale3),
#                     ('DY4JetsToLL%s' %postName, "%sdy4%s" %(preFix, postFix), 23000*dyScale4),
# 
#                     ('W1JetsToLNu%s' %postName, "%sw1%s" %(preFix, postFix), 5400000*wScale),
#                     ('W2JetsToLNu%s' %postName, "%sw2%s" %(preFix, postFix), 1750000*wScale),
#                     ('W3JetsToLNu%s' %postName, "%sw3%s" %(preFix, postFix), 519000*wScale),
#                     ('W4JetsToLNu%s' %postName, "%sw4%s" %(preFix, postFix), 214000*wScale),
# 
#                     ("ZZ%s" %postName,      "%szz%s" %(preFix, postFix), 2500),
#                     ('WZJetsTo2L2Q%s' %postName, "%swz%s" %(preFix, postFix), 2207),
#                     ('zzTo4L%s' %postName, "%szzTo4L%s" %(preFix, postFix), 181.0),
#                     ('zzTo2L2Nu%s' %postName, "%szzTo2L2Nu%s" %(preFix, postFix), 716.0),
#                     ('WW%s' %postName, "%sww%s" %(preFix, postFix), 5824.0),
#                     ('WZ3L%s' %postName, "%swz3L%s" %(preFix, postFix), 1058.0),

#                     ('wbbj%s' %postName, "%swbbj%s" %(preFix2, postFix), 0),


# 
#                     ('VBF_HToTauTau', "%svbf%s" %(preFix, postFix)),
#                     ('GluGluToHToTauTau',  "%sggh%s" %(preFix, postFix)),

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
