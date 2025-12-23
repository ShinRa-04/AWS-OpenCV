import requests
import os

url = "http://localhost:8000/process_video"
video_path = "c:\\Projects\\OpenSeeWe-SIH25197-Prototype-Website\\backend_old\\videos\\video_2.mp4"

if not os.path.exists(video_path):
    print(f"Video file not found: {video_path}")
else:
    with open(video_path, "rb") as f:
        files = {"file": (os.path.basename(video_path), f, "video/mp4")}
        response = requests.post(url, files=files)
        print(response.status_code)
        print(response.json())
