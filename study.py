'''
Created on Aug 23, 2012

@author: jason
'''
#Required
import os
os.sys.path.append("/share/users/js2746_Jason/Scripts/QualityControlCode")
from ManageStudy.Study import Study
from ManageStudy.databin import databin
from ManageStudy.DICOM.series.DICOMseries_read import DICOMseries_read as DSR
from ManageStudy.DICOM.series.DICOMseries_check import DICOMseries_check as DSC
from ManageStudy.DICOM.series.DICOMseries_sort import DICOMseries_sort as DSS
from ManageStudy.DICOM.series.DICOMseries_import import DICOMseries_import as DSI
from ManageStudy.DICOM.dcm4che2wrapper.dcmqr import dcmqr as dcmqr_wrapper
from ManageStudy.Ref.CSV_Ref import CSV_Ref
from ManageStudy.StudyEmailAlert import send_email
import sort_dicom_helpers
#Optional Taub
from Taub.QualityControl.db_connect import db_connect
from Taub.QualityControl import quality_control
import Taub.misc as misc
from Taub.Spreadsheet_Formatter import format_CSVs
import Taub.Recon_DICOM as Recon_DICOM

import RunQA
import CheckSubject
#from subfnFindFiles import * 
from db_connect_main import db_connect_main
#Optional FreeSurfer
#from ManageFreesurfer.FS_Study import FS_Study
#import run_freesurfer

print "Reading RANN Study"
study = Study('/share/studies/RANN', 'RANN')
os.chdir(study.path)
studydata = databin()
studydata.maintainer = 'Nikhil Chandra'
studydata.maintainer_email = 'nsc2124@columbia.edu'
studydata.dcmqr_object = dcmqr_wrapper(dcmqr_path='dcmqr', dcm4chee_inst='TAUB_CHEE@156.145.15.135:11112', dcmqr_inst='RANN_QR@156.145.15.135:11140', dcmrcv_inst='RANN')
studydata.dcmqr_args_list = [studydata.dcmqr_object.get_dcmqr_args(PatientName='*RANN_4*')]
studydata.db_connection = db_connect(host='156.145.15.135', port=3306, user='steffejr', passwd='ticabl', db='MRIQualityControl')
studydata.db_connection_main = db_connect_main(host='156.145.15.135', port=3306, user='steffejr', passwd='ticabl', db='cnsdivdb')
format_CSVs(['CSV/Subject_List/RANN_Subjects.csv'], 'CSV/Subject_List/ref_list.csv', accepted_headings=['MRI1', 'MRI2', 'MRI3'])
studydata.ref_csv = CSV_Ref(os.path.join(study.path, 'CSV', 'Subject_List', 'ref_list.csv'))
#studydata.fs_study = FS_Study(os.path.join(study.path, 'FreeSurfer'), '/usr/local/aleksey/freesurfer/freesurfer5_1', fsIDRE='^P[0-9]{8}_S[0-9]{4}$')
dcmrcv_port='11121'
#studydata.fs_study = FS_Study(os.path.join(study.path, 'FreeSurfer'), '/usr/local/aleksey/freesurfer/freesurfer5_1', fsIDRE='^P[0-9]{8}_S[0-9]{4}$')

def check_AE_port():
    Str="dcmecho "+studydata.dcmqr_object.dcmrcv_inst+"@10.115.15.198:"+dcmrcv_port
    RET=os.system(Str)
    
    if RET>0:
        print "WARNING: dcmrcv is not running so no data can be imported."
    else:
        print "dcmrcv is up and running!!"
    return RET
        
    
def check_make_vars(force=False):
    if force or not hasattr(studydata, 'dicom_series_read'):
        print "Pulling Data from dcm4chee & Creating dicom_series_read"
        studydata.dicom_series_read = DSR(study,
                                   sort_dicom_helpers.DICOMseries2study_subid, sort_dicom_helpers.DICOMseries2study_visid,
                                   sort_dicom_helpers.DICOMseries2study_series_types, sort_dicom_helpers.assign_series,
                                   studydata.dcmqr_args_list)
    if force or not hasattr(studydata, 'dicom_series_check'):
        print "dicom_series_check"+" is TRUE"
        studydata.dicom_series_check = DSC(studydata.dicom_series_read, dcmqr_object=studydata.dcmqr_object, csv_ref=studydata.ref_csv, check_birthyear=False, check_gender=False)
    if force or not hasattr(studydata, 'dicom_series_sort'):
        print "dicom_series_sort"+" is TRUE"
        studydata.dicom_series_sort = DSS(studydata.dicom_series_read, studydata.dicom_series_check)
    if force or not hasattr(studydata, 'dicom_series_import'):
        print "dicom_series_import"+" is TRUE"
        studydata.dicom_series_import = DSI(studydata.dicom_series_sort, studydata.dcmqr_object)


