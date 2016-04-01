jetPtThreshold = 20
corruptedROOTfiles = []

preFix2 = '/hdfs/store/user/zmao/Spring15_eletronID2/'
preFix3 = '/hdfs/store/user/zmao/sync_combined_take3/'
preFix = '/hdfs/store/user/zmao/newEMuTrigger/'
preFix3 = '/hdfs/store/user/zmao/Spring15_eletronID3/'
preFix2 = '/hdfs/store/user/zmao/noElectronIDCut/'
preFix4 = '/hdfs/store/user/zmao/newSplitting_noChargeMatch/'

preFix5 = '/hdfs/store/user/zmao/noElectronIDCut/'
preFix_datav3= '/hdfs/store/user/zmao/Lumi594/'
preFix_data= '/hdfs/store/user/zmao/Lumi1280/'
# preFix5 = '/hdfs/store/user/zmao/newSplitting_noChargeMatch/'
preFixHiggs = '/hdfs/store/user/zmao/higgs2TauTau/'
preFix_data= '/hdfs/store/user/zmao/miniAODv2/'

preFix = '/hdfs/store/user/zmao/miniAODv2/'
preFix_data = '/hdfs/store/user/zmao/miniAODv2_data/'
preFix = '/hdfs/store/user/zmao/Nov18Prodruction_eleTriggerUpdate/'
preFix_data = '/hdfs/store/user/zmao/Feb22Production/'
preFix2 = '/hdfs/store/user/zmao/Mar2Production/'

# preFix = '/hdfs/store/user/zmao/Jan4Prodruction/'
preFix3 = '/hdfs/store/user/zmao/Jan19Prodruction_et_tauEC/'
# preFix = '/hdfs/store/user/zmao/Jan13Prodruction_et_jetEC/'
preFix = '/hdfs/store/user/zmao/pdfProduction/'
# preFix2 = '/hdfs/store/user/zmao/pdfProduction2/'

type = 'signalRegionNoZetaNoCosPhi'     #selection type (baseline, inclusive)
category = 'all'       #ZLL splitting (all, ZTT, ZL, ZJ)
pairChoice = 'iso'     #pair selection method (iso, pt)

fs = ''
sys = ''
K_WJets = 61526.7/50690
K_DY = 6025.2/4895.0
K_DY_mass = 6025.2/6104.

