#!/usr/bin/env python
import sys
import ROOT as r
import time
from operator import itemgetter
import os

lvClass = r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))
b1 = lvClass()
b2 = lvClass()
tau1 = lvClass()
tau2 = lvClass()
j1 = lvClass()
j2 = lvClass()
v_tmp = lvClass()


def matchBJet(tree):
    genBPt1 = tree.genBPt.at(0)
    genBPt2 = tree.genBPt.at(1)
    genBEta1 = tree.genBEta.at(0)
    genBEta2 = tree.genBEta.at(1)
    genBPhi1 = tree.genBPhi.at(0)
    genBPhi2 = tree.genBPhi.at(1)
    genBMass1 = tree.genBMass.at(0)
    genBMass2 = tree.genBMass.at(1)

    b1.SetCoordinates(genBPt1, genBEta1, genBPhi1, genBMass1)
    b2.SetCoordinates(genBPt2, genBEta2, genBPhi2, genBMass2)
    
    dr1 = 1000
    dr2 = 1000

    #Loop to find best matching gen jet
    for j in range(1, 5):
        v_tmp.SetCoordinates(tree.GetLeaf("J%sPt" %(j)).GetValue(0),
                             tree.GetLeaf("J%sEta" %(j)).GetValue(0),
                             tree.GetLeaf("J%sPhi" %(j)).GetValue(0),
                             4.8)
        if dr1 > r.Math.VectorUtil.DeltaR(b1, v_tmp):
            dr1 = r.Math.VectorUtil.DeltaR(b1, v_tmp)
            j1pt = tree.GetLeaf("J%sPt" %(j)).GetValue(0)
            j1eta = tree.GetLeaf("J%sEta" %(j)).GetValue(0)
            j1phi = tree.GetLeaf("J%sPhi" %(j)).GetValue(0)
        if dr2 > r.Math.VectorUtil.DeltaR(b2, v_tmp):
            dr2 = r.Math.VectorUtil.DeltaR(b2, v_tmp)
            j2pt = tree.GetLeaf("J%sPt" %(j)).GetValue(0)
            j2eta = tree.GetLeaf("J%sEta" %(j)).GetValue(0)
            j2phi = tree.GetLeaf("J%sPhi" %(j)).GetValue(0)


    if dr1 < 0.5 and dr2 < 0.5:
        j1.SetCoordinates(j1pt, j1eta, j1phi, 4.8)
        j2.SetCoordinates(j2pt, j2eta, j2phi, 4.8)
    
    return j1, j2

def genHiggsMatchGenTaus(tree):
    higgs = lvClass()
    if tree.genTauPt.size():
        tau1.SetCoordinates(tree.genTauPt.at(0), tree.genTauEta.at(0), tree.genTauPhi.at(0), tree.genTauMass.at(0))
        if tree.genTauPt.size() > 1:
            tau2.SetCoordinates(tree.genTauPt.at(1), tree.genTauEta.at(1), tree.genTauPhi.at(1), tree.genTauMass.at(1))
    
    combinedGenTaus = tau1 + tau2

    dr = 1.
    #Loop to find best matching gen jet
    for j in range(tree.higgsPt.size()):
        v_tmp.SetCoordinates(tree.higgsPt.at(j), tree.higgsEta.at(j),
                             tree.higgsPhi.at(j), 125)
        dr_tmp = r.Math.VectorUtil.DeltaR(combinedGenTaus, v_tmp)

        if dr > dr_tmp:
            dr = dr_tmp
            higgs = v_tmp

    return higgs, dr

def printProcessStatus(iCurrent, total, processName = 'Foo process', iPrevious = None):
    iCurrent+=0.
    total+=0.
    AddedPercent = iCurrent/total
    AddedPercent_Pre = -1
    if iPrevious != None:
        AddedPercent_Pre = round((iPrevious+0.0)/total,2)
    if AddedPercent_Pre < round(AddedPercent,2):
        sys.stdout.write("\r%s completed: %0.f" %(processName, round(AddedPercent,2)*100) + "%")
        sys.stdout.flush()

def findFilesInDir(dirName):
    for iFile in os.listdir(dirName):
        fName = dirName + '/' + iFile
        if fName.endswith(".root"):
            print fName

