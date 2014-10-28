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

fileList = [# ('16 Variables',r.kGreen), 
    #             ('TMVA%s_10.root' %massPoint,'10 Variables (Highest rank)',r.kGreen),
    #             ('TMVA%s_9.root' %massPoint,'9 Variables (10 Variables drop MEt)',r.kBlue),
    #             ('TMVA%s_8.root' %massPoint,'8 Variables (Highest rank)',r.kRed-7),
    #             ('TMVA%s_6.root' %massPoint,'6 Variables (Highest rank)',r.kBlack),
            ('16 Variables + fullMass', r.kRed),
            ('16 Variables + fullMassKinFit',r.kGreen), 
            ('svMass svPt dRJJ mJJReg met CSVJ2 fMassKinFit metSvTauPairDPhi',r.kMagenta-9),
            ('svMass svPt dRJJ mJJReg met CSVJ2 fMass metSvTauPairDPhi',r.kOrange),

#             ('16 Variables + tau1MVA + tau2MVA',r.kBlue),
#             ('16 Variables + fullMassKinFit + tau1MVA + tau2MVA',r.kOrange),
#             ('svMass svPt dRJJ mJJReg met tau1MVA tau2MVA CSVJ2 fMassKinFit',r.kMagenta-9),
#             ('svMass svPt dRJJ mJJReg met tau1MVA tau2MVA CSVJ2 fMassKinFit metSvTauPairDPhi',r.kBlack),
            ('svMass mJJReg MassKinFit',r.kBlue-7),

#             ('%s met tau1MVA tau2MVA' %Vars,r.kGreen+7),

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
for iName, iColor in fileList:
    bkgEffs.append(r.TGraph(3))
    bkgEffs[i].SetLineColor(iColor)
#     bkgEffs[i].SetMarkerSize(2)

    i+=1
iMassPoint = 0
for massPoint in massPoints:
    iFileList = [# ('TMVA%s_16.root' %massPoint, fileList[0][0], fileList[0][1]), 
                ('TMVA%s_17.root' %massPoint, fileList[0][0], fileList[0][1]),
                ('TMVA%s_17_kinFit.root' %massPoint, fileList[1][0], fileList[1][1]),
                ('TMVA%s_8_kinFit2.root' %massPoint, fileList[2][0], fileList[2][1]),
                ('TMVA%s_8.root' %massPoint, fileList[3][0], fileList[3][1]),

#                 ('TMVA%s_18_kinFit.root' %massPoint, fileList[2][0], fileList[2][1]),
#                 ('TMVA%s_19_kinFit.root' %massPoint, fileList[3][0], fileList[3][1]),
#                 ('TMVA%s_9_kinFit.root' %massPoint, fileList[4][0], fileList[4][1]),
#                 ('TMVA%s_10_kinFit2.root' %massPoint, fileList[5][0], fileList[5][1]),
                ('TMVA%s_3_kinFit2.root' %massPoint, fileList[4][0], fileList[4][1]),

#                 ('TMVA%s_7_kinFit.root' %massPoint, fileList[5][0], fileList[5][1]),

# 
#                 ('TMVA%s_5.root' %massPoint, fileList[2][0], fileList[2][1]),
#                 ('TMVA%s_5_1.root' %massPoint, fileList[3][0], fileList[3][1]),
#                 ('TMVA%s_5_2.root' %massPoint, fileList[4][0], fileList[4][1]),
#                 ('TMVA%s_6.root' %massPoint, fileList[5][0], fileList[5][1]),
#                 ('TMVA%s_2.root' %massPoint, fileList[6][0], fileList[6][1]),
                ]

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
            lHistList3.append((effList_both[i], fileList[i][0]))

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
        bkgEffs[0].SetMaximum(0.15)
        for j in range(1, len(iFileList)):
            bkgEffs[j].Draw('PLsame')
        l.append(tool.setMyLegend((0.3, 0.6, 0.9, 0.9), lHistList3))
        l[iMassPoint+1].Draw('same')
        c.Update()
        c.Print('%s)' %psfile)
    iMassPoint += 1

print 'plot saved at: %s' %psfile