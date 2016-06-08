import os,socket,configuration

def site() :
    d = {"hep.ph.ic.ac.uk":"ic",
         "sesame1":"pu",
         "brown.edu":"bn",
         "cern.ch":"cern",
         "fnal.gov":"fnal",
         "wisc.edu":"uw",
         }
    hostName = socket.getfqdn()
    for match,prefix in d.iteritems() :
        if match in hostName : return prefix
    return "default"

def prefix() :
    tokens = filter(None, [site(), configuration.experiment()])
    return '_'.join(tokens)

def specs() :
    user = os.environ["USER"]
    return {
        "default" :{"localOutputDir" : "/tmp/%s"%user,
                    "globalOutputDir": "/tmp/%s"%user,
                    "dCachePrefix":"",
                    "dCacheTrim":"",
                    "srmPrefix":"",
                    "eosPrefix":"",
                    "lsPrefix":"",
                    "queueHeaders":[],
                    "queueVars":{},
                    "moveOutputFilesBatch": True,
                    "tarCommand"   : "",
                    "extractCommand" : "",
                    "workingDir": os.environ["PWD"],
            },
        "ic_cms"  :{"localOutputDir" : "/vols/cms04/%s/tmp/"%user,
                    "globalOutputDir": "/vols/cms04/%s/tmp/"%user,
                    "dCachePrefix"   : "root://xrootd.grid.hep.ph.ic.ac.uk//",
                    "dCacheTrim"     : "/pnfs/hep.ph.ic.ac.uk/data/cms",
                    "srmPrefix"      : "srm://gfe02.grid.hep.ph.ic.ac.uk:8443/srm/managerv2?SFN=/pnfs/hep.ph.ic.ac.uk/data/cms/store/user",
                    "queueHeaders"   : ["job-ID", "prior", "name", "user", "state", "submit1", "submit2", "queue", "slots", "ja-task-ID"],
                    "queueVars"      : {"queue":"queue", "user":"user", "state":"state", "run":"r", "userBlackList":["user"],
                                        "summary":"qstat -u '*'", "sample":"qstat | head"},
                    },
        "pu_cms"  :{"localOutputDir" : "/tmp/%s"%user,
                    "globalOutputDir": "/tigress-hsm/%s/tmp/"%user,
                    "queueHeaders"   : ["Job id","Name","User","Time Use","S","Queue"],
                    "queueVars"      : {"queueName":"hep", "queue": "Queue", "user":"User", "state":"S", "run":"R", "summary":"qstat", "sample": "qstat -u %s | head"%user},
                    },
        "bn_cms": {"localOutputDir" : os.environ["_CONDOR_SCRATCH_DIR"] if "_CONDOR_SCRATCH_DIR" in os.environ else "/tmp/%s" % user,
                   "globalOutputDir": "/user_data/%s/supy-output/" % os.environ["USER"],
                   "moveOutputFilesBatch": False,
                   "queueHeaders"   : ["ID", "OWNER", "SUBMITTED1", "SUBMITTED2", "RUN_TIME", "ST", "PRI", "SIZE", "CMD"],
                   "queueVars"      : {"user":"OWNER", "state":"ST", "run":"R", "userBlackList":["OWNER", "jobs;"],
                                       "summary":"condor_q -global", "sample": "condor_q -global -submitter %s | head"%user},
                   "tarCommand"     : "cd ..; tar -chf %s.tar %s/; cd %s" % tuple((os.path.basename(os.environ["PWD"]),)*3),
                   "extractCommand" : "tar -xf %s.tar" % os.path.basename(os.environ["PWD"]),
                   "workingDir"     : "${_CONDOR_JOB_IWD}/" + os.path.basename(os.environ["PWD"]),
                    },
        "cern_atlas":{"localOutputDir" : "/tmp/%s"%user,
                      "globalOutputDir": "/afs/cern.ch/work/%s/%s/tmp/"%(user[0],user),
                      "eos"            : "/afs/cern.ch/project/eos/installation/0.1.0-22d/bin/eos.select", #See https://twiki.cern.ch/twiki/bin/view/EOS.
                      "eosPrefix"      : "root://eosatlas.cern.ch/",
                      "queueHeaders"   : ["JOBID", "USER", "STAT", "QUEUE", "FROM_HOST", "EXEC_HOST", "JOB_NAME", "SUBMIT_TIME"],
                      "queueVars"      : {"queueName":"8nh", "queue":"QUEUE", "user":"USER", "state":"STAT", "run":"RUN", "summary":"bjobs -u all", "sample": "bjobs | head"},
                      },
        "cern_cms":{"localOutputDir" : "/tmp/%s"%user,
                    "globalOutputDir": "/afs/cern.ch/work/%s/%s/tmp/"%(user[0],user),
                    "eos"            : "/afs/cern.ch/project/eos/installation/0.2.31/bin/eos.select",
                    "eosPrefix"      : "root://eoscms.cern.ch/",
                    "queueHeaders"   : ["JOBID", "USER", "STAT", "QUEUE", "FROM_HOST", "EXEC_HOST", "JOB_NAME", "SUBMIT_TIME"],
                    "queueVars"      : {"queueName":"8nh", "queue":"QUEUE", "user":"USER", "state":"STAT", "run":"RUN", "summary":"bjobs -u all", "sample": "bjobs | head"},
                    },
        "fnal_cms":{"localOutputDir" : os.environ["_CONDOR_SCRATCH_DIR"] if "_CONDOR_SCRATCH_DIR" in os.environ else "/tmp/%s"%user,
                    "globalOutputDir": "/uscms_data/d3/%s/supy-output/"%os.environ["USER"],
                    "moveOutputFilesBatch": False,
                    "dCacheTrim"     : "/pnfs/cms/WAX/",
                    "dCachePrefix"   : "dcap://cmsgridftp.fnal.gov:24125/pnfs/fnal.gov/usr/cms/WAX/",
                    #"globalOutputDir":"/pnfs/cms/WAX/resilient/%s/tmp/"%user,
                    #"srmPrefix"      : "srm://cmssrm.fnal.gov:8443/pnfs/cms/WAX/11/store/user/lpcsusyra1",
                    "lsPrefix"       : "/pnfs/cms/WAX/11/store/user/lpcsusyra1/",
                    "queueHeaders"   : ["ID", "OWNER", "SUBMITTED1", "SUBMITTED2", "RUN_TIME", "ST", "PRI", "SIZE", "CMD"],
                    "queueVars"      : {"user":"OWNER", "state":"ST", "run":"R", "userBlackList":["OWNER", "jobs;"],
                                        "summary":"condor_q -global", "sample": "condor_q -global -submitter %s | head"%user},
                    "tarCommand"     : "cd ..; tar -chf %s.tar %s/; cd %s" % tuple((os.path.basename(os.environ["PWD"]),)*3),
                    "extractCommand" : "tar -xf %s.tar" % os.path.basename(os.environ["PWD"]),
                    "workingDir"     : "${_CONDOR_JOB_IWD}/"+os.path.basename(os.environ["PWD"]),
                    },
        "uw_cms": {"localOutputDir" : os.environ["_CONDOR_SCRATCH_DIR"] if "_CONDOR_SCRATCH_DIR" in os.environ else "/nfs_scratch/%s/supy-tmp/" % user,
                   "globalOutputDir": "/nfs_scratch/%s/supy-output/" % os.environ["USER"],
                   "moveOutputFilesBatch": False,
                   "queueHeaders"   : ["ID", "OWNER", "SUBMITTED1", "SUBMITTED2", "RUN_TIME", "ST", "PRI", "SIZE", "CMD"],
                   "queueVars"      : {"user":"OWNER", "state":"ST", "run":"R", "userBlackList":["OWNER", "jobs;"],
                                       "summary":"condor_q -global", "sample": "condor_q -global -submitter %s | head"%user},
                   "tarCommand"     : "cd ..; tar -chf %s.tar %s/; cd %s" % tuple((os.path.basename(os.environ["PWD"]),)*3),
                   "extractCommand" : "tar -xf %s.tar" % os.path.basename(os.environ["PWD"]),
                   "workingDir"     : "${_CONDOR_JOB_IWD}/" + os.path.basename(os.environ["PWD"]),
                    },

        }

def info(site = prefix(), key = None) :
    ss = specs()
    dct = ss["default"]
    if site in ss :
        dct.update(ss[site])
    return dct[key]

def lumiEnvScript() :
    return "sites/%sLumi.sh"%prefix()

def srmFunc() :
    return 'utils.fileListFromSrmLs(dCachePrefix = "%s", dCacheTrim = "%s", location="%s'%(info(key = "dCachePrefix"),
                                                                                           info(key = "dCacheTrim"),
                                                                                           info(key = "srmPrefix"))

def eos() :
    return 'utils.fileListFromEos(eos = "%s", xrootdRedirector = "%s", location="'%(info(key = "eos"), info(key = "eosPrefix"))

def pnfs() :
    return 'utils.fileListFromPnfs(lsPrefix = "%s", dCachePrefix = "%s", dCacheTrim = "%s", location="'%(info(key = "lsPrefix"),
                                                                                                         info(key = "dCachePrefix"),
                                                                                                         info(key = "dCacheTrim"))

# FIXME: adapt susycaf and remove this
if "susycaf" in os.environ["PWD"]:
    srm = srmFunc()