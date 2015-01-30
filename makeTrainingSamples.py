#!/usr/bin/env python
import os as os
import makeWholeTools2
import makeWholeSample_cfg

# preFix = "/scratch/zmao/BDTStudy/8/260/ClassApp_both_TMVARegApp_"
# preFix = "/scratch/zmao/v3/TMVARegApp_"
# preFix = "/nfs_scratch/zmao/fromLogin05/forPlots/"
preFixTauOn = "/nfs_scratch/zmao/samples_new/tauESOn/"
preFixTauOff = "/nfs_scratch/zmao/samples_new/tauESOff/"
preFixData = "/nfs_scratch/zmao/samples_new/data/"
outputFileDir = "/nfs_scratch/zmao/samples_new/BDT/"
postFix = ""

shifts = ['normal','tauUp','tauDown', 'jetUp', 'jetDown','bSys', 'bMis'] 
shifts = ['bSys', 'bMis'] 


#Make Data in OSTight
iso = 'Tight'
sign = 'OS'
relaxedRegion = 'one1To4'
bRegion = 'M'
inputFile = "%s/data.root" %preFixData
outputFile = '%s/%s' %(outputFileDir, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
command = "python makeTrainingSample.py --i "
command += "%s --o %s --iso %s --sign %s --relaxRegion %s --bRegion %s" %(inputFile, outputFile, iso, sign, relaxedRegion, bRegion)
# os.system(command)


#Make samples for application

samples = [# (preFixTauOff, 'Electroweak_withSingleTop.root'),
#            (preFixTauOff, 'Electroweak.root'), 
#            (preFixTauOff, 'singleTop.root'), 
           (preFixTauOff, 'WJets.root'), 
           (preFixTauOn, 'dy.root'),
#            (preFixTauOff, 'TT.root'),
#            (preFixTauOn, 'DY_embed.root'), 
#            (preFixTauOff, 'tt_embed_all.root')
            ]


sign = 'OS'
relaxedRegion = 'one1To4'
massPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]
for iShift in shifts:
    outputFileDir2 = outputFileDir + '/' + iShift
    if not os.path.isdir(outputFileDir2):
        os.makedirs(outputFileDir2)
    for iMass in massPoints:
        inputFile = preFixTauOn
        inputFile += iShift
        inputFile += '/H2hh%i_all.root' %iMass
        outputFile = '%s/%s' %(outputFileDir2, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
        command = "python makeTrainingSample.py --i "
        command += "%s --o %s --sign %s --relaxRegion %s --iso %s" %(inputFile, outputFile, sign, relaxedRegion, 'Tight')
#         os.system(command) 

    for iLocation, iSample in samples:
        inputFile = iLocation + '/' + iShift
        inputFile += '/' + iSample
        outputFile = '%s/%s' %(outputFileDir2, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
        command = "python makeTrainingSample.py --i "
        command += "%s --o %s --sign %s --relaxRegion %s --iso %s" %(inputFile, outputFile, sign, relaxedRegion, 'Relax')
        os.system(command) 

    for iLocation, iSample in samples:
        inputFile = iLocation + '/' + iShift
        inputFile += '/' + iSample
        outputFile = '%s/%s' %(outputFileDir2, inputFile[inputFile.rfind('/'):inputFile.rfind('.')])
        command = "python makeTrainingSample.py --i "
        command += "%s --o %s --sign %s --relaxRegion %s --iso %s" %(inputFile, outputFile, sign, relaxedRegion, 'Tight')
        os.system(command) 
