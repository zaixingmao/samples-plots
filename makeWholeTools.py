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

def calcSysUnc(sf, num, denom, delta_num = 0, delta_denom = 0):
    if delta_num == 0:
        delta_num = math.sqrt(num)
    if delta_denom == 0:
        delta_denom = math.sqrt(denom)
    return sf*math.sqrt((delta_num/num)**2 + (delta_denom/denom)**2)

def passCut(tree, option):
    if tree.pt1.at(0) < 45 or tree.pt2.at(0) < 45:
        return 0
    passIso = 0
    passSign = 0
    isoTight = 1.5
    isoCut = 3
    isoMax = 10

    if 'INFN' in option:
        isoTight = 1.0
        isoCut = 1.0
        isoMax = 4.0
    if 'very' in option:
        isoCut = 1.5

    if 'tight' in option and (tree.iso1.at(0) < isoTight and tree.iso2.at(0) < isoTight):
            passIso = 1
    if 'semiTight' in option and ((tree.iso1.at(0) < isoTight and isoCut < tree.iso2.at(0) < isoMax) or (isoCut < tree.iso1.at(0) < isoMax and tree.iso2.at(0) < isoTight)):
            passIso = 1
    if 'relaxed' in option and (isoCut < tree.iso1.at(0) < isoMax and isoCut < tree.iso2.at(0) < isoMax):
            passIso = 1


    if 'SS' in option and (tree.charge1.at(0) == tree.charge2.at(0)):
            passSign = 1
    if 'OS' in option and (tree.charge1.at(0) == -tree.charge2.at(0)):
            passSign = 1
    return passIso*passSign


