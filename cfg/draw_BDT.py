#!/usr/bin/env python
from array import array

bins_1M = range(0,200,10)+range(200, 360, 25)
bins_2M = range(0,80,20)+range(80,160,10)+range(160,200,20)+range(200, 360, 50)
bdt_bins = [x * 0.1 for x in range(-6, 2)]

bins_1M2 = range(30,360,20)
bins_2M2 = range(30,360,40)
bins_1M3 = range(200,800,30)
bins_2M3 = range(200,800,50)
bins_1M4 = range(30,150,10)
bins_2M4 = range(30,150,15)

bins_1M_array = array('d',bins_1M)
bins_2M_array = array('d',bins_2M)
bins_1M_array2 = array('d',bins_1M2)
bins_2M_array2 = array('d',bins_2M2)
bins_1M_array3 = array('d',bins_1M3)
bins_2M_array3 = array('d',bins_2M3)
bdt_bins_array = array('d',bdt_bins)
bins_1M_array4 = array('d',bins_1M4)
bins_2M_array4 = array('d',bins_2M4)

dR_range = []
x = 0.0
while x <= 6:
    dR_range.append(x)
    x += 0.25

bins_dR_array = array('d', dR_range)

bins_chi_array = array('d', range(0, 220, 10))
bins_met_array = array('d', range(0, 300, 20))
bdt_bins_array = array('d', [-0.618, -0.518, -0.41800000000000004, -0.31799999999999995, -0.21799999999999997, -0.118, -0.018000000000000016, 0.08200000000000007, 0.18200000000000008])
varsRange = { 
#              'dRTauTau': (bins_dR_array, bins_dR_array, bins_dR_array,'', 700, 80, 20, ''),
#              'dRJJ': (bins_dR_array, bins_dR_array, bins_dR_array,'', 700, 80, 20, ''),
#              'met': (bins_met_array, bins_met_array, bins_met_array,'(GeV)', 100, 14, 2, 'width'),
             'svMass': (bins_1M_array, bins_1M_array, bins_2M_array,'(GeV)', 50, 6, 1, 'width'),
#              'mJJ': (bins_1M_array2, bins_1M_array2, bins_2M_array2,'(GeV)', 60, 6, 1, 'width'),
#              'fMassKinFit': (bins_1M_array3, bins_1M_array3, bins_2M_array3,'(GeV)', 10, 1, 0.2, 'width'),
#              'chi2KinFit2': (bins_chi_array, bins_chi_array, bins_chi_array,'', 500, 50, 10, ''),
# 
# 
#              'pt1': (bins_1M_array4, bins_1M_array4, bins_2M_array4,'(GeV)', 150, 15, 3, 'width'),
#              'pt2': (bins_1M_array4, bins_1M_array4, bins_2M_array4,'(GeV)', 300, 30, 6, 'width'),

#              'CSVJ1Pt': (bins_1M_array2, bins_1M_array2, bins_2M_array2,'(GeV)', 100, 10, 1, 'width'),
#              'CSVJ2Pt': (bins_1M_array2, bins_1M_array2, bins_2M_array2,'(GeV)', 100, 10, 1, 'width'),

#              'BDT': (bdt_bins_array, bdt_bins_array, bdt_bins_array, '', 2500, 250, 50, ''),
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

predictLocation_front = '/nfs_scratch/zmao/fromLogin05/CMSSW_5_3_15/src/samples-plots/combined_'
predictLocation_front = '/nfs_scratch/zmao/samples_Iso/datacard_new/combined_iso'
predictLocation_front = '/nfs_scratch/zmao/samples_Iso/datacard_new/bdt_new/combined_H'
# predictLocation_front = '/nfs_scratch/zmao/samples_Iso/datacard/bdt_new/combined_'

# predictLocation_back = '%.1f_INFN_relaxed__newMethod_withMCOSRelax_Fix.root' %iso
predictLocation_back = '%.1f_one1To4_iso_normal__withDYEmbed.root' %iso
predictLocation_back = '_normal.root'
massWindowCut = False
drawWhichDY = 'DY_Embed'#'DY+ttLep'
method = ''#BDT_inputs_style2'
addIntegrals = True