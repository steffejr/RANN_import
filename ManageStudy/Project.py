import os.path
import warnings
from Index import Index
from ManageStudyErrors import StudyErrors
from Config.ProjectConfig import ProjectConfig

#===============================================================================
#===============================================================================

class Project(object):

    def __init__(self, path, name=''):
        self.name = name
        self.path = os.path.normpath(path)
        self.config = ProjectConfig(self)
        self.Indexes = {}
        self.IndexList = []
        self.load_indexes()

    def load_indexes(self):
        'adds indexes specified in the Config/study.cfg file'
        #This is a list of objects, NOT directories. A list of directories is in self.MainConfig
        self.Indexes = {}
        self.IndexList = []
        for index_name, index_path in self.config.indexes.iteritems():
            index_path = os.path.join(self.path, index_path)
            config_path = os.path.join(self.path, 'Config', 'Indexes', index_name + '.cfg')
            self.Indexes[index_name] = Index(self, index_name, index_path, config_path)
            self.IndexList.append(self.Indexes[index_name])

    def __str__(self):
        outstring = 'Project: %s\n' % self.config.name
        for index in self.IndexList:
            outstring += "\t Index: " + index.config.name + "\n"
        return outstring