def study_email_merged_sheet(To=[]):
    if type(To) == str:
        To = [To]
    check_make_vars()
    email_csv_dir = os.path.join(study.path, 'CSV', 'Email')
    if not os.path.exists(email_csv_dir):
        os.mkdir(email_csv_dir)
    merged_sheet_path = os.path.join(email_csv_dir, '{}_merged_series.csv'.format(study.name))
    check_sheet_path = os.path.join(email_csv_dir, '{}_check_series.xls'.format(study.name))
    print "creating merged series spreadsheet"
    studydata.dicom_series_read.series_info_dict_2_csv(studydata.dicom_series_read.merged_series, path=merged_sheet_path)
    studydata.dicom_series_check.check_results_xls(xls_path=check_sheet_path)
    send_email(To=To, From=studydata.maintainer_email, subject="{} Status Update".format(study.name), preamble='test', attachment_paths=[merged_sheet_path, check_sheet_path])
    os.unlink(merged_sheet_path)
    os.unlink(check_sheet_path)

def study_import_dicoms():
    if check_AE_port()==0:
        study_sort_dicoms()
        print "Importing DICOMs"
        studydata.dicom_series_import.import_dicoms()
        print "\n"
        # update the SQL dB with the imported subjects
        study_sql_update_ref()

    #studydata.dicom_series_import.check_dicoms_in_ref_not_in_chee()

def study_sort_dicoms():
    check_make_vars()
    studydata.dicom_series_sort.sort_dicoms(reload_incoming=True, override=True)

def study_recon_dicoms(shallow_recon=False):
    check_make_vars()
    print "Reconstructing Dicoms..."
    Recon_DICOM.recon_dicoms(study.quarantine, studydata, shallow_recon)
    Recon_DICOM.recon_dicoms(study.study_main, studydata, shallow_recon)
    Recon_DICOM.recon_dicoms(study.excluded, studydata, shallow_recon)
#    study_db_insert_subjects()
#    if hasattr(studydata, 'ref_csv'):
#        study_db_update_ref()

def study_qc_move():
    global study
    qc_table_dict = studydata.db_connection.fetch_table_dict_of_study(study.name)
    quality_control.move_subjects(study, qc_table_dict)
    study = Study(study.path, study.name)
    #check_make_vars(force=True)




def study_db_insert_subjects():
    print "attempting to enter new data into db..."
    studydata.db_connection.enter_index_visits(study.name, study.quarantine)
    studydata.db_connection.enter_index_visits(study.name, study.study_main)
    studydata.db_connection.enter_index_visits(study.name, study.excluded)

def study_db_update_ref():
    #check_make_vars()
    studydata.db_connection.update_db_from_csvref(study.name, studydata.ref_csv)

def study_run_qc():
    RunQA.RunQA()


def study_update_qc_mainDB():
    # This section checks the QC database and creates summaries of the qc results and puts them in the main database
    study_check_qc(['T1'],'T1')
    #
    #study_check_qc(['LS_r1','LS_r2','LS_r3'],'LS')
    #study_check_qc(['ECF_r1','ECF_r2','ECF_r3','ECF_r4','ECF_r5','ECF_r6'],'ECF')
    study_check_qc(['pASL'],'pASL')
    study_check_qc(['DTI_1','DTI_2'],'DTI')
    study_check_qc(['FLAIR'],'FLAIR')
    study_check_qc(['REST_BOLD'],'REST')
    #study_check_qc(['Checkerboard_pASL_ACC','Checkerboard_pASL_V1'],'CBpASL')
    
    
def study_check_qc(SeriesName,shortSeriesName):
    # This command will check all the subjects for this study and set the 
    # MRI qc flags in the main database as needed.    
    # Need to establish a connection to the main database
    conn_main = studydata.db_connection_main
    conn_qc = studydata.db_connection
    # get all subjects in qc table with the series names
    # If more than one series is selected put the names all together
    sqlcommand = "SELECT subid,visitid,StudyName"
    for i in SeriesName:
        sqlcommand=sqlcommand+","+i+"_usable"
    sqlcommand=sqlcommand+" FROM "+study.name
    print sqlcommand
    conn_qc.cur.execute(sqlcommand)
    for row_dict in conn_qc.cur.fetchall():
        print row_dict
        study_name = row_dict['StudyName']
        subid = row_dict['subid']
        visid = row_dict['visitid']
        # create a list of all entries for the SeriesName
        usable=[]
        for i in SeriesName:
            usable.append(int(row_dict[i+'_usable']))
        # check to see if any of the Series are not usable
        UsableFlag = True
        for i in usable:
            if i!=1:
                UsableFlag=False
        if UsableFlag:
            sqlcommand = "insert into AllData (subid,visitid,StudyName,qc_mri_"+shortSeriesName+") values ('"+subid+"','"+visid+"','"+study_name+"','1') on duplicate key update visitid='"+visid+"',subid='"+subid+"',StudyName='"+study_name+"',qc_mri_"+shortSeriesName+"='1';"
        else:
            sqlcommand = "insert into AllData (subid,visitid,StudyName,qc_mri_"+shortSeriesName+") values ('"+subid+"','"+visid+"','"+study_name+"','0') on duplicate key update visitid='"+visid+"',subid='"+subid+"',StudyName='"+study_name+"',qc_mri_"+shortSeriesName+"='0';"
        conn_main.cur.execute(sqlcommand)