sampleLocations = [
#                     ("data_Tau",     "%s/data_Tau_Run2015D-05Oct_PromptReco_25ns" %preFix, 1, 'tt'),
#                     ("data_Tauv4",     "%s/data_Tau_Run2015DV4_PromptReco_25ns" %preFix, 1, 'tt'),
#                     ("data_MuonEG",     "%s/data_MuonEG_Run2015D-05Oct_PromptReco_25ns" %preFix, 1, 'em'),
#                     ("data_MuonEGv4",     "%s/data_MuonEG_Run2015DV4_PromptReco_25ns" %preFix, 1, 'em'),
                    ("data_Electron",     "%s/data_Electron_Run2015D-05Oct_PromptReco_25ns" %preFix_data, 1, fs),
                    ("data_Electronv4",     "%s/data_Electron_Run2015DV4_PromptReco_25ns" %preFix_data, 1, fs),
#                     ("data_Muon",     "%s/data_Muon_Run2015D-05Oct_PromptReco_25ns" %preFix, 1, 'em'),
#                     ("data_Muonv4",     "%s/data_Muon_Run2015DV4_PromptReco_25ns" %preFix, 1, 'em'),
# 
                    ("WJets_LO",     "%s/WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 61526.7, fs),
                    ("WJets_LO_HT-100to200",     "%s/WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 1345*K_WJets, fs),
                    ("WJets_LO_HT-200to400",     "%s/WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 359.7*K_WJets, fs),
                    ("WJets_LO_HT-400to600",     "%s/WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 48.91*K_WJets, fs),
                    ("WJets_LO_HT-600toInf",     "%s/WJetsToLNu_HT-600ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 18.77*K_WJets, fs),

#                     ("DY-50_LO",     "%s/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 6025.2, fs),
#                     ("DY-50_LO_HT-100to200",     "%s/DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 139.4*K_DY, fs),
#                     ("DY-50_LO_HT-200to400",     "%s/DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 42.75*K_DY, fs),
#                     ("DY-50_LO_HT-400to600",     "%s/DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 5.497*K_DY, fs),
#                     ("DY-50_LO_HT-600toInf",     "%s/DYJetsToLL_M-50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 2.21*K_DY, fs),

                    ('vbfH', "%s/VBFHToTauTau_M125_13TeV_powheg_pythia8" %(preFix3), 3.748*0.0632, fs),
                    ('ggH',  "%s/GluGluHToTauTau_M125_13TeV_powheg_pythia8" %(preFix3), 43.92*0.0632, fs),

                    ("T",     "%s/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 35.6, fs),
                    ("antiT",     "%s/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 35.6, fs),
                    ("T_t-channel",     "%s/ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 136.02, fs),
                    ("antiT_t-channel",     "%s/ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 80.95, fs),

                    ("ZPrime_500",     "%s/ZprimeToTauTau_M_500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_1000",     "%s/ZprimeToTauTau_M_1000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_1500",     "%s/ZprimeToTauTau_M_1500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_2000",     "%s/ZprimeToTauTau_M_2000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_2500",     "%s/ZprimeToTauTau_M_2500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_3000",     "%s/ZprimeToTauTau_M_3000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_3500",     "%s/ZprimeToTauTau_M_3500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_4000",     "%s/ZprimeToTauTau_M_4000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_4500",     "%s/ZprimeToTauTau_M_4500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),
                    ("ZPrime_5000",     "%s/ZprimeToTauTau_M_5000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix3), 1, fs),

                    ("TTJets_LO",     "%s/TT_TuneCUETP8M1_13TeV-powheg-pythia8" %(preFix), 831.76, fs),
                    ("WZTo1L3Nu",     "%s/WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix3), 3.05, fs),
                    ("WWTo1L1Nu2Q",     "%s/WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix3), 49.997, fs),
                    ("WZTo1L1Nu2Q",     "%s/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix3), 10.71 , fs),
                    ("WZJets",     "%s/WZJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix3), 5.26, fs),
                    ("ZZTo2L2Q",     "%s/ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix3), 3.22, fs),
                    ("WZTo2L2Q",     "%s/WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix3), 5.595, fs),
                    ("VVTo2L2Nu",     "%s/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix3), 11.95, fs),
                    ("ZZTo4L",     "%s/ZZTo4L_13TeV-amcatnloFXFX-pythia8" %(preFix3), 1.212, fs),

#                     ("ZPrime_500",     "/nfs_scratch/zmao/newSignalSamples_500", 1, fs),
#                     ("ZPrime_750",     "/nfs_scratch/zmao/newSignalSamples_750", 1, fs),
#                     ("ZPrime_1250",     "/nfs_scratch/zmao/newSignalSamples_1250", 1, fs),


                    ("DY-50",     "%s/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 6025.2, fs),
# #                     ("DY-100to200",     "%s/DYJetsToLL_M-100to200_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 226*K_DY_mass, fs),
                    ("DY-200to400",     "%s/DYJetsToLL_M-200to400_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 7.67*K_DY_mass, fs),
                    ("DY-400to500",     "%s/DYJetsToLL_M-400to500_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 0.423*K_DY_mass, fs),
                    ("DY-500to700",     "%s/DYJetsToLL_M-500to700_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 0.24*K_DY_mass, fs),
                    ("DY-700to800",     "%s/DYJetsToLL_M-700to800_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 0.035*K_DY_mass, fs),
                    ("DY-800to1000",     "%s/DYJetsToLL_M-800to1000_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 0.03*K_DY_mass, fs),
                    ("DY-1000to1500",     "%s/DYJetsToLL_M-1000to1500_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 0.016*K_DY_mass, fs),
#                     ("DY-1500to2000",     "%s/DYJetsToLL_M-1500to2000_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 0.002*K_DY_mass, fs),
#                     ("DY-2000to3000",     "%s/DYJetsToLL_M-2000to3000_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix2), 0.0005*K_DY_mass, fs),


#                    ("TTJets_LO",     "%s/TT_TuneCUETP8M1_13TeV-powheg-scaleup-pythia8" %(preFix), 831.76, fs),
#                     ("T",     "%s/ST_tW_top_5f_scaleup_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 35.6, fs),
#                     ("antiT",     "%s/ST_tW_antitop_5f_scaleup_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 35.6, fs),

#                     ("TTJets_LO",     "%s/TT_TuneCUETP8M1_13TeV-powheg-scaledown-pythia8" %(preFix), 831.76, fs),
#                     ("T",     "%s/ST_tW_top_5f_scaledown_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 35.6, fs),
#                     ("antiT",     "%s/ST_tW_antitop_5f_scaledown_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 35.6, fs),


#                     ("DY-5to50_LO",     "%s/DYJetsToLL_M-5to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 71310, fs),
#                     ("DY-5to50_LO_HT-100to200",     "%s/DYJetsToLL_M-5to50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 224.2, fs),
#                     ("DY-5to50_LO_HT-200to400",     "%s/DYJetsToLL_M-5to50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 37.2, fs),
#                     ("DY-5to50_LO_HT-400to600",     "%s/DYJetsToLL_M-5to50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 3.581, fs),
#                     ("DY-5to50_LO_HT-600toInf",     "%s/DYJetsToLL_M-5to50_HT-600toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 1.124, fs),





#                      ("SUSY", "%sSUSYGluGluToHToTauTau_M-160_TuneCUETP8M1_13TeV-pythia8"  %(preFix), 1, ''),
#                      ("T-tchannel",     "%s/ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 103.02),
#                      ("antiT-tchannel",     "%s/ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 80.95),
#                      ("SUSY", "/nfs_scratch/zmao/susy_1file/", 1, ''),
#                      ("QCD_30to50",     "%s/QCD_Pt-30to50_EMEnriched_TuneCUETP8M1_13TeV_pythia8" %(preFix), 136000000, 'em'),
#                      ("QCD_50to80",     "%s/QCD_Pt-50to80_EMEnriched_TuneCUETP8M1_13TeV_pythia8" %(preFix), 19800000, 'em'),
#                      ("QCD_80to120",     "%s/QCD_Pt-80to120_EMEnriched_TuneCUETP8M1_13TeV_pythia8" %(preFix), 2800000, 'em'),
#                      ("QCD_120to170",     "%s/QCD_Pt-120to170_EMEnriched_TuneCUETP8M1_13TeV_pythia8" %(preFix), 477000, 'em'),
#                      ("QCD_170to300",     "%s/QCD_Pt-170to300_EMEnriched_TuneCUETP8M1_13TeV_pythia8" %(preFix), 114000, 'em'),
#                      ("QCD_300toInf",     "%s/QCD_Pt-300toInf_EMEnriched_TuneCUETP8M1_13TeV_pythia8" %(preFix), 9000, 'em'),

#                      ("WR_2700", "/hdfs/store/user/zmao/test/WRToNuTauToTauTau_2700" , 1, 'mt'),
#                      ("WR_2700", "/hdfs/store/user/zmao/wr1000/WRToNuTauToTauTau_1000" , 1, 'mt'),

#                      ("DY", "%s/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8"  %(preFix5), 1, 'et'),

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
# sampleLocations = [
#                     ("ZPrime_2000",     "%s/ZprimeToTauTau_M_2000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, ''),
# ]