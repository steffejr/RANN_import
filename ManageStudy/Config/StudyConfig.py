from ProjectConfig import ProjectConfig
import ConfigErrors
import os.path
import re

#
#All paths except for path path are relative. pathpath and StudyConfig.path are full.
#

class StudyConfig(ProjectConfig):

    def __init__(self, study):
        '''Creates a ProjectConfig object which has parsed the study.cfg file usually located at $PROJECTDIR/Config/main.cfg and created
        
        ProjectConfig.indexes
        ProjectConfig.incoming_DICOM_dir
        as well as a parser object
        ProjectConfig.parser
        '''
        super(StudyConfig, self).__init__(project=study)

    def set_index_paths(self, indexes={'study_main':'Subjects', 'excluded':'ExcludedSubjects', 'quarantine':os.path.join('Quarantine', 'Subjects')}):
        '''Will set StudyConfig.indexes to defaults when invoked with no arguments. If provided with a hash, will update config file and StudyConfig.indexes
        values in the hash'''
        super(StudyConfig, self).set_index_paths(indexes)

    def update(self):
        super(StudyConfig, self).update()
        self.get_incoming_dicom_dir()
        self.get_study_indexes();

    def get_study_indexes(self):
        if self.parser.has_section('study indexes'):
            if self.parser.has_option('study indexes', 'study_main'):
                self.study_main = self.parser.get('study indexes', 'study_main')
                if self.study_main not in self.indexes:
                    raise ConfigErrors.BadIndexPathError('study_main', self.study_main)
            else:
                self.parser.set('study indexes', 'study_main', '')
                with open(self.path, 'wb') as StudyConfig:
                    self.parser.write(StudyConfig)
                raise ConfigErrors.MissingIndexError('study_main')
            if self.parser.has_option('study indexes', 'quarantine'):
                self.quarantine = self.parser.get('study indexes', 'quarantine')
                if self.quarantine not in self.indexes:
                    raise ConfigErrors.BadIndexPathError('quarantine', self.quarantine)
            else:
                self.parser.set('study indexes', 'quarantine', '')
                with open(self.path, 'wb') as StudyConfig:
                    self.parser.write(StudyConfig)
                raise ConfigErrors.MissingIndexError('excluded')
            if self.parser.has_option('study indexes', 'excluded'):
                self.excluded = self.parser.get('study indexes', 'excluded')
                if self.excluded not in self.indexes:
                    raise ConfigErrors.BadIndexPathError('excluded', self.excluded)
            else:
                self.parser.set('study indexes', 'excluded', '')
                with open(self.path, 'wb') as StudyConfig:
                    self.parser.write(StudyConfig)
                raise ConfigErrors.MissingIndexError('excluded')
        else:
            self.set_study_indexes()

    def set_study_indexes(self, study_main='study_main', quarantine='quarantine', excluded='excluded'):
        '''Set entries for study indexes in config file, should only be called'''
        self.parser.add_section('study indexes')
        self.parser.set('study indexes', 'study_main', study_main)
        self.parser.set('study indexes', 'quarantine', quarantine)
        self.parser.set('study indexes', 'excluded', excluded)

        with open(self.path, 'wb') as StudyConfig:
            self.parser.write(StudyConfig)
        self.study_main = study_main
        self.quarantine = quarantine
        self.excluded = excluded


    def get_incoming_dicom_dir(self):
        ''''''
        if self.parser.has_section('Quarantine'):
            if self.parser.has_option('Quarantine', 'incoming_DICOM_dir'):
                self.incoming_DICOM_dir = self.parser.get('Quarantine', 'incoming_DICOM_dir')
            else:
                print "Did not find Quarantine::incoming_DICOM_dir, setting defaults...."
                self.set_incoming_dicom_dir()
                return
        else:
            print "Did not find Quarantine, setting defaults...."
            self.set_incoming_dicom_dir()
        return

    def set_incoming_dicom_dir(self, incoming_DICOM_dir=os.path.join('Quarantine', 'IncomingDICOM')):
        ''''''
        if not self.parser.has_section('Quarantine'):
            self.parser.add_section('Quarantine')
        self.parser.set('Quarantine', 'incoming_DICOM_dir', incoming_DICOM_dir)
        with open(self.path, 'wb') as StudyConfig:
            self.parser.write(StudyConfig)
        self.incoming_DICOM_dir = incoming_DICOM_dir
        if not os.path.exists(self.incoming_DICOM_dir):
            os.makedirs(self.incoming_DICOM_dir)


