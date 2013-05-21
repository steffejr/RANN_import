from ConfigWrapper import ConfigWrapper
import os.path
import re

#
#All paths except for path path are relative. pathpath and ProjectConfig.path are full.
#

class ProjectConfig(ConfigWrapper):

    def __init__(self, project):
        self.path = os.path.join(project.path, 'Config', project.name + '.cfg')
        '''Creates a ProjectConfig object which has parsed the main.cfg file usually located at $PROJECTDIR/Config/main.cfg and created
        
        ProjectConfig.indexes
        ProjectConfig.incoming_DICOM_dir
        as well as a parser object
        ProjectConfig.parser
        '''
        super(ProjectConfig, self).__init__(path=self.path)

    def update(self):
        '''Reparses the file to have the latest information. Will replace current parser so save changes beforehand.
        Also fetches ProjectConfig Globals from Config File'''
        super(ProjectConfig, self).update()
        self.get_index_paths()


    def get_index_paths(self):
        'Updates ProjectConfig with locations of indexes for this study. Uses defaults on failure to locate entry in config file'
        if self.parser.has_section('indexes'):
            index_tuples = self.parser.items('indexes')
            self.indexes = {}
            for index in index_tuples:
                self.indexes[index[0]] = os.path.normpath(index[1])
            self.primarysubjectsdir = index_tuples[0][0]
        else:
            print "Couldn't find Section '{0}' in {1}..creating...".format('indexes', self.path)
            self.set_index_paths()



    #############################################################################
    ##The Set Routines Below should really only be used to set the defaults...###
    #############################################################################

    def set_index_paths(self, indexes={'project_main':'Subjects'}):
        """Will set ProjectConfig.indexes to defaults when invoked with no arguments. If provided with a hash, will update config file and ProjectConfig.indexes
        values in the hash. Has formatted as indexes={'name':'path','name':'path'} Path can be relative to project root or absolute"""
        self.parser.remove_section('indexes') # to wipe all existing entries
        self.parser.add_section('indexes')
        for k, v in indexes.iteritems():
            self.parser.set('indexes', k, v)
        with open(self.path, 'wb') as ProjectConfig:
            self.parser.write(ProjectConfig)
        self.indexes = indexes





