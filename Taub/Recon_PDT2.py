from ManageStudy.Nifti.NiftiTools.path import is_nifti
from ManageStudy.Nifti.NiftiTools.query import getshape
from ManageStudy.ManageStudyErrors.ReconErrors import Wrong_Number_Of_Files_Error, Bad_Nifti_Error
import os
from ManageStudy.Nifti.fslutils_wrapper.fslsplit import fslsplit

def rename_reshape_pdt2_scans(quar_dir, is_whicap_V1=False, is_whicap_V2=False , is_whicap_V3=False):
    files = os.listdir(quar_dir)
    nifti_paths = [os.path.join(quar_dir, x) for x in files if is_nifti(x)]

    if is_whicap_V2:
        for path in nifti_paths:
            if os.path.basename(path).startswith('x'):
                os.unlink(path)
                continue
        files = os.listdir(quar_dir)
        nifti_paths = [os.path.join(quar_dir, x) for x in files if is_nifti(x)]
        if len(nifti_paths) == 1:
            shape = getshape(nifti_paths[0])
            if shape[3] != 2:
                raise Bad_Nifti_Error(path, "DWI Nifti has {} timepoints but should have 2".format(shape[3]))
            split = fslsplit()
            split.split(nifti_paths[0], os.path.join(quar_dir, 'pdt2sp_'))
            splits1 = [os.path.join(quar_dir, "pdt2sp_{0:04d}.nii.gz".format(x)) for x in range(0, 30)]
            os.unlink(nifti_paths[0])
            return
        elif len(nifti_paths) == 3:
            sizes = [(x, os.stat(x).st_size) for x in nifti_paths]
            sizes.sort(key=lambda x :x[1])
            os.unlink(sizes[2][0])
        elif len(nifti_paths) == 2:
            return
        else:
            raise Wrong_Number_Of_Files_Error(quar_dir, "Wrong number of DWI files left after pruning stage, expected 1, got {}".format(len(nifti_paths)))




