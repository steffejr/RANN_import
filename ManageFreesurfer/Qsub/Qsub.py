import os
import subprocess

#you will probably make 1 template instance and use it many times

class Qsub(object):
    def __init__(self, templatepath, scriptdir, qsubpath='qsub', command_args=['mem_free=3.5G', 'h_vmem=3.5G']):
        self.scriptdir = scriptdir #directory where qsub scripts are placed
        self.outfiledir = os.path.join(self.scriptdir, 'logs', 'output')  #directory where stdout outputs will be placed
        self.errfiledir = os.path.join(self.scriptdir, 'logs', 'error')  #directory where error outputs will be placed
        self.done_dir = os.path.join(self.scriptdir, 'done') #directory where finished scripts will be placed
        self.submitted_dir = os.path.join(self.scriptdir, 'submitted') #directory where finished scripts will be placed
        self.templatepath = templatepath #path (string) to template
        self.qsubpath = qsubpath #path to qsub executable
        self.command_args = command_args #stuff preceeded with -l in qsub
        self.__checkdirs__()



    def submit(self, subs, command_args=None, submitted_dir=None, done_dir=None, hold_jid=[]):
        '''
        Takes a dictionary defining terms in a template, along with an optional list of command arguments and executes qsub on the sun grid engine
        
        |subs-a dictionary that must at least have a mapping {'filename':'scriptname.sh'}. Can optionally have 'done_dir':<path> defined for special log placement (as in the case of freesurfer)
        |command_args-optional arguments ex: ['mem_free=3.5G','h_vmem=3.5G'] will be treated as qsub <other stuff> -l MEM_FREE=3.5G,h_vmem=3.5G <script>
        |hold_jid-list of jobids that this job must wait for before executing (list of number strings).
        
        returns the string valued jobid of the job just submitted
        '''

        #if we don't have subject specific paths, use default for this qsub object
        if done_dir == None:
            done_dir = self.done_dir
        if submitted_dir == None:
            submitted_dir = self.submitted_dir

        submitted_path = os.path.join(submitted_dir, subs['filename'])
        subs['submitted_path'] = submitted_path
        subs['done_path'] = os.path.join(done_dir, subs['filename'])

        #open template and output file
        templatefile = open(self.templatepath, 'r')
        submitted_file = open(submitted_path, 'w')

        #read in template, add bottom line to move script when done, substitute, and write to script
        templatestring = templatefile.read()
        templatestring += '\nmv %(submitted_path)s %(done_path)s\n'

        #substitute in dictionary vars
        submitted_file.write(templatestring % subs)

        #close files
        templatefile.close()
        submitted_file.close()

        #build args
        args = [self.qsubpath, '-o', self.outfiledir, '-e', self.errfiledir]
        if len(hold_jid) > 0:
            args += ['-hold_jid'] + [','.join(hold_jid)]
        if command_args != None and len(command_args) > 0:
            args += ['-l', ','.join(command_args)]
        elif self.command_args != None and len(self.command_args) > 0:
            args += ['-l', ','.join(self.command_args)]
        args += [submitted_path]

        #execute script
        print "Executing {}".format(' '.join(args))
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if stderr != '':
            print "Qsub Error: {}".format(stderr)
        print stdout
        return stdout.split()[2] #jobid


    def __checkdirs__(self):
        if not os.path.exists(self.scriptdir):
            os.makedirs(self.scriptdir)
        if not os.path.exists(self.outfiledir):
            os.makedirs(self.outfiledir)
        if not os.path.exists(self.errfiledir):
            os.makedirs(self.errfiledir)
        if not os.path.exists(self.done_dir):
            os.makedirs(self.done_dir)
        if not os.path.exists(self.submitted_dir):
            os.makedirs(self.submitted_dir)

    def __str__(self):
        with open(self.templatepath, 'r') as templatefile:
            return templatefile.read()
