#!/usr/bin/env python
import ROOT as r
import tool
import os
import cProfile
from array import array
import optparse
import plots_cfg
import cutSampleTools
import plots
import math

r.gROOT.SetBatch(True)
r.gErrorIgnoreLevel = 2000
r.gStyle.SetOptStat(0)

r.gStyle.SetOptStat("e")
vec = r.vector('double')()

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

l1 = lvClass()
l2 = lvClass()
met = lvClass()
deltaTauES = lvClass()

bins = array('d', plots_cfg.list)

def expandFinalStates(FS):
    finalStates = [x.strip() for x in FS.split(',')]
    for iFS in finalStates:
        if iFS not in ['tt', 'et', 'mt', 'em']:
            print 'ERROR::Final state [%s] not supported, please choose [tt, et, mt, em]' %iFS
            return False
    return finalStates
 

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--profile", dest="profile", default=False, action="store_true", help="")
    parser.add_option("--FS", dest="FS", default='mt', help="final state product, et, tt")
    parser.add_option("--PUWeight", dest="PUWeight", default=False, action="store_true", help="")
    parser.add_option("--method", dest="method", default='Loose', help="")
    parser.add_option("--signal", dest="signal", default=False, action="store_true", help="")
    parser.add_option("--noGenEvtWeight", dest="noGenEvtWeight", default=False, action="store_true", help="")
    parser.add_option("--noNegGenEvts", dest="noNegGenEvts", default=False, action="store_true", help="")

    options, args = parser.parse_args()

    return options

options = opts()

def getVar(nEvents):
    if nEvents > 300:
        return 2
    elif nEvents > 80:
        return 4
    elif nEvents > 60:
        return 6
    else:
        return 8

def getPDFWeightID(i, iSample, pdfID):
    id = 2000 + i
    if "WJets" in iSample:
        id = 10 + i
    for j in range(len(pdfID)):
        if pdfID[j] == id:
            return j
    return -1, "not found!!"

def getVariations(pdfHists, initSumPDF, initSumWeights):
    ups = []
    downs = []
    ups_var = []
    downs_var = []
    nominals = []
    nBins = len(bins)
    lastBin = []
    xs_variations = initSumPDF
    for iBin in range(1, nBins):
        values = []
        if options.signal:
            pdfHists[0].Scale(1./initSumWeights)
        nominal = pdfHists[0].GetBinContent(iBin)
        nominal_unc = pdfHists[0].GetBinError(iBin)
        nominalEntry = pdfHists[0].GetEntries()
        nominals.append(nominal)
        for i in range(1, len(pdfHists)):
            if options.signal:
                pdfHists[i].Scale(1./initSumPDF[i-1])
            values.append(pdfHists[i].GetBinContent(iBin))
        #sort and pick 16 and 84
        down_quantile = 15-getVar(nominalEntry)
        up_quantile = 83+getVar(nominalEntry)

        beforeSort = values
        values.sort() 
        if nominal != 0:
            for i in values:
                lastBin.append(i/nominal)
        if nominal != 0:
            downs.append(values[15]/nominal)
            ups.append(values[83]/nominal)
            downs_var.append(values[down_quantile]/nominal)
            ups_var.append(values[up_quantile]/nominal)
        else:
            ups.append(1.0)
            downs.append(1.0)
            ups_var.append(1.0)
            downs_var.append(1.0)

#        print ""
#        for i in range(10):
#            print "%i: %.3f" %(i+11, values[i+10]/nominal)
#        print "nominal: ", nominal
#        for i in range(10):
#            print "%i: %.3f" %(i+79, values[i+78]/nominal)

    if options.signal:
        xs_variations.sort()
        xs_down = xs_variations[15]/(initSumWeights+0.0)
        xs_up = xs_variations[83]/(initSumWeights+0.0)

        print ""
        print "entries: %i" %nominalEntry
        print "variations \t down \t up \t\t sqrt"
        print "dxs/xs \t\t %.3f \t %.3f \t %.3f" %(xs_down, xs_up, math.sqrt(xs_up/xs_down))
        print "dac/ac \t\t %.3f \t %.3f \t %.3f" %(downs[0], 
                                                   ups[0], 
                                                   math.sqrt(ups[0]/downs[0]),
                                                )
        print "dac/ac (var)  %.3f \t %.3f \t %.3f" %(downs_var[0], 
                                                     ups_var[0], 
                                                     math.sqrt(ups_var[0]/downs_var[0]),
                                                )
        print "d(dac/ac) \t %.3f \t %.3f \t %.3f" %((downs[0]-downs_var[0])/downs[0], 
                                                (ups_var[0]-ups[0])/ups[0], 
                                                (math.sqrt(ups_var[0]/downs_var[0])-math.sqrt(ups[0]/downs[0]))/math.sqrt(ups[0]/downs[0]),
                                                )

    ups = []
    downs = []
    return ups, downs#, lastBin

