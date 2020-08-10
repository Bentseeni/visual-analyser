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
 
 IoU and confidence should be values between 0 and 1. If you're not getting enough recognitions, try raising the confidence threshold.
 If you're getting many false positives, try lowering the confidence threshold.
 
 If you're having problems with overlapping objects or recognitions, try adjusting the IoU threshold.
### Usage
Click on "Open file" to choose the video file or image file(s) you want to process. You can analyse only one video at a time, but you can run the analysis on multiple images at once.

Click on "Save location" to choose the folder where the analysed files will be saved.

Click on "Analyse" to start the analysis. If you want to END the analysis of a video at any time, press 'q'. Whatever was processed until then will still be saved.

The analysed file will simply have the name of the original file with '_analysed' added to the name. This means running the analysis on the same file with different settings will overwrite earlier analyses of the same file if you choose to save in the same folder.

### Polling a folder
This function allows analysis to happen automatically as image or video files are added to a folder. Analyses will be saved in the same folder or different chosen folder.
This feature can be used for example with Syncthing application. 

Click "Polling location" to choose the folder to poll.

Check the "Use polling location for saving" box if you want to save analysed images and videos to same location you are polling.

Click "Start polling" to start polling.
Click "Stop polling" to stop polling.

### Options & settings
Click "Options" to get to the options tab.

* Create CSV: if toggled on, when doing video analysis, a csv-file containing the number recognitions per class each second will be created.
* Print Classes: Prints the number and class names of recognitions each frame or each image on the top left corner.
* Print Iou: Prints the IoU threshold value used for that particular run of the analyser. (bottom left corner)
* Print Confidence: Prints the confidence threshold value used for that particular run of the analyser. (bottom left corner)
* Print Names Path: Prints the name of the .names-file used. (bottom left corner)
* Print Weights Path: Prints the name of the .WEIGHTS-file used. (bottom left corner)
* Text color: Choose the primary text color for the previously mentioned information.
* Text stroke color: Choose the secondary or text stroke color for the previously mentioned information.

Settings are applied when the "Save settings" button is pressed.
## To-Do List
* Finish documentation

## Acknowledgments
* [Yolo v3 official paper](https://arxiv.org/abs/1804.02767)
* [A Tensorflow Slim implementation](https://github.com/mystic123/tensorflow-yolo-v3)
* [ResNet official implementation](https://github.com/tensorflow/models/tree/master/official/resnet)
* [DeviceHive video analysis repo](https://github.com/devicehive/devicehive-video-analysis)
* [A Street Walk in Shinjuku, Tokyo, Japan](https://www.youtube.com/watch?v=kZ7caIK4RXI)
* [The original Yolo v3 project this one was based on](https://github.com/theAIGuysCode/yolo-v3)
