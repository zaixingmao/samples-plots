#!/usr/bin/env python
import optparse
import sys
import os


def opts():
    parser = optparse.OptionParser()
    parser.add_option("--l", dest="location", default='currentLocation', help="location for dump file")
    options, args = parser.parse_args()
    return options

def checkJobs(opt):
    checks = ['66M', '65M', '64M']
    currentLocation = os.getcwd()
    if opt.location == 'currentLocation':
        location = currentLocation

    else:
        location = opt.location
        os.chdir(location)
    print 'In %s' %location
    os.system("du -lh > check.txt")
    location = location + '/check.txt'
    lines = open(location, "r").readlines()
   
    for iLine in range(len(lines)):
        current_line = lines[iLine]
        if current_line[0:3] in checks:
            os.system("rm %s/user_code.tgz" %current_line[4:67])
        
    os.system("rm check.txt")

if __name__ == "__main__":
    opt = opts()
    checkJobs(opt)
