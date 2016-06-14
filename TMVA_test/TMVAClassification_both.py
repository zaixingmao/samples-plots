#!/usr/bin/env python
# @(#)root/tmva $Id$
# ------------------------------------------------------------------------------ #
# Project      : TMVA - a Root-integrated toolkit for multivariate data analysis #
# Package      : TMVA                                                            #
# Python script: TMVAClassification.py                                           #
#                                                                                #
# This python script provides examples for the training and testing of all the   #
# TMVA classifiers through PyROOT.                                               #
#                                                                                #
# The Application works similarly, please see:                                   #
#    TMVA/macros/TMVAClassificationApplication.C                                 #
# For regression, see:                                                           #
#    TMVA/macros/TMVARegression.C                                                #
#    TMVA/macros/TMVARegressionpplication.C                                      #
# and translate to python as done here.                                          #
#                                                                                #
# As input data is used a toy-MC sample consisting of four Gaussian-distributed  #
# and linearly correlated input variables.                                       #
#                                                                                #
# The methods to be used can be switched on and off via the prompt command, for  #
# example:                                                                       #
#                                                                                #
#    python TMVAClassification.py --methods Fisher,Likelihood                    #
#                                                                                #
# The output file "TMVA.root" can be analysed with the use of dedicated          #
# macros (simply say: root -l <../macros/macro.C>), which can be conveniently    #
# invoked through a GUI that will appear at the end of the run of this macro.    #
#                                                                                #
# for help type "python TMVAClassification.py --help"                            #
# ------------------------------------------------------------------------------ #

# --------------------------------------------
# Standard python import
import sys    # exit
import time   # time accounting
import getopt # command line parser
import tool
import ROOT as r
import os
import varsList

# --------------------------------------------

# Default settings for command line arguments
DEFAULT_OUTFNAME = "TMVA.root"
DEFAULT_INFNAME  = "tmva_class_example.root"
DEFAULT_TREESIG  = "TreeS"
DEFAULT_TREEBKG  = "TreeB"
DEFAULT_METHODS  = "Cuts,CutsD,CutsPCA,CutsGA,CutsSA,Likelihood,LikelihoodD,LikelihoodPCA,LikelihoodKDE,LikelihoodMIX,PDERS,PDERSD,PDERSPCA,PDEFoam,PDEFoamBoost,KNN,LD,Fisher,FisherG,BoostedFisher,HMatrix,FDA_GA,FDA_SA,FDA_MC,FDA_MT,FDA_GAMT,FDA_MCMT,MLP,MLPBFGS,MLPBNN,CFMlpANN,TMlpANN,SVM,BDT,BDTD,BDTG,BDTB,RuleFit"
DEFAULT_NTREES = "150"
# Print usage help
def usage():
    print " "
    print "Usage: python %s [options]" % sys.argv[0]
    print "  -m | --methods    : gives methods to be run (default: all methods)"
    print "  -i | --inputfile  : name of input ROOT file (default: '%s')" % DEFAULT_INFNAME
    print "  -o | --outputfile : name of output ROOT file containing results (default: '%s')" % DEFAULT_OUTFNAME
    print "  -n | --nTrees : amount of trees for BDT study (default: '%s')" %DEFAULT_NTREES 

    print "  -t | --inputtrees : input ROOT Trees for signal and background (default: '%s %s')" \
          % (DEFAULT_TREESIG, DEFAULT_TREEBKG)
    print "  -v | --verbose"
    print "  -? | --usage      : print this help message"
    print "  -h | --help       : print this help message"
    print " "

