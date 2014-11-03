#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array

r.gROOT.SetBatch(True)
massPoints = ['260','300','350']
Vars = 'svMass dRTauTau dRJJ mJJReg'
psfile = 'BDT_Eff_diff_combined.pdf'
c = r.TCanvas("c","Test", 800, 600)
c.SetGrid()

fileList = [('_18.root','16 Variables + fullMassKinFit + chi2',r.kRed),
            ('_17.root','16 Variables + chi2',r.kOrange),  
#             ('_8.root', '%s met fMassKinFit metTauPairDPhi metJ2DPhi' %Vars,r.kOrange),
#             ('_9.root', '%s met chi2KinFit fullMassKinFit metJ2DPhi svPt' %Vars, r.kOrange),
            ('_8.root', '%s met chi2KinFit fullMassKinFit metJ2DPhi' %Vars,r.kGreen+7),
            ('_7.root', '%s met chi2KinFit metJ2DPhi' %Vars,r.kBlack),

            ('_3.root','svMass mJJReg chi2KinFit',r.kBlue-7),
            ('_2.root', 'svMass mJJ' ,r.kMagenta-9),

#             ('%s JJPt' %Vars,r.kOrange),
#             ('%s svPt' %Vars,r.kBlue-7),
#             ('%s fMass' %Vars,r.kBlack),
#             ('%s svPt JJPt' %Vars,r.kMagenta-9),
#             ('svMass mJJReg',r.kGreen+7),
            ]

sigEff = 0.8
bkgEffs = []
lHistList3 = []
l = []
i = 0
for iFileName, iName, iColor in fileList:
    bkgEffs.append(r.TGraph(3))
    bkgEffs[i].SetLineColor(iColor)
#     bkgEffs[i].SetMarkerSize(2)

    i+=1
iMassPoint = 0
for massPoint in massPoints:
    iFileList = []
    for indexFile in range(len(fileList)):
        iFileList.append(('TMVA%s%s' %(massPoint, fileList[indexFile][0]), fileList[indexFile][1], fileList[indexFile][2]))    

    lHistList1=[]
    lHistList2=[]
    f = open('%s.txt' %massPoint,'w')
    ifiles = []
    intMassPoint = int(massPoint)
    effList_both = []
    for i in range(len(iFileList)):
        ifiles.append(r.TFile(iFileList[i][0]))
        keys = ifiles[i].Get("InputVariables_Id").GetListOfKeys()
        f.write("%s Vars_____\n" %iFileList[i][0][8: iFileList[i][0].find('.')])
        for iKey in keys:
            name = iKey.GetName()
            if "__Signal_Id" in name:
                f.write('%s\n' %name[0: name.find("__")])
        f.write('\n')
        effList_both.append(ifiles[i].Get("Method_BDT/BDT/MVA_BDT_rejBvsS"))
        effList_both[i].SetLineColor(iFileList[i][2])
        effList_both[i].SetMarkerSize(1)
        xBin = 	effList_both[i].FindBin(sigEff)
        effList_both[i].SetMarkerStyle(2)
        lHistList2.append((effList_both[i], '%s (sigEff@0.8, bkgEff = %.3f)' %(iFileList[i][1], 1-effList_both[i].GetBinContent(xBin))))
        bkgEffs[i].SetPoint(iMassPoint, intMassPoint, 1-effList_both[i].GetBinContent(xBin))
        if massPoint == '350':
            lHistList3.append((effList_both[i], fileList[i][1]))

    legendPosition = (0.1, 0.2, 0.85, 0.5)
    f.close()


    effList_both[0].SetTitle('Background Rejection VS Signal Efficiency (%s); Signal Efficiency; Background Rejection' %massPoint)
    effList_both[0].SetMinimum(0.5)
    effList_both[0].GetXaxis().SetRangeUser(0.5, 1)
    effList_both[0].Draw('L')
    for j in range(1, len(iFileList)):
        effList_both[j].Draw('sameL')
    line = r.TLine(0.8, 0.5, 0.8, 1)
    line.SetLineColor(r.kRed)
    line.SetLineStyle(2)
    line.Draw('same')

    l.append(tool.setMyLegend(legendPosition, lHistList2))
    l[iMassPoint].Draw('same')

    c.Update()
    if massPoint == '260':
        c.Print('%s(' %psfile)
    if massPoint == '300':
        c.Print('%s' %psfile)
    if massPoint == '350':
        c.Print('%s' %psfile)
        c.Clear()
        bkgEffs[0].SetTitle('Bkg Efficiency with Sig Efficency at %.2f; H Mass; Background Efficiency' %sigEff)

        bkgEffs[0].Draw('APL')
        bkgEffs[0].SetMinimum(0.00)
        bkgEffs[0].SetMaximum(0.2)
        for j in range(1, len(iFileList)):
            bkgEffs[j].Draw('PLsame')
        l.append(tool.setMyLegend((0.3, 0.6, 0.9, 0.9), lHistList3))
        l[iMassPoint+1].Draw('same')
        c.Update()
        c.Print('%s)' %psfile)
    iMassPoint += 1

print 'plot saved at: %s' %psfile