def addFiles(ch, dirName, knownEventNumber, maxFileNumber=-1, printTotalEvents = False, blackList = []):
    added = 0.
    totalAmount = len(os.listdir(dirName))
    for iFile in os.listdir(dirName):
        fName = dirName + '/' + iFile
        if fName in blackList:
            continue
        if fName.endswith(".root"):
            ch.Add(fName, knownEventNumber)
            added+=1
            if maxFileNumber-added == 0:
                break
            printProcessStatus(iCurrent=added, total=totalAmount, processName = 'Adding files from [%s]' %dirName, iPrevious = added - 1)
    if printTotalEvents:
        nEntries = ch.GetEntries()
        print "  -- found %d events" %(nEntries)
        return nEntries
    else:
        print " "
        return added

def unitNormHists(HistNameList):
    integralList = []
    for iHist in HistNameList:
        integral = iHist.Integral()
        integralList.append(integral+0.)
        if integral > 0:
            iHist.Scale(1/integral)
    print integralList
    return integralList

def xsNormHists(HistNameList, xsList):
    i=0
    for iHist in HistNameList:
        integral = iHist.Integral()
        if integral > 0:
            iHist.Scale(xsList[i]/integral*20)
        i+=1

def setDraw2Hists(hist1, hist2, drawColor=1, DrawOpt = ""):

    hist1.SetLineWidth(1)
    hist1.SetLineStyle(2)
    hist2.SetFillStyle(0)
    hist1.SetLineColor(drawColor)

    hist2.SetLineWidth(1)
    hist2.SetFillStyle(3944)
    hist2.SetFillColor(drawColor)
    hist2.SetLineColor(drawColor)

    histMaxList = [(hist1.GetMaximum(), hist1), (hist2.GetMaximum(), hist2)]
    histMaxList = sorted(histMaxList, key=itemgetter(0), reverse=True)
    #draw from the highest histogram

    histMaxList[0][1].Draw(DrawOpt)
    histMaxList[1][1].Draw("same %s" %(DrawOpt))

def setDraw2Hists(hist1, hist2, drawColor1=1, drawColor2=1, DrawOpt = ""):

    hist1.SetLineWidth(1)
    hist1.SetLineStyle(2)
    hist2.SetFillStyle(0)
    hist1.SetLineColor(drawColor1)

    hist2.SetLineWidth(1)
    hist2.SetFillStyle(3944)
    hist2.SetFillColor(drawColor2)
    hist2.SetLineColor(drawColor2)

    histMaxList = [(hist1.GetMaximum(), hist1), (hist2.GetMaximum(), hist2)]
    histMaxList = sorted(histMaxList, key=itemgetter(0), reverse=True)
    #draw from the highest histogram

    histMaxList[0][1].Draw(DrawOpt)
    histMaxList[1][1].Draw("same %s" %(DrawOpt))


def setDraw3Hists(hist1, hist2, fixHist, drawColor=1):

    hist1.SetLineWidth(1)
    hist1.SetLineStyle(2)
    hist2.SetFillStyle(0)
    hist1.SetLineColor(drawColor)

    hist2.SetLineWidth(1)
    hist2.SetFillStyle(3944)
    hist2.SetFillColor(drawColor)
    hist2.SetLineColor(drawColor)

    fixHist.SetLineWidth(1)
    fixHist.SetLineStyle(2)
    fixHist.SetLineColor(46)

    histMaxList = [(hist1.GetMaximum(), hist1), (hist2.GetMaximum(), hist2), (fixHist.GetMaximum(), fixHist)]
    histMaxList = sorted(histMaxList, key=itemgetter(0), reverse=True)
    #draw from the highest histogram

    histMaxList[0][1].Draw()
    histMaxList[1][1].Draw("same")
    histMaxList[2][1].Draw("same")
    


def setDrawHists(sigHist, ttHist, ZZHist, DrawOpt = ""):

    sigHist.SetLineWidth(2)
    sigHist.SetFillStyle(3001)
    sigHist.SetFillColor(4)
    sigHist.SetLineColor(4)

    ttHist.SetLineWidth(2)
#     ttHist.SetFillStyle(3001)
#     ttHist.SetFillColor(2)
    ttHist.SetLineColor(2)
    ttMax = ttHist.GetMaximum() 

    ZZHist.SetLineWidth(2)
    ZZHist.SetLineStyle(2)
    ZZHist.SetLineColor(1)
    ZZMax = ZZHist.GetMaximum()

    HistMaxList = [(sigHist.GetMaximum(), sigHist),
                   (ttHist.GetMaximum(), ttHist),
                   (ZZHist.GetMaximum(), ZZHist)]
    HistMaxList = sorted(HistMaxList, key=itemgetter(0), reverse=True)
    #draw from the highest histogram

    HistMaxList[0][1].Draw(DrawOpt)
    DrawOpt = "same" + DrawOpt
    HistMaxList[1][1].Draw(DrawOpt)
    HistMaxList[2][1].Draw(DrawOpt)

