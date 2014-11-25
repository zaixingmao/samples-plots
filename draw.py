#!/usr/bin/env python

import varsList
import os
import ROOT as r
from cfg import draw_sync as draw_cfg
import makeWholeTools
import makeWholeSample_cfg


# import drawVarsData_new2

#getHistos(varName, signalSelection, logY, sigBoost, nbins, useData, max, rangeMin, rangeMax, location):
region = 'tight'

relPath = __file__
script = os.path.abspath(relPath).replace(relPath, "%s" % draw_cfg.drawConfigs['script'])

bTags = ['1M']


weights = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'SFveto012', region,True, 1.5)
# weights = [0.0511, 0.0511, 0.0511]

for ibTag in bTags:
    bTag = ibTag
    if bTag == '1M':
        weight = weights[0]
    elif bTag == '1M1NonM':
        weight = weights[1]
    elif bTag == '2M':
        weight = weights[2]

    for varName, varConfig in draw_cfg.varsRange.items():
#         if ('pt2' in varName) or ('Pt' in varName):
#             yMax = 100
#         elif ('pt1' in varName):
#             yMax = 80
#         elif varName == 'CSVJ2':
#             yMax = 100
#         elif varName == 'CSVJ1':
#             yMax = 200
#         else:
#             yMax = 50
        yMax = 100
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

        os.system(output)

