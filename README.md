####setup
```bash
cd CMSSW_5_3_15/src
cmsenv
git clone https://github.com/zaixingmao/samples-plots.git
cd samples-plots
```

####make samples from ntuples
* Specify samples location, name in samples-plots/python/Tools/enVars.py
* python samples-plots/python/Tools/cutSamples.py -l LOCATIONOFOUTPUTFILE
######to combined data, since we have A, B, C, D,
1. generate A, B, C, D separately in the same location (with no other sample in that directory)
2. specify that location in samples-plots/python/Tools/enVars.py
3. `python samples-plots/python/Tools/cutSamples.py -a True -l LOCATIONOFOUTPUTFILE`  # (the option -a tells cutSample to simply add the files with mine format)

####BDT training
```bash
cd CMSSW_5_3_15/src/TMVA-v4.2.0/test/
source setup.sh
```

1) mJJ regression:
    1. specify configs in runRegression.py
    2. python runRegression.py

2) make training samples with regression:
    1. for MC bkg
        python samples-plots/python/Tools/makeTrainingSample.py --i INPUTFILE --o OUTPUTFILE --c tightoppositebTag
    2. for QCD bkg
        python samples-plots/python/Tools/makeTrainingSample.py --i INPUTFILE --o OUTPUTFILE --c relaxedsamebTag
    or use wrapper for all samples, need to specify locations: samples-plots/python/Tools/makeTrainingSamples.py

3) train BDT:
    1. specify sample location in TMVA-v4.2.0/test/TMVAClassification_both.py
    2. specify input variables in TMVA-v4.2.0/test/varsList.py
    3. cd TMVA-v4.2.0/test/
    3. python runBDTClassification.py
    4. make sure that the last training is what you want to use

4) apply BDT:
    1. specify input variables in TMVA-v4.2.0/test/TMVAClassificationApplication_new.C
    2. specify samples in TMVA-v4.2.0/test/runClassification.py
    3. cd TMVA-v4.2.0/test/
    3. python runClassification.py


####.root file for limits
1. specify sample location in samples-plots/python/Tools/makeWholeSample_cfg.py
2. python samples-plots/python/Tools/makeWholeSample.py

####plots
1. Specify variables to draw, sample location and signal mass point in samples-plots/python/Tools/draw_cfg.py
2. python samples-plots/python/Tools/draw.py
