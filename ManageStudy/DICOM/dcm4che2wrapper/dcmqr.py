import subprocess
import re
from ManageStudy.DICOM.series.DICOMseries_info import DICOMseries_info as DICOMseries
import warnings
#address in study.config


class dcmqr(object):

    def __init__(self, dcmqr_path, dcm4chee_inst, dcmqr_inst, dcmrcv_inst):
        self.dcmqr_path = dcmqr_path
        self.dcm4chee_inst = dcm4chee_inst
        self.dcmrcv_inst = dcmrcv_inst
        self.dcmqr_inst = dcmqr_inst

    #===============================================================================
    # Code that gets information from dcm4chee
    #===============================================================================
    def get_dcmqr_args(self, PatientName='*', SeriesDescription='*', StudyDate='*', StudyTime='*', SeriesDate='*', SeriesTime='*', PatientBirthDate='*', PatientSex='*'):
        command_args = [self.dcmqr_path, self.dcm4chee_inst ,
         '-S',
         '-qPatientName=' + PatientName,
         '-qSeriesDescription=' + SeriesDescription,
         '-qStudyDate=' + StudyDate,
         '-qStudyTime=' + StudyTime,
         '-qSeriesDate=' + SeriesDate,
         '-qSeriesTime=' + SeriesTime,
         '-qPatientBirthDate=' + PatientBirthDate,
         '-qPatientSex=' + PatientSex]
        print ' '.join(command_args)
        return command_args

    @staticmethod
    def series_generator(dcmqr_args, REC=re.compile('Query Response \#[0-9]+ for Query Request')):
        dcmqr_process = subprocess.Popen(dcmqr_args, stdout=subprocess.PIPE)
        within_series = False
        series_dict = None
        while True:
            line = dcmqr_process.stdout.readline()
            if within_series:
                if line == '\n':
                    within_series = False
                    yield DICOMseries.cls_from_dict(series_dict)
                    series_dict = None
                    continue
                newfield = dcmqr.parse_line(line)
                series_dict[newfield[0]] = newfield[1]
            elif REC.search(line):   #if this is the start of a response entry...
                within_series = True
                series_dict = {}
            elif (line != ''):
                continue
            else:
                break

    @staticmethod
    def parse_line(line, REC=re.compile('^(\([0-9A-Z]{4},[0-9A-Z]{4}\))\s+[A-Z]{2}\s+\#[0-9]+\s+\[(.*)\](.*)$')):
        result = re.match(REC, line.rstrip())
        if result == None:
            warnings.warn('Failed to match expression {0}'.format(line.rstrip()))
            return ('')
        results = result.groups()
        return [x.strip() for x in results] # strip away extra whitespace


    #===============================================================================
    # Code that gets instances from dcm4chee
    #===============================================================================

#command='dcmqr -L WHICAP_V2_ASL_QR@156.145.15.162:11138 DCM4CHEE@156.145.113.60:11112 -cmove WHICAP_V2_ASL -S -qPatientName=W39069V2 -qSeriesInstanceUID="1.3.46.670589.11.8508.5.0.4676.2009082715025290558" -cgetrspTO 6000000 -cfindrspTO 6000000 -acceptTO 6000000 -cmoverspTO 6000000 -releaseTO 6000000

#ADD DEBUGGING CODE!
    def cmove_series_instance(self, dicom_series_info_object): #requiring dicom_series_info_object makes it more likely that data is correct

        command_args = [self.dcmqr_path, '-L' , self.dcmrcv_inst, self.dcm4chee_inst , '-cmove', self.dcmrcv_inst,
         '-S',
         '-qPatientName=' + dicom_series_info_object.PatientsName,
         '-qSeriesInstanceUID=' + dicom_series_info_object.SeriesInstanceUID,
         '-cgetrspTO', '6000000', '-cfindrspTO', '6000000', '-acceptTO', '6000000', '-cmoverspTO', '6000000', '-releaseTO', '6000000']
        print "imported subid:{0.subid} visid:{0.visid} with return code {1} series:{0.series}".format(dicom_series_info_object, subprocess.check_call(command_args, stdout=subprocess.PIPE))

