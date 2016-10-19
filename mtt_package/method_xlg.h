#ifndef method_xlg_h
#define method_xlg_h

#include <TH2.h>
#include <TStyle.h>
#include <TCanvas.h>
#include "TLorentzVector.h"
#include "TFile.h"
#include "TLegend.h"
#include "TString.h"
#include <fstream>
#include "TRandom.h"
#include "TMath.h"
#include "TArrow.h"
#include <iostream>

TH2F* h_Minvvis_pperp[3];

void load_pdf_xlg(){
  TFile* file_pdf = new TFile("mtt_package/jpf_DY-50_LO.root", "read");
  for(int i=0; i<3; i++) {
    h_Minvvis_pperp[i] = (TH2F*) file_pdf -> Get(Form("h_Minvvis_pperp_%i", i));
    //cout<<i<<""<<h_Minvvis_pperp[i] -> Integral()<<endl;
  }
  //   delete file_pdf;
}

double cal_mtt_xlg(TLorentzVector P_vis_0, TLorentzVector P_vis_1, int vis_type_0, int vis_type_1, 
		   double MET_et_x, double MET_et_y, double sigma_MET, double mtt_max, double mtt_wbin){

  TLorentzVector P_vis[2];
  int vis_type[2];
  double MET_et[2];

  P_vis[0] = P_vis_0;
  P_vis[1] = P_vis_1;
  vis_type[0] = vis_type_0;
  vis_type[1] = vis_type_1;
  MET_et[0] = MET_et_x;
  MET_et[1] = MET_et_y;


  double vis_pt[2];
  double vis_eta[2];
  double vis_phi[2];
  for(int i=0; i<2; i++){
    vis_pt[i] = P_vis[i].Perp();
    vis_eta[i]= P_vis[i].Eta();
    vis_phi[i]= P_vis[i].Phi();
  }
  double MET_etx = MET_et[0];
  double MET_ety = MET_et[1];


  const int Nsampling = 200;//200;
  double Minvov[2];
  double invp[2];
  double vispz[2];
  double invE[2];
  double visp[2];
  double visE[2];
  double visEcm[2];
  double cosvl[2];
  double ptau[2];
  double mtt;
  double costt = cos((P_vis[0].Vect()).Angle(P_vis[1].Vect()));
  double gammabeta[2];
  double pcm[2];
  double pzcm[2];
  double ptcm[2];
  int option[2] = {1, -1};
  double missetx;
  double missety;
  double MET_resolution = 10;//3.5;
  //MET_resolution = 0.7*sqrt(MET_sumet);
  MET_resolution = sigma_MET;
  double mmax = mtt_max;
  int Nbins = mtt_max/mtt_wbin;
  TH1F* h1 = new TH1F("h1", "", Nbins, 0, mmax);
#if 1
  for(int i1=0; i1<Nsampling; i1++){
    for(int i2=0; i2<Nsampling; i2++){
      for(int j=0; j<2; j++){
	visp[j] = vis_pt[j]*cosh(vis_eta[j]);
	if(vis_type[j]<0) {
	  h_Minvvis_pperp[0] -> GetRandom2(Minvov[j], ptcm[j]);
	}
	else if(vis_type[j]==1) {
	  h_Minvvis_pperp[1] -> GetRandom2(Minvov[j], ptcm[j]);
	}
	else if(vis_type[j]==3) {
	  h_Minvvis_pperp[2] -> GetRandom2(Minvov[j], ptcm[j]);
	}
	pcm[j] = (1.777*1.777 - Minvov[j]*Minvov[j])/2.0/1.777;
	pzcm[j] = sqrt(pcm[j]*pcm[j] - ptcm[j]*ptcm[j]);
	vispz[j] = sqrt(visp[j]*visp[j] - ptcm[j]*ptcm[j]);
	if(vis_type[j]<0) {
	  visEcm[j] = pcm[j];
	  visE[j] = visp[j];
	}
	else {
	  visEcm[j] = sqrt(pcm[j]*pcm[j] + Minvov[j]*Minvov[j]);
	  visE[j] = sqrt(visp[j]*visp[j] + Minvov[j]*Minvov[j]);
	}
      }


      for(int j0=0; j0<2; j0++){ 
	gammabeta[0] = (visEcm[0]*vispz[0]+option[j0]*visE[0]*pzcm[0])/(visEcm[0]*visEcm[0]-pzcm[0]*pzcm[0]);
	if(gammabeta[0]!=gammabeta[0] || gammabeta[0]<0) continue;
	ptau[0] = gammabeta[0]*1.777;
	invE[0] = sqrt(ptau[0]*ptau[0] + 1.777*1.777) - visE[0];
	if(vis_type[0]<0){
	  invp[0] = sqrt(invE[0]*invE[0]-Minvov[0]*Minvov[0]);
	}
	else invp[0] = invE[0];

	for(int j1=0; j1<2; j1++){
	  gammabeta[1] = (visEcm[1]*vispz[1]+option[j1]*visE[1]*pzcm[1])/(visEcm[1]*visEcm[1]-pzcm[1]*pzcm[1]);
	  if(gammabeta[1]!=gammabeta[1] || gammabeta[1]<0) continue;
	  //if(j0!=0 || j1!=0) continue;
	  ptau[1] = gammabeta[1]*1.777;
	  invE[1] = sqrt(ptau[1]*ptau[1] + 1.777*1.777) - visE[1];
	  if(vis_type[1]<0){
	    invp[1] = sqrt(invE[1]*invE[1]-Minvov[1]*Minvov[1]);
	  }
	  else invp[1] = invE[1];

	  mtt = sqrt(2*1.777*1.777+2*sqrt(ptau[0]*ptau[0]+1.777*1.777)*sqrt(ptau[1]*ptau[1]+1.777*1.777)-2*ptau[0]*ptau[1]*costt);
	  double weight = 1.0;
	  missetx = invp[0]/cosh(vis_eta[0])*cos(vis_phi[0]) + invp[1]/cosh(vis_eta[1])*cos(vis_phi[1]);
	  missety = invp[0]/cosh(vis_eta[0])*sin(vis_phi[0]) + invp[1]/cosh(vis_eta[1])*sin(vis_phi[1]);
	  weight = 1.0/sqrt(2.0*M_PI)/MET_resolution*exp(-0.5*pow(missetx-MET_etx,2)/pow(MET_resolution,2))*1.0/sqrt(2.0*M_PI)/MET_resolution*exp(-0.5*pow(missety-MET_ety,2)/pow(MET_resolution,2));
	  h1 -> Fill(mtt, weight);
	}
      }
    }
  }
#endif
#if 1
  double mtt_xlg = h1 -> GetBinCenter(h1->GetMaximumBin());
#endif
  if(h1->GetMaximumBin() == 1) mtt_xlg = -1;
#if 0
  h1 -> Scale(1.0/h1 -> Integral());
  TCanvas* C1 = new TCanvas("C1", "", 10, 10, 800, 600);
  h1 -> Draw("hist");
  h1 -> SetLineWidth(2);
  h1 -> GetXaxis() -> SetTitle("M(#tau#tau) [GeV/c^{2}]");
  h1 -> GetYaxis() -> SetRangeUser(0, 1.2*h1->GetMaximum());
  TLegend* leg1 = new TLegend(0.6, 0.6, 0.9, 0.9);
  leg1 -> AddEntry(h1, "One event (ME)", "L");
  leg1 -> SetBorderSize(0);
  leg1 -> SetFillStyle(0);
  leg1 -> Draw();
  C1 -> SaveAs(Form("mtt_package/event/C1_%i_%i.pdf",  vis_type[0], vis_type[1]));
  delete C1;
#endif
  delete h1;
  return  mtt_xlg;
}

#endif
