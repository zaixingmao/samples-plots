#!/usr/bin/env python

import varsList
import os
import ROOT as r
from cfg import draw as draw_cfg

# import drawVarsData_new2

#getHistos(varName, signalSelection, logY, sigBoost, nbins, useData, max, rangeMin, rangeMax, location):
region = 'LL'

relPath = __file__
script = os.path.abspath(relPath).replace(relPath, "%s" % draw_cfg.drawConfigs['script'])

for varName, varConfig in draw_cfg.varsRange.items():

    output = 'python %s --location %s  --signal %s' %(script, draw_cfg.drawConfigs['sampleLocation'], draw_cfg.drawConfigs['signal'])

    output += ' --variable %s --nbins %i --setRangeMin %f --setRangeMax %f' %(varName, varConfig[0], varConfig[1], varConfig[2])
    output += ' --setMax %i' %varConfig[3]
    output += ' --sigBoost %i' %varConfig[4]
    output += ' --logY %s' %varConfig[5]
    output += ' --bTag True'
    output += ' --predict %s' %varConfig[6]
    output += ' --useData True'
    output += ' --region %s' %region
#     output += ' --unit %s' %varConfig[7]

    os.system(output)

