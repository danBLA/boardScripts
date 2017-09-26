import math
import os
import sys
import Solid
import Domain
import Snappy
import Simple
import force

import help_functions as hf

class Project(object):
   def __init__(self,logger):
       self._solid            = None
       self._refsolid         = None
       self._edgesolid        = None
       self._solidfile        = ""
       self._refsolidfile     = ""
       self._edgesolidfile    = ""
       self._projectdir       = ""
       self._projectname      = ""
       self._snappyHexMeshDir = ""
       self._simpleFoamDir    = ""
       self._scale            = 1.0
       self._rotX             = 0.0
       self._rotY             = 0.0
       self._rotZ             = 0.0
       self._speedknots       = 0.0
       self._snappy           = None
       self._domain           = None
       self._simple           = None
       self._logger           = logger

   def prepare(self):
       # create project directory name
       self.createProjectName()

       # create snappy and domain object
       self._snappy = Snappy.Snappy(self._snappyHexMeshDir,self._logger)
       self._domain = Domain.Domain(self._snappyHexMeshDir,self._logger)
       self._simple = Simple.Simple(self._simpleFoamDir,self._snappyHexMeshDir,self._logger)

       # read/load solid
       if self._snappy.solidWritten() and not self._solidfile:
           self._logger.info("Loading Solid from snappyHexMesh")
           [self._solid, self._refsolid] = self._snappy.loadSolid()
       else:
           # check if solid file exists
           self.checkSolidFile(self._solidfile)
           self._solid = Solid.createSolidFromSTL(self._solidfile)

           self.checkSolidFile(self._refsolidfile)
           self._refsolid = Solid.createSolidFromSTL(self._refsolidfile)

           if self._edgesolidfile:
              self.checkSolidFile(self._edgesolidfile)
              self._edgesolid = Solid.createSolidFromSTL(self._edgesolidfile)

       # assign solid to snappy/domain-object
       self._snappy.setsolid(self._solid)
       self._snappy.setRefsolid(self._refsolid)
       self._snappy.setEdgesolid(self._edgesolid)
       self._domain.setsolid(self._solid)

       self._simple.setVelocityKnots(self._speedknots)

   def create(self):   
       print self._solid
       self.checkObjects() 
       print self._solid

       # create all folder for the setup
       self.createFolders()
       print self._solid

       # write all solids and dictionaries
       self.writeAllFiles()
       print self._solid

   def createGrid(self):
       if not self._domain.meshCreated():
           self._domain.blockMesh()
       if not self._snappy.featuresExtracted():
           self._snappy.extractSurfaceFeatures()
       if not self._snappy.meshCreated():
           self._snappy.snappyHexMesh()

   def checkGrid(self):
       if not self._snappy.meshChecked():
           self._snappy.checkSnappyHexMesh()

   def copyMesh(self):
       if not self._snappy.meshChecked():
           print("Warning:")
           print("Copy mesh without check")
       self._simple.copyMesh()

   def writeAllFiles(self):   
       self.checkFolders()

       # transform solid
       if not self._snappy.solidWritten():
           self.transformSolid(self._solid)
           self.transformSolid(self._refsolid)
           if self._edgesolid:
              self.transformSolid(self._edgesolid)
           self._snappy.writeSolid()

       # set solid again so that the domain is
       # adjusted which is needed if there has
       # been any solid tranfsormation for
       # if the solid has been loaded
       self._domain.setsolid(self._solid)

       self._domain.writeBlockDict()
       self._snappy.writeExtractFeatureDict()
       self._snappy.writeSnappyHexMeshDict()

       self._snappy.copytemplateDict("controlDict")
       self._snappy.copytemplateDict("fvSchemes")
       self._snappy.copytemplateDict("fvSolution")
       self._snappy.copytemplateDict("transportProperties","constant")
       self._snappy.copytemplateDict("turbulenceProperties","constant")

       self._simple.writeInitialAndBCinclude()
       self._simple.copytemplateDict("controlDict")
       self._simple.copytemplateDict("fvSchemes")
       self._simple.copytemplateDict("fvSolution")
       self._simple.copytemplateDict("transportProperties","constant")
       self._simple.copytemplateDict("turbulenceProperties","constant")

   def checkFolders(self):
       self.checkObjects()

       if not self._projectdir:
           print("ERROR: Project->checkFolders")
           print("       project-directory not assigned yet")
           print("       call \"createProjectName\" first...")
           hf.flush_output()
           hf.exit(1)

       if not self._snappy.foldersExist():
           print("ERROR: Project->checkFolders")
           print("       snappy folders not yet created!")
           hf.flush_output()
           hf.exit(1)

       if not self._domain.foldersExist():
           print("ERROR: Project->checkFolders")
           print("       domain folders not yet created!")
           hf.flush_output()
           hf.exit(1)

   def checkObjects(self):
       if not self._projectdir:
           print("ERROR: Project->createFolders")
           print("       project-directory not assigned yet")
           print("       call \"createProjectName\" first...")
           hf.flush_output()
           hf.exit(1)
       if not self._snappy:
           print("ERROR: Project->createFolders")
           print("       snappy object not allocated!")
           hf.flush_output()
           hf.exit(1)
       if not self._domain:
           print("ERROR: Project->createFolders")
           print("       snappy object not allocated!")
           hf.flush_output()
           hf.exit(1)

   def createFolders(self):
       hf.create_folder(self._projectdir)
       self._snappy.createFolders()
       self._domain.createFolders()
       self._simple.createFolders()

   def createProjectName(self):
       self.checkSolidFile(self._solidfile)


       self._projectname = os.path.splitext(self._solidfile)[0]
       self._projectname = os.path.join(self._projectname,str(abs(self._speedknots))+"knots")
       self._projectname = os.path.join(self._projectname, "X"+str(self._rotX)
                                                         +".Y"+str(self._rotY)
                                                         +".Z"+str(self._rotZ))

       self._projectdir = os.path.join("simulations",self._projectname)

       self._snappyHexMeshDir = os.path.join(self._projectdir,"snappyHexMesh")
       self._simpleFoamDir    = os.path.join(self._projectdir,"simpleFoam")

   def writeMainDicts(self,directory="."):
       self._writeMainDict("controlDict",directory)
       self._writeMainDict("fvSchemes",directory)
       self._writeMainDict("fvSolution",directory)
       self._writeMainDict("fvSolution",directory)

   def writeMainDict(self,filename,directory="."):
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]

        template = os.path.join(*[sourcedir,"..","templates",filename])
        target   = os.path.join(targetDir,filename)

        hf.copyfile(template,target)

   def checkSolidFile(self,filename):
       if not filename:
           print("ERROR: solid filename not defined!")
           print("       given name -> "+filename)
           sys.exit(1)
       if not os.path.isfile(os.path.join("geometries",filename)):
           print("ERROR: solid file not found in geometries!")
           print("       given name -> "+filename)
           sys.exit(1)

   def transformSolid(self,solid):   

      if not self._scale == 1.0:
          solid.scale(self._scale)

      if not self._rotX == 0.0:
          solid.rotate(self._rotX,"X")

      if not self._rotY == 0.0:
          solid.rotate(self._rotY,"Y")

      if not self._rotZ == 0.0:
          solid.rotate(self._rotZ,"Z")

      solid.repair()

   def setSolidFile(self,filename):
       self._solidfile = filename

   def setRefSolidFile(self,filename):
       self._refsolidfile = filename

   def setEdgeSolidFile(self,filename):
       self._edgesolidfile = filename

   def setObjeScaling(self,scale):
       self._scale = scale

   def setObjeRotX(self,rotX):
       self._rotX = rotX

   def setObjeRotY(self,rotY):
       self._rotY = rotY

   def setObjeRotZ(self,rotZ):
       self._rotZ = rotZ

   def setFluidVelInKnots(self,speed):
       self._speedknots = speed

   def statusShort(self):
       string = "empty"
       string = self._domain.laststep(string)
       string = self._snappy.laststep(string)
       string = self._simple.laststep(string)
       string  =(   "Project: "+self._projectname
                +" -> last step: "+string
                +" -> ready2run: "+str(self._simple.meshCopied()))
       return string
   def statusInfo(self):
       string  =   "Project: "+self._projectname+"\n"
       #if self._solidfile:
           #string += "Solid File:"+self._solidfile+"\n"
       if self._domain:
           string += self._domain.statusInfo()
       if self._snappy:
           string += self._snappy.statusInfo()
       if self._simple:
           string += self._simple.statusInfo()
       return string

   def __str__(self):
       return self.statusInfo()

   def __eq__(self,other):
       if (     self._solidfile     == other._solidfile
           and  self._refsolidfile  == other._refsolidfile
           and  self._edgesolidfile == other._edgesolidfile
           and  self._scale         == other._scale
           and  self._rotX          == other._rotX
           and  self._rotY          == other._rotY
           and  self._rotZ          == other._rotZ
           and  self._speedknots    == other._speedknots):
           return True
       else:
           return False
   def __ne__(self,other):
       return (not self.__eq__(other))

   def runSolver(self):
       self._simple.runSimulation()

   def forces(self,outerLogFile):
       header = []
       header.append("SolidFile: "+self._solidfile)
       header.append("X: "+str(self._rotX)+", Y: "+str(self._rotY)+", Z: "+str(self._rotZ))

       forcesFile = os.path.join(*[self._simpleFoamDir,"postProcessing","forces","0","forces.dat"])
       force.printAndLogForce(forcesFile, header, self._logger, outerLogFile)
