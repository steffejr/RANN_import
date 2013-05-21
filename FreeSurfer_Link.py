import os
import re
from ManageStudy.Study import Study
from ManageStudy.databin import databin
from ManageFreesurfer.FS_Study import FS_Study
from ManageFreesurfer.fsutils_wrapper.mri_convert import mri_convert
from FreeSurfer_helpers import fsID_from_visit
from Taub.FreeSurfer.Fetch_FS_Images import *

print "Reading RANN Study"
study = Study('/share/data/studies/RANN', 'RANN')
fs_study = FS_Study(root_dir='/share/data/studies/RANN/FreeSurfer', fs_home='/usr/local/freesurfer/5.1', fsIDRE=re.compile('[0-9]+_[0-9]+_RANN'))


def recon_subjects():
    global fs_study
    for fs_subject in fs_study.subjectlist:
        if not fs_subject.jobs_running and 'import' in fs_subject.jobs and 'all' not in fs_subject.jobs:
            fs_study.recon_all(fs_subject, 'all', '-all', 'This script does a full recon-all of all subjects')

def import_subjects(index):
    for subject in index.subjectlist:
        for visit in subject.visitlist:
            fsID = fsID_from_visit(visit)
            #fs_subject = fs_study.subjects[fsID]
            if fsID not in fs_study.subjects and "T1" in visit.niftis["T1"]:
                fs_study.importT1(fsID, visit.niftis["T1"]["T1"].path)






