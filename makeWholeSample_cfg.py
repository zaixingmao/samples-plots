#!/usr/bin/env python

#Sample should be in directory preFix0/TRAINEDMASSPOINT
#with name ClassApp_both_TMVARegApp_*
#example, for sample trained with H260:
#sample: /scratch/zmao/relaxed_regression4/260/ClassApp_both_TMVARegApp_H2hh260_all.root


#preFix0 = '/scratch/zmao/relaxed_regression4/'
# preFix0 = '/scratch/zmao/v4/'
preFixTools = '/nfs_scratch/zmao/fromLogin05/forPlots/'

# preFix0 = '/scratch/zmao/BDTStudy/7_noDPhiMetJ2_mJJ/'
scaleOption = ''
# scaleOption = 'tauUp'
# scaleOption = 'tauDown'
# scaleOption = 'jetUp'
# scaleOption = 'jetDown'

preFix0 = '/nfs_scratch/zmao/fromLogin05/forPlots/%s/' %scaleOption


iso = 1.0
postFix = ''
bTag = '1M'
relaxed = 'INFN_relaxed'
thirdLeptonVeto = True

scaleFactors = {'bTag': 0.051,
                '2M': 0.058,
                '1M1NonM': 0.0523,
                '1M': 0.0523}  

if thirdLeptonVeto:
    scaleFactors = {'bTag': 0.051,
                    '2M': 0.0507,
                    '1M1NonM': 0.0498,
                    '1M': 0.0499}

WScale = 1.193

# sampleConfigs =[('H2hh260', 'H2hh260%s_all.root' %postFix, 'OStight%s' %bTag, 14.76),
# 
#                 ('H2hh270', 'H2hh270%s_all.root' %postFix, 'OStight%s' %bTag, 14.76),
#                 ('H2hh280', 'H2hh280%s_all.root' %postFix, 'OStight%s' %bTag, 14.76),
#                 ('H2hh290', 'H2hh290%s_all.root' %postFix, 'OStight%s' %bTag, 14.76),
# 
#                 ("H2hh300", "H2hh300%s_all.root" %postFix, 'OStight%s' %bTag, 15.9),
# 
#                 ('H2hh310', 'H2hh310%s_all.root' %postFix, 'OStight%s' %bTag, 14.76),
#                 ('H2hh320', 'H2hh320%s_all.root' %postFix, 'OStight%s' %bTag, 14.76),
#                 ('H2hh330', 'H2hh330%s_all.root' %postFix, 'OStight%s' %bTag, 14.76),
#                 ('H2hh340', 'H2hh340%s_all.root' %postFix, 'OStight%s' %bTag, 14.76),
# 
#                 ('H2hh350', 'H2hh350%s_all.root' %postFix, 'OStight%s' %bTag, 8.57),
# 
# #                 ('H2hh500', 'H2hh500_all.root', 'OStight%s' %bTag, 8.57),
# #                 ('H2hh700', 'H2hh700_all.root', 'OStight%s' %bTag, 8.57),
# #                 ('H2hh1000', 'H2hh1000_all.root', 'OStight%s' %bTag, 8.57),
# 
#                 ('ZZ','ZZ_all.root', 'OStight%s' %bTag, 2500),
#                 ("tt_full","tt%s_all.root" %postFix, 'OStight%s' %bTag, 26197.5),
#                 ("tt_semi","tt_semi%s_all.root" %postFix, 'OStight%s' %bTag, 109281),
#                 ('WZJetsTo2L2Q', 'WZJetsTo2L2Q_all.root', 'OStight%s' %bTag, 2207),
#                 ("DYJetsToLL","DYJetsToLL%s_all.root" %postFix, 'OStight%s' %bTag, 3504000),
# #                 ("DY1JetsToLL","DY1JetsToLL_all.root", 'OStight%s' %bTag, 561000),
# #                 ('DY2JetsToLL','DY2JetsToLL_all.root', 'OStight%s' %bTag, 181000),
# #                 ('DY3JetsToLL','DY3JetsToLL_all.root', 'OStight%s' %bTag, 51100),
#                 ('W1JetsToLNu','W1JetsToLNu_all.root', 'OStight%s' %bTag, 5400000*WScale),
#                 ('W2JetsToLNu','W2JetsToLNu_all.root', 'OStight%s' %bTag, 1750000*WScale),
#                 ('W3JetsToLNu','W3JetsToLNu_all.root', 'OStight%s' %bTag, 519000*WScale),
#                 ('dataOSRelax','dataTotal_all.root', 'OSrelaxed%s' %bTag, scaleFactors[bTag])]
data_bTag = '1L'
if bTag == '2M':
    data_bTag = '2L'

sampleConfigs =[('signals', 'signal.root', 'OStight%s' %bTag),
                ('Electroweak','Electroweak_new.root', 'OStight%s' %bTag),
                ("DYJetsToLL","DYJetsToLL_all.root", 'OStight%s' %bTag),
                ("t#bar{t}","tt_new.root", 'OStight%s' %bTag),

                ('MCOSRelax','Electroweak_new.root', 'OSrelaxed%s' %data_bTag),
                ("MCOSRelax","DYJetsToLL_all.root", 'OSrelaxed%s' %data_bTag),
                ("MCOSRelax","tt_new.root", 'OSrelaxed%s' %data_bTag),
                ('data','dataTotal_all.root', 'OSrelaxed%s' %data_bTag)]

oFileName = 'combined%s_%s_iso%.1f_%s_%s_newMethod_withMCOSRelax.root' %(postFix, bTag, iso, relaxed, scaleOption)
trainedMassPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]

sampleConfigsTools =[('Electroweak', 'Electroweak_new.root'),
                     ('DYJetsToLL', 'DYJetsToLL_all.root'),
                     ('t#bar{t}','tt_new.root'),
                     ('data','dataTotal_all.root')]

# sampleConfigsTools =[('Electroweak', 'Electroweak.root'),
#                      ('DYJetsToLL', 'DYJetsToLL_all.root'),
#                      ('t#bar{t}','tt_withHad.root'),
#                      ('data','dataTotal_all.root')]


