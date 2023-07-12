from soma import aims
import numpy as np
import nibabel as nib
import sys


def tck2npy(diff, odf, tracto):

    file=nib.streamlines.load(tracto)
    testTransfo=file.tractogram.affine_to_rasmm
    print(testTransfo)
    fileOdf=nib.load(odf)

   # aims_vox_to_ras_mm = fileOdf.affine
   # ras_mm_to_aims_vox=np.linalg.inv(aims_vox_to_ras_mm)
   # print('ras_mm_to_aims_vox')
   # print(aims_vox_to_ras_mm)
   # print(ras_mm_to_aims_vox)
    tractogram=file.tractogram

    vol=aims.read(diff)

   # aims_vox_to_aims_mm=np.diag(vol.header()['voxel_size'])
    ras_mm_to_aims_mm=np.linalg.inv(np.array(aims.AffineTransformation3d(vol.header()['transformations'][0]).toMatrix()))
    #print('aims_vox_to_aims_mm')
    #print(aims_vox_to_aims_mm)
    print(ras_mm_to_aims_mm)
    #ras_mm_to_aims_mm = np.dot(aims_vox_to_aims_mm, ras_mm_to_aims_vox)
    print('Final')
    #print(ras_mm_to_aims_mm)
    tractogram=tractogram.apply_affine(ras_mm_to_aims_mm)
    return(tractogram.streamlines)

# main function

def main(arguments):
    diff=arguments[1]
    odf=arguments[2]
    tracto=arguments[3]
    out=arguments[4]

    print('converting')
    stream=tck2npy(diff, odf, tracto)
    print('saving')
    np.save(out, stream)
    print('OK')

if __name__ == "__main__":
     main(sys.argv)



