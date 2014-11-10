#!/usr/bin/env python
import os as os

preFix = "/scratch/zmao/triggerMatch/TMVARegApp_"
postFix = ""
MC_Samples = [#'ZZ_eff_all%s.root' %postFix,
#               'WZJetsTo2L2Q_eff_all.root',
              'W1JetsToLNu_all.root',
              'W2JetsToLNu_all.root',
              'W3JetsToLNu_all.root',
              'DY1JetsToLL_all.root',
              'DY2JetsToLL_all.root',
              'DY3JetsToLL_all.root',
#               'tt_eff_all%s.root' %postFix,
#               'tt_semi_eff_all%s.root' %postFix,
              ]
# QCD_Sample = "dataTotal_all%s.root" %postFix

for iMCSample in MC_Samples:
    inputFile = preFix+iMCSample
    outputFile = inputFile[0:inputFile.rfind('.')]
    command = "python makeTrainingSample.py --i "
    command += "%s --o %s --c tightoppositebTag" %(inputFile, outputFile)
    os.system(command) 

# command = "python Tools/makeTrainingSample.py --i "
# inputFile = preFix+QCD_Sample
# outputFile = inputFile[0:inputFile.rfind('.')]
# command += "%s --o %s --c relaxedsamebTag" %(inputFile, outputFile)
# os.system(command)
