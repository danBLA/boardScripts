def run(command,directory=""):
   import os
   import mycommand
   import tempfile
   cwd = ""
   if directory:
       cwd = os.getcwd()
       os.chdir(directory)

   # create and open temporary file
   mytempfile = tempfile.NamedTemporaryFile(suffix='.txt',dir='.')
   # get name of file so we have a name for a temporary file
   filename_start = os.path.split(mytempfile.name)[-1]
   # close the file (which will delete it)
   mytempfile.close()
   print("creating temporary txt-file: "+str(filename_start))

   mycmd = mycommand.Command(" ".join(command),filename_start)
   status, output, error = mycmd.run(timeout=None)
   #try:
   #   import subprocess as sp
   #   returnvalue = sp.call(command)
   #except ImportError:
   #   import os
   #   returnvalue = os.WEXITSTATUS(os.system(" ".join(command)))

   print("removing temporary txt-file: "+str(filename_start))
   remove_file(filename_start)

   if directory:
       os.chdir(cwd)

   return status

def exit(code):
   """"This function exits python."""
   import sys
   sys.exit(code)

def flush_output():
   """This function flushes stderr and stdout"""
   import sys
   sys.stdout.flush()
   sys.stderr.flush()

def copyfile(fromFile,toFile,ReplaceDict=None):
    template = open(fromFile,'r')
    target   = open(toFile,'w')

    for line in template:
        found = False
        if ReplaceDict:
            for key in ReplaceDict:
                if key in line:
                    ReplaceDict[key](target)
                    found = True

        if not found:
            target.write(line)

    template.close()
    target.close()


def create_folder(path, verbose=None):
   """This function creates a folder if it does not exist."""
   import os
   if os.path.isdir(path):
      exist=True
      if(verbose):
         print("Folder "+path+" exists already...")
         flush_output()
   else:
      exist=None
      if(verbose):
         print("Creating folder "+path)
         flush_output()
      os.makedirs(path)
   return exist

def folder_exists(path):
   """This function checks that the folder exists."""
   import os
   if os.path.isdir(path):
      exist=True
   else:
      exist=None
   return exist

def read_key(cparser,section,key,default="",emptydefault=None):
   """This function returns the value associated to the key in parameter."""
   if cparser.has_option(section,key):
      # key found, return key
      return cparser.get(section,key).replace('"','')
   elif default or emptydefault:
      # key not found, return default value
      return default
   else:
      # key not found, no default value available, stop here!
      print("ERROR reading config file")
      print("* section: "+section)
      print("* key    : "+key)
      print("is not defined, no default value available!")
      print("stopping here!")
      flush_output()
      exit(1)

def convert_string_logical(lstring,varname):
   """"This function converts a string into a logical."""
   # convert a string with "true" of "false"
   # to logical
   if lstring.lower() == "true":
      return True
   elif lstring.lower() == "false":
      return None
   else:
      print("ERROR: Can not convert logical "+varname+" !") 
      print("       value="+lstring+", allowed values: true/false")
      flush_output()
      exit(1)

def convert_logical_string(logical):
   """"This function converts a logical to a string"""
   # convert logical to a string
   # with "true" of "false"
   if logical:
      return "true"
   else:
      return "false"

def remove_folder(path,verbose=None):
   """This function removes a folder."""
   import os
   import shutil
   if os.path.isdir(path):
      if verbose:
         print("removing folder: "+path)
         flush_output()
      shutil.rmtree(path)
   else:
      if verbose:
         print("could not remove folder: "+path)
         flush_output()

def remove_file(filename):
    import os
    if os.path.exists(filename):
       os.remove(filename)        

def query_yes_no(question, default="yes"):
    import sys
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def copy_folder(source,destination,verbose=None):
   """This function copy a folder."""
   import os
   import shutil
   print source
   print destination
   source = abspath(source)
   destination = abspath(destination)
   print source
   print destination
   if os.path.isdir(source):
      if not os.path.isdir(destination):
         if verbose:
            print("copy_folder:")
            print("  -> from "+source)
            print("  -> to   "+destination)
            flush_output()
         shutil.copytree(source,destination)
      elif source == destination:
         if verbose:
            print("copy_folder: source = destination")
            flush_output()
      else:        
         if verbose:
            print("copy_folder: target exists...")
            print("  -> updating target folder")
            flush_output()
         print source
         print destination
         shutil.rmtree(destination)
         shutil.copytree(source,destination)
        #for item in os.listdir(destination):
        #   if os.path.isdir(item):
        #      shutil.copytree(item,destination)
        #   elif os.path.isfile(os.path.join(destination,item)):
        #      copy_file(os.path.join(source,item),destination)
        #   else:
        #      print("copy folder: item "+item+" not recognised!")
        #      flush_output()
        #      exit(1)
   else:
      print("copy folder: source folder "+source+" not found")
      flush_output()

def copy_file(filename,destination):
   """This function copy filename into the destination."""
   import os
   import shutil
   if os.path.isfile(filename):
      copied = True
      if os.path.abspath(filename) != os.path.abspath(destination):
         shutil.copy(filename,destination)
      else:
         print("copy file: source and destination are the same file...")
   else:
      print("copy file: ERROR -> source file not found!")
      copied = False
   flush_output()
   return copied
def abspath(path,recdepth=0):
   import os
   if not os.path.isabs(path):
      abs_path = os.path.join(os.getcwd(),path)
   else:
      abs_path = os.path.normpath(path)

   # error handling
   if not os.path.isdir(abs_path) and recdepth < 2:
      # this function is also used for cases
      # where environment variables are used
      # try to get the value for the environment variable from the system
      # note: $()% have to be romeved from the string to use the python function
      abs_path = os.environ.get(path.replace('$','').replace('(','').replace(')','').replace('%',''))
      if abs_path:
         # recursively call the function again to get the absolut path
         return abspath(os.getcwd(),abs_path,recdepth+1)
      else:
         # if it was not an environment variable or the environment variable
         # does not exist just return the input path
         return path

   return abs_path

def relpath(pathfrom, pathto):
   import os
   pathfrom = abspath(pathfrom)
   pathto   = abspath(pathto)

   #if gl.os == "windows":
      # note that in Windows, "C:\" will always be
      # a common prefix, checking for length 3
      # will catch this case and return the
      # absolute path
      #sys_lencommonprefix = 3
   #elif gl.os == "linux":
      # note that in linux, "/" will always be
      # a common prefix, checking for length 1
      # will catch this case and return the
      # absolute path
   sys_lencommonprefix = 1
   #else:
   #   sys_lencommonprefix = 1

   # check if the they have the same prefix, otherwise
   # there's no relative path and we can return the
   # absolute path
   commonprefix = os.path.commonprefix([pathfrom,pathto])
   lencommonprefix = len(commonprefix)
   if lencommonprefix <= sys_lencommonprefix:
      return pathto

   relpath=""
   try:
      relpath = os.path.relpath(pathto,pathfrom)
   except:
      # in python versions < 2.6 os.path.relpath does
      # not exist, in this case return the absolut
      # path of the target
      relpath = pathto
   return relpath
