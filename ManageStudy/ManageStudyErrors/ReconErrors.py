class Wrong_Number_Of_Files_Error(Exception):
    def __init__(self, location, description='Wrong Number of files'):
        self.location = location
        self.description = description
    def __str__(self):
        infostring = 'cannot recon nii files at:\n{0.location}\n{0.description}'.format(self)
        return infostring

class Bad_Nifti_Error(Exception):
    def __init__(self, location, description='Bad Nifti Error'):
        self.location = location
        self.description = description
    def __str__(self):
        infostring = 'cannot recon nii files at:\n{0.location}\n{0.description}'.format(self)
        return infostring
