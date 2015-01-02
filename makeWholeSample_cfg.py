#!/usr/bin/env python

#Sample should be in directory preFix0/TRAINEDMASSPOINT
#with name ClassApp_both_TMVARegApp_*
#example, for sample trained with H260:
#sample: /scratch/zmao/Relax_regression4/260/ClassApp_both_TMVARegApp_H2hh260_all.root


#preFix0 = '/scratch/zmao/Relax_regression4/'
# preFix0 = '/scratch/zmao/v4/'
preFixTools = '/nfs_scratch/zmao/fromLogin05/looseCSV2/'
# preFix0 = '/scratch/zmao/BDTStudy/7_noDPhiMetJ2_mJJ/'
scaleOption = ''
# scaleOption = 'tauUp'
# scaleOption = 'tauDown'
# scaleOption = 'jetUp'
# scaleOption = 'jetDown'
preFixTauESOff = '/nfs_scratch/zmao/samples/tauESOff/normal/'
preFixTauESOn = '/nfs_scratch/zmao/samples/tauESOn/normal/'
preFixData = '/nfs_scratch/zmao/samples/data/'
preFixDataEmbed = '/nfs_scratch/zmao/samples/data_embed/'

preFix0 = '/nfs_scratch/zmao/fromLogin05/looseCSV2/%s/' %scaleOption


iso = 1.0
pairOption = 'pt'
postFix = ''
bTag = 'M'
tail = '_withDYEmbed'
Relax = 'one1To4'
thirdLeptonVeto = True
massWindow = True
if massWindow:
    tail += '_massWindow'

data_bTag = 'L'
# if bTag == '2M':
#     data_bTag = '2L'

sampleConfigs =[('signals', '%s/signal.root' %preFixTauESOn, 'OSTight%s' %bTag, False),
                ("DY_inclusive","%s/dy.root" %preFixTauESOn, 'OSTight%s' %bTag, False),
                ("t#bar{t}","%s/TT.root" %preFixTauESOff, 'OSTight%s' %bTag, False),
                ('Electroweak','%s/Electroweak.root' %preFixTauESOff, 'OSTight%s' %data_bTag, False),
                ("singleT","%s/singleTop.root" %preFixTauESOff, 'OSTight%s' %data_bTag, True),
                ("DY_embed","%s/DY_embed.root" %preFixDataEmbed, 'OSTight%s' %data_bTag, True),
                ("tt_embed","%s/tt_embed_all.root" %preFixTauESOn, 'OSTight%s' %data_bTag, True),
                ('MCOSRelax','%s/Electroweak.root' %preFixTauESOff, 'OSRelax%s' %data_bTag, False),
                ("MCOSRelax","%s/dy.root" %preFixTauESOn, 'OSRelax%s' %data_bTag, False),
                ("MCOSRelax","%s/TT.root" %preFixTauESOff, 'OSRelax%s' %data_bTag, False),
                ('data','%s/data.root' %preFixData, 'OSRelax%s' %data_bTag, False)]

oFileName = 'combined%s_iso%.1f_%s_%s_%s.root' %(postFix, iso, Relax, scaleOption, tail)
trainedMassPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]

sampleConfigsTools =[('Electroweak', '%s/Electroweak_withSingleTop.root' %preFixTauESOff),
                     ('DYJetsToLL', '%s/dy.root' %preFixTauESOn),
                     ('t#bar{t}','%s/TT.root' %preFixTauESOff),
                     ('data','%s/data_new.root' %preFixData)]



