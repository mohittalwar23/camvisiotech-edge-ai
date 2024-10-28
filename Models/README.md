## Model Details and Usage

The following models are directly loaded into the Maixduino board’s on-board KPU (Kendryte Processing Unit), enabling efficient on-device AI processing. These models allow the Maixduino to perform face detection, landmark detection, and feature extraction without requiring an external host computer, making it a fully edge-based AI solution.

### Loading the Models
To load these models onto the Maixduino, use `kflash_gui`. Follow the [step-by-step guide](#link-to-step-by-step-guide) for detailed instructions.

### Models

- **Face Detection Model**  
  - **File:** `face_model_at_0x300000.kfpkg`  
  - **Description:** Detects faces in the camera feed, serving as the primary model to initialize the detection pipeline on the edge device.

- **Face Landmark Detection Model**  
  - **File:** `FaceLandmarkDetection.Smodel`  
  - **Description:** Identifies key facial landmarks following face detection, providing reference points for more detailed recognition tasks.

- **Feature Extraction Model**  
  - **File:** `FeatureExtraction.Smodel`  
  - **Description:** Extracts facial features based on detected landmarks, facilitating advanced tasks like recognition or matching against saved profiles.

These models work in tandem to form a comprehensive edge-based AI application capable of face detection and recognition, all processed directly on the Maixduino board.
