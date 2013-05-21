from ManageStudy.Nifti.fslutils_wrapper.fslmerge import fslmerge
from ManageStudy.Nifti.fslutils_wrapper.fslsplit import fslsplit
from ManageStudy.Nifti.NiftiTools.path import is_nifti
from ManageStudy.Nifti.NiftiTools.query import getshape
from ManageStudy.ManageStudyErrors.ReconErrors import Wrong_Number_Of_Files_Error, Bad_Nifti_Error
import nibabel as nib
import numpy as np
import math
import os

def rename_reshape_asl_scans(quar_dir, is_whicap_V2=False):
    files = os.listdir(quar_dir)
    nifti_paths = [os.path.join(quar_dir, x) for x in files if is_nifti(x)]
    if len(nifti_paths) == 2:
        if is_whicap_V2:
            return
        else:
            raise Wrong_Number_Of_Files_Error(series_folder.path, "Wrong number of ASL files to reshape and not whicap, expected 1, got {}".format(len(nifti_paths)))
    elif len(nifti_paths) == 1:
        if is_whicap_V2:
            shape = getshape(nifti_paths[0])
            if shape[3] > 60:
                raise Bad_Nifti_Error(quar_dir, "nifti has {} timepoints, expected 60".format(shape[3]))
            if shape[2] == 15:
                reshapeASL(nifti_paths[0], z_voxel_size_multiplier=0.5)
                os.unlink(nifti_paths[0])
            else:
                split = fslsplit()
                merge = fslmerge()
                split.split(nifti_paths[0], os.path.join(quar_dir, 'aslsp_'))
                splits1 = [os.path.join(quar_dir, "aslsp_{0:04d}.nii.gz".format(x)) for x in range(0, 30)]
                splits2 = [os.path.join(quar_dir, "aslsp_{0:04d}.nii.gz".format(x)) for x in range(30, 60)]
                merge.merge(os.path.join(quar_dir, 'ASLOne.nii.gz'), splits1)
                merge.merge(os.path.join(quar_dir, 'ASLTwo.nii.gz'), splits2)
                [os.unlink(file) for file in splits1]
                [os.unlink(file) for file in splits2]
                os.unlink(nifti_paths[0])
        else:
            reshapeASL(nifti_paths[0], z_voxel_size_multiplier=1)
            os.unlink(nifti_paths[0])
    else:
        raise Wrong_Number_Of_Files_Error(quar_dir, "dcm2nii produced {} nifti paths, expected 1 or 2".format(len(nifti_paths)))




def reshapeASL(input, z_voxel_size_multiplier=1):
    '''because dcm2nii reconstructs the ASL and shuffles 
    the slices they need to be un-shuffled. 
    This DID NOT Work for the JACK tasks.
    Optionally provide z_voxel_size_multiplier to scale output in z-dim (useful for some whicap v2 asl data)'''
    print "Reshaping: {}".format(input)
    Output_Path = os.path.dirname(input)
    print "Output Path: {}".format(Output_Path)
    II = nib.load(input)
    hdr = II.get_header()
    affine = II.get_affine()
    affine[2][2] = affine[2][2] * z_voxel_size_multiplier #correct voxel size along z dimension. (it was too wide in these scans.)
    Data = np.array(II.get_data())
    shape = Data.shape
# Create zero arrays
    Label = np.zeros((shape[0], shape[1], shape[2], int(float(shape[3]) / 2)))
    Control = np.zeros((shape[0], shape[1], shape[2], int(float(shape[3]) / 2)))

    # BEGIN ATTEMPT TWO
    if shape[2] % 2 == 0: # EVEN number of slices
        for i in range(0, int(float(shape[3]) / 2), 1):
            for j in range(0, int(float(shape[2]) / 2), 1):
                Label[:, :, j * 2, i] = Data[:, :, j, i]
                Label[:, :, j * 2 + 1, i] = Data[:, :, j, i + float(shape[3]) / 2]

        hdr.set_data_shape((shape[0], shape[1], shape[2], float(shape[3]) / 2))
        out = nib.Nifti1Image(Label, affine, header=hdr)
        OutputNiiFilename = os.path.join(Output_Path, 'ASLOne.nii')
        print OutputNiiFilename
        out.to_filename(OutputNiiFilename)
        for i in range(0, int(float(shape[3]) / 2), 1):
            for j in range(0, int(float(shape[2]) / 2), 1):
                Control[:, :, j * 2, i] = Data[:, :, j + float(shape[2]) / 2, i]
                Control[:, :, j * 2 + 1, i] = Data[:, :, j + float(shape[2]) / 2, i + float(shape[3]) / 2]

        hdr.set_data_shape((shape[0], shape[1], shape[2], shape[3] / 2))
        out = nib.Nifti1Image(Control, affine, header=hdr)
        OutputNiiFilename = os.path.join(Output_Path, 'ASLTwo.nii')
        print OutputNiiFilename
        out.to_filename(OutputNiiFilename)
    else: # ODD
        for i in range(0, int(float(shape[3]) / 2), 1):
            for j in range(0, int(math.ceil(float(shape[2]) / 2)), 1):
                Label[:, :, j * 2, i] = Data[:, :, j, i]
            for j in range(0, int(math.floor(float(shape[2]) / 2)), 1):
                Label[:, :, j * 2 + 1, i] = Data[:, :, int(j + math.ceil(float(shape[2]) / 2)), i]
        hdr.set_data_shape((shape[0], shape[1], shape[2], float(shape[3]) / 2))
        out = nib.Nifti1Image(Label, affine, header=hdr)
        OutputNiiFilename = os.path.join(Output_Path, 'ASLOne.nii')
        print OutputNiiFilename
        out.to_filename(OutputNiiFilename)
        for i in range(0, int(float(shape[3]) / 2), 1):
            for j in range(0, int(math.floor(float(shape[2]) / 2)), 1):
                Control[:, :, j * 2 + 1, i] = Data[:, :, j, i + int(float(shape[3]) / 2)]
            for j in range(0, int(math.ceil(float(shape[2]) / 2)), 1):
                Control[:, :, j * 2, i] = Data[:, :, j + int(math.floor(float(shape[2]) / 2)), i + int(float(shape[3]) / 2)]

        hdr.set_data_shape((shape[0], shape[1], shape[2], shape[3] / 2))
        out = nib.Nifti1Image(Control, affine, header=hdr)
        OutputNiiFilename = os.path.join(Output_Path, 'ASLTwo.nii')
        print OutputNiiFilename
        out.to_filename(OutputNiiFilename)

