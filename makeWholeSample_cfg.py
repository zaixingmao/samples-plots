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
# scaleOption = 'tauDown'
# scaleOption = 'tauDown'
# scaleOption = 'jetUp'
# scaleOption = 'jetDown'
bTagShift = '' # bMisDown,sysUp, sysDown, misUp, misDown 
iso = 1.0
pairOption = 'iso'
checkSpeed = False
postFix = ''
tail = '_withDYEmbed'
Relax = 'one1To4'
thirdLeptonVeto = True
usePassJetTrigger = True
massWindow = True
bTag = 'M'


locationName = 'samples_new'
if pairOption == 'iso':
    locationName = 'samples_Iso'
if pairOption == 'region':
    locationName = 'samples_Region'

preFixTauESOff = '/nfs_scratch/zmao/%s/tauESOff/normal/' %locationName
preFixTauESOn = '/nfs_scratch/zmao/%s/tauESOn/normal/' %locationName
preFixData = '/nfs_scratch/zmao/%s/data/' %locationName

if bTagShift != '':
    if 'Sys' in bTagShift:
        scaleOption = 'bSys'
    else:
        scaleOption = 'bMis'
        
if scaleOption == 'normal' or 'tau' in scaleOption:
    preFixTauESOnDYEmbed = '/nfs_scratch/zmao/%s/tauESOn/%s/' %(locationName, scaleOption)
else:
    preFixTauESOnDYEmbed = '/nfs_scratch/zmao/%s/tauESOn/normal/'%locationName
preFixTauESOn = '/nfs_scratch/zmao/%s/tauESOn/%s/' %(locationName, scaleOption)

if 'tau' not in scaleOption:
    preFixTauESOffVV = '/nfs_scratch/zmao/%s/tauESOff/%s/' %(locationName, scaleOption)
else:
    preFixTauESOffVV = '/nfs_scratch/zmao/%s/tauESOff/normal/' %locationName
preFixTauESOff = '/nfs_scratch/zmao/%s/tauESOff/%s/' %(locationName, scaleOption)



if massWindow:
    tail += '_massWindow'

data_bTag = 'L'
# if bTag == '2M':
#     data_bTag = '2L'

sampleConfigs =[('signals', '%s/signal_new.root' %preFixTauESOn, 'OSTight%s' %bTag, False),
                ("DY_inclusive","%s/dy_new.root" %preFixTauESOn, 'OSTight%s' %bTag, False),
                ("t#bar{t}","%s/TT.root" %preFixTauESOff, 'OSTight%s' %bTag, False),
                ("WJets","%s/WJets_new.root" %preFixTauESOff, 'OSTight%s' %bTag, False),
                ('VV','%s/Electroweak.root' %preFixTauESOffVV, 'OSTight%s' %data_bTag, True),
                ("singleT","%s/singleTop.root" %preFixTauESOffVV, 'OSTight%s' %data_bTag, True),
                ("ZLL","%s/dy.root" %preFixTauESOn, 'OSTight%s' %data_bTag, True),
                ("DY_embed","%s/DY_embed_new.root" %preFixTauESOnDYEmbed, 'OSTight%s' %data_bTag, True),
                ("tt_embed","%s/tt_embed_all_new.root" %preFixTauESOff, 'OSTight%s' %data_bTag, True),
                ('MCOSRelax','%s/Electroweak_withSingleTop.root' %preFixTauESOffVV, 'OSRelax%s' %data_bTag, False),
                ("MCOSRelax","%s/dy_new.root" %preFixTauESOn, 'OSRelax%s' %data_bTag, False),
                ("MCOSRelax","%s/TT.root" %preFixTauESOff, 'OSRelax%s' %data_bTag, False),
                ('dataOSRelax','%s/data.root' %preFixData, 'OSRelax%s' %data_bTag, False),
                ('dataOSTight','%s/data.root' %preFixData, 'OSTight%s' %bTag, False)]

if bTagShift != '':
    oFileName = 'combined%s_iso%.1f_%s_%s_%s_%s.root' %(postFix, iso, Relax, pairOption, bTagShift, tail)
else:
    oFileName = 'combined%s_iso%.1f_%s_%s_%s_%s.root' %(postFix, iso, Relax, pairOption, scaleOption, tail)

trainedMassPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]

sampleConfigsTools =[('VV', '%s/Electroweak_withSingleTop.root' %preFixTauESOffVV),
                     ('DYJetsToLL', '%s/dy_new.root' %preFixTauESOn),
                     ('t#bar{t}','%s/TT.root' %preFixTauESOff),
                     ('data','%s/data.root' %preFixData)]



