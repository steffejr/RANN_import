#!/usr/local/aleksey/epd/epd7_3_1/bin/python
import os
import sys
import re
from FS_Study import FS_Study


Usage = 'Usage: pyrecon-all -prefix <prefix> <recon-all args here>'



#if no recon-all args given, print recon-all help text
if len(sys.argv) <= 3:
    print Usage
    print "\n************ recon-all usage ************"
    os.system('recon-all')
    exit(1)

if sys.argv[1] != '-prefix':
    print Usage
    exit(1)
else:
    prefix = sys.argv[2]

#get subjid
fsID = ''
subj_argnum = -1
for i in range(0,len(sys.argv)):
    if sys.argv[i] == '-subjid':
        subj_argnum = i
	break
fsID = sys.argv[subj_argnum+1]
del sys.argv[subj_argnum+1]
del sys.argv[subj_argnum]
FREESURFER_HOME = os.environ['FREESURFER_HOME']
SUBJECTS_DIR = os.environ['SUBJECTS_DIR']
ROOT_DIR = os.path.dirname(os.path.normpath(SUBJECTS_DIR))
fs_study = FS_Study(root_dir=ROOT_DIR, fs_home=FREESURFER_HOME,fsIDRE=re.compile('.*'),subjects_dir=SUBJECTS_DIR )

if fsID not in fs_study.subjects:
    fs_study.__addsubject__(fsID)
fs_subject = fs_study.subjects[fsID]

if not fs_subject.jobs_running:
    fs_study.recon_all(fs_subject, prefix, ' '.join(sys.argv[3:]))
else:
    print "could not submit job, there is a job already running for this subject, look in {} for the job".format(fs_subject.submitted_dir)

