import re


class DICOMseries_type(object):

    def __init__(self, name, series_desc_RE_list, patient_name_RE_list=[] , folder=None, series_desc_exclusion_RE_list=[], numslices= -1, expected_instances= -1, expected_image_quantity= -1):
        self.name = name
        self.folder = folder or name
        self.series_desc_REC_list = [re.compile(x, re.IGNORECASE) if type(x) == str else x for x in series_desc_RE_list]
        self.patient_name_REC_list = [re.compile(x, re.IGNORECASE) if type(x) == str else x for x in patient_name_RE_list]
        self.series_desc_exclusion_REC_list = [re.compile(x, re.IGNORECASE) if type(x) == str else x for x in series_desc_exclusion_RE_list]
        self.numslices = numslices
        self.expected_instances = expected_instances
        self.expected_image_quantity = expected_image_quantity

    def add_series_desc_RE(self, RE):
        self.series_desc_REC_list.push(re.compile(RE, re.IGNORECASE))

    def add_patient_name_RE(self, RE):
        self.patient_name_REC_list.push(re.compile(RE, re.IGNORECASE))

    def add_exclusion_RE(self, RE):
        self.series_desc_exclusion_REC_list.push(re.compile(RE, re.IGNORECASE))

    def pattern_match(self, series_description, patient_name=None):
#        import pdb
#        pdb.set_trace()
        if self.series_pattern_match(series_description) and self.patientname_pattern_match(patient_name) and not self.exclusion_match(series_description):
            return True
        return False


    def series_pattern_match(self, series_description):
        for REC in self.series_desc_REC_list:
            if re.search(REC, series_description):
                return True
        return False

    def patientname_pattern_match(self, patient_name):
        if len(self.patient_name_REC_list) == 0 or (patient_name == None):
            return True
        for REC in self.patient_name_REC_list:
            if re.search(REC, patient_name):
                return True
        return False


    def exclusion_match(self, series_description):
        for REC in self.series_desc_exclusion_REC_list:
            if re.search(REC, series_description):
                return True
        return False

    def __str__(self):
        return "DICOMseries_type: {0.name}\n\tseries_desc_REC_list:\n\t\t {1}\n\tpatient_name_REC_list:\n\t\t {2}\n\tseries_desc_exclusion_REC_list:\n\t\t {3}".format(self.name,
                                        '\n\t\t'.join(self.series_desc_REC_list),
                                        '\n\t\t'.join(self.patient_name_REC_list),
                                        '\n\t\t'.join(self.exclusion_REC_list))
