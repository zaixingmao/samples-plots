#!/usr/bin/env python
import ROOT as r
import optparse
import tool


r.gROOT.SetBatch(True)  # to suppress canvas pop-outs

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--file1", dest="file1", default="", help="REQUIRED: .root file 1 over which to run")
    parser.add_option("--file2", dest="file2", default="", help="REQUIRED: .root file 2 over which to run")
    parser.add_option("--tree1", dest="tree1", default="tt/final/Ntuple", help="REQUIRED: tree name of file 1")
    parser.add_option("--tree2", dest="tree2", default="tt/final/Ntuple", help="REQUIRED: tree name of file 2")
    options, args = parser.parse_args()

    if not all([options.file1, options.file2]):
        parser.print_help()
        exit()
    return options

options = opts()

f1 = r.TFile(options.file1)
f2 = r.TFile(options.file2)
tree1 = f1.Get(options.tree1)
tree1.SetLineColor(r.kAzure+9)
tree1.SetFillColor(r.kAzure+9)
tree1.SetFillStyle(3003)
tree2 = f2.Get(options.tree2)
tree2.SetLineColor(2)
tree2.SetLineWidth(2)
tree2.SetLineStyle(2)
tHist1 = r.TH1F()
tHist1.SetLineColor(r.kAzure+9)
tHist1.SetFillColor(r.kAzure+9)
tHist1.SetFillStyle(3003) 
tHist2 = r.TH1F() 
tHist2.SetLineColor(2)
tHist2.SetLineWidth(2)
tHist2.SetLineStyle(2)

legendPosition = (0.5, 0.75, 0.9, 0.85)
legendHistos = [(tHist1,"%s with %d events" %(options.file1, tree1.GetEntries())),
                (tHist2,"%s with %d events" %(options.file2, tree2.GetEntries()))]
listBranch = tree1.GetListOfBranches()

oFileName = "diff.root"
ofile = r.TFile(oFileName, "RECREATE")

nBranches = listBranch.GetEntries()

for i in range(nBranches):
    iBranchName = listBranch.At(i).GetName()
    tmpCanvas = r.TCanvas(iBranchName,"c",800,600)

    tree1.Draw("%s" %(iBranchName), "")
    tree2.Draw("%s" %(iBranchName), "", "same")
    l = tool.setMyLegend(lPosition=legendPosition, lHistList=legendHistos)
    l.Draw("same")
    tmpCanvas.Write()
    tool.printProcessStatus(i+1, nBranches, 'Saving to file %s.root' %(oFileName))
print '  -- saved %d branches' %(nBranches)
    
