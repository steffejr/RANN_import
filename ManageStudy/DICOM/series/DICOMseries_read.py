from collections import defaultdict
import os
import re
import csv
import dicom as pydicom
from DICOMseries_info import DICOMseries_info as DICOMseries
from ManageStudy.ManageStudyErrors.SortErrors import MergeSeriesError, FindUnsortedSeriesError, FindcheeSeriesError
from ManageStudy.DICOM.dcm4che2wrapper.dcmqr import dcmqr
from ManageStudy.DICOM.dcm4che2wrapper.dcm2txt import dcm2txt

class DICOMseries_read(object):

    def __init__(self, study, DICOMseries2study_subid, DICOMseries2study_visid, DICOMseries2study_series_types, assign_series, dcmqr_args_list):
        self.study = study
        self.DICOMseries2study_subid = DICOMseries2study_subid
        self.DICOMseries2study_visid = DICOMseries2study_visid
        self.DICOMseries2study_series_types = DICOMseries2study_series_types
        self.assign_series = assign_series

        self.dcmqr_args_list = dcmqr_args_list
        print "\tLoading Chee Series"
        chee_series_list = self.load_chee_series_list(self.dcmqr_args_list)
        print "\tLoading Unsorted Series"
        unsorted_series = self.load_unsorted_series()
        print "\tLoading Sorted Series"
        sorted_series = self.load_sorted_series()
        series_list = [unsorted_series, sorted_series] + chee_series_list
        print "\tMerging Dictionaries"
        self.merged_series = self.merge_dictionaries(series_list)
        print "\tAssigning Series Types"
        self.assign_series_types()
        print "\tAssigning Series"
        self.assign_series(self)



    @staticmethod
    def series_info_dict_2_csv(csv_dict, path):
        with open(path, 'wb') as csv_file:
            series_info_writer = csv.writer(csv_file, delimiter=r',', quotechar=r'"', quoting=csv.QUOTE_MINIMAL)
            series_info_writer.writerow(['subid',
                                         'visid',
                                         'PatientsName',
                                         'series',
                                         'series#',
                                         'SeriesDescription',
                                         'SeriesInstanceUID',
                                         'StudyInstanceUID',
                                         'BirthDate[Year]',
                                         'VisitDateTime',
                                         'SeriesDateTime',
                                         'Modality',
                                         'Number of Instances',
                                         'Unsorted DICOMS',
                                         'Sorted DICOMS',
                                         'Matched Series Types'])
            for key1 in csv_dict.iterkeys():
                for key2 in csv_dict[key1].iterkeys():
                    for key3 in csv_dict[key1][key2].iterkeys():
                        series_info_item = csv_dict[key1][key2][key3]
                        series_info_writer.writerow([series_info_item.subid,
                                             series_info_item.visid,
                                             series_info_item.PatientsName,
                                             series_info_item.series,
                                             series_info_item.SeriesNumber,
                                             series_info_item.SeriesDescription,
                                             series_info_item.SeriesInstanceUID,
                                             series_info_item.StudyInstanceUID,
                                             series_info_item.BirthDate.year,
                                             series_info_item.VisitDateTime,
                                             series_info_item.SeriesDateTime,
                                             series_info_item.Modality,
                                             series_info_item.number_of_instances,
                                             len(series_info_item.unsorted_dicom_paths),
                                             series_info_item.sorted_files,
                                             ' '.join([x.name for x in series_info_item.DICOMseries_types.values()])
                            ])
    @staticmethod
    def series_info_list_2_csv(series_list, path):
        with open(path, 'wb') as csv_file:
            series_info_writer = csv.writer(csv_file, delimiter=r',', quotechar=r'"', quoting=csv.QUOTE_MINIMAL)
            series_info_writer.writerow(['subid',
                                         'visid',
                                         'PatientsName',
                                         'series',
                                         'series#',
                                         'SeriesDescription',
                                         'SeriesInstanceUID',
                                         'StudyInstanceUID',
                                         'BirthDate[Year]',
                                         'VisitDateTime',
                                         'SeriesDateTime',
                                         'Modality',
                                         'Number of Instances',
                                         'Unsorted DICOMS',
                                         'Sorted DICOMS',
                                         'Matched Series Types'])
            for series_info_item in series_list:
                series_info_writer.writerow([series_info_item.subid,
                                             series_info_item.visid,
                                             series_info_item.PatientsName,
                                             series_info_item.series,
                                             series_info_item.SeriesNumber,
                                             series_info_item.SeriesDescription,
                                             series_info_item.SeriesInstanceUID,
                                             series_info_item.StudyInstanceUID,
                                             series_info_item.BirthDate.year,
                                             series_info_item.VisitDateTime,
                                             series_info_item.SeriesDateTime,
                                             series_info_item.Modality,
                                             series_info_item.number_of_instances,
                                             len(series_info_item.unsorted_dicom_paths),
                                             series_info_item.sorted_files,
                                             ' '.join([x.name for x in series_info_item.DICOMseries_types.values()])
                                             ])


    def assign_series_types(self):
        series_dict = self.merged_series
        for key1 in series_dict.iterkeys():
            for key2 in series_dict[key1].iterkeys():
                for key3 in series_dict[key1][key2].iterkeys():
                    self.DICOMseries2study_series_types(series_dict[key1][key2][key3])



    def load_unsorted_series(self, H_REC=re.compile('^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+\.[0-9]+\.[0-9]+)\.([0-9]+\.[0-9]+\.[0-9]+)$')):
        DICOMseries_dict = defaultdict(lambda: defaultdict(dict))
        dicomlist = os.listdir(self.study.config.incoming_DICOM_dir)
        header_dict = {}
        otherdicoms = []
        dicom_reader = dcm2txt()
        for dicom in dicomlist:
            if dicom.find('part') != -1: #skip files in transit
                continue
            result = H_REC.match(dicom)
            if result != None:
                tupple = result.groups()
                if tupple[1] == r'5.24.5':
                    dicompath = os.path.join(self.study.config.incoming_DICOM_dir, dicom)
                    try:
                        pydicomobject = pydicom.read_file(dicompath, stop_before_pixels=True)
                        dicom_series = DICOMseries.cls_from_pydicom(pydicomobject)
                    except NotImplementedError:
                        series_dict = dicom_reader.make_dict(dicompath)
                        dicom_series = DICOMseries.cls_from_dict(series_dict)
                    dicom_series.subid = self.DICOMseries2study_subid(dicom_series)
                    dicom_series.visid = self.DICOMseries2study_visid(dicom_series)
                    dicom_series.unsorted_dicom_paths.append(dicompath)
                    key = tupple[0] + tupple[2]
                    header_dict[key] = (tupple[0], tupple[1], tupple[2], dicom_series.subid, dicom_series.visid, dicom_series.SeriesInstanceUID)

                    if dicom_series.SeriesInstanceUID not in DICOMseries_dict[dicom_series.subid][dicom_series.visid]:
                        DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID] = dicom_series

                    elif dicom_series.is_same_series(DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID]):
                        DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID].unsorted_dicom_paths.append(dicompath)

                    else:
                        raise FindUnsortedSeriesError(dicom_series, DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID])
                    continue
            otherdicoms.append(dicom)
        numloading = 0
        for dicom in otherdicoms:
            numloading = numloading + 1
            if numloading % 200 == 0:
                print "\t\tnumloading: {}".format(numloading)
            dicompath = os.path.join(self.study.config.incoming_DICOM_dir, dicom)
            result = H_REC.match(dicom)
            if result != None:
                tupple = result.groups()
                key = tupple[0] + tupple[2]
                if (key) in header_dict:
                    tupple = header_dict[key]
                    DICOMseries_dict[tupple[3]][tupple[4]][tupple[5]].unsorted_dicom_paths.append(dicompath)
                    continue
            try:
                pydicomobject = pydicom.read_file(dicompath, stop_before_pixels=True)
                dicom_series = DICOMseries.cls_from_pydicom(pydicomobject)
            except Exception:
                series_dict = dicom_reader.make_dict(dicompath)
                dicom_series = DICOMseries.cls_from_dict(series_dict)
            dicom_series.subid = self.DICOMseries2study_subid(dicom_series)
            dicom_series.visid = self.DICOMseries2study_visid(dicom_series)
            dicom_series.unsorted_dicom_paths.append(dicompath)

            if dicom_series.SeriesInstanceUID not in DICOMseries_dict[dicom_series.subid][dicom_series.visid]:
                DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID] = dicom_series
            elif dicom_series.is_same_series(DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID]):
                DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID].unsorted_dicom_paths.append(dicompath)
            else:
                raise FindUnsortedSeriesError(dicom_series, DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID])

        return DICOMseries_dict

    def load_chee_series_list(self, dcmqr_args_list):
        out_dict_list = []
        for dcmqr_args in dcmqr_args_list:
            out_dict_list.append(self.load_chee_series(dcmqr_args))
        return out_dict_list

    def load_chee_series(self, dcmqr_args):
        DICOMseries_dict = defaultdict(lambda: defaultdict(dict))
        gen = dcmqr.series_generator(dcmqr_args)
        for dicom_series in gen:
            dicom_series.subid = self.DICOMseries2study_subid(dicom_series)
            dicom_series.visid = self.DICOMseries2study_visid(dicom_series)
            if dicom_series.SeriesInstanceUID not in DICOMseries_dict[dicom_series.subid][dicom_series.visid]:
                DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID] = dicom_series
            else:
                raise FindcheeSeriesError(dicom_series, DICOMseries_dict[dicom_series.subid][dicom_series.visid][dicom_series.SeriesInstanceUID])
        return DICOMseries_dict

    def load_sorted_series(self, read_dicom_headers=False):
        DICOMseries_dict = defaultdict(lambda: defaultdict(dict))
        for index in self.study.IndexList:
            for subject in index.subjectlist:
                for visit in subject.visitlist:
                    
                    if subject.subid == "P00004580" and visit.visid == "S0001":
                        print "Debug!!"
                    
                    for dicom_image in visit.dicomlist:
                        for dicom_folder in dicom_image.series_folder_list:
                            if read_dicom_headers == True:
                                dicom_series = dicom_folder.load_DICOMseries_using_headers()
                            else:
                                dicom_series = dicom_folder.load_DICOMseries()
                            
                            if dicom_series != None:
                                DICOMseries_dict[subject.subid][visit.visid][dicom_series.SeriesInstanceUID] = dicom_series
        return DICOMseries_dict


    def merge_dictionaries(self, dict_list, prune_paths=False):
        merged_dict = defaultdict(lambda: defaultdict(dict))
        for DICOMseries_dict in dict_list:
            for key1 in DICOMseries_dict.iterkeys():
                for key2 in DICOMseries_dict[key1].iterkeys():
                    for key3 in DICOMseries_dict[key1][key2].iterkeys():
                        if key3=="1.3.46.670589.11.17184.5.0.8892.20120330161438986131":
                            print "Debug!"
                        
                        if key3 in merged_dict[key1][key2]:
                            if merged_dict[key1][key2][key3].is_same_series(DICOMseries_dict[key1][key2][key3]):
                                merged_dict[key1][key2][key3].merge_info(DICOMseries_dict[key1][key2][key3], prune_paths)
                            else:
                                raise MergeSeriesError(merged_dict[key1][key2][key3], DICOMseries_dict[key1][key2][key3], "Error: two entries to be merged are not from the same series")
                        else:
                            merged_dict[key1][key2][key3] = DICOMseries_dict[key1][key2][key3]
        return merged_dict

