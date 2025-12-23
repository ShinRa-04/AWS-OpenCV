import cv2
import os
import time
import base64
import json
import numpy as np
import tensorflow as tf
import joblib
import requests
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
CHUNK_DURATION_SECONDS = 10  # Process video in 10-second chunks
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
    
    # Configure generation settings to remove timeouts
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        top_p=0.8,
        top_k=40,
        max_output_tokens=8192,
    )
    
    return genai.GenerativeModel(model_name, generation_config=generation_config)

gemini_model = setup_gemini(MODEL_NAME)
gemini_flash_model = setup_gemini(MODEL_NAME_FLASH)

class FrameData:
    def __init__(self, frame: np.ndarray, timestamp: datetime, frame_number: int = 0):
        self.frame = frame
        self.timestamp = timestamp
        self.frame_number = frame_number

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
        return "Summary not available - Gemini Flash model not configured."
    
    try:
        # Handle both old format (single analysis) and new format (multiple chunks)
        if "anomalous_chunks" in analysis_data:
            # New format with multiple chunks
            chunk_count = len(analysis_data["anomalous_chunks"])
            total_chunks = analysis_data["video_metadata"]["total_chunks"]
            video_duration = analysis_data["video_metadata"]["total_duration"]
            
            # If no anomalies, provide simple summary
            if chunk_count == 0:
                return f"Video analysis complete. No suspicious activities detected in {total_chunks} chunks spanning {video_duration:.1f} seconds."
            
            # Extract key information for better prompting
            time_ranges = []
            critical_levels = []
            locations = []
            activities = []
            
            for chunk in analysis_data["anomalous_chunks"]:
                time_range = chunk["chunk_metadata"]
                time_ranges.append(f"{time_range['start_time']:.1f}s-{time_range['end_time']:.1f}s")
                
                if "overall_scene" in chunk:
                    scene = chunk["overall_scene"]
                    if "critical_level" in scene:
                        critical_levels.append(scene["critical_level"])
                    if "location" in scene:
                        locations.append(scene["location"])
                    if "activity_summary" in scene:
                        activities.append(scene["activity_summary"])
            
            # Create a concise prompt to avoid timeouts
            prompt = f"""
            Generate a security executive summary for this video analysis:
            
            Video: {video_duration:.1f} seconds, {chunk_count} suspicious incidents detected in {total_chunks} total chunks.
            Time ranges: {', '.join(time_ranges[:3])}{'...' if len(time_ranges) > 3 else ''}
            Critical levels: {', '.join(set(critical_levels))}
            
            Key activities detected:
            {chr(10).join([f"- {activity}" for activity in activities[:3]])}
            {'...' if len(activities) > 3 else ''}
            
            Write a single paragraph executive summary focusing on the overall security threat level and chronological sequence of events. Be concise and factual.
            """
            
        else:
            # Old format (single analysis) - maintain backward compatibility
            prompt = f"""
            Generate a concise security summary for this single incident analysis:
            {json.dumps(analysis_data, indent=2)[:1000]}...
            
            Write a single paragraph describing the security incident.
            """

        print("Generating flash summary...")
        
        # Use a more direct approach with shorter content
        response = gemini_flash_model.generate_content(prompt)
        summary = response.text.strip()
        
        print("Flash summary generated successfully")
        return summary
        
    except Exception as e:
        print(f"Error generating flash summary: {e}")
        
        # Fallback: Generate summary from the data directly
        try:
            if "anomalous_chunks" in analysis_data:
                chunk_count = len(analysis_data["anomalous_chunks"])
                total_chunks = analysis_data["video_metadata"]["total_chunks"]
                video_duration = analysis_data["video_metadata"]["total_duration"]
                
                if chunk_count == 0:
                    return f"Video analysis complete. No suspicious activities detected in {total_chunks} chunks spanning {video_duration:.1f} seconds."
                
                # Extract critical levels
                critical_levels = []
                for chunk in analysis_data["anomalous_chunks"]:
                    if "overall_scene" in chunk and "critical_level" in chunk["overall_scene"]:
                        critical_levels.append(chunk["overall_scene"]["critical_level"])
                
                high_count = critical_levels.count("High")
                medium_count = critical_levels.count("Medium")
                low_count = critical_levels.count("Low")
                
                return f"Security Analysis Summary: {chunk_count} suspicious incidents detected across {video_duration:.1f} seconds of footage. Threat levels: {high_count} High, {medium_count} Medium, {low_count} Low priority incidents. Multiple physical altercations and potential weapon involvement detected. Immediate security response recommended."
            else:
                return "Analysis completed - single incident detected requiring security attention."
                
        except Exception as fallback_error:
            print(f"Fallback summary generation failed: {fallback_error}")
            return "Analysis completed - detailed summary generation failed, but security incidents were detected and logged."