def textArray(array):
    output = ""
    for i in array:
        if output != "":
            output += ", "
        if i > 0:
            output += "%.6f" %i
        else:
            output += "0"

    return output

r.gStyle.SetOptStat(0)

controlRegionName = 'SS'
signalRegionName = 'OS'

if options.method == 'Loose':
    controlRegionName = 'Loose'
    signalRegionName = 'Tight'

def loop_one_sample(iSample, iLocation, iFS):
    print 'combining sample [%s] for LUT' %(iSample)
    if 'data' in iSample:
        return 0
    if ('H2hh' in iSample) or ('ggH' in iSample) or ('Zprime' in iSample):
        return 0

    #pdfWeights
    pdfHists = []
    nWeights = 101
    initSumPDF = []
    for i in range(nWeights):
        pdfHists.append(r.TH1F("pdf_%i" %i, "", len(bins)-1, bins))
        pdfHists[i].Sumw2()
    iFile = r.TFile(iLocation)
    iTree = iFile.Get("Ntuple")
    nEntries = iTree.GetEntries()
    iTree.SetBranchStatus("*",1)
    iTree.SetBranchStatus("sampleName",0)

    eventCount = iFile.Get('eventCount')
    eventCountWeighted = iFile.Get('eventCountWeighted')

    if options.signal:
        for i in range(100):
            initSumPDF.append(int((iFile.Get('eventCountWeightedPDF_%i' %i)).GetBinContent(1)))
    hist_highPUWeight = r.TH1F("hist_highPUWeight", "", 50, 0.5, 1.5)
    hist_lowPUWeight =r.TH1F("hist_lowPUWeight", "", 50, 0.5, 1.5)

    yieldEstimator_OS = 0.0
    yieldEstimator_SS = 0.0
    fillcounter=0
    met = lvClass()
    nBins = len(plots_cfg.list)
