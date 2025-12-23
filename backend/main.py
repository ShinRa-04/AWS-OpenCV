import cv2
import os
import time
import base64
import json
import numpy as np
import tensorflow as tf
import joblib
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras import mixed_precision
import google.generativeai as genai
from dotenv import load_dotenv
import shutil

# Load environment variables
load_dotenv()

# Setup Mixed Precision
mixed_precision.set_global_policy('mixed_float16')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
BATCH_SIZE = 100
TARGET_FPS = 5
FRAME_INTERVAL_FOR_GEMINI = 10
MODEL_NAME = 'gemini-2.5-pro' 
MODEL_NAME_FLASH = 'gemini-2.5-flash'

UPLOAD_FOLDER = "uploaded_videos"
ANOMALY_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anomaly")

for folder in [UPLOAD_FOLDER, ANOMALY_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Load Anomaly Detection Models
print("Loading anomaly detection models (ResNet50 + SVM)...")
try:
    feature_extractor = ResNet50(weights='imagenet', include_top=False, pooling='avg', input_shape=(224, 224, 3))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    svm_path = os.path.join(base_dir, "weights", "svm_model.pkl")
    svm_model = joblib.load(svm_path)
    print("Warming up GPU...")
    dummy_input = np.zeros((1, 224, 224, 3), dtype=np.float16)
    feature_extractor.predict(dummy_input, verbose=0)
    print("Anomaly detection models loaded and ready.")
except Exception as e:
    print(f"Critical error loading models: {e}")

# Setup Gemini
def setup_gemini(model_name):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in .env file.")
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

gemini_model = setup_gemini(MODEL_NAME)
gemini_flash_model = setup_gemini(MODEL_NAME_FLASH)

class FrameData:
    def __init__(self, frame: np.ndarray, timestamp: datetime):
        self.frame = frame
        self.timestamp = timestamp

def process_batch(frame_batch: list[FrameData]) -> bool:
    if not frame_batch:
        return False

    frames = [fd.frame for fd in frame_batch]
    preprocessed_batch = np.array(
        [tf.keras.applications.resnet50.preprocess_input(image.img_to_array(f)) for f in frames],
        dtype=np.float16
    )
    features = feature_extractor.predict(preprocessed_batch, verbose=0)
    predictions = svm_model.predict(features)
    
    return any(pred == 1 for pred in predictions)

def generate_flash_summary(analysis_data: dict):
    if not gemini_flash_model:
        return "Summary not available."
    
    prompt = f"""
    Based on the provided security analysis JSON, generate a concise, factual paragraph describing the events.
    Ensure all key details from the JSON (persons, actions, objects, critical level) are included.
    Do not add any information not present in the JSON, and do not omit any significant details.
    The output should be a single, well-structured paragraph.
    
    Analysis Data:
    {json.dumps(analysis_data, indent=2)}
    """

    try:
        response = gemini_flash_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating flash summary: {e}")
        return "Summary generation failed."

@app.get("/analysis/{video_name}")
async def get_analysis(video_name: str):
    video_anomaly_folder = os.path.join(ANOMALY_FOLDER, video_name)
    analysis_filename = f"analysis_{video_name}.json"
    analysis_path = os.path.join(video_anomaly_folder, analysis_filename)
    
    if os.path.exists(analysis_path):
        with open(analysis_path, 'r') as f:
            analysis_data = json.load(f)
        
        summary = generate_flash_summary(analysis_data)
        
        return {
            "status": "complete",
            "analysis": analysis_data,
            "summary": summary
        }
    else:
        # Check if processing is still in progress
        found = False
        for ext in ['.mp4', '.avi', '.mov', '.mkv']:
            if os.path.exists(os.path.join(UPLOAD_FOLDER, f"{video_name}{ext}")):
                found = True
                break
        
        if found:
            return {"status": "processing"}
        
        return {"status": "not_found"}

def analyze_with_gemini(frames: list[FrameData], video_name: str, output_folder: str):
    if not gemini_model or not frames:
        return None

    selected_frames = frames[::FRAME_INTERVAL_FOR_GEMINI]
    images_base64 = []
    for f in selected_frames:
        _, buffer = cv2.imencode('.jpg', f.frame)
        encoded = base64.b64encode(buffer).decode('utf-8')
        images_base64.append({"mime_type": "image/jpeg", "data": encoded})
    
    prompt = """
                A machine learning model has flagged this sequence of frames for a potential suspicious activity.
                Your task is to act as a security analyst and provide a concise, factual description of the events.
                Focus on describing the specific actions that are likely suspicious. What is happening that is out of the ordinary?
                Return a single JSON object ONLY. Do not include ```json or any other text.
                {
                "activity_description": {
                    "summary": "A brief, one-sentence summary of the suspicious event, starting with a verb phrase.",
                    "involved_persons_actions": ["Detailed description of actions"],
                    "involved_objects": ["object1", "object2"],
                    "critical_level": "High/Medium/Low"
                }
                }
            """
    content = [prompt] + images_base64

    try:
        response = gemini_model.generate_content(content)
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned_text)
        
        # Save analysis to JSON file
        analysis_filename = f"analysis_{video_name}.json"
        analysis_path = os.path.join(output_folder, analysis_filename)
        with open(analysis_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"Gemini Analysis saved: {analysis_path}")
        return data
    except Exception as e:
        print(f"Error during Gemini analysis: {e}")
        return None

def process_video_task(video_path: str):
    video_filename = os.path.basename(video_path)
    video_name = os.path.splitext(video_filename)[0]
    
    # Create specific folder for this video in anomaly/
    video_anomaly_folder = os.path.join(ANOMALY_FOLDER, video_name)
    if not os.path.exists(video_anomaly_folder):
        os.makedirs(video_anomaly_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return

    input_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_skip = max(1, int(input_fps / TARGET_FPS))
    
    queue_frames = []
    frame_count = 0
    all_anomalous_batches = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_skip == 0:
            frame_resized = cv2.resize(frame, (224, 224))
            queue_frames.append(FrameData(frame_resized, datetime.now()))
        
        frame_count += 1
        
        if len(queue_frames) >= BATCH_SIZE:
            is_anomalous = process_batch(queue_frames)
            if is_anomalous:
                all_anomalous_batches.append(list(queue_frames))
                print(f"Anomaly detected in batch ending at frame {frame_count}")
                # Save frames to video-specific anomaly folder
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                for i, fd in enumerate(queue_frames[::FRAME_INTERVAL_FOR_GEMINI]):
                    frame_name = f"anomaly_{timestamp}_{frame_count}_{i}.jpg"
                    cv2.imwrite(os.path.join(video_anomaly_folder, frame_name), fd.frame)
            
            queue_frames = [] # Clear batch

    cap.release()
    
    if all_anomalous_batches:
        analyze_with_gemini(all_anomalous_batches[0], video_name, video_anomaly_folder)

    print(f"Processing complete for {video_path}")

@app.post("/process_video")
async def process_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    background_tasks.add_task(process_video_task, file_path)
    
    return {"message": "Video uploaded and processing started.", "filename": file.filename}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
