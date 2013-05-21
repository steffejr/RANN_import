#class DICOM_import_error(Exception):
#    def __init__(self, source, dest='', description='DICOM_import_error'):
#        self.source = source
#        self.dest = dest
#        self.description = description
#    def __str__(self):
#        infostring = 'cannot import DICOM file:\n' + self.source
#        if self.dest != '':
#            infostring += "\ninto\n" + self.dest
#        if (self.description != 'DICOM_import_error'):
#            infostring += "\n" + self.description
#        return infostring
