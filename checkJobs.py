#!/usr/bin/env python
import optparse
import sys
import os


def trueSize(sizeofFile):
    k = sizeofFile.find('K')
    m = sizeofFile.find('M')
    if 0 <= k:
        return float(sizeofFile[:k])
    elif 0 <= m:
        return float(sizeofFile[:m]) * 1000
    else:
        print "invalid size:", sizeOfFile
        return None

def get_hdfs_location(location):
    data_location = '/store/user/'
    log_location = '/uscms_data/d3/'
    if location.find('/submit') > 0:
        data_location += location[len(log_location):location.find('/submit')]
    else:
        data_location += location[len(log_location):]
    print location
    return data_location

def opts():
    parser = optparse.OptionParser()
    parser.add_option("--l", dest="location", default='currentLocation', help="location for dump file")
    parser.add_option("--threshold", dest="threshold", default=4, help="threshold for dir size")
    parser.add_option("--fileType", dest="fileType", default='-', help="prefix of dir name")
    options, args = parser.parse_args()
    return options

def checkJobs(opt):
    currentLocation = os.getcwd()
    if opt.location == 'currentLocation':
        location = currentLocation
    else:
        os.system("du -lh > check.txt")
        location = opt.location
        os.chdir(location)
    print 'In %s' %location

#    os.system("eos root://cmseos.fnal.gov ls %s | wc > check.txt" %get_hdfs_location(location))
    os.system("eos root://cmseos.fnal.gov ls -lhtr %s  > check.txt" %get_hdfs_location(location))

    lines2 = open(location + '/check.txt', "r").readlines()
    finishedFiles = 0
    smallestLine = ""
    smallestFile = 99999999
    for iLine in lines2:
        finished = False
        currentFileSize = 0
        if iLine.split()[5] == "M":
            currentFileSize = float(iLine.split()[4])*1000
        elif iLine.split()[5] == "G":
            currentFileSize = float(iLine.split()[4])*1000000
        elif iLine.split()[5] == "k":
            currentFileSize = float(iLine.split()[4])
        else:
            currentFileSize = float(iLine.split()[4])/1000
        if currentFileSize > 5:
            finishedFiles += 1
            if smallestFile > currentFileSize:
                smallestFile = currentFileSize
                smallestLine = iLine.split()[9]
        else:
            print "failed: ", currentFileSize, iLine.split()[8]

    os.system("rm check.txt")

    os.system("du -lh > check.txt")
    location = location + '/check.txt'
    lines = open(location, "r").readlines()
    threshold = int(opt.threshold)

    foundIncompleteJobs = 0
    foundCompleteJobs = 0
    minSize = 999
    smallestSet = ''

    for iLine in range(len(lines)):
        current_line = lines[iLine]
        if not (opt.fileType in current_line):
            continue
        sizeofFile = current_line.split()[0]
        TrueSize = trueSize(sizeofFile)
        if (TrueSize is not None) and TrueSize < minSize:
            minSize = TrueSize
            smallestSet = current_line

        if len(sizeofFile) < threshold:
            print current_line
            foundIncompleteJobs += 1
        else:
            foundCompleteJobs += 1

    if foundIncompleteJobs:
        print 'Found %i incomplete jobs as above' %foundIncompleteJobs
        print '%i of %i jobs complete' %(foundCompleteJobs, (foundCompleteJobs+foundIncompleteJobs))
    elif foundCompleteJobs:
        print 'Smallest output:   %s' %(smallestSet)
        print 'All %i jobs seems to have been completed' %foundCompleteJobs
    else:
        print 'No file with *%s* found' %opt.fileType

    print 'Found %s root files out of %i jobs' %(finishedFiles, foundCompleteJobs+foundIncompleteJobs)
    print 'Smallest output file is %s with size %.2fK' %(smallestLine, smallestFile)
    os.system("rm check.txt")

if __name__ == "__main__":
    opt = opts()
    checkJobs(opt)
