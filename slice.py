import supy
import configuration
import os
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

    def outputSuffix(self):
        return "_events.root"

    def setup(self, chain, fileDir):
        self.outputFile = r.TFile(self.outputFileName, "RECREATE")
        self.outputFile.Close()

    # copied from supy.steps.master
    def mergeFunc(self, products) :
        def printComment(lines) :
            if self.quietMode : return
            skip = ['Source file','Target path','Found subdirectory']
            line = next(L for L in lines.split('\n') if not any(item in L for item in skip))
            print line.replace("Target","The output") + " has been written."

        def cleanUp(stderr, files) :
            okList = configuration.haddErrorsToIgnore()
            assert (stderr in okList), "hadd had this stderr: '%s'"%stderr
            if stderr : print stderr
            for fileName in files : os.remove(fileName)

        tmp = self.outputFileName.replace(".root", "_tmp.root")
        hAdd = supy.utils.getCommandOutput("%s -f %s %s"%(configuration.hadd(), tmp, " ".join(products["outputFileName"])))
        printComment(hAdd["stdout"])
        cleanUp(hAdd["stderr"], products["outputFileName"])

        # re-hadding was observed to reduce drastically the memory usage of chain.GetEntry(0)
        hAdd = supy.utils.getCommandOutput("%s -f %s %s"%(configuration.hadd(), self.outputFileName, tmp))
        printComment(hAdd["stdout"])
        cleanUp(hAdd["stderr"], [tmp])


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
        out = []
        for name, path, xs, fs in enVars.sampleLocations:
            if (not fs) or fs == pars["tag"]:
                out += supy.samples.specify(names=name)
        return tuple(out)
