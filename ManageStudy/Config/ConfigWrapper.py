import os.path
import string
from ConfigParser import SafeConfigParser

class ConfigWrapper(object):

    def __init__(self, path):
        '''Creates a object which parsed the file 'path' and created Config.parser'''
        self.path = os.path.normpath(path)
        self.name = string.replace(os.path.basename(os.path.normpath(path)), '.cfg' , '')
        configdir = os.path.dirname(self.path)
        if not os.path.exists(configdir):
            os.makedirs(configdir)
        if not os.path.exists(self.path): #create config file if it doesn't exist
            f = open(self.path, 'w')
            f.close()
        self.update();


    def update(self):
        'Reparses the file to have the latest information. Will replace current parser so save changes beforehand'
        self.parser = SafeConfigParser()
        confighandle = open(self.path, 'r')
        self.parser.readfp(confighandle, self.path)
        confighandle.close()

