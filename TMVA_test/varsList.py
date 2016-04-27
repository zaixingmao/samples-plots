#!/usr/bin/env python

# varList = ['svMass', 'dRTauTau', 'dRJJ', 'svPt', 'dRhh', 'met', 'mJJReg', 'metTau1DPhi', 'metTau2DPhi', 
#                 'metJ1DPhi', 'metJ2DPhi', 'metTauPairDPhi', 'metSvTauPairDPhi', 'metJetPairDPhi','CSVJ1', 'CSVJ2', 'fMassKinFit', 'chi2KinFit']

# varList = ['svMass', 'dRJJ', 'metSvTauPairDPhi', 'mJJReg', 'met', 'metJetPairDPhi', 'fMassKinFit', 'svPt']

# varList = ['svMass', 'dRTauTau', 'dRJJ', 'met', 'mJJReg', 'metJ2DPhi', 'fMassKinFit', 'chi2KinFit']
# varList = ['svMass1', 'dRTauTau', 'dRJJ', 'met1', 'mJJ', 'metJ2DPhi', 'fMassKinFit', 'chi2KinFit2']
varList = ['met', 'pZetaCut', 'cosDPhi', 'm_eff']

# varList = ['svMass', 'dRTauTau', 'dRJJ', 'met', 'mJJ', 'fMassKinFit', 'chi2KinFit2']

# varList = ['svMass','met', 'mJJReg','chi2KinFit2']

# varList = ['svMass', 'mJJ']


# varList = ['svMass', 'dRTauTau', 'dRJJ', 'svPt', 'mJJReg', 'ptJJ']

# varList = ['svMass', 'dRTauTau', 'dRJJ', 'mJJReg', 'ptJJ']
# 
# varList = ['svMass', 'dRTauTau', 'dRJJ', 'mJJReg', 'svPt']
# 
# varList = ['svMass', 'dRTauTau', 'dRJJ', 'mJJReg', 'fMass']
# 
# varList = ['svMass', 'mJJ', 'chi2KinFit']


preFix = '/user_data/zmao/TMVA/'
fs = 'em'

bkg = [('DY', 'DY-50to200_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DY', 'DY-200to400_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DY', 'DY-400to500_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DY', 'DY-500to700_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DY', 'DY-700to800_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DY', 'DY-800to1000_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DY', 'DY-1000to1500_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('singleT', 'antiT_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('singleT', 'antiT_t-channel_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('singleT', 'T_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('singleT', 'T_t-channel_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('TT', 'TTJets_LO_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DiBoson', 'WZTo1L3Nu_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DiBoson', 'WWTo1L1Nu2Q_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DiBoson', 'WZTo1L1Nu2Q_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DiBoson', 'WZJets_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DiBoson', 'ZZTo2L2Q_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DiBoson', 'WZTo2L2Q_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DiBoson', 'VVTo2L2Nu_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('DiBoson', 'ZZTo4L_all_SYNC_%s_noIso_OSTight.root' %fs),

       ('signal', 'ZPrime_500_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('signal', 'ZPrime_1000_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('signal', 'ZPrime_1500_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('signal', 'ZPrime_2000_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('signal', 'ZPrime_2500_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('signal', 'ZPrime_3000_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('signal', 'ZPrime_3500_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('signal', 'ZPrime_4000_all_SYNC_%s_noIso_OSTight.root' %fs),
       ('dataOSLoose', 'data_Electron_all_SYNC_%s_noIso_OSLoose.root' %fs),
      ]
