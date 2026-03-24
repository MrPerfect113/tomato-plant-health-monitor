# Tomato Plant Health Monitoring

A rail-assisted tomato plant health monitoring system using YOLOv8, ESP32-CAM, Flask, and automated rail movement for real-time tomato disease detection.

## Overview

The system captures tomato plant images and video using an ESP32-CAM mounted on a motorized rail platform. The camera stream is sent to a laptop-based Flask server, where a YOLOv8 model performs tomato leaf disease detection.

The detection results, including disease class, confidence score, and bounding boxes, are displayed through a web interface.

The rail system provides controlled camera movement, while a servo motor changes the camera viewing angle. A Hall-effect sensor provides feedback for tracking the rail position.

## Disease Classes

- Healthy
- Early Blight
- Late Blight
- Leaf Mold

## Key Features

- Real-time tomato disease detection
- YOLOv8 object detection
- ESP32-CAM video streaming
- Flask-based inference backend
- Web-based monitoring
- Bounding-box visualization
- Confidence-score display
- Motorized rail movement
- Servo-controlled camera rotation
- Hall-effect sensor feedback

## System Architecture

    Tomato Plant
         |
         v
      ESP32-CAM
         |
      Wi-Fi / HTTP
         |
         v
     Flask Server
         |
         v
     YOLOv8 Model
         |
         v
   Disease Detection
         |
         v
    Web Dashboard
         |
         v
 ESP32 Rail Controller
         |
    +----+----+
    |         |
    v         v
Motor Driver Servo Motor
    |         |
    v         v
Rail Movement Camera Rotation
    |
    v
Hall Sensor Feedback

## Technologies

- Python
- YOLOv8
- PyTorch
- CUDA
- Flask
- OpenCV
- ESP32-CAM
- ESP32
- HTML
- CSS
- JavaScript
- LabelImg

## Hardware

- ESP32-CAM
- ESP32 controller
- Motor
- Motor driver
- Servo motor
- Hall-effect sensor
- Permanent magnet
- Linear rail mechanism
- Camera mounting platform
- Power supply

## Machine Learning

The machine-learning workflow includes:

- Dataset cleaning
- Dataset merging
- Dataset organization
- Annotation consistency checking
- Bounding-box annotation
- Dataset validation
- Data augmentation
- YOLOv8 model training
- CUDA GPU training
- Batch-size tuning
- Model experimentation
- Precision, recall, and mAP evaluation

### Machine Learning Pipeline

    Dataset Collection
            |
            v
    Dataset Cleaning
            |
            v
    Dataset Merging
            |
            v
       Annotation
            |
            v
    Annotation Validation
            |
            v
    Train / Validation / Test Split
            |
            v
      Data Augmentation
            |
            v
       YOLOv8 Training
            |
       +----+----+
       |         |
       v         v
    YOLOv8n   YOLOv8m
       |         |
       +----+----+
            |
            v
      Model Evaluation
            |
            v
    Precision / Recall / mAP
            |
            v
        Best Model
            |
            v
     Flask Deployment

## Dataset

The dataset was prepared using publicly available tomato leaf images and images collected from tomato farms.

The dataset preparation process included:

- Image collection
- Dataset cleaning
- Dataset merging
- Class organization
- Annotation checking
- Bounding-box annotation
- Dataset validation
- Train/validation/test organization
- Data augmentation

## Model Development

Two YOLOv8 variants were experimented with:

### YOLOv8n

YOLOv8 Nano was used as a lightweight model for faster experimentation and lower computational requirements.

### YOLOv8m

YOLOv8 Medium was used for improved feature extraction and detection performance.

Pre-trained YOLOv8 weights were used for transfer learning.

## GPU Training

CUDA-enabled GPU training was used to accelerate model development and experimentation.

Training parameters such as:

- Batch size
- Image size
- Learning rate
- Optimizer
- Number of epochs
- Early stopping

were tuned during experimentation.

## Model Evaluation

The models were evaluated using:

- Precision
- Recall
- mAP
- Confusion Matrix

These metrics were used to compare YOLOv8n and YOLOv8m and analyze class-wise detection performance.

## YOLOv8n vs YOLOv8m

### YOLOv8n

- Lower computational requirements
- Faster inference
- Smaller model size
- Suitable for lightweight applications

### YOLOv8m

- Higher model capacity
- Better feature extraction
- More robust detection
- Better separation between visually similar classes

YOLOv8m provided more stable and reliable detection performance during the project experiments.

## Rail System

The camera is mounted on a platform that moves along a linear rail.

The rail system provides:

- Controlled camera movement
- Repeatable image acquisition
- Stable positioning
- Continuous monitoring along crop rows
- Improved camera coverage

A motor driver controls the movement of the platform.

## Camera Rotation

A servo motor is used to rotate the ESP32-CAM and provide different viewing angles.

This helps reduce blind spots and improves the coverage of the monitoring system.

## Position Feedback

A Hall-effect sensor is used for movement feedback.

A permanent magnet is attached to the moving wheel while the Hall sensor remains stationary.

The ESP32 detects sensor pulses corresponding to wheel rotation and uses the count to estimate the travelled distance.

    Distance = Count × Wheel Circumference

    Wheel Circumference = 2 × π × Radius

## Web Application

The Flask-based backend provides communication between the ESP32-CAM stream, YOLOv8 model, and web interface.

The application supports:

- Live camera/video input
- YOLOv8 inference
- Tomato disease detection
- Bounding-box visualization
- Confidence-score display
- Plant health monitoring
- Rail movement control

## My Contributions

My primary contributions focused on the machine-learning pipeline.

### Dataset

- Dataset cleaning
- Dataset merging
- Dataset organization
- Dataset validation
- Annotation consistency
- Bounding-box verification
- Image-annotation checking

### Model Development

- YOLOv8 model experimentation
- YOLOv8n and YOLOv8m comparison
- Transfer learning
- CUDA GPU training
- Batch-size tuning
- Image-size tuning
- Training-parameter experimentation
- Data augmentation
- Early-stopping configuration

### Model Evaluation

- Precision analysis
- Recall analysis
- mAP evaluation
- Confusion-matrix analysis
- Class-wise performance analysis
- Model comparison
- Model selection

### Integration

- Integration of the trained YOLOv8 model with the Flask backend
- Testing with camera-streamed images
- Evaluation of real-time detection performance

## Results

The project demonstrates an integrated system combining:

- Deep learning
- Computer vision
- IoT communication
- Real-time video streaming
- Automated rail movement
- Servo-controlled camera positioning
- Web-based monitoring

YOLOv8m provided more robust detection performance compared with YOLOv8n during the model experiments.

## Repository Structure

    tomato-plant-health-monitor/
    |
    +-- backend/
    |
    +-- docs/
    |
    +-- .gitignore
    |
    +-- README.md

## Future Improvements

- Larger and more diverse datasets
- Additional disease classes
- Disease severity estimation
- Improved low-light detection
- Fully autonomous rail navigation
- Edge-device deployment
- Cloud-based monitoring

## Project Information

Project: Tomato Plant Health Monitoring

Institution: Amrita School of Engineering, Coimbatore

Main Technologies: YOLOv8, Python, Flask, ESP32-CAM, CUDA, PyTorch, and OpenCV
