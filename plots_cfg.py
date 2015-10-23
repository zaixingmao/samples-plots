#!/usr/bin/env python
from array import array

dir = "/nfs_scratch/zmao/13TeV_samples_25ns_Spring15_eletronID2"
dir = "/user_data/elaird/svSkim-sep18/"
dir_data = "/user_data/zmao/RunD_svfit/"
dir = "/user_data/zmao/antiIso_newEMutrigger/"
# dir = "/user_data/zmao/antiIso/"

dir_data = "/user_data/zmao/RunD_1263/"
dir_higgs = "/user_data/zmao/higgs_svfit/"
dir = "/user_data/elaird/svSkim-sep18/"
dir_Zprime = "/user_data/zmao/zprime/"
dir_dy = '/user_data/zmao/DY/'
sampleList = [
    ('WJets', '%s/WJets_all_SYNC_' %dir, 'WJets'),
    ('WW', '%s/WW_all_SYNC_' %dir, 'Diboson'),
    ('WZ', '%s/WZ_all_SYNC_' %dir, 'Diboson'),
    ('ZZ', '%s/ZZ_all_SYNC_' %dir, 'Diboson'),
#     ('ZTT', '%s/DY_all_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
    ('ZTT', '%s/DY_all_ZTT_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
    ('ZL', '%s/DY_all_ZL_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
    ('ZJ', '%s/DY_all_ZJ_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
#     ('DY_10to50', '%s/DY-10to50_all_SYNC_' %dir_dy, 'Z#rightarrow#tau#tau'),
    ('ST_antiTop_tW', '%s/antiT_all_SYNC_' %dir, 't#bar{t}'),
    ('ST_top_tW', '%s/T_all_SYNC_' %dir, 't#bar{t}'),
    ('TTJets', '%s/TTJets_all_SYNC_' %dir, 't#bar{t}'),
    ('data', '%s/data_all_SYNC_' %dir_data, 'Observed'),
#    ('ggH160', '%s/SUSY_all_SYNC_' %dir, 'ggH160'),
    ('ggH', '%s/ggH_all_SYNC_' %dir_higgs, 'h125#rightarrow#tau#tau'),
    ('vbfH', '%s/vbfH_all_SYNC_' %dir_higgs, 'h125#rightarrow#tau#tau'),
#     ]
   ] + [('Zprime_2000', '%s/ZPrime_2000_all_SYNC_' %dir, 'ZPrime_2000')]
#     ]+ [('Zprime%d' % m, '%s/ZPrime_%d_all_SYNC_' % (dir_Zprime, m), 'ZPrime_%d' % m) for m in (set([2500, 4500]))] + [('Zprime%d' % m, '%s/ZPrime_%d_all_SYNC_' % (dir, m), 'ZPrime_%d' % m) for m in (set(range(500, 4500, 500)) - set([2500, 4500]))]


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
for i in range(nBins+1):
    bins.append(-2.5 + (5*i+0.0)/nBins)
bins2 = []
nBins = 20
# for i in range(4+1):
#     bins2.append(-1.0 + (i+0.0)/nBins)
# for i in range(8):
#     bins2.append(-0.7 + (i+0.0)/10.)
for i in range(nBins+1):
    bins2.append(-1.0 + (2*i+0.0)/nBins)


bins3 = []
nBins = 40
for i in range(nBins+1):
    bins3.append(0.0 + (2*i+0.0)/nBins)
vars = [# ( "ePt", array('d', range(0,160,10)), 'GeV', 0.25),
        ("mPt", array('d', range(0,160,10)), 'GeV', 0.25),
#       ("tPt", array('d', range(0, 160, 10)), 'GeV', 0.25),
#        ("eEta", array('d', bins), 'GeV', 80), 
#        ("mEta", array('d', bins), 'GeV', 80),
#        ("m_vis", array('d', range(400, 2600, 200)), 'GeV', 0.25),
#        ("pfmet_svmc_mass", array('d', range(400, 2600, 200)), 'GeV', 0.25),
#        ("m_withMET", array('d', range(400, 2600, 200)), 'GeV', 0.25),

#        ("pfmet_svmc_mass", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
#        ("m_vis", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
#        ("m_withMET", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
#         ("m_vis", array('d', range(0, 500, 20)), 'GeV', 0.25),
#        ("pfmet_svmc_mass", array('d', range(0, 300, 10)), 'GeV', 0.25),
#        ("m_withMET", array('d', range(0, 5005, 5)), 'GeV', 0.25),
#        ("pfmet_svmc_mass", array('d', range(0, 5005, 5)), 'GeV', 0.25),
#         ("m_vis", array('d', range(0, 5005, 5)), 'GeV', 0.25),

#        ("pZeta - 3.1pZetaVis", array('d',  range(-210, -60, 30) + range(-60, 100, 10)), '', 0.25),
#        ("pfMetEt", array('d', range(0, 300, 10)), '', 0.25),
#        ("nCSVL", array('d', range(0, 10, 1)), '', 0.25),
#        ("cos_phi_tau1_tau2", array('d', bins2), '', 0.25),
#        ("mRelIso", array('d', bins3), '', 0.25),
#        ("eRelIso", array('d', bins3), '', 0.25),

#        ("pfmet_svmc_mass", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),

#        ("m_withMET", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
#        ("m_gen", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),

#         ("mt_1", array('d', range(40, 200, 10)), 'GeV', 12),
#         ("mt_2", array('d', range(40, 200, 10)), 'GeV', 12),
#         ("nvtx", array('d', range(0, 35, 1)), '', 0.15),

#         ("njets", array('d', range(0,6,1)), '', 100),
#         ("met", array('d', range(0, 200, 10)), 'GeV', 80),
        ]

QCD_scale = {'tt': 1.0,
              'mt': 1.0,
              'et': 1.03,
              'em': 1.4}

addIntegrals = True


sampleDict = {"WJets": ("WJets_all_SYNC_", 24089991000),
              "WW": ('WW_all_SYNC_', 989608000),
              "WZ": ('WZ_all_SYNC_', 996920000),
              "ZZ": ('ZZ_all_SYNC_', 998848000),
              'DY': ('DY_all_SYNC_', 19925500000),
              'ST_antiT_tW': ('antiT_all_SYNC_', 500000000),
              'ST_antiT_tW': ('T_all_SYNC_', 998400000),
              'TTJets': ('TTJets_all_SYNC_', 4994250000),
}
