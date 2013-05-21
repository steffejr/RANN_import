from ManageStudy.Nifti.NiftiTools.path import is_nifti
from ManageStudy.Nifti.NiftiTools.query import getshape
from ManageStudy.ManageStudyErrors.ReconErrors import Wrong_Number_Of_Files_Error, Bad_Nifti_Error
import os

def rename_reshape_dwi_scans(quar_dir, is_whicap_V1=False, is_whicap_V2=False , is_whicap_V3=False):
    files = os.listdir(quar_dir)
    nifti_paths = [os.path.join(quar_dir, x) for x in files if is_nifti(x)]

    if is_whicap_V1:
        for path in nifti_paths:
            if os.path.basename(path).startswith('x'):
                os.unlink(path)
                continue
        files = os.listdir(quar_dir)
        nifti_paths = [os.path.join(quar_dir, x) for x in files if is_nifti(x)]
        if len(nifti_paths) == 1:
            shape = getshape(nifti_paths[0])
            if shape[3] != 5 and shape[3] != 2:
                raise Bad_Nifti_Error(path, "DWI Nifti has {} timepoints but should have 2 or 5".format(shape[3]))
            return
        else:
            raise Wrong_Number_Of_Files_Error(quar_dir, "Wrong number of DWI files left after pruning stage, expected 1, got {}".format(len(nifti_paths)))

    if is_whicap_V2:
        for path in nifti_paths:
            if os.path.basename(path).startswith('x'):
                os.unlink(path)
                continue
        files = os.listdir(quar_dir)
        nifti_paths = [os.path.join(quar_dir, x) for x in files if is_nifti(x)]
        if len(nifti_paths) == 1:
            shape = getshape(nifti_paths[0])
            if shape[3] != 5 and shape[3] != 2:
                raise Bad_Nifti_Error(path, "DWI Nifti has {} timepoints but should have 2 or 5".format(shape[3]))
            return
        else:
            raise Wrong_Number_Of_Files_Error(quar_dir, "Wrong number of DWI files left after pruning stage, expected 1, got {}".format(len(nifti_paths)))

    if is_whicap_V3:
        if len(nifti_paths) == 1:
            shape = getshape(nifti_paths[0])
            if shape[3] != 2:
                raise Bad_Nifti_Error(path, "DWI Nifti has {} timepoints but should have 2".format(shape[3]))
            return
        elif len(nifti_paths) == 2:
            for path in nifti_paths:
                if os.path.basename(path).startswith('x'):
                    os.unlink(path)
                    continue
                shape = getshape(path)
                if len(shape) < 4 or shape[3] != 2:  #delete files that only have 1 image, should have two
                    os.unlink(path)

            files = os.listdir(quar_dir)
            nifti_paths = [os.path.join(quar_dir, x) for x in files if is_nifti(x)]
            if len(nifti_paths) == 0:
                raise Wrong_Number_Of_Files_Error(quar_dir, "Wrong number of DWI files left after pruning stage, expected 1, got {}".format(len(nifti_paths)))


