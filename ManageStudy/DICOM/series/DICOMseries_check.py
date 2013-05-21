from collections import defaultdict
from pandas import *


class DICOMseries_check(object):

    def __init__(self, dicom_series_read, dcmqr_object, csv_ref=None, check_birthyear=True, check_gender=True, check_visit_date=True):
        self.dicom_series_read = dicom_series_read
        self.study = dicom_series_read.study
        self.csv_ref = csv_ref
        self.check_birthyear = check_birthyear
        self.check_gender = check_gender
        self.check_visit_date = check_visit_date

        self.repeat_patient_names_dict = self.check_for_duplicate_PatientsNames() #dict, of lists, of series info objects w/ duplicate PatientName, key is PatientName
        self.different_demographics_between_visits_dict = self.check_for_different_demographics_between_visits() #dict of lists of series info objects w/ mismatched demographics info that should be static
        if csv_ref != None:
            self.do_not_match_ref_dict = self.check_if_patients_match_ref()
            self.in_ref_not_chee_list = self.check_dicoms_in_ref_not_in_chee()  #list of Visit_Ref objects
        else:
            self.do_not_match_ref_dict = {}
            self.in_ref_not_chee_list = []


    def check_against_ref(self, dicom_series_info):
        if (dicom_series_info.PatientsName not in self.repeat_patient_names_dict and
        dicom_series_info.PatientsName not in self.do_not_match_ref_dict and
        dicom_series_info.subid not in self.different_demographics_between_visits_dict):
            return True
        return False


    def different_demographics_between_visits_df(self):
        COLUMN_NAMES = ['DCM:PatientsName', 'Subid', 'Visid', 'DCM:VisitDateTime', 'REF:VisitDateTime', 'DCM:BirthYear', 'REF:BirthYear', 'DCM:Gender', 'REF:Gender', 'REF:Performance', 'REF:Exclude', 'Error']
        tupple_list = []
        ref_dict = self.csv_ref.ref_dict
        for dicom_series_info_list in self.different_demographics_between_visits_dict.itervalues():
            first_subject = dicom_series_info_list[0]
            gender_match = [x.PatientsSex == first_subject.PatientsSex for x in dicom_series_info_list]
            YOB_match = [x.BirthYear == first_subject.BirthYear for x in dicom_series_info_list] #year of birth
            if not all(gender_match):
                discrepancy = 'Gender'
            elif not all(YOB_match):
                discrepancy = 'Birth Year'
            else:
                discrepancy = ''
            for dicom_series_info in dicom_series_info_list:
                subid = dicom_series_info.subid
                visid = dicom_series_info.visid
                if dicom_series_info.subid not in ref_dict:
                    discrepancy = "Subid not in Ref Dict"
                    subid = None
                    visid = None
                    ref_VisitDateTime = None
                    ref_birth_year = None
                    ref_gender = None
                    ref_Performance = None
                    ref_exclude = None
                elif dicom_series_info.visid not in ref_dict[subid]:
                    discrepancy = "Visid not in Ref Dict"
                    visid = None
                    ref_VisitDateTime = None
                    ref_birth_year = None
                    ref_gender = None
                    ref_Performance = None
                    ref_exclude = None
                else:
                    visit_ref = ref_dict[dicom_series_info.subid][dicom_series_info.visid]
                    ref_VisitDateTime = visit_ref.VisitDateTime
                    ref_birth_year = visit_ref.BirthDate.year if visit_ref.BirthDate != None else None
                    ref_gender = visit_ref.Gender
                    ref_Performance = visit_ref.Performance
                    ref_exclude = visit_ref.exclude
                tupple_list.append((dicom_series_info.PatientsName,
                                    dicom_series_info.subid,
                                    dicom_series_info.visid,
                                    dicom_series_info.VisitDateTime,
                                    ref_VisitDateTime,
                                    dicom_series_info.BirthDate.year,
                                    ref_birth_year,
                                    dicom_series_info.PatientsSex,
                                    ref_gender,
                                    ref_Performance,
                                    ref_exclude,
                                    discrepancy))
        if len(tupple_list) == 0:
            tupple_list.append(('Everything is OK!',) * len(COLUMN_NAMES))
        df = DataFrame(tupple_list, columns=COLUMN_NAMES)
        return df.sort(columns='Subid')

    def repeat_patient_names_df(self):
        COLUMN_NAMES = ['DCM:PatientsName', 'Subid', 'Visid', 'DCM:VisitDateTime', 'REF:VisitDateTime', 'DCM:BirthYear', 'REF:BirthYear', 'DCM:Gender', 'REF:Gender', 'REF:Performance', 'REF:Exclude', 'Error']
        tupple_list = []
        ref_dict = self.csv_ref.ref_dict
        for dicom_series_info_list in self.repeat_patient_names_dict.itervalues():
            for dicom_series_info in dicom_series_info_list:
                subid = dicom_series_info.subid
                visid = dicom_series_info.visid
                if dicom_series_info.subid not in ref_dict:
                    discrepancy = "Subid not in Ref Dict"
                    subid = None
                    visid = None
                    ref_VisitDateTime = None
                    ref_birth_year = None
                    ref_gender = None
                    ref_Performance = None
                    ref_exclude = None
                elif dicom_series_info.visid not in ref_dict[subid]:
                    discrepancy = "Visid not in Ref Dict"
                    visid = None
                    ref_VisitDateTime = None
                    ref_birth_year = None
                    ref_gender = None
                    ref_Performance = None
                    ref_exclude = None
                else:
                    visit_ref = ref_dict[dicom_series_info.subid][dicom_series_info.visid]
                    ref_VisitDateTime = visit_ref.VisitDateTime
                    ref_birth_year = visit_ref.BirthDate.year if visit_ref.BirthDate != None else None
                    ref_gender = visit_ref.Gender
                    ref_Performance = visit_ref.Performance
                    ref_exclude = visit_ref.exclude
                    discrepancy = ''
                    if ref_gender != None and dicom_series_info.PatientsSex != ref_gender:
                        discrepancy = 'Gender'
                    elif dicom_series_info.VisitDateTime == None or dicom_series_info.VisitDateTime.date() != ref_VisitDateTime.date():
                        discrepancy = 'Visit Date'
                    elif ref_birth_year != None and dicom_series_info.BirthDate.year != ref_birth_year:
                        discrepancy = 'Birth Year'
                    else:
                        discrepancy = 'Has Duplicate'
                tupple_list.append((dicom_series_info.PatientsName,
                                    dicom_series_info.subid,
                                    dicom_series_info.visid,
                                    dicom_series_info.VisitDateTime,
                                    ref_VisitDateTime,
                                    dicom_series_info.BirthDate.year,
                                    ref_birth_year,
                                    dicom_series_info.PatientsSex,
                                    ref_gender,
                                    ref_Performance,
                                    ref_exclude,
                                    discrepancy))
        if len(tupple_list) == 0:
            tupple_list.append(('Everything is OK!',) * len(COLUMN_NAMES))
        df = DataFrame(tupple_list, columns=COLUMN_NAMES)
        return df.sort(columns='DCM:PatientsName')

    def do_not_match_ref_df(self):
        COLUMN_NAMES = ['DCM:PatientsName', 'Subid', 'Visid', 'DCM:VisitDateTime', 'REF:VisitDateTime', 'DCM:BirthYear', 'REF:BirthYear', 'DCM:Gender', 'REF:Gender', 'REF:Performance', 'REF:Exclude', 'Error']
        tupple_list = []
        ref_dict = self.csv_ref.ref_dict
        for dicom_series_info in self.do_not_match_ref_dict.itervalues():
            subid = dicom_series_info.subid
            visid = dicom_series_info.visid
            if dicom_series_info.subid not in ref_dict:
                discrepancy = "Subid not in Ref Dict"
                subid = None
                visid = None
                ref_VisitDateTime = None
                ref_birth_year = None
                ref_gender = None
                ref_Performance = None
                ref_exclude = None
            elif dicom_series_info.visid not in ref_dict[subid]:
                discrepancy = "Visid not in Ref Dict"
                visid = None
                ref_VisitDateTime = None
                ref_birth_year = None
                ref_gender = None
                ref_Performance = None
                ref_exclude = None
            else:
                visit_ref = ref_dict[dicom_series_info.subid][dicom_series_info.visid]
                ref_VisitDateTime = visit_ref.VisitDateTime
                ref_birth_year = visit_ref.BirthDate.year if visit_ref.BirthDate != None else None
                ref_gender = visit_ref.Gender
                ref_Performance = visit_ref.Performance
                ref_exclude = visit_ref.exclude
                discrepancy = ''
                if ref_gender != None and dicom_series_info.PatientsSex != ref_gender:
                    discrepancy = 'Gender'
                elif self.check_visit_date == True:
                    if ref_VisitDateTime == None:
                        discrepancy = 'No Ref Visit Date'
                    elif dicom_series_info.VisitDateTime.date() != ref_VisitDateTime.date():
                        discrepancy = 'Visit Date'
                elif self.check_birthyear == True:
                    if ref_birth_year == None:
                        discrepancy = 'No Ref Birth Year'
                    elif dicom_series_info.BirthDate.year != ref_birth_year:
                        discrepancy = 'Birth Year'
            tupple_list.append((dicom_series_info.PatientsName,
                                dicom_series_info.subid,
                                dicom_series_info.visid,
                                dicom_series_info.VisitDateTime,
                                ref_VisitDateTime,
                                dicom_series_info.BirthDate.year,
                                ref_birth_year,
                                dicom_series_info.PatientsSex,
                                ref_gender,
                                ref_Performance,
                                ref_exclude,
                                discrepancy))
        if len(tupple_list) == 0:
            tupple_list.append(('Everything is OK!',) * len(COLUMN_NAMES))
        df = DataFrame(tupple_list, columns=COLUMN_NAMES)
        return df.sort(columns='DCM:PatientsName')

    def in_ref_not_chee_df(self):
        COLUMN_NAMES = ['Subid', 'Visid', 'VisitDateTime', 'BirthYear', 'Gender', 'Performance', 'Exclude']
        tupple_list = []

        for visit in self.in_ref_not_chee_list:
            ref_birth_year = visit.BirthDate.year if visit.BirthDate != None else None
            ref_gender = visit.Gender if visit.Gender != None else None
            tupple_list.append((visit.subid, visit.visid, visit.VisitDateTime, ref_birth_year, ref_gender, visit.Performance, visit.exclude))
        if len(tupple_list) == 0:
            tupple_list.append(('Everything is OK!',) * len(COLUMN_NAMES))
        df = DataFrame(tupple_list, columns=COLUMN_NAMES)
        return df.sort(columns='Subid')


    def check_results_xls(self, xls_path):
        'print csv of mismatches'
        #Get DataFrames
        repeat_patient_names_df = self.repeat_patient_names_df()
        different_demographics_between_visits_df = self.different_demographics_between_visits_df()
        if (self.csv_ref != None):
            do_not_match_ref_df = self.do_not_match_ref_df()
            in_ref_not_chee_df = self.in_ref_not_chee_df()
        else:
            print "No CSV REF, can't make extra check spreadsheets!"

        #Get Stuff
        writer = ExcelWriter(xls_path)
        repeat_patient_names_df.to_excel(writer, sheet_name="Repeated PatientNames", index=False)
        different_demographics_between_visits_df.to_excel(writer, sheet_name="Changed Demographics", index=False)
        if (self.csv_ref != None):
            do_not_match_ref_df.to_excel(writer, sheet_name="Did Not Match Ref", index=False)
            in_ref_not_chee_df.to_excel(writer, sheet_name="In Reference Not DCM4CHEE", index=False)
        writer.save()


    def check_for_duplicate_PatientsNames(self):
        'Returns a dict of lists of duplicate dicomseries_info objects with duplicate patient names. Arbitrary series_info returned from each visit'
        patientnames = {} #dict mapping from patientnames to StudyInstanceUID
        repeat_patientnames = defaultdict(list)
        repeat_patientnames_SUIDs = {}
        merged_series = self.dicom_series_read.merged_series
        for subid in merged_series.iterkeys():
            for visid in merged_series[subid].iterkeys():
                for SIU in merged_series[subid][visid].iterkeys():
                    dicom_series_info = merged_series[subid][visid][SIU]
                    if dicom_series_info.PatientsName not in patientnames: #not repeat
                        patientnames[dicom_series_info.PatientsName] = dicom_series_info
                    elif dicom_series_info.StudyInstanceUID != patientnames[dicom_series_info.PatientsName].StudyInstanceUID and dicom_series_info.StudyInstanceUID not in repeat_patientnames_SUIDs: #new repeat
                        repeat_patientnames[dicom_series_info.PatientsName].append(dicom_series_info)
                        repeat_patientnames_SUIDs[dicom_series_info.StudyInstanceUID] = True
                        if patientnames[dicom_series_info.PatientsName].StudyInstanceUID not in repeat_patientnames_SUIDs:
                            repeat_patientnames[dicom_series_info.PatientsName].append(patientnames[dicom_series_info.PatientsName])
                            repeat_patientnames_SUIDs[patientnames[dicom_series_info.PatientsName].StudyInstanceUID] = True
        return repeat_patientnames

    def check_for_different_demographics_between_visits(self):
        "Returns a dict of lists of dseries_info objects for patients who's demographics changed between visits. Arbitrary series_info returned from each visit"
        subids_changed_demos = defaultdict(list)
        subids_changed_demos_SUIDs = {}
        merged_series = self.dicom_series_read.merged_series
        for subid in merged_series.iterkeys():
            dicom_series_info = None
            for visid in merged_series[subid].iterkeys():
                for SIU in merged_series[subid][visid].iterkeys():
                    if dicom_series_info == None:
                        dicom_series_info = merged_series[subid][visid][SIU]
                    elif dicom_series_info.PatientsSex != merged_series[subid][visid][SIU].PatientsSex or dicom_series_info.BirthYear != merged_series[subid][visid][SIU].BirthYear:
                        if dicom_series_info.StudyInstanceUID not in subids_changed_demos_SUIDs:
                            subids_changed_demos[subid].append(dicom_series_info)
                            subids_changed_demos_SUIDs[dicom_series_info.StudyInstanceUID] = True
                        if merged_series[subid][visid][SIU].StudyInstanceUID not in subids_changed_demos_SUIDs:
                            subids_changed_demos[subid].append(merged_series[subid][visid][SIU])
                            subids_changed_demos_SUIDs[merged_series[subid][visid][SIU].StudyInstanceUID] = True
        return subids_changed_demos

    def check_if_patients_match_ref(self):
        'Returns a dictionary of subjects patientnames that did not match the reference. There must be no duplicates present for this to be unique'
        do_not_match_ref_dict = {}
        merged_series = self.dicom_series_read.merged_series
        for subid in merged_series.iterkeys():
            for visid in merged_series[subid].iterkeys():
                for SIU in merged_series[subid][visid].iterkeys():
                    dicom_series_info = merged_series[subid][visid][SIU]
                    
                    #print "{}\t{}\t{}\t{}".format("Debug",dicom_series_info.PatientsName,dicom_series_info.VisitDateTime,dicom_series_info.SeriesNumber,dicom_series_info.SeriesDescription)
                    
                    try:
                        if  ((self.check_gender == True and not self.csv_ref.dicom_series_info_gender_checks_against_ref(dicom_series_info))
                             or (self.check_birthyear == True and not self.csv_ref.dicom_series_info_birth_year_checks_against_ref(dicom_series_info))
                             or self.check_visit_date == True and not self.csv_ref.dicom_series_info_date_checks_against_ref(dicom_series_info)):
                            do_not_match_ref_dict[dicom_series_info.PatientsName] = dicom_series_info
                    except:
                        print "BAD DICOMseries_check: SUBUD {}   VISID {}   SIU   {}".format(subid,visid,SIU)
        return do_not_match_ref_dict


    def check_dicoms_in_ref_not_in_chee(self):
        in_ref_not_chee_list = []
        series_dict = self.dicom_series_read.merged_series

        if self.csv_ref == None:
            print "CSV file must be loaded"
            return

        for subid in self.csv_ref.ref_dict.iterkeys():
            for visid in self.csv_ref.ref_dict[subid].iterkeys():
                if self.csv_ref.ref_dict[subid][visid].Performance != 0 and visid not in series_dict[subid]:
                    in_ref_not_chee_list.append(self.csv_ref.ref_dict[subid][visid])

        return in_ref_not_chee_list
