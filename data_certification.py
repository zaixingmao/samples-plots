# from https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/

__fileName = "Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt"
__certDict = eval(open(__fileName).readline())


def passes(tree, isData):
    if not isData:
        return True

    ranges = __certDict.get(str(tree.RUN))
    if not ranges:
        return False

    for (minSection, maxSection) in ranges:
        if minSection <= tree.LUMI <= maxSection:
            return True

    return False


def __test():
    class vessel(object):
        pass

    tree = vessel()
    assert passes(tree, False)

    tree.RUN = 1234567890
    assert not passes(tree, True)

    #  "190705": [[1, 5], [7, 65], [81, 336], [338, 350], [353, 383]],
    tree.RUN = 190705
    tree.LUMI = 2
    assert passes(tree, True)

    tree.LUMI = 6
    assert not passes(tree, True)

    tree.LUMI = 350
    assert passes(tree, True)


if __name__ == "__main__":
    # print __certDict
    __test()
