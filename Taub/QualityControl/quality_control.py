from shutil import copy2, rmtree
from os.path import join
import os
import Taub.misc as misc

def move_replace(source, dest):
    for root, dir, files in os.walk(source, topdown=False):
        for name in files:
            newdir = root.replace(source, dest)
            if not os.path.isdir(newdir):
                os.makedirs(newdir, 0775)
            copy2(join(root, name), join(newdir, name))
    rmtree(source)
    misc.set_permissions(dest)


def movevisit(visit, index):
    newvisitpath = join(index.path, visit.subject.subid, visit.visid)
    print "moving {0} to {1}".format(visit.path, newvisitpath)
    move_replace(visit.path, newvisitpath)

def move_subjects(study, study_db_table):
    for subject in study.quarantine.subjectlist:
        for visit in subject.visitlist:
            if (subject.subid in  study_db_table) and (visit.visid in study_db_table[subject.subid]):
                if study_db_table[subject.subid][visit.visid]['ReCheck'] != '0':
                    continue
                elif study_db_table[subject.subid][visit.visid]['IncludeSubject'] == '1' and study_db_table[subject.subid][visit.visid]['IncludeSubjectRef'] == '1':
                    movevisit(visit, study.study_main)
                elif study_db_table[subject.subid][visit.visid]['IncludeSubject'] == '0' or study_db_table[subject.subid][visit.visid]['IncludeSubjectRef'] == '0':
                    movevisit(visit, study.excluded)
        if len(os.listdir(subject.path)) == 0:
            os.rmdir(subject.path)

    for subject in study.study_main.subjectlist:
        for visit in subject.visitlist:
            if (subject.subid in  study_db_table) and (visit.visid in study_db_table[subject.subid]):
                if study_db_table[subject.subid][visit.visid]['ReCheck'] != '0':
                    continue
                elif study_db_table[subject.subid][visit.visid]['IncludeSubject'] == '0':
                    movevisit(visit, study.excluded)
        if len(os.listdir(subject.path)) == 0:
            os.rmdir(subject.path)
            
    for subject in study.excluded.subjectlist:
        for visit in subject.visitlist:
            if (subject.subid in  study_db_table) and (visit.visid in study_db_table[subject.subid]):
                if study_db_table[subject.subid][visit.visid]['ReCheck'] != '0':
                    continue
                elif study_db_table[subject.subid][visit.visid]['IncludeSubject'] == '1':
                    movevisit(visit, study.study_main)
        if len(os.listdir(subject.path)) == 0:
            os.rmdir(subject.path)



