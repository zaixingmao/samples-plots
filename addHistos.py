#!/usr/bin/env python

from plots_cfg import sampleList
import os

def go(FS):
    for iSample, iLocation, iCat in sampleList:
        if iSample == 'ZL' or iSample == 'ZJ':
            continue
        command = 'hadd %s_%s.root %s*' %(iLocation[iLocation.rfind('/')+1: iLocation.rfind('_all')], FS, iLocation[iLocation.rfind('/')+1: iLocation.rfind('_all')])
        os.system(command)


go('em')
