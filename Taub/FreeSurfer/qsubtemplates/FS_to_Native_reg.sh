#!/bin/bash
#stop script execution on error
set -ex
#%(filename)s
#script registers FreeSurfer space images to Native Space Image. 
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
mkdir -p xforms;

####ANTS####
#register %(Movable_Image)s to %(Target)s ANTS. Put Transform in xforms/FS_to_Native.txt
ANTS 3 -m CC[%(Target)s,%(Movable_Image)s,1,6] -i 0 --number-of-affine-iterations 100000x100000x100000x100000x100000 -o xforms/FS_to_Native.nii;