# Main routine
def main():

    try:
        # retrive command line options
        shortopts  = "m:i:n:t:o:vh?"
        longopts   = ["methods=", "inputfile=", "nTrees=", "inputtrees=", "outputfile=", "verbose", "help", "usage"]
        opts, args = getopt.getopt( sys.argv[1:], shortopts, longopts )

    except getopt.GetoptError:
        # print help information and exit:
        print "ERROR: unknown options in argument %s" % sys.argv[1:]
        usage()
        sys.exit(1)

    infname     = DEFAULT_INFNAME
    treeNameSig = DEFAULT_TREESIG
    treeNameBkg = DEFAULT_TREEBKG
    outfname    = DEFAULT_OUTFNAME
    methods     = DEFAULT_METHODS
    nTrees = DEFAULT_NTREES
    verbose     = False
    for o, a in opts:
        if o in ("-?", "-h", "--help", "--usage"):
            usage()
            sys.exit(0)
        elif o in ("-m", "--methods"):
            methods = a
        elif o in ("-i", "--inputfile"):
            infname = a
        elif o in ("-n", "--nTrees"):
            nTrees = a
        elif o in ("-o", "--outputfile"):
            outfname = a
        elif o in ("-t", "--inputtrees"):
            a.strip()
            trees = a.rsplit( ' ' )
            trees.sort()
            trees.reverse()
            if len(trees)-trees.count('') != 2:
                print "ERROR: need to give two trees (each one for signal and background)"
                print trees
                sys.exit(1)
            treeNameSig = trees[0]
            treeNameBkg = trees[1]
        elif o in ("-v", "--verbose"):
            verbose = True

    # Print methods
    mlist = methods.replace(' ',',').split(',')
    print "=== TMVAClassification: use method(s)..."
    for m in mlist:
        if m.strip() != '':
            print "=== - <%s>" % m.strip()

    # Import ROOT classes
    from ROOT import gSystem, gROOT, gApplication, TFile, TTree, TCut
    
    # check ROOT version, give alarm if 5.18 
    if gROOT.GetVersionCode() >= 332288 and gROOT.GetVersionCode() < 332544:
        print "*** You are running ROOT version 5.18, which has problems in PyROOT such that TMVA"
        print "*** does not run properly (function calls with enums in the argument are ignored)."
        print "*** Solution: either use CINT or a C++ compiled version (see TMVA/macros or TMVA/examples),"
        print "*** or use another ROOT version (e.g., ROOT 5.19)."
        sys.exit(1)
    
    # Logon not automatically loaded through PyROOT (logon loads TMVA library) load also GUI
    gROOT.SetMacroPath( "./" )
    gROOT.Macro       ( "./TMVAlogon.C" )    
    gROOT.LoadMacro   ( "./TMVAGui.C" )
    
    # Import TMVA classes from ROOT
    from ROOT import TMVA

    # Output file
    outputFile = TFile( outfname, 'RECREATE' )
    
    # Create instance of TMVA factory (see TMVA/macros/TMVAClassification.C for more factory options)
    # All TMVA output can be suppressed by removing the "!" (not) in 
    # front of the "Silent" argument in the option string
    factory = TMVA.Factory( "TMVAClassification", outputFile, 
                            "!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification" )
    # Set verbosity
    factory.SetVerbose( verbose )
    
    # If you wish to modify default settings 
    # (please check "src/Config.h" to see all available global options)
    #    gConfig().GetVariablePlotting()).fTimesRMS = 8.0
    #    gConfig().GetIONames()).fWeightFileDir = "myWeightDirectory"

    # Define the input variables that shall be used for the classifier training
    # note that you may also use variable expressions, such as: "3*var1/var2*abs(var3)"
    # [all types of expressions that can also be parsed by TTree::Draw( "expression" )]

    
    varList = varsList.varList


    for iVar in varList:
        factory.AddVariable(iVar, 'F')

    #factory.AddVariable( "NBTags",'I' )

    # You can add so-called "Spectator variables", which are not used in the MVA training, 
    # but will appear in the final "TestTree" produced by TMVA. This TestTree will contain the 
    # input variables, the response values of all trained MVAs, and the spectator variables
    print "here"

    massPoint = infname
    preFix = varsList.preFix
    infname = "ZPrime_%s_all_SYNC_%s_noIso%s" %(massPoint, varsList.fs, varsList.tail)
    iFileSig = TFile.Open(preFix+infname)
    sigChain = iFileSig.Get("eventTree_train")
    factory.AddSignalTree(sigChain)

    bkg_list = []
    bkg_trees_list = []
    hist_list = []
    weightsList = []
    for i in range(len(varsList.bkg)):
        bkg_list.append(TFile.Open(preFix+varsList.bkg[i][1]))
        print preFix+varsList.bkg[i][1]
        bkg_trees_list.append(bkg_list[i].Get("eventTree"))
        bkg_trees_list[i].GetEntry(0)

        if bkg_trees_list[i].GetEntries() == 0:
            continue
        factory.AddBackgroundTree( bkg_trees_list[i], 1)
        print "%s:\t\t%.2f" %(varsList.bkg[i][0], bkg_trees_list[i].GetEntries())

    signalWeight     = 1 #0.0159/sigChain.GetEntries() #xs (pb)

    # ====== register trees ====================================================
    factory.SetSignalWeightExpression('weightWithPU')
    factory.SetBackgroundWeightExpression('weightWithPU')

    # To give different trees for training and testing, do as follows:
    #    factory.AddSignalTree( signalTrainingTree, signalTrainWeight, "Training" )
    #    factory.AddSignalTree( signalTestTree,     signalTestWeight,  "Test" )
    
    # Use the following code instead of the above two or four lines to add signal and background 
    # training and test events "by hand"
    # NOTE that in this case one should not give expressions (such as "var1+var2") in the input 
    #      variable definition, but simply compute the expression before adding the event
    #
    #    # --- begin ----------------------------------------------------------
    #    
    # ... *** please lookup code in TMVA/macros/TMVAClassification.C ***
    #    
    #    # --- end ------------------------------------------------------------
    #
    # ====== end of register trees ==============================================    
            
    # Set individual event weights (the variables must exist in the original TTree)
    #    for signal    : factory.SetSignalWeightExpression    ("weight1*weight2");
    #    for background: factory.SetBackgroundWeightExpression("weight1*weight2");
    #factory.SetBackgroundWeightExpression( "weight" )

    # Apply additional cuts on the signal and background sample. 
    # example for cut: mycut = TCut( "abs(var1)<0.5 && abs(var2-0.5)<1" )
        
    mycutSig = TCut( "") 
    mycutBkg = TCut( "" ) 
    
    # Here, the relevant variables are copied over in new, slim trees that are
    # used for TMVA training and testing
    # "SplitMode=Random" means that the input events are randomly shuffled before
    # splitting them into training and test samples
    factory.PrepareTrainingAndTestTree( mycutSig, mycutBkg,
                                        "nTrain_Signal=0:nTrain_Background=0:nTest_Signal=1:nTest_Background=1:SplitMode=Block:NormMode=NumEvents:!V" )
