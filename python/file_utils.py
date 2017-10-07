import os
from os.path import join as pjoin
import shutil
import sys
from tempfile import mkstemp
import numpy as np
import platform
import fnmatch

iswin = platform.system() == 'Windows'
win_prefix = "\\\\?\\"

def get_path(path):
    if iswin and not path.startswith(win_prefix):
        path = unicode(win_prefix + os.path.abspath(path))
    return path

def flush_output():
    sys.stdout.flush()
    sys.stderr.flush()


def exit(code):
    sys.exit(code)


def folder_exists(path):
    if os.path.isdir(get_path(path)):
        exist = True
    else:
        exist = None
    return exist


def file_exists(path):
    if os.path.isfile(get_path(path)):
        exist = True
    else:
        exist = None
    return exist


def exists(path):
    if os.path.exists(get_path(path)):
        exist = True
    else:
        exist = None
    return exist


def create_folder(path):
    path = get_path(path)
    if os.path.isdir(path):
        exist = True
    else:
        exist = None
        os.mkdir(path)
    return exist


def makedirs(path):
    """
    Check if a directory exists. If not, create it (imitates mkdir -p). If yes, do nothing.
    """
    path = get_path(path)
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except:
            print "Failed to create directory " + path.lstrip(win_prefix)
            raise


def makedir(path):
    """
    Check if a directory exists. If not, create it (imitates mkdir -p). If yes, do nothing.
    """
    path = get_path(path)
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except:
            print "Failed to create directory " + path.lstrip(win_prefix)
            raise


def remove_folder(path):
    path = get_path(path)
    if os.path.isdir(path):
        shutil.rmtree(path)
        exist = True
    else:
        exist = None
    return exist


def copy_folder(filename, destination):
    filename = get_path(filename)
    destination = get_path(destination)
    if os.path.isdir(filename):
        copied = True
        if not os.path.isdir(destination):
            shutil.copytree(filename, destination)
        else:
            for item in os.listdir(destination):
                copy_file(os.path.join(filename, item), destination)
    else:
        copied = False
        print "copy folder: folder "+filename.lstrip(win_prefix)+" not found"
        flush_output()
    return copied


def copytree(src, dst, symlinks=False, ignore=None):
    iswin = platform.system() == 'Windows'
    for item in os.listdir(src):
        s = get_path(os.path.join(src, item))
        d = get_path(os.path.join(dst, item))
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def remove_file(filename):
    filename = get_path(filename)
    if os.path.isfile(filename):
        os.remove(filename)
    else:
        print "remove file: file "+filename.lstrip(win_prefix)+" not found"
        flush_output()


def copy_file(filename, destination):
    filename = get_path(filename)
    destination = get_path(destination)
    if os.path.isfile(filename):
        if filename != destination:
            copied = True
            shutil.copy(filename, destination)
        else:
            copied = False
            print "copy file: source and destination are the same file"
            flush_output()
    else:
        copied = False
    return copied


def copy_file_w_dir(filename, src, dest):
    """
    same as copy_file except that the filename can also contain directories
    e.g.
    copy_file_w_dir(RESULT/text.txt, /here/ /there/) will create the directory /there/RESULT/ and copy text.txt into it)
    """
    from os.path import join as pjoin

    srcfile = get_path(pjoin(src, filename))
    dest = get_path(dest)
    if os.path.isfile(srcfile):
        destdir = pjoin(dest, os.path.dirname(filename))
        makedirs(destdir)
        if srcfile != dest:
            shutil.copy(srcfile, destdir)
            copied = True
        else:
            print "copy file: source and destination are the same file"
            flush_output()
            copied = False
    else:
        copied = False
    return copied
        

def copy2server(filename, root, server_loc, prefix=".", server_key="C:\Users\\ross\.ssh\wintesting-calanda"):
        """
        Copy file to the server (Windows only)
        """
        import mycommand
        cmds = []
        os.chdir(root)
        relpath = os.path.relpath(pjoin(prefix,filename),root).replace("\\","/")
        cmds.append("scp -i " + server_key + " " + relpath + " testr@192.168.1.101:" + server_loc)
        mycommand.run_command(cmds)


def rename_file(filename, new_filename):
    filename = get_path(filename) 
    new_filename = get_path(new_filename) 
    if os.path.isfile(filename):
        if filename != new_filename:
            res = True
            os.rename(filename, new_filename)
        else:
            res = False
            print "rename file: source and destination are the same file"
            flush_output()
    else:
        print "rename file: "+filename.lstrip(win_prefix)+" not found"
        res = False
    return res