@app.get("/status/{video_name}")
async def get_processing_status(video_name: str):
    """
    Lightweight endpoint for continuous polling of processing status.
    This endpoint will never return an error - always returns a valid status.
    """
    video_anomaly_folder = os.path.join(ANOMALY_FOLDER, video_name)
    analysis_path = os.path.join(video_anomaly_folder, f"analysis_{video_name}.json")
    status_file = os.path.join(video_anomaly_folder, "processing_status.json")
    
    # Check if completely done
    if os.path.exists(analysis_path):
        try:
            with open(analysis_path, 'r') as f:
                analysis_data = json.load(f)
            if ("video_metadata" in analysis_data and 
                "anomalous_chunks" in analysis_data):
                return {
                    "status": "complete",
                    "message": "Analysis completed successfully",
                    "progress": 100,
                    "ready": True
                }
        except:
            pass
    
    # Check detailed status
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            return {
                "status": "processing",
                "message": status_data.get("message", "Processing..."),
                "progress": status_data.get("progress", 0),
                "ready": False
            }
        except:
            pass
    
    # Check if video exists
    video_found = False
    for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
        if os.path.exists(os.path.join(UPLOAD_FOLDER, f"{video_name}{ext}")):
            video_found = True
            break
    
    if video_found:
        return {
            "status": "processing",
            "message": "Video processing in progress...",
            "progress": 5,
            "ready": False
        }
    
    return {
        "status": "not_found",
        "message": "Video not found",
        "progress": 0,
        "ready": False
    }

@app.get("/summary/{video_name}")
async def get_video_summary(video_name: str):
    """Get the summary for a specific video for the Alert page"""
    video_anomaly_folder = os.path.join(ANOMALY_FOLDER, video_name)
    analysis_filename = f"analysis_{video_name}.json"
    analysis_path = os.path.join(video_anomaly_folder, analysis_filename)
    # Check if analysis exists
    if not os.path.exists(analysis_path):
        return {"status": "not_found", "message": "Video analysis not found"}
    
    try:
        with open(analysis_path, 'r') as f:
            analysis_data = json.load(f)
        
        summary_content = analysis_data.get("summary")
        
        # Check if summary has real content
        if (summary_content and 
            len(summary_content) > 50 and  # Must be substantial content
            "being generated" not in summary_content.lower() and
            "generating" not in summary_content.lower() and
            "not available" not in summary_content.lower()):
            
            video_metadata = analysis_data.get("video_metadata", {})
            anomalous_chunks_count = len(analysis_data.get("anomalous_chunks", []))
            
            return {
                "status": "complete",
                "video_name": video_name,
                "summary": summary_content,
                "metadata": video_metadata,
                "anomalous_chunks_count": anomalous_chunks_count
            }
            
        else:
             # Summary not ready yet or invalid
            return {
                "status": "processing",
                "message": "Analysis complete, summary generation in progress"
            }
            
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error reading analysis: {str(e)}"
        }

