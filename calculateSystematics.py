#!/usr/bin/env python
import ROOT as r
import tool

lumi = 19.7
tt = ['tt', 'tt_semi', 'tthad']
VV_old = ['ZZ', 'zzTo4L', 'zzTo2L2Nu', 'WW', 'WZ3L', 'WZJetsTo2L2Q']
singleT = ['t', 'tbar']
ZTT = ['DY_embed', 'tt_embed']
QCD = ['MCOSRelax', 'dataOSRelax']

def getWeight(tree, name):
    if name == 'dataOSRelax':
        return 1.0
    elif name == 'MCOSRelax':
        return -tree.triggerEff*tree.PUWeight*tree.xs*lumi/tree.initEvents
    else:
        return tree.triggerEff*tree.PUWeight*tree.decayModeWeight*tree.xs*lumi/tree.initEvents


def getSampleName(name):
    if name in tt:
        return 'tt'
    elif name in QCD:
        return 'QCD'
    else:
        return name

def getScales(f):
    scaleDict = {'1M': {}, '2M': {}}
    dy1M_scale = f.Get('MC2Embed2Cat_1M')
    dy2M_scale = f.Get('MC2Embed2Cat_2M')
    predictSF1MHist = f.Get('L_to_T_SF_1M')
    predictSF2MHist = f.Get('L_to_T_SF_2M')
    electroweakWeightHist1M = f.Get('VV_1M')
    electroweakWeightHist2M = f.Get('VV_2M')
    singleTWeightHist1M = f.Get('singleT_1M')
    singleTWeightHist2M = f.Get('singleT_2M')
    ZLLWeightHist1M = f.Get('ZLL_1M')
    ZLLWeightHist2M = f.Get('ZLL_2M')

    scaleDict['1M']['ZTT'] = dy1M_scale.GetBinContent(1)
    scaleDict['2M']['ZTT'] = dy2M_scale.GetBinContent(1)
    scaleDict['1M']['QCD'] = predictSF1MHist.GetBinContent(1)
    scaleDict['2M']['QCD'] = predictSF2MHist.GetBinContent(1)
    scaleDict['1M']['VV'] = electroweakWeightHist1M.GetBinContent(1)
    scaleDict['2M']['VV'] = electroweakWeightHist2M.GetBinContent(1)
    scaleDict['1M']['singleT'] = singleTWeightHist1M.GetBinContent(1)
    scaleDict['2M']['singleT'] = singleTWeightHist2M.GetBinContent(1)
    scaleDict['1M']['ZLL'] = ZLLWeightHist1M.GetBinContent(1)
    scaleDict['2M']['ZLL'] = ZLLWeightHist2M.GetBinContent(1)
    return scaleDict


def getYieldsFromFile(file):
    f = r.TFile(file)    
    tree = f.Get('eventTree')
    total = tree.GetEntries()

    scaleDict = getScales(f)
    yieldsDict = {}
    yieldsDict['1M'] = {'QCD': 0.0, 'tt': 0.0, 'VV': 0.0, 'ZTT': 0.0, 'ZLL': 0.0, 'signal': 0.0,
                        'H2hh260': 0.0, 'H2hh270': 0.0, 'H2hh280': 0.0, 'H2hh290': 0.0, 'H2hh300': 0.0,
                        'H2hh310': 0.0, 'H2hh320': 0.0, 'H2hh330': 0.0, 'H2hh340': 0.0, 'H2hh350': 0.0}
    yieldsDict['2M'] = {'QCD': 0.0, 'tt': 0.0, 'VV': 0.0, 'ZTT': 0.0, 'ZLL': 0.0, 'signal': 0.0,
                        'H2hh260': 0.0, 'H2hh270': 0.0, 'H2hh280': 0.0, 'H2hh290': 0.0, 'H2hh300': 0.0,
                        'H2hh310': 0.0, 'H2hh320': 0.0, 'H2hh330': 0.0, 'H2hh340': 0.0, 'H2hh350': 0.0}

    for iEvent in range(total):
        tool.printProcessStatus(iEvent, total, 'Looping file [%s]' % (file))
        tree.GetEntry(iEvent)
        name = getSampleName(tree.sampleName)
        if name in yieldsDict['1M'].keys():
            if tree.Category == '0M':
                continue
            yieldsDict[tree.Category][name] += getWeight(tree, tree.sampleName)
    #rescale
    for cat in ['1M', '2M']:
        yieldsDict[cat]['ZTT'] = scaleDict[cat]['ZTT']
        yieldsDict[cat]['ZLL'] = scaleDict[cat]['ZLL']
        yieldsDict[cat]['VV'] = scaleDict[cat]['VV'] + scaleDict[cat]['singleT']
        yieldsDict[cat]['QCD'] = yieldsDict[cat]['QCD']*scaleDict[cat]['QCD']
        for i in ['H2hh260', 'H2hh270', 'H2hh280', 'H2hh290', 'H2hh300', 'H2hh310', 'H2hh320', 'H2hh330', 'H2hh340', 'H2hh350']:
            yieldsDict[cat]['signal'] += yieldsDict[cat][i]

    print ''
    return yieldsDict

