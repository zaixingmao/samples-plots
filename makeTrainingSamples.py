#!/usr/bin/env python
import os as os
import makeWholeTools2
import makeWholeSample_cfg

# preFix = "/scratch/zmao/BDTStudy/8/260/ClassApp_both_TMVARegApp_"
# preFix = "/scratch/zmao/v3/TMVARegApp_"
# preFix = "/nfs_scratch/zmao/fromLogin05/forPlots/"
preFixTauOn = "/nfs_scratch/zmao/samples/tauESOn/normal/"
preFixTauOff = "/nfs_scratch/zmao/samples/tauESOff/normal/"
preFixData = "/nfs_scratch/zmao/samples/data/"
outputFileDir = "/nfs_scratch/zmao/samples/BDT_1.0/"
postFix = ""

MC_Samples = [#('%s/Electroweak_withSingleTop.root' %preFixTauOff), 
              ('%s/dy.root' %preFixTauOn),
              #('%s/TT.root' %preFixTauOff)
             ]

SamplesForRerunning = [('%s/DY_embed.root' %preFixTauOn), 
                       ('%s/tt_embed_all.root' %preFixTauOff)]

QCD_Sample = "%s/data.root" %preFixData

iso = 'Tight'
sign = 'OS'
relaxedRegion = 'one1To4'
bRegion = 'M'

massPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]

for iMass in massPoints:
    inputFile = preFixTauOn
    inputFile += 'H2hh%i_all.root' %iMass
    outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
    command = "python makeTrainingSample.py --i "
    command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion)
#     os.system(command) 

for iMCSample in MC_Samples:
    inputFile = iMCSample
    outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
    command = "python makeTrainingSample.py --i "
    command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion)
#     command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion L --useLooseForShape 1" %(inputFile, outputFile, iso, sign, relaxedRegion)
    os.system(command)

inputFile = "%s/data.root" %preFixData
outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
command = "python makeTrainingSample.py --i "
command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion)
# os.system(command)

iso = 'Tight'
sign = 'OS'
bRegion = 'L'

for iRerunSample in SamplesForRerunning:
    inputFile = iRerunSample
    outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
    command = "python makeTrainingSample.py --i "
    command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion)
#     os.system(command) 

iso = 'Relax'
sign = 'OS'
bRegion = 'L'

for iRerunMCSample in MC_Samples:
    inputFile = iRerunMCSample
    outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
    command = "python makeTrainingSample.py --i "
    command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion)
#     os.system(command) 

# iso = 'Relax'
# weights = makeWholeTools2.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'SF12', 'Tight', relaxedRegion, True, 1.0, makeWholeSample_cfg.pairOption, False)
# 
# command = "python makeTrainingSample.py --i "
# inputFile = QCD_Sample
# outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
# command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s --weightOne %.6f --weightTwo %.6f" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion, weights[0], weights[1])
# 
# os.system(command)
