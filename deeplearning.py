import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import pytesseract
from pytesseract import Output
import math
import re


# LOAD YOLO MODEL
INPUT_WIDTH =  640
INPUT_HEIGHT = 640
net = cv2.dnn.readNetFromONNX('./static/models/best.onnx')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)



def get_detections(img, net):
    # CONVERT IMAGE TO YOLO FORMAT
    image = img.copy()
    row, col, d = image.shape

    max_rc = max(row, col)
    input_image = np.zeros((max_rc, max_rc, 3), dtype=np.uint8)
    input_image[0:row, 0:col] = image

    # GET PREDICTION FROM YOLO MODEL
    blob = cv2.dnn.blobFromImage(input_image, 1/255, (INPUT_WIDTH, INPUT_HEIGHT), swapRB=True, crop=False)
    net.setInput(blob)
    preds = net.forward()
    detections = preds[0]
    
    return input_image, detections

def non_maximum_supression(input_image, detections):
    # FILTER DETECTIONS BASED ON CONFIDENCE AND PROBABILITY SCORE
    boxes = []
    confidences = []

    image_w, image_h = input_image.shape[:2]
    x_factor = image_w/INPUT_WIDTH
    y_factor = image_h/INPUT_HEIGHT

    for i in range(len(detections)):
        row = detections[i]
        confidence = row[4] # confidence of detecting license plate
        if confidence > 0.1:
            class_score = row[5] # probability score of license plate
            if class_score > 0.1:
                cx, cy , w, h = row[0:4]

                left = int((cx - 0.5*w)*x_factor)
                top = int((cy-0.5*h)*y_factor)
                width = int(w*x_factor)
                height = int(h*y_factor)
                box = np.array([left, top, width, height])

                confidences.append(confidence)
                boxes.append(box)

    # clean
    boxes_np = np.array(boxes).tolist()
    confidences_np = np.array(confidences).tolist()
    # NMS
    index = np.array(cv2.dnn.NMSBoxes(boxes_np, confidences_np, 0.1, 0.1)).flatten()
    
    return boxes_np, confidences_np, index

def extract_text(image, bbox):
    x, y, w, h = bbox
    roi = image[y:y+h, x:x+w]
    
    if 0 in roi.shape:
        return '', 0.0
    else:
        # Resize the ROI to expand it along the x-axis to 150%
        new_w = int(w * 2)
        new_h = int(h * 1.2)
        resized_roi = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Use Tesseract to extract text and confidence scores from the resized ROI
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
        details = pytesseract.image_to_data(resized_roi, config=custom_config, output_type=Output.DICT)
        
        text_list = []
        confidence_list = []
        
        for i in range(len(details['text'])):
            text = details['text'][i]
            conf = int(details['conf'][i])
            if conf > 0:  # Filter out empty results
                text_list.append(text)
                confidence_list.append(conf)

        if not text_list:
            return "", 0
        
        # Join the text parts
        text = ''.join(text_list).strip()
        
        # Calculate the average confidence score
        avg_confidence = sum(confidence_list) / len(confidence_list)
        
        print(text, avg_confidence, "number")
        return text, avg_confidence

