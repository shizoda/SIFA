"""Code for testing SIFA."""
import json
import numpy as np
import os, pdb, sys
import medpy.metric.binary as mmb
import tensorflow as tf
import nibabel as nib
import model
from stats_func import *
defaultAffine = np.diag((1,1,1,1))

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

CHECKPOINT_PATH = os.path.join( os.path.abspath(os.path.dirname(__file__)), 'output/sifa-cardiac-mr2ct') # model path
dirPath = CHECKPOINT_PATH+"-test"
BASE_FID = os.path.abspath(os.path.dirname(__file__)) # folder path of test files
TESTFILE_FID = "./data/datalist/evalfiles.txt" # path of the .txt file storing the test filenames
TEST_MODALITY = 'CT'
USE_newstat = True
KEEP_RATE = 1.0
IS_TRAINING = False
NORMALIZE = True
BATCH_SIZE = 256

data_size = [256, 256, 1]
label_size = [256, 256, 1]

contour_map = {
    "bg": 0,
    "la_myo": 1,
    "la_blood": 2,
    "lv_blood": 3,
    "aa": 4,
}


class SIFA:
    """The SIFA module."""

    def __init__(self, config):

        self.keep_rate = KEEP_RATE
        self.is_training = IS_TRAINING
        self.checkpoint_pth = CHECKPOINT_PATH
        self.batch_size = BATCH_SIZE

        self._pool_size = int(config['pool_size'])
        self._skip = bool(config['skip'])
        self._num_cls = int(config['num_cls'])

        self.base_fd = BASE_FID
        self.test_fid = BASE_FID + '/' + TESTFILE_FID

    def model_setup(self):

        self.input_a = tf.placeholder(
            tf.float32, [
                self.batch_size,
                model.IMG_WIDTH,
                model.IMG_HEIGHT,
                1
            ], name="input_A")
        self.input_b = tf.placeholder(
            tf.float32, [
                self.batch_size,
                model.IMG_WIDTH,
                model.IMG_HEIGHT,
                1
            ], name="input_B")
        self.fake_pool_A = tf.placeholder(
            tf.float32, [
                None,
                model.IMG_WIDTH,
                model.IMG_HEIGHT,
                1
            ], name="fake_pool_A")
        self.fake_pool_B = tf.placeholder(
            tf.float32, [
                None,
                model.IMG_WIDTH,
                model.IMG_HEIGHT,
                1
            ], name="fake_pool_B")
        self.gt_a = tf.placeholder(
            tf.float32, [
                self.batch_size,
                model.IMG_WIDTH,
                model.IMG_HEIGHT,
                self._num_cls
            ], name="gt_A")
        self.gt_b = tf.placeholder(
            tf.float32, [
                self.batch_size,
                model.IMG_WIDTH,
                model.IMG_HEIGHT,
                self._num_cls
            ], name="gt_B")

        inputs = {
            'images_a': self.input_a,
            'images_b': self.input_b,
            'fake_pool_a': self.fake_pool_A,
            'fake_pool_b': self.fake_pool_B,
        }

        outputs = model.get_outputs(inputs, skip=self._skip, is_training=self.is_training, keep_rate=self.keep_rate)

        self.pred_mask_b = outputs['pred_mask_b']

        self.predicter_b = tf.nn.softmax(self.pred_mask_b)
        self.compact_pred_b = tf.argmax(self.predicter_b, 3)
        self.compact_y_b = tf.argmax(self.gt_b, 3)

    def read_lists(self, fid):
        """read test file list """

        with open(fid, 'r') as fd:
            _list = fd.readlines()

        my_list = []
        for _item in _list:
            my_list.append(self.base_fd + '/' + _item.split('\n')[0])
        return my_list

    def label_decomp(self, label_batch):
        """decompose label for one-hot encoding """

        _batch_shape = list(label_batch.shape)
        _vol = np.zeros(_batch_shape)
        _vol[label_batch == 0] = 1
        _vol = _vol[..., np.newaxis]
        for i in range(self._num_cls):
            if i == 0:
                continue
            _n_slice = np.zeros(label_batch.shape)
            _n_slice[label_batch == i] = 1
            _vol = np.concatenate( (_vol, _n_slice[..., np.newaxis]), axis = 3 )
        return np.float32(_vol)

    def test(self):
        """Test Function."""

        self.model_setup()
        saver = tf.train.Saver()
        init = tf.global_variables_initializer()

        test_list = self.read_lists(self.test_fid)

        with tf.Session() as sess:
            sess.run(init)

            saver.restore(sess, self.checkpoint_pth)

            dice_list = []
            assd_list = []
            for idx_file, fid in enumerate(test_list):
                
                prefix = os.path.join(dirPath, os.path.basename(fid).replace(".npy",""))
                _npz_dict = np.load(fid, allow_pickle=False)
                data = _npz_dict['arr_0']
                label = _npz_dict['arr_1']
                
                '''
                if data.shape[0]>data_size[0] or data.shape[1]>data_size[1]:
                  startX = int(data.shape[0]/2)
                  startY = int(data.shape[1]/2)
                  data  = data[startX:startX+data_size[0], startY:startY+data_size[1], :]
                  label = label[startX:startX+data_size[0], startY:startY+data_size[1], :]
                  print("Cropped around center", data.shape)
                '''
                # This is to make the orientation of test data match with the training data
                # Set to False if the orientation of test data has already been aligned with the training data
                if True:
                    data = np.flip(data, axis=0)
                    data = np.flip(data, axis=1)
                    label = np.flip(label, axis=0)
                    label = np.flip(label, axis=1)

                tmp_pred = np.zeros(label.shape)

                frame_list = [kk for kk in range(data.shape[2])]
                for ii in range(int(np.floor(data.shape[2] // self.batch_size))):
                    data_batch = np.zeros([self.batch_size, data_size[0], data_size[1], data_size[2]])

                    label_batch = np.zeros([self.batch_size, label_size[0], label_size[1]])
                    for idx, jj in enumerate(frame_list[ii * self.batch_size: (ii + 1) * self.batch_size]):
                        data_batch[idx, ...] = np.expand_dims(data[..., jj].copy(), 3)
                        label_batch[idx, ...] = label[..., jj].copy()
                    label_batch = self.label_decomp(label_batch)
                    
                    
                    if NORMALIZE:
                        if TEST_MODALITY=='CT':
                            if USE_newstat:
                                data_batch = np.subtract(np.multiply(np.divide(np.subtract(data_batch, -2.8), np.subtract(3.2, -2.8)), 2.0),1) # {-2.8, 3.2} need to be changed according to the data statistics
                            else:
                                data_batch = np.subtract(np.multiply(np.divide(np.subtract(data_batch, -1.9), np.subtract(3.0, -1.9)), 2.0),1) # {-1.9, 3.0} need to be changed according to the data statistics      
                        elif TEST_MODALITY=='MR':
                            data_batch = np.subtract(np.multiply(np.divide(np.subtract(data_batch, -1.8), np.subtract(4.4, -1.8)), 2.0),1)  # {-1.8, 4.4} need to be changed according to the data statistics

                    if ii==0:
                      nib.save(nib.Nifti1Image(data_batch, defaultAffine), prefix+"-batch.nii.gz")
                      print((np.min(data_batch), np.max(data_batch)))

                    compact_pred_b_val = sess.run(self.compact_pred_b, feed_dict={self.input_b: data_batch, self.gt_b: label_batch})
                    # pdb.set_trace()

                    for idx, jj in enumerate(frame_list[ii * self.batch_size: (ii + 1) * self.batch_size]):
                        tmp_pred[..., jj] = compact_pred_b_val[idx, ...].copy()
                        
                # save input and output files
                if not os.path.exists(dirPath) :
                  os.makedirs(dirPath)
                nib.save(nib.Nifti1Image(tmp_pred, defaultAffine), prefix+"-pred.nii.gz")
                nib.save(nib.Nifti1Image(data    , defaultAffine), prefix+"-data.nii.gz")
                nib.save(nib.Nifti1Image(label   , defaultAffine), prefix+"-label.nii.gz")


                for c in range(1, self._num_cls):
                    pred_test_data_tr = tmp_pred.copy()
                    pred_test_data_tr[pred_test_data_tr != c] = 0

                    pred_gt_data_tr = label.copy()
                    pred_gt_data_tr[pred_gt_data_tr != c] = 0

                    dice_list.append(mmb.dc(pred_test_data_tr, pred_gt_data_tr))
                    assd_list.append(mmb.assd(pred_test_data_tr, pred_gt_data_tr))

            dice_arr = 100 * np.reshape(dice_list, [4, -1]).transpose()

            dice_mean = np.mean(dice_arr, axis=0)
            dice_std = np.std(dice_arr, axis=0)

            print('Dice:')
            print('AA :%.1f (%.1f)' % (dice_mean[3], dice_std[3]))
            print('LAC:%.1f (%.1f)' % (dice_mean[1], dice_std[1]))
            print('LVC:%.1f (%.1f)' % (dice_mean[2], dice_std[2]))
            print('Myo:%.1f (%.1f)' % (dice_mean[0], dice_std[0]))
            print('Mean:%.1f' % np.mean(dice_mean))

            assd_arr = np.reshape(assd_list, [4, -1]).transpose()

            assd_mean = np.mean(assd_arr, axis=0)
            assd_std = np.std(assd_arr, axis=0)

            print('ASSD:')
            print('AA :%.1f (%.1f)' % (assd_mean[3], assd_std[3]))
            print('LAC:%.1f (%.1f)' % (assd_mean[1], assd_std[1]))
            print('LVC:%.1f (%.1f)' % (assd_mean[2], assd_std[2]))
            print('Myo:%.1f (%.1f)' % (assd_mean[0], assd_std[0]))
            print('Mean:%.1f' % np.mean(assd_mean))


def main(config_filename):

    with open(config_filename) as config_file:
        config = json.load(config_file)

    sifa_model = SIFA(config)
    sifa_model.test()


if __name__ == '__main__':
    main(config_filename='./config_param.json')
