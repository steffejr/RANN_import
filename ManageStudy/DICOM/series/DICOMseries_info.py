import textwrap
import os
from datetime import datetime
from ManageStudy.ManageStudyErrors.SortErrors import MergeSeriesError, CreateSeriesError

class DICOMseries_info(object):

    def __init__(self, subid=None, visid=None, series=None, number_of_instances=None, sorted_files=None):
        self.subid = subid #get from dir structure or dcm4chee parse
        self.visid = visid #get from dir structure or dcm4chee parse
        self.PatientsName = None
        self.series = series
        self.sorted_files = sorted_files
        self.number_of_instances = number_of_instances
        self.unsorted_dicom_paths = []
        self.DICOMseries_types = {}
        self.VisitDateTime = None
        self.SeriesDateTime = None
        self.BirthDate = None
        self.SeriesInstanceUID = None
        self.StudyInstanceUID = None
        self.SeriesDescription = None
        self.Modality = None
        self.PatientsSex = None

    @property
    def BirthYear(self):
        if self.BirthDate == None:
            return None
        else:
            return self.BirthDate.year

    @classmethod
    def cls_from_pydicom(cls, pydicom):
        "Initialize MyData from a file"
        temp_DICOMseries = cls()
        temp_DICOMseries.set_from_pydicom(pydicom)
        return temp_DICOMseries

    @classmethod
    def cls_from_dict(cls, dicom_dict):
        temp_DICOMseries = cls()
        temp_DICOMseries.set_from_dict(dicom_dict)
        return temp_DICOMseries

    def set_from_pydicom(self, py_dicom):
        self.PatientsName = py_dicom.PatientsName
        try:
            self.SeriesDescription = py_dicom.SeriesDescription
        except AttributeError:
            self.SeriesDescription = None
        self.SeriesNumber = py_dicom.SeriesNumber

        if (not hasattr(py_dicom, 'StudyDate') or py_dicom.StudyDate == '') and (not hasattr(py_dicom, 'StudyTime') or py_dicom.StudyTime == ''):
            self.VisitDateTime = None
        elif (not hasattr(py_dicom, 'StudyDate') or py_dicom.StudyDate == '') :
            self.VisitDateTime = datetime.strptime("{:.6f}".format(py_dicom.StudyTime), '%H%M%S.%f')
        elif (not hasattr(py_dicom, 'StudyTime') or py_dicom.StudyTime == ''):
            self.VisitDateTime = datetime.strptime(py_dicom.StudyDate, '%Y%m%d')
        else:
            date_time = "{0}_{1:.6f}".format(py_dicom.StudyDate, float(py_dicom.StudyTime))
            self.VisitDateTime = datetime.strptime(date_time, '%Y%m%d_%H%M%S.%f')

        if (not hasattr(py_dicom, 'SeriesDate') or py_dicom.SeriesDate == '') and (not hasattr(py_dicom, 'SeriesTime') or py_dicom.SeriesTime == ''):
            self.SeriesDateTime = None
        elif (not hasattr(py_dicom, 'SeriesDate') or py_dicom.SeriesDate == '') :
            self.SeriesDateTime = datetime.strptime("{:.6f}".format(py_dicom.SeriesTime), '%H%M%S.%f')
        elif (not hasattr(py_dicom, 'SeriesTime') or py_dicom.SeriesTime == ''):
            self.SeriesDateTime = datetime.strptime(py_dicom.SeriesDate, '%Y%m%d')
        else:
            date_time = "{0}_{1:.6f}".format(py_dicom.SeriesDate, float(py_dicom.SeriesTime))
            self.SeriesDateTime = datetime.strptime(date_time, '%Y%m%d_%H%M%S.%f')

        if (not hasattr(py_dicom, 'PatientsBirthDate') or py_dicom.PatientsBirthDate == ''):
            self.BirthDate = None
        else:
            self.BirthDate = datetime.strptime(py_dicom.PatientsBirthDate, '%Y%m%d')

        if (not hasattr(py_dicom, 'PatientsSex') or py_dicom.PatientsSex == ''):
            self.PatientsSex = None
        else:
            self.PatientsSex = py_dicom.PatientsSex
        self.Modality = py_dicom.Modality
        self.SeriesInstanceUID = py_dicom.SeriesInstanceUID
        if self.SeriesInstanceUID == None:
            raise CreateSeriesError(self.SeriesInstanceUID, "SeriesInstanceUID == None")
        self.StudyInstanceUID = py_dicom.StudyInstanceUID

    def set_from_dict(self, dicom_dict):
        #make sure tests against none work later

        keylist = ['(0008,0020)', '(0008,0030)', '(0008,0021)', '(0008,0031)', '(0010,0030)', '(0010,0040)', '(0010,0010)', '(0008,103E)', '(0020,0011)', '(0008,0060)', '(0020,000E)', '(0020,000D)', '(0020,1209)']

        for key in keylist:
            if key not in dicom_dict or dicom_dict[key] == '':
                dicom_dict[key] = None


        if dicom_dict['(0008,0020)'] == None and dicom_dict['(0008,0030)'] == None:
            self.VisitDateTime = None
        elif dicom_dict['(0008,0020)'] == None :
            self.VisitDateTime = datetime.strptime("{:.6f}".format(dicom_dict['(0008,0030)']), '%H%M%S.%f')
        elif dicom_dict['(0008,0030)'] == None :
            self.VisitDateTime = datetime.strptime(dicom_dict['(0008,0020)'], '%Y%m%d')
        else:
            date_time = "{0}_{1:.6f}".format(dicom_dict['(0008,0020)'], float(dicom_dict['(0008,0030)']))
            self.VisitDateTime = datetime.strptime(date_time, '%Y%m%d_%H%M%S.%f')

        if dicom_dict['(0008,0021)'] == None and dicom_dict['(0008,0031)'] == None:
            self.SeriesDateTime = None
        elif dicom_dict['(0008,0021)'] == None :
            self.SeriesDateTime = datetime.strptime("{:.6f}".format(dicom_dict['(0008,0031)']), '%H%M%S.%f')
        elif dicom_dict['(0008,0031)'] == None :
            self.SeriesDateTime = datetime.strptime(dicom_dict['(0008,0021)'], '%Y%m%d')
        else:
            date_time = "{0}_{1:.6f}".format(dicom_dict['(0008,0021)'], float(dicom_dict['(0008,0031)']))
            self.SeriesDateTime = datetime.strptime(date_time, '%Y%m%d_%H%M%S.%f')

        if dicom_dict['(0010,0030)'] == None or dicom_dict['(0010,0030)'] == '':
            self.BirthDate = None
        else:
            self.BirthDate = datetime.strptime(dicom_dict['(0010,0030)'], '%Y%m%d')


        if dicom_dict['(0010,0040)'] == None or dicom_dict['(0010,0040)'] == '':
            self.PatientsSex = None
        else:
            self.PatientsSex = dicom_dict['(0010,0040)'].upper()



        self.PatientsName = dicom_dict['(0010,0010)']
        self.SeriesDescription = dicom_dict['(0008,103E)']
        self.SeriesNumber = int(dicom_dict['(0020,0011)'])
        self.Modality = dicom_dict['(0008,0060)']
        self.SeriesInstanceUID = dicom_dict['(0020,000E)']
        if self.SeriesInstanceUID == None:
            raise CreateSeriesError(self.SeriesInstanceUID, "SeriesInstanceUID == None")
        self.StudyInstanceUID = dicom_dict['(0020,000D)']

        if dicom_dict['(0020,1209)'] != None:
            self.number_of_instances = int(dicom_dict['(0020,1209)'])



    def chk_add_DICOMseries_type(self, series_type):
        if self.SeriesDescription == None:
            return
        if series_type.pattern_match(self.SeriesDescription, self.PatientsName):
            self.DICOMseries_types[series_type.name] = series_type

    def __str__(self):
        return textwrap.dedent((
            """\
            DICOMseries
            PatientsName: {0.PatientsName}
            subid: {0.subid}
            visid: {0.visid}
            series: {0.series}
            series#: {0.SeriesNumber}
            SeriesDescription: {0.SeriesDescription}
            SeriesInstanceUID: {0.SeriesInstanceUID}
            StudyInstanceUID: {0.StudyInstanceUID}
            BirthDate[Year]: {3}
            SeriesDateTime: {0.SeriesDateTime}
            Modality: {0.Modality}
            Number of Instances: {0.number_of_instances}
            Unsorted DICOMS: {1}
            Sorted DICOMS: {0.sorted_files}
            Matched Series Types: {2}
            """
            ).format(self, len(self.unsorted_dicom_paths), ' '.join([x.name for x in self.DICOMseries_types.values()]), self.BirthDate.year)
        )


    def delete_series_unsorted_files(self):
        for path in self.unsorted_dicom_paths:
            os.unlink(path)
        self.unsorted_dicom_paths = []

    def add_unsorted_dicom(self, path):
        self.unsorted_dicom_paths.append(path)

    def is_same_series(self, other_DICOMseries):
        if self.SeriesInstanceUID == other_DICOMseries.SeriesInstanceUID:
            return True
        return False

    def merge_info(self, other_DICOMseries, prune_paths=False):
        '''merges two series, preferring entries in provided item to self, default behavior is to merge unsorted. unsorted dicom paths lists are merged
        so only unique entries from both lists remain'''
        if self.SeriesInstanceUID != other_DICOMseries.SeriesInstanceUID:
            raise MergeSeriesError(self.SeriesInstanceUID, other_DICOMseries.SeriesInstanceUID, "There is no good reason for merging two series relating to two unique pieces of data and SeriesInstanceUID")
        if self.SeriesInstanceUID == None:
            raise MergeSeriesError(self.SeriesInstanceUID, other_DICOMseries.SeriesInstanceUID, "SeriesInstanceUID == None")

        self.subid = self.overwrite_merge_item(self.subid, other_DICOMseries.subid)
        self.visid = self.overwrite_merge_item(self.visid, other_DICOMseries.visid)
        self.series = self.overwrite_merge_item(self.series, other_DICOMseries.series)
        self.PatientsName = self.overwrite_merge_item(self.PatientsName, other_DICOMseries.PatientsName)
        self.SeriesDescription = self.overwrite_merge_item(self.SeriesDescription, other_DICOMseries.SeriesDescription)
        self.SeriesNumber = self.test_merge_item(self.SeriesNumber, other_DICOMseries.SeriesNumber)
        self.SeriesDateTime = self.test_merge_item(self.SeriesDateTime, other_DICOMseries.SeriesDateTime)
        self.VisitDateTime = self.test_merge_item(self.VisitDateTime, other_DICOMseries.VisitDateTime)
        self.BirthDate = self.test_merge_item(self.BirthDate, other_DICOMseries.BirthDate)
        self.PatientsSex = self.test_merge_item(self.PatientsSex, other_DICOMseries.PatientsSex)
        self.Modality = self.overwrite_merge_item(self.Modality, other_DICOMseries.Modality)

        self.sorted_files = self.test_merge_item(self.sorted_files, other_DICOMseries.sorted_files)
        self.number_of_instances = self.test_merge_item(self.number_of_instances, other_DICOMseries.number_of_instances)

        self.unsorted_dicom_paths.extend(other_DICOMseries.unsorted_dicom_paths)
        self.unsorted_dicom_paths = list(set(self.unsorted_dicom_paths))#we only want unique entries

        self.StudyInstanceUID = self.test_merge_item(self.StudyInstanceUID, other_DICOMseries.StudyInstanceUID)

        for key in other_DICOMseries.DICOMseries_types.iterkeys():  #merge keys, uses fact that they are drawn from same list
            if key not in self.DICOMseries_types:
                self.DICOMseries_types[key] = other_DICOMseries.DICOMseries_types[key]

        if prune_paths:
            self.prune_unsorted_paths()

    def prune_unsorted_paths(self):
        out_path_list = []
        for path in self.unsorted_dicom_paths:
            if os.path.exists(path):
                out_path_list.append(path)
        return out_path_list

    @staticmethod
    def overwrite_merge_item(item, other_item):
        'merge items, overwriting when available'
        if other_item == None:
            return item
        else:
            return other_item


    @staticmethod
    def test_merge_item(item, other_item):
        'merge items if equal, or if one is None, else error'
        if item == other_item:
            return item
        elif item == None:
                return other_item
        elif other_item == None:
            return item
        else:
            print "Error in test_merge_item, items not equal and not null"
            raise AttributeError

