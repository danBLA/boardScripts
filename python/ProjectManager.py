import Project
import help_functions as hf
class ProjectManager(object):
    def __init__(self):
        self._configurations = []
        self._geometries = []
        self._projectlist = []

    def searchCFGfiles(self,directory):
        from os import listdir
        from os.path import isfile, join, splitext
        onlyfiles = [ f for f in listdir(directory) if isfile(join(directory,f)) ]
        cfgfiles=[]
        for f in onlyfiles:
            try:
                ext = splitext(f)[-1]
            except:
                ext = ""
            if "cfg" in ext:
                cfgfiles.append(f)
        return cfgfiles

    def prepare(self):
        import os
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]
        maindir = os.path.join(sourcedir,"..")

        simCFGs  = self.searchCFGfiles(maindir)
        for item in simCFGs:
            sCFG = simCFG(maindir,item)
            if not sCFG in self._configurations:
                self._configurations.append(sCFG)
        print("Simulation configurations found: "+str(len(self._configurations)))

        geomCFGs = self.searchCFGfiles(os.path.join(maindir,"geometries"))
        for item in geomCFGs:
            gCFG = geomCFG(os.path.join(maindir,"geometries"),item)
            if not gCFG in self._geometries:
                self._geometries.append(gCFG)
        print("Geometry configurations found: "+str(len(self._geometries)))

    def createProjects(self):
       for sCFG in self._configurations:
           for gCFG in self._geometries:
               project = Project.Project()

               project.setSolidFile(gCFG.getGeometrySTL())
               project.setRefSolidFile(gCFG.getRefGeometrySTL())
               project.setObjeScaling(gCFG.getScale())
               project.setObjeRotX(sCFG.getXrotation())
               project.setObjeRotY(sCFG.getYrotation())
               project.setObjeRotZ(sCFG.getZrotation())
               project.setFluidVelInKnots(sCFG.getSpeed())

               project.prepare()
               self._projectlist.append(project)

    def selectProjectToRun(self):
        print("===============================")
        print("= Select a project to prepare =")
        print("===============================")

        questionair = {}
        for i in range(len(self._projectlist)):
            #print("-------")
            #print("-- "+str(i)+" --")
            #print("-------")
            #print self._projectlist[i]
            print("("+str(i)+") "+self._projectlist[i].statusShort())
            questionair[str(i)] = i

        print("(a) to prepare all projects\n")
        questionair["a"] = -1
        print("(x) to exit\n")
        questionair["x"] = -2
        userchoice = self.query_project("Please select project number of 'a' or 'x': ",questionair)

        if userchoice == -2:
            hf.exit(0)
        elif userchoice == -1:
            for i in range(len(self._projectlist)):
                self._projectlist[i].create()
                self._projectlist[i].createGrid()
            for i in range(len(self._projectlist)):
                self._projectlist[i].checkGrid()
            for i in range(len(self._projectlist)):
                self._projectlist[i].copyMesh()
        else:
            self._projectlist[i].create()
            self._projectlist[i].createGrid()
            self._projectlist[i].checkGrid()
            self._projectlist[i].copyMesh()

        self.selectProjectToRun()

    def query_project(self,question,valid):
        import sys

        while True:
            sys.stdout.write(question)
            choice = raw_input().lower()
            if choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please select one of the choices given above...\n")
                #sys.stdout.write("Please respond with 'yes' or 'no' "\
                #                 "(or 'y' or 'n').\n")
   

class simCFG(object):
    def __init__(self,directory,cfgfile):
        import os
        self._speed     = 0.0
        self._Xrotation = 0.0
        self._Yrotation = 0.0
        self._Zrotation = 0.0
        self.readCFG(os.path.join(directory,cfgfile))
    def getSpeed(self):
        return self._speed
    def getXrotation(self):
        return self._Xrotation
    def getYrotation(self):
        return self._Yrotation
    def getZrotation(self):
        return self._Zrotation
    def __eq__(self,other):
        if (     self._speed     == other.getSpeed()
            and  self._Xrotation == other.getXrotation()
            and  self._Yrotation == other.getYrotation()
            and  self._Zrotation == other.getZrotation()):
            return True
        else:
            return False
    def __ne__(self,other):
        return (not self.__eq__(other))
    def readCFG(self,filename):
      import ConfigParser
      try:
          config = ConfigParser.SafeConfigParser()
      except:
          config = ConfigParser.RawConfigParser()

      config.read(filename)
      if config.has_section('VELOCITY'):    
         self._speed = float(hf.read_key(config,'VELOCITY','speed',0.0))
      if config.has_section('ROTATION'):    
         self._Xrotation = float(hf.read_key(config,'ROTATION','Xrotation',0.0))
         self._Yrotation = float(hf.read_key(config,'ROTATION','Yrotation',0.0))
         self._Zrotation = float(hf.read_key(config,'ROTATION','Zrotation',0.0))


class geomCFG(object):
    def __init__(self,directory,cfgfile):
        import os
        self._geometrySTL = ""
        self._refGeometrySTL = ""
        self._scale = 1.0
        self.readCFG(os.path.join(directory,cfgfile))
    def getGeometrySTL(self):
        return self._geometrySTL
    def getRefGeometrySTL(self):
        return self._refGeometrySTL
    def getScale(self):
        return self._scale
    def __eq__(self,other):
        if (     self._geometrySTL    == other.getGeometrySTL()
             and self._refGeometrySTL == other.getRefGeometrySTL()
             and self._scale          == other.getScale()):
            return True
        else:
            return False
    def __ne__(self,other):
        return (not self.__eq__(other))
    def readCFG(self,filename):
      import ConfigParser
      cfgfile = open(filename, 'r')
      try:
          config = ConfigParser.SafeConfigParser()
      except:
          config = ConfigParser.RawConfigParser()

      config.read(filename)
      if config.has_section('GEOMETRY'):    
         self._scale = float(hf.read_key(config,'GEOMETRY','scale',1.0))
         self._geometrySTL = hf.read_key(config,'GEOMETRY','solid',"")
         self._refGeometrySTL = hf.read_key(config,'GEOMETRY','refsolid',"")
         print("geometry section found")
      else:
         print("no geometry section found")

