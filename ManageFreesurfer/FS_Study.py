'''
The FS_Study module containts the FS_Study class.

.. moduleauthor:: Aleksey Orekhov <cruser42@gmail.com>

'''

import os
import warnings
import string
import re
from ManageFreesurferErrors import FSStudyErrors
from Qsub.Qsub import Qsub
import FS_Subject

known_fs_files = ['fsaverage', 'lh.EC_average', 'rh.EC_average']

class FS_Study(object):
    """
    The FS_Study class manages one freesurfer SUBJECTS_DIR. Specifically, it enables easy submission of
    freesurfer jobs to a rocks cluster running sun grid engine using the qsub console command. 
    
    Layout of the directory structure
    
    | root_dir/freesurfer                    -Freesurfer SUBJECTS_DIR to Use
    | root_dir/runs_freesurfer               -Where scripts that have not completed exist
    | root_dir/runs_freesurfer/done          -Where scripts that have completed are placed
    | root_dir/runs_freesurfer/logs/errors   -Where qsub stderr outputs go  (error messages raised by script)
    | root_dir/runs_freesurfer/logs/output   -Where qsub stdout data goes   (output messages produced by script)
    
    If the appropriate directory structure does not exist, the module will attempt to create it when it is run at the root_dir.
    """


    def __init__(self, root_dir, fs_home,fsIDRE,subjects_dir=None):
        '''
        | root_dir - path to root of fs FS_Study directory structure
        | fs_home - path to freesurfer home on machine that will be running the scripts, usually, /usr/local/freesurfer
        | fsIDRE - regular expression string or object that freesurfer subject names (subjid when give to a freesurfer recon-all command) must match (case sensitive)
        '''
        #: path to root of fs FS_Study directory structure
        self.path = os.path.normpath(root_dir)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        #: path to freesurfer home on machine that will be running the scripts, usually, /usr/local/freesurfer
        self.fs_home = fs_home
        #: path to freesurfer home on machine that will be running the scripts, usually, /usr/local/freesurfer
        self.subjects_dir = os.path.normpath(os.path.join(self.path, 'freesurfer')) if subjects_dir == None else subjects_dir
        #: compiled regular expression object module tests against subject directory names
        self.__fsIDREC__ = re.compile(fsIDRE) if type(fsIDRE) == 'str' else fsIDRE#freesurfer subid regular expression compiled
        #: list of FS_Scan objects created by parsing the folders in root_dir/freesurfer (SUBJECTS_DIR). Useful when making for loops over all subjects.
        self.subjectlist = []
        #: dict of FS_Scan objects created by parsing the folders in root_dir/freesurfer (SUBJECTS_DIR). Useful when making queries on specific subjects.
        self.subjects = {}
        #: directory where module looks for qsub templates. There should only be one template for recon-all and it comes with this package
        self.qsubTemplatesDir = os.path.join(os.path.dirname(FS_Subject.__file__), 'qsubtemplates')
        self.__findSubjects__()




    def importT1(self, fsID, path):
        '''
        Imports single T1 image into freesurfer SUBJECTS_DIR managed by this module instance if it matches the pattern for the directory and does
        not already exist
        
        |fsID - foldername subject is expected to have. 
        |path - path to nifti file that we will try to import
        '''

        if not self.__fsIDREC__.match(fsID):
            print "{} did not match rec pattern {} during import: aborted".format(fsID, __fsIDREC__.pattern)

        #do not import image if it already exists
        if fsID in self.subjects:
            return False

        #get subject/scan info & set up template objects
        fs_subject = self.__addsubject__(fsID)

        #set up args & help text
        helptext = ('#This script was used to import the subject with id %(fsID)s from\n'
                       + '#{}\n'.format(path)
                       + '#into the FreeSurfer Analysis'
                  )
        args_import = '-i {0}'.format(path)
        import_jobid = self.recon_all(fs_subject=fs_subject, prefix='import', args=args_import, helptext=helptext)
        reconall_jobid = self.recon_all(fs_subject=fs_subject, prefix='all', args='-all', helptext='This script does a full recon-all of this subject', hold_jid=[import_jobid])
        return fs_subject.fsID



    def recon_all(self, fs_subject, prefix='prefix', args='RECON-ALL ARGS GO HERE!', helptext='#The helptext was not filled in', hold_jid=[]):
        '''
        Generic Freesurfer recon-all command. Will create and submit script to SGE qmon
        
        |fs_subject - FS_Subject object we want to work on
        |prefix - text to prepend to script file so we know what operation was carried out
        |args - arguments to the recon-all command
        |helptext - Descriptive text to put at top of script file
        |hold_jid - list of jobids 
        returns jobid of submitted job as string
        '''
        #set up template objects
        reconalltemplate = os.path.join(self.qsubTemplatesDir, 'reconall.sh')
