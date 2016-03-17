#!/usr/bin/env python
import optparse
import sys
import os
import time


def opts():
    parser = optparse.OptionParser()
    parser.add_option("--l", dest="location", default='currentLocation', help="location for dump file")
    parser.add_option("--loop", dest="loop", default=False, action="store_true", help="location for dump file")
    parser.add_option("--list", dest="list", default=False, action="store_true", help="location for dump file")

    options, args = parser.parse_args()
    return options

dir = "/nfs_scratch/zmao/Jan12Prodruction_jetBTag/"
fileList = []


def checkJobs(location):
    checks = ['147M', '152M', '161M', '156M', '151M']
    currentLocation = os.getcwd()

    print 'In %s' %location
    os.system("du -lh %s > check.txt" %location)
    location = 'check.txt'
    lines = open(location, "r").readlines()
    rmCounter = 0
    for iLine in range(len(lines)):
        current_line = lines[iLine]
        if current_line[0:4] in checks:
            os.system("rm %s/user_code.tgz" %current_line[4:current_line.rfind('\n')])
            rmCounter+=1
    print time.strftime("%c") + 'removed %i files' %rmCounter
    os.system("rm check.txt")

if __name__ == "__main__":
    opt = opts()
    if opt.location == 'currentLocation':
        location = currentLocation

    else:
        location = opt.location
    if not opt.list:
        checkJobs(location)
        while opt.loop:
            time.sleep(60)
            checkJobs(location)
    else:
        for location in fileList:
            checkJobs(location)
            while opt.loop:
                time.sleep(60)
                checkJobs(location)
