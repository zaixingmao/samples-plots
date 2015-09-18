#!/usr/bin/env python
from array import array

dir = "/nfs_scratch/zmao/13TeV_samples_25ns_Spring15_eletronID2"

sampleList = [
    ('Wjets', '%s/WJets_all_SYNC_' %dir, 'Electroweak'),
    ('WW', '%s/WW_all_SYNC_' %dir, 'Electroweak'),
    ('WZ', '%s/WZ_all_SYNC_' %dir, 'Electroweak'),
    ('ZZ', '%s/ZZ_all_SYNC_' %dir, 'Electroweak'),
    ('ZTT', '%s/DY_all_ZTT_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
    ('ZL', '%s/DY_all_ZL_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
    ('ZJ', '%s/DY_all_ZJ_SYNC_' %dir, 'Z#rightarrow#tau#tau'),
    ('ST_antiTop_tW', '%s/antiT_all_SYNC_' %dir, 't#bar{t}'),
    ('ST_top_tW', '%s/T_all_SYNC_' %dir, 't#bar{t}'),
    ('TTJets', '%s/TTJets_all_SYNC_' %dir, 't#bar{t}'),
    ('data', '%s/data_all_SYNC_' %dir, 'Observed'),
    ('ggH160', '%s/SUSY_all_SYNC' %dir, 'ggH160'),
    ] + [('Zprime%d' % m, '%s/ZPrime_%d_all_SYNC' % (dir, m), 'ZPrime_%d' % m) for m in (set(range(500, 5500, 500)) - set([2500, 4500]))]


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

nBins = 10
bins = []
for i in range(nBins+1):
    bins.append(-3.0 + (6*i+0.0)/nBins)

vars = [# ("pt_1", array('d', range(0,200,10)), 'GeV', 0.25),
#         ("pt_2", array('d', range(0, 200, 10)), 'GeV', 0.25),
#         ("eta_1", array('d', bins), 'GeV', 80),
#         ("eta_2", array('d', bins), 'GeV', 80),

        ("m_vis", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
       ("m_withMET", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),
        ("m_gen", array('d', range(0, 200, 20) + range(200, 400, 50) + range(400, 2600, 200)), 'GeV', 0.25),

#         ("mt_1", array('d', range(0, 200, 10)), 'GeV', 12),
#         ("mt_2", array('d', range(0, 200, 10)), 'GeV', 12),
#         ("npv", array('d', range(0, 35, 1)), '', 0.15),

#         ("njets", array('d', range(0,6,1)), '', 100),
#         ("met", array('d', range(0, 200, 10)), 'GeV', 80),
        ]

QCD_scale = {'tt': 1.073,
              'et': 0.981,
              'mt': 1.012,
              'em': 1.0}

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
