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
preFix = '/store/user/zmao/Apr15/'
preFix = '/store/user/zmao/Jun15Production/'
preFix_data = '/store/user/zmao/Jun30Production/'
preFix = '/store/user/zmao/Jul15Production/'

type = 'highDCosPhi0BhighMET'     #selection type (baseline, inclusive)
category = 'all'       #ZLL splitting (all, ZTT, ZL, ZJ)
pairChoice = 'iso'     #pair selection method (iso, pt)

fs = 'mt'
sys = ''
K_WJets = 61526.7/50690
K_DY = 6025.2/4895.0
K_DY_mass = 6025.2/6104.

sampleLocations = [
                    ("data_Muon",     "%s/data_Muon_Run2016B" %preFix, 1, fs),
#                     ("data_Electron",     "%s/data_Electron_Run2016B" %preFix_data, 1, fs),
#                     ("WJets",     "%s/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix), 61526.7, fs),
                    ("WJets",     "%s/WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 61526.7, fs),
                    ("WJets_LO_HT-100to200",     "%s/WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 1345*K_WJets, fs),
                    ("WJets_LO_HT-200to400",     "%s/WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 359.7*K_WJets, fs),
                    ("WJets_LO_HT-400to600",     "%s/WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 48.91*K_WJets, fs),
                    ("WJets_LO_HT-600to800",     "%s/WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 12.05*K_WJets, fs),
                    ("WJets_LO_HT-800to1200",     "%s/WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 5.501*K_WJets, fs),
                    ("WJets_LO_HT-1200to2500",     "%s/WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 1.329*K_WJets, fs),
                    ("WJets_LO_HT-2500toInf",     "%s/WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 0.03216*K_WJets, fs),
# 
# # 
                    ("DY-50_LO",     "%s/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8" %(preFix), 6025.2, fs),
# 
#                     ("TTJets",     "%s/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8" %(preFix), 831.76, fs),
                    ("TT",     "%s/TT_TuneCUETP8M1_13TeV-powheg-pythia8" %(preFix), 831.76, fs),
                    ("ST_s",     "%s//ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1" %(preFix), 10.32*0.108*3 , fs),
                    ("T",     "%s/ST_tW_top_5f_NoFullyHadronicDecays_13TeV-powheg_TuneCUETP8M1" %(preFix), 35.6*(1-0.676*0.676), fs),
                    ("antiT",     "%s/ST_tW_antitop_5f_NoFullyHadronicDecays_13TeV-powheg_TuneCUETP8M1" %(preFix), 35.6*(1-0.676*0.676), fs),
                    ("T_t-channel",     "%s/ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 136.02*0.108*3, fs),
                    ("antiT_t-channel",     "%s/ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1" %(preFix), 80.95*0.108*3, fs),
# # # 
# #                    ("ZPrime_500",     "%s/ZprimeToTauTau_M_500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_1000",     "%s/ZprimeToTauTau_M_1000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_1500",     "%s/ZprimeToTauTau_M_1500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_2000",     "%s/ZprimeToTauTau_M_2000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_2500",     "%s/ZprimeToTauTau_M_2500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_3000",     "%s/ZprimeToTauTau_M_3000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_3500",     "%s/ZprimeToTauTau_M_3500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_4000",     "%s/ZprimeToTauTau_M_4000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_4500",     "%s/ZprimeToTauTau_M_4500_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# #                     ("ZPrime_5000",     "%s/ZprimeToTauTau_M_5000_TuneCUETP8M1_tauola_13TeV_pythia8" %(preFix), 1, fs),
# # # # 
                    ("WZTo1L3Nu",     "%s/WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix), 3.05, fs),
                    ("WWTo1L1Nu2Q",     "%s/WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix), 45.85, fs),
                    ("WZTo1L1Nu2Q",     "%s/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix), 10.96 , fs),
                    ("WZTo3LNu",     "%s/WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8" %(preFix), 4.42965, fs),
                    ("ZZTo2L2Q",     "%s/ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix), 3.38, fs),
                    ("WZTo2L2Q",     "%s/WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix), 5.52, fs),
                    ("VVTo2L2Nu",     "%s/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8" %(preFix), 12.05, fs),
                    ("ZZTo4L",     "%s/ZZTo4L_13TeV_powheg_pythia8" %(preFix), 1.256, fs),

]