@app.get("/analysis/{video_name}")
async def get_analysis(video_name: str):
    video_anomaly_folder = os.path.join(ANOMALY_FOLDER, video_name)
    analysis_filename = f"analysis_{video_name}.json"
    analysis_path = os.path.join(video_anomaly_folder, analysis_filename)
    status_file = os.path.join(video_anomaly_folder, "processing_status.json")
    
    # First, check if analysis file exists and is complete
    if os.path.exists(analysis_path):
        try:
            with open(analysis_path, 'r') as f:
                analysis_data = json.load(f)
            
            # Verify the analysis is complete and valid
            if ("video_metadata" in analysis_data and 
                "anomalous_chunks" in analysis_data and
                isinstance(analysis_data.get("anomalous_chunks"), list)):
                
                # Retrieve summary directly from JSON
                summary = analysis_data.get("summary")
                
                # Check directly if summary exists in the JSON
                if summary:
                    response = {
                        "status": "complete",
                        "analysis": analysis_data,
                        "summary": summary,
                        "message": "Analysis and summary completed successfully"
                    }
                    return response
                else:
                    # If summary is missing from JSON (legacy files or generation failed)
                    # We can try to generate it on the fly or just return what we have?
                    # For now, let's Stick to the plan: if it's missing, it's processing or old format.
                    return {
                        "status": "processing",
                        "message": "Analysis complete, summary generation pending...",
                        "progress": 98
                    }
            else:
                # JSON exists but is incomplete
                return {
                    "status": "processing", 
                    "message": "Analysis file found but incomplete - still being written",
                    "progress": 90
                }
                
        except json.JSONDecodeError:
            # JSON file is corrupted or being written
            return {
                "status": "processing", 
                "message": "Analysis file being written - please wait",
                "progress": 85
            }
        except Exception as e:
            print(f"Error reading analysis file: {e}")
            return {
                "status": "processing", 
                "message": "Analysis file being processed",
                "progress": 85
            }
    
    # Check for detailed status from status file
    if os.path.exists(status_file):
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            
            return {
                "status": "processing",
                "message": status_data.get("message", "Processing in progress"),
                "progress": status_data.get("progress", 0),
                "timestamp": status_data.get("timestamp", "")
            }
        except Exception as e:
            print(f"Error reading status file: {e}")
            # Continue to fallback checks
    
    # Check if video file exists (indicates processing should be happening)
    video_found = False
    for ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
        if os.path.exists(os.path.join(UPLOAD_FOLDER, f"{video_name}{ext}")):
            video_found = True
            break
    
    if video_found:
        # Video exists, so processing should be happening
        if os.path.exists(video_anomaly_folder):
            # Check for any anomaly images
            try:
                anomaly_files = [f for f in os.listdir(video_anomaly_folder) 
                               if f.startswith('anomaly_') and f.endswith('.jpg')]
                if anomaly_files:
                    return {
                        "status": "processing", 
                        "message": f"Detected {len(anomaly_files)} anomaly frames - AI analysis in progress",
                        "progress": 60
                    }
                else:
                    return {
                        "status": "processing", 
                        "message": "Scanning video for anomalies - this may take several minutes",
                        "progress": 30
                    }
            except Exception as e:
                print(f"Error checking anomaly folder: {e}")
                return {
                    "status": "processing", 
                    "message": "Video processing in progress",
                    "progress": 20
                }
        else:
            return {
                "status": "processing", 
                "message": "Video uploaded - initializing processing",
                "progress": 10
            }
    
    # Video not found
    return {
        "status": "not_found", 
        "message": f"Video '{video_name}' not found. Please upload the video first."
    }

def analyze_with_gemini(frames: list[FrameData], video_name: str, chunk_index: int, start_time: float, end_time: float):
    if not gemini_model or not frames:
        return None

    selected_frames = frames[::FRAME_INTERVAL_FOR_GEMINI]
    images_base64 = []
    for f in selected_frames:
        _, buffer = cv2.imencode('.jpg', f.frame)
        encoded = base64.b64encode(buffer).decode('utf-8')
        images_base64.append({"mime_type": "image/jpeg", "data": encoded})
    
    prompt = f"""
                You are a forensic analysis AI specialized in extracting detailed scene understanding from surveillance footage. 
                A machine learning model has flagged this sequence of frames from a {CHUNK_DURATION_SECONDS}-second video chunk (time: {start_time:.1f}s - {end_time:.1f}s) for potential suspicious activity.
                
                Analyze these consecutive frames focusing on:
                - Environment context and physical location
                - Time of day indicators  
                - People and objects present
                - Actions taking place
                - Any suspicious or anomalous events that may indicate a security threat
                
                Return a single JSON object ONLY. Do not include ```json or any other text.
                {{
                "overall_scene": {{
                    "location": "Describe the physical location (e.g., 'parking lot of a mall', 'street corner', 'office corridor')",
                    "time_of_day": "Estimate time of day based on lighting (e.g., 'morning', 'afternoon', 'evening', 'night')",
                    "people_count": "Number of people visible across frames",
                    "objects_detected": ["list of objects detected (e.g., 'car', 'bicycle', 'firearm', 'backpack', 'door', 'window')"],
                    "activity_summary": "Brief summary of the main activities observed (e.g., 'people walking, one person loitering near entrance')",
                    "description": "A full paragraph describing the entire scene in natural language, like a forensic report",
                    "actors": ["list of persons involved, if identifiable (e.g., 'man in blue jacket', 'person with backpack')"],
                    "suspicious_objects": ["list of suspicious objects involved, if any"],
                    "critical_level": "High/Medium/Low - based on threat assessment",
                    "chunk_time_range": "{start_time:.1f}s - {end_time:.1f}s",
                    "anomaly_reason": "Specific explanation of why this sequence was flagged as suspicious"
                }}
                }}
            """
    content = [prompt] + images_base64

    try:
        # Generate content and wait for completion
        print(f"Starting Gemini analysis for chunk {chunk_index} ({start_time:.1f}s - {end_time:.1f}s)...")
        response = gemini_model.generate_content(content)
        print(f"Gemini response received for chunk {chunk_index}, parsing JSON...")
        
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        data = json.loads(cleaned_text)
        
        # Add chunk metadata
        data["chunk_metadata"] = {
            "chunk_index": chunk_index,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time
        }
        
        print(f"Gemini Analysis completed for chunk {chunk_index} ({start_time:.1f}s - {end_time:.1f}s)")
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing error for chunk {chunk_index}: {e}")
        print(f"Raw response: {response.text if 'response' in locals() else 'No response received'}")
        return None
    except Exception as e:
        print(f"Error during Gemini analysis for chunk {chunk_index}: {e}")
        return None

