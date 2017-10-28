import Solid
import os
import help_functions as hf
class Snappy(object):
    def __init__(self,snappydir,logger):
        self._solid     = None
        self._refsolid  = None
        self._edgesolid = None
        self._logger    = logger

        self._snappydir     = snappydir
        self._constantdir   = os.path.join(snappydir,"constant")
        self._systemdir     = os.path.join(snappydir,"system")
        self._triSurfacedir = os.path.join(self._constantdir,"triSurface")
        self._folderlist = []
        self._folderlist.append(self._snappydir)
        self._folderlist.append(self._constantdir)
        self._folderlist.append(self._systemdir)
        self._folderlist.append(self._triSurfacedir)

        self._statusfilename = os.path.join(self._snappydir,"snappy.cfg")
        self._solidWritten      = False
        self._featuresExtracted = False
        self._meshCreated       = False
        self._meshChecked       = False

        self._pointOutsideSolid = [0.0 , 0.0 , 0.0]

        if self.statusFileExists():
            self.readStatus()

    def setPointOutsideSolid(self,point):
        self._pointOutsideSolid[0] = point[0]
        self._pointOutsideSolid[1] = point[1]
        self._pointOutsideSolid[2] = point[2]

    def readStatus(self):
      import ConfigParser
      try:
          config = ConfigParser.SafeConfigParser()
      except:
          config = ConfigParser.RawConfigParser()

      config.read(self._statusfilename)

      if config.has_section('SNAPPY'):    
         self._solidWritten      = hf.convert_string_logical(hf.read_key(config,'SNAPPY','solidWritten',"False"),'solidWritten')
         self._featuresExtracted = hf.convert_string_logical(hf.read_key(config,'SNAPPY','featuresExtracted',"False"),'reaturesExtracted')
         self._meshCreated       = hf.convert_string_logical(hf.read_key(config,'SNAPPY','meshCreated',"False"),'meshCreated')
         self._meshChecked       = hf.convert_string_logical(hf.read_key(config,'SNAPPY','meshChecked',"False"),'meshChecked')
      else:
          print("WARNING: Snappy -> config file found but no section SNAPPY")

    def writeStatus(self):
      import ConfigParser
      try:
          config = ConfigParser.SafeConfigParser()
      except:
          config = ConfigParser.RawConfigParser()

      config.add_section('SNAPPY')
      config.set('SNAPPY','solidWritten',     hf.convert_logical_string(self.solidWritten()))
      config.set('SNAPPY','featuresExtracted',hf.convert_logical_string(self.featuresExtracted()))
      config.set('SNAPPY','meshCreated',      hf.convert_logical_string(self.meshCreated()))
      config.set('SNAPPY','meshChecked',      hf.convert_logical_string(self.meshChecked()))

      statusfile = open(self._statusfilename, 'w')
      config.write(statusfile)
      statusfile.close()

    def statusFileExists(self):
        return os.path.isfile(self._statusfilename)

    def setMeshCreated(self,boolean=True):
        self._meshCreated = boolean
        self.writeStatus()

    def setMeshChecked(self,boolean=True):
        self._meshChecked = boolean
        self.writeStatus()

    def setFeatuesExtracted(self,boolean=True):
        self._featuresExtracted = boolean
        self.writeStatus()

    def setSolidWritten(self,boolean=True):
        self._solidWritten = boolean
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

    def setsolid(self,solid):
        self._solid = solid

    def setRefsolid(self,solid):
        self._refsolid = solid

    def setEdgesolid(self,solid):
        self._edgesolid = solid

    def checksolid(self,whichfunction):
        if not self._solid:
            print("ERROR: Snappy -> no solid defined!")
            print("       in "+whichfunction+"!")
            hf.flush_output()
            hf.exit(1)
        if not self._refsolid:
            print("ERROR: Snappy -> no ref solid defined!")
            print("       in "+whichfunction+"!")
            hf.flush_output()
            hf.exit(1)

    def writeSolid(self):
        import pickle
        self.checksolid("writeSolid")
        if not self.solidWritten():
            self._solid.repairAndWriteToFile(self._solid.getSTLName(),self._triSurfacedir)
            pickle.dump(self._solid,open(os.path.join(self._triSurfacedir,"surface.p"),"wb"))

            self._refsolid.repairAndWriteToFile(self._refsolid.getSTLName(),self._triSurfacedir)
            pickle.dump(self._refsolid,open(os.path.join(self._triSurfacedir,"refsurface.p"),"wb"))

            if self._edgesolid:
               self._edgesolid.repairAndWriteToFile(self._edgesolid.getSTLName(),self._triSurfacedir)
               pickle.dump(self._edgesolid,open(os.path.join(self._triSurfacedir,"edgesurface.p"),"wb"))

            self.setSolidWritten()

    def loadSolid(self):
        import pickle
        if self.solidWritten():
            self._solid = pickle.load(open(os.path.join(self._triSurfacedir,"surface.p"),"rb"))
            self._solid.freeze()
            self._refsolid = pickle.load(open(os.path.join(self._triSurfacedir,"refsurface.p"),"rb"))
            self._refsolid.freeze()
        return [self._solid, self._refsolid]

    def writeExtractFeatureDict(self):
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]

        if self._edgesolid:
            template = os.path.join(*[sourcedir,"..","templates","surfaceFeatureExtractDict_WithEdgeSolid"])
        else:
            template = os.path.join(*[sourcedir,"..","templates","surfaceFeatureExtractDict"])
        target   = os.path.join(self._systemdir,"surfaceFeatureExtractDict")

        replacedict = {"{STLFILENAME}"    :  self.writeSTLFilename}
        if self._edgesolid:
            replacedict["{EDGESTLFILENAME}"] = self.writeEdgeSTLFilename

        hf.copyfile(template,target,replacedict)

        if not self.statusFileExists():
            self.writeStatus()

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

    def writePointOutsideSolid(self,target):
        target.write("         locationInMesh ( "+str(self._pointOutsideSolid[0])+" "+str(self._pointOutsideSolid[1])+" "+str(self._pointOutsideSolid[2])+");\n")
        print("Point outside solid: "+str(self._pointOutsideSolid[0])+" "+str(self._pointOutsideSolid[1])+" "+str(self._pointOutsideSolid[2]))

    def writeSTLFilename(self,target):
        self.checksolid("writeSTLFilename")
        target.write("    "+self._solid.getSTLName()+"\n")
        print("writeSTLFilename: "+self._solid.getSTLName())

    def writeRefSTLFilename(self,target):
        self.checksolid("writeRefSTLFilename")
        target.write("    "+self._refsolid.getSTLName()+"\n")
        print("writeRefSTLFilename: "+self._refsolid.getSTLName())

    def writeEdgeSTLFilename(self,target):
        self.checksolid("writeEdgeSTLFilename")
        target.write("    "+self._edgesolid.getSTLName()+"\n")
        print("writeEdgeSTLFilename: "+self._edgesolid.getSTLName())

    def writeSTLeMesh(self,target):
        self.checksolid("writeSTLeMesh")
        filename = self._solid.getSTLName()
        filename = os.path.splitext(filename)[0]+".eMesh"
        target.write("          file \""+filename+"\";\n")

    def writeEdgeSTLeMesh(self,target):
        self.checksolid("writeEdgeSTLeMesh")
        filename = self._edgesolid.getSTLName()
        filename = os.path.splitext(filename)[0]+".eMesh"
        target.write("          file \""+filename+"\";\n")

    def writeSTLObjectName(self,target):
        self.checksolid("writeSTLObjectName")
        target.write("           "+self._solid.getName().replace(" ","")+"\n")

    def writeRefinementBox(self,target):
        self.checksolid("writeRefinementBox")
        target.write("    refinementBox\n")
        target.write("    {\n")
        target.write("        type searchableBox;\n")
        target.write("        min (")
        target.write(" "+str(self._solid.getXmin()))
        target.write(" "+str(self._solid.getYmin()))
        target.write(" "+str(self._solid.getZmin()))
        target.write(");\n")
        target.write("        max (")
        target.write(" "+str(self._solid.getXmax()))
        target.write(" "+str(self._solid.getYmax()))
        target.write(" "+str(self._solid.getZmax()))
        target.write(");\n")
        target.write("    }\n")


    def writeSnappyHexMeshDict(self):
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]

        if self._edgesolid:
            template = os.path.join(*[sourcedir,"..","templates","snappyHexMeshDict_WithEdgeSolid"])
        else:
            template = os.path.join(*[sourcedir,"..","templates","snappyHexMeshDict"])
        target   = os.path.join(self._systemdir,"snappyHexMeshDict")

        replacedict = {"{STLFILENAME}"      :  self.writeSTLFilename,
                       "{STLREFFILENAME}"   :  self.writeRefSTLFilename,
                       "{STLOBJECTNAME}"    :  self.writeSTLObjectName,
                       "{REFINEMENTBOX}"    :  self.writeRefinementBox,
                       "{STLEMESHNAME}"     :  self.writeSTLeMesh,
                       "{EDGESTLEMESHNAME}" :  self.writeEdgeSTLeMesh,
                       "{POINTOUTSIDESOLID}":  self.writePointOutsideSolid}

        hf.copyfile(template,target,replacedict)

    def meshCreated(self):
        return self._meshCreated

    def meshChecked(self):
        return self._meshChecked

    def featuresExtracted(self):
        return self._featuresExtracted

    def solidWritten(self):
        return self._solidWritten

    def statusInfo(self,string=""):
        if self.statusFileExists():
            self.readStatus()
        string += "SnappyHexMesh:\n"
        string += " * Solid written            : "+str(self.solidWritten())+"\n"
        string += " * SurfaceFeatures extracted: "+str(self.featuresExtracted())+"\n"
        string += " * Mesh created             : "+str(self.meshCreated())+"\n"
        string += " * Mesh checked             : "+str(self.meshChecked())+"\n"
        return string

    def laststep(self,string):
        if self.statusFileExists():
            self.readStatus()
        if self.featuresExtracted():
            string = "SurfaceFeatures extracted"
        if self.meshCreated():
            string = "HexMesh created"
        if self.meshChecked():
            string = "HexMesh checked"
        return string

    def extractSurfaceFeatures(self):
       if not self._solidWritten:
           print("WARNING: trying to extract surface features")
           print("         but solid is not written yet.")
           print("         -> trying to first write solid...")
           self.writeSolid()
       if not hf.run(["surfaceFeatureExtract"],self._snappydir) == 0:
           print("ERROR  : surfaceFeatureExtract")
           hf.exit(1)
       else:
           self.setFeatuesExtracted()

    def snappyHexMesh(self):
       if not self.featuresExtracted():
           print("WARNING: trying to run snappyHexMesh")
           print("         but surface features are not extracted yet.")
           print("         -> trying to first extract features...")
           self.extractSurfaceFeatures()

       hf.remove_folder(os.path.join(self._snappydir,"1"))
       hf.remove_folder(os.path.join(self._snappydir,"2"))
       hf.remove_folder(os.path.join(self._snappydir,"3"))

       if not hf.run(["snappyHexMesh"],self._snappydir) == 0:
           print("ERROR while writing snappyHexMesh")
           hf.exit(1)
       else:
           self.setMeshCreated()

    def checkSnappyHexMesh(self):
       if not self.meshCreated():
           print("WARNING: trying to check mesh")
           print("         but mesh has not yet been created!")
           print("         -> trying to create mesh...")
           self.snappyHexMesh()

       if not hf.run(["paraFoam"],self._snappydir) == 0:
           print("ERROR while checking mesh")
           hf.exit(1)
       else:
           if hf.query_yes_no("Do you accept the mesh?", default="yes"):
               self.setMeshChecked()
           else:
               if hf.query_yes_no("Do you want to delete the mesh?", default="no"):
                   self.setMeshCreated(False)
                   hf.remove_folder(os.path.join(self._snappydir,"1"))
                   hf.remove_folder(os.path.join(self._snappydir,"2"))
                   hf.remove_folder(os.path.join(self._snappydir,"3"))
               hf.exit(1)
