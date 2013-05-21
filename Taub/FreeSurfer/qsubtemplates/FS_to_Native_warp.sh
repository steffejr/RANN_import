#!/bin/bash
#stop script execution on error
set -ex
#%(filename)s
#script registers FreeSurfer space images to Native Space Image. Uses nearest neigbor interpolation: for masks
#Subject: %(subid)s
#Visit: %(visid)s


FSLDIR=%(FSL_PATH)s
. ${FSLDIR}/etc/fslconf/fsl.sh
PATH=${FSLDIR}/bin:${PATH}
export FSLDIR PATH
export PATH=$PATH:%(ANTS_PATH)s
export PATH=$PATH:${FSLDIR}/bin
FSLOUTPUTTYPE=NIFTI

cd %(fs_folder)s

####ANTS####

#warp %(Movable_Image)s to %(Target)s ANTS. Using Transform in xforms/FS_to_Native.txt saving to %(Output)s
WarpImageMultiTransform 3 %(Movable_Image)s %(Output)s -R %(Target)s --use-NN xforms/FS_to_NativeAffine.txt;

