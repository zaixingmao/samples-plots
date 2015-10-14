#!/usr/bin/env python

import ROOT as r
import tool
import array

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
met = lvClass()

def getVar(tree, varName, leg1, leg2):
    if varName == 'mass_vis':
        return getattr(tree, "%s_%s_Mass" %(leg1, leg2))
    if varName == "mass_withMEt":
        l1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
        l2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)
        met.SetCoordinates(tree.pfMetEt, 0.0, tree.pfMetPhi, 0.0)
        return (l1 + l2 + met).mass()
    if varName == "mass_gen":
        genName = "Gen"
        if not ('t' in leg1):
            genName = genName + "Tau"
        l1.SetCoordinates(getattr(tree, "%s%sPt" %(leg1, genName)),
                          getattr(tree, "%s%sEta" %(leg1, genName)),
                          getattr(tree, "%s%sPhi" %(leg1, genName)),
                          getattr(tree, "%s%sMass" %(leg1, genName)))
        genName = "Gen"
        if not ('t' in leg2):
            genName = genName +"Tau"
        l2.SetCoordinates(getattr(tree, "%s%sPt" %(leg2, genName)),
                          getattr(tree, "%s%sEta" %(leg2, genName)),
                          getattr(tree, "%s%sPhi" %(leg2, genName)),
                          getattr(tree, "%s%sMass" %(leg2, genName)))
        if l1.pt()>0 and l2.pt()>0:
            return (l1 + l2).mass()
        else:
            return -10
    if varName == "mass_svfit":
        return tree.pfmet_svmc_mass

def getLegNames(FS):
    if FS[0] == FS[1]:
        return "%s1" %FS[0], "%s2" %FS[0]
    else:
        return "%s" %FS[0], "%s" %FS[1]

def loop_through_files(inputFile, varsDict, FS, resolution = False):
    leg1, leg2 = getLegNames(FS)
    file = r.TFile(inputFile)    
    tree = file.Get('Ntuple')
    #eventCountWeighted = file.Get('eventCountWeighted').GetBinContent(1)
    nEntries = tree.GetEntries()
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'Looping sample %s' %(inputFile), iEntry-1)
        if tree.q_1 == tree.q_2:
            continue
        if resolution:
            for iKey in varsDict.keys():
                varsDict[iKey][0].Fill((getVar(tree, iKey, leg1, leg2) - getVar(tree, 'mass_gen', leg1, leg2))/getVar(tree, 'mass_gen', leg1, leg2))
        else:
            for iKey in varsDict.keys():
                varsDict[iKey][0].Fill(getVar(tree, iKey, leg1, leg2))
    return varsDict

