#!/usr/bin/env python

#Sample should be in directory preFix0/TRAINEDMASSPOINT
#with name ClassApp_both_TMVARegApp_*
#example, for sample trained with H260:
#sample: /scratch/zmao/Relax_regression4/260/ClassApp_both_TMVARegApp_H2hh260_all.root


#preFix0 = '/scratch/zmao/Relax_regression4/'
# preFix0 = '/scratch/zmao/v4/'
preFixTools = '/nfs_scratch/zmao/fromLogin05/looseCSV2/'
# preFix0 = '/scratch/zmao/BDTStudy/7_noDPhiMetJ2_mJJ/'
scaleOption = 'normal'
scaleOption = 'tauUp'
scaleOption = 'tauDown'
# scaleOption = 'jetUp'
# scaleOption = 'jetDown'
preFixTauESOff = '/nfs_scratch/zmao/samples/tauESOff/normal/'
preFixTauESOn = '/nfs_scratch/zmao/samples/tauESOn/normal/'
preFixData = '/nfs_scratch/zmao/samples/data'
preFixEmbed = '/nfs_scratch/zmao/samples/ZTT/'
preFixTauESOffTauShift = '/nfs_scratch/zmao/samples/tauESOff/%s/' %scaleOption
preFixTauESOnTauShift = '/nfs_scratch/zmao/samples/tauESOn/%s/' %scaleOption
bTagShift = '' # ,sysUp, sysDown, misUp, misDown 
usePassJetTrigger = False

# preFixTauESOff = '/nfs_scratch/zmao/fromLogin05/looseCSV2/%s/' %scaleOption
# preFixTauESOn = '/nfs_scratch/zmao/fromLogin05/looseCSV2/%s/' %scaleOption
# preFixData = '/nfs_scratch/zmao/fromLogin05/looseCSV2/%s/' %scaleOption
# preFixDataEmbed = '/nfs_scratch/zmao/fromLogin05/looseCSV2/%s/' %scaleOption


iso = 1.0
pairOption = 'pt'
checkSpeed = False
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

sampleConfigs =[('signals', '%s/signal.root' %preFixTauESOnTauShift, 'OSTight%s' %bTag, False),
                ("DY_inclusive","%s/dy.root" %preFixTauESOnTauShift, 'OSTight%s' %bTag, False),
                ("t#bar{t}","%s/TT.root" %preFixTauESOffTauShift, 'OSTight%s' %bTag, False),
                ('VV','%s/Electroweak.root' %preFixTauESOff, 'OSTight%s' %data_bTag, True),
                ("singleT","%s/singleTop.root" %preFixTauESOff, 'OSTight%s' %data_bTag, True),
                ("ZLL","%s/dy.root" %preFixTauESOnTauShift, 'OSTight%s' %data_bTag, True),
                ("DY_embed","%s/DY_embed.root" %preFixTauESOnTauShift, 'OSTight%s' %data_bTag, True),
                ("tt_embed","%s/tt_embed_all.root" %preFixTauESOffTauShift, 'OSTight%s' %data_bTag, True),
                ('MCOSRelax','%s/Electroweak.root' %preFixTauESOff, 'OSRelax%s' %data_bTag, False),
                ("MCOSRelax","%s/dy.root" %preFixTauESOn, 'OSRelax%s' %data_bTag, False),
                ("MCOSRelax","%s/TT.root" %preFixTauESOff, 'OSRelax%s' %data_bTag, False),
                ('dataOSRelax','%s/data.root' %preFixData, 'OSRelax%s' %data_bTag, False),
                ('dataOSTight','%s/data.root' %preFixData, 'OSTight%s' %bTag, False)]

if bTagShift != '':
    if scaleOption != 'normal':
        print "ERROR!!!!!!!!!!!!!
    else:
        scaleOption = bTagShift

oFileName = 'combined%s_iso%.1f_%s_%s_%s_%s.root' %(postFix, iso, Relax, pairOption, scaleOption, tail)
trainedMassPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]

sampleConfigsTools =[('VV', '%s/Electroweak_withSingleTop.root' %preFixTauESOff),
                     ('DYJetsToLL', '%s/dy.root' %preFixTauESOn),
                     ('t#bar{t}','%s/TT.root' %preFixTauESOff),
                     ('data','%s/data.root' %preFixData)]