#                                         "nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V" )

    # --------------------------------------------------------------------------------------------------

    # ---- Book MVA methods
    #
    # please lookup the various method configuration options in the corresponding cxx files, eg:
    # src/MethoCuts.cxx, etc, or here: http://tmva.sourceforge.net/optionRef.html
    # it is possible to preset ranges in the option string in which the cut optimisation should be done:
    # "...:CutRangeMin[2]=-1:CutRangeMax[2]=1"...", where [2] is the third input variable

    # Cut optimisation

    # Fisher discriminant (same as LD)
#    if "Fisher" in mlist:
        #factory.BookMethod( TMVA.Types.kFisher, "Fisher", "H:!V:Fisher:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10" )
 #       factory.BookMethod( TMVA.Types.kFisher, "Fisher")
    bdtSetting = '!H:!V:NTrees=%s' %nTrees
    bdtSetting += ':MinNodeSize=2.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=100'
    if "BDT" in mlist:
         factory.BookMethod( TMVA.Types.kBDT, "BDT",bdtSetting)


    # --------------------------------------------------------------------------------------------------
            
    # ---- Now you can tell the factory to train, test, and evaluate the MVAs. 

    # Train MVAs
    factory.TrainAllMethods()

    # Test MVAs
    factory.TestAllMethods()
    
    # Evaluate MVAs
    factory.EvaluateAllMethods()    
    

    # Save the output.
    outputFile.Close()
#     
#     print "=== wrote root file %s\n" % outfname
#     print "=== TMVAClassification is done!\n"
    
    # open the GUI for the result macros    
#     gROOT.ProcessLine( "TMVAGui(\"%s\")" % outfname )
    
    ChangeWeightName = 'mv %s/weights/TMVAClassification_BDT.weights.xml %s/weights/TMVAClassification_BDT.weights_both_%s.xml' %(os.getcwd(), os.getcwd(), massPoint)
    os.system(ChangeWeightName)    
    # keep the ROOT thread running
#     gApplication.Run() 

# ----------------------------------------------------------

if __name__ == "__main__":
    main()
