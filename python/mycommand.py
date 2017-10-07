import threading
import subprocess
import traceback
import shlex
import time
import sys
import io
import file_utils as fu

class Command(object):
    """
    Enables to run subprocess commands in a different thread with TIMEOUT option.

    Based on jcollado's solution:
    http://stackoverflow.com/questions/1191374/subprocess-with-timeout/4825933#4825933
    """
    command = None
    process = None
    status = None
    output, error = '', ''

    def __init__(self, command, filename, screen_output=False):
        if isinstance(command, basestring):
            command = shlex.split(command)
        self.command = command
        self.screen_output = screen_output
        self.filename = fu.get_path(filename)
        self.error = "No error detected"

    def run(self, timeout=None, **kwargs):
        """ Run a command then return: (status, output, error). """
        import os
        import sys
        import signal

        def target(**kwargs):
            try:
                with io.open(self.filename, 'wb') as writer, io.open(self.filename, 'rb', 1) as reader:
                    self.process = subprocess.Popen(self.command, stdout=writer, **kwargs)
                    while self.process.poll() is None:
                        if self.screen_output:
                            sys.stdout.write(reader.read())
                        time.sleep(0.5)
                    self.process.communicate()
                    self.status = self.process.returncode
                    self.output = reader.read()
                    if self.screen_output:
                        sys.stdout.write(self.output)
            except BaseException:
                self.error = traceback.format_exc()
                print self.error
                self.status = -1
        # default stderr
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.STDOUT

        platform = sys.platform

        if platform == "win32":
            if 'shell' not in kwargs:
                kwargs['shell'] = True
        else:
            kwargs['preexec_fn'] = os.setsid  # necessary for os.killgp


        # thread
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.start()
        thread.join(timeout)
        err = ''
        out = ''
        if thread.is_alive():
            if timeout:
                msg = "\nProcess has exceeded timeout limit of " + str(timeout) + " seconds" + \
                      "\nThis can be changed in test.cfg"
                err += msg
                out += msg

                if platform == "win32":
                    print msg
                    subprocess.Popen("taskkill /F /T /PID %i >null" % self.process.pid, shell=True)
                else:
                    os.killpg(self.process.pid, signal.SIGTERM)
                    # NB: using self.process.terminate() does not work with mpiexec
                    msg = "\nKilled process"
                    err += msg
                    out += msg
            thread.join()
        fu.remove_file(self.filename)
        return self.status, str(self.output)+out, str(self.error)+err

def run_command(cmds,iswindows=None):
    """ run set of commands contained in a list"""
    import os
    if iswindows is None:
        import platform
        iswindows = platform.system() == "Windows"

    try:
        for i in cmds:
            if isinstance(i,tuple):
               cmd = i[0]
               args = [elt for elt in i if i.index(elt)>0]
            else:
               cmd = i
               args = None
            print "                           "
            print ">> Running command: " + str(cmd) 
            print "                           "
            content = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
            if args:
                output, error = content.communicate(input="\n".join(args)+"\n")
            else:
                output, error = content.communicate()
            if content.returncode !=0:
                print "                                 "
                print "#===============================#"
                print "# Problem experienced, exiting! #"
                print "#===============================#"
                print "                                 "
                print output 
                print error
                print "                                 "
                if not iswindows: 
                    sys.exit(1)
                else:
                    os._exit(1)
    except subprocess.CalledProcessError as e:
        errorcode = e.returncode
        if errorcode >= 1:
            print "                                 "
            print "#===============================#"
            print "# Problem experienced, exiting! #"
            print "#===============================#"
            print "                                 "
            print e
            print "                                 "
            if not iswindows: 
                sys.exit(1)
            else:
                os._exit(1)