def drawings(image, boxes_np, confidences_np, index):
    # drawings
    if not boxes_np:
        return image, "", 0
    for ind in index:
        x, y, w, h = boxes_np[ind]
        bb_conf = confidences_np[ind]
        conf_text = 'plate: {:.0f}%'.format(bb_conf * 100)
        license_text, correct_factor = extract_text(image, boxes_np[ind])
        
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.rectangle(image, (x, y - 30), (x + w, y), (255, 0, 255), -1)
        cv2.rectangle(image, (x, y + h), (x + w, y + h + 30), (0, 0, 0), -1)

        cv2.putText(image, conf_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        cv2.putText(image, license_text, (x, y + h + 27), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 1)
        
    return image, license_text, correct_factor

# predictions
def yolo_predictions(img, net):
    ## step-1: get detections
    input_image, detections = get_detections(img, net)
    ## step-2: NMS
    boxes_np, confidences_np, index = non_maximum_supression(input_image, detections)
    ## step-3: Drawings
    result_img, text_result, correct_factor = drawings(img, boxes_np, confidences_np, index)
    return result_img, text_result, correct_factor


def rotate_y(img, y):
    height, width = img.shape[:2]

    # Calculate the new size to avoid cropping
    diagonal = int(math.sqrt(width ** 2 + height ** 2))
    canvas_width = diagonal
    canvas_height = diagonal

    # Create a blank canvas with a larger size
    canvas = np.zeros((canvas_height, canvas_width, 3), dtype=np.uint8)

    # Calculate the position to place the original image in the center of the canvas
    x_offset = (canvas_width - width) // 2
    y_offset = (canvas_height - height) // 2
    canvas[y_offset:y_offset + height, x_offset:x_offset + width] = img

    # Update the projection matrices based on the new canvas size
    proj2dto3d = np.array([[1, 0, -canvas_width / 2],
                           [0, 1, -canvas_height / 2],
                           [0, 0, 0],
                           [0, 0, 1]], np.float32)

    ry = np.array([[1, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]], np.float32)

    trans = np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, 100], 
                      [0, 0, 0, 1]], np.float32)

    proj3dto2d = np.array([[100, 0, canvas_width / 2, 0],
                           [0, 100, canvas_height / 2, 0],
                           [0, 0, 1, 0]], np.float32)

    ay = float(y * (math.pi / 180))

    ry[0, 0] = math.cos(ay)
    ry[0, 2] = -math.sin(ay)
    ry[2, 0] = math.sin(ay)
    ry[2, 2] = math.cos(ay)

    final = proj3dto2d.dot(trans.dot(ry.dot(proj2dto3d)))

    abs_cos = abs(math.cos(ay))
    abs_sin = abs(math.sin(ay))

    bound_w = int(canvas_height * abs_sin + canvas_width * abs_cos)
    bound_h = int(canvas_height * abs_cos + canvas_width * abs_sin)

    dst = cv2.warpPerspective(canvas, final, (bound_w, bound_h), None, cv2.INTER_LINEAR, cv2.BORDER_CONSTANT, (0, 0, 0))
    return dst

# Add this function to rotate along the z-axis
def rotate_z(img, angle):
    height, width = img.shape[:2]
    center = (width // 2, height // 2)
    rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_img = cv2.warpAffine(img, rot_matrix, (width, height), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    return rotated_img

# Modify the process_images_with_yolo function to include both rotations
def process_images_with_yolo(img, net, angles):
    z_rotated_images = [rotate_z(img, angle) for angle in angles]
    y_rotated_images = [rotate_y(z_img, angle) for z_img in z_rotated_images for angle in angles]

    best_image = None
    highest_correct_factor = 0
    correct_text = None

    for rotated_img in y_rotated_images:
        result_img, text_result, correct_factor = yolo_predictions(rotated_img, net)
        text_result = text_result.replace(" ", "")
        match = re.search(r'\b\d{6}\b', text_result)
        if match and correct_factor > highest_correct_factor:
            highest_correct_factor = correct_factor
            best_image = result_img
            correct_text = match.group()

    if best_image is None:
        return img, "No text detected"

    return best_image, correct_text

# Keep the original set of angles
angles = [ -10,-8,-6,-4,-2,2,4,6,8,10]

# Ensure this function calls the updated process_images_with_yolo
def object_detection(path, filename):
    image = cv2.imread(path)  # Read image
    image = np.array(image, dtype=np.uint8)  # Convert to 8-bit array
    result_img, text_list = process_images_with_yolo(image, net, angles)
    cv2.imwrite('./static/predict/{}'.format(filename), result_img)
    return [text_list]
