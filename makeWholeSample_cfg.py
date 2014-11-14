#!/usr/bin/env python

#Sample should be in directory preFix0/TRAINEDMASSPOINT
#with name ClassApp_both_TMVARegApp_*
#example, for sample trained with H260:
#sample: /scratch/zmao/relaxed_regression4/260/ClassApp_both_TMVARegApp_H2hh260_all.root


#preFix0 = '/scratch/zmao/relaxed_regression4/'
# preFix0 = '/scratch/zmao/newKinFit/8/'
# preFix0 = '/scratch/zmao/jetPt20/'
preFix0 = '/scratch/zmao/v3/'

# preFix0 = '/scratch/zmao/BDTStudy/7_noDPhiMetJ2_mJJ/'


postFix = ''
bTag = '1M'

thirdLeptonVeto = False

scaleFactors = {'bTag': 0.051,
                '2M': 0.058,
                '1M': 0.0523}  

if thirdLeptonVeto:
    scaleFactors = {'bTag': 0.051,
                    '2M': 0.0507,
                    '1M': 0.0498}


sampleConfigs =[('H2hh260', 'H2hh260_all%s.root' %postFix, 'OStight%s' %bTag, 14.76),

                ('H2hh270', 'H2hh270_all%s.root' %postFix, 'OStight%s' %bTag, 14.76),
                ('H2hh280', 'H2hh280_all%s.root' %postFix, 'OStight%s' %bTag, 14.76),
                ('H2hh290', 'H2hh290_all%s.root' %postFix, 'OStight%s' %bTag, 14.76),

                ("H2hh300", "H2hh300_all%s.root" %postFix, 'OStight%s' %bTag, 15.9),

                ('H2hh310', 'H2hh310_all%s.root' %postFix, 'OStight%s' %bTag, 14.76),
                ('H2hh320', 'H2hh320_all%s.root' %postFix, 'OStight%s' %bTag, 14.76),
                ('H2hh330', 'H2hh330_all%s.root' %postFix, 'OStight%s' %bTag, 14.76),
                ('H2hh340', 'H2hh340_all%s.root' %postFix, 'OStight%s' %bTag, 14.76),

                ('H2hh350', 'H2hh350_all%s.root' %postFix, 'OStight%s' %bTag, 8.57),

                ('H2hh500', 'H2hh500_all.root', 'OStight%s' %bTag, 8.57),
                ('H2hh700', 'H2hh700_all.root', 'OStight%s' %bTag, 8.57),
                ('H2hh1000', 'H2hh1000_all.root', 'OStight%s' %bTag, 8.57),

                ('ZZ','ZZ_all%s.root' %postFix, 'OStight%s' %bTag, 2500),
                ("tt_full","tt_all%s.root" %postFix, 'OStight%s' %bTag, 26197.5),
                ("tt_semi","tt_semi_all%s.root" %postFix, 'OStight%s' %bTag, 109281),
                ('WZJetsTo2L2Q', 'WZJetsTo2L2Q_all.root', 'OStight%s' %bTag, 2207),
                ("DY1JetsToLL","DY1JetsToLL_all.root", 'OStight%s' %bTag, 561000),
                ('DY2JetsToLL','DY2JetsToLL_all.root', 'OStight%s' %bTag, 181000),
                ('DY3JetsToLL','DY3JetsToLL_all.root', 'OStight%s' %bTag, 51100),
                ('W1JetsToLNu','W1JetsToLNu_all.root', 'OStight%s' %bTag, 5400000),
                ('W2JetsToLNu','W2JetsToLNu_all.root', 'OStight%s' %bTag, 1750000),
                ('W3JetsToLNu','W3JetsToLNu_all.root', 'OStight%s' %bTag, 519000),
                ('dataOSRelax','dataTotal_all%s.root' %postFix, 'OSrelaxed%s' %bTag, scaleFactors[bTag])]

oFileName = 'combined%s_%s.root' %(postFix, bTag)
trainedMassPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]
