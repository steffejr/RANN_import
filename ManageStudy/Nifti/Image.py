import os
from ..MedImage import MedImage
from ManageStudy.ManageStudyErrors import VisitErrors
#A NIfTI image, this adds two extensions (.nii,.nii.gz) to the MedImage class
#ToDo: more info (say from a call wrapper call to fslhd may be added)

class Image(MedImage):

    def __init__(self, visit, folder, filename):
        filenamesplit = filename.split('.')
        if filenamesplit[-1] == 'nii':
            self.extension = filenamesplit[-1]
            basename = '.'.join(filenamesplit[:-1])
        else:   #.nii.gz
            self.extension = '.'.join(filenamesplit[-2:])
            basename = '.'.join(filenamesplit[:-2])
        super(Image, self).__init__(visit=visit, folder=folder, filename=filename, basename=basename)

    def unlink(self, override=False):
        'Unlinks nii file specified by path, confirms first, override'
        if os.path.exists(self.path):
            if override == True:
                response = 'y'
            else:
                response = 'n'
                response = raw_input('Are you SURE that you want to delete %s ? (y/n)[n]: ' % self.path)
            if (response.lower() in ['y', 'yes']):
                os.unlink(self.path)
                return True
        else:
            raise VisitErrors.DeleteNiiError(niiname=self.path, description="File does not exist")

    def __str__(self):
        outstring = 'NIfTI: {0}\\{1}'.format(self.folder, self.filename)
        return outstring
