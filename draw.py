#!/usr/bin/env python

import varsList
import os
import ROOT as r
from cfg import draw_sync as draw_cfg
import makeWholeTools
import makeWholeSample_cfg


# import drawVarsData_new2

#getHistos(varName, signalSelection, logY, sigBoost, nbins, useData, max, rangeMin, rangeMax, location):
# region = 'INFN_tight' #'tight'
# relaxedRegionOption ='INFN_relaxed'# 'relaxed'

relPath = __file__
script = os.path.abspath(relPath).replace(relPath, "%s" % draw_cfg.drawConfigs['script'])

bTags = ['1M1NonM','2M']
bTagsNone = ['None']
bTags = ['2M']

configs = [('semiTight', 'relaxed', bTags),
#            ('INFN_tight', 'INFN_relaxed', bTagsNone),
#            ('semiTight', 'very_relaxed', bTags)]
#            ('tight', 'relaxed', bTagsNone)
          ]

pu = [True]

def drawPlots(config, usePU):
    region = config[0]
    relaxedRegionOption = config[1]
    weights = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, 
                                         makeWholeSample_cfg.preFixTools,
                                         'SFveto012None', region, relaxedRegionOption, True)
    bTags = config[2]
    for ibTag in bTags:
        bTag = ibTag
        if bTag == '1M':
            weight = weights[0]
        elif bTag == '1M1NonM':
            weight = weights[1]
        elif bTag == '2M':
            weight = weights[2]
        elif bTag == 'None':
            region = 'tight'
            weights = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'SFveto012None', region, relaxedRegionOption, True)
            weight = weights[3]

        for varName, varConfig in draw_cfg.varsRange.items():
            yMax = 2000
            if 'INFN' in region:
                yMax = yMax*0.8
            if bTag == '2M':
                yMax = yMax/10
            if bTag == 'None':
                yMax = yMax*2
            if ('mJJ' in varName) or ('svMass' in varName):
                yMax = yMax*0.6
            elif ('CSVJ1Pt' in varName):
                yMax = yMax*2
            elif ('pt1' in varName):
                yMax = yMax*0.9

            output = 'python %s --location %s  --signal %s' %(script, draw_cfg.drawConfigs['sampleLocation'], draw_cfg.drawConfigs['signal'])
            output += ' --variable %s --nbins %i --setRangeMin %f --setRangeMax %f' %(varName, varConfig[0], varConfig[1], varConfig[2])
            output += ' --setMax %i' %varConfig[3]
            output += ' --sigBoost %i' %varConfig[4]
            output += ' --logY %s' %varConfig[5]
            output += ' --bTag %s' %bTag
            output += ' --predict %s' %varConfig[6]
            output += ' --useData True'
            output += ' --region %s' %region
            output += ' --thirdLeptonVeto True'
            output += ' --weight %.5f' %weight
            output += ' --yMax %i' %yMax
            output += ' --relaxedRegionOption %s' %relaxedRegionOption
            if usePU:
                output += ' --usePUWeight'
            os.system(output)

for iPU in pu:
    for iConfig in configs:
        drawPlots(iConfig, iPU)
