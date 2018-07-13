#!/usr/bin/env python
from array import array
import math


dir = "/user_data/zmao/2016_highDPhi0B_noIso/"
dir = "/user_data/zmao/2016_signalRegionNoPZeta_Aug17/"
dir = "/user_data/zmao/2016_HighCosDPhi_Aug22/"
# dir = "/user_data/zmao/2016_HighCosDPhi_looseAntiElectron/"
# dir = "/user_data/zmao/2016_signalRegion_noBTagSF_withSVFit_tauECUp/"
dir_data = "/user_data/zmao/moriond_signalRegion_reMiniAOD/"
dir = "/user_data/zmao/moriond_signalRegion_WP90_noBTagSF/"

# _bSysUp
sampleList = [
#___WJets
#     ('WJets', '%s/WJets_all_SYNC_' %dir, 'WJets'),
#     ('WJets', '%s/WJets_LO_all_SYNC_' %dir, 'WJets'),
    ('WJets_HT-0to100', '%s/WJets_LO_HT-0to100_all_SYNC_' %dir, 'WJets'),
    ('WJets_HT-100to200', '%s/WJets_LO_HT-100to200_all_SYNC_' %dir, 'WJets'),
    ('WJets_HT-200to400', '%s/WJets_LO_HT-200to400_all_SYNC_' %dir, 'WJets'),
    ('WJets_HT-400to600', '%s/WJets_LO_HT-400to600_all_SYNC_' %dir, 'WJets'),
    ('WJets_HT-600to800', '%s/WJets_LO_HT-600to800_all_SYNC_' %dir, 'WJets'),
    ('WJets_HT-800to1200', '%s/WJets_LO_HT-800to1200_all_SYNC_' %dir, 'WJets'),
    ('WJets_HT-1200to2500', '%s/WJets_LO_HT-1200to2500_all_SYNC_' %dir, 'WJets'),
    ('WJets_HT-2500toInf', '%s/WJets_LO_HT-2500toInf_all_SYNC_' %dir, 'WJets'),

# #___DY
#     ('DY_M-50', '%s/DY-50_LO_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-50to200', '%s/DY-50to200_LO_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-200to400', '%s/DYJetsToLL_M-200to400_all_SYNC_' %dir, 'Z #rightarrow ll'),
#    ('DY_M-50to400', '%s/DY-50to400_LO_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-400to500', '%s/DYJetsToLL_M-400to500_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-500to700', '%s/DYJetsToLL_M-500to700_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-700to800', '%s/DYJetsToLL_M-700to800_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-800to1000', '%s/DYJetsToLL_M-800to1000_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-1000to1500', '%s/DYJetsToLL_M-1000to1500_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-1500to2000', '%s/DYJetsToLL_M-1500to2000_all_SYNC_' %dir, 'Z #rightarrow ll'),
    ('DY_M-2000to3000', '%s/DYJetsToLL_M-2000to3000_all_SYNC_' %dir, 'Z #rightarrow ll'),

#     ('DY_M-150', '%s/DY-150_LO_all_SYNC_' %dir, 'Z #rightarrow ll'),

#___DiBoson
    ('WZTo1L3Nu', '%s/WZTo1L3Nu_all_SYNC_' %dir, 'Diboson'),
    ('WZTo3LNu', '%s/WZTo3LNu_all_SYNC_' %dir, 'Diboson'),
    ('WWTo1L1Nu2Q', '%s/WWTo1L1Nu2Q_all_SYNC_' %dir, 'Diboson'),
    ('WZTo1L1Nu2Q', '%s/WZTo1L1Nu2Q_all_SYNC_' %dir, 'Diboson'),
    ('ZZTo2L2Q', '%s/ZZTo2L2Q_all_SYNC_' %dir, 'Diboson'),
    ('WZTo2L2Q', '%s/WZTo2L2Q_all_SYNC_' %dir, 'Diboson'),
    ('VVTo2L2Nu', '%s/VVTo2L2Nu_all_SYNC_' %dir, 'Diboson'),
    ('ZZTo4L', '%s/ZZTo4L_all_SYNC_' %dir, 'Diboson'),


#___ttbar
    ('ST_t-channel_antiTop_tW', '%s/antiT_t-channel_all_SYNC_' %dir, 't#bar{t}'),
    ('ST_t-channel_top_tW', '%s/T_t-channel_all_SYNC_' %dir, 't#bar{t}'),
    ('TTJets', '%s/TT_all_SYNC_' %dir, 't#bar{t}'),

    ('ST_s-channel', '%s/ST_s_all_SYNC_' %dir, 't#bar{t}'),
    ('ST_antiTop_tW', '%s/antiT_all_SYNC_' %dir, 't#bar{t}'),
    ('ST_top_tW', '%s/T_all_SYNC_' %dir, 't#bar{t}'),

    ('data', '%s/data_all_SYNC_' %dir_data, 'Observed'),
# 
#     ('ggH', '%s/ggH_all_SYNC_' %dir, 'h125#rightarrow#tau#tau'),
#     ('vbfH', '%s/VBFH_all_SYNC_' %dir, 'h125#rightarrow#tau#tau'),
# #     ]
    ] + [
#     ("Z'(500)", '%s/ZPrime_500_all_SYNC_' %dir, 'ZPrime'),
#     ("Z'(750)", '%s/ZPrime_750_all_SYNC_' %dir, 'ZPrime'),
#     ("Z'(1000)", '%s/ZPrime_1000_all_SYNC_' %dir, 'ZPrime'),
#     ("Z'(1250)", '%s/ZPrime_1250_all_SYNC_' %dir, 'ZPrime'),
#     ("Z'(1500)", '%s/ZPrime_1500_all_SYNC_' %dir, 'ZPrime'),
#     ("Z'(1750)", '%s/ZPrime_1750_all_SYNC_' %dir, 'ZPrime'),
    ("Z'(2000)", '%s/ZPrime_2000_all_SYNC_' %dir, 'ZPrime'),
#     ("Z'(2500)", '%s/ZPrime_2500_all_SYNC_' %dir, 'ZPrime'),    
#     ("Z'(3000)", '%s/ZPrime_3000_all_SYNC_' %dir, 'ZPrime'),
#     ("Z'(3500)", '%s/ZPrime_3500_all_SYNC_' %dir, 'ZPrime'),
#     ("Z'(4000)", '%s/ZPrime_4000_all_SYNC_' %dir, 'ZPrime'),
    ]
