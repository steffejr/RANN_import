import shutil
import os.path
from ManageStudy.DICOM.dcm2nii_wrapper.dcm2nii import dcm2nii
from ManageStudy.ManageStudyErrors.ReconErrors import Wrong_Number_Of_Files_Error
from Recon_ASL import rename_reshape_asl_scans
from Recon_DWI import rename_reshape_dwi_scans
from Recon_DTI import rename_reshape_dti_scans
from Recon_PDT2 import rename_reshape_pdt2_scans
from ManageStudy.Nifti.NiftiTools.path import is_nifti, get_nifti_extension, nifti_exists, delete_nifti_by_basename
import Taub.misc as misc

def recon_dicoms(index, databin, shallow_recon=False):
    could_not_recon_list = []
    for subject in index.subjectlist:
        for visit in subject.visitlist:
            could_not_recon_list.extend(recon_visit(visit, databin, shallow_recon))
    if len(could_not_recon_list) > 0:
        print "I could not reconstruct these series:\n", '\n'.join(could_not_recon_list)



#make this code work if files are scattered over several indexes-> generic file in study functionality to be added?

def recon_visit(visit, databin, shallow_recon=False):
    'shallow_recon will NOT check the individual files to see if they exist. Shallow Recon will stop if the top level folder exists'
    dcm2nii_object = dcm2nii(args_list=['-a', 'N', '-d', 'N', '-e', 'N', '-g', 'N', '-i', 'N', '-n', 'Y', '-p', 'N', '-m', 'N', '-r', 'N', '-v', 'Y', '-x', 'N'])
    could_not_recon_list = []
    #remove garbage in quarantine
    for dicom in visit.dicomlist:
        dicom.series_folder_list.sort(key=lambda x: x.SeriesNumber) # to ensure that 0 entry removed first
        folders_to_check = [x for x in dicom.series_folder_list if x.bad == False and x.manual_recon == False]
        num_folders_to_check = len(folders_to_check)
        skip_check = False
        for series_folder in folders_to_check:
            series_info = databin.dicom_series_read.merged_series[visit.subject.subid][visit.visid][series_folder.SeriesInstanceUID]
            dicom_series_type = series_info.DICOMseries_types.itervalues().next()
            folder_name = dicom_series_type.folder #folder inside visit dir
            expected_image_quantity = dicom_series_type.expected_image_quantity #number of niftis we expect
            if series_info.series == 'DTI_1' or series_info.series == 'DTI_2':
                folder_name = series_info.series
            if shallow_recon and folder_name in visit.niftis:  #i
                print "SHALLOW SKIPPING"
                continue
            if num_folders_to_check == 1:
                skip_check = True
            if databin.dicom_series_read.merged_series[visit.subject.subid][visit.visid][series_folder.SeriesInstanceUID].Modality == 'PR': #skip PR visits
                num_folders_to_check = num_folders_to_check - 1
                continue
            elif skip_check:
                check_recon_dicom_folder(series_folder, dcm2nii_object, folder_name, expected_image_quantity)
            
            if expected_image_quantity >= 0: #not -1, the default
                generated_nifti_paths = gen_nifti_basename_fullpaths(series_folder, folder_name, expected_image_quantity)
                if all([nifti_exists(x) for x in generated_nifti_paths]):
                    break
                else:
                    could_not_recon_list.append("subid:{0.visit.subject.subid} visid: {0.visit.visid} series: {0.series}".format(dicom))
    
    misc.set_permissions(visit.path)
    return could_not_recon_list


def check_recon_dicom_folder(series_folder, dcm2nii_object, folder_name, expected_image_quantity):
    reconstructed_image_quantity = -1
    number_paths_to_generate = expected_image_quantity
    if expected_image_quantity < 0:
        reconstructed_image_quantity = recon_into_quarantine(series_folder, dcm2nii_object)
        number_paths_to_generate = reconstructed_image_quantity
    generated_nifti_paths = gen_nifti_basename_fullpaths(series_folder, folder_name, number_paths_to_generate)

    #if all niftis exist, delete all files in quarantine and exit
    niftis_exist = [nifti_exists(x) for x in generated_nifti_paths]
    if all(niftis_exist):
        visit = series_folder.image.visit
        quar_dir = os.path.join(visit.path, 'Quarantine')
        if os.path.exists(quar_dir):
            shutil.rmtree(quar_dir)
            os.mkdir(quar_dir)
        return

    #reconstruct into nifti if we havn't already
    elif reconstructed_image_quantity < 0: #not reconstructed into quarantine before
        reconstructed_image_quantity = recon_into_quarantine(series_folder, dcm2nii_object)

    #check that number of reconstructed images matches number expected
    if expected_image_quantity > 0 and expected_image_quantity != reconstructed_image_quantity:
        visit = series_folder.image.visit
        quar_dir = os.path.join(visit.path, 'Quarantine')
        reconed_files = os.listdir(quar_dir)
        reconstructed_niftis = [x for x in reconed_files if is_nifti(x)]
        quar_dir = os.path.join(visit.path, 'Quarantine')
        raise Wrong_Number_Of_Files_Error(quar_dir, "Unexpected number niftis produced by reconstruction. Expected:{0} Reconstructed:{1}\nReconstructedPaths\n{2}\nExpectedBasenames\n{3}".format(
                        expected_image_quantity,
                        reconstructed_image_quantity,
                        '\n'.join(reconstructed_niftis),
                        '\n'.join(generated_nifti_paths)
                        ))

    move_niftis(series_folder, folder_name, generated_nifti_paths)
    move_non_niftis(series_folder, folder_name)

