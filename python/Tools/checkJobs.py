#!/usr/bin/env python
import optparse
import sys
import os


def trueSize(sizeofFile):
    if sizeofFile.find('K'):
        return int(sizeofFile[0:sizeofFile.rfind('K')])
    elif sizeofFile.find('M'):
        return (int(sizeofFile[0:sizeofFile.rfind('M')])*1000)
    else:
        return "invalid size"
    

def opts(currentLocation):
    parser = optparse.OptionParser()
    parser.add_option("--l", dest="location", default=currentLocation, help="location for dump file")
    parser.add_option("--threshold", dest="threshold", default=4, help="location for dump file")

    options, args = parser.parse_args()
    return options

def checkJobs():
    os.system("du -lh > check.txt")
    currentLocation = os.getcwd()
    currentLocation = currentLocation + '/check.txt'
    opt = opts(currentLocation)
    lines = open(opt.location, "r").readlines()
    threshold = int(opt.threshold)

    foundIncompleteJobs = 0
    minSize = 999
    smallestSet = ''

    for iLine in range(len(lines)):
        current_line = lines[iLine]
        sizeofFile = current_line.split()[0]
        TrueSize = trueSize(sizeofFile)
        if TrueSize != "invalid size" and TrueSize < minSize:
            minSize = TrueSize
            smallestSet = current_line

        if len(sizeofFile) < threshold:
            print current_line
            foundIncompleteJobs += 1

    if foundIncompleteJobs:
        print 'Found %i incomplete jobs as above' %foundIncompleteJobs

    else:
        print 'Smallest output:   %s' %(smallestSet)
        print 'All %i jobs seems to have been completed' %len(lines)

    os.system("rm check.txt")
