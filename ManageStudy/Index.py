import os.path
import warnings
import string
import shutil
from Config.IndexConfig import IndexConfig
from Subject import Subject
from ManageStudyErrors import StudyErrors

class Index(object):


    def __init__(self, project, name, path, config_path):
        self.name = name
        self.project = project
        self.path = path
        self.config = IndexConfig(self, config_path)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.nonconformingniilist = []
        self.nonconformingdicomlist = []
        self.find_subjects()

    def find_subjects(self):
        '''takes subjects_dir and returns a list and hash of subject objects for all the folders inside 
        as (subjectlist,subjectdict)=__findSubjects__(subjects_dir)'''

        try:
            subjectFiles = os.listdir(self.path)
        except:
            warnings.warn("\nCould not list files in: " + self.path)
            return

        self.subjectlist = []
        self.subjects = {}

        for file in subjectFiles:
            fulldir = os.path.join(self.path, file)
            if (not os.path.isdir(fulldir)):
                continue
            m = self.config.__subjectfolderREC__.match(file)
            if m:
                newsubject = Subject(self, m.group(0))
            else:
                raise Exception('Index: ' + self.config.name + ' at location ' + self.path + '\nCould not parse subject ' + fulldir + '\nShould it be in this directory?\n')
            self.subjectlist.append(newsubject)
            self.subjects[newsubject.subid] = newsubject

    def add_subjects(self, subids, warn):
        for subid in subids:
            self.add_subject(subid, warn)

    def add_subject(self, subid, warn=False):
        m = self.config.__subjectfolderREC__.match(subid)
        if not m:
            warnings.warn(self.name + '::Did not create subject with subid ' + subid + '\n::Subject Regex did not match.\n' + 'Regex:: ' + self.config.__subjectfolderRE__)
            return False
        elif subid not in self.subjects:
            newsubject = Subject(self, subid)
            self.subjectlist.append(newsubject)
            self.subjects[newsubject.subid] = newsubject
            return True
        elif warn == True:
            warnings.warn('Did not create subject with subid ' + subid + '::Already Exists.')
            return False

    @staticmethod
    def unlink_subject(subject, override=False):
        '''archives and removes a subject dir'''
        if os.path.exists(subject.path):
            if override == True:
                response = 'y'
            else:
                response = 'n'
                response = raw_input('Are you SURE that you want to delete %s ? (y/n)[n]: ' % subject.path)
            if (response.lower() in ['y', 'yes']):
                shutil.rmtree(subject.path)
                return True
        else:
            raise StudyErrors.DeleteSubjectError(subid=subject.subid, description="Directory does not exist")
            return False

    def wipe_nonconforming_niis(self):
        if (raw_input("Are you sure? (YES/NO): ") == 'YES'):
            for niftipath in self.nonconformingniilist:
                print "Deleting %s" % niftipath
                os.unlink(niftipath)
            self.nonconformingniilist = []

    def __str__(self):
        outstring = 'Index: {}\n\t'.format(self.config.name)
        subject_text = '\n\t'.join([x.__str_concise__().replace('\n', '\n\t') for x in self.subjectlist])
#        for subject in self.subjectlist:
#            outstring += subject.__str__().replace('\n', '\n\t')

#        if len(self.nonconformingniilist) > 0:
#            outstring += "WARNING: Nonconforming NIfTI File Names Found\n"
#            outstring += '\n\t'.join(self.nonconformingniilist) + '\n'
#        if len(self.nonconformingdicomlist) > 0:
#            outstring += "\nWARNING: Nonconforming DICOM Folder Names Found\n"
#            outstring += '\n\t'.join(self.nonconformingdicomlist) + '\n'
        return outstring + subject_text

    def load_DICOMseries(self):
        DICOMseries_list = []
        for subject in self.subjectlist:
            DICOMseries_list.extend(subject.load_DICOMseries())
        return DICOMseries_list
