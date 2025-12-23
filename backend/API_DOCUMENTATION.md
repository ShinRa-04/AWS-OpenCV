# OpenSeeWe Video Analysis System - API Documentation

## 🎬 Video Analysis Service (Port 8000)

### **Alert Page Endpoints**

#### Upload Video
```http
POST /process_video
Content-Type: multipart/form-data

Body: file (video file)
```
**Response:**
```json
{
  "message": "Video uploaded and processing started.",
  "filename": "video.mp4"
}
```

#### Get Video Summary (for Alert Page)
```http
GET /summary/{video_name}
```
**Response:**
```json
{
  "status": "complete",
  "video_name": "video_1",
  "summary": "Security Analysis Summary: 3 suspicious incidents detected...",
  "metadata": {
    "filename": "video_1.mp4",
    "total_duration": 28.17,
    "total_chunks": 3,
    "anomalous_chunks_count": 3
  },
  "anomalous_chunks_count": 3
}
```

#### Get Processing Status
```http
GET /status/{video_name}
```
**Response:**
```json
{
  "status": "processing|complete|not_found",
  "message": "Processing status message",
  "progress": 75,
  "ready": false
}
```

#### Get Full Analysis
```http
GET /analysis/{video_name}
```
**Response:**
```json
{
  "status": "complete",
  "analysis": {
    "video_metadata": {...},
    "anomalous_chunks": [...]
  },
  "summary": "Executive summary text"
}
```

---

## 🔍 Search Service (Port 8001)

### **Search Page Endpoints**

#### List All Processed Videos
```http
GET /videos
```
**Response:**
```json
{
  "videos": [
    {
      "video_name": "video_1",
      "metadata": {
        "filename": "video_1.mp4",
        "total_duration": 28.17,
        "total_chunks": 3,
        "anomalous_chunks_count": 3
      },
      "anomalous_chunks_count": 3
    }
  ],
  "total_count": 1
}
```

#### Semantic Search
```http
GET /search?query={search_text}&top_k={number}
```
**Example:**
```http
GET /search?query=physical%20altercation&top_k=5
```
**Response:**
```json
{
  "query": "physical altercation",
  "results": [
    {
      "rank": 1,
      "similarity_score": 0.201,
      "video_name": "video_2",
      "video_metadata": {
        "filename": "video_2.mp4",
        "total_duration": 47.8,
        "total_chunks": 5
      },
      "chunk_data": {
        "overall_scene": {
          "location": "Indoor corridor",
          "time_of_day": "Night",
          "people_count": 4,
          "activity_summary": "A physical altercation breaks out...",
          "description": "Full forensic description...",
          "actors": ["Man in suit", "Man in shirt"],
          "suspicious_objects": [],
          "critical_level": "High",
          "anomaly_reason": "Sudden physical assault detected"
        },
        "chunk_metadata": {
          "chunk_index": 0,
          "start_time": 0.0,
          "end_time": 10.0,
          "duration": 10.0
        }
      },
      "matched_text": "Location: Indoor corridor | Activity: Physical altercation..."
    }
  ],
  "total_results": 1
}
```

#### Rebuild Search Index
```http
POST /rebuild_index
```
**Response:**
```json
{
  "message": "Index rebuilt successfully",
  "total_chunks": 8
}
```

#### Get Index Statistics
```http
GET /index_stats
```
**Response:**
```json
{
  "total_chunks": 8,
  "dimension": 1000,
  "index_file_exists": true,
  "metadata_file_exists": true,
  "last_modified": "2025-12-23T08:31:47"
}
```

---

## 🔄 System Workflow

### **Alert Page Workflow:**
1. **Upload Video** → `POST /process_video`
2. **Check Status** → `GET /status/{video_name}` (poll until complete)
3. **Get Summary** → `GET /summary/{video_name}` (display alert summary)

### **Search Page Workflow:**
1. **List Videos** → `GET /videos` (show all processed videos)
2. **Search Query** → `GET /search?query=text` (semantic search)
3. **Display Results** → Show matching chunks with full details

### **Auto-Processing:**
- ✅ Video upload triggers analysis
- ✅ Analysis generates JSON with forensic details
- ✅ Summary is auto-generated and saved
- ✅ Search index is automatically updated
- ✅ Vector embeddings are created for semantic search

---

## 🚀 Starting the System

```bash
# Start both services
python backend/start_services.py

# Services will be available at:
# - Video Analysis: http://localhost:8000
# - Search: http://localhost:8001
```

---

## ✅ Verification Checklist

### **Alert Page Requirements:**
- ✅ Video upload functionality
- ✅ Auto-summary generation when video is processed
- ✅ Processing status tracking
- ✅ Summary display for alerts

### **Search Page Requirements:**
- ✅ List all successfully processed videos
- ✅ Query input for semantic search
- ✅ Auto-generation of vector embeddings when JSON is created
- ✅ Semantic search across multiple indexes (chunks)
- ✅ Display matching chunk information as-is
- ✅ Real-time index updates when new videos are processed