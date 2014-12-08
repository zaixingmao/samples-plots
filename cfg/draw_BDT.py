#!/usr/bin/env python
from array import array

bins_1M = range(0,200,10)+range(200, 360, 25)
bins_2M = range(0,80,20)+range(80,160,10)+range(160,200,20)+range(200, 360, 50)
bdt_bins = [x * 0.15 for x in range(-6, 7)]

bins_1M_array = array('d',bins_1M)
bins_2M_array = array('d',bins_2M)
bdt_bins_array = array('d',bdt_bins)

varsRange = { 

#             'J4Pt': (15, 0, 250, 5000, 100, True, True),
             'svMass': (bins_1M_array, bins_2M_array,'(GeV)', 6, 1, 'width'),
#             'svPt': (10, 0, 600, 50, 100, False, True),

#              'BDT': (bdt_bins_array, bdt_bins_array, '', 250, 50, ''),
#             'nTauPairs': (5, 0, 5, 10000, 100, True, True),
#             'CSVJ1': (20, 0.5, 1.0, 50000, 100, True, True),
#             'CSVJ2': (20, 0.0, 1.0, 50000, 100, True, True),
#             'fMass': (15, 100, 1000, 20000, 100, True, True),
#              'fMassKinFit': (21, -30, 600, 50, 100, False, True),
#              'chi2KinFit2': (11, 0, 220, 50, 100, False, True),

#            'byIsolationMVA2raw_1': (20, -1., 1., 20, 100, False, True),
#            'byIsolationMVA2raw_2': (20, -1., 1., 20, 100, False, True),
            }

iso = 1.0
######### BDT ###########
# predictLocation_front = '/nfs_scratch/zmao/fromLogin05/BDT/combined_H'
# predictLocation_back = '_7_n150_mJJ_test__%.1f.root' %iso
# observedLocation_front = '/nfs_scratch/zmao/fromLogin05/BDT/'
# observedLocation_back = '/ClassApp_both_dataTotal_all_tightopposite1M3rdLepVeto.root'

#########  None BDT ###########
predictLocation_front = '/nfs_scratch/zmao/fromLogin05/cutBased/combined_'
predictLocation_back = '%.1f_INFN_relaxed__newMethod_withMCOSRelax.root' %iso
observedLocation_front = '/nfs_scratch/zmao/fromLogin05/forPlots/'
observedLocation_back = 'dataTotal_all_tightopposite1M3rdLepVeto.root'