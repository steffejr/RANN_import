import os
import shutil
from ManageStudy.MedImage import MedImage
from series.DICOMseries_folder import DICOMseries_folder
#from ManageStudy.ManageStudyErrors.DICOMImageErrors import DICOM_import_error

class Image(MedImage):
    def __init__(self, visit, folder, filename):
        super(Image, self).__init__(visit=visit, folder=folder, filename=filename)
        self.find_series_folder_list()

    def find_series_folder_list(self):
        self.series_folder_list = []
        self.series_folders = {}
        folders = os.listdir(self.path)
        for folder in folders:
            series_folder = DICOMseries_folder(self, folder)
            self.series_folder_list.append(series_folder)
            self.series_folders[series_folder.SeriesInstanceUID] = series_folder

    def importDICOM(self, dicomlocation, series_info, override=False):
        if series_info.SeriesInstanceUID not in self.series_folders:
            folder_name = str(series_info.SeriesNumber) + '_' + series_info.SeriesInstanceUID
            os.makedirs(os.path.join(self.path, folder_name))
            series_folder = DICOMseries_folder(self, name=folder_name)
            self.series_folder_list.append(series_folder)
            self.series_folders[series_info.SeriesInstanceUID] = series_folder
        series_folder = self.series_folders[series_info.SeriesInstanceUID]
        destfile = (os.path.join(series_folder.path, os.path.basename(os.path.normpath(dicomlocation))))
        if (override == True) or not os.path.exists(destfile):
            shutil.copyfile(dicomlocation, destfile)
            return True
        else:
            print "File {} exists and override False".format(destfile)
            return False

    def __str__(self):
            outstring = 'Series: {0.folder}{1}{0.filename}'.format(self, os.sep)
            return outstring
