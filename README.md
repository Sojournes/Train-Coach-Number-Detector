# Train Coach Number Detector

This project implements object detection and Optical Character Recognition (OCR) to extract train coach numbers from images using YOLO (You Only Look Once) and Tesseract.

## Images
![Screenshot 1](https://github.com/Sojournes/Train-Coach-Number-Detector/assets/97471046/827c2d40-466d-4942-8996-d109dd25cacc)

![Screenshot 2](https://github.com/Sojournes/Train-Coach-Number-Detector/assets/97471046/216313cb-d479-4495-a58b-54a6b1011d2c)

## Features

- **YOLO Model**: Utilizes a pretrained YOLO model for object detection in images.
- **OCR with Tesseract**: Extracts text from the detected regions using Tesseract.
- **Image Rotation**: Enhances OCR accuracy by rotating images at specified angles to improve text readability.

## Setup

### Prerequisites

- Python 3.x
- OpenCV
- NumPy
- Matplotlib
- Pytesseract
- Flask

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Download the YOLO model**:
    - Ensure the `best.onnx` model is located in `./static/models/`.

### Running the Application

1. **Start the Flask server**:
    ```bash
    python app.py
    ```

2. **Open your browser** and navigate to `http://127.0.0.1:5000/`.

## Usage

1. **Upload an Image**:
    - Click on "Choose File" to select an image containing train coach numbers.
    - Click on "Upload" to process the image.

2. **View Results**:
    - The processed image with detected regions and extracted text will be displayed on the web page.

## Image Rotation for Enhanced OCR

To improve OCR accuracy, images are rotated at specified angles. This adjustment helps Tesseract recognize text more accurately by aligning the train numbers optimally.

```python
angles = [-10, -8, -6, -4, -2, 2, 4, 6, 8, 10]
```

Each image undergoes rotation through these angles, and OCR is performed on each rotated image. The image yielding the highest confidence score from Tesseract is selected as the best result.

## Key Functions

### `get_detections(img, net)`
Converts the image to YOLO format and retrieves predictions from the YOLO model.

### `non_maximum_supression(input_image, detections)`
Filters detections based on confidence and probability scores, applying Non-Maximum Suppression (NMS).

### `extract_text(image, bbox)`
Extracts text from the specified bounding box region of the image using Tesseract.

### `drawings(image, boxes_np, confidences_np, index)`
Draws bounding boxes and extracted text on the image.

### `rotate_y(img, y)`
Rotates the image by the specified angle.

### `rotate_z(img, angle)`
Rotates the image by the specified angle around the center using affine transformation.

### `process_images_with_yolo(img, net, angles)`
Processes the image with YOLO and OCR, iterating over different rotation angles.

### `object_detection(path, filename)`
Main function to handle image reading, processing, and saving the result.

## Flask Application

### Routes

- **`/`**: Main route to upload and display images.

### Running the Server

To run the server, execute:

```bash
python app.py
```
