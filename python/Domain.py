import os
import math
import Solid
import help_functions as hf
class Domain(object):
    def __init__(self,snappydir,logger):
        self._solid = None
        self._logger = logger

        self._facXmin = 19.0
        self._facXmax =  3.3
        self._facY    =  1.5
        self._facZ    =  1.0

        self._pointOutsideSolid = [0.0, 0.0, 0.0]

        #self._nx = 30
        self._nx = 28
        self._ny = 0
        self._nz = 0

        self._snappydir   = snappydir
        self._polymeshdir = os.path.join(*[snappydir, "constant","polyMesh"])

        self._folderlist = []
        self._folderlist.append(self._snappydir)
        self._folderlist.append(self._polymeshdir)

        self._statusfilename = os.path.join(self._snappydir,"polymesh.cfg")
        self._meshCreated = False

        if self.statusFileExists():
            self.readStatus()

    def setMeshCreated(self,boolean=True):
        self._meshCreated = boolean
        self.writeStatus()

    def writeStatus(self):
      import ConfigParser
      try:
          config = ConfigParser.SafeConfigParser()
      except:
          config = ConfigParser.RawConfigParser()

      config.add_section('POLYMESH')
      config.set('POLYMESH','meshCreated',hf.convert_logical_string(self._meshCreated))

      statusfile = open(self._statusfilename, 'w')
      config.write(statusfile)
      statusfile.close()

    def readStatus(self):
      import ConfigParser
      try:
          config = ConfigParser.SafeConfigParser()
      except:
          config = ConfigParser.RawConfigParser()

      config.read(self._statusfilename)
      if config.has_section('POLYMESH'):
          self._meshCreated = hf.convert_string_logical(hf.read_key(config,'POLYMESH','meshCreated',"False"),'meshCreated')
      else:
          print("WARNING: Domain -> config file found but no section POLYMESH")

    def statusFileExists(self):
        return os.path.isfile(self._statusfilename)

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

        dx=solid.getDx()
        dy=solid.getDy()
        dz=solid.getDz()

        self._xmin = solid.getXmin()-self._facXmin*dx
        self._xmax = solid.getXmax()+self._facXmax*dx

        self._ymin = solid.getYmin()-self._facY   *dy
        self._ymax = solid.getYmax()+self._facY   *dy

        self._zmin = solid.getZmin()-self._facZ   *dz
        self._zmax = solid.getZmax()+self._facZ   *dz

        self.adjustDomainNX(self._nx)

        self._pointOutsideSolid[0] = (self._xmin + solid.getXmin())*0.5
        self._pointOutsideSolid[1] = (self._ymin + solid.getYmin())*0.5
        self._pointOutsideSolid[2] = (self._zmin + solid.getZmin())*0.5

    def getPointOutsideSolid(self):
        return self._pointOutsideSolid

    def checksolid(self,whichfunction):
        if not self._solid:
            print("ERROR: Domain -> no solid defined!")
            print("       in "+whichfunction+"!")
            hf.flush_output()
            hf.exit(1)

    def adjustDomainNX(self,nx_in=None):
        self.checksolid("adjustDomainNX")
        if nx_in:
           self._nx = nx_in
           nx = nx_in
        else:
           nx = self._nx
        dx = (self._xmax - self._xmin)/nx

        cy = (self._ymin + self._ymax)/2.0
        ny = math.ceil((self._ymax - cy)/dx)
        self._ymin = cy - ny*dx
        self._ymax = cy + ny*dx
        self._ny = int(2*ny)

        cz = (self._zmin + self._zmax)/2.0
        nz = math.ceil((self._zmax - cz)/dx)
        self._zmin = cz - nz*dx
        self._zmax = cz + nz*dx
        self._nz = int(2*nz)

    def meshCreated(self):
        return self._meshCreated

    def statusInfo(self,string=""):
        string += "Polymesh/Domain:\n"
        string += " * Mesh created: "+str(self.meshCreated())+"\n"
        return string

    def laststep(self,string):
        if self.statusFileExists():
            self.readStatus()
        if self.meshCreated():
            string = "Domain Mesh created"
        return string

    def __str__(self):
        self.checksolid("__str__")
        string  = "Domain with solid  : "+self._solid.getName()+"\n"
        string += "xmin/xmax          : "+str(self.getXmin())+","+str(self.getXmax())+"\n"
        string += "ymin/ymax          : "+str(self.getYmin())+","+str(self.getYmax())+"\n"
        string += "zmin/zmax          : "+str(self.getZmin())+","+str(self.getZmax())+"\n"
        string += "Nx                 : "+str(self.getNx())+"\n"
        string += "Ny                 : "+str(self.getNy())+"\n"
        string += "Nz                 : "+str(self.getNz())+"\n"
        string += "dx                 : "+str((self.getXmax()-self.getXmin())/self.getNx())+"\n"
        string += "dy                 : "+str((self.getYmax()-self.getYmin())/self.getNy())+"\n"
        string += "dz                 : "+str((self.getZmax()-self.getZmin())/self.getNz())+"\n"
        return string

    def getXmin(self):
        self.checksolid("getXmin")
        return self._xmin

    def getXmax(self):
        self.checksolid("getXmax")
        return self._xmax

    def getYmin(self):
        self.checksolid("getYmin")
        return self._ymin

    def getYmax(self):
        self.checksolid("getYmax")
        return self._ymax

    def getZmin(self):
        self.checksolid("getZmin")
        return self._zmin

    def getZmax(self):
        self.checksolid("getZmax")
        return self._zmax

    def getNx(self):
        self.checksolid("getNx")
        return self._nx

    def getNy(self):
        self.checksolid("getNy")
        return self._ny

    def getNz(self):
        self.checksolid("getNz")
        return self._nz

    def writeBlockDict(self):
        self.checksolid("writeBlockDict")
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]

        template = os.path.join(*[sourcedir,"..","templates","blockMeshDict"])
        target   = os.path.join(self._polymeshdir,"blockMeshDict")

        replacedict = {"{VERTICES}"    :  self.writeVertices,
                       "{BLOCKS}"      :  self.writeBlock}

        hf.copyfile(template,target,replacedict)

        if not self.statusFileExists():
            self.writeStatus()


    def writeVertices(self,outfile):
        self.checksolid("writeVertices")
        x0 = str(self.getXmin())
        x1 = str(self.getXmax())
        y0 = str(self.getYmin())
        y1 = str(self.getYmax())
        z0 = str(self.getZmin())
        z1 = str(self.getZmax())
        outfile.write("vertices\n")
        outfile.write("(\n")
        outfile.write("   ("+x0+" "+y0+" "+z0+")\n")
        outfile.write("   ("+x1+" "+y0+" "+z0+")\n")
        outfile.write("   ("+x1+" "+y1+" "+z0+")\n")
        outfile.write("   ("+x0+" "+y1+" "+z0+")\n")
        outfile.write("   ("+x0+" "+y0+" "+z1+")\n")
        outfile.write("   ("+x1+" "+y0+" "+z1+")\n")
        outfile.write("   ("+x1+" "+y1+" "+z1+")\n")
        outfile.write("   ("+x0+" "+y1+" "+z1+")\n")
        outfile.write(");\n")

    def writeBlock(self,outfile):
        self.checksolid("writeBlock")
        nx = str(self.getNx())
        ny = str(self.getNy())
        nz = str(self.getNz())
        outfile.write("blocks\n")
        outfile.write("(\n")
        outfile.write("   hex (0 1 2 3 4 5 6 7)")
        outfile.write(" ("+nx+" "+ny+" "+nz+")")
        outfile.write(" simpleGrading (1 1 1)\n")
        outfile.write(");\n")

    def blockMesh(self):

       if not hf.run(["blockMesh"],self._snappydir) == 0:
           print("ERROR while writing blockMesh")
           hf.exit(1)
       else:
           self.setMeshCreated()
