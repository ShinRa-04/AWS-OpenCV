import os
import re
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
ANOMALY_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anomaly")
TEMP_TXT_FILE = os.path.join(ANOMALY_FOLDER, "temp.txt")

print("Initializing Simple Text Search system...")

class Segment:
    def __init__(self, video_name: str, segment_id: str, time_range: str, threat_level: str, full_text: str):
        self.video_name = video_name
        self.segment_id = segment_id
        self.time_range = time_range
        self.threat_level = threat_level
        self.full_text = full_text

    def to_dict(self):
        # Parse basic info from full text for better frontend display
        details = {}
        for line in self.full_text.split('\n'):
            line = line.strip()
            if line.startswith("- The scene is located at:"):
                details['location'] = line.replace("- The scene is located at:", "").strip()
            elif line.startswith("- Summary of activity:"):
                details['activity'] = line.replace("- Summary of activity:", "").strip()
            elif line.startswith("- Detailed description:"):
                details['description'] = line.replace("- Detailed description:", "").strip()

        return {
            "video_name": self.video_name,
            "segment_id": self.segment_id,
            "time_range": self.time_range,
            "threat_level": self.threat_level,
            "full_text": self.full_text,
            "parsed_details": details
        }

class SimpleTextSearchEngine:
    def __init__(self):
        self.segments: List[Segment] = []
        self.load_data()

    def load_data(self):
        """Parse temp.txt into structured segments"""
        self.segments = []
        if not os.path.exists(TEMP_TXT_FILE):
            print(f"Error: {TEMP_TXT_FILE} not found.")
            return

        print(f"Loading data from {TEMP_TXT_FILE}...")
        
        try:
            with open(TEMP_TXT_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_video = None
            current_segment_lines = []
            capture_segment = False
            
            # Temporary storage for segment parsing
            seg_header_pattern = re.compile(r"Segment (\d+) \(Time: (.*?)\):")
            
            for line in lines:
                stripped = line.strip()
                
                # Detect Video Header
                if stripped.startswith("Analysis for Video:"):
                    current_video = stripped.replace("Analysis for Video:", "").strip()
                    continue

                # Detect Segment Start
                match = seg_header_pattern.search(stripped)
                if match:
                    # Save previous segment if exists
                    if capture_segment and current_segment_lines:
                        self._add_segment(current_video, current_segment_lines)
                        current_segment_lines = []

                    capture_segment = True
                    current_segment_lines.append(line) # Add header line
                    continue
                
                # If inside a segment or accumulating valid segment data (indented lines or blank lines)
                if capture_segment:
                     # Check if we hit a new non-segment block (like a new video header or separator)
                    if stripped.startswith("Analysis for Video:") or stripped.startswith("================"):
                         # Save previous segment
                        if current_segment_lines:
                            self._add_segment(current_video, current_segment_lines)
                        
                        capture_segment = False
                        current_segment_lines = []
                        
                        if stripped.startswith("Analysis for Video:"):
                            current_video = stripped.replace("Analysis for Video:", "").strip()
                    else:
                        current_segment_lines.append(line)

            # Add the very last segment
            if capture_segment and current_segment_lines:
                self._add_segment(current_video, current_segment_lines)

            print(f"Loaded {len(self.segments)} segments.")

        except Exception as e:
            print(f"Error parsing text file: {e}")

    def _add_segment(self, video_name, lines):
        if not lines:
            return
            
        full_text = "".join(lines).strip()
        header_line = lines[0].strip()
        
        # Parse metadata from header
        # Header format: "Segment 1 (Time: 0.0s - 10.0s):"
        match = re.search(r"Segment (\d+) \(Time: (.*?)\):", header_line)
        segment_id = match.group(1) if match else "Unknown"
        time_range = match.group(2) if match else "Unknown"
        
        # Find threat level
        threat_level = "Unknown"
        for line in lines:
            if "The threat level is marked as" in line:
                threat_level = line.split("marked as")[-1].strip().replace(".", "")
                break
        
        self.segments.append(Segment(video_name, segment_id, time_range, threat_level, full_text))

    def search(self, query: str) -> List[Dict]:
        """Case-insensitive keyword search"""
        if not query:
            return []
            
        query = query.lower()
        results = []
        
        for segment in self.segments:
            if query in segment.full_text.lower():
                results.append(segment.to_dict())
                
        return results

# Initialize search engine
search_engine = SimpleTextSearchEngine()

@app.get("/")
async def root():
    return {"message": "Simple Text Video Search API", "status": "running"}

@app.post("/rebuild_index")
async def rebuild_index():
    """Reloads the data from temp.txt"""
    try:
        search_engine.load_data()
        return {"message": "Data reloaded successfully", "total_segments": len(search_engine.segments)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload data: {str(e)}")

@app.get("/search")
async def search(query: str, top_k: int = 5):
    """Search for relevant segments"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        results = search_engine.search(query)
        
        # Limit results if needed, though simple search usually returns everything
        # We'll respect top_k just in case
        limited_results = results[:top_k]
        
        return {
            "query": query,
            "results": limited_results,
            "total_results": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/index_stats")
async def get_index_stats():
    """Get statistics about the loaded segments"""
    return {
        "total_segments": len(search_engine.segments),
        "source_file": TEMP_TXT_FILE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)