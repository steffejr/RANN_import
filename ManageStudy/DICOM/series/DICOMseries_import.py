import os
from DICOMseries_check import DICOMseries_check
from DICOMseries_sort import DICOMseries_sort
class DICOMseries_import(object):

    def __init__(self, dicom_series_sort, dcmqr_object):
        self.dicom_series_read = dicom_series_sort.dicom_series_read
        self.dicom_series_check = dicom_series_sort.dicom_series_check
        self.dicom_series_sort = dicom_series_sort
        self.dcmqr_object = dcmqr_object
        self.study = dicom_series_sort.study


    def import_dicoms(self):
        merged_series = self.dicom_series_read.merged_series
        for subid in merged_series.iterkeys():
            for visid in merged_series[subid].iterkeys():
                print "Importing {} {}".format(subid,visid)

                for SIU in merged_series[subid][visid].iterkeys():
                    dicom_series_info = merged_series[subid][visid][SIU]
                    if self.dicom_series_check.check_against_ref(dicom_series_info):
                        self.import_dicom_series(dicom_series_info)
                        self.dicom_series_sort.sort_dicoms(reload_incoming=True, override=True)
        self.wipe_part_files()


    def import_dicom_series(self, dicom_series_info):
        if dicom_series_info.subid == None or dicom_series_info.visid == None or dicom_series_info.series == None:
            return
        chee_instances = 0 if (dicom_series_info.number_of_instances == None) else dicom_series_info.number_of_instances
        local_sorted_instances = 0 if (dicom_series_info.sorted_files == None) else dicom_series_info.sorted_files
        local_unsorted_instances = len(dicom_series_info.unsorted_dicom_paths)
        if chee_instances > (local_sorted_instances):
            print "importing {3.subid} {3.visid} {3.series} chee_instances: {0} sorted {1}, unsorted {2}".format(chee_instances, local_sorted_instances, local_unsorted_instances, dicom_series_info)
            self.dcmqr_object.cmove_series_instance(dicom_series_info)


    def wipe_part_files(self):
        incoming_files = os.listdir(self.study.config.incoming_DICOM_dir)
        for incoming_file in incoming_files:
            if file[-5:] == '.part':
                fullpath = os.path.join(self.study.config.incoming_DICOM_dir, incoming_file)
                os.unlink(fullpath)
