#!/usr/bin/env python                                                                                                                                                                                                                                                     
import ROOT as r
import tool
import array
import cutSampleTools

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
met = lvClass()

def passCut(tree, fs):
    if tree.q_1 == tree.q_2:
        return False
    if fs == 'et':
        if not (tree.tByTightCombinedIsolationDeltaBetaCorr3Hits):
            return False
    if fs == 'em':
        if not (tree.mRelIso < 0.15):
            return False
    return True

def loopOneFile(iSample, varName, hist, fs, varBins = 0):
    file = r.TFile(iSample)    
    tree = file.Get('Ntuple')
    weight = file.Get('eventCountWeighted').GetBinContent(1)
    print weight
    nEntries = tree.GetEntries()
    hist.Sumw2()
    for i in range(nEntries):
        tree.GetEntry(i)
        if passCut(tree, fs):
            value = -1
            if varName != 'nTruePU':
                wegiht = weight*cutSampleTools.getPUWeight(tree.nTruePU)
            if varName == 'm_eff':
                met.SetCoordinates(tree.pfMetEt, 0.0, tree.pfMetPhi, 0)
                l1.SetCoordinates(tree.pt_1, tree.eta_1, tree.phi_1, tree.m_1)
                l2.SetCoordinates(tree.pt_2, tree.eta_2, tree.phi_2, tree.m_2)
                value = (l1 + l2 + met).mass()
                if value > varBins[len(varBins)-1]:
                    value = (varBins[len(varBins)-1]+varBins[len(varBins)-2]+0.0)/2.0
            else:
                value = getattr(tree, varName)
            hist.Fill(value, 1.0/weight)

def compareSamples(fs):

    varNameDict_et = {'m_eff': 'm(#tau_{e}, #tau_{h}, #slash{E}_{T}) [GeV]',
                      'ePt': 'Electron Pt [GeV]',
                      'tPt': 'Tau Pt [GeV]',
                      'nTruePU': 'nTruePU',
                    }
    varNameDict_em = {'m_eff': 'm(#tau_{e}, #tau_{#mu}, #slash{E}_{T}) [GeV]',
                      'ePt': 'Electron Pt [GeV]',
                      'mPt': 'Muon Pt [GeV]',
                      'nTruePU': 'nTruePU',
                    }

    varName = 'ePt'
    varBins = 0
    if varName == 'm_eff':
        varBins = array.array('d', [0,100,110,120,130,140,150,160,170,180,190,200,225,250,275,300,400,600,900])
        hist1 = r.TH1F("hist_1", "", len(varBins)-1, varBins)
        hist2 = r.TH1F("hist_2", "", len(varBins)-1, varBins)
    else:
        hist1 = r.TH1F("hist_1", "", 50, 0, 500)
        hist2 = r.TH1F("hist_2", "", 50, 0, 500)

    loopOneFile(iSample = '/user_data/zmao/Jan13Production_signalRegion/ZPrime_500_all_SYNC_%s_noIso.root' %fs,
                varName = varName,
                hist = hist1,
                fs = fs,
                varBins = varBins)
    loopOneFile(iSample = '/user_data/zmao/Jan13Production_signalRegion/ZPrime_500_2_all_SYNC_%s_noIso.root' %fs,
                varName = varName,
                hist = hist2,
                fs = fs,
                varBins = varBins)

    position  = (0.65, 0.85 - 0.06*2, 0.85, 0.85)
    histList = []
    histList.append((hist1, 'Old Zprime_500', 'lp'))
    histList.append((hist2, 'New Zprime_500', 'lp'))
    legend = tool.setMyLegend(position, histList)


    c = r.TCanvas("c","Test", 800, 600)
    hist1.SetMarkerSize(0.5)
    hist1.SetLineColor(r.kBlue)
    hist1.SetMarkerColor(r.kBlue)
    hist2.SetMarkerSize(0.5)
    hist2.SetLineColor(r.kRed)
    hist2.SetMarkerColor(r.kRed)
    if fs == 'et':
        title = varNameDict_et[varName]
    else:
        title = varNameDict_em[varName]

    hist1.SetTitle("ZPrime Sample Comparison; %s; Events/Initial Events" %title)
    hist1.SetMinimum(0.000001)
    hist1.Scale(1, 'width')
    hist2.Scale(1, 'width')

    hist1.Draw("E1")
    hist2.Draw("E1same")
    legend.Draw('same')

    r.gPad.SetLogy()

    r.gPad.SetTicky()
    r.gPad.SetTickx()
    c.Print('sampleCheck_%s_%s.pdf' %(fs, varName))

cutSampleTools.setupLumiReWeight()
compareSamples('et')
# compareSamples('em')
cutSampleTools.freeLumiReWeight()
