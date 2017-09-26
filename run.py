#!/usr/bin/python

import sys
import os
from optparse  import OptionParser
import logging

path_filename=os.path.abspath(__file__)
executablesDir = os.path.split(path_filename)[0]
sys.path.insert(0,os.path.join(executablesDir,"python"))

# user defined classes
from Project import *
from ProjectManager import *

processId = os.getpid()
logFilename = "run."+str(processId)+".log"

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

#--                    --#
# command line arguments #
#--                    --#
parser = OptionParser()
parser.add_option("-g","--geometryFile",default="",help="geometry file (*.cfg)")
parser.add_option("-c","--configurationFile",default="",help="setup config file")
parser.add_option("-l","--logging",help="logging level",default="info",choices=["debug","info","warning","error","critical"])
parser.add_option("-f","--forces_log",help="log file for forces",default="")


(options, args) = parser.parse_args()

if args:
    print("Command line argument not recognised!")
    for item in args:
        print("Argument: "+item)
        hf.flush_output()
    sys.stdout.flush()
    sys.stderr.flush()
    sys.exit(1)

loggingLevel = LEVELS.get(options.logging, logging.NOTSET)
logging.basicConfig(level=loggingLevel,filename=logFilename)

logging.info("Checking arguments")
if options.geometryFile or options.configurationFile:
    logging.info("arguments found...")
    if not options.geometryFile or not options.configurationFile:
        logging.error("either define both geometry and configuration file or none of them!")
        logging.error("your configuration file: "+options.configurationFile)
        logging.error("your geometry      file: "+options.geometryFile)
        sys.exit(1)
    if not os.path.isfile(options.geometryFile):
        logging.error("Geometry file not found!")
        logging.error("your geometry      file: "+options.geometryFile)
        sys.stdout.flush()
        sys.stderr.flush()
        sys.exit(1)
    if not os.path.isfile(options.configurationFile):
        logging.error("Configuration file not found!")
        logging.error("your configuration file: "+options.configurationFile)
        sys.stdout.flush()
        sys.stderr.flush()
        sys.exit(1)

    logging.info("configuration file: "+options.configurationFile)
    logging.info("geometry      file: "+options.geometryFile)
    logging.info("load configuration...")
    sCFG = simCFG(".",options.configurationFile)
    logging.info("load geometry...")
    gCFG = geomCFG(".",options.geometryFile)
    logging.info("new project...")
    project = Project.Project(logging)
    logging.info("   -> set solid in project")
    project.setSolidFile(gCFG.getGeometrySTL())
    logging.info("   -> set ref solid in project")
    project.setRefSolidFile(gCFG.getRefGeometrySTL())
    logging.info("   -> set edge solid in project")
    project.setEdgeSolidFile(gCFG.getEdgeGeometrySTL())
    logging.info("   -> set scaling in project")
    project.setObjeScaling(gCFG.getScale())
    logging.info("   -> set x-rotation in project")
    project.setObjeRotX(sCFG.getXrotation())
    logging.info("   -> set y-rotation in project")
    project.setObjeRotY(sCFG.getYrotation())
    logging.info("   -> set z-rotation in project")
    project.setObjeRotZ(sCFG.getZrotation())
    logging.info("   -> set velocity in project")
    project.setFluidVelInKnots(sCFG.getSpeed())
    logging.info("prepare project...")
    project.prepare()
    logging.info("create project...")
    project.create()
    logging.info("create grid...")
    project.createGrid()
    logging.info("create mesh...")
    project.copyMesh()
    logging.info("run solver")
    project.runSolver()
    logging.info("forces")
    project.forces(options.forces_log)
    logging.info("DONE")
else:
    #project = Project()
    #
    #project.setSolidFile("g6_schwert.stl")
    #project.setObjeScaling("0.001")
    #project.prepare()
    #project.create()
    #print(project)
    #project.createGrid()

    manager = ProjectManager(logging)
    manager.prepare()
    manager.run()
    #manager.selectGeometry()
    #manager.createProjects()
    #manager.selectProjectToRun()