def setDrawHists2(sigHist1, sigHist2, sigHist3, ttHist, ZZHist, DrawOpt = ""):

    sigHist1.SetLineWidth(2)
    sigHist1.SetFillStyle(3001)
    sigHist1.SetFillColor(4)
    sigHist1.SetLineColor(4)

    sigHist1.SetLineWidth(2)
    sigHist2.SetFillStyle(3001)
    sigHist2.SetFillColor(6)
    sigHist2.SetLineColor(6)

    sigHist3.SetLineWidth(2)
    sigHist3.SetFillStyle(3001)
    sigHist3.SetFillColor(8)
    sigHist3.SetLineColor(8)

    ttHist.SetLineWidth(2)
    ttHist.SetFillStyle(3001)
    ttHist.SetFillColor(2)
    ttHist.SetLineColor(2)
    ttMax = ttHist.GetMaximum() 

    ZZHist.SetLineWidth(2)
    ZZHist.SetLineStyle(2)
    ZZHist.SetLineColor(1)
    ZZMax = ZZHist.GetMaximum()
    
    HistMaxList = [(sigHist1.GetMaximum(), sigHist1),
                   (sigHist2.GetMaximum(), sigHist2),
                   (sigHist3.GetMaximum(), sigHist3),
                   (ttHist.GetMaximum(), ttHist),
                   (ZZHist.GetMaximum(), ZZHist)]
    HistMaxList = sorted(HistMaxList, key=itemgetter(0), reverse=True)
    #draw from the highest histogram

    HistMaxList[0][1].Draw(DrawOpt)
    DrawOpt = "same" + DrawOpt
    HistMaxList[1][1].Draw(DrawOpt)
    HistMaxList[2][1].Draw(DrawOpt)
    HistMaxList[3][1].Draw(DrawOpt)
    HistMaxList[4][1].Draw(DrawOpt)

def setDrawHists4(hist1, hist2, hist3, hist4, DrawOpt = ""):

    hist1.SetLineWidth(2)
    hist1.SetLineStyle(2)
    hist1.SetLineColor(63)

    hist2.SetLineWidth(2)
    hist2.SetLineStyle(2)
    hist2.SetLineColor(6)

    hist3.SetLineWidth(2)
    hist3.SetLineColor(4)

    hist4.SetLineWidth(2)
    hist4.SetLineColor(2)
    
    HistMaxList = [(hist1.GetMaximum(), hist1),
                   (hist2.GetMaximum(), hist2),
                   (hist3.GetMaximum(), hist3),
                   (hist4.GetMaximum(), hist4)]
    HistMaxList = sorted(HistMaxList, key=itemgetter(0), reverse=True)
    #draw from the highest histogram

    HistMaxList[0][1].Draw(DrawOpt)
    DrawOpt = "same" + DrawOpt
    HistMaxList[1][1].Draw(DrawOpt)
    HistMaxList[2][1].Draw(DrawOpt)
    HistMaxList[3][1].Draw(DrawOpt)

def setMyLegend(lPosition, lHistList):
    l = r.TLegend(lPosition[0], lPosition[1], lPosition[2], lPosition[3])
    l.SetFillStyle(0)
    l.SetBorderSize(0)
    for i in range(len(lHistList)):
        l.AddEntry(lHistList[i][0], lHistList[i][1])
    return l

def addHistFirstBinFromFiles(dirName, nBins=15, xMin=0, xMax=14):
    added = 0.
    firstBinSum = 0
    dir = r.TSystemDirectory(dirName, dirName)
    files = dir.GetListOfFiles()
    totalAmount = files.GetSize() - 2.
    for iFile in files:
        fName = dirName + '/' + iFile.GetName()
        if (not iFile.IsDirectory()) and fName.endswith(".root"):
            tmpHist = r.TH1F("tmpHist", " ", nBins, xMin, xMax)
            ifile = r.TFile(fName)
            tmpHist = ifile.Get("TT/results")
            firstBinSum+=tmpHist.GetBinContent(1)
            added+=1
            printProcessStatus(iCurrent=added, total=totalAmount, processName = 'Adding files from [%s]' %dirName, iPrevious = added -1)
    print ""
    return firstBinSum

