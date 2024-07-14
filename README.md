# Image-Based Object Detection and OCR

This project utilizes YOLO (You Only Look Once) for object detection and Tesseract for Optical Character Recognition (OCR) to extract text from images. Specifically, it is designed to detect train coach numbers from images.
## Images
![Screenshot (9215)](https://github.com/Sojournes/Train-Coach-Number-Detector/assets/97471046/827c2d40-466d-4942-8996-d109dd25cacc)

![Screenshot (9214)](https://github.com/Sojournes/Train-Coach-Number-Detector/assets/97471046/216313cb-d479-4495-a58b-54a6b1011d2c)

## Features

- **YOLO Model**: Uses a pre-trained YOLO model to detect objects in images.
- **OCR with Tesseract**: Extracts text from the detected regions.
- **Image Rotation**: Rotates images to improve OCR accuracy. The rotation angles are specified, and the image with the highest OCR confidence is selected.

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
    - Ensure you have the `best.onnx` model in the `./static/models/` directory.

### Running the Application

1. **Start the Flask server**:
    ```bash
    python app.py
    ```

2. **Open your browser** and go to `http://127.0.0.1:5000/`.

## Usage

1. **Upload an Image**:
    - Click on the "Choose File" button and select an image containing train coach numbers.
    - Click on the "Upload" button to process the image.

2. **View Results**:
    - The processed image with detected regions and extracted text will be displayed on the web page.

## Image Rotation for Enhanced OCR

To improve the accuracy of OCR, images are rotated by specified angles. The train number is generally aligned such that it goes from bigger to smaller. By rotating the images, the text becomes more readable for Tesseract, thus enhancing the recognition accuracy.

```python
angles = [ -10,-8,-6,-4,-2,2,4,6,8,10]
```

Each image is rotated through these angles, and OCR is performed on each rotated image. The image that yields the highest confidence score from Tesseract is selected as the best result.

## Key Functions

### `get_detections(img, net)`
Converts the image to YOLO format and gets predictions from the YOLO model.

### `non_maximum_supression(input_image, detections)`
Filters detections based on confidence and probability scores and applies Non-Maximum Suppression (NMS).

### `extract_text(image, bbox)`
Extracts text from the specified bounding box region of the image using Tesseract.

### `drawings(image, boxes_np, confidences_np, index)`
Draws bounding boxes and extracted text on the image.

### `rotate_y(img, y)`
Rotates the image by the specified angle.

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
