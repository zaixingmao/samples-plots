/**********************************************************************************
 * Project   : TMVA - a Root-integrated toolkit for multivariate data analysis    *
 * Package   : TMVA                                                               *
 * Exectuable: TMVAClassificationApplication                                      *
 *                                                                                *
 * This macro provides a simple example on how to use the trained classifiers     *
 * within an analysis module                                                      *
 **********************************************************************************/

#include <cstdlib>
#include <vector>
#include <iostream>
#include <map>
#include <string>

#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TStopwatch.h"

#include "TMVAGui.C"

#if not defined(__CINT__) || defined(__MAKECINT__)
#include "TMVA/Tools.h"
#include "TMVA/Reader.h"
#include "TMVA/MethodCuts.h"
#endif

using namespace TMVA;

void TMVAClassificationApplication_new(TString myMethodList = "" , TString iFileName = "", TString bkgSample = "", TString sampleLocation = "", TString massPoint = "", TString oFileLocation = "") 
{   
#ifdef __CINT__
   gROOT->ProcessLine( ".O0" ); // turn off optimization in CINT
#endif

   //---------------------------------------------------------------

   // This loads the library
   TMVA::Tools::Instance();

   // Default MVA methods to be trained + tested
   std::map<std::string,int> Use;

   // --- Cut optimisation
   Use["Cuts"]            = 0;
   Use["CutsD"]           = 0;
   Use["CutsPCA"]         = 0;
   Use["CutsGA"]          = 0;
   Use["CutsSA"]          = 0;
   // 
   // 
   // --- Boosted Decision Trees
   Use["BDT"]             = 1; // uses Adaptive Boost
   std::cout << std::endl;
   std::cout << "==> Start TMVAClassificationApplication" << std::endl;

   // Select methods (don't look at this code - not of interest)
   if (myMethodList != "") {
      for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) it->second = 0;

      std::vector<TString> mlist = gTools().SplitString( myMethodList, ',' );
      for (UInt_t i=0; i<mlist.size(); i++) {
         std::string regMethod(mlist[i]);

         if (Use.find(regMethod) == Use.end()) {
            std::cout << "Method \"" << regMethod 
                      << "\" not known in TMVA under this name. Choose among the following:" << std::endl;
            for (std::map<std::string,int>::iterator it = Use.begin(); it != Use.end(); it++) {
               std::cout << it->first << " ";
            }
            std::cout << std::endl;
            return;
         }
         Use[regMethod] = 1;
      }
   }

   // --------------------------------------------------------------------------------------------------

   // --- Create the Reader object

   TMVA::Reader *reader = new TMVA::Reader("!Color:!Silent" );   
    TString weightTail = "_";
    weightTail = weightTail + massPoint;
   // Create a set of variables and declare them to the reader
   // - the variable names MUST corresponds in name and type to those given in the weight file(s) used

   Float_t var1, var2, var3, var4;
   reader->AddVariable( "met", &var1);
   reader->AddVariable( "pZetaCut", &var2 );
   reader->AddVariable( "cosDPhi", &var3 );
   reader->AddVariable( "m_eff", &var4 );


   // Spectator variables declared in the training have to be added to the reader, too
//    Float_t spec1,spec2,spec3,spec4,spec5,spec6,spec7,spec8,spec9,spec10,spec11,spec12,spec13,spec14,spec15,spec16,spec17,spec18,spec19;
//    reader->AddSpectator( "sampleName2", &spec1);
//    reader->AddSpectator( "svMass", &spec2);
//    reader->AddSpectator( "met", &spec3);
//    reader->AddSpectator( "fMass", &spec4);
//    reader->AddSpectator( "CSVJ2", &spec5);
//    reader->AddSpectator( "PUWeight", &spec6);
//    reader->AddSpectator( "chi2KinFit", &spec7);
//    reader->AddSpectator( "category2", &spec8);
//    reader->AddSpectator( "triggerEff", &spec9);
//    reader->AddSpectator( "initEvents", &spec10);
//    reader->AddSpectator( "xs", &spec11);
//    reader->AddSpectator( "LUMI", &spec12);
//    reader->AddSpectator( "iso1_1", &spec13);
//    reader->AddSpectator( "iso2_1", &spec14);
//    reader->AddSpectator( "NBTags", &spec15);
//    reader->AddSpectator( "ZLL", &spec16);
//    reader->AddSpectator( "ZTT", &spec17);
//    reader->AddSpectator( "embeddedWeight", &spec18);
//    reader->AddSpectator( "decayModeWeight", &spec19);

//    Float_t Category_cat1, Category_cat2, Category_cat3;
//    if (Use["Category"]){
//       // Add artificial spectators for distinguishing categories
//       reader->AddSpectator( "Category_cat1 := var3<=0",             &Category_cat1 );
//       reader->AddSpectator( "Category_cat2 := (var3>0)&&(var4<0)",  &Category_cat2 );
//       reader->AddSpectator( "Category_cat3 := (var3>0)&&(var4>=0)", &Category_cat3 );
//    }

   // --- Book the MVA methods
   // Book method(s)
  TString weightFileName = "/home/zmao/CMSSW_7_2_4/src/TMVA-v4.2.0/test/weights/TMVAClassification_BDT.weights_";
  weightFileName += bkgSample;
  weightFileName += weightTail;
  reader->BookMVA("BDT method", weightFileName+".xml" ); 

   
   // Book output histograms
   UInt_t nbin = 200;
   TH1F   *histBdt(0);
   histBdt = new TH1F( "MVA_BDT",  "MVA_BDT", nbin, -1.0, 1.0);

   // Prepare input tree (this must be replaced by your data source)
   // in this example, there is a toy tree with signal and one with background events
   // we'll later on use only the "signal" events for the test in this example.
   //   
   TFile *input(0);
   TString fileName = iFileName;
   TString fname = sampleLocation;
   fname += fileName;
   TString oFileName = oFileLocation;