#      ]+ [('Zprime_%d' % m, '%s/ZPrime_%d_all_SYNC_' % (dirMC, m), 'ZPrime_%d' % m) for m in (set(range(500, 3500, 500)))]
# ]
# selection = '_antiIso'
# 
# sampleList = [
#                 ('%s/WJets_all_SYNC_' %dir, 'Electroweak', selection),
#               ('%s/WW_all_SYNC_' %dir, 'Electroweak', selection),
#               ('%s/WZ_all_SYNC_' %dir, 'Electroweak', selection),
#               ('%s/ZZ_all_SYNC_' %dir, 'Electroweak', selection),
#               ('%s/DY_all_SYNC_' %dir, 'Z #rightarrow ll', selection),
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
bins4 = []
bins5 = []

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
for i in range(41):
    bins4.append(-1.0 + 0.05*i)

for i in range(41):
    bins5.append(-3.0 + 0.1*i)

bins3 = []
nBins = 20
for i in range(nBins+1):
    bins3.append(0.0 + (1*i+0.0)/nBins)
vars = [#("ePt", array('d', range(35, 125, 15) + range(125, 325, 25) + range(350, 450, 50)), 'GeV', 100.),
#         ("mPt", array('d', range(35, 125, 15) + range(125, 325, 25) + range(350, 450, 50)), 'GeV', 100.),
#         ("mPt", array('d', range(35, 120, 15) + range(140, 230, 30)), 'GeV', 100.),
#        ("tPt", array('d', range(20, 125, 15) + range(125, 225, 25)), 'GeV', 100.),
# 
# 
# 
# #         ("m_withMET", array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300, 400]), 'GeV', 100.), #em os hMEtlPZeta
# #         ("m_withMET", array('d', [85,100,110,120,130,140,150,160,170,180,190,200]), 'GeV', 100.), #em os hMEtlPZeta
#         ("m_vis", array('d', [70, 85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300, 400,600, 900, 1200]), 'GeV', 100.), #em os hMEtlPZeta
# 
#         ("m_withMET", array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600, 900, 1200, 1700]), 'GeV', 100.), #em os hMEtlPZeta
# 
        ("m_eff", array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600, 900, 1200, 1700]), 'GeV', 100.), #em os hMEtlPZeta