def compare_file(filename1, filename2):
    import filecmp
    if os.path.isfile(filename1) & os.path.isfile(filename2):
        match = filecmp.cmp(filename1, filename2)
    else:
        print "compare file: file "+filename1+" and/or "+filename2+" not found"
        raise
    return match


def diff_file(filename1, filename2, filename3):
    import filecmp
    import difflib
    if os.path.isfile(filename1) & os.path.isfile(filename2):
        match = filecmp.cmp(filename1, filename2)

        if not match:
            f1 = open(filename1)
            f1content = f1.readlines()
            f1.close()

            f2 = open(filename2)
            f2content = f2.readlines()
            f2.close()

            root, file1 = os.path.split(filename1)
            root, file2 = os.path.split(filename2)

            f3 = open(filename3, "a")
            f3.write(difflib.HtmlDiff().make_file(f1content, f2content,
                                                  fromdesc=file1, todesc=file2, context=True, numlines=0))
            f3.close()
    else:
        print "compare file: file "+filename1+" and/or "+filename2+" not found"
        raise
    return match


def get_paths_to_file(directory,fname,blacklist=None):
    """
    Get list with all paths to specific file in a directory
    """
    paths = []
    for root, dirnames, filenames in os.walk(directory):
        #do not search in folders that are in the blacklist
        if blacklist:
            for folder in blacklist:
                if folder in dirnames:
                    dirnames.remove(folder)
        for filename in fnmatch.filter(filenames, fname):
            paths.append(root)
    return paths


def search_and_replace(filename,str_to_search,str_to_replace):
    """search and replace in file"""
    if len(str_to_search) != len(str_to_replace):
        print "Not running search_and_replace as search and replace string lists do not have the same size"
        return

    # Read in the file
    filedata = None
    with open(filename, 'r') as f:
      filedata = f.read()

    # Replace the target strings
    for elt in zip(str_to_search,str_to_replace):
        filedata = filedata.replace(elt[0], elt[1])

    # Write the file out again
    with open(filename, 'w') as f:
      f.write(filedata)


def lookup_file(filename,path,root,suffix=None):
    """
    Get path to filename by looking for filename in parent directories
    """
    path = path.lstrip(win_prefix)
    root = root.lstrip(win_prefix)
    while root in path:
        if suffix:
            path_to_ref = pjoin(path,suffix)
        else:
            path_to_ref = path
        if file_exists(pjoin(path_to_ref,filename)):
            return get_path(path_to_ref)
        path = os.path.normpath(pjoin(path,os.pardir))
    return None


def search_check_executable(exe, verbose=False):
    returnpath = None
    if not exe:
        return [returnpath, exe]
    exe_found = 0

    [path, exename] = os.path.split(exe)
    if exe:
        if os.access(exe, os.X_OK):
            exe_found = 1
            [path, filename] = os.path.split(exe)
            returnpath = path
        elif os.path.isfile(exe):
            if verbose:
                print(exe+" is not executable!")
            exe = None
        else:
            if verbose:
                print(exe+" is not found!")
                print("-> given as: "+exe)
            exe = None

    # Check in the PATH environment
    if exe_found == 0:
        if verbose:
            print("searching "+exename+" in PATH")
        for path in os.environ["PATH"].split(os.pathsep):
            exe_tmp = os.path.join(path, exename)
            if os.access(exe_tmp, os.X_OK):
                exe_found += 1
                # set PYTHONPATH
                if exe_found == 1:
                    exe = exe_tmp
                    returnpath = path

    if exe_found != 0:
        if verbose:
            print("\n --> "+exename+" found <--")
            print(exe+"\n")
    else:
        print("\n --> "+exename+" not found <--\n")
        print("hint: there is a known bug if the path to transatMB/bin is set up in .bashrc with '~/transatMB/bin'")
        print("temporary fix: dont use the ~ symbol. Use /home/yourname/ instead")

    flush_output()
    return [returnpath, exe]


