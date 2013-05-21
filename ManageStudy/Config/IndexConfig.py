from ConfigWrapper import ConfigWrapper
import re
#
#All paths except for configfile path are relative. configfilepath and IndexConfig.path are full.
#

class IndexConfig(ConfigWrapper):

    def __init__(self, index, config_path):
        '''Creates a IndexConfig object which has parsed the <index>.cfg file at config_path 
        
        IndexConfig.__subjectfolderRE__
        IndexConfig.__subjectfolderREC__
        IndexConfig.__visitfolderRE__
        IndexConfig.__visitfolderREC__
        IndexConfig.__ignoredirlist__

        as well as a parser object
        IndexConfig.parser
        
        '''
        super(IndexConfig, self).__init__(path=config_path)


    def update(self):
        '''Reparses the file to have the latest information. Will replace current parser so save changes beforehand.
        Also fetches IndexConfig Globals from Config File'''
        super(IndexConfig, self).update()
        self.get_subject_folder_RE()
        self.get_visit_folder_RE()
        self.get_excluded_visit_folders()

    def get_subject_folder_RE(self):
        'Updates IndexConfig with Subject folder Regex from study.cfg'
        if self.parser.has_option('Subject', 'subjectfolderRE_list'):
            self.__subjectfolderRE_list__ = self.parser.get('Subject', 'subjectfolderRE_list').rstrip(',').split(',')
            self.__subjectfolderRE_list__ = [x.strip('"') for x in self.__subjectfolderRE_list__]
            self.__subjectfolderRE__ = '|'.join(self.__subjectfolderRE_list__)
            self.__subjectfolderREC__ = re.compile(self.__subjectfolderRE__)
        else:
            print "Couldn't find Section {0} with option {1} in {2}..setting defaults...".format('Subject', 'subjectfolderRE_list', self.path)
            self.set_subject_folder_RE()

    def get_visit_folder_RE(self):
        'Updates IndexConfig with visit folder Regex from study.cfg'
        if self.parser.has_option('Visit', 'visitfolderRE_list'):
            self.__visitfolderRE_list__ = self.parser.get('Visit', 'visitfolderRE_list').rstrip(',').split(',')
            self.__visitfolderRE_list__ = [x.strip('"') for x in self.__visitfolderRE_list__]
            self.__visitfolderRE__ = '|'.join(self.__visitfolderRE_list__)
            self.__visitfolderREC__ = re.compile(self.__visitfolderRE__)
        else:
            print "Couldn't find Section {0} with option {1} in {2}..setting defaults...".format('visit', 'visitfolderRE_list', self.path)
            self.set_visit_folder_RE()

    def get_excluded_visit_folders(self):
        'Updates IndexConfig with list of folders to ignore in the subjectsdir when looking for Niftis'
        if self.parser.has_option('Visit', 'IgnoreDirList'):
            self.__ignoredirlist__ = self.parser.get('Visit', 'IgnoreDirList').rstrip(',').split(',')
            self.__ignoredirlist__ = [x.strip('"') for x in self.__ignoredirlist__]
        else:
            print "Couldn't find Section {0} with option {1} in {2}..setting defaults...".format('visit', 'IgnoreDirList', self.path)
            self.set_excluded_visit_folders()

    #############################################################################
    ##The Set Routines Below should really only be used to set the defaults...###
    #############################################################################



    def set_subject_folder_RE(self, subjectfolderRE_list=['P[0-9]+']):
        '''Will set IndexConfig.subjectfolderRE_list and IndexConfig.subjectfolderREC_list to defaults when invoked with no arguments. If provided with a regex, will update config file and
        two regex values mentioned'''
        self.__subjectfolderRE_list__ = subjectfolderRE_list
        self.__subjectfolderRE__ = '|'.join(self.__subjectfolderRE_list__)
        self.__subjectfolderREC__ = re.compile(self.__subjectfolderRE__)
        if not self.parser.has_section('Subject'):
            self.parser.add_section('Subject')
        subjectfolderRE_list = ['"' + x + '"' for x in subjectfolderRE_list]
        self.parser.set('Subject', 'subjectfolderRE_list', ','.join(subjectfolderRE_list))
        with open(self.path, 'wb') as IndexConfig:
            self.parser.write(IndexConfig)

    def set_visit_folder_RE(self, visitfolderRE_list=['S[0-9]+']):
        '''Will set IndexConfig.__visitfolderRE_list__ and IndexConfig.__visitfolderREC_list__ to defaults when invoked with no arguments. If provided with a regex, will update config file and
        two regex values mentioned'''
        self.__visitfolderRE_list__ = visitfolderRE_list
        self.__visitfolderRE__ = '|'.join(self.__visitfolderRE_list__)
        self.__visitfolderREC__ = re.compile(self.__visitfolderRE__)
        if not self.parser.has_section('Visit'):
            self.parser.add_section('Visit')
        visitfolderRE_list = ['"' + x + '"' for x in visitfolderRE_list]
        self.parser.set('Visit', 'visitfolderRE_list', ','.join(visitfolderRE_list))
        with open(self.path, 'wb') as IndexConfig:
            self.parser.write(IndexConfig)


    def set_excluded_visit_folders(self, ignoredirlist=['DICOM', 'Log', 'Quarantine']):
        '''Will set IndexConfig.__ignoredirlist__ to defaults with no arguments, or values in provided list'''
        self.__ignoredirlist__ = ignoredirlist
        if not self.parser.has_section('Visit'):
            self.parser.add_section('Visit')
        ignoredirlist = ['"' + x + '"' for x in ignoredirlist]
        self.parser.set('Visit', 'IgnoreDirList', ','.join(ignoredirlist))
        with open(self.path, 'wb') as IndexConfig:
            self.parser.write(IndexConfig)