#         ("pfmet_svmc_mass", array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600, 900, 1200, 1700]), 'GeV', 100.), #em os hMEtlPZeta

#         ("m_eff", array('d', [85,110,130,150,170,190,225,250,275,300,400,600, 900]), 'GeV', 100.), #em os hMEtlPZeta
#         ("m_eff", array('d', [200,225,250,275,300,400,600, 900, 1200]), 'GeV', 100.), #em os hMEtlPZeta
#         ("m_eff", array('d', [200,225,250,275,300,400,500,700, 900, 1200]), 'GeV', 100.), #em os hMEtlPZeta
#          ("met", array('d', range(0, 110, 10) + range(125, 275, 25) + [300]), 'GeV', 100.),

#         ("pfmet_svmc_mass", array('d', [85,110,130,150,170,190,225,250,275,300,400,600, 900]), 'GeV', 100.), #em os hMEtlPZeta

#         ("m_eff", array('d', range(1000, 4000, 250)), 'GeV', 100),
#         ("m_eff", array('d', range(800, 2500, 150)), 'GeV', 100),
#         ("m_eff", array('d', range(60, 160, 10)), 'GeV', 100),

#         ("m_vis", array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600, 900]), 'GeV', 100.), #em os hMEtlPZeta

#         ("true_mass", array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600, 900, 1200, 1700]), 'GeV', 100.), #em os hMEtlPZeta
#         ("total_transverse_mass", array('d', [85,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600, 900, 1200, 1700]), 'GeV', 100.), #em os hMEtlPZeta


#          ("mt_1", array('d', range(0, 150, 10) + range(160, 525, 25)), 'GeV', 12),

#         ("cosDPhi_MEt_1", array('d', bins4), 'GeV', 12),
#         ("cos_phi_tau1_tau2", array('d', [-1.0, -0.95, -0.9, -0.8, -0.6, -0.4, -0.2, 0]), 'GeV', 12),
#         ("cosDPhi_MEt_1", array('d', [-1.0, -0.95, -0.9, -0.8, -0.6, -0.2, 0.2, 0.6, 0.8, 0.9, 0.95, 1.0]), '', 100.),
#         ("cosDPhi_MEt_2", array('d', [-1.0, -0.95, -0.9, -0.8, -0.6, -0.2, 0.2, 0.6, 0.8, 0.9, 0.95, 1.0]), '', 100.),
#         ("cosDPhi_MEt_lowerPtLep", array('d', [-1.0, -0.95, -0.9, -0.8, -0.6, -0.2, 0.2, 0.6, 0.8, 0.9, 0.95, 1.0]), '', 100.),

#         ("iso_2", array('d', [0, 0.05, 0.10, 0.15, 0.3, 0.6, 1.0]), '', 100.),

#         ("ZetaCut", array('d', range(-200, 125, 25)), 'GeV', 100.), #em os hMEtlPZeta


#         ("cosDPhi_MEt_deltaPt", array('d', [-1.0, -0.95, -0.9, -0.8, -0.6, -0.2, 0.2, 0.6, 0.8, 0.9, 0.95, 1.0]), 'GeV', 12),
#         ("cosDPhi_MEt_lowerPtLep", array('d', [-1.0, -0.95, -0.9, -0.8, -0.6, -0.2, 0.2, 0.6, 0.8, 0.9, 0.95, 1.0]), 'GeV', 12),

#         ("r", array('d', [-3.0, -2.5, -2.0, -1.5, -1.4, -1.3, -1.2, -1.1, -1.05, -1.0, -0.95, -0.9, -0.8, -0.7, -0.5, 0, 0.5, 1]), 'GeV', 12),
#         ("r", array('d', bins5), '', 12),

