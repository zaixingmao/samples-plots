import ROOT as r


r.gROOT.LoadMacro("Htautau_TriggerEfficiency.h+")
__namespace = r.analysis.Htautau_Summer13.trigger.Run2012ABCD.TauTau

__DiTau_correction_one_leg = __namespace.DiTau.WeightOneLeg
__DiTauJet_correction_one_leg = __namespace.DiTauJet.WeightOneLeg

__DiTau_eff_tau_mc   = __namespace.DiTau.MC.tauEfficiency
__DiTau_eff_tau_data = __namespace.DiTau.Data.tauEfficiency

__DiTauJet_eff_tau_mc   = __namespace.DiTauJet.MC.tauEfficiency
__DiTauJet_eff_tau_data = __namespace.DiTauJet.Data.tauEfficiency
__DiTauJet_eff_jet_data = __namespace.DiTauJet.Data.jetEfficiency


def __correction_one_leg(tree, pt, eta):
    tt = False
    tt |= tree.HLT_DoubleMediumIsoPFTau35_Trk5_eta2p1_fired
    tt |= tree.HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_fired
    if tt:
        return __DiTau_correction_one_leg(pt, eta)

    ttj = False
    ttj |= tree.HLT_DoubleMediumIsoPFTau25_Trk5_eta2p1_Jet30_fired
    ttj |= tree.HLT_DoubleMediumIsoPFTau30_Trk5_eta2p1_Jet30_fired
    ttj |= tree.HLT_DoubleMediumIsoPFTau30_Trk1_eta2p1_Jet30_fired
    if ttj:
        return __DiTauJet_correction_one_leg(pt, eta)

    return 0.0


def correction_leg1(tree, iBestPair):
    return __correction_one_leg(tree, tree.pt1.at(iBestPair), tree.eta1.at(iBestPair))


def correction_leg2(tree, iBestPair):
    return __correction_one_leg(tree, tree.pt2.at(iBestPair), tree.eta2.at(iBestPair))