def calculateSF(fileList, location0, out, sigRegionOption = 'tight', relaxedRegionOption = 'relaxed', verbose = False):
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

    MC_SS_TT_catNone_veto = 0
    MC_SS_LL_catNone_veto = 0
    MC_OS_LL_catNone_veto = 0
    DATA_SS_TT_catNone_veto = 0
    DATA_SS_LL_catNone_veto = 0
    DATA_OS_LL_catNone_veto = 0

    for fileName, location, in fileList:

        files.append(r.TFile(location0+location))
        trees.append(files[len(files)-1].Get("eventTree"))
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
                if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption):
                    if isData:
                        DATA_SS_TT_cat1+=1
                    else:
                        MC_SS_TT_cat1+=trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                elif passCut(trees[len(trees)-1], '%sOS' %relaxedRegionOption):
                    if isData:
                        DATA_OS_LL_cat1+=1
                    else:
                        MC_OS_LL_cat1+=trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                elif passCut(trees[len(trees)-1], '%sSS' %relaxedRegionOption):
                    if isData:
                        DATA_SS_LL_cat1+=1
                    else:
                        MC_SS_LL_cat1 +=trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
            elif trees[len(trees)-1].category == '2M':
                if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption):
                    if isData:
                        DATA_SS_TT_cat2 += 1
                    else:
                        MC_SS_TT_cat2 += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                elif passCut(trees[len(trees)-1], '%sOS' %relaxedRegionOption):
                    if isData:
                        DATA_OS_LL_cat2 += 1
                    else:
                        MC_OS_LL_cat2 += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                elif passCut(trees[len(trees)-1], '%sSS' %relaxedRegionOption):
                    if isData:
                        DATA_SS_LL_cat2 += 1
                    else:
                        MC_SS_LL_cat2 += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff


            if trees[len(trees)-1].nElectrons == 0 and trees[len(trees)-1].nMuons == 0:
                if trees[len(trees)-1].category == '1M1NonM':
                    if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption):
                        if isData:
                            DATA_SS_TT_cat1_veto+=1
                        else:
                            MC_SS_TT_cat1_veto+=trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], '%sOS' %relaxedRegionOption):
                        if isData:
                            DATA_OS_LL_cat1_veto+=1
                        else:
                            MC_OS_LL_cat1_veto+=trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], '%sSS' %relaxedRegionOption):
                        if isData:
                            DATA_SS_LL_cat1_veto+=1
                        else:
                            MC_SS_LL_cat1_veto +=trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                elif trees[len(trees)-1].category == '2M':
                    if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption):
                        if isData:
                            DATA_SS_TT_cat2_veto += 1
                        else:
                            MC_SS_TT_cat2_veto += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], '%sOS' %relaxedRegionOption):
                        if isData:
                            DATA_OS_LL_cat2_veto += 1
                        else:
                            MC_OS_LL_cat2_veto += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], '%sSS' %relaxedRegionOption):
                        if isData:
                            DATA_SS_LL_cat2_veto += 1
                        else:
                            MC_SS_LL_cat2_veto += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                elif trees[len(trees)-1].category == 'none':
                    if passCut(trees[len(trees)-1], '%sSS' %sigRegionOption):
                        if isData:
                            DATA_SS_TT_catNone_veto += 1
                        else:
                            MC_SS_TT_catNone_veto += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], '%sOS' %relaxedRegionOption):
                        if isData:
                            DATA_OS_LL_catNone_veto += 1
                        else:
                            MC_OS_LL_catNone_veto += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff
                    elif passCut(trees[len(trees)-1], '%sSS' %relaxedRegionOption):
                        if isData:
                            DATA_SS_LL_catNone_veto += 1
                        else:
                            MC_SS_LL_catNone_veto += trees[len(trees)-1].xs*(lumi/trees[len(trees)-1].initEvents)*trees[len(trees)-1].triggerEff


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

    QCD_SS_LL_catNone_veto = DATA_SS_LL_catNone_veto - MC_SS_LL_catNone_veto
    QCD_SS_TT_catNone_veto = DATA_SS_TT_catNone_veto - MC_SS_TT_catNone_veto
    QCD_OS_LL_catNone_veto = DATA_OS_LL_catNone_veto - MC_OS_LL_catNone_veto

    QCD_SS_LL_cat0_veto = QCD_SS_LL_cat1_veto + QCD_SS_LL_cat2_veto
    QCD_SS_TT_cat0_veto = QCD_SS_TT_cat1_veto + QCD_SS_TT_cat2_veto
    QCD_OS_LL_cat0_veto = QCD_OS_LL_cat1_veto + QCD_OS_LL_cat2_veto
    DATA_SS_LL_cat0_veto = DATA_SS_LL_cat1_veto + DATA_SS_LL_cat2_veto
    DATA_SS_TT_cat0_veto = DATA_SS_TT_cat1_veto + DATA_SS_TT_cat2_veto
    DATA_OS_LL_cat0_veto = DATA_OS_LL_cat1_veto + DATA_OS_LL_cat2_veto

    SF_cat0_veto = QCD_SS_TT_cat0_veto/QCD_SS_LL_cat0_veto
    sf_cat0_veto = QCD_OS_LL_cat0_veto/DATA_OS_LL_cat0_veto
    weight0_veto = SF_cat0_veto*sf_cat0_veto

    un_SF_cat0_veto = calcSysUnc(SF_cat0_veto, QCD_SS_TT_cat0_veto, QCD_SS_LL_cat0_veto)
    un_sf_cat0_veto = calcSysUnc(1-sf_cat0_veto, DATA_OS_LL_cat0_veto - QCD_SS_TT_cat0_veto, DATA_OS_LL_cat0_veto)
    un_weight0_veto = calcSysUnc(weight0_veto, SF_cat0_veto, sf_cat0_veto, un_SF_cat0_veto, un_sf_cat0_veto)

    SF_cat1_veto = QCD_SS_TT_cat1_veto/QCD_SS_LL_cat1_veto
    sf_cat1_veto = QCD_OS_LL_cat1_veto/DATA_OS_LL_cat1_veto
    weight1_veto = SF_cat1_veto*sf_cat1_veto
    
    un_SF_cat1_veto = calcSysUnc(SF_cat1_veto, QCD_SS_TT_cat1_veto, QCD_SS_LL_cat1_veto)
    un_sf_cat1_veto = calcSysUnc(1-sf_cat1_veto, MC_OS_LL_cat1_veto, DATA_OS_LL_cat1_veto)
    un_weight1_veto = calcSysUnc(weight1_veto, SF_cat1_veto, sf_cat1_veto, un_SF_cat1_veto, un_sf_cat1_veto)

    SF_cat2_veto = QCD_SS_TT_cat2_veto/QCD_SS_LL_cat2_veto
    sf_cat2_veto = QCD_OS_LL_cat2_veto/DATA_OS_LL_cat2_veto
    weight2_veto = SF_cat2_veto*sf_cat2_veto

    un_SF_cat2_veto = calcSysUnc(SF_cat2_veto, QCD_SS_TT_cat2_veto, QCD_SS_LL_cat2_veto)
    un_sf_cat2_veto = calcSysUnc(1-sf_cat2_veto, MC_OS_LL_cat2_veto, DATA_OS_LL_cat2_veto)
    un_weight2_veto = calcSysUnc(weight2_veto, SF_cat2_veto, sf_cat2_veto, un_SF_cat2_veto, un_sf_cat2_veto)

    SF_catNone_veto = QCD_SS_TT_catNone_veto/QCD_SS_LL_catNone_veto
    sf_catNone_veto = QCD_OS_LL_catNone_veto/DATA_OS_LL_catNone_veto
    weightNone_veto = SF_catNone_veto*sf_catNone_veto

    un_SF_catNone_veto = calcSysUnc(SF_catNone_veto, QCD_SS_TT_catNone_veto, QCD_SS_LL_catNone_veto)
    un_sf_catNone_veto = calcSysUnc(1-sf_catNone_veto, MC_OS_LL_catNone_veto, DATA_OS_LL_catNone_veto)
    un_weightNone_veto = calcSysUnc(weightNone_veto, SF_catNone_veto, sf_catNone_veto, un_SF_catNone_veto, un_sf_catNone_veto)

    if verbose:
        
        print 'MC/QCD/Data'
        print 'Category 0tag'
        print '\t\t\t%.1f/%.1f/%.0f' %(MC_SS_TT_catNone_veto,QCD_SS_TT_catNone_veto, DATA_SS_TT_catNone_veto)
        print '%.1f/%.1f/%.0f\t%.1f/%.1f/%.0f'%(MC_OS_LL_catNone_veto, QCD_OS_LL_catNone_veto, DATA_OS_LL_catNone_veto, 
                                                MC_SS_LL_catNone_veto, QCD_SS_LL_catNone_veto, DATA_SS_LL_catNone_veto)        
        print ''
        print 'Category 1+2tag'
        print '\t\t\t%.1f/%.1f/%.0f' %(DATA_SS_TT_cat0_veto-QCD_SS_TT_cat0_veto,QCD_SS_TT_cat0_veto, DATA_SS_TT_cat0_veto)
        print '%.1f/%.1f/%.0f\t%.1f/%.1f/%.0f'%(DATA_OS_LL_cat0_veto-QCD_OS_LL_cat0_veto, QCD_OS_LL_cat0_veto, DATA_OS_LL_cat0_veto, 
                                                DATA_SS_LL_cat0_veto-QCD_SS_LL_cat0_veto, QCD_SS_LL_cat0_veto, DATA_SS_LL_cat0_veto) 
        print ''
        print 'Category 1tag'
        print '\t\t\t%.1f/%.1f/%.0f' %(MC_SS_TT_cat1_veto,QCD_SS_TT_cat1_veto, DATA_SS_TT_cat1_veto)
        print '%.1f/%.1f/%.0f\t%.1f/%.1f/%.0f'%(MC_OS_LL_cat1_veto, QCD_OS_LL_cat1_veto, DATA_OS_LL_cat1_veto, 
                                                MC_SS_LL_cat1_veto, QCD_SS_LL_cat1_veto, DATA_SS_LL_cat1_veto)
        print ''
        print 'Category 2tag'
        print '\t\t\t%.1f/%.1f/%.0f' %(MC_SS_TT_cat2_veto,QCD_SS_TT_cat2_veto, DATA_SS_TT_cat2_veto)
        print '%.1f/%.1f/%.0f\t\t%.1f/%.1f/%.0f'%(MC_OS_LL_cat2_veto, QCD_OS_LL_cat2_veto, DATA_OS_LL_cat2_veto, 
                                                MC_SS_LL_cat2_veto, QCD_SS_LL_cat2_veto, DATA_SS_LL_cat2_veto)

        print 'Results__________________________________'
        print 'Category\t1+2tag_veto\t\t1tag_veto\t\t2tag_veto\t\t0tag_veto'
        print 'SF\t\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)' %(SF_cat0_veto, un_SF_cat0_veto, 100*un_SF_cat0_veto/SF_cat0_veto,
                                                                                                                   SF_cat1_veto, un_SF_cat1_veto, 100*un_SF_cat1_veto/SF_cat1_veto,
                                                                                                                   SF_cat2_veto, un_SF_cat2_veto, 100*un_SF_cat2_veto/SF_cat2_veto,
                                                                                                                   SF_catNone_veto, un_SF_catNone_veto, 100*un_SF_catNone_veto/SF_catNone_veto)
        print 'OCD/Data\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)' %(sf_cat0_veto, un_sf_cat0_veto, 100*un_sf_cat0_veto/sf_cat0_veto,
                                                                                                   sf_cat1_veto, un_sf_cat1_veto, 100*un_sf_cat1_veto/sf_cat1_veto,
                                                                                                   sf_cat2_veto, un_sf_cat2_veto, 100*un_sf_cat2_veto/sf_cat2_veto,
                                                                                                   sf_catNone_veto, un_sf_catNone_veto, 100*un_sf_catNone_veto/sf_catNone_veto)
        print 'Weights\t\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)\t%.3f +/- %.3f (%.f%%)' %(weight0_veto, un_weight0_veto, 100*un_weight0_veto/weight0_veto,
                                                                                                    weight1_veto, un_weight1_veto, 100*un_weight1_veto/weight1_veto,
                                                                                                    weight2_veto, un_weight2_veto, 100*un_weight2_veto/weight2_veto,
                                                                                                    weightNone_veto, un_weightNone_veto, 100*un_weightNone_veto/weightNone_veto)


    output = []
    if 'SF' not in out:
        if 'veto' in out:
            if '0' in out:
                output.append(weight0_veto) 
            if '1' in out:
                output.append(weight1_veto) 
            if '2' in out:
                output.append(weight2_veto)
            if 'None' in out:
                output.append(weightNone_veto)
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
            if 'None' in out:
                output.append(SF_catNone_veto)
        else:
            if '0' in out:
                output.append(SF_cat0) 
            if '1' in out:
                output.append(SF_cat1) 
            if '2' in out:
                output.append(SF_cat2) 
        return output

# calculateSF(makeWholeSample_cfg.sampleConfigsTools, makeWholeSample_cfg.preFixTools, 'veto012None', 'tight','relaxed',True)
