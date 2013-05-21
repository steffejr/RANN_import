import os
import dicom
from DICOMseries_info import DICOMseries_info as DICOMseries
import dicom as pydicom
from collections import defaultdict
import re
import pdb
from ManageStudy.DICOM.dcm4che2wrapper.dcm2txt import dcm2txt
#A DICOM series folder, in this case, is actual a folder containing the dicoms.
#It retains a count of the number of dicoms, in addition to it's other functionality


import pdb;

class DICOMseries_folder(object):

    def __init__(self, image, name):        
        self.image = image
        self.name = name
        self.path = os.path.join(image.path, name)
        namesplit = name.capitalize().replace('X', '').replace('R', '').split('_')
        #pdb.set_trace()
        self.SeriesInstanceUID = namesplit[1]
        self.bad = True
        if name.capitalize().find('X') == -1:
            self.bad = False
        self.manual_recon = True
        if name.capitalize().find('R') == -1:
            self.manual_recon = False
        self.SeriesNumber = int(namesplit[0])
        
        dicomlist = os.listdir(self.path)
        self.numdicoms = len(dicomlist)

    def recount_dicoms(self):
        dicomlist = os.listdir(self.path)
        self.numdicoms = len(dicomlist)

    def __str__(self):
        outstring = 'DICOM: {0.numdicoms:,>4} files at {0.image.folder}{1}{0.image.filename}{1}{0.series_foldername}'.format(self, os.sep)
        return outstring

    def mark_bad(self):
        self.bad = True
        self.series_foldername = 'X' + self.series_foldername
        newpath = os.path.join(self.image.path, self.series_foldername)
        os.rename(self.path, newpath)
        self.path = newpath

    def mark_good(self):
        self.bad = False
        self.series_foldername = self.series_foldername.capitalize().replace('X', '')
        newpath = os.path.join(self.image.path, self.series_foldername)
        os.rename(self.path, newpath)
        self.path = newpath

    def load_DICOMseries(self):
        'returns a dicom_series_info object created with information from the directory structure without actually looking at the dicoms'
        dicomlist = os.listdir(self.path)
        self.numdicoms = len(dicomlist)
        dicom_series = DICOMseries(subid=self.image.visit.subject.subid, visid=self.image.visit.visid, series=self.image.series, sorted_files=self.numdicoms)
        dicom_series.SeriesInstanceUID = self.SeriesInstanceUID
        dicom_series.SeriesNumber = self.SeriesNumber
        return dicom_series


    def load_DICOMseries_using_headers(self, H_REC=re.compile('^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+\.[0-9]+\.[0-9]+)$')):
        'Load in one of the dicoms (prefering smaller ones) and use the information inside to construct a dicom_series_info object, which it returns'
        dicomlist = os.listdir(self.path)
        self.numdicoms = len(dicomlist)
        dicompath = None
        if self.numdicoms == 0:
            return None
        elif self.numdicoms == 2:
            for dicom in dicomlist:
                result = H_REC.match(dicom)
                if result != None:
                    tupple = result.groups()
                    if tupple[1] == r'5.24.5':
                        dicompath = os.path.join(self.path, dicom)
                        break
        if dicompath == None:
            dicompath = os.path.join(self.path, dicomlist[0])
        dicom_series = DICOMseries(subid=self.image.visit.subject.subid, visid=self.image.visit.visid, series=self.image.series, sorted_files=self.numdicoms)
        try:
            pydicomobject = pydicom.read_file(dicompath, stop_before_pixels=True)
            dicom_series.set_from_pydicom(pydicomobject)
        except Exception:
            dicom_reader = dcm2txt()
            series_dict = dicom_reader.make_dict(dicompath)
            dicom_series.set_from_dict(series_dict)
        if self.SeriesInstanceUID != dicom_series.SeriesInstanceUID:
            raise Exception, "File {0} does not have same SeriesInstanceUID as folder\n{1}".format(dicompath, self.path)
        if self.SeriesNumber != dicom_series.SeriesNumber:
            raise Exception, "File {0} does not have same SeriesNumber as folder\n{1}".format(dicompath, self.path)
        return dicom_series


