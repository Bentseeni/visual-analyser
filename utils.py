"""Contains utility functions for Yolo v3 model."""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from seaborn import color_palette
import cv2
import json


def load_images(img_names, model_size):
    """Loads images in a 4D array.
    Args:
        img_names: A list of images names.
        model_size: The input size of the model.
        data_format: A format for the array returned
            ('channels_first' or 'channels_last').
    Returns:
        A 4D NumPy array.
    """
    imgs = []

    for img_name in img_names:
        img = Image.open(img_name)
        img = img.resize(size=model_size)
        img = np.array(img, dtype=np.float32)
        img = np.expand_dims(img[:, :, :3], axis=0)
        imgs.append(img)

    imgs = np.concatenate(imgs)

    return imgs


def load_class_names(file_name):
    """Returns a list of class names read from `file_name`."""
    with open(file_name, 'r') as f:
        class_names = f.read().splitlines()
    return class_names


def draw_boxes(img_names, boxes_dicts, class_names, model_size, save_folder='./detections'):
    """Draws detected boxes.
    Args:
        img_names: A list of input images names.
        boxes_dicts: A class-to-boxes dictionary.
        class_names: A class names list.
        model_size: The input size of the model.
        save_folder: Folder where output images are to be saved.
    Returns:
        None.
    """
    analyser_config = load_json()
    colors = ((np.array(color_palette("hls", 80)) * 255)).astype(np.uint8)
    for num, img_name, boxes_dict in zip(range(len(img_names)), img_names,
                                         boxes_dicts):
        img = Image.open(img_name)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font='./data/fonts/futur.ttf',
                                  size=(img.size[0] + img.size[1]) // 100)
        resize_factor = \
            (img.size[0] / model_size[0], img.size[1] / model_size[1])
        curr_cls_number = 0
        curr_txt_y_pos = 0
        for cls in range(len(class_names)):
            boxes = boxes_dict[cls]
            if np.size(boxes) != 0:
                color = colors[cls]
                number_of_obj_for_cls = 0
                curr_cls_number += 1
                for box in boxes:
                    number_of_obj_for_cls += 1
                    xy, confidence = box[:4], box[4]
                    xy = [xy[i] * resize_factor[i % 2] for i in range(4)]
                    x0, y0 = xy[0], xy[1]
                    thickness = (img.size[0] + img.size[1]) // 400
                    for t in np.linspace(0, 1, thickness):
                        xy[0], xy[1] = xy[0] + t, xy[1] + t
                        xy[2], xy[3] = xy[2] - t, xy[3] - t
                        draw.rectangle(xy, outline=tuple(color))
                    text = '{} {:.1f}%'.format(class_names[cls],
                                               confidence * 100)
                    text_size = draw.textsize(text, font=font)
                    draw.rectangle(
                        [x0, y0 - text_size[1], x0 + text_size[0], y0],
                        fill=tuple(color))
                    draw.text((x0, y0 - text_size[1]), text, fill='black',
                              font=font)
                    print('{} {:.2f}%'.format(class_names[cls],
                                              confidence * 100))
                if analyser_config['printClasses']:
                    number_obj_txt = class_names[cls] + ": " + str(number_of_obj_for_cls)
                    txt_size = draw.textsize(number_obj_txt, font=font)
                    # draw.text((0, curr_cls_number * txt_size[1] * 2),
                    #        number_obj_txt, fill='green', font=font)
                    curr_txt_y_pos += txt_size[1] + 1
                    #draw.rectangle(
                    #    [0, curr_txt_y_pos, txt_size[0], curr_txt_y_pos + txt_size[1]],
                    #    fill=tuple(color))
                    draw.text((0, curr_txt_y_pos),
                              number_obj_txt, fill='white', font=font, stroke_width=(img.size[0] + img.size[1]) // 2000, stroke_fill='#FF00AF')
                    #print(txt_size[1])

        # Print additional texts
        additional_text = ''
        if analyser_config['printIou']:
            additional_text += "\n" + "IOU: " + analyser_config['iou']
        if analyser_config['printConfidence']:
            additional_text += "\n" + "Confidence: " + analyser_config['confidence']
        if analyser_config['printNamesPath']:
            additional_text += "\n" + analyser_config['namesPath']
        if analyser_config['printWeightPath']:
            additional_text += "\n" + analyser_config['weightsPath']

        if additional_text is not '':
            add_font = ImageFont.truetype(font='./data/fonts/futur.ttf',
                                      size=(img.size[0] + img.size[1]) // 200)
            add_txt_size = draw.multiline_textsize(additional_text, font=add_font, spacing=1, stroke_width=(img.size[0] + img.size[1]) // 2000)
            draw.multiline_text((0, img.size[1] - add_txt_size[1]),
                                additional_text, fill='white', font=add_font, spacing=1, stroke_width=(img.size[0] + img.size[1]) // 2000,
                                stroke_fill='#FF00AF')

        # Convert image to RGB and save it to folder
        rgb_img = img.convert('RGB')
        input_name_base = os.path.basename(img_name)
        #rgb_img.save(save_folder + '/' + os.path.splitext(input_name_base)[0] + '_analysed.jpg')
        rgb_img.save(save_folder + '/' + os.path.splitext(input_name_base)[0] + '_analysed' + os.path.splitext(input_name_base)[1])
        # rgb_img.save(save_folder + '/' + str(num + 1) + '.jpg')


def draw_frame(frame, frame_size, boxes_dicts, class_names, model_size):
    """Draws detected boxes in a video frame.
    Args:
        frame: A video frame.
        frame_size: A tuple of (frame width, frame height).
        boxes_dicts: A class-to-boxes dictionary.
        class_names: A class names list.
        model_size:The input size of the model.
    Returns:
        None.
    """
    analyser_config = load_json()


    boxes_dict = boxes_dicts[0]
    resize_factor = (frame_size[0] / model_size[1], frame_size[1] / model_size[0])
    colors = ((np.array(color_palette("hls", 80)) * 255)).astype(np.uint8)
    curr_cls_number = 0
    for cls in range(len(class_names)):
        boxes = boxes_dict[cls]
        color = colors[cls]
        color = tuple([int(x) for x in color])
        if np.size(boxes) != 0:
            number_of_obj_for_cls = 0
            curr_cls_number += 1
            for box in boxes:
                number_of_obj_for_cls += 1
                xy = box[:4]
                xy = [int(xy[i] * resize_factor[i % 2]) for i in range(4)]
                cv2.rectangle(frame, (xy[0], xy[1]), (xy[2], xy[3]), color[::-1], 1)
                (test_width, text_height), baseline = cv2.getTextSize(class_names[cls],
                                                                      cv2.FONT_HERSHEY_SIMPLEX,
                                                                      0.75, 1)
                cv2.rectangle(frame, (xy[0], xy[1]),
                              (xy[0] + test_width, xy[1] - text_height - baseline),
                              color[::-1], thickness=cv2.FILLED)
                cv2.putText(frame, class_names[cls], (xy[0], xy[1] - baseline),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)

            if analyser_config['printClasses']:
                (test_width, text_height), baseline = cv2.getTextSize(class_names[cls],
                                                                      cv2.FONT_HERSHEY_SIMPLEX,
                                                                      0.75, 1)
                number_obj_txt = class_names[cls] + ": " + str(number_of_obj_for_cls)
                cv2.putText(frame, number_obj_txt, (0, curr_cls_number * text_height),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 180), 2)
                cv2.putText(frame, number_obj_txt, (1, curr_cls_number * text_height + 1),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1)

    # Print additional info

    number_of_additional_prints = 0

    if analyser_config['printWeightPath']:
        number_of_additional_prints += 1
        additional_text = analyser_config['weightsPath']
        draw_additional_text(frame, frame_size, additional_text, number_of_additional_prints)

    if analyser_config['printNamesPath']:
        number_of_additional_prints += 1
        additional_text = analyser_config['namesPath']
        draw_additional_text(frame, frame_size, additional_text, number_of_additional_prints)

    if analyser_config['printConfidence']:
        number_of_additional_prints += 1
        additional_text = "Confidence: " + analyser_config['confidence']
        draw_additional_text(frame, frame_size, additional_text, number_of_additional_prints)

    if analyser_config['printIou']:
        number_of_additional_prints += 1
        additional_text = "IOU: " + analyser_config['iou']
        draw_additional_text(frame, frame_size, additional_text, number_of_additional_prints)


def load_json():
    config_location = 'config.json'

    if os.path.exists(config_location):
        config = json.load(open(config_location))
        return config
    else:
        config = {
            'printClasses': True,
            'printIou': False,
            'printConfidence': False,
            'printNamesPath': False,
            'printWeightPath': False,
            'createCsv': False,
            'namesPath': './data/labels/coco.names',
            'weightsPath': './weights/yolov3.weights',
            'iou': '0.5',
            'confidence': '0.5'
        }
        json.dump(config, open(config_location, 'w'), sort_keys=True, indent=4)
        return config


def draw_additional_text(frame, frame_size, additional_text, number_of_additional_prints):
    (test_width, text_height), baseline = cv2.getTextSize(additional_text,
                                                          cv2.FONT_HERSHEY_SIMPLEX,
                                                          0.5, 1)
    cv2.putText(frame, additional_text, (0, int(frame_size[1]) - number_of_additional_prints * text_height),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 180), 2, bottomLeftOrigin=False)
    cv2.putText(frame, additional_text, (1, int(frame_size[1]) - number_of_additional_prints * text_height + 1),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, bottomLeftOrigin=False)
