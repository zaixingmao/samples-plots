#!/usr/bin/env python
from array import array

dir = "/nfs_scratch/zmao/13TeV_samples"

sampleList = [
                ('%s/WJets_all_SYNC_' %dir, 'Electroweak', 24089991),
              ('%s/WW_all_SYNC_' %dir, 'Electroweak', 989608),
              ('%s/WZ_all_SYNC_' %dir, 'Electroweak', 996920),
              ('%s/ZZ_all_SYNC_' %dir, 'Electroweak', 998848),
              ('%s/DY_all_SYNC_' %dir, 'Z#rightarrow#tau#tau', 19925500),
              ('%s/antiT_all_SYNC_' %dir, 't#bar{t}', 500000),
              ('%s/T_all_SYNC_' %dir, 't#bar{t}', 998400),
              ('%s/TTJets_all_SYNC_' %dir, 't#bar{t}', 4994250),
              ('%s/data_all_SYNC_' %dir, 'Observed', 1),
            ]

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

vars = [( "pt_1", array('d', range(0,200,10)), 'GeV', 80),
#         ("pt_2", array('d', range(0, 200, 10)), 'GeV', 80),
        ("eta_1", array('d', bins), 'GeV', 80),
        ("eta_2", array('d', bins), 'GeV', 80),

        ("m_vis", array('d', range(0, 200, 20) + range(200, 400, 50)), 'GeV', 12),
#         ("mt_1", array('d', range(0, 200, 10)), 'GeV', 12),
#         ("mt_2", array('d', range(0, 200, 10)), 'GeV', 12),

#         ("njets", array('d', range(0,6,1)), '', 100),
#         ("met", array('d', range(0, 200, 10)), 'GeV', 80),
        ]

QCD_scale = {'tt': 1.073,
              'et': 0.981,
              'mt': 1.012,
              'em': 1.0}

addIntegrals = False
