#!/usr/bin/env python

import os
import ROOT as r


# use same hypotheses for all events
hypo_mh1 = r.std.vector('Int_t')()
hypo_mh2 = r.std.vector('Int_t')()
hypo_mh1.push_back(125)
hypo_mh2.push_back(125)


def setup(path="HHKinFit", lib="libHHKinFit.so"):
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/HHKinFit
    full = "%s/%s" % (path, lib)
    if not os.path.exists(full):
        os.system("cd %s && ./compile.sh" % path)
    r.gSystem.Load(full)
    r.gROOT.LoadMacro("%s/include/HHKinFitMaster.h+" % path)


def fit(tree, j1, j2):
    # NOTE! j1 and j2 are expected to be r.Math.LorentzVector(r.Math.PtEtaPhiM4D('double'))

    b1 = r.TLorentzVector()
    b2 = r.TLorentzVector()
    tauvis1 = r.TLorentzVector()
    tauvis2 = r.TLorentzVector()

    b1.SetPtEtaPhiM(j1.pt(), j1.eta(), j1.phi(), j1.mass())
    b2.SetPtEtaPhiM(j2.pt(), j2.eta(), j2.phi(), j2.mass())

    tauvis1.SetPtEtaPhiM(tree.pt1.at(0), tree.eta1.at(0), tree.phi1.at(0), tree.m1.at(0))
    tauvis2.SetPtEtaPhiM(tree.pt2.at(0), tree.eta2.at(0), tree.phi2.at(0), tree.m2.at(0))

    kinFits = r.HHKinFitMaster(b1, b2, tauvis1, tauvis2)

    ptmiss = r.TLorentzVector()
    ptmiss.SetPtEtaPhiM(tree.met.at(0), 0.0, tree.metphi.at(0), 0.0)

    metcov = r.TMatrixD(2, 2)
    metcov[0][0] = tree.mvacov00
    metcov[1][0] = tree.mvacov10
    metcov[0][1] = tree.mvacov01
    metcov[1][1] = tree.mvacov11
    #metcov.Print()

    kinFits.setAdvancedBalance(ptmiss, metcov)

    kinFits.addMh1Hypothesis(hypo_mh1)
    kinFits.addMh2Hypothesis(hypo_mh2)
    
    kinFits.doFullFit()
    chi2 = kinFits.getBestChi2FullFit()
    mh = kinFits.getBestMHFullFit()
    #prob = kinFits.getFitProbFullFit()
    #print prob
    #print iEvent, chi2, prob, mh
    return chi2, mh