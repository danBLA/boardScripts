import math
import os
import help_functions as hf

class Solid(object):
    def __init__(self,name,filename):
       self._name = name
       self._filename = filename
       self._freeze = False
       self.reset()

    def freeze(self):
        self._freeze = True

    def getSTLName(self):
       return self._filename

    def reset(self):
       if self._freeze:
           print("ERROR: Solid can not be changed!")
           print("       (function reset())")
           hf.flush_output()
           hf.exit(1)
       self._nTriangles = 0
       self._nVertices  = 0
       self._pointsX = []
       self._pointsY = []
       self._pointsZ = []
       self._normalX = []
       self._normalY = []
       self._normalZ = []

    def addPoint(self,x,y,z):
        if self._freeze:
           print("ERROR: Solid can not be changed!")
           print("       (function addPoint())")
           hf.flush_output()
           hf.exit(1)
        self._pointsX.append(float(x))
        self._pointsY.append(float(y))
        self._pointsZ.append(float(z))
        self._nVertices += 1

    def addTriangle(self,nx,ny,nz):
        if self._freeze:
           print("ERROR: Solid can not be changed!")
           print("       (function addTriangle())")
           hf.flush_output()
           hf.exit(1)
        self._normalX.append(float(nx))
        self._normalY.append(float(ny))
        self._normalZ.append(float(nz))
        self._nTriangles += 1

    def getName(self):
        return self._name

    def getXmin(self):
        return min(self._pointsX)

    def getXmax(self):
        return max(self._pointsX)

    def getYmin(self):
        return min(self._pointsY)

    def getYmax(self):
        return max(self._pointsY)

    def getZmin(self):
        return min(self._pointsZ)

    def getZmax(self):
        return max(self._pointsZ)

    def getDx(self):
        return self.getXmax() - self.getXmin()

    def getDy(self):
        return self.getYmax() - self.getYmin()

    def getDz(self):
        return self.getZmax() - self.getZmin()

    def move(self,dx,dy,dz):
        if self._freeze:
           print("ERROR: Solid can not be changed!")
           print("       (function move())")
           hf.flush_output()
           hf.exit(1)
        print("Moving solid \""+self._name+"\" by (dx/dy/dz): "+str(dx)+","+str(dy)+","+str(dz))
        for i, [x,y,z] in enumerate(zip(self._pointsX,self._pointsY,self._pointsZ)):
            self._pointsX[i] = x + float(dx)
            self._pointsY[i] = y + float(dy)
            self._pointsZ[i] = z + float(dz)

    def scale(self,factor):
        if self._freeze:
           print("ERROR: Solid can not be changed!")
           print("       (function scale())")
           hf.flush_output()
           hf.exit(1)
        print("Scaling solid \""+self._name+"\" by factor: "+str(factor))
        for i, [x,y,z] in enumerate(zip(self._pointsX,self._pointsY,self._pointsZ)):
            self._pointsX[i] = float(factor)*x
            self._pointsY[i] = float(factor)*y
            self._pointsZ[i] = float(factor)*z

    def rotate(self,beta,axis):
        if self._freeze:
           print("ERROR: Solid can not be changed!")
           print("       (function rotate())")
           hf.flush_output()
           hf.exit(1)
        print("Rotating solid \""+self._name+"\" by angle: "+str(beta)+" around "+axis.upper()+"-axis")
        alpha  = math.radians(float(beta))
        matrix = [[math.cos(alpha),-math.sin(alpha)],[math.sin(alpha),math.cos(alpha)]]
        if axis.lower() == "x":
            for i, [y,z] in enumerate(zip(self._pointsY,self._pointsZ)):
                self._pointsY[i] = y*matrix[0][0] + z*matrix[0][1]
                self._pointsZ[i] = y*matrix[1][0] + z*matrix[1][1]
            for i, [ny,nz] in enumerate(zip(self._normalY,self._normalZ)):
                self._normalY[i] =ny*matrix[0][0] +nz*matrix[0][1]
                self._normalZ[i] =ny*matrix[1][0] +nz*matrix[1][1]
        elif axis.lower() == "y":
            for i, [z,x] in enumerate(zip(self._pointsZ,self._pointsX)):
                self._pointsZ[i] = z*matrix[0][0] + x*matrix[0][1]
                self._pointsX[i] = z*matrix[1][0] + x*matrix[1][1]
            for i, [nz,nx] in enumerate(zip(self._normalZ,self._normalX)):
                self._normalZ[i] =nz*matrix[0][0] +nx*matrix[0][1]
                self._normalX[i] =nz*matrix[1][0] +nx*matrix[1][1]
        elif axis.lower() == "z":
            for i, [x,y] in enumerate(zip(self._pointsX,self._pointsY)):
                self._pointsX[i] = x*matrix[0][0] + y*matrix[0][1]
                self._pointsY[i] = x*matrix[1][0] + y*matrix[1][1]
            for i, [nx,ny] in enumerate(zip(self._normalX,self._normalY)):
                self._normalX[i] =nx*matrix[0][0] +ny*matrix[0][1]
                self._normalY[i] =nx*matrix[1][0] +ny*matrix[1][1]
        else:
            print("ERROR in rotate")
            sys.exit(1)

    def __str__(self):
        string  = "Solid name         : "+self._name+"\n"
        string += "Number of Triangles: "+str(self._nTriangles)+"\n"
        string += "Number of Vertices : "+str(self._nVertices)+"\n"
        string += "xmin/xmax          : "+str(self.getXmin())+","+str(self.getXmax())+"\n"
        string += "ymin/ymax          : "+str(self.getYmin())+","+str(self.getYmax())+"\n"
        string += "zmin/zmax          : "+str(self.getZmin())+","+str(self.getZmax())+"\n"
        return string

    def writeToFile(self,filename,directory="stl_final"):
        stl = open(os.path.join(directory,filename),'w')
        stl.write("solid "+self._name+"\n")
        if not self._nTriangles*3 == self._nVertices:
           print("ERROR: nTriangles*3 /= nVertices")
           sys.exit(1)

        for i in xrange(0,self._nTriangles):
            #stl.write(("  facet normal  "
            #           +    str(self._normalX[i])
            #           +" "+str(self._normalY[i])
            #           +" "+str(self._normalZ[i])
            #           +"\n"))
            stl.write(" facet normal  {:e} {:e} {:e}\n".format(self._normalX[i],self._normalY[i],self._normalZ[i]))
            stl.write("    outer loop\n")
            for j in xrange(0,3):
                stl.write("      vertex  {:e} {:e} {:e}\n".format(self._pointsX[3*i+j],self._pointsY[3*i+j],self._pointsZ[3*i+j]))
            #    stl.write(("      vertex  "
            #                 +    str(self._pointsX[3*i+j])
            #                 +" "+str(self._pointsY[3*i+j])
            #                 +" "+str(self._pointsZ[3*i+j])
            #                 +"\n"))
            stl.write("    endloop\n")
            stl.write("  endfacet\n")
        stl.write("endsolid\n")

    def repairAndWriteToFile(self,filename,directory="stl_final"):
        if self._freeze:
           print("ERROR: Solid can not be changed!")
           print("       (function repair())")
           hf.flush_output()
           hf.exit(1)
        path_filename=os.path.abspath(__file__)
        executablesDir = os.path.split(path_filename)[0]
        self.writeToFile("tmp.stl",".")
        command = []
        command.append(os.path.join(executablesDir,"admesh"))
        command.append("-nufdv")
        command.append("--write-ascii-stl=tmp1.stl")
        command.append("tmp.stl")

        hf.run(command)

        stl = open(os.path.join(directory,filename),'w')

        for line in open("tmp1.stl"):
            elements = line.lower().split()
            if elements[0] == "solid":
               stl.write("solid "+self._name+"\n")
            elif elements[0] == "endsolid":
               stl.write("endsolid "+self._name+"\n")
            else:
               stl.write(line)

        stl.close()

        os.remove("tmp.stl")
        os.remove("tmp1.stl")

    def repair(self):
        if self._freeze:
           print("ERROR: Solid can not be changed!")
           print("       (function repair())")
           hf.flush_output()
           hf.exit(1)
        path_filename=os.path.abspath(__file__)
        executablesDir = os.path.split(path_filename)[0]
        self.writeToFile("tmp.stl",".")
        command = []
        command.append(os.path.join(executablesDir,"admesh"))
        command.append("-nufdv")
        command.append("--write-ascii-stl=tmp1.stl")
        command.append("tmp.stl")

        hf.run(command)

        self.reset()
        for line in open("tmp1.stl"):
            elements = line.lower().split()
            if elements[0] == "solid":
                self._name = elements[1]
            if elements[0] == "facet":
                self.addTriangle(elements[2],elements[3],elements[4])
            if elements[0] == "vertex":
                self.addPoint(elements[1],elements[2],elements[3])

        os.remove("tmp.stl")
        os.remove("tmp1.stl")


def createSolidsFromSTL(filename,directory="geometries"):
    solids = []
    solid = None
    for line in open(os.path.join(directory,filename)):
       elements = line.lower().split()
       if elements[0] == "solid":
           solid = Solid(elements[1],filename)
           solids.append(solid)
       elif elements[0] == "facet":
           solid.addTriangle(float(elements[2]),float(elements[3]),float(elements[4]))
       elif elements[0] == "vertex":
           solid.addPoint(float(elements[1]),float(elements[2]),float(elements[3]))
    return solids

def createSolidFromSTL(filename,directory="geometries"):
    solids = createSolidsFromSTL(filename,directory)
    if not len(solids) == 1:
        print("ERROR reading file: "+filename)
        print("File contains "+str(len(solids)))
        print("but it should contain exactly 1 solid!")
        sys.exit(1)
    return solids[0]
