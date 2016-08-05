####setup
```bash
cd CMSSW_7_6_3/src
cmsenv

git clone https://github.com/zaixingmao/samples-plots.git
cd samples-plots
git checkout fnal
```

####make samples from ntuples
* Specify samples location, name in `cfg/enVars.py`
* cutSamples currently supports [tt, et, mt, em]
* cuts defined in cutSampleTools.py consists of two stage:
* 1) passCuts --- always applied 
* 2) passAdditionalCuts --- additional cuts 

```bash
git clone https://github.com/elaird/supy.git
cd supy
git checkout tweaks
cd -
mv fnal_cmsJob.sh supy/sites/
mv __init__.py supy/sites/
source env.sh

#running without supy (for fast tests, use -n to indicate how many events you want to run over)
python cutSamples.py --FS et -l /uscms/home/zmao/nobackup/ -n 10

#running locally
supy slice.py --loop 1 --slices 10

#running batch
supy slice.py --loop 1 --slices 10 --batch

# after jobs are complete:
supy slice.py
```

####BDT training
```bash
cd CMSSW_5_3_15/src/TMVA-v4.2.0/test/
source setup.sh
```

```
1) mJJ regression:
    1. specify configs in runRegression.py
    2. python runRegression.py

2) make training samples with regression:
    1. for MC bkg
        python makeTrainingSample.py --i INPUTFILE --o OUTPUTFILE --c tightoppositebTag
    2. for QCD bkg
        python makeTrainingSample.py --i INPUTFILE --o OUTPUTFILE --c relaxedsamebTag
    or use wrapper for all samples, need to specify locations: makeTrainingSamples.py

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
```

####.root file for limits
```
1. specify sample location in cfg/makeWholeSample.py
2. python makeWholeSample.py
```

####plots
```
1. Specify variables to draw, sample location and signal mass point in cfg/draw.py
2. python draw.py
```