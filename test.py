#!/usr/bin/env python
import ROOT as r

r.gStyle.SetOptStat(0)
r.gSystem.Load("libFWCoreFWLite.so")
r.AutoLibraryLoader.enable()


def test(file):
    ifile = r.TFile(file)
    tree = ifile.Get("Events")
    
    hist = r.TH1F('hist', '', 4, 0, 4)

    nEntries = tree.GetEntries()
    for i in range(nEntries):
        tree.GetEntry(i)
        print (tree.edmTriggerResults_TriggerResults__PAT).getTriggerNames().at(0)

test('/home/zmao/EE72ECF8-996B-E411-B541-20CF305B057C.root')