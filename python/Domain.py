import os
import math
import Solid
class Domain(object):
    def __init__(self,solid):
        dx=solid.getDx()
        dy=solid.getDy()
        dz=solid.getDz()

        self._solid = solid

        self._facXmin =  3.3
        self._facXmax = 19.0
        self._facY    =  1.5
        self._facZ    =  1.0

        self._nx = 34
        self._ny = 0
        self._nz = 0

        self._xmin = solid.getXmin()-self._facXmin*dx
        self._xmax = solid.getXmax()+self._facXmax*dx

        self._ymin = solid.getYmin()-self._facY   *dy
        self._ymax = solid.getYmax()+self._facY   *dy

        self._zmin = solid.getZmin()-self._facZ   *dz
        self._zmax = solid.getZmax()+self._facZ   *dz

        self.adjustDomainNX(self._nx)

    def adjustDomainNX(self,nx):
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

    def __str__(self):
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
        return self._xmin

    def getXmax(self):
        return self._xmax

    def getYmin(self):
        return self._ymin

    def getYmax(self):
        return self._ymax

    def getZmin(self):
        return self._zmin

    def getZmax(self):
        return self._zmax

    def getNx(self):
        return self._nx

    def getNy(self):
        return self._ny

    def getNz(self):
        return self._nz

    def writeBlockDict(self,targetDir="."):
        path_filename=os.path.abspath(__file__)
        sourcedir = os.path.split(path_filename)[0]

        template = open(os.path.join(*[sourcedir,"..","templates","blockMeshDict"]),'r')
        target   = open(os.path.join(targetDir,"blockMeshDict"),'w')

        for line in template:
            if "{VERTICES}" in line:
                self.writeVertices(target)
            elif "{BLOCKS}" in line:
                self.writeBlock(target)
            else:
                target.write(line)

        template.close()
        target.close()

    def writeVertices(self,outfile):
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
        nx = str(self.getNx())
        ny = str(self.getNy())
        nz = str(self.getNz())
        outfile.write("blocks\n")
        outfile.write("(\n")
        outfile.write("   hex (0 1 2 3 4 5 6 7)")
        outfile.write(" ("+nx+" "+ny+" "+nz+")")
        outfile.write(" simpleGrading (1 1 1)\n")
        outfile.write(");\n")