#        qsub = Qsub(templatepath=reconalltemplate, scriptdir=os.path.join(self.path, 'runs_freesurfer'), qsubpath='qsub', command_args=['mem_free=3.5G', 'h_vmem=3.5G'])
        qsub = Qsub(templatepath=reconalltemplate, scriptdir=os.path.join(self.path, 'runs_freesurfer'), qsubpath='qsub', command_args=['mem_free=3.5G'])

        #set up substitution dictionary
        subs_dict = self.__buildDict__(fs_subject=fs_subject, prefix=prefix, args=args, helptext=helptext)

        #submit and return jobid
        return qsub.submit(subs_dict, submitted_dir=fs_subject.submitted_dir, done_dir=fs_subject.done_dir, hold_jid=hold_jid)

    def __buildDict__(self, fs_subject, prefix='prefix', args='RECON-ALL ARGS GO HERE!', helptext='#The helptext was not filled in'):
        '''
        Returns a dictionary ready to substitute into a qsub recon-all job. 
        |fs_subject - FS_Subject object we want to work on
        |prefix - text to prepend to script file so we know what operation was carried out
        |args - arguments to the recon-all command
        |helptext - Descriptive text to put at top of script file    
        '''
        subs_dict = {'filename':prefix + '_' + fs_subject.fsID + '.sh',
                'helptext':helptext,
                'FREESURFER_HOME':self.fs_home,
                'subjects_dir':self.subjects_dir,
                'recon-all_args': args,
                'fsID': fs_subject.fsID
                }
        subs_dict['helptext'] = subs_dict['helptext'] % subs_dict
        return subs_dict


    def __findSubjects__(self):
        '''
        Reloads the list of FS_Subject objects at the subject dir for this FS_Study instance
        '''
        global known_fs_files

        if not os.path.exists(self.subjects_dir):
            os.makedirs(self.subjects_dir)

        try:
            fsfiles = os.listdir(self.subjects_dir)
        except:
            warnings.warn("\nCould not list files in: " + self.subjects_dir)
            return

        self.subjectlist = []
        self.subjects = {}


        for fsfile in fsfiles:
            fsfile_fullpath = os.path.normpath(os.path.join(self.subjects_dir, fsfile))
            if (not os.path.isdir(fsfile_fullpath)):
                continue
            m = self.__fsIDREC__.match(fsfile)
            if m:
                self.__addsubject__(fsID=fsfile)
            elif fsfile in known_fs_files:
                continue
            else:
                raise Exception('could not parse ' + fsfile + '\n Should it be in this directory?\n')


    def __addsubject__(self, fsID):
        '''
        Creates a new subject with provided fsID and adds it to this instance's dictionary and list.
        NOTE: This will NOT import data ore create a folder, this will affect the running state of this
        instance of the FS_Study module only
        
        |fsID - foldername subject is expected to have. 
        '''
        #create new FSscan object
        newFSsubject = FS_Subject.FS_Subject(self, fsID=fsID)

        #add scan to list and dictionary
        self.subjectlist.append(newFSsubject)
        self.subjects[fsID] = newFSsubject

        return newFSsubject

    def __rm_isrunning__(self, fsID):
        '''
        Removes the file freesurfer places in a subjects dir to indicate that freesurfer is running on the subject. Useful when
        you have aborted a run, and want to re-run the subject, but due to the presence of the file, freesurfer still thinks the subject
        is being run and refuses to start.
        
        |fsID - foldername subject is expected to have. 
        '''
        isrunningpath = os.path.join(self.subjects_dir, fsID, 'scripts/IsRunning.lh+rh')
        try:
            os.remove(isrunningpath)
            print "Removed %s" % isrunningpath
        except Exception as e:
            print "Failed to remove: %s" % isrunningpath

    def __str__(self):
        self.__findSubjects__()
        outstring = 'Study: %s\n\t ' % self.path
        subject_strings = []
        for subject in self.subjectlist:
            subject_strings.append(subject.__str__())
        subject_strings.sort()
        subject_strings = [string.replace(subject_string, '\t', '\t\t') for subject_string in subject_strings]
        outstring += '\t '.join(subject_strings)
        return outstring



