#!/usr/bin/env python

import ROOT as r
r.gROOT.SetBatch(True)
r.PyConfig.IgnoreCommandLineOptions = True

import os
import optparse
from supy import utils
import plots_cfg


def opts():
    parser = optparse.OptionParser("usage: %prog dir1 dir2")
    parser.add_option("-n", "--dry-run", dest="dry_run", default=False, action="store_true", help="print commands rather than execute them")
    parser.add_option("-v", "--verbose", dest="verbose", default=False, action="store_true", help="print sets of filenames")
    options, args = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        exit()
    return options, args


def notify(s, msg):
    print msg
    for f in sorted(s):
        print f
    if not s:
        print "(None)"
    print


def common_files(dir1, dir2, verbose):
    s1 = set(os.listdir(dir1))
    s2 = set(os.listdir(dir2))
    common = s1.intersection(s2)

    if verbose:
        notify(s1 - s2, "Only in %s:" % dir1)
        notify(s2 - s1, "Only in %s:" % dir2)
        notify(common, "Common:")

    return common


def system(x):
    os.system(x)


def main(nCores=None, out_dir=""):
    options, (dir1, dir2) = opts()
    args = []
    for f in common_files(dir1, dir2, verbose=options.verbose):
        csd_args = "--f1 %s/%s --f2 %s/%s --n1 one --n2 two --t1 Ntuple --t2 Ntuple --subset diff" % (dir1, f, dir2, f)
        out_file = f.replace(".root", "_comparison.txt")
        t = ("./checkSyncDev.py %s > %s/%s" % (csd_args, out_dir, out_file),)
        args.append(t)

    if options.dry_run:
        for arg in args:
            print arg[0]
    else:
        utils.mkdir(out_dir)
        utils.operateOnListUsingQueue(nCores, utils.qWorker(system), args)


if __name__ == "__main__":
    main(nCores=4, out_dir="comparison_results")
