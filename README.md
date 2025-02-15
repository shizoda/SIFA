## Unsupervised Bidirectional Cross-Modality Adaptation via Deeply Synergistic Image and Feature Alignment for Medical Image Segmentation

Tensorflow implementation of an unsupervised cross-modality domain adaptation framework. <br/>
This is the version of this [TMI paper](https://arxiv.org/abs/2002.02255). <br/>
Please refer to the branch [SIFA-v1](https://github.com/cchen-cc/SIFA/tree/SIFA-v1) for the version of the AAAI paper. <br/>

## Paper
[Unsupervised Bidirectional Cross-Modality Adaptation via Deeply Synergistic Image and Feature Alignment for Medical Image Segmentation](https://arxiv.org/abs/2002.02255)
<br/>
IEEE Transactions on Medical Imaging
<br/>
<br/>
<p align="center">
  <img src="figure/framework.png">
</p>

## Installation
* ~~Install TensorFlow 1.10 and CUDA 9.0~~ This fork works with the Docker image `nvcr.io/nvidia/tensorflow:22.02-tf1-py3` and an Ampere architecture GPU.
* Clone this repo (updated to this branch)
```
git clone https://github.com/shizoda/SIFA
cd SIFA
```

## Data Preparation
* Raw data needs to be written into `tfrecord` format to be decoded by `./data_loader.py`. The pre-processed data has been released from our work [PnP-AdaNet](https://github.com/carrenD/Medical-Cross-Modality-Domain-Adaptation). The training data can be downloaded [here](https://drive.google.com/file/d/1m9NSHirHx30S8jvN0kB-vkd7LL0oWCq3/view). The testing CT data can be downloaded [here](https://drive.google.com/file/d/1SJM3RluT0wbR9ud_kZtZvCY0dR9tGq5V/view). The testing MR data can be downloaded [here](https://drive.google.com/file/d/1Bm2uU4hQmn5L3GwXz6I0vuCN3YVMEc8S/view?usp=sharing).
* Put `tfrecord` data of two domains into corresponding folders under `./data` accordingly.
* Run `./create_datalist.py` to generate the datalists containing the path of each data.

## Train
* Modify the data statistics in data_loader.py according to the specifc dataset in use. Note that this is a very important step to correctly convert the data range to [-1, 1] for the network inputs and ensure the performance.
* Modify paramter values in `./config_param.json`
* Run `./main.py` to start the training process

## Evaluate
* (Modified: Trained models for the original code can be downloaded from the Dropbox link on https://github.com/cchen-cc/SIFA )
* Specify the model path and test file path in `./evaluate.py`
* Run `./evaluate.py` to start the evaluation.

## Citation
If you find the code useful for your research, please cite our paper.
```
@article{chen2020unsupervised,
  title     = {Unsupervised Bidirectional Cross-Modality Adaptation via 
               Deeply Synergistic Image and Feature Alignment for Medical Image Segmentation},
  author    = {Chen, Cheng and Dou, Qi and Chen, Hao and Qin, Jing and Heng, Pheng Ann},
  journal   = {arXiv preprint arXiv:2002.02255},
  year      = {2020}
}

@inproceedings{chen2019synergistic,
  author    = {Chen, Cheng and Dou, Qi and Chen, Hao and Qin, Jing and Heng, Pheng-Ann},
  title     = {Synergistic Image and Feature Adaptation: 
               Towards Cross-Modality Domain Adaptation for Medical Image Segmentation},
  booktitle = {Proceedings of The Thirty-Third Conference on Artificial Intelligence (AAAI)},
  pages     = {865--872},
  year      = {2019},
}
```

## Acknowledgement
Part of the code is revised from the [Tensorflow implementation of CycleGAN](https://github.com/leehomyc/cyclegan-1).

## Note
* Original code
  * https://github.com/cchen-cc/SIFA with original author's contact
  * Do not contact the original author for the problems specific to this fork!