def study_sql_update_ref():
    # This updates the main database with important information about this visit
    for i in studydata.ref_csv.ref_dict:
        for j in studydata.ref_csv.ref_dict[i]:
            try:
                temp = studydata.ref_csv.ref_dict[i][j]
                visitid_long=study.name+"_"+temp.subid+"_"+temp.visid
                visitdate=str(temp.VisitDateTime.year)+"-"+str(temp.VisitDateTime.month)+"-"+str(temp.VisitDateTime.day)
                print visitdate
                dob=str(temp.BirthDate.year)+"-"+str(temp.BirthDate.month)+"-"+str(temp.BirthDate.day)
                sqlcommand="insert into AllData (subid,visitid,StudyName,visitdate,dob,gender) values ("
                sqlcommand="%s '%s','%s','%s','%s','%s','%s')" %(sqlcommand,temp.subid,visitid_long,study.name,visitdate,dob,temp.Gender)
                sqlcommand="%s on duplicate key update subid='%s',visitid='%s',StudyName='%s',visitdate='%s',dob='%s',gender='%s';"%(sqlcommand,temp.subid,visitid_long,study.name,visitdate,dob,temp.Gender)
                studydata.db_connection_main.cur.execute(sqlcommand)
                print sqlcommand
            except:
                pass
            
def check_RANN_Subject_Behav(subid,studydata):
    RANNBehav={}
    Tasks = ['DgtSym','LetComp','PaperFold','LetSet','Syn','Ant','LogMem','MatReas','PairAssoc','PattComp','WordOrder']
    Measures = ['PropOnTimeCor','medianAllRT']
    
    for task in Tasks:
        RANNBehav[task]={}
        sqlcommand = "SELECT subid"
        for meas in Measures: 
            sqlcommand = sqlcommand+", %s_%s"%(task,meas)
        sqlcommand=sqlcommand+" FROM cnsdivdb.RANNBehav where subid='%s'"%(subid)
        #print sqlcommand
        conn_qc = studydata.db_connection
        conn_qc.cur.execute(sqlcommand)
        for row_dict in conn_qc.cur.fetchall():
            for meas in Measures:
                if row_dict[task+"_"+meas]>-1:
                    RANNBehav[task][meas]=row_dict[task+"_"+meas]   
    print subid
    for task in RANNBehav.iteritems():
        Str="%15s:"%(task[0])
        for meas in Measures:
            if len(task[1])>0:
                Str="%s %s=%3.4f,"%(Str,meas,task[1][meas])
            else:
                Str="%s no data found"%(Str)
        if len(task[1])>0:
            if task[1][Measures[0]]<0.5:
                Str="%s <<<<<< "%(Str)
        print Str
        
def display_RANN_Behav_AllSubjects(study):
    for s in study.subjectlist:
        print s.subid
        check_RANN_Subject_Behav(s.subid,studydata)

def study_CheckSubjects(subid):
    SubjectSummary = []
    conn_qc = studydata.db_connection
    #for i in range(0,5,1):
        #S=study.subjectlist[i]
    #for S in study.subjectlist:
    if subid in study.quarantine.subjects:
        S = study.quarantine.subjects[subid]
        D=CheckSubject.CheckSubject(S)
        #D.InitializeScansCogRes()
        D.InitializeScansRANN()
        print "\n-----------------------------"
        print "============================="
        print "========= %s ========="%(D.Subject.subid)
        print "======= %s ======="%("Acquistion Problems")  
        for V in D.Subject.visitlist: 
            Files=os.listdir(V.path)
            D.InspectImages(Files,V.path)
            SubjectSummary.append(D)
        print "======= %s ======="%("Found Scans")
        D.CheckAllScansCollected()
        print "======= %s ======="%("Missing Scans")
        D.CheckAllScansNOTCollected()
        print "======= %s ======="%("QC Assessment")
        D.PrintQCAssessment(conn_qc,study.name)
    else:
        print "Subject: %s not imported"%(subid)
    
def study_CheckAllSubjects():
    SubjectSummary = []
    conn_qc = studydata.db_connection
    for S in study.quarantine.subjectlist:
    #for i in range(0,5,1):
        #S=study.subjectlist[i]
    #for S in study.subjectlist:
        D=CheckSubject.CheckSubject(S)
        D.InitializeScansCogRes()
        D.InitializeScansRANN()
        print "\n-----------------------------"
        print "============================="
        print "========= %s ========="%(D.Subject.subid)
        print "======= %s ======="%("Acquistion Problems")  
        for V in D.Subject.visitlist: 
            Files=os.listdir(V.path)
            D.InspectImages(Files,V.path)
            SubjectSummary.append(D)
        print "======= %s ======="%("Missing Scans")
        D.CheckAllScansCollected()
        print "======= %s ======="%("QC Assessment")
        D.PrintQCAssessment(conn_qc,study.name)

## STUFF TO RUN AT STARTUP
print 
print
print "Checking for the DICOM server port"
check_AE_port()