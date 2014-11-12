import ROOT as r

def calcTrigOneTauEff(eta, pt, data = True, fitStart=25):
        le14_da = {20: (0.898, 44.3, 1.02),
                  25: (0.866, 43.1, 0.86),
                  30: (0.839, 42.3, 0.73),
                  35: (0.846, 42.4, 0.78),
                  }
        le14_mc = {20: (0.837, 43.6, 1.09),
                   25: (0.832, 40.4, 0.80),
                   30: (0.829, 40.4, 0.74),
                   35: (0.833, 40.1, 0.86),
                   }
        ge16_da = {20: (0.81, 43.6, 1.09),
                   25: (0.76, 41.8, 0.86),
                   30: (0.74, 41.2, 0.75),
                   35: (0.74, 41.2, 0.79),
                   }
        ge16_mc = {20: (0.70, 39.7, 0.95),
                   25: (0.69, 38.6, 0.74),
                   30: (0.69, 38.7, 0.61),
                   35: (0.69, 38.8, 0.61),
                   }
        le14 = le14_da if data else le14_mc
        ge16 = ge16_da if data else ge16_mc
        if abs(eta) < 1.4:
            d = le14
        else:
            d = ge16
        e, x0, sigma = d[fitStart]
        y = r.TMath.Erf((pt-x0)/2.0/sigma/math.sqrt(pt))  # https://github.com/rmanzoni/HTT/blob/master/CMGTools/H2TauTau/interface/TriggerEfficiency.h
        #y = r.TMath.Erf((pt-x0)/sigma/math.sqrt(2.0))
        return (1+y)*e/2.0

r.gROOT.LoadMacro("Htautau_TriggerEfficiency.h+")