def addHistFromFiles(dirName, histName, hist, xAxisLabels = ['']):
    added=0.
    dir = r.TSystemDirectory(dirName, dirName)
    files = dir.GetListOfFiles()
    totalAmount = files.GetSize() - 2.
    isFirstFile = True
    for iFile in files:
        fName = dirName + '/' + iFile.GetName()
        if (not iFile.IsDirectory()) and fName.endswith(".root"):
            tmpHist = r.TH1F()
            ifile = r.TFile(fName)
            if ifile.IsZombie():
                print 'skipping file: %s' %(fName)
                continue
            tmpHist = ifile.Get(histName)
            nBins = tmpHist.GetNbinsX()
            for i in range(len(xAxisLabels)):
                if i+1 <= nBins: 
                    hist.Fill(xAxisLabels[i],tmpHist.GetBinContent(i+1))
                else:
                    hist.Fill(xAxisLabels[i], 0)
            added+=1.
            printProcessStatus(iCurrent=added, total=totalAmount, processName = 'Adding Histogram from files in [%s]' %dirName, iPrevious = added - 1)
    print ""

def addEventsCount2Hist(hist, count, labelName):
    hist.Fill(labelName, count)

def reWeightROOTFile(fileName, treeName, weight = 1.0):
    oldFile = r.TFile(fileName, "READ")
    tree = oldFile.Get(treeName)
    newFileName = './' + fileName[fileName.rfind('/'): fileName.find('.')] + "_reweighted.root"
    newFile = r.TFile(newFileName, "NEW")
    newTree = tree.CloneTree(-1, 'fast')
    entries = tree.GetEntries()
    newTree.SetWeight(weight/entries)
    newFile.Write()
    newFile.Close()
    oldFile.Close()
    return newFileName

def calc(iChain):# 
#     if  iChain.pt2.at(0) > 40 and iChain.J1Pt > 30 and abs(iChain.J1Eta) < 3.1:
#         return True
#     else:
#         return False
    return True

def addFakeTHStack(hist, stack, scale = 1.0):
    for iHist in stack.GetHists():
        for i in range(iHist.GetNbinsX()):
            currentValue = hist.GetBinContent(i+1)
            if currentValue < 0:
                currentValue = 0
            hist.SetBinContent(i+1,currentValue + iHist.GetBinContent(i+1)*scale)
            a = currentValue + iHist.GetBinContent(i+1)*scale
            b = iHist.GetBinContent(i+1)
            if a < b:
                print a, b, currentValue
    return hist

def nameEnDecoder(name, opt = 'encode'):
    nameDict = {'H2hh260': 260,
                'H2hh270': 270,
                'H2hh280': 280,
                'H2hh290': 290,
                'H2hh300': 300,
                'H2hh310': 310,
                'H2hh320': 320,
                'H2hh330': 330,
                'H2hh340': 340,
                'H2hh350': 350,
                'H2hh500': 500,
                'H2hh700': 700,
                'H2hh1000': 1000,
                'tt': 1,
                'tt_semi': 2,
                'tthad': 3,
                't': 4,
                'tbar': 5,
                'ZZ': 6,
                'zzTo2L2Nu': 7,
                'zzTo4L': 8,
                'WJetsToLNu': 10,
                'W1JetsToLNu': 11,
                'W2JetsToLNu': 12,
                'W3JetsToLNu': 13,
                'W4JetsToLNu': 14,
                'WZJetsTo2L2Q': 15,
                'WW': 16,
                'WZ3L': 17,
                'DYJetsToLL': 20,
                'DY1JetsToLL': 21,
                'DY2JetsToLL': 22,
                'DY3JetsToLL': 23,
                'DY4JetsToLL': 24,
                'GluGlu': 50,
                'VBF': 60,
                'dataOSRelax': 0,
                'tt_embed': 2001,
                'DY_embed': 2002
                }

    if opt == 'encode': 
        start = name.rfind('TMVARegApp_')
        if start != -1:
            name = name[len(TMVARegApp_): name.find("_all")]
        elif name.find("_all") != -1:
            name = name[:name.find("_all")]
        return nameDict[name]
    else:
        inv_nameDict = dict((nameDict[k], k) for k in nameDict)
        return inv_nameDict[name]