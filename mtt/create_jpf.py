#!/usr/bin/env python

import ROOT as r

def getValue(tree, mode, FS, leg = 'e'):
    if mode == 0:
        if FS == "mt" and tree.mIsTau2Muon:
            return (tree.p_perp_1, tree.m_vis_invis_1)
        elif FS == "et" and tree.eIsTau2Electron:
            return (tree.p_perp_1, tree.m_vis_invis_1)

        elif FS == "em":
            if leg == "e"and tree.eIsTau2Electron:
                return (tree.p_perp_1, tree.m_vis_invis_1)
            elif leg == "m" and tree.mIsTau2Muon:
                return (tree.p_perp_2, tree.m_vis_invis_2)
            else:
                return (-1, -1)
        else:
            return (-1, -1)
    elif mode == 1 and tree.tIsTauh and tree.tDecayMode < 4:
        return (tree.p_perp_2, tree.m_vis_invis_2)
    elif mode == 2 and tree.tIsTauh and tree.tDecayMode > 8:
        return (tree.p_perp_2, tree.m_vis_invis_2)
    else:
        return (-1, -1)

def saveToHist(inputFile, FS, mode, hist):
    file = r.TFile(inputFile)    
    tree = file.Get('Ntuple')
    nEntries = tree.GetEntries()
    for iEntry in range(nEntries):
        tree.GetEntry(iEntry)
        values = getValue(tree, mode, FS)
        if values[0] != -1:
            hist.Fill(values[1], values[0])
        if FS == 'em':
            values = getValue(tree, mode, FS, 'm')
        if values[0] != -1:
            hist.Fill(values[1], values[0])

def main(parent):
    h_Minvvis_pperp_0 = r.TH2F("h_Minvvis_pperp_0", "", 50, 0, 1.8, 50, 0, 1.1)
    h_Minvvis_pperp_1 = r.TH2F("h_Minvvis_pperp_1", "", 50, 0, 1.8, 50, 0, 1.1)
    h_Minvvis_pperp_2 = r.TH2F("h_Minvvis_pperp_2", "", 50, 0, 1.8, 50, 0, 1.1)

    saveToHist("%s_et.root" %(parent), 'et', 0, h_Minvvis_pperp_0)
    saveToHist("%s_mt.root" %(parent), 'mt', 0, h_Minvvis_pperp_0)
    saveToHist("%s_em.root" %(parent), 'em', 0, h_Minvvis_pperp_0)

    saveToHist("%s_et.root" %(parent), 'et', 1, h_Minvvis_pperp_1)
    saveToHist("%s_et.root" %(parent), 'et', 2, h_Minvvis_pperp_2)
    saveToHist("%s_mt.root" %(parent), 'mt', 1, h_Minvvis_pperp_1)
    saveToHist("%s_mt.root" %(parent), 'mt', 2, h_Minvvis_pperp_2)

    h_Minvvis_pperp_0.Scale(1./h_Minvvis_pperp_0.Integral())
    h_Minvvis_pperp_1.Scale(1./h_Minvvis_pperp_1.Integral())
    h_Minvvis_pperp_2.Scale(1./h_Minvvis_pperp_2.Integral())

    outFile = r.TFile("jpf_%s.root" %parent, 'recreate')
    outFile.cd()
    h_Minvvis_pperp_0.Write()
    h_Minvvis_pperp_1.Write()
    h_Minvvis_pperp_2.Write()
    outFile.Close()

# main("ZPrime_2500")
main("ZPrime_4000")
# main("DY-50_LO")
    


