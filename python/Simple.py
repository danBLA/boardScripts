import Solid
import os
import help_functions as hf
class Simple(object):
    def __init__(self,simpledir,snappydir):
        self._solid = None

        self._snappydir     = snappydir
        self._simpledir     = simpledir
        self._constantdir   = os.path.join(simpledir,"constant")
        self._systemdir     = os.path.join(simpledir,"system")
        self._velocity      = 0.0
        self._folderlist = []
        self._folderlist.append(self._snappydir)
        self._folderlist.append(self._simpledir)
        self._folderlist.append(self._constantdir)
        self._folderlist.append(self._systemdir)

        self._statusfilename = os.path.join(self._simpledir,"simple.cfg")
        self._gridCopied        = False
        self._simulationStarted = False
        self._simulationFinished= False

        if self.statusFileExists():
            self.readStatus()

    def setVelocityKnots(self,knots):
        self._velocity = 0.514444444*knots

    def readStatus(self):
      import ConfigParser
      try:
          config = ConfigParser.SafeConfigParser()
      except:
          config = ConfigParser.RawConfigParser()

      config.read(self._statusfilename)

      if config.has_section('SIMPLE'):    
         self._gridCopied        = hf.convert_string_logical(hf.read_key(config,'SIMPLE','gridCopied',"False"),'gridCopied')
         self._simulationStarted = hf.convert_string_logical(hf.read_key(config,'SIMPLE','simulationStarted',"False"),'simulationStarted')
         self._simulationFinished= hf.convert_string_logical(hf.read_key(config,'SIMPLE','simulationFinished',"False"),'simulationFinished')
      else:
          print("WARNING: Simple -> config file found but no section SIMPLE")

    def writeStatus(self):
      import ConfigParser
      try:
          config = ConfigParser.SafeConfigParser()
      except:
          config = ConfigParser.RawConfigParser()

      config.add_section('SIMPLE')
      config.set('SIMPLE','gridCopied',        hf.convert_logical_string(self.meshCopied()))
      config.set('SIMPLE','simulationStarted', hf.convert_logical_string(self.simulationStarted()))
      config.set('SIMPLE','simulationFinished',hf.convert_logical_string(self.simulationFinished()))

      statusfile = open(self._statusfilename, 'w')
      config.write(statusfile)
      statusfile.close()

    def statusFileExists(self):
        return os.path.isfile(self._statusfilename)

    def setGridCopied(self,boolean=True):
        self._gridCopied = boolean
        self.writeStatus()

    def setSimulationStarted(self,boolean=True):
        self._simulationStarted = boolean
        self.writeStatus()

    def setSimulationFinished(self,boolean=True):
        self._simulationFinished = boolean
        self.writeStatus()

    def createFolders(self):
        for item in self._folderlist:
            hf.create_folder(item)

        if not self.statusFileExists():
            self.writeStatus()

    def foldersExist(self):
        allfoldersexist = True
        for item in self._folderlist:
            allfoldersexist = allfoldersexist and hf.folder_exists
        return allfoldersexist


    def copytemplateDict(self,dictname,targ="system"):
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]

        template = os.path.join(*[sourcedir,"..","templates",dictname])

        targetdirs = { "system"  : self._systemdir,
                       "constant": self._constantdir}

        target   = os.path.join(targetdirs[targ],dictname)

        hf.copyfile(template,target)

        if not self.statusFileExists():
            self.writeStatus()

    def writeInitialFileVelocity(self,target):
        target.write("flowVelocity         (")
        target.write(" "+str(self._velocity))
        target.write(" 0 0);\n")


    def writeInitialAndBCinclude(self):
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]

        source = os.path.join(*[sourcedir,"..","templates","0"])
        target = os.path.join(self._simpledir,"0")
        hf.copy_folder(source,target,verbose=True)

        template = os.path.join(*[sourcedir,"..","templates","initialConditions"])
        target   = os.path.join(*[self._simpledir,"0","include","initialConditions"])

        replacedict = {"{FLOWVELOCITY}"  :  self.writeInitialFileVelocity}

        hf.copyfile(template,target,replacedict)

    def copyMesh(self):
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]

        source = os.path.join(*[self._snappydir,"3","polyMesh"])
        target = os.path.join(self._constantdir,"polyMesh")
        hf.copy_folder(source,target)
        self.setGridCopied()

    def meshCopied(self):
        return self._gridCopied

    def simulationStarted(self):
        return self._simulationStarted

    def simulationFinished(self):
        return self._simulationFinished

    def statusInfo(self,string=""):
        if self.statusFileExists():
            self.readStatus()
        string += "Simple:\n"
        string += " * Mesh copied          : "+str(self.meshCopied())+"\n"
        string += " * Simulation started   : "+str(self.simulationStarted())+"\n"
        string += " * Simulation finished  : "+str(self.simulationFinished())+"\n"
        return string

    def laststep(self,string):
        if self.statusFileExists():
            self.readStatus()
        if self.meshCopied():
            string = "SimpleFoam: Mesh copied"
        if self.simulationStarted():
            string = "SimpleFoam: Simulation started"
        if self.simulationFinished():
            string = "SimpleFoam: Simulation finished"
        return string
