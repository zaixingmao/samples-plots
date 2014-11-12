import ROOT as r


r.gROOT.LoadMacro("Htautau_TriggerEfficiency.h+")
__namespace = r.analysis.Htautau_Summer13.trigger.Run2012ABCD.TauTau
__DiTauWeightOneLeg = __namespace.DiTau.WeightOneLeg
__DiTauJetWeightOneLeg = __namespace.DiTauJet.WeightOneLeg


def __efficiency_one_leg(tree, pt, eta):
    tt = False
    tt |= tree.HLT_DoubleMediumIsoPFTau35_Trk5_eta2p1_fired
    tt |= tree.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_fired
    if tt:
        return __DiTauWeightOneLeg(pt, eta)

    ttj = False
    ttj |= tree.HLT_DoubleMediumIsoPFTau25_Trk5_eta2p1_Jet30_fired
    ttj |= tree.HLT_DoubleMediumIsoPFTau30_Trk5_eta2p1_Jet30_fired
    ttj |= tree.HLT_DoubleMediumIsoPFTau30_Trk1_eta2p1_Jet30_fired
    if ttj:
        return __DiTauJetWeightOneLeg(pt, eta)

    return 0.0


def efficiency1(tree, iBestPair):
    return __efficiency_one_leg(tree, tree.pt1.at(iBestPair), tree.eta1.at(iBestPair))


def efficiency2(tree, iBestPair):
    return __efficiency_one_leg(tree, tree.pt2.at(iBestPair), tree.eta2.at(iBestPair))