#    nEntries = int(nEntries/3.)
    for iEntry in range(nEntries):
        iTree.GetEntry(iEntry)
        tool.printProcessStatus(iEntry, nEntries, 'looping over file %s' %(iSample), iEntry-1)
        met.SetCoordinates(iTree.pfMetEt, 0.0, iTree.pfMetPhi, 0)
        l1.SetCoordinates(iTree.pt_1, iTree.eta_1, iTree.phi_1, iTree.m_1)
        l2.SetCoordinates(iTree.pt_2, iTree.eta_2, iTree.phi_2, iTree.m_2)

        if not plots.passCut(iTree, iFS, False, l1, l2, met, ''):
            continue
        if options.method != 'SS' and iTree.q_1 == iTree.q_2:
            continue

        if plots.regionSelection(iTree, iFS, "control", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            sampleName = 'MC' + controlRegionName
        elif plots.regionSelection(iTree, iFS, "signal", options.method, plots_cfg.scanRange[0], plots_cfg.scanRange[1]):
            sampleName = iSample
        else:
            continue

        triggerEff = iTree.trigweight_1*iTree.trigweight_2
        xs = iTree.xs

        if 'WJets' in iSample:
            xs = xs*plots_cfg.WJetsScanRange[0]
        if "Zprime" in iSample:
            xs = plots.getZPrimeXS(iSample[7:])

        if eventCount:
            initEvents = int(eventCount.GetBinContent(1))
        else:    
            initEvents = int(iTree.initEvents)
        if eventCountWeighted:
            initSumWeights = int(eventCountWeighted.GetBinContent(1))
        else:    
            initSumWeights = int(iTree.initWeightedEvents)

        m_effective = (l1 + l2 + met).mass()
        #overflow and underflow
        if m_effective < plots_cfg.list[0]:
            m_effective = (plots_cfg.list[0] + plots_cfg.list[1])/2.0
        if m_effective > plots_cfg.list[nBins-1]:
            m_effective = (plots_cfg.list[nBins-1] + plots_cfg.list[nBins-2])/2.0
        if options.PUWeight:
            PUWeight = cutSampleTools.getPUWeight(iTree.nTruePU)
        else:
            PUWeight = 1.0

        genEventWeight = iTree.genEventWeight
        if options.noNegGenEvts and genEventWeight < 0:
            continue
        if options.noGenEvtWeight:
            genEventWeight = 1.0


        if (sampleName == 'MC' + controlRegionName) and ("WJets" in iSample):
            totalNormalWeights = triggerEff*xs*(plots.lumi)*genEventWeight*PUWeight
            pdfHists[0].Fill(m_effective, totalNormalWeights)
            for i in range(1, nWeights):
                pdfID = getPDFWeightID(i, iSample, iTree.pdfID)
                pdfHists[i].Fill(m_effective, totalNormalWeights*iTree.pdfWeight.at(pdfID))
        elif (controlRegionName not in sampleName) and ("WJets" not in iSample):
            totalNormalWeights = triggerEff*xs*(plots.lumi)*genEventWeight*PUWeight
            absMax = 0
            for i in range(1, nWeights):
                pdfID = getPDFWeightID(i, iSample, iTree.pdfID)
                if abs(iTree.pdfWeight.at(pdfID)) > absMax:
                    absMax = iTree.pdfWeight.at(pdfID)
            if absMax > 2.5:
                continue
            pdfHists[0].Fill(m_effective, totalNormalWeights)
            for i in range(1, nWeights):
                pdfID = getPDFWeightID(i, iSample, iTree.pdfID)
                pdfHists[i].Fill(m_effective, totalNormalWeights*iTree.pdfWeight.at(pdfID))
                #hist_highPUWeight.Fill(PUWeight)
                if PUWeight > 1.0:
                    hist_highPUWeight.Fill(iTree.pdfWeight.at(pdfID), genEventWeight*PUWeight)
                else:
                    hist_lowPUWeight.Fill(iTree.pdfWeight.at(pdfID), genEventWeight*PUWeight)

    c = r.TCanvas("c","Test",600, 600)
    c.Range(0,0,1,1)
    c.SetFillColor(0)
#    r.gPad.SetLogy()
        
    hist_highPUWeight.SetLineColor(r.kBlue)

    hist_lowPUWeight.SetLineColor(r.kRed)
#    hist_lowPUWeight.Scale(1./hist_lowPUWeight.Integral(0, hist_lowPUWeight.GetNbinsX()+1))
    hist_highPUWeight.Draw()
    hist_lowPUWeight.Draw("same")

    position  = (0.15, 0.85 - 0.05*2, 0.47, 0.85)
    histList = []
    histList.append((hist_highPUWeight, "high PU-weight events", 'l'))
    histList.append((hist_lowPUWeight, "low PU-weight events", 'l'))
    
    legends = tool.setMyLegend(position, histList)
    legends.Draw("same")

    c.Print('pdfSys.pdf')

    return getVariations(pdfHists, initSumPDF, initSumWeights)

def go():
    finalStates = expandFinalStates(options.FS)
    if not finalStates:
        return 0
    for iFS in finalStates:
        tail = ''
        totalQCD = 0.0

        if options.PUWeight:
            tail = '_withPUWeight'

        oFile = open('%s/LUT_%s%s.py' %(os.path.dirname(os.path.realpath(__file__)), iFS, tail),"w")        
        print 'creating LUT for final state: %s >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>' %iFS
        oFile.write('#!/usr/bin/env python\n')            
        oFile.write('luts = {}\n')            

        for iSample, iLocation, iCat in plots_cfg.sampleList:
            iLocation += '%s_noIso.root' %iFS
            ups, downs = loop_one_sample(iSample, iLocation, iFS)
            oFile.write('luts[\'%s_up\'] = [%s]\n' %(iSample, textArray(ups)))            
            oFile.write('luts[\'%s_down\'] = [%s]\n' %(iSample, textArray(downs))) 
            print ''           

#         for iSample, iLocation, iCat in plots_cfg.sampleList:
#             iLocation += '%s_noIso.root' %iFS
#             ups, downs, lastBin = loop_one_sample(iSample, iLocation, iFS)
# 
#         hist = r.TH1F("hist", "", 15, 0.7, 1.3)
#         for i in lastBin:
#             hist.Fill(i)
#         psfile = 'lastBin.pdf'
#         c = r.TCanvas("c","Test", 800, 600)
#         c.cd()
#         hist.SetTitle("; pdf variation / nominal; ")
#         hist.Draw()
#         ar_up = r.TArrow(ups[len(ups)-1],0.1,ups[len(ups)-1],5,0.02,"<|")
#         ar_up.SetAngle(60)
#         ar_up.SetFillColor(2)
#         ar_down = r.TArrow(downs[len(ups)-1],0.1,downs[len(ups)-1],5,0.02,"<|")
#         ar_down.SetAngle(60)
#         ar_down.SetFillColor(2)
#         ar_up.Draw()
#         ar_down.Draw()
# 
#         c.Print('%s' %psfile)




if __name__ == "__main__":
    if options.PUWeight:
        cutSampleTools.setupLumiReWeight()
    if options.profile:
        cProfile.run("go()", sort="time")
    else:
        go()
    if options.PUWeight:
        cutSampleTools.freeLumiReWeight()

