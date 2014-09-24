#!/usr/bin/env python
import os as os

preFix = "TMVARegApp_"
MC_Samples = ['ZZ_eff_all.root',
              'WZJetsTo2L2Q_eff_all.root',
              'W1JetsToLNu_eff2_all.root',
              'W2JetsToLNu_eff2_all.root',
              'W3JetsToLNu_eff2_all.root',
              'DY1JetsToLL_eff2_all.root',
              'DY2JetsToLL_eff2_all.root',
              'DY3JetsToLL_eff2_all.root',
              'tt_eff_all.root',
              'tt_semi_eff_all.root',
              ]
QCD_Sample = "dataTotal_all.root"

for iMCSample in MC_Samples:
    inputFile = preFix+iMCSample
    outputFile = inputFile[0:inputFile.rfind('.')]
    command = "python /afs/hep.wisc.edu/home/zmao/myScripts/H2hh2bbTauTau/python/Tools/makeTrainingSample.py --i "
    command += "%s --o %s --c tightoppositebTag" %(inputFile, outputFile)
    os.system(command) 

command = "python /afs/hep.wisc.edu/home/zmao/myScripts/H2hh2bbTauTau/python/Tools/makeTrainingSample.py --i "
inputFile = preFix+QCD_Sample
outputFile = inputFile[0:inputFile.rfind('.')]
command += "%s --o %s --c relaxedsamebTag" %(inputFile, outputFile)
os.system(command)
