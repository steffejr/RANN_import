'''
The FS_Subject class represents one freesurfer subject folder.

.. moduleauthor:: Aleksey Orekhov <cruser42@gmail.com>

'''

import os.path

class FS_Subject:
    '''
    fs_study- Parent fs_study object

    fsID- what freesurfer calls the 'subjid'
    '''

    def __init__(self, fs_study, fsID):

        self.fs_study = fs_study
        self.fsID = fsID
        #: Path to freesurfer subject folder
        self.path = os.path.join(fs_study.subjects_dir, fsID)
        self.submitted_dir = os.path.join(fs_study.path, 'runs_freesurfer', 'submitted', self.fsID)
        self.done_dir = os.path.join(fs_study.path, 'runs_freesurfer', 'done', self.fsID)
        if not os.path.exists(self.submitted_dir):
            os.makedirs(self.submitted_dir, 0775)
        if not os.path.exists(self.done_dir):
            os.makedirs(self.done_dir, 0775)
        self.jobs_running = False
        self.read_processing_steps()


    def read_processing_steps(self):
        self.jobs = {}
        submitted_jobs = os.listdir(self.submitted_dir)
        for job in submitted_jobs:
            prefix = job.split('_')[0]
            self.jobs[prefix] = 'submitted'
            self.jobs_running = True
        done_jobs = os.listdir(self.done_dir)
        for job in done_jobs:
            prefix = job.split('_')[0]
            self.jobs[prefix] = 'done'

    def __str__(self):
        outstring = 'FS_Subject: %s\n' % self.fsID
        return outstring


