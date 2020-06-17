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

'''
def main(type, input_names, save_folder='./detections', iou_threshold=0.5, confidence_threshold=0.5, class_names_file=_CLASS_NAMES_FILE, create_csv=False):
    class_names = load_class_names(class_names_file)
    n_classes = len(class_names)

    tf.compat.v1.reset_default_graph()

    model = Yolo_v3(n_classes=n_classes, model_size=_MODEL_SIZE,
                    max_output_size=_MAX_OUTPUT_SIZE,
                    iou_threshold=iou_threshold,
                    confidence_threshold=confidence_threshold)

    if type == 'images':
        batch_size = len(input_names)
        batch = load_images(input_names, model_size=_MODEL_SIZE)
        inputs = tf.compat.v1.placeholder(tf.float32, [batch_size, *_MODEL_SIZE, 3])
        detections = model(inputs, training=False)



        saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(scope='yolo_v3_model'))

        with tf.compat.v1.Session() as sess:
            saver.restore(sess, './weights/model.ckpt')
            detection_result = sess.run(detections, feed_dict={inputs: batch})

        draw_boxes(input_names, detection_result, class_names, _MODEL_SIZE, save_folder)

        print('Detections have been saved successfully.')

    elif type == 'video':
        inputs = tf.compat.v1.placeholder(tf.float32, [1, *_MODEL_SIZE, 3])
        detections = model(inputs, training=False)
        saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(scope='yolo_v3_model'))

        with tf.compat.v1.Session() as sess:
            saver.restore(sess, './weights/model.ckpt')

            win_name = 'Video detection'
            cv2.namedWindow(win_name)
            cap = cv2.VideoCapture(input_names[0])
            frame_size = (cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                          cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'X264')
            fps = cap.get(cv2.CAP_PROP_FPS)
            input_name_base = os.path.basename(input_names[0])
            video_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_analysed.mp4'
            out = cv2.VideoWriter(video_save_path, fourcc, fps,
                                  (int(frame_size[0]), int(frame_size[1])))
            if create_csv:
                csv_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_statistics.csv'
                csv_field_names = class_names[:]
                csv_field_names.insert(0, "frame")
                print(fps)
                with open(csv_save_path, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvfile.write("sep=,")
                    csvfile.write('\n')
                    csvwriter.writerow(csv_field_names)
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    resized_frame = cv2.resize(frame, dsize=_MODEL_SIZE[::-1],
                                               interpolation=cv2.INTER_NEAREST)
                    detection_result = sess.run(detections,
                                                feed_dict={inputs: [resized_frame]})
                    if create_csv:
                        csv_input_dict = {"frame": cap.get(cv2.CAP_PROP_POS_FRAMES)}
                        #csv_input_dict = {"frame": cap.get(cv2.CAP_PROP_POS_MSEC)}
                        for cls in range(len(class_names)):
                            number_of_obj = len(detection_result[0][cls])
                            if number_of_obj != 0:
                                print(class_names[cls] + str(number_of_obj))
                                csv_input_dict[class_names[cls]] = number_of_obj

                        with open(csv_save_path, 'a', newline='') as csvfile:
                            csvwriter = csv.DictWriter(csvfile, fieldnames=csv_field_names)
                            csvwriter.writerow(csv_input_dict)

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
'''


def main(type, input_names, save_folder='./detections', iou_threshold=0.5, confidence_threshold=0.5,
         class_names_file=_CLASS_NAMES_FILE, create_csv=False):
    class_names = load_class_names(class_names_file)
    n_classes = len(class_names)

    tf.compat.v1.reset_default_graph()

    model = Yolo_v3(n_classes=n_classes, model_size=_MODEL_SIZE,
                    max_output_size=_MAX_OUTPUT_SIZE,
                    iou_threshold=iou_threshold,
                    confidence_threshold=confidence_threshold)

    if type == 'images':
        batch_size = len(input_names)
        batch = load_images(input_names, model_size=_MODEL_SIZE)
        inputs = tf.compat.v1.placeholder(tf.float32, [batch_size, *_MODEL_SIZE, 3])
        detections = model(inputs, training=False)

        saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(scope='yolo_v3_model'))

        with tf.compat.v1.Session() as sess:
            saver.restore(sess, './weights/model.ckpt')
            detection_result = sess.run(detections, feed_dict={inputs: batch})

        draw_boxes(input_names, detection_result, class_names, _MODEL_SIZE, save_folder)

        print('Detections have been saved successfully.')

    elif type == 'video':
        inputs = tf.compat.v1.placeholder(tf.float32, [1, *_MODEL_SIZE, 3])
        detections = model(inputs, training=False)
        saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(scope='yolo_v3_model'))

        with tf.compat.v1.Session() as sess:
            saver.restore(sess, './weights/model.ckpt')

            win_name = 'Video detection'
            cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(win_name, 1280, 720)
            cap = cv2.VideoCapture(input_names[0])
            frame_size = (cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                          cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'X264')
            fps = cap.get(cv2.CAP_PROP_FPS)
            input_name_base = os.path.basename(input_names[0])
            #video_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_analysed.mp4'
            video_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_analysed' + os.path.splitext(input_name_base)[1]
            #print(os.path.splitext(input_name_base)[1])
            out = cv2.VideoWriter(video_save_path, fourcc, fps,
                                  (int(frame_size[0]), int(frame_size[1])))
            if create_csv:
                csv_save_path = save_folder + '/' + os.path.splitext(input_name_base)[0] + '_statistics.csv'
                csv_field_names = class_names[:]
                csv_field_names.insert(0, "time")
                csv_field_names.insert(0, "frame")
                print(fps)
                sec_counter = 0
                with open(csv_save_path, 'w', newline='') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    csvfile.write("sep=,")
                    csvfile.write('\n')
                    csvwriter.writerow(csv_field_names)
            csv_input_dict = {"frame": cap.get(cv2.CAP_PROP_POS_FRAMES)}
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    resized_frame = cv2.resize(frame, dsize=_MODEL_SIZE[::-1],
                                               interpolation=cv2.INTER_NEAREST)
                    detection_result = sess.run(detections,
                                                feed_dict={inputs: [resized_frame]})
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
                            with open(csv_save_path, 'a', newline='') as csvfile:
                                csvwriter = csv.DictWriter(csvfile, fieldnames=csv_field_names)
                                csvwriter.writerow(csv_input_dict)
                            sec_counter += 1
                            for cls in range(len(class_names)):
                                csv_input_dict.pop(class_names[cls], None)
                            print(sec_counter)

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
