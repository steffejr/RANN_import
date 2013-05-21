from ManageStudy.DICOM.series.DICOMseries_type import DICOMseries_type as DST
import re



def DICOMseries2study_subid(dicom_series, DICOM_subid_REC=re.compile('^RANN_([0-9]{4}).*', re.IGNORECASE)):
    result = re.search(DICOM_subid_REC, dicom_series.PatientsName)
    if result != None:
        subid = result.group(1)
        return "P{0:08d}".format(int(subid))
    else:
        return None

def DICOMseries2study_visid(dicom_series, DICOM_visid_REC=re.compile('^RANN_[0-9]{4}_?([0-9]*)$', re.IGNORECASE)):
    if dicom_series.subid == None:
        return None
    result = re.search(DICOM_visid_REC, dicom_series.PatientsName)
    if result != None:
        visid = result.group(1)
        if visid == '':
            return "S{0:04d}".format(1)
        else:
            return "S{0:04d}".format(int(visid))
    else:
        return None

def DICOMseries2study_series_types(dicom_series, DICOMseries_type_list=[
                DST(name='Syn_r1', series_desc_RE_list=['^Synonyms'], expected_image_quantity=1),
                DST(name='DgtSym_r1', series_desc_RE_list=['^Digit-Symbol'], expected_image_quantity=1),
                DST(name='Ant_r1', series_desc_RE_list=['^Antonyms'], expected_image_quantity=1),
                DST(name='LetComp_r1', series_desc_RE_list=['^Letter-Comparison'], expected_image_quantity=1),
                DST(name='PictName_r1', series_desc_RE_list=['^Picture Naming'], expected_image_quantity=1),
                DST(name='PattComp_r1', series_desc_RE_list=['^Pattern-Comparison'], expected_image_quantity=1),
                DST(name='FLAIR', series_desc_RE_list=['^T2W_FLAIR CLEAR'], expected_image_quantity=1),
                DST(name='REST_BOLD', series_desc_RE_list=['^RestingState_150dyn'], expected_image_quantity=1),
                DST(name='pASL', series_desc_RE_list=['^ASL'], expected_image_quantity=2),
                DST(name='MatReas_r1', series_desc_RE_list=['^Matrices'], expected_image_quantity=1),
                DST(name='LetSet_r1', series_desc_RE_list=['^Letter Sets'], expected_image_quantity=1),
                DST(name='PairAssoc_r1', series_desc_RE_list=['^Paired Associates'], expected_image_quantity=1),
                DST(name='PaperFold_r1', series_desc_RE_list=['^Paper-Folding'], expected_image_quantity=1),
                DST(name='LogMem_r1', series_desc_RE_list=['^Logical Memory'], expected_image_quantity=1),
                DST(name='WordOrder_r1', series_desc_RE_list=['^Word Order Recognition'], expected_image_quantity=1),
                DST(name='T1', series_desc_RE_list=['^MPRAGE1x1x1 SENSE'], expected_image_quantity=1),
                DST(name='DTI', series_desc_RE_list=['^WIP DTI|^DTI'], expected_image_quantity=1),
                DST(name='Survey', series_desc_RE_list=['Surv'])
              ]):
    if dicom_series.subid == None or dicom_series.visid == None:
        return None
    for series_type in DICOMseries_type_list:
        dicom_series.chk_add_DICOMseries_type(series_type)

def assign_series(DSR):
    for key1 in DSR.merged_series.iterkeys():
        for key2 in DSR.merged_series[key1].iterkeys():
            dti_list = []
            for key3 in DSR.merged_series[key1][key2].iterkeys():
                if key3 in DSR.merged_series[key1][key2]:

                        #remove data without series descriptions
                    if (DSR.merged_series[key1][key2][key3].SeriesDescription == None) or (DSR.merged_series[key1][key2][key3].SeriesDescription == ''):
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                        #delete bad data
                    elif (DSR.merged_series[key1][key2][key3].SeriesDescription.lower().find('xxxx') != -1):
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                        #delete derived data
                    elif int(DSR.merged_series[key1][key2][key3].SeriesNumber) > 100 and ((int(DSR.merged_series[key1][key2][key3].SeriesNumber) % 10) > 1):
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                    #delete PR data
                    elif DSR.merged_series[key1][key2][key3].Modality.upper() == 'PR':
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                        #skip if no series matched
                    elif (len(DSR.merged_series[key1][key2][key3].DICOMseries_types) == 0):
                        pass

                        #DTI handled specially
                    elif ('DTI' in DSR.merged_series[key1][key2][key3].DICOMseries_types):
                        dti_list.append(DSR.merged_series[key1][key2][key3])

                        #more than 1 match handled specially
                    elif (len(DSR.merged_series[key1][key2][key3].DICOMseries_types) > 1):
                        pass

                        #Survey data thrown out
                    elif ('Survey' in DSR.merged_series[key1][key2][key3].DICOMseries_types):
                        DSR.merged_series[key1][key2][key3].delete_series_unsorted_files()

                        #skip if number of instances too small
                    elif DSR.merged_series[key1][key2][key3].number_of_instances < DSR.merged_series[key1][key2][key3].DICOMseries_types.itervalues().next().expected_instances:
                        pass

                        #if only one series type matched and it was not one of the special ones above...
                    else:
                        #assign series if not previously assigned
                        if DSR.merged_series[key1][key2][key3].series == None:
                            DSR.merged_series[key1][key2][key3].series = DSR.merged_series[key1][key2][key3].DICOMseries_types.iterkeys().next()
            dti_list.sort(key=lambda x: x.SeriesNumber)
            for i in range(0, len(dti_list)):
                dti_name = "DTI_" + str(i + 1)
                dti_list[i].series = dti_name
                dti_list[i].DICOMseries_types.itervalues().next().folder = dti_name

