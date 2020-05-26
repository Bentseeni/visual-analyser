# OAMK visual-analyser UI featuring Yolo v3 Object Detection with Tensorflow 2
Yolo v3 is an algorithm that uses deep convolutional neural networks to detect objects. <br> 
This project uses a graphical user interface(vaUI.py) to make object detection easier to use<br>

## Getting started

### Prerequisites
This project is written in Python 3.7 using Tensorflow 2.2 (deep learning), NumPy (numerical computing), Pillow (image processing), OpenCV (computer vision) and seaborn (visualization) packages.

```
pip install -r requirements.txt
```

#### Install CUDA/cuDNN
See tensorflow GPU support guide [here](https://www.tensorflow.org/install/gpu). <br>
For windows, scroll down to Windows setup. <br>
NVidia's CUDA Install guide [here](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/).
### Downloading official pretrained weights
For Linux: Let's download official weights pretrained on COCO dataset. 

```
wget -P weights https://pjreddie.com/media/files/yolov3.weights
```
For Windows:
You can download the yolov3 weights by clicking [here](https://pjreddie.com/media/files/yolov3.weights) and adding them to the weights folder.

### Using Custom trained weights
<strong> Learn How To Train Custom YOLOV3 Weights Here: https://www.youtube.com/watch?v=zJDUhGL26iU </strong>

Add your custom weights file to weights folder and your custom .names file into data/labels folder.

  
### Save the weights in Tensorflow format
In the program, choose the appropriate weights location and classes(.names) location on your computer, then click on "Load Weights".

This will convert the yolov3 weights into TensorFlow .ckpt model files!


## Running the model
 The script works on images, or video. Don't forget to set the IoU (Intersection over Union) and confidence thresholds.
### Usage
Click on "Open file" to choose the video file or image file(s) you want to process. You can analyse only one video at a time, but you can run the analysis on multiple images at once.

Click on "Save location" to choose the folder where the analysed files will be saved.

Click on "Analyse" to start the analysis. If you want to END the analysis of a video at any time, press 'q'.

The analysed file will simply have the name of the original file with '_analysed' added to the name. This means running the analysis on the same file with different settings will overwrite earlier analyses of the same file if you choose to save in the same folder.

### Polling a folder
This function allows analysis to happen automatically as image or video files are added to a folder. Analyses will be saved in the same folder.

Click "Save location" to choose the folder to poll. 

Click "Start polling" to start polling.
Click "Stop polling" to stop polling.
## To-Do List
* Finish documentation

## Acknowledgments
* [Yolo v3 official paper](https://arxiv.org/abs/1804.02767)
* [A Tensorflow Slim implementation](https://github.com/mystic123/tensorflow-yolo-v3)
* [ResNet official implementation](https://github.com/tensorflow/models/tree/master/official/resnet)
* [DeviceHive video analysis repo](https://github.com/devicehive/devicehive-video-analysis)
* [A Street Walk in Shinjuku, Tokyo, Japan](https://www.youtube.com/watch?v=kZ7caIK4RXI)
* [The original Yolo v3 project this one was based on](https://github.com/theAIGuysCode/yolo-v3)
