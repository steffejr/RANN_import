import os.path
from Qsub.Qsub import Qsub

template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qsubtemplates')

def FS_to_Native_reg(Target, Movable_Image, prefix='FS_to_Native_reg', fsl_path='/usr/local/aleksey/fsl', ants_path='/usr/local/aleksey/ANTS/bin'):
    visit = Target.visit
    qsub = Qsub(templatepath=os.path.join(template_folder, 'FS_to_Native_reg.sh'), scriptdir=os.path.join(visit.path, 'Qsub'), qsubpath='qsub', command_args=['mem_free=2G', 'h_vmem=2G'])
    dict = {'filename':prefix + '_' + visit.visid + '_' + visit.subject.subid + '.sh',
            'subid':visit.subject.subid,
            'visid':visit.visid,
            'fs_folder':os.path.join(visit.path, Movable_Image.folder),
            'Target':Target.path,
            'Movable_Image':Movable_Image.path,
            'FSL_PATH':fsl_path,
            'ANTS_PATH':ants_path,
            }
    return qsub.submit(dict) #return jobid as str


def FS_to_Native_warp(Target, Movable_Image, Output, hold_jid=[], prefix='FS_to_Native_warp', fsl_path='/usr/local/aleksey/fsl', ants_path='/usr/local/aleksey/ANTS/bin'):
    visit = Target.visit
    prefix = Movable_Image.series + '_FS_to_Native_warp'
    qsub = Qsub(templatepath=os.path.join(template_folder, 'FS_to_Native_warp.sh'), scriptdir=os.path.join(visit.path, 'Qsub'), qsubpath='qsub', command_args=['mem_free=2G', 'h_vmem=2G'])
    dict = {'filename':prefix + '_' + visit.visid + '_' + visit.subject.subid + '.sh',
            'subid':visit.subject.subid,
            'visid':visit.visid,
            'fs_folder':os.path.join(visit.path, Movable_Image.folder),
            'Target':Target.path,
            'Movable_Image':Movable_Image.path,
            'Output':Output.path,
            'FSL_PATH':fsl_path,
            'ANTS_PATH':ants_path,
            }
    return qsub.submit(dict, hold_jid=hold_jid) #return jobid as str
