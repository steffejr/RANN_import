"""



"""

import os.path
import warnings
from Index import Index
from Project import Project
from ManageStudyErrors import StudyErrors
from Config.StudyConfig import StudyConfig

#===============================================================================
#===============================================================================

class Study(Project):
    '''a doc string!'''

    def __init__(self, path, name=''):
        '''The Study init routine'''
        self.name = name
        self.path = os.path.normpath(path)
        self.config = StudyConfig(self)
        self.load_indexes()
        self.incoming_DICOM_dir = os.path.join(self.path, self.config.incoming_DICOM_dir)
        self.subjectlist = self.Indexes[self.config.study_main].subjectlist
        self.subjects = self.Indexes[self.config.study_main].subjects
        self.study_main = self.Indexes[self.config.study_main]
        self.quarantine = self.Indexes[self.config.quarantine]
        self.excluded = self.Indexes[self.config.excluded]


    def __str__(self):
        outstring = 'Study: %s\n' % self.config.name
        for index in self.IndexList:
            outstring += "\t Index: " + index.config.name + "\n"
        return outstring

    def test_routine(self):
        "some doc info here"
        pass
