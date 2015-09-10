import supy
from cfg import enVars
import ROOT as r


class summed_ini_histos(supy.wrappedChain.calculable):
    def __init__(self, fs):
        self.fs = fs

    def update(self, _):
        self.value = []
        elements = self.source["chain"].GetListOfFiles()

        for hName in ["eventWeights", "eventCountWeighted", "eventCount"]:
            self.value.append(self.histo(elements, self.fs, hName))

    def histo(self, elements, hDir, hName):
        # http://root.cern.ch/root/html/TChain.html#TChain:AddFile
        out = None
        hPath = "%s/%s" % (hDir, hName)
        for iElement in range(elements.GetEntries()):
            element = elements.At(iElement)
            f = r.TFile(element.GetTitle())
            assert f
            h = f.Get(hPath)
            assert h, "Histogram %s not found." % hPath
            if out:
                out.Add(h)
            else:
                out = h.Clone()
                out.SetDirectory(0)
            f.Close()
        return out


class call_out_once(supy.analysisStep):
    def __init__(self, fs, sampleName, xs):
        self.done = False
        self.fs = fs
        self.sampleName = sampleName
        self.xs = xs

    def outputSuffix(self):
        return "_skim_entry_per_event.root"

    def uponAcceptance(self, s):
        if not self.done:
            # self.test_call_out(s["chain"], self.fs, self.outputFileName, self.sampleName, self.xs, histos=s["summed_ini_histos"])
            import cutSamples
            cutSamples.loop_one_sample(self.sampleName, "FAKE_iLocation", self.xs, self.fs,
                                       chain=s["chain"],
                                       outPutFileName=self.outputFileName,
                                       histos=s["summed_ini_histos"])
            self.done = True

    def test_call_out(self, chain, FS, outputFileName, sampleName, xs, histos):
        print chain.GetListOfFiles().GetEntries(), FS, outputFileName, sampleName, xs, histos


class slice(supy.analysis):
    def parameters(self):
        return {"FS": self.vary(dict([("tt", {}),
                                      ("et", {}),
                                      ("mt", {}),
                                      ("em", {}),
                                      ])
                                ),
                }

    def mainTree(self, fs):
        return ("%s/final" % fs, "Ntuple")

    def listOfSteps(self, p):
        found = False
        for name, path, xs, fs in enVars.sampleLocations:
            if name == p["sample"]:
                found = True
                break
        assert found

        return [supy.steps.printer.progressPrinter(),
                call_out_once(p["tag"], p["sample"], xs),
                ]

    def listOfCalculables(self, pars):
        out = supy.calculables.zeroArgs(supy.calculables)
        out += [summed_ini_histos(pars["tag"]),
                ]
        return out

    def listOfSampleDictionaries(self):
        h = supy.samples.SampleHolder()
        uf = 'utils.fileListFromDisk("%s", pruneList=False, isDirectory=True)'
        for name, path, xs, fs in enVars.sampleLocations:
            h.add(name, uf % path, xs=xs)
        return [h]

    def listOfSamples(self, pars):
        from supy.samples import specify
        out = []
        names = []
        for name, path, xs, fs in enVars.sampleLocations:
            if fs and fs != pars["tag"]:
                continue
            names.append(name)
            out += specify(names=name)
        assert len(names) == len(set(names)), names
        return tuple(out)