def run(mass, FS):
    inputFile = '/user_data/elaird/svSkim-sep18/ZPrime_%s_all_SYNC_%s_inclusive.root' %(mass, FS)
    bins = array.array('d', range(0, 1000, 50) + range(1000, 4000, 100))
    bins2 = array.array('d', range(0, 1000, 50) + range(1000, 8000, 100))

    maximum = 0.005
    if mass == "2000":
        bins = array.array('d', range(0, 1000, 50) + range(1000, 3000, 100))
    if mass == '1000':
        bins = array.array('d', range(0, 1000, 50) + range(1000, 1500, 100))
        maximum = 0.01

    varsDict = {"mass_vis": (r.TH1D("mass_vis_%s_%s" %(mass, FS), "", len(bins)-1, bins), r.kRed),
                "mass_gen": (r.TH1D("mass_gen_%s_%s" %(mass, FS), "", len(bins)-1, bins), r.kBlue),
                "mass_withMEt": (r.TH1D("mass_withMEt_%s_%s" %(mass, FS), "", len(bins)-1, bins), r.kGreen),
                "mass_svfit": (r.TH1D("mass_svfit_%s_%s" %(mass, FS), "", len(bins)-1, bins), r.kBlack),
                }
    varsDict2 = {"mass_vis": (r.TH1D("mass2_vis_%s_%s" %(mass, FS), "", len(bins2)-1, bins2), r.kRed),
                "mass_gen": (r.TH1D("mass2_gen_%s_%s" %(mass, FS), "", len(bins2)-1, bins2), r.kBlue),
                "mass_withMEt": (r.TH1D("mass2_withMEt_%s_%s" %(mass, FS), "", len(bins2)-1, bins2), r.kGreen),
                "mass_svfit": (r.TH1D("mass2_svfit_%s_%s" %(mass, FS), "", len(bins2)-1, bins2), r.kBlack),
                }
    nbins = 60
    varsDict3 = {"mass_vis": (r.TH1D("mass3_vis_%s_%s" %(mass, FS), "", nbins, -1.5, 1.5), r.kRed),
                "mass_withMEt": (r.TH1D("mass3_withMEt_%s_%s" %(mass, FS), "", nbins, -1.5, 1.5), r.kGreen),
                "mass_svfit": (r.TH1D("mass3_svfit_%s_%s" %(mass, FS), "", nbins, -1.5, 1.5), r.kBlack),
                }

    varsDict = loop_through_files(inputFile, varsDict, FS)
    varsDict2 = loop_through_files(inputFile, varsDict2, FS)
    varsDict3 = loop_through_files(inputFile, varsDict3, FS, True)

    psfile = 'mass_compare_%s_%s.pdf' %(mass, FS)
    histlist = []
    histlist3 = []

    c = r.TCanvas("c","Test", 800, 600)
    r.gPad.SetTicky()
    r.gPad.SetTickx()
    print ''
    for iKey in varsDict.keys():
        varsDict[iKey][0].Scale(1.0/varsDict[iKey][0].Integral(0, len(bins) + 1), 'width')
        varsDict[iKey][0].SetLineColor(varsDict[iKey][1])
        histlist.append((varsDict[iKey][0], "%s: #bar{x} = %.2f, RMS = %.2f, RMS/#bar{x} = %.1f%%" %(iKey, varsDict2[iKey][0].GetMean(), varsDict2[iKey][0].GetRMS(), varsDict2[iKey][0].GetRMS()/varsDict2[iKey][0].GetMean()*100), 'l'))

        if len(histlist) == 1:
            varsDict[iKey][0].SetMaximum(maximum)
            varsDict[iKey][0].Draw()
            varsDict[iKey][0].SetTitle("Zprime %s (%s); %s mass; A.U" %(mass, FS, FS))

        else:
            varsDict[iKey][0].Draw("same")
    if mass != '500':
        leg = tool.setMyLegend((0.1, 0.8 - 0.07*(len(histlist)-1), 0.6, 0.8), histlist)
    else:
        leg = tool.setMyLegend((0.35, 0.8 - 0.07*(len(histlist)-1), 0.85, 0.8), histlist)
    leg.Draw("same")

    c.Print('%s(' %psfile)
    c.Clear()
    for iKey in varsDict3.keys():
        varsDict3[iKey][0].Scale(1.0/varsDict3[iKey][0].Integral(0, nbins + 1), 'width')
        varsDict3[iKey][0].SetLineColor(varsDict3[iKey][1])
        histlist3.append((varsDict3[iKey][0], "%s" %(iKey), 'l'))
        if len(histlist3) == 1:
            varsDict3[iKey][0].SetMaximum(3)
            varsDict3[iKey][0].Draw()
            varsDict3[iKey][0].SetTitle("Zprime %s (%s); %s mass resolution; A.U" %(mass, FS, FS))
        else:
            varsDict3[iKey][0].Draw("same")
    leg2 = tool.setMyLegend((0.6, 0.8 - 0.07*(len(histlist3)-1), 0.85, 0.8), histlist3)
    leg2.Draw("same")


    c.Print('%s)' %psfile)
    c.Close()

# run('500', 'et')
# run('2000', 'et')
# run('5000', 'et')
#run('4000', 'et')

run('500', 'em')
run('2000', 'em')
run('5000', 'em')
#run('500', 'tt')
#run('2000', 'tt')
#run('5000', 'tt')

#run('500', 'em')
#run('2000', 'em')
#run('5000', 'em')
