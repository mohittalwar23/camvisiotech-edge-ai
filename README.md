## camvisiotech-edge-ai-wifi
CamVisioTech is a standalone AI-powered face detection and recognition system built on the Maixduino hardware. This project is designed to operate independently without relying on external computing resources, making it efficient and accessible in low-resource environments. The project integrates both WiFi and GSM modules for network connectivity, allowing for real-time alerts and versatile deployment in environments with limited internet access. This particular repository contains the setup for the Wifi based approach to it.

## **Project Overview**

A smart surveillance system capable of:
- Detecting faces and objects in real time using the **NNCase** and **Yolo** based ML models.
- When an Intruder is detected, buzzer goes off and similarly any actuator can be controlled.
- Sending Telegram notifications to alert the user bu utilising Wifi capabalities. ( Other Third Party applications can also be integrated easily using applications like IFTTT, PipeDream etc. )
- No external computing is needed; all processing, from running ML model calculations to sending alerts, is handled on-board.
  

### **Demo Video**

For a live demonstration of the project in action, check out this video on Yourube
[CamVisioTech 3.0 Maixduino ](https://www.youtube.com)

## **Hardware & Software Requirements**

### Hardware:
- **Maixduino** RISC V + AI Kit : An AI-focused development board with onboard image processing and machine learning. It also has an ESP32 chip for WI-FI and Bluetooth Capabilities.
- **Buzzer**: For triggering alerts.
- **Breadboard & Jumper Wires**: For wiring connections.
- **OV2640**: Camera Module
- **2.4 inch TFT Display**
- **Type C Data  Cable**

### Software:
- **Micropython**
- **MaixPy IDE**  (for build and run )
- **kflash_gui**  (for uploading firmware and models to the chip)
- **uPyLoader** (accessing, updating and deleting content of flash)
  
## Setup
soon
