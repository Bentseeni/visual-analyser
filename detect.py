"""Yolo v3 detection script.

The type parameter should be 'images' or 'video'
Saves the detections in save_folder (parameter)
Input video/images should be put as a list of paths in input_names (parameter)
The iou_threshold (Intersection over Union) parameter should be a float between 0 and 1, preferrably above 0.5
The confidence_threshold parameter should be a float between 0 and 1, preferrably above 0.5
The class_names_file parameter should point to a .names-file that is valid for the model you are running.
The create_csv parameter determines whether a csv-file will be created of the detections in the case of video.

Note that only one video can be processed at one run.
"""
import os
import tensorflow as tf
import sys
import cv2
import csv

from yolo_v3 import Yolo_v3
from utils import load_images, load_class_names, draw_boxes, draw_frame

tf.compat.v1.disable_eager_execution()
# _CLASS_NAMES_FILE has the DEFAULT .names path
_MODEL_SIZE = (416, 416)
_CLASS_NAMES_FILE = './data/labels/coco.names'
_MAX_OUTPUT_SIZE = 20
_TO_MP4_FORMAT_LIST = [".webm", ".gif"]


def main(type, input_names, save_folder='./detections', iou_threshold=0.5, confidence_threshold=0.5,
         class_names_file=_CLASS_NAMES_FILE, create_csv=False):
    # Get class names and number
    class_names = load_class_names(class_names_file)
    n_classes = len(class_names)

    # Tensorflow prep
    tf.compat.v1.reset_default_graph()

    # Load Yolo_v3 model
    model = Yolo_v3(n_classes=n_classes, model_size=_MODEL_SIZE,
                    max_output_size=_MAX_OUTPUT_SIZE,
                    iou_threshold=iou_threshold,
                    confidence_threshold=confidence_threshold)

    if type == 'images':

        # Load pictures and set up detection inputs
        batch_size = len(input_names)
        batch = load_images(input_names, model_size=_MODEL_SIZE)
        inputs = tf.compat.v1.placeholder(tf.float32, [batch_size, *_MODEL_SIZE, 3])
        detections = model(inputs, training=False)

        saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(scope='yolo_v3_model'))

        # Load the weights model.ckpt and run detection on inputs
        with tf.compat.v1.Session() as sess:
            saver.restore(sess, './weights/model.ckpt')
            detection_result = sess.run(detections, feed_dict={inputs: batch})

        # Using detection results, draw detection boxes on input pictures and save them
        draw_boxes(input_names, detection_result, class_names, _MODEL_SIZE, save_folder)

        print('Detections have been saved successfully.')

    elif type == 'video':

        # Set yolo_v3 to tensorflow
        inputs = tf.compat.v1.placeholder(tf.float32, [1, *_MODEL_SIZE, 3])
        detections = model(inputs, training=False)
        saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(scope='yolo_v3_model'))

        # Run tensorflow session
        with tf.compat.v1.Session() as sess:
            # Load model
            saver.restore(sess, './weights/model.ckpt')

            # Create window for output video
            win_name = 'Video detection'
            cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(win_name, 1280, 720)

            # Create OpenCV capture and get video metadata
            cap = cv2.VideoCapture(input_names[0])
            frame_size = (cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                          cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'X264')
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Set name and save destination for output video
            input_name_base = os.path.basename(input_names[0])
            # video_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_analysed.mp4'
            video_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_analysed' + \
                              os.path.splitext(input_name_base)[1]
            if os.path.splitext(input_name_base)[1] in _TO_MP4_FORMAT_LIST:
                video_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_analysed.mp4'
            # print(os.path.splitext(input_name_base)[1])

            # Create output video
            out = cv2.VideoWriter(video_save_path, fourcc, fps,
                                  (int(frame_size[0]), int(frame_size[1])))

            # Create csv file and insert row of time, frame, and classes if create_csv is set to True
            if create_csv:
                csv_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_statistics.csv'
                csv_field_names = class_names[:]
                csv_field_names.insert(0, "time")
                csv_field_names.insert(0, "frame")
                print(fps)
                sec_counter = 0
                with open(csv_save_path, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_file.write("sep=,")
                    csv_file.write('\n')
                    csv_writer.writerow(csv_field_names)
                csv_input_dict = {"frame": cap.get(cv2.CAP_PROP_POS_FRAMES)}
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Resize frame to fit model and run detection
                    resized_frame = cv2.resize(frame, dsize=_MODEL_SIZE[::-1],
                                               interpolation=cv2.INTER_NEAREST)
                    detection_result = sess.run(detections,
                                                feed_dict={inputs: [resized_frame]})
                    # In one second intervals, insert the maximum number of detections per class to a new row in csv
                    if create_csv:

                        csv_input_dict["frame"] = cap.get(cv2.CAP_PROP_POS_FRAMES)
                        csv_input_dict["time"] = cap.get(cv2.CAP_PROP_POS_MSEC)
                        for cls in range(len(class_names)):
                            number_of_obj = len(detection_result[0][cls])
                            if number_of_obj != 0:
                                print(class_names[cls] + str(number_of_obj))
                                if class_names[cls] in csv_input_dict:
                                    csv_input_dict[class_names[cls]] = max(number_of_obj,
                                                                           csv_input_dict[class_names[cls]])
                                else:
                                    csv_input_dict[class_names[cls]] = number_of_obj
                        if cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 >= sec_counter:
                            with open(csv_save_path, 'a', newline='') as csv_file:
                                csv_writer = csv.DictWriter(csv_file, fieldnames=csv_field_names)
                                csv_writer.writerow(csv_input_dict)
                            sec_counter += 1
                            for cls in range(len(class_names)):
                                csv_input_dict.pop(class_names[cls], None)
                            print(sec_counter)

                    # Draw detection boxes on the frame being handled
                    draw_frame(frame, frame_size, detection_result,
                               class_names, _MODEL_SIZE)

                    # Show the current output frame on window
                    cv2.imshow(win_name, frame)

                    # Poll for key inputs, if 'q' is pressed, break to end processing video
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord('q'):
                        break

                    # Write the current frame to the output file
                    out.write(frame)
            finally:
                cv2.destroyAllWindows()
                cap.release()
                print('Detections have been saved successfully.')

    # Not in use currently
    elif type == 'webcam':
        inputs = tf.compat.v1.placeholder(tf.float32, [1, *_MODEL_SIZE, 3])
        detections = model(inputs, training=False)
        saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(scope='yolo_v3_model'))

        with tf.compat.v1.Session() as sess:
            saver.restore(sess, './weights/model.ckpt')

            win_name = 'Webcam detection'
            cv2.namedWindow(win_name)
            cap = cv2.VideoCapture(0)
            frame_size = (cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                          cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'X264')
            fps = cap.get(cv2.CAP_PROP_FPS)
            out = cv2.VideoWriter('./detections/detections.mp4', fourcc, fps,
                                  (int(frame_size[0]), int(frame_size[1])))

            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    resized_frame = cv2.resize(frame, dsize=_MODEL_SIZE[::-1],
                                               interpolation=cv2.INTER_NEAREST)
                    detection_result = sess.run(detections,
                                                feed_dict={inputs: [resized_frame]})

                    draw_frame(frame, frame_size, detection_result,
                               class_names, _MODEL_SIZE)

                    cv2.imshow(win_name, frame)

                    key = cv2.waitKey(1) & 0xFF

                    if key == ord('q'):
                        break

                    out.write(frame)
            finally:
                cv2.destroyAllWindows()
                cap.release()
                print('Detections have been saved successfully.')

    else:
        raise ValueError("Inappropriate data type. Please choose either 'video' or 'images'.")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[6:], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])
