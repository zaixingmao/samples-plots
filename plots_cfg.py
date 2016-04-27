#!/usr/bin/env python
from array import array
import math

dir = "/nfs_scratch/zmao/13TeV_samples_25ns_Spring15_eletronID2"
dir = "/user_data/elaird/svSkim-sep18/"
dir_data = "/user_data/zmao/RunD_svfit/"
# dir = "/user_data/zmao/antiIso/"

dir_data = "/user_data/zmao/supy-output//svSkim/"
dir_higgs = "/user_data/zmao/higgs_svfit/"
dir = "/user_data/elaird/svSkim-sep18/"
dir_Zprime = "/user_data/zmao/zprime/"
dir_dy = '/user_data/zmao/DY/'
# dir = "/user_data/zmao/antiIso_newEMutrigger/"
dir_WJets = '/user_data/zmao/WJets/'
dir = '/user_data/zmao/miniAODv2/'
# dir = '/user_data/zmao/miniAODv2_em/'
dir = '/user_data/zmao/Nov18Prodruction_ntuple_TightTo5/'
# dir = '/user_data/zmao/Nov18Prodruction_ntuple_noIso/MVANonTrigWP80/'
# dir = '/user_data/zmao/Nov18Prodruction_ntuple_MVANonTrigWP80_singleEforEMu/'
# dir = '/user_data/zmao/Nov18Prodruction_ntuple_mu/'
# dirMC = '/user_data/zmao/Jan13Production_highMETlowPZeta0B/'
# dirMC = '/user_data/zmao/signalRegionNoCosPhi/'
# # dirMC = '/user_data/zmao/Jan13Production_jetEC/'
# dirMC = '/user_data/zmao/signalRegionBTagged/'
# dirMC = '/user_data/zmao/signalRegionNoMET/'
# dirMC = '/user_data/zmao/highMET0BNotSignal/'

dir = '/user_data/zmao/Jan13Production_signalRegion/'
dir_pdf = '/user_data/zmao/singalRegion_pdf/'
dir = '/user_data/zmao/NoBTag_7_6_X/normal'

# 
# dir = '/user_data/zmao/signalRegion_7_6_X_2/'
dir_pdf = dir
# dir = '/user_data/zmao/lowMET0B/'
# dir = '/user_data/zmao/highMET0BNotSignal/'
# dirMC = '/user_data/zmao/Jan13Production_jetBTag/'
# dirMC = '/user_data/zmao/Jan13Production_tauDown/'
dirMC = dir#'/user_data/zmao/signalRegion_tauECUp2/'


# dirMC = '/user_data/zmao/Jan13Production_jetBTag/'
# dirMC = '/user_data/zmao/Jan13Production_tauUp/'

# 
# dirMC = '/user_data/zmao/signalRegionNoCosPhi/'
# dirMC = '/user_data/zmao/signalRegionNoMETreversePZeta/'
# dirMC = '/user_data/zmao/Jan13Production_tauDown/'
# dirMC = '/user_data/zmao/Jan13Production_tauUp/'

# dirMC = '/user_data/zmao/Nov18Prodruction_ntuple_TightTo5/'
dirMC_variation = dirMC#'/user_data/zmao/signalRegion_scaleup/'

