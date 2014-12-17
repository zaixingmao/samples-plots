#!/usr/bin/env python
import os as os
import makeWholeTools
import makeWholeSample_cfg

# preFix = "/scratch/zmao/BDTStudy/8/260/ClassApp_both_TMVARegApp_"
# preFix = "/scratch/zmao/v3/TMVARegApp_"
preFix = "/nfs_scratch/zmao/fromLogin05/forPlots/"

postFix = ""
# MC_Samples = [('ZZ_all%s.root' %postFix, 2.500), 
#               ('WZJetsTo2L2Q_all.root', 2.207), 
#               ('W1JetsToLNu_all.root', 5400), 
#               ('W2JetsToLNu_all.root', 1750), 
#               ('W3JetsToLNu_all.root', 519), 
#               ('DY1JetsToLL_all.root', 561), 
#               ('DY2JetsToLL_all.root', 181), 
#               ('DY3JetsToLL_all.root', 51.1), 
#               ('tt_all%s.root' %postFix, 26.1975), 
#               ('tt_semi_all%s.root' %postFix, 109.281), 
#               ]

MC_Samples = [('Electroweak.root'), 
              ('signal.root'),
              ('DYJetsToLL_all.root'),
              ('tt.root')]

QCD_Sample = "dataTotal_all%s.root" %postFix

region = '1M3rdLepVeto'
relaxed = 'relaxed'


massPoints = [260, 270, 280, 290, 300, 310, 320, 330, 340, 350]

# for iMass in massPoints:
#     inputFile = preFix
#     inputFile += 'H2hh%i_all.root' %iMass
#     outputFile = inputFile[0:inputFile.rfind('.')]
#     command = "python makeTrainingSample.py --i "
#     command += "%s --o %s --c tightopposite%s" %(inputFile, outputFile, region)
#     os.system(command) 
# 
# for iMCSample in MC_Samples:
#     inputFile = preFix+iMCSample
#     outputFile = inputFile[0:inputFile.rfind('.')]
#     command = "python makeTrainingSample.py --i "
#     command += "%s --o %s --c tightopposite%s " %(inputFile, outputFile, region)
#     os.system(command) 
# 
# weights = [1]
# weights = makeWholeTools.calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012', 'tight', relaxed, False, True)
# command = "python makeTrainingSample.py --i "
# inputFile = preFix+QCD_Sample
# outputFile = inputFile[0:inputFile.rfind('.')]
# command += "%s --o %s --c %sopposite%s --xs %.6f" %(inputFile, outputFile, region,relaxed, weights[0])
# os.system(command)

command = "python makeTrainingSample.py --i "
inputFile = preFix+QCD_Sample
outputFile = inputFile[0:inputFile.rfind('.')]
command += "%s --o %s --c tightopposite%s --xs 1.0" %(inputFile, outputFile, region)
os.system(command)