//    oFileName += "ClassApp_" + bkgSample;
//    oFileName += "_";
   oFileName += fileName;

   if (!gSystem->AccessPathName( fname )) 
      input = TFile::Open(fname); // check if file in local directory exists
   if (!input) {
      std::cout << "ERROR: could not open data file: "<<fname<< std::endl;
      exit(1);
   }
   std::cout << "--- TMVAClassificationApp    : Using input file: " << input->GetName() << std::endl;

   // --- Event loop

   // Prepare the event tree
   // - here the variable names have to corresponds to your tree
   // - you can use the same variables as above which is slightly faster,
   //   but of course you can use different ones and copy the values inside the event loop
   //
   std::cout << "--- Select signal sample" << std::endl;
   TTree* theTree = (TTree*)input->Get("Ntuple");
   TFile *target  = new TFile( oFileName,"RECREATE" );
   TTree *newTree = theTree->CloneTree();
   Float_t BDT;
   TBranch *branchBDT = newTree->Branch("BDT_"+bkgSample,&BDT,"BDT/F");

   TH1F *eventWeights = (TH1F*)input->Get("eventWeights"); 
   TH1F *eventCountWeighted = (TH1F*)input->Get("eventCountWeighted"); 
   TH1F *eventCount = (TH1F*)input->Get("eventCount"); 

   reader->AddVariable( "met", &var1);
   reader->AddVariable( "pZetaCut", &var2 );
   reader->AddVariable( "cosDPhi", &var3 );
   reader->AddVariable( "m_eff", &var4 );

   theTree->SetBranchAddress( "met", &var1);
   theTree->SetBranchAddress( "pZetaCut", &var2);
   theTree->SetBranchAddress( "cosDPhi", &var3 );
   theTree->SetBranchAddress( "m_eff", &var4 );

   //to get initial pre-processed events
//    TH1F* cutFlow = (TH1F*)input->Get("preselection");

   // Efficiency calculator for cut method
   Int_t    nSelCutsGA = 0;
   Double_t effS       = 0.7;

   std::vector<Float_t> vecVar(4); // vector for EvaluateMVA tests

   std::cout << "--- Processing: " << theTree->GetEntries() << " events" << std::endl;
   TStopwatch sw;
   sw.Start();
   for (Long64_t ievt=0; ievt<theTree->GetEntries();ievt++) {
      if (ievt%1000 == 0) std::cout << "--- ... Processing event: " << ievt << std::endl;
      theTree->GetEntry(ievt);
      // --- Return the MVA outputs and fill into histograms

      if (Use["CutsGA"]) {
         // Cuts is a special case: give the desired signal efficienciy
         Bool_t passed = reader->EvaluateMVA( "CutsGA method", effS );
         if (passed) nSelCutsGA++;
      }
      BDT = reader->EvaluateMVA( "BDT method");
      histBdt->Fill(BDT);
      branchBDT->Fill();
   }

   // Get elapsed time
   sw.Stop();
   std::cout << "--- End of event loop: "; sw.Print();

   // Get efficiency for cuts classifier
   if (Use["CutsGA"]) std::cout << "--- Efficiency for CutsGA method: " << double(nSelCutsGA)/theTree->GetEntries()
                                << " (for a required signal efficiency of " << effS << ")" << std::endl;

   if (Use["CutsGA"]) {

      // test: retrieve cuts for particular signal efficiency
      // CINT ignores dynamic_casts so we have to use a cuts-secific Reader function to acces the pointer  
      TMVA::MethodCuts* mcuts = reader->FindCutsMVA( "CutsGA method" ) ;

      if (mcuts) {      
         std::vector<Double_t> cutsMin;
         std::vector<Double_t> cutsMax;
         mcuts->GetCuts( 0.7, cutsMin, cutsMax );
         std::cout << "--- -------------------------------------------------------------" << std::endl;
         std::cout << "--- Retrieve cut values for signal efficiency of 0.7 from Reader" << std::endl;
         for (UInt_t ivar=0; ivar<cutsMin.size(); ivar++) {
            std::cout << "... Cut: " 
                      << cutsMin[ivar] 
                      << " < \"" 
                      << mcuts->GetInputVar(ivar)
                      << "\" <= " 
                      << cutsMax[ivar] << std::endl;
         }
         std::cout << "--- -------------------------------------------------------------" << std::endl;
      }
   }

   // --- Write histograms

   histBdt->Write();
   eventWeights->Write();
   eventCountWeighted->Write();
   eventCount->Write();

//    cutFlow->Write();
   newTree->Write();
   target->Close();

   std::cout << "--- Created root file: \""<<oFileName<<"\" containing the MVA output histograms" << std::endl;
  
   delete reader;
    
   std::cout << "==> TMVAClassificationApplication is done!" << endl << std::endl;
} 
