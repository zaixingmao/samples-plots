#!/usr/bin/env python
import ROOT as r
from operator import itemgetter
import tool
import math
import optparse
import os
from array import array
import makeWholeSample_cfg

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))


lumi = 19.7

def passCut(tree, option, iso):
    if tree.pt1.at(0) < 45 or tree.pt2.at(0) < 45:
        return 0
    passIso = 0
    passSign = 0
    if 'tight' in option and (tree.iso1.at(0) < iso and tree.iso2.at(0) < iso):
            passIso = 1
    if 'semiTight' in option and (tree.iso1.at(0) < 1.5 and tree.iso2.at(0) > 3):
            passIso = 1
    if 'relaxed' in option and (tree.iso1.at(0) > 3 and tree.iso2.at(0) > 3):
            passIso = 1
    if 'SS' in option and (tree.charge1.at(0) == tree.charge2.at(0)):
            passSign = 1
    if 'OS' in option and (tree.charge1.at(0) == -tree.charge2.at(0)):
            passSign = 1
    return passIso*passSign


def calculateSF(fileList, location0, out, sigRegionOption = 'tight', verbose = False, iso = 1.5):
    files = []
    trees = []

    MC_SS_TT_cat1 = 0
    MC_SS_LL_cat1 = 0
    MC_OS_LL_cat1 = 0
    DATA_SS_TT_cat1 = 0
    DATA_SS_LL_cat1 = 0
    DATA_OS_LL_cat1 = 0

    MC_SS_TT_cat2 = 0
    MC_SS_LL_cat2 = 0
    MC_OS_LL_cat2 = 0
    DATA_SS_TT_cat2 = 0
    DATA_SS_LL_cat2 = 0
    DATA_OS_LL_cat2 = 0

    MC_SS_TT_cat1_veto = 0
    MC_SS_LL_cat1_veto = 0
    MC_OS_LL_cat1_veto = 0
    DATA_SS_TT_cat1_veto = 0
    DATA_SS_LL_cat1_veto = 0
    DATA_OS_LL_cat1_veto = 0

    MC_SS_TT_cat2_veto = 0
    MC_SS_LL_cat2_veto = 0
    MC_OS_LL_cat2_veto = 0
    DATA_SS_TT_cat2_veto = 0
    DATA_SS_LL_cat2_veto = 0
    DATA_OS_LL_cat2_veto = 0

    for fileName, location, selection, xs in fileList:

        files.append(r.TFile(location0+location))
        trees.append(files[len(files)-1].Get("eventTree"))
        initEvents = (files[len(files)-1].Get("preselection")).GetBinContent(1)
        total = trees[len(trees)-1].GetEntries()
        if 'data' in fileName:
            isData = True
        else:
            isData = False
        if 'H2hh' in fileName:
            continue
        for i in range(total):
            tool.printProcessStatus(iCurrent=i+1, total=total, processName = 'Looping sample [%s]' %fileName)
            trees[len(trees)-1].GetEntry(i)
            if trees[len(trees)-1].category == '1M1NonM':
                if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption, iso):
                    if isData:
                        DATA_SS_TT_cat1+=1
                    else:
                        MC_SS_TT_cat1+=xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                elif passCut(trees[len(trees)-1], 'relaxedOS', iso):
                    if isData:
                        DATA_OS_LL_cat1+=1
                    else:
                        MC_OS_LL_cat1+=xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                elif passCut(trees[len(trees)-1], 'relaxedSS', iso):
                    if isData:
                        DATA_SS_LL_cat1+=1
                    else:
                        MC_SS_LL_cat1 +=xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
            elif trees[len(trees)-1].category == '2M':
                if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption, iso):
                    if isData:
                        DATA_SS_TT_cat2 += 1
                    else:
                        MC_SS_TT_cat2 += xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                elif passCut(trees[len(trees)-1], 'relaxedOS', iso):
                    if isData:
                        DATA_OS_LL_cat2 += 1
                    else:
                        MC_OS_LL_cat2 += xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                elif passCut(trees[len(trees)-1], 'relaxedSS', iso):
                    if isData:
                        DATA_SS_LL_cat2 += 1
                    else:
                        MC_SS_LL_cat2 += xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff

            if trees[len(trees)-1].nElectrons == 0 and trees[len(trees)-1].nMuons == 0:
                if trees[len(trees)-1].category == '1M1NonM':
                    if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption, iso):
                        if isData:
                            DATA_SS_TT_cat1_veto+=1
                        else:
                            MC_SS_TT_cat1_veto+=xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], 'relaxedOS', iso):
                        if isData:
                            DATA_OS_LL_cat1_veto+=1
                        else:
                            MC_OS_LL_cat1_veto+=xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], 'relaxedSS', iso):
                        if isData:
                            DATA_SS_LL_cat1_veto+=1
                        else:
                            MC_SS_LL_cat1_veto +=xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                elif trees[len(trees)-1].category == '2M':
                    if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption, iso):
                        if isData:
                            DATA_SS_TT_cat2_veto += 1
                        else:
                            MC_SS_TT_cat2_veto += xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], 'relaxedOS', iso):
                        if isData:
                            DATA_OS_LL_cat2_veto += 1
                        else:
                            MC_OS_LL_cat2_veto += xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], 'relaxedSS', iso):
                        if isData:
                            DATA_SS_LL_cat2_veto += 1
                        else:
                            MC_SS_LL_cat2_veto += xs*(lumi/initEvents)*trees[len(trees)-1].triggerEff

        print ''

    QCD_SS_LL_cat1 = DATA_SS_LL_cat1 - MC_SS_LL_cat1
    QCD_SS_TT_cat1 = DATA_SS_TT_cat1 - MC_SS_TT_cat1
    QCD_OS_LL_cat1 = DATA_OS_LL_cat1 - MC_OS_LL_cat1

    QCD_SS_LL_cat2 = DATA_SS_LL_cat2 - MC_SS_LL_cat2
    QCD_SS_TT_cat2 = DATA_SS_TT_cat2 - MC_SS_TT_cat2
    QCD_OS_LL_cat2 = DATA_OS_LL_cat2 - MC_OS_LL_cat2


    QCD_SS_LL_cat0 = QCD_SS_LL_cat1 + QCD_SS_LL_cat2
    QCD_SS_TT_cat0 = QCD_SS_TT_cat1 + QCD_SS_TT_cat2
    QCD_OS_LL_cat0 = QCD_OS_LL_cat1 + QCD_OS_LL_cat2
    DATA_OS_LL_cat0 = DATA_OS_LL_cat1 + DATA_OS_LL_cat2

    SF_cat0 = QCD_SS_TT_cat0/QCD_SS_LL_cat0
    sf_cat0 = QCD_OS_LL_cat0/DATA_OS_LL_cat0
    weight0 = SF_cat0*sf_cat0

    SF_cat1 = QCD_SS_TT_cat1/QCD_SS_LL_cat1
    sf_cat1 = QCD_OS_LL_cat1/DATA_OS_LL_cat1
    weight1 = SF_cat1*sf_cat1
    
    SF_cat2 = QCD_SS_TT_cat2/QCD_SS_LL_cat2
    sf_cat2 = QCD_OS_LL_cat2/DATA_OS_LL_cat2
    weight2 = SF_cat2*sf_cat2


    QCD_SS_LL_cat1_veto = DATA_SS_LL_cat1_veto - MC_SS_LL_cat1_veto
    QCD_SS_TT_cat1_veto = DATA_SS_TT_cat1_veto - MC_SS_TT_cat1_veto
    QCD_OS_LL_cat1_veto = DATA_OS_LL_cat1_veto - MC_OS_LL_cat1_veto

    QCD_SS_LL_cat2_veto = DATA_SS_LL_cat2_veto - MC_SS_LL_cat2_veto
    QCD_SS_TT_cat2_veto = DATA_SS_TT_cat2_veto - MC_SS_TT_cat2_veto
    QCD_OS_LL_cat2_veto = DATA_OS_LL_cat2_veto - MC_OS_LL_cat2_veto


    QCD_SS_LL_cat0_veto = QCD_SS_LL_cat1_veto + QCD_SS_LL_cat2_veto
    QCD_SS_TT_cat0_veto = QCD_SS_TT_cat1_veto + QCD_SS_TT_cat2_veto
    QCD_OS_LL_cat0_veto = QCD_OS_LL_cat1_veto + QCD_OS_LL_cat2_veto
    DATA_OS_LL_cat0_veto = DATA_OS_LL_cat1_veto + DATA_OS_LL_cat2_veto

    SF_cat0_veto = QCD_SS_TT_cat0_veto/QCD_SS_LL_cat0_veto
    sf_cat0_veto = QCD_OS_LL_cat0_veto/DATA_OS_LL_cat0_veto
    weight0_veto = SF_cat0_veto*sf_cat0_veto

    SF_cat1_veto = QCD_SS_TT_cat1_veto/QCD_SS_LL_cat1_veto
    sf_cat1_veto = QCD_OS_LL_cat1_veto/DATA_OS_LL_cat1_veto
    weight1_veto = SF_cat1_veto*sf_cat1_veto
    
    SF_cat2_veto = QCD_SS_TT_cat2_veto/QCD_SS_LL_cat2_veto
    sf_cat2_veto = QCD_OS_LL_cat2_veto/DATA_OS_LL_cat2_veto
    weight2_veto = SF_cat2_veto*sf_cat2_veto

    if verbose:
        print 'Category 0'
        print '\t\t%.1f' %(QCD_SS_TT_cat0_veto)
        print '%.1f\t%.1f'%(QCD_OS_LL_cat0_veto, QCD_SS_LL_cat0_veto)
        print 'Category 1'
        print '\t\t%.1f' %(QCD_SS_TT_cat1_veto)
        print '%.1f\t%.1f'%(QCD_OS_LL_cat1_veto, QCD_SS_LL_cat1_veto)
        print 'Category 2'
        print '\t\t%.1f' %(QCD_SS_TT_cat2_veto)
        print '%.1f\t%.1f'%(QCD_OS_LL_cat2_veto, QCD_SS_LL_cat2_veto)

        print 'Results__________________________________'
        print 'Category\t0\t\t1\t\t2\t\t0_veto\t\t1_veto\t\t2_veto'
        print 'SF\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f' %(SF_cat0, SF_cat1, SF_cat2, SF_cat0_veto, SF_cat1_veto, SF_cat2_veto)
        print 'OCD/Data\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f' %(sf_cat0, sf_cat1, sf_cat2, sf_cat0_veto, sf_cat1_veto, sf_cat2_veto)
        print 'Weights\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f\t\t%.3f' %(weight0, weight1, weight2, weight0_veto, weight1_veto, weight2_veto)

    output = []
    if 'SF' not in out:
        if 'veto' in out:
            if '0' in out:
                output.append(weight0_veto) 
            if '1' in out:
                output.append(weight1_veto) 
            if '2' in out:
                output.append(weight2_veto)
        else:
            if '0' in out:
                output.append(weight0) 
            if '1' in out:
                output.append(weight1) 
            if '2' in out:
                output.append(weight2) 
        return output
    else:
        if 'veto' in out:
            if '0' in out:
                output.append(SF_cat0_veto) 
            if '1' in out:
                output.append(SF_cat1_veto) 
            if '2' in out:
                output.append(SF_cat2_veto)
        else:
            if '0' in out:
                output.append(SF_cat0) 
            if '1' in out:
                output.append(SF_cat1) 
            if '2' in out:
                output.append(SF_cat2) 
        return output

# calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012', 'semiTight',True)
