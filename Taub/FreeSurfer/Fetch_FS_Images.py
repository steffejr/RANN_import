import os
import re
from Qsub_Functions import *


def import_subjects(fs_study, index, folder, series):
    for subject in index.subjectlist:
        for visit in subject.visitlist:
            if folder in scan.niftis and series in scan.niftis[folder]:
                fsID = fsID_from_visit(visit)
                if fsID not in fs_study.subjects:
                    fs_study.importT1(fsID, visit.niftis[folder][series].path)


def import_mri_as_nii(index, dest_folder, series_list=['orig', 'nu', 'aparc+aseg', 'aparc.a2009s+aseg'], extension='.nii'):
    mri_convert_args = ['-it', 'mgz' , '-ot', 'nii' , '-iid', '-1', '0', '0', '-ijd', '0', '0', '-1', '-ikd', '0', '1', '0' , '-r', '1', '-3', '2']
    mgz2nii = mri_convert(path='/usr/local/aleksey/freesurfer/freesurfer5_1/bin/mri_convert', args_list=mri_convert_args)
    for subject in index.subjectlist:
        for visit in subject.visitlist:
            fsID = fsID_from_visit(visit)
            if fsID in fs_study.subjects:
                fs_subject = fs_study.subjects[fsID]
            else:
                continue
            paths = [(os.path.join(fs_subject.path, 'mri', x + '.mgz'), visit.image_path(folder='freesurfer', series=x, extension=extension)) for x in series_list]
            for mgz, nii in paths:
                if not os.path.exists(nii) and os.path.exists(mgz):
                    if not os.path.exists(os.path.dirname(nii)):
                        os.makedirs(os.path.dirname(nii), 0775)
                    mgz2nii.convert(mgz, nii)
                    visit.add_nifti_by_full_path(nii)

def reg_mri_to_native(index, ref=('T1', 'T1'), fs_folder='freesurfer', series_list=[ 'aparc+aseg', 'aparc.a2009s+aseg'], extension='.nii'):
    '''Bring FreeSurfer image from freesurfer space to native space using ANTS, meant to work with masks, but will work with other images'''
    (ref_folder, ref_series) = ref
    for subject in index.subjectlist:
        for visit in subject.visitlist:
            #if no ref or no freesurfer files: skip
            if fs_folder not in visit.niftis or ref_folder not in visit.niftis or ref_series not in visit.niftis[ref_folder]:
                continue
            hold_jid = []
            xforms_dir = os.path.join(visit.path, fs_folder, 'xforms')
            if not os.path.exists(xforms_dir) or 'FS_to_NativeAffine.txt' not in os.listdir(xforms_dir):
                Target = visit.niftis[ref_folder][ref_series]
                Movable_Image = visit.niftis[fs_folder]['orig']
                hold_jid = [FS_to_Native_reg(Target, Movable_Image, fsl_path='/usr/local/aleksey/fsl', ants_path='/usr/local/aleksey/ANTS/bin')]
            for series in series_list:
                native_series = "n" + series
                if series in visit.niftis[fs_folder] and native_series not in visit.niftis[fs_folder]:
                    Target = visit.niftis[ref_folder][ref_series]
                    Movable_Image = visit.niftis[fs_folder][series]
                    visit.add_nifti_by_full_path(visit.image_path(fs_folder, native_series, '.nii'))
                    Output = visit.niftis[fs_folder][native_series]
                    FS_to_Native_warp(Target, Movable_Image, Output, hold_jid=hold_jid, fsl_path='/usr/local/aleksey/fsl', ants_path='/usr/local/aleksey/ANTS/bin')




