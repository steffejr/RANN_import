import os

class DICOMseries_sort(object):

    def __init__(self, dicom_series_read, dicom_series_check):
        self.dicom_series_read = dicom_series_read
        self.dicom_series_check = dicom_series_check
        self.study = dicom_series_read.study

    def sort_dicoms(self, reload_incoming=True, override=False):
        '''Goes through every series and runs 'sort_series' on it. Optionally reloads unsorted before operation. Updates related dicom_read afterwards.
        Override parameter passed to eventual visit.importDICOM routine. If unsorted files don't pass check, deletes them'''
        if reload_incoming:
            unsorted_series = self.dicom_series_read.load_unsorted_series()
            merged_series = self.dicom_series_read.merge_dictionaries([unsorted_series, self.dicom_series_read.merged_series], prune_paths=True)

        for key1 in merged_series.iterkeys():
            for key2 in merged_series[key1].iterkeys():
                for key3 in merged_series[key1][key2].iterkeys():
                    series_info = merged_series[key1][key2][key3]
                    if len(series_info.unsorted_dicom_paths) > 0 and self.dicom_series_check.check_against_ref(series_info):
                        merged_series[key1][key2][key3] = self.sort_series(series_info, override)
                    else:
                        merged_series[key1][key2][key3].delete_series_unsorted_files()
        self.dicom_series_read.merged_series = merged_series

    def sort_series(self, series_info, override=False):
        if len(series_info.unsorted_dicom_paths) == 0:
            return
        imported = 0
        unsorted_dicom_paths_new = []
        if series_info.subid not in self.study.quarantine.subjects:
            self.study.quarantine.add_subject(series_info.subid)
        if series_info.visid not in self.study.quarantine.subjects[series_info.subid].visits:
            self.study.quarantine.subjects[series_info.subid].add_visit(series_info.visid)
        for path in series_info.unsorted_dicom_paths:
            if self.study.quarantine.subjects[series_info.subid].visits[series_info.visid].importDICOM(dicomlocation=path, series_info=series_info, override=override):
                os.remove(path)
                imported += 1
            else:
                unsorted_dicom_paths_new.append(path)
        if imported == len(series_info.unsorted_dicom_paths):
            print "Imported {0.subid} {0.visid} {0.series} Files: {1}".format(series_info, len(series_info.unsorted_dicom_paths))
        else:
            print "Partially Imported {0.subid} {0.visid} {0.series} Files: {2} of {1}".format(series_info, len(series_info.unsorted_dicom_paths), imported)
        series_folder = self.study.quarantine.subjects[series_info.subid].visits[series_info.visid].dicoms[series_info.series].series_folders[series_info.SeriesInstanceUID]
        series_folder.recount_dicoms()
        dicom_series = series_folder.load_DICOMseries()
        dicom_series.merge_info(series_info)
        dicom_series.sorted_files = series_folder.numdicoms
        dicom_series.unsorted_dicom_paths = unsorted_dicom_paths_new
        return dicom_series
