import os
import datetime
def printAndLogForce(filename, header, logger=None, outfile=None):

    if not os.path.isfile(filename):
        if logger:
            logger.error("Forces file does not exist!!")
            logger.error("Force filename given: "+filename)
        else:
            print("Forces file does not exist!!")
            print("Force filename given: "+filename)
    else:
        with open(filename, "r") as f:
            first = f.readline()     # Read the first line.
            f.seek(-2, 2)            # Jump to the second last byte.
            while f.read(1) != "\n": # Until EOL is found...
                f.seek(-2, 1)        # ...jump back the read byte plus one more.
            last = f.readline()      # Read last line.
        print("*******")
        for line in header:
            print("* "+line)
        print("*******")
        mylist = last.replace(","," ").replace("(","").replace(")","").split()

        forces = list()
        forces.append((float(mylist[1])+float(mylist[4])+float(mylist[7]))/float(10.0))
        forces.append((float(mylist[2])+float(mylist[5])+float(mylist[8]))/float(10.0))
        forces.append((float(mylist[3])+float(mylist[6])+float(mylist[9]))/float(10.0))

        moments = list()
        moments.append((float(mylist[10])+float(mylist[13])+float(mylist[16]))/float(10.0))
        moments.append((float(mylist[11])+float(mylist[14])+float(mylist[17]))/float(10.0))
        moments.append((float(mylist[12])+float(mylist[15])+float(mylist[18]))/float(10.0))

        print("Last lime iteration number:")
        print(int(float(mylist[0])))
        print("Forces [dN]:")
        print(forces)
        #print("Moments [dNm]:")
        #print(moments)
        print("*******\n")

        if logger:
            logger.info("")
            for line in header:
                logger.info(line)
            logger.info("date & time: "+str(unicode(datetime.datetime.now())))
            logger.info("Last lime iteration number: "+str(int(float(mylist[0]))))
            logger.info("Forces [dN]")
            logger.info(str(forces[0])+", "+str(forces[1])+", "+str(forces[2]))
            logger.info("")

        if outfile:
            with open(outfile,"a") as outerLogFile:
                outerLogFile.write("\n")
                for line in header:
                    outerLogFile.write(line+"\n")
                outerLogFile.write("date & time: "+str(unicode(datetime.datetime.now()))+"\n")
                outerLogFile.write("Last lime iteration number: "+str(int(float(mylist[0])))+"\n")
                outerLogFile.write("Forces [dN]\n")
                outerLogFile.write(str(forces[0])+", ")
                outerLogFile.write(str(forces[1])+", ")
                outerLogFile.write(str(forces[2])+"\n\n")
