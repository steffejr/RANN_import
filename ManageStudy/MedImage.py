import os.path
import shutil

class MedImage(object):

    def __init__(self, visit, folder, filename, basename=None):
        self.visit = visit
        self.folder = folder
        self.basename = basename;
        if (basename == None):
            self.basename = filename.split('.')[0]
        self.series = self.basename.replace('_' + self.visit.subject.subid + '_' + self.visit.visid , '')
        self.filename = filename
        self.path = os.path.join(self.visit.path, self.folder, self.filename)
        folder_path = os.path.join(self.visit.path, self.folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, 0775)



    def __str__(self):
        outstring = 'Image: %s\\%s\n' % (self.folder, self.filename)
        return outstring

