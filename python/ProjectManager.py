import Project
import help_functions as hf
class ProjectManager(object):
    def __init__(self):
        self._configurations = []
        self._geometries = []
        self._selected_geometries = []
        self._selected_configurations = []
        self._projectlist = []
        self._active_projectlist = []

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

    def run(self):
        print("===============================")
        print("= Project configuration       =")
        print("===============================")
        print("")
        print("Geometries loaded:")
        if self._selected_geometries:
           for item in self._selected_geometries:
              print("* "+str(item))
        else:
           print("* none")
        print("Configurations loaded:")
        if self._selected_configurations:
           for item in self._selected_configurations:
              print("* "+str(item))
        else:
           print("* none")

        print("")
        questionair = {}
        print("1: load geometry")
        questionair["1"] = self.loadGeometry
        print("2: remove geometry")
        questionair["2"] = self.removeGeometry
        print("3: load configuration")
        questionair["3"] = self.loadConfiguration
        print("4: remove configuration")
        questionair["4"] = self.removeConfiguration
        print("5: create projects")
        questionair["5"] = self.createProjects
        print("x: exit")
        questionair["x"] = self.exit

        userchoice = self.query_project("Please select: ",questionair)
        userchoice()

    def exit(self):
        hf.exit(0)
    def pleasedefine(self):
        print("please define this function...")
        self.run()

    def loadGeometry(self):
        if len(self._geometries) == len(self._selected_geometries):
           print("All possible geometries are already loaded...")
           self.run()
        print("Geometries:")

        print("")
        questionair = {}

        j=-1
        for i in xrange(len(self._geometries)):
           if not self._geometries[i] in self._selected_geometries:
              j += 1
              print(str(j)+": "+str(self._geometries[i]))
              questionair[str(j)] = i
           else:
              print("*"   +": "+str(self._geometries[i]))

        print("")
        print("a: all")
        questionair["a"] = -1
        print("b: back")
        questionair["b"] = -2
        userchoice = self.query_project("Please select: ",questionair)
        if userchoice == -1:
           for i in xrange(len(self._geometries)):
              if not self._geometries[i] in self._selected_geometries:
                 self._selected_geometries.append(self._geometries[i])
           self.run()
        if userchoice == -2:
           self.run()
        else:
           self._selected_geometries.append(self._geometries[userchoice])
           self.loadGeometry()

    def removeGeometry(self):
        if len(self._selected_geometries) < 1:
           print("No geometry is currently loaded...")
           self.run()
        print("Geometries:")

        print("")
        questionair = {}

        j=-1
        for i in xrange(len(self._geometries)):
           if self._geometries[i] in self._selected_geometries:
              j += 1
              print(str(j)+": "+str(self._geometries[i]))
              questionair[str(j)] = i
           else:
              print("*"   +": "+str(self._geometries[i]))

        print("")
        print("a: all")
        questionair["a"] = -1
        print("b: back")
        questionair["b"] = -2
        userchoice = self.query_project("Please select: ",questionair)
        if userchoice == -1:
           self._selected_geometries = []
           self.run()
        if userchoice == -2:
           self.run()
        else:
           self._selected_geometries.remove(self._geometries[userchoice])
           self.removeGeometry()

    def loadConfiguration(self):
        if len(self._configurations) == len(self._selected_configurations):
           print("All possible configurations are already loaded...")
           self.run()
        print("Configurations:")

        print("")
        questionair = {}

        j=-1
        for i in xrange(len(self._configurations)):
           if not self._configurations[i] in self._selected_configurations:
              j += 1
              print(str(j)+": "+str(self._configurations[i]))
              questionair[str(j)] = i
           else:
              print("*"   +": "+str(self._configurations[i]))

        print("")
        print("a: all")
        questionair["a"] = -1
        print("b: back")
        questionair["b"] = -2
        userchoice = self.query_project("Please select: ",questionair)
        if userchoice == -1:
           for i in xrange(len(self._configurations)):
              if not self._configurations[i] in self._selected_configurations:
                 self._selected_configurations.append(self._configurations[i])
           self.run()
        if userchoice == -2:
           self.run()
        else:
           self._selected_configurations.append(self._configurations[userchoice])
           self.loadConfiguration()

    def removeConfiguration(self):
        if len(self._selected_configurations) < 1:
           print("No configuration is currently loaded...")
           self.run()
        print("Configurations:")

        print("")
        questionair = {}

        j=-1
        for i in xrange(len(self._configurations)):
           if self._configurations[i] in self._selected_configurations:
              j += 1
              print(str(j)+": "+str(self._configurations[i]))
              questionair[str(j)] = i
           else:
              print("*"   +": "+str(self._configurations[i]))

        print("")
        print("a: all")
        questionair["a"] = -1
        print("b: back")
        questionair["b"] = -2
        userchoice = self.query_project("Please select: ",questionair)
        if userchoice == -1:
           self._selected_configurations = []
           self.run()
        if userchoice == -2:
           self.run()
        else:
           self._selected_configurations.remove(self._configurations[userchoice])
           self.removeConfigurations()

    def createProjects(self):
       for sCFG in self._selected_configurations:
           for gCFG in self._selected_geometries:
               project = Project.Project()

               project.setSolidFile(gCFG.getGeometrySTL())
               project.setRefSolidFile(gCFG.getRefGeometrySTL())
               project.setEdgeSolidFile(gCFG.getEdgeGeometrySTL())
               project.setObjeScaling(gCFG.getScale())
               project.setObjeRotX(sCFG.getXrotation())
               project.setObjeRotY(sCFG.getYrotation())
               project.setObjeRotZ(sCFG.getZrotation())
               project.setFluidVelInKnots(sCFG.getSpeed())

               if not project in self._projectlist:
                  project.prepare()
                  self._projectlist.append(project)
                  self._active_projectlist.append(project)

       #self.selectProjectToRun()
       self.baseProjectPage()

    def baseProjectPage(self):
        print("=============")
        print("= Projects  =")
        print("=============\n")

        questionair = {}
        print("Active Projects:")
        j = -1
        for i in range(len(self._projectlist)):
            if self._projectlist[i] in self._active_projectlist:
               j += 1
               print("("+str(j)+") "+self._projectlist[i].statusShort())
               questionair[str(j)] = i

        print("\nInctive Projects:")
        for i in range(len(self._projectlist)):
            if self._projectlist[i] not in self._active_projectlist:
               j += 1
               print("("+str(j)+") "+self._projectlist[i].statusShort())
               questionair[str(j)] = i

        print("\na: prepare all active projects")
        questionair["a"] = -1
        print("c: prepare all active projects without grid check")
        questionair["c"] = -4
        print("b: back")
        questionair["b"] = -3
        print("x: to exit")
        questionair["x"] = -2
        userchoice = self.query_project("Select project to switch active/inactive or a/c/b/x: ",questionair)

        if userchoice == -3:
            self.run()
        elif userchoice == -2:
            hf.exit(0)
        elif userchoice == -1:
            for i in range(len(self._active_projectlist)):
                self._active_projectlist[i].create()
                self._active_projectlist[i].createGrid()
            for i in range(len(self._active_projectlist)):
                self._active_projectlist[i].checkGrid()
            for i in range(len(self._active_projectlist)):
                self._active_projectlist[i].copyMesh()
        elif userchoice == -4:
            for i in range(len(self._active_projectlist)):
                self._active_projectlist[i].create()
                self._active_projectlist[i].createGrid()
            for i in range(len(self._active_projectlist)):
                self._active_projectlist[i].copyMesh()
        else:
            if self._projectlist[userchoice] in self._active_projectlist:
               self._active_projectlist.remove(self._projectlist[userchoice])
            else:
               self._active_projectlist.append(self._projectlist[userchoice])
        self.baseProjectPage()

    def selectProjectToRun(self,withGridCheck=True):
        if withGridCheck:
           print("===============================")
           print("= Select a project to prepare =")
           print("===============================\n")
        else:
           print("==================================================")
           print("= Select a project to prepare without grid check =")
           print("==================================================\n")

        questionair = {}
        for i in range(len(self._projectlist)):
            print("("+str(i)+") "+self._projectlist[i].statusShort())
            questionair[str(i)] = i

        print("a: to prepare all projects")
        questionair["a"] = -1
        print("b: back")
        questionair["b"] = -3
        print("x: to exit")
        questionair["x"] = -2
        userchoice = self.query_project("Please select: ",questionair)

        if userchoice == -3:
            self.run()
        elif userchoice == -2:
            hf.exit(0)
        elif userchoice == -1:
            for i in range(len(self._projectlist)):
                self._projectlist[i].create()
                self._projectlist[i].createGrid()
            if withGridCheck:
               for i in range(len(self._projectlist)):
                   self._projectlist[i].checkGrid()
            for i in range(len(self._projectlist)):
                self._projectlist[i].copyMesh()
        else:
            self._projectlist[userchoice].create()
            self._projectlist[userchoice].createGrid()
            if withGridCheck:
               self._projectlist[userchoice].checkGrid()
            self._projectlist[userchoice].copyMesh()

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
    def __str__(self):
        string  =      str(self._speed    )+" kns"
        string += ", "+str(self._Xrotation)+" Xrot"
        string += ", "+str(self._Yrotation)+" Yrot"
        string += ", "+str(self._Zrotation)+" Zrot"
        return string
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
      else:
         print("no velocity section found")
      if config.has_section('ROTATION'):    
         self._Xrotation = float(hf.read_key(config,'ROTATION','Xrotation',0.0))
         self._Yrotation = float(hf.read_key(config,'ROTATION','Yrotation',0.0))
         self._Zrotation = float(hf.read_key(config,'ROTATION','Zrotation',0.0))
      else:
         print("no rotation section found")


class geomCFG(object):
    def __init__(self,directory,cfgfile):
        import os
        self._geometrySTL = ""
        self._refGeometrySTL = ""
        self._edgeGeometrySTL = ""
        self._scale = 1.0
        self.readCFG(os.path.join(directory,cfgfile))
    def __str__(self):
        string  =  str(self._scale)+" scale"
        string += ", "+self._geometrySTL
        string += ", "+self._refGeometrySTL
        if self._edgeGeometrySTL:
            string += ", "+self._edgeGeometrySTL
        return string
    def getGeometrySTL(self):
        return self._geometrySTL
    def getRefGeometrySTL(self):
        return self._refGeometrySTL
    def getEdgeGeometrySTL(self):
        return self._edgeGeometrySTL
    def getScale(self):
        return self._scale
    def __eq__(self,other):
        if (     self._geometrySTL     == other.getGeometrySTL()
             and self._refGeometrySTL  == other.getRefGeometrySTL()
             and self._edgeGeometrySTL == other.getEdteGeometrySTL()
             and self._scale           == other.getScale()):
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
         self._edgeGeometrySTL = hf.read_key(config,'GEOMETRY','edgesolid',"",True)
      else:
         print("no geometry section found")