#basename because PATHS ARE MISSING file EXTENSIONS!!!
def gen_nifti_basename_fullpaths(series_folder, folder_name, number_paths_to_generate):
    visit = series_folder.image.visit
    studyname = visit.subject.index.project.name
    target_folder = os.path.join(visit.path, folder_name)
    basename = visit.image_basename(series_folder.image.series)
    if studyname == 'WHICAP' and visit.visid == 'V1' and series_folder.image.series == 'PDT2':
        nifti_basename_paths = [visit.image_path(folder_name, 'PD'), visit.image_path(folder_name, 'T2')]
    elif studyname == 'WHICAP' and visit.visid == 'V2' and series_folder.image.series == 'PDT2':
        nifti_basename_paths = [visit.image_path(folder_name, 'PD'), visit.image_path(folder_name, 'T2')]
    elif number_paths_to_generate > 1:
        nifti_basename_paths = [os.path.join(target_folder, 'x{0}_{1}'.format(x, basename)) for x in range(1, number_paths_to_generate + 1)]
    else:
        nifti_basename_paths = [os.path.join(target_folder, basename)]
    return nifti_basename_paths

def move_niftis(series_folder, folder_name, expected_nifti_paths):
    visit = series_folder.image.visit
    quar_dir = os.path.join(visit.path, 'Quarantine')
    target_folder = os.path.join(visit.path, folder_name)
    reconed_files = os.listdir(quar_dir)

    if not os.path.exists(target_folder):
        os.mkdir(target_folder)

    myniftis = [x for x in reconed_files if is_nifti(x)]
    myniftis.sort()

    for i in range(0, len(expected_nifti_paths)):
        old_name_fullpath = os.path.join(quar_dir, reconed_files[i])
        extension = get_nifti_extension(old_name_fullpath)
        new_name_fullpath = os.path.join(quar_dir, expected_nifti_paths[i] + extension)
        if os.path.exists(new_name_fullpath):
            os.unlink(new_name_fullpath)
        shutil.move(old_name_fullpath, new_name_fullpath)
        visit.check_add_nifti(folder_name, expected_nifti_paths[i])

def move_non_niftis(series_folder, folder_name):
    'bvecs and bvals'
    visit = series_folder.image.visit
    quar_dir = os.path.join(visit.path, 'Quarantine')
    target_folder = os.path.join(visit.path, folder_name)
    reconed_files = os.listdir(quar_dir)

    if not os.path.exists(target_folder):
        os.mkdir(target_folder)

    my_non_niftis = [x for x in reconed_files if not is_nifti(x)]

    for i in range(0, len(my_non_niftis)):
        old_name_fullpath = os.path.join(quar_dir, my_non_niftis[i])
        extension = os.path.splitext(old_name_fullpath)[1]
        new_name_fullpath = os.path.join(target_folder, visit.image_basename(series_folder.image.series) + extension)
        if os.path.exists(new_name_fullpath):
            os.unlink(new_name_fullpath)
        shutil.move(old_name_fullpath, new_name_fullpath)


def recon_into_quarantine(series_folder, dcm2nii_object):
    print "Recon {0.path}".format(series_folder)
    visit = series_folder.image.visit
    studyname = visit.subject.index.project.name

    #wipe contents of quarantine dir
    quar_dir = os.path.join(visit.path, 'Quarantine')
    if os.path.exists(quar_dir):
        shutil.rmtree(quar_dir)
    os.makedirs(quar_dir)

    #reconstruct
    dcm2nii_object.recon(input_path=series_folder.path, output_path=quar_dir)
    #treat ASL scans specially
    if studyname == 'WHICAP':
        if visit.visid == 'V1':
            if series_folder.image.series == 'DWI':
                rename_reshape_dwi_scans(quar_dir, is_whicap_V1=True)
        elif visit.visid == 'V2':
            if series_folder.image.series == 'ASL':
                rename_reshape_asl_scans(quar_dir, is_whicap_V2=True)
            elif series_folder.image.series == 'DWI':
                rename_reshape_dwi_scans(quar_dir, is_whicap_V2=True)
            elif series_folder.image.series == 'PDT2':
                rename_reshape_pdt2_scans(quar_dir, is_whicap_V2=True)
        elif visit.visid == 'V3':
            if series_folder.image.series == 'DWI':
                rename_reshape_dwi_scans(quar_dir, is_whicap_V3=True)
            elif series_folder.image.series == 'DTI_1':
                rename_reshape_dti_scans(quar_dir, is_whicap_V3=True)
            if series_folder.image.series == 'ASL':
                rename_reshape_asl_scans(quar_dir, is_whicap_V2=False)
    elif series_folder.image.series in ['pASL', 'ASL']:
        rename_reshape_asl_scans(quar_dir, is_whicap_V2=False)

    reconed_files = os.listdir(quar_dir)
    myniftis = [x for x in reconed_files if is_nifti(x)]
    return len(myniftis)