def calcSystematics(file_norm, file_up, file_down):
    yield_normal = getYieldsFromFile(file_norm)
    yield_up = getYieldsFromFile(file_up)
    yield_down = getYieldsFromFile(file_down)

    samples = ['ZTT', 'ZLL', 'VV', 'QCD', 'tt', 'H2hh260', 'H2hh270', 'H2hh280', 'H2hh290', 'H2hh300', 'H2hh310', 'H2hh320', 'H2hh330', 'H2hh340', 'H2hh350', 'signal']

    for cat in ['1M', '2M']:

        print '%s______________________' %cat
        print 'sample\t\tdown\t\tnormal\t\tup'

        for iSample in samples:
            sampleName = iSample
            if 'H2hh' in sampleName:
                sampleName = 'H' + sampleName[4:]
            print '%s\t\t%.2f (%.1f%%)\t%.2f\t\t%.2f (%.1f%%)' %(sampleName, yield_down[cat][iSample], 
                                                                2*(yield_down[cat][iSample]-yield_normal[cat][iSample])/(yield_normal[cat][iSample]+yield_down[cat][iSample])*100,
                                                                yield_normal[cat][iSample],
                                                                yield_up[cat][iSample],
                                                                2*(yield_up[cat][iSample]-yield_normal[cat][iSample])/(yield_normal[cat][iSample]+yield_up[cat][iSample])*100)
        print ''

    print '1M+2M______________________'
    print 'sample\t\tdown\t\tnormal\t\tup'

    for iSample in samples:
        sampleName = iSample
        if 'H2hh' in sampleName:
            sampleName = 'H' + sampleName[4:]
        print '%s\t\t%.2f (%.1f%%)\t%.2f\t\t%.2f (%.1f%%)' %(sampleName, yield_down['1M'][iSample]+yield_down['2M'][iSample], 
                                                            2*(yield_down['1M'][iSample]+yield_down['2M'][iSample]-yield_normal['1M'][iSample]-yield_normal['2M'][iSample])/(yield_normal['1M'][iSample]+yield_down['1M'][iSample]+yield_normal['2M'][iSample]+yield_down['2M'][iSample])*100,
                                                            yield_normal['1M'][iSample]+yield_normal['2M'][iSample],
                                                            yield_up['1M'][iSample]+yield_up['2M'][iSample],
                                                            2*(yield_up['1M'][iSample]+yield_up['2M'][iSample]-yield_normal['1M'][iSample]-yield_normal['2M'][iSample])/(yield_normal['1M'][iSample]+yield_up['1M'][iSample]+yield_normal['2M'][iSample]+yield_up['2M'][iSample])*100)
    print ''


calcSystematics(file_norm = '/nfs_scratch/zmao/samples_Iso/datacard/combined_iso1.0_one1To4_iso_normal__withDYEmbed.root', 
                file_up = '/nfs_scratch/zmao/samples_Iso/datacard/combined_iso1.0_one1To4_iso_bSysUp__withDYEmbed.root',
                file_down = '/nfs_scratch/zmao/samples_Iso/datacard/combined_iso1.0_one1To4_iso_bSysDown__withDYEmbed.root')