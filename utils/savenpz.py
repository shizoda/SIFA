import numpy as np
import medpy.io as medio
import nibabel as nib
import pdb

def nii2npz():
    data_nii_pth = ''
    label_nii_pth = ''
    npz_pth = ''

    data_arr = nib.load(data_nii_pth).get_data()
    label_arr = nib.load(label_nii_pth).get_data()
    pdb.set_trace()

    np.savez(npz_pth, data_arr, label_arr)


if __name__=="__main__":
    nii2npz()