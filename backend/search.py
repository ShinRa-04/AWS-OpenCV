import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pickle
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
INDEX_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faiss_index.bin")
METADATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chunk_metadata.pkl")
VECTORIZER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tfidf_vectorizer.pkl")

print("Initializing search system...")

class ChunkSearchEngine:
    def __init__(self):
        self.index = None
        self.chunk_metadata = []
        self.vectorizer = None
        self.dimension = None
        
    def extract_text_from_chunk(self, chunk_data: Dict) -> str:
        """Extract searchable text from a chunk"""
        text_parts = []
        
        if "overall_scene" in chunk_data:
            scene = chunk_data["overall_scene"]
            
            # Add location
            if "location" in scene:
                text_parts.append(f"Location: {scene['location']}")
            
            # Add activity summary
            if "activity_summary" in scene:
                text_parts.append(f"Activity: {scene['activity_summary']}")
            
            # Add description
            if "description" in scene:
                text_parts.append(f"Description: {scene['description']}")
            
            # Add actors
            if "actors" in scene and scene["actors"]:
                text_parts.append(f"People involved: {', '.join(scene['actors'])}")
            
            # Add objects detected
            if "objects_detected" in scene and scene["objects_detected"]:
                text_parts.append(f"Objects: {', '.join(scene['objects_detected'])}")
            
            # Add suspicious objects
            if "suspicious_objects" in scene and scene["suspicious_objects"]:
                text_parts.append(f"Suspicious items: {', '.join(scene['suspicious_objects'])}")
            
            # Add anomaly reason
            if "anomaly_reason" in scene:
                text_parts.append(f"Reason flagged: {scene['anomaly_reason']}")
            
            # Add critical level
            if "critical_level" in scene:
                text_parts.append(f"Threat level: {scene['critical_level']}")
        
        return " | ".join(text_parts)
    
    def load_all_analysis_files(self) -> List[Dict]:
        """Load all analysis JSON files and extract chunks"""
        all_chunks = []
        
        if not os.path.exists(ANOMALY_FOLDER):
            print(f"Anomaly folder not found: {ANOMALY_FOLDER}")
            return all_chunks
        
        # Iterate through all video folders
        for video_folder in os.listdir(ANOMALY_FOLDER):
            video_path = os.path.join(ANOMALY_FOLDER, video_folder)
            
            if not os.path.isdir(video_path):
                continue
            
            # Look for analysis JSON file
            analysis_file = os.path.join(video_path, f"analysis_{video_folder}.json")
            
            if os.path.exists(analysis_file):
                try:
                    with open(analysis_file, 'r') as f:
                        analysis_data = json.load(f)
                    
                    # Extract chunks from this video
                    if "anomalous_chunks" in analysis_data:
                        for chunk in analysis_data["anomalous_chunks"]:
                            chunk_info = {
                                "video_name": video_folder,
                                "video_metadata": analysis_data.get("video_metadata", {}),
                                "chunk_data": chunk,
                                "text_content": self.extract_text_from_chunk(chunk)
                            }
                            all_chunks.append(chunk_info)
                            
                    print(f"Loaded {len(analysis_data.get('anomalous_chunks', []))} chunks from {video_folder}")
                    
                except Exception as e:
                    print(f"Error loading analysis file {analysis_file}: {e}")
        
        print(f"Total chunks loaded: {len(all_chunks)}")
        return all_chunks
    
    def build_index(self):
        """Build FAISS index from all analysis chunks using TF-IDF"""
        print("Building FAISS index with TF-IDF...")
        
        # Load all chunks
        all_chunks = self.load_all_analysis_files()
        
        if not all_chunks:
            print("No chunks found to index")
            return
        
        # Extract text content
        texts = [chunk["text_content"] for chunk in all_chunks]
        print(f"Generating TF-IDF vectors for {len(texts)} chunks...")
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Fit and transform texts
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        embeddings = tfidf_matrix.toarray().astype('float32')
        
        self.dimension = embeddings.shape[1]
        print(f"TF-IDF dimension: {self.dimension}")
        
        # Create FAISS index
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        self.index.add(embeddings)
        
        # Store metadata
        self.chunk_metadata = all_chunks
        
        # Save index and metadata
        self.save_index()
        
        print(f"FAISS index built successfully with {self.index.ntotal} chunks")
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        if self.index is not None:
            faiss.write_index(self.index, INDEX_FILE)
            print(f"Index saved to {INDEX_FILE}")
        
        with open(METADATA_FILE, 'wb') as f:
            pickle.dump(self.chunk_metadata, f)
        print(f"Metadata saved to {METADATA_FILE}")
        
        if self.vectorizer is not None:
            with open(VECTORIZER_FILE, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            print(f"Vectorizer saved to {VECTORIZER_FILE}")
    
    def load_index(self):
        """Load FAISS index and metadata from disk"""
        if (os.path.exists(INDEX_FILE) and 
            os.path.exists(METADATA_FILE) and 
            os.path.exists(VECTORIZER_FILE)):
            try:
                self.index = faiss.read_index(INDEX_FILE)
                
                with open(METADATA_FILE, 'rb') as f:
                    self.chunk_metadata = pickle.load(f)
                
                with open(VECTORIZER_FILE, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                self.dimension = self.index.d
                print(f"Index loaded successfully with {self.index.ntotal} chunks")
                return True
            except Exception as e:
                print(f"Error loading index: {e}")
                return False
        return False
    
    def should_rebuild_index(self) -> bool:
        """Check if index needs rebuilding based on file timestamps"""
        if not os.path.exists(INDEX_FILE) or not os.path.exists(METADATA_FILE):
            return True
        
        # Get index file timestamp
        index_time = os.path.getmtime(INDEX_FILE)
        
        # Check all analysis files for newer timestamps
        if not os.path.exists(ANOMALY_FOLDER):
            return False
        
        for video_folder in os.listdir(ANOMALY_FOLDER):
            video_path = os.path.join(ANOMALY_FOLDER, video_folder)
            if not os.path.isdir(video_path):
                continue
            
            analysis_file = os.path.join(video_path, f"analysis_{video_folder}.json")
            if os.path.exists(analysis_file):
                analysis_time = os.path.getmtime(analysis_file)
                if analysis_time > index_time:
                    print(f"Found newer analysis file: {analysis_file}")
                    return True
        
        return False
    
    def auto_update_index_if_needed(self):
        """Automatically update index if new analysis files are found"""
        if self.should_rebuild_index():
            print("🔄 Auto-updating search index with new analysis files...")
            self.build_index()
            return True
        return False
        """Search for similar chunks"""
        if self.index is None or self.vectorizer is None:
            raise ValueError("Index not loaded. Please build or load index first.")
        
        # Generate query embedding using TF-IDF
        query_tfidf = self.vectorizer.transform([query]).toarray().astype('float32')
        faiss.normalize_L2(query_tfidf)
        
        # Search
        scores, indices = self.index.search(query_tfidf, top_k)
        
        # Prepare results
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.chunk_metadata):
                result = {
                    "rank": i + 1,
                    "similarity_score": float(score),
                    "video_name": self.chunk_metadata[idx]["video_name"],
                    "video_metadata": self.chunk_metadata[idx]["video_metadata"],
                    "chunk_data": self.chunk_metadata[idx]["chunk_data"],
                    "matched_text": self.chunk_metadata[idx]["text_content"]
                }
                results.append(result)
        
        return results

# Initialize search engine
search_engine = ChunkSearchEngine()

# Try to load existing index, otherwise build new one
if not search_engine.load_index():
    print("No existing index found. Building new index...")
    search_engine.build_index()

@app.get("/")
async def root():
    return {"message": "Video Analysis Search API", "status": "running"}

@app.get("/videos")
async def list_videos():
    """Get list of all processed videos"""
    # Auto-update index if needed
    search_engine.auto_update_index_if_needed()
    
    videos = []
    
    if not os.path.exists(ANOMALY_FOLDER):
        return {"videos": videos}
    
    for video_folder in os.listdir(ANOMALY_FOLDER):
        video_path = os.path.join(ANOMALY_FOLDER, video_folder)
        
        if not os.path.isdir(video_path):
            continue
        
        analysis_file = os.path.join(video_path, f"analysis_{video_folder}.json")
        
        if os.path.exists(analysis_file):
            try:
                with open(analysis_file, 'r') as f:
                    analysis_data = json.load(f)
                
                video_info = {
                    "video_name": video_folder,
                    "metadata": analysis_data.get("video_metadata", {}),
                    "anomalous_chunks_count": len(analysis_data.get("anomalous_chunks", [])),
                    "analysis_file": analysis_file
                }
                videos.append(video_info)
                
            except Exception as e:
                print(f"Error reading {analysis_file}: {e}")
    
    return {"videos": videos, "total_count": len(videos)}

@app.get("/search")
async def search_chunks(query: str, top_k: int = 5):
    """Search for similar chunks across all videos"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Auto-update index if needed
    search_engine.auto_update_index_if_needed()
    
    try:
        results = search_engine.search(query, top_k)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/rebuild_index")
async def rebuild_index():
    """Rebuild the search index with latest data"""
    try:
        search_engine.build_index()
        return {"message": "Index rebuilt successfully", "total_chunks": search_engine.index.ntotal}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rebuild index: {str(e)}")

@app.get("/index_stats")
async def get_index_stats():
    """Get statistics about the search index"""
    if search_engine.index is None:
        return {"status": "No index loaded"}
    
    return {
        "total_chunks": search_engine.index.ntotal,
        "dimension": search_engine.dimension,
        "index_file_exists": os.path.exists(INDEX_FILE),
        "metadata_file_exists": os.path.exists(METADATA_FILE),
        "last_modified": datetime.fromtimestamp(os.path.getmtime(INDEX_FILE)).isoformat() if os.path.exists(INDEX_FILE) else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)