sampleList = [
#___WJets
#     ('WJets', '%s/WJets_all_SYNC_' %dir, 'WJets'),
#     ('WJets', '%s/WJets_MLM_all_SYNC_' %dir, 'WJets'),
#     ('WJets', '%s/WJets_LO_all_SYNC_' %dir, 'WJets'),

    ('WJets_HT-0to100', '%s/WJets_LO_HT-0to100_all_SYNC_' %dir_pdf, 'WJets'),
    ('WJets_HT-100to200', '%s/WJets_LO_HT-100to200_all_SYNC_' %dir_pdf, 'WJets'),
    ('WJets_HT-200to400', '%s/WJets_LO_HT-200to400_all_SYNC_' %dir_pdf, 'WJets'),
    ('WJets_HT-400to600', '%s/WJets_LO_HT-400to600_all_SYNC_' %dir_pdf, 'WJets'),
    ('WJets_HT-600toInf', '%s/WJets_LO_HT-600toInf_all_SYNC_' %dir_pdf, 'WJets'),
# 

#___DY
#     ('DY_M-50', '%s/DY-50_all_SYNC_' %dirMC, 'Z#rightarrow#tau#tau'),
    ('DY_M-50to200', '%s/DY-50to200_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
#     ('DY_M-100to200', '%s/DY-100to200_all_SYNC_' %dirMC, 'Z#rightarrow#tau#tau'),
    ('DY_M-200to400', '%s/DY-200to400_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
    ('DY_M-400to500', '%s/DY-400to500_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
    ('DY_M-500to700', '%s/DY-500to700_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
    ('DY_M-700to800', '%s/DY-700to800_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
    ('DY_M-800to1000', '%s/DY-800to1000_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
    ('DY_M-1000to1500', '%s/DY-1000to1500_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
# 
# #     ('DY_M-450to500', '%s/DY-450to500_all_SYNC_' %dirMC2, 'Z#rightarrow#tau#tau'),
#     ('DY_M-500to550', '%s/DY-500to550_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
# # #     ('DY_M-950to1000', '%s/DY-950to1000_all_SYNC_' %dirMC2, 'Z#rightarrow#tau#tau'),
#     ('DY_M-1000to1050', '%s/DY-1000to1050_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
# # #     ('DY_M-1450to1500', '%s/DY-1450to1500_all_SYNC_' %dirMC2, 'Z#rightarrow#tau#tau'),
#     ('DY_M-1500to1550', '%s/DY-1500to1550_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
# # #     ('DY_M-1950to2000', '%s/DY-1950to2000_all_SYNC_' %dirMC2, 'Z#rightarrow#tau#tau'),
#     ('DY_M-2000to2050', '%s/DY-2000to2050_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
#     ('DY_M-2450to2550', '%s/DY-2450to2550_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
#     ('DY_M-2800to3000', '%s/DY-2800to3000_all_SYNC_' %dir_pdf, 'Z#rightarrow#tau#tau'),
# 
# 
# #     ('DY_M-50', '%s/DY-50_LO_all_SYNC_' %dirMC, 'Z#rightarrow#tau#tau'),
# #     ('DY_M-50-H-0to100', '%s/DY-50_LO_HT-0to100_all_SYNC_' %dirMC, 'Z#rightarrow#tau#tau'),
# #     ('DY_M-50-H-100to200', '%s/DY-50_LO_HT-100to200_all_SYNC_' %dirMC, 'Z#rightarrow#tau#tau'),
# #     ('DY_M-50-H-200to400', '%s/DY-50_LO_HT-200to400_all_SYNC_' %dirMC, 'Z#rightarrow#tau#tau'),
# #     ('DY_M-50-H-400to600', '%s/DY-50_LO_HT-400to600_all_SYNC_' %dirMC, 'Z#rightarrow#tau#tau'),
# #     ('DY_M-50-H-600toInf', '%s/DY-50_LO_HT-600toInf_all_SYNC_' %dirMC, 'Z#rightarrow#tau#tau'),
# 
# #     ('DY_10to50', '%s/DY-10to50_all_SYNC_' %dir_dy, 'Z#rightarrow#tau#tau'),
# #     ('ZTT', '%s/DY_all_ZTT_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
# #     ('ZL', '%s/DY_all_ZL_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
# #     ('ZJ', '%s/DY_all_ZJ_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
# 
# 
# #___DiBoson
# #     ('WW', '%s/WW_all_SYNC_' %dir, 'Diboson'),
# #     ('WZ', '%s/WZ_all_SYNC_' %dir, 'Diboson'),
# #     ('ZZ', '%s/ZZ_all_SYNC_' %dir, 'Diboson'),

    ('WZTo1L3Nu', '%s/WZTo1L3Nu_all_SYNC_' %dirMC, 'Diboson'),
    ('WWTo1L1Nu2Q', '%s/WWTo1L1Nu2Q_all_SYNC_' %dirMC, 'Diboson'),
    ('WZTo1L1Nu2Q', '%s/WZTo1L1Nu2Q_all_SYNC_' %dirMC, 'Diboson'),
    ('WZJets', '%s/WZJets_all_SYNC_' %dirMC, 'Diboson'),
    ('ZZTo2L2Q', '%s/ZZTo2L2Q_all_SYNC_' %dirMC, 'Diboson'),
    ('WZTo2L2Q', '%s/WZTo2L2Q_all_SYNC_' %dirMC, 'Diboson'),
    ('VVTo2L2Nu', '%s/VVTo2L2Nu_all_SYNC_' %dirMC, 'Diboson'),
    ('ZZTo4L', '%s/ZZTo4L_all_SYNC_' %dirMC, 'Diboson'),
# # 
# # #___ttbar
# # #     ('ST_antiTop_tW', '%s/antiT_all_SYNC_' %dirMC, 't#bar{t}'),
# # #     ('ST_top_tW', '%s/T_all_SYNC_' %dirMC, 't#bar{t}'),
    ('ST_t-channel_antiTop_tW', '%s/antiT_t-channel_all_SYNC_' %dirMC, 't#bar{t}'),
    ('ST_t-channel_top_tW', '%s/T_t-channel_all_SYNC_' %dirMC, 't#bar{t}'),
# 
# #     ('TTJets', '%s/TTJets_all_SYNC_' %dir, 't#bar{t}'),
# #     ('TTJets', '%s/TTJets_LO_all_SYNC_' %dirMC, 't#bar{t}'),
# 
# #___ttbar variations
    ('ST_antiTop_tW', '%s/antiT_all_SYNC_' %dirMC, 't#bar{t}'),
    ('ST_top_tW', '%s/T_all_SYNC_' %dirMC, 't#bar{t}'),
    ('TTJets', '%s/TTJets_LO_all_SYNC_' %dir_pdf, 't#bar{t}'),
# # 
    ('data', '%s/data_Electron_all_SYNC_' %dir, 'Observed'),
#    ('ggH160', '%s/SUSY_all_SYNC_' %dir, 'ggH160'),
#     ('ggH', '%s/ggH_all_SYNC_' %dirMC, 'h125#rightarrow#tau#tau'),
#     ('vbfH', '%s/vbfH_all_SYNC_' %dirMC, 'h125#rightarrow#tau#tau'),
#     ]
#     ] + [('Zprime_1000', '%s/ZPrime_1000_all_SYNC_' %dirMC, 'ZPrime_1000')]
     ]+ [('Zprime_%d' % m, '%s/ZPrime_%d_all_SYNC_' % (dirMC, m), 'ZPrime_%d' % m) for m in (set(range(500, 3500, 500)))]

# selection = '_antiIso'
# 
# sampleList = [
#                 ('%s/WJets_all_SYNC_' %dir, 'Electroweak', selection),
#               ('%s/WW_all_SYNC_' %dir, 'Electroweak', selection),
#               ('%s/WZ_all_SYNC_' %dir, 'Electroweak', selection),
#               ('%s/ZZ_all_SYNC_' %dir, 'Electroweak', selection),
#               ('%s/DY_all_SYNC_' %dir, 'Z#rightarrow#tau#tau', selection),
#               ('%s/antiT_all_SYNC_' %dir, 't#bar{t}', selection),
#               ('%s/T_all_SYNC_' %dir, 't#bar{t}', selection),
#               ('%s/TTJets_all_SYNC_' %dir, 't#bar{t}', selection),
#               ('%s/data_all_SYNC_' %dir, 'Observed', selection),
#             ]

nBins = 50
bins = []
for i in range(12+1):
    bins.append(-2.4 + 0.4*i)
bins2 = []
BDT_bins = []
nBins = 10
# for i in range(4+1):
#     bins2.append(-1.0 + (i+0.0)/nBins)
# for i in range(8):
#     bins2.append(-0.7 + (i+0.0)/10.)
for i in range(5):
    bins2.append(-1.0 + 0.05*i)
for i in range(2):
    bins2.append(-0.7 + 0.1*i)
for i in range(8):
    bins2.append(-0.4 + 0.2*i)
for i in range(20):
    BDT_bins.append(-1.0 + 0.1*i)
bins3 = []
nBins = 40
for i in range(nBins+1):
    bins3.append(0.0 + (2*i+0.0)/nBins)
vars = [# ("ePt", array('d', range(30, 110, 10) + range(125, 225, 25) + range(250, 450, 50)), 'GeV', 100.),
#         ("mPt", array('d', range(0, 60, 10) + range(75, 225, 25) + range(250, 500, 100)), 'GeV', 100.),
#         ("tPt", array('d', range(20, 120, 20) + range(140, 300, 40)), 'GeV', 100.),
#        ("tEta", array('d', bins), 'GeV', 80), 
#        ("eEta", array('d', bins), 'GeV', 80),
#        ("mEta", array('d', bins), 'GeV', 80),

#        ("m_vis", array('d', range(400, 2600, 200)), 'GeV', 0.25),
#        ("pfmet_svmc_mass", array('d', range(400, 2600, 200)), 'GeV', 0.25),
#        ("m_withMET", array('d', range(400, 2600, 200)), 'GeV', 0.25),
#        ("pfmet_svmc_mass", array('d', [97.0, 122.0, 147.0, 172.0, 197.0, 222.0, 277.0, 349.0, 374.0]), 'GeV', 0.25),
#        ("m_withMET", array('d',[60.0, 85.0, 110.0, 135.0, 160.0, 185.0, 210.0, 235.0, 260.0, 285.0, 310.0, 335.0, 360.0, 385.0, 413.0, 578.0, 603.0]), 'GeV', 0.25),
#        ("m_vis", array('d', range(0, 300, 50) + [300, 400, 600, 800, 1200]), 'GeV', 0.25), 
#        ("pfmet_svmc_mass", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
#        ("m_vis", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
#        ("m_withMET", array('d', range(0, 220, 20)), 'GeV', 100.),
#         ("m_vis", array('d', range(0, 550, 50)), 'GeV', 0.25),
#         ("m_vis", array('d', range(0, 300, 25) + [315, 450]), 'GeV', 0.25),
#         ("m_withMET", array('d', [0, 50] + range(60, 310, 10) + range(320, 380, 20) + [400]), 'GeV', 0.25), #a

#         ("m_withMET", array('d', [0, 100] + range(125, 300, 25) + [315, 450]), 'GeV', 0.25),
#         ("m_withMET", array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600,900]), 'GeV', 100.), #em os hMEtlPZeta
#         ("m_withMET", array('d', [0,75] + range(100, 475, 25)), 'GeV', 100.), #em os hMEtlPZeta
        ("BDT_both", array('d', BDT_bins), 'GeV', 100.), #em os hMEtlPZeta

#         ("m_withMET", array('d', [0,100,120,140,160,180,200,225,250,275,300,400,600,900]), 'GeV', 100.), #em os hMEtlPZeta

#         ("m_withMET", array('d', range(50, 470, 20)), 'GeV', 0.25), #em os hMEtlPZeta
#         ("m_withMET", array('d', range(50, 160, 10)), 'GeV', 0.25), #em os hMEtlPZeta
#         ("m_withMET", array('d', range(0, 150, 25)), 'GeV', 100.), #em os hMEtlPZeta

#         ("m_withMET", array('d', [0, 50] + range(75, 375, 25) + [400, 450]), 'GeV', 0.25), #em os lMET
#         ("m_withMET", array('d', [0, 60] + range(80, 200, 20) + [230, 400]), 'GeV', 0.25), #em SS lMET
#         ("m_withMET", array('d',  range(0, 400, 10)), 'GeV', 0.25), #em ss hMetlPZeta 
#         ("m_withMET", array('d', [0, 60] + range(80, 280, 20) + [300, 340, 400]), 'GeV', 0.25), #em ss 
#         ("m_withMET", array('d', [0, 60] + range(80, 420, 20)), 'GeV', 0.25), #em os hMetlPZeta

#         ("m_withMET", array('d', [0, 100] + range(125,300,25) + [350,450]), 'GeV', 0.25), #em ss hMetlPZeta

#         ("m_withMET", array('d', [0, 120] + range(140, 220, 20) + [250, 400]), 'GeV', 0.25),
#         ("pfmet_svmc_mass", array('d', [0,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600,900]), 'GeV', 100.), #em os hMEtlPZeta
#        ("m_withMET", array('d', range(100, 325, 25) + [400,600,900]), 'GeV', 100.),
#        ("pfmet_svmc_mass", array('d', range(100, 325, 25) + [400,600,900]), 'GeV', 100.),
#        ("m_vis", array('d', range(0, 325, 25) + [400,600,900]), 'GeV', 100.), 

#        ("m_withMET", array('d', range(0, 5005, 5)), 'GeV', 0.25),
#        ("pfmet_svmc_mass", array('d', range(0, 5005, 5)), 'GeV', 0.25),
#         ("m_vis", array('d', range(0, 5005, 5)), 'GeV', 0.25),
#         ("j1Pt", array('d', range(0, 100, 5)), 'GeV', 0.25),

#        ("pZeta - 3.1pZetaVis", array('d',  range(-150, 0, 50) + range(-30, 120, 20)), '', 100.0),
#        ("pfMetEt", array('d', range(0, 110, 10) + range(120, 220, 20)), '', 100.),
#        ("nCSVL", array('d', range(0, 10, 1)), '', 10.0),
#        ("cos_phi_tau1_tau2", array('d', bins2), '', 10.0),

#        ("mRelIso", array('d', bins3), '', 0.25),
#        ("eRelIso", array('d', bins3), '', 0.25),
#        ("tByCombinedIsolationDeltaBetaCorrRaw3Hits", array('d', range(0, 10, 1)), '', 0.25),

#        ("pfmet_svmc_mass", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
# 
#        ("m_withMET", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
#        ("m_gen", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
#        ("genHT", array('d', range(0, 800, 10)), 'GeV', 0.25),

#         ("mt_2", array('d', range(0, 170, 20)), 'GeV', 12),
#         ("mt_1", array('d', range(20, 140, 10) + [150]), 'GeV', 12),
#         ("mt_1", array('d', range(0, 165, 15)), 'GeV', 12),

#         ("mt_1", array('d', range(0, 215, 15)), 'GeV', 12),
#         ("mt_2", array('d', range(0, 215, 15)), 'GeV', 12),

#         ("njets", array('d', range(0,6,1)), '', 100),
#         ("npv", array('d', range(0, 50, 1)), '', 1),
# 
#         ("tDecayMode", array('d', range(0, 17, 1)), 'GeV', 0.25),

#         ("met", array('d', range(0, 300, 15)), 'GeV', 0.25),
#         ("pfMetNoHFEt", array('d', range(0, 300, 10)), 'GeV', 80),
#         ("metPuppiEt", array('d', range(0, 300, 10)), 'GeV', 80),
        ]

QCD_scale = {'tt': 1.0,
             'mt': 1.0,
             'et': [# (0.089, 0.008),
#                     (0.100, 0.019),
                    (0.127, 0.022),
                    (0.408, 0.055),
                    (0.127, 0.022),
                    (0.126, 0.024),
                    (0.118, 0.021),
                    (0.100, 0.019),
                    (0.128, 0.022),
                    (0.069, 0.019),
                    (0.090, 0.014),
                    (0.119, 0.015),
                    (0.120, 0.016),
                    (0.120, 0.018),
                    (0.121, 0.020),
                    (0.122, 0.023),
                    (0.122, 0.026),
                    (0.123, 0.030),
                    (0.125, 0.035),
                    (0.126, 0.042),
                    (0.129, 0.051),
                    (0, 0),
                    (0, 0),
                    (0.093, 0.084),
                    (0, 0),
                    (0.106, 0.063),
                    (0.042, 0.079),
                    (0.131, 0.007),],
             'em': [# (0.174, 0.016), #lowMET
#                     (0.229, 0.042), #highMETlowPZeta
#                     (0.149, 0.081),
                    (0.161, 0.037),
                    (0.149, 0.081),
#                     (0.142, 0.079),
#                     (0.174, 0.031),
#                         (0.201, 0.075),
#                     (0.200, 0.040),#                       (0.232, 0.044), #signal region
                    #single mu for emu
#                     (0.265, 0.026), #lowMET
#                     (0.0, 0.0), #highMETlowPZeta
#                     (0.779, 0.162), #signal region

                    ]
            }

# QCD_scale_1prong_3prong = (0.093, 0.014)
QCD_scale_1prong_3prong = (0.127, 0.022)#(0.100, 0.019)#(0.128, 0.022)



addIntegrals = True
showRegion = True
binned = False
unc = True

scanRange = ['Tight','Medium', 'Loose']
for i in range(9):
    scanRange.append(i+2)
scanRange = ['Tight', 5]

SF_prong1 = [0.276, 0.111]
SF_prong3 = [0.132, 0.137]
WJetsScanRange = [1.15]#, 1.0, 1.1]#, 1.0, 1.15]#, 1.0, 2.0]
WJetsLoose2Tight = [0.171, 0.005]
WJetsLoose2Tigh_1prong_3prong = [0.14635, 0.01391]#[0.145, 0.012]#[0.146, 0.014]

# WJetsScanRange = [0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3]#, 1.0, 1.1]#, 1.0, 1.15]#, 1.0, 2.0]
# for i in range(7):
#     WJetsScanRange.append((i+0.0)*0.1)
# for i in range(21):
#     WJetsScanRange.append((i+0.0)*0.02+0.7)

# for em
# scanRange = []
# for i in range(10):
#     scanRange.append(i*0.1+0.15)
WJetsScanRange = [1.0]
WJetsLoose2Tight = [0.38278, 0.05325]#[0.074, 0.030]
scanRange = [0.15, 0.95]

# for i in range(3):
#     WJetsScanRange.append((i+0.0)*0.1+1.2)
# for i in range(21):
#     WJetsScanRange.append((i+0.0)*0.02+0.7)

list = [0,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600,900]
# list = [0,900]

sysUnc = {}
sysUnc['et'] = {'WJets': 0.0,
                'Z#rightarrow#tau#tau': math.sqrt(0.14**2 + 0.12**2),
                't#bar{t}': math.sqrt(0.18**2 + 0.08**2),
                'Diboson': 0.15,

                }
sysUnc['em'] = {'WJets': 0.0,
                'Z#rightarrow#tau#tau': math.sqrt(0.11**2 + 0.12**2),
                't#bar{t}': math.sqrt(0.17**2 + 0.08**2),
                'Diboson': 0.15,
                }

sampleDict = {"WJets": ("WJets_all_SYNC_", 24089991000),
              "WW": ('WW_all_SYNC_', 989608000),
              "WZ": ('WZ_all_SYNC_', 996920000),
              "ZZ": ('ZZ_all_SYNC_', 998848000),
              'DY': ('DY_all_SYNC_', 19925500000),
              'ST_antiT_tW': ('antiT_all_SYNC_', 500000000),
              'ST_antiT_tW': ('T_all_SYNC_', 998400000),
              'TTJets': ('TTJets_all_SYNC_', 4994250000),
}
