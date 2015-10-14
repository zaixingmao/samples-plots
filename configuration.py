from supy.defaults import *
import supy


def useCachedFileLists():
    return False

def leavesToBlackList():
    return ["weight"]

def experiment():
    return "cms"

def hadd():
    return ["hadd", "phaddy"][0]