def which(program):
    """
    like the Unix 'which' command
    """
    def is_exe(filepath):
        return os.path.isfile(filepath) and os.access(filepath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


def issubpath(a, b):
    """true if directory b is a subpath of directory a"""
    def fixpath(p):
        return os.path.normpath(p) + os.sep
    return fixpath(a).startswith(fixpath(b))


def split_path(p):
    a, b = os.path.split(p)
    return (split_path(a) if len(a) and len(b) else []) + [b]


def directory_dict_to_absolute_path(relative_path_dict, root='.', skip=None):
    """
    Convert a dictionary of relative paths to one of absolute paths, with root
    being used as the reference directory.
    The only exception is for the case when the relative dict contains the
    root itself.
    """
    absolute_path = dict()

    if skip and not (type(skip) is list):
        raise BaseException("argument should be a list")

    for key, dirname in relative_path_dict.iteritems():
        if skip and key in skip:
            pass
        else:
            if os.path.abspath(dirname) == os.path.abspath(root):
                absolute_path[key] = os.path.abspath(dirname)
            else:
                absolute_path[key] = os.path.abspath(os.path.join(root, dirname))
    return absolute_path


def change_file(filename, change_dict):
    """
    modify the input in the input file.
    If the input does not exist, inserts it in the namelist given as an (optional) argument
    """
    import re
    try:
        shutil.copy(filename, filename + "_save")
    except:
        print("Could not copy input file to simulation directory")
        return -1, 'OS error'

    # search for the keys to change
    with open(filename + "_save") as f_in:
        newlines = []
        found = {}
        for key in change_dict:
            found[key] = False
        for line in f_in:
            new_line = None
            for key, value in change_dict.items():
                fieldtomatch = r'(\s|^)'+str(re.escape(value[0]))+r'(\s|$)'
                regexp = re.compile(fieldtomatch, re.IGNORECASE)
                inputname = line.split("=")[0]
                if re.match(regexp, inputname.lower()):
                    found[key] = True
                    new_line = value[1] + "\n"
            if new_line:
                newlines.append(new_line)
            else:
                newlines.append(line)

    # if some key was not found, insert it in the right namelist
    for key, value in change_dict.items():
        if not found[key]:
            if len(value) < 3:
                print change_dict
                print key, value
                raise Exception("Input not found. Need to provide namelist for insertion.")
            # search for the keys to change
            currentlines = newlines
            newlines = []
            for line in currentlines:
                new_line = None
                if value[2].lower() in line.lower():
                    new_line = line + value[1] + "\n"
                    found[key] = True
                if new_line:
                    newlines.append(new_line)
                else:
                    newlines.append(line)

    for key, value in change_dict.items():
        if not found[key]:
            raise Exception(str("Could not change some of the inputs ("+key+")"))

    # Write the changed file
    with file(filename, "w") as f_out:
        f_out.writelines(newlines)


def replace(file_path, pattern, subst, backup=False):
    """
    pattern substitution in a file
    if backup is true, a version of the old file is kept (.old)
    """
    #Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path, 'w')
    old_file = open(file_path)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    #close temp file
    new_file.close()
    os.close(fh)
    old_file.close()
    if not backup:
        #Remove original file
        os.remove(get_path(file_path))
    else:
        #Rename original file
        shutil.move(get_path(file_path), get_path(os.path.join(file_path, '.old')))
    #Move new file
    shutil.move(get_path(abs_path), get_path(file_path))


def has_header(filename):
    """
    Check if file has a header
    """
    with open(filename,'r') as f:
        return f.read(1) == '#'


def write_data_to_file(filename, data_list, header_list, units=None, altnames=None, legend=None):
    """
    Write data from numpy arrays to file
    """
    # Write output data to file
    test_output = np.column_stack(tuple(data_list))
    header = []

    # Create list with lines of header
    if legend:
        header.append(r'legend %s' % (legend))
    for element in header_list:
        if units and altnames:
            if element in units:
                if element in altnames:
                    header.append(r'%s: %s %s %s' % ((header_list.index(element)+1), element, units[element], altnames[element]))
                else:
                    header.append(r'%s: %s %s %s' % ((header_list.index(element)+1), element, units[element], "-"))
            else:
                header.append(r'%s: %s %s' % ((header_list.index(element)+1), element, units[element]))
        else:
            header.append(r'%s: %s' % ((header_list.index(element)+1), element))

    # Write data to file
    np.savetxt(filename,test_output,header=os.linesep.join(header))


def add_header(filename,dataobj):
    """
    Add header to a data file (dataobject should be a Testdata object)
    """
    if not has_header(filename):
        data = np.loadtxt(filename)
        if len(np.shape(data))>1:
            values = zip(*data)
        else:
            values = zip(data)
        varnames = dataobj.varnames
        units = dataobj.units
        altnames = dataobj.altnames
        legend = dataobj.legend
        write_data_to_file(filename,values,varnames,units=units,altnames=altnames,legend=legend)

class Tee(object):
    """
    usefull if one wants to write to stdout at the same time as writing to a file
    """
    def __init__(self, name, mode):
        self.file = open(name, mode)
        self.stdout = sys.stdout
        sys.stdout = self

    def __del__(self):
        sys.stdout = self.stdout
        self.file.close()

    def close(self):
        sys.stdout = self.stdout
        self.file.close()

    def write(self, data):
        self.file.write(data)
        self.stdout.write(data)

    def flush(self):
        import sys
        self.stdout.flush()
        sys.stderr.flush()
