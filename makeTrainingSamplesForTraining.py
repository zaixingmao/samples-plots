#!/usr/bin/env python
import os as os
import makeWholeTools2
import makeWholeSample_cfg

preFixTauOn = "/nfs_scratch/zmao/samples_Iso/tauESOn/normal/"
preFixTauOff = "/nfs_scratch/zmao/samples_Iso/tauESOff/normal/"
preFixData = "/nfs_scratch/zmao/samples_Iso/data/"
outputFileDir = "/nfs_scratch/zmao/samples_Iso/BDT_new/"
postFix = ""
relaxedRegion = 'one1To4'
sign = 'OS'

MC_Samples = [('%s/Electroweak_withSingleTop.root' %preFixTauOff), 
              ('%s/dy.root' %preFixTauOn),
              ('%s/TT.root' %preFixTauOff)
             ]

QCD_Sample = "%s/data.root" %preFixData

iso = 'Tight'
bRegion = 'M'

massPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]

for iMass in massPoints:
    inputFile = preFixTauOn
    inputFile += 'H2hh%i_all.root' %iMass
    outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
    command = "python makeTrainingSample.py --i "
    command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion)
    os.system(command) 

for iMCSample in MC_Samples:
    inputFile = iMCSample
    outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
    command = "python makeTrainingSample.py --i "
    if 'TT.root' in inputFile:
        command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion)
    else:
        command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion L --useLooseForShape 1" %(inputFile, outputFile, iso, sign, relaxedRegion)
    os.system(command)

iso = 'Relax'
bRegion = 'L'
weights = makeWholeTools2.calculateSF(fileList = makeWholeSample_cfg.sampleConfigsTools,
                                      sigRegionOption = 'Tight', 
                                      relaxedRegionOption = makeWholeSample_cfg.Relax, 
                                      verbose = True,
                                      isoTight = 1.0, 
                                      pairOption = makeWholeSample_cfg.pairOption,
                                      massWindow = False,
                                      usePassJetTrigger = True,
                                      nBtag = '')

command = "python makeTrainingSample.py --i "
inputFile = QCD_Sample
outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s --weightOne %.6f --weightTwo %.6f" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion, weights[0], weights[1])

os.system(command)