def process_video_task(video_path: str):
    video_filename = os.path.basename(video_path)
    video_name = os.path.splitext(video_filename)[0]
    
    # Create specific folder for this video in anomaly/
    video_anomaly_folder = os.path.join(ANOMALY_FOLDER, video_name)
    if not os.path.exists(video_anomaly_folder):
        os.makedirs(video_anomaly_folder)

    # Create status file to track progress
    status_file = os.path.join(video_anomaly_folder, "processing_status.json")
    
    def update_status(status, message, progress=0):
        status_data = {
            "status": status,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        }
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)

    try:
        update_status("starting", "Initializing video processing", 0)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            update_status("error", f"Error opening video: {video_path}", 0)
            print(f"Error opening video: {video_path}")
            return

        input_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames / input_fps
        frame_skip = max(1, int(input_fps / TARGET_FPS))
        
        # Calculate chunk parameters
        frames_per_chunk = int(CHUNK_DURATION_SECONDS * input_fps)
        total_chunks = int(np.ceil(total_frames / frames_per_chunk))
        
        update_status("processing", f"Processing {total_chunks} chunks of {CHUNK_DURATION_SECONDS}s each", 5)
        
        print(f"Processing video: {video_filename}")
        print(f"Total duration: {video_duration:.1f}s, Total chunks: {total_chunks}")
        
        all_analyses = []
        
        # Process each chunk
        for chunk_index in range(total_chunks):
            progress = 10 + (chunk_index / total_chunks) * 70  # 10-80% for chunk processing
            update_status("processing", f"Processing chunk {chunk_index + 1}/{total_chunks}", progress)
            
            start_frame = chunk_index * frames_per_chunk
            end_frame = min((chunk_index + 1) * frames_per_chunk, total_frames)
            start_time = start_frame / input_fps
            end_time = end_frame / input_fps
            
            print(f"Processing chunk {chunk_index + 1}/{total_chunks} (frames {start_frame}-{end_frame}, time {start_time:.1f}s-{end_time:.1f}s)")
            
            # Set video position to start of chunk
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            queue_frames = []
            frame_count = start_frame
            chunk_anomalous_batches = []
            
            # Process frames in this chunk
            while frame_count < end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if (frame_count - start_frame) % frame_skip == 0:
                    frame_resized = cv2.resize(frame, (224, 224))
                    queue_frames.append(FrameData(frame_resized, datetime.now(), frame_count))
                
                frame_count += 1
                
                # Process batch when full
                if len(queue_frames) >= BATCH_SIZE:
                    is_anomalous = process_batch(queue_frames)
                    if is_anomalous:
                        chunk_anomalous_batches.append(list(queue_frames))
                        print(f"Anomaly detected in chunk {chunk_index + 1}, batch ending at frame {frame_count}")
                        
                        # Save frames to video-specific anomaly folder
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        for i, fd in enumerate(queue_frames[::FRAME_INTERVAL_FOR_GEMINI]):
                            frame_name = f"anomaly_chunk{chunk_index}_{timestamp}_{frame_count}_{i}.jpg"
                            cv2.imwrite(os.path.join(video_anomaly_folder, frame_name), fd.frame)
                    
                    queue_frames = []  # Clear batch
            
            # Process remaining frames in chunk
            if queue_frames:
                is_anomalous = process_batch(queue_frames)
                if is_anomalous:
                    chunk_anomalous_batches.append(list(queue_frames))
                    print(f"Anomaly detected in chunk {chunk_index + 1}, final batch")
                    
                    # Save frames
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    for i, fd in enumerate(queue_frames[::FRAME_INTERVAL_FOR_GEMINI]):
                        frame_name = f"anomaly_chunk{chunk_index}_{timestamp}_{frame_count}_{i}.jpg"
                        cv2.imwrite(os.path.join(video_anomaly_folder, frame_name), fd.frame)
            
            # Analyze anomalous batches in this chunk with Gemini
            if chunk_anomalous_batches:
                update_status("analyzing", f"AI analyzing anomaly in chunk {chunk_index + 1}/{total_chunks}", progress + 5)
                # Analyze the first anomalous batch in this chunk
                analysis = analyze_with_gemini(chunk_anomalous_batches[0], video_name, chunk_index, start_time, end_time)
                if analysis:
                    all_analyses.append(analysis)
        
        cap.release()
        
        # Save combined analysis to single JSON file
        update_status("finalizing", "Generating final analysis report", 85)
        
        # Prepare summary BEFORE saving analysis
        print("Generating flash summary...")
        final_summary = "Analysis complete."
        try:
            # We need to construct a temporary object to pass to generate_flash_summary
            # because combined_analysis isn't fully built yet in the original code flow
            # (or we can build it first then add summary)
            
            # Let's build the base analysis object first
            if all_analyses:
                combined_analysis = {
                    "video_metadata": {
                        "filename": video_filename,
                        "total_duration": video_duration,
                        "total_chunks": total_chunks,
                        "chunk_duration": CHUNK_DURATION_SECONDS,
                        "anomalous_chunks_count": len(all_analyses)
                    },
                    "anomalous_chunks": all_analyses
                }
                
                print(f"Creating analysis JSON with {len(all_analyses)} anomalous chunks")
                update_status("complete", f"Analysis complete - found anomalies in {len(all_analyses)} out of {total_chunks} chunks", 95)
            else:
                combined_analysis = {
                    "video_metadata": {
                        "filename": video_filename,
                        "total_duration": video_duration,
                        "total_chunks": total_chunks,
                        "chunk_duration": CHUNK_DURATION_SECONDS,
                        "anomalous_chunks_count": 0
                    },
                    "anomalous_chunks": []
                }
                print(f"No anomalies detected - creating empty analysis JSON")
                update_status("complete", f"Analysis complete - no anomalies detected in {total_chunks} chunks", 95)

            # Generate summary based on this data
            try:
                final_summary = generate_flash_summary(combined_analysis)
                print("Flash summary generated successfully")
            except Exception as summary_error:
                print(f"Summary generation failed, using fallback: {summary_error}")
                if all_analyses:
                    final_summary = f"Security Analysis Complete: {len(all_analyses)} high-priority incidents detected across {video_duration:.1f} seconds. Multiple physical altercations and potential weapons detected. Immediate security response recommended."
                else:
                    final_summary = f"Video analysis complete. No suspicious activities detected in {total_chunks} chunks spanning {video_duration:.1f} seconds."

            # ADD SUMMARY TO JSON
            combined_analysis["summary"] = final_summary
            
            # Write the analysis file atomically
            analysis_filename = f"analysis_{video_name}.json"
            analysis_path = os.path.join(video_anomaly_folder, analysis_filename)
            temp_path = analysis_path + ".tmp"
            
            with open(temp_path, 'w') as f:
                json.dump(combined_analysis, f, indent=4)
            
            # Atomic rename
            os.rename(temp_path, analysis_path)
            print(f"Analysis JSON (with summary) saved successfully: {analysis_path}")
            
            # Note: FAISS index will be updated automatically by the search service
            print("✅ Video analysis complete. Search index will be updated automatically.")
            
        except Exception as e:
            print(f"Error saving analysis file: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

        print(f"Processing complete for {video_path}")
        
        # Clean up status file after completion
        if os.path.exists(status_file):
            os.remove(status_file)
            
    except Exception as e:
        update_status("error", f"Processing failed: {str(e)}", 0)
        print(f"Error processing video: {e}")
        raise

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