#         ("cosDPhi_MEt_1", array('d', [0.2, 0.6, 0.8, 0.9, 0.95, 1.0]), 'GeV', 12),

#         ("mt_2", array('d', range(0, 210, 15)), 'GeV', 12),

#         ("nCSVL", array('d', range(0,6,1)), '', 100),
#         ("npv", array('d', range(0, 51, 1)), '', 1),
# 
#         ("tDecayMode", array('d', range(0, 17, 1)), 'GeV', 0.25),

#         ("met", array('d', range(0, 160, 10) + [200, 300]), 'GeV', 0.25),
#         ("pfMetNoHFEt", array('d', range(0, 300, 10)), 'GeV', 80),
#         ("metPuppiEt", array('d', range(0, 300, 10)), 'GeV', 80),
        ]

QCD_scale = {'tt': 1.0,
             'mt': [
                    (0.375, 0.029),
                    ],
             'et': [# (0.089, 0.008),
                    (1.191, 0.071),
                     (0.131, 0.007),],
             'em': [
                    (0.228, 0.050),#e-mu signal region
#                     (0.251, 0.110),
#                     (0.220, 0.028),
#                     (0.194, 0.063),

#                     (0.169, 0.070),
                    ]
            }

# QCD_scale_1prong_3prong = (0.093, 0.014)
QCD_scale_1prong_3prong = (0.258, 0.014)#(0.131, 0.020)#(0.127, 0.022)#(0.100, 0.019)#(0.128, 0.022)



addIntegrals = True
showRegion = True
binned = False
unc = False

scanRange = ['Tight','Medium', 'Loose']
for i in range(9):
    scanRange.append(i+2)
scanRange = ['Tight', 'VLoose']

SF_prong1 = [0.276, 0.111]
SF_prong3 = [0.132, 0.137]

SF_endcap = [0.069, 0.019]
SF_barrel = [0.116, 0.022]

SF_WJets_endcap = [0.10440, 0.00969]
SF_WJets_barrel = [0.13722, 0.01482]

WJetsScanRange = [1.0]#, 1.0, 1.1]#, 1.0, 1.15]#, 1.0, 2.0]
# WJetsLoose2Tight = [0.205, 0.068] #e-mu signal region
# WJetsLoose2Tight = [0.192, 0.021] #mu-tau signal region _ new
# WJetsLoose2Tight = [0.245, 0.043] #e-tau signal region _ new

#WJetsLoose2Tight = [0.249, 0.020] #mu-tau signal region _ old
#WJetsLoose2Tight = [0.198, 0.033] #e-tau signal region _ old
# WJetsLoose2Tight = [0.214, 0.028]
# WJetsLoose2Tight = [0.338, 0.189]

#0.263, 0.039 e-tau
#0.259, 0.018 m-tau
scanRange = [0.15, 1.0]

# for i in range(3):
#     WJetsScanRange.append((i+0.0)*0.1+1.2)
# for i in range(21):
#     WJetsScanRange.append((i+0.0)*0.02+0.7)

list = [0,900]#[0,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600,900]
# list = [0,900]

sysUnc = {}
sysUnc['et'] = {'WJets': 0.0,
                'Z #rightarrow ll': 0.0,
                't#bar{t}': 0.0,
                'Diboson': 0.0,
                }
sysUnc['mt'] = {'WJets': 0.0,
                'Z #rightarrow ll': 0.0,
                't#bar{t}': 0.0,
                'Diboson': 0.0,
                }
sysUnc['em'] = {'WJets': 0.0,
                'Z #rightarrow ll': 0.0,
#                 'Z #rightarrow ll': math.sqrt(0.11**2),
                't#bar{t}':0.0,
#                 't#bar{t}': math.sqrt(0.17**2),
                'Diboson': 0.0,
                }

tauPtBinnedWJetsL2TSF = [(30, 0.47, 0.01),
                         (50, 0.44, 0.02),
                         ('Inf', 0.3, 0.03)]