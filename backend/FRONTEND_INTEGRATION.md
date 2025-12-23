# Frontend Integration Guide

## ✅ **No More Placeholder Text!**

The API has been updated to **never return placeholder text** like "Summary is being generated...". Instead, the frontend should **keep polling** until the real summary is ready.

## 🔄 **Alert Page Integration**

### **Polling for Summary (Recommended)**

```javascript
async function pollForSummary(videoName, maxAttempts = 60, intervalMs = 3000) {
    let attempts = 0;
    
    const poll = async () => {
        try {
            const response = await fetch(`/summary/${videoName}`);
            const data = await response.json();
            
            if (data.status === "complete" && data.summary) {
                // ✅ Summary is ready - display it!
                displaySummary(data.summary, data.metadata);
                return;
            }
            
            if (data.status === "processing") {
                // Still processing - continue polling
                attempts++;
                if (attempts < maxAttempts) {
                    setTimeout(poll, intervalMs);
                } else {
                    showError("Summary generation timed out");
                }
            } else if (data.status === "error") {
                showError(data.message);
            } else if (data.status === "not_found") {
                showError("Video not found");
            }
            
        } catch (error) {
            console.error("Error polling summary:", error);
            attempts++;
            if (attempts < maxAttempts) {
                setTimeout(poll, intervalMs);
            } else {
                showError("Failed to get summary");
            }
        }
    };
    
    // Start polling
    poll();
}

// Usage after video upload
function onVideoUploaded(videoName) {
    showMessage("Video uploaded successfully. Generating analysis...");
    pollForSummary(videoName);
}

function displaySummary(summary, metadata) {
    document.getElementById('analysis-result').innerHTML = `
        <h2>Analysis Result</h2>
        <div class="summary">
            <h3>Executive Summary</h3>
            <p>${summary}</p>
        </div>
        <div class="metadata">
            <p><strong>Duration:</strong> ${metadata.total_duration}s</p>
            <p><strong>Anomalous Chunks:</strong> ${metadata.anomalous_chunks_count}</p>
        </div>
    `;
}
```

### **Alternative: Using Status Endpoint**

```javascript
async function pollVideoStatus(videoName) {
    const response = await fetch(`/status/${videoName}`);
    const data = await response.json();
    
    if (data.status === "complete" && data.ready) {
        // Analysis is complete, now get the summary
        pollForSummary(videoName);
    } else if (data.status === "processing") {
        // Show progress
        updateProgress(data.progress, data.message);
        setTimeout(() => pollVideoStatus(videoName), 2000);
    }
}
```

## 🔍 **Search Page Integration**

### **List Videos and Search**

```javascript
// List all processed videos
async function loadVideos() {
    try {
        const response = await fetch('/videos');
        const data = await response.json();
        
        displayVideoList(data.videos);
    } catch (error) {
        console.error("Error loading videos:", error);
    }
}

// Perform semantic search
async function searchVideos(query) {
    if (!query.trim()) return;
    
    try {
        const response = await fetch(`/search?query=${encodeURIComponent(query)}&top_k=10`);
        const data = await response.json();
        
        displaySearchResults(data.results, data.query);
    } catch (error) {
        console.error("Error searching:", error);
    }
}

function displaySearchResults(results, query) {
    const container = document.getElementById('search-results');
    
    if (results.length === 0) {
        container.innerHTML = `<p>No results found for "${query}"</p>`;
        return;
    }
    
    const html = results.map(result => `
        <div class="search-result">
            <h3>Video: ${result.video_name}</h3>
            <p><strong>Similarity Score:</strong> ${result.similarity_score.toFixed(3)}</p>
            <p><strong>Time Range:</strong> ${result.chunk_data.chunk_metadata.start_time}s - ${result.chunk_data.chunk_metadata.end_time}s</p>
            <p><strong>Location:</strong> ${result.chunk_data.overall_scene.location}</p>
            <p><strong>Activity:</strong> ${result.chunk_data.overall_scene.activity_summary}</p>
            <p><strong>Critical Level:</strong> ${result.chunk_data.overall_scene.critical_level}</p>
            <details>
                <summary>Full Description</summary>
                <p>${result.chunk_data.overall_scene.description}</p>
            </details>
        </div>
    `).join('');
    
    container.innerHTML = html;
}
```

## 📋 **API Response Examples**

### **Summary Endpoint Responses**

**While Processing:**
```json
{
  "status": "processing",
  "message": "Analysis complete, summary generation in progress"
}
```

**When Complete:**
```json
{
  "status": "complete",
  "video_name": "video_1",
  "summary": "The 28.2-second video analysis indicates a High overall security threat level...",
  "metadata": {
    "filename": "video_1.mp4",
    "total_duration": 28.17,
    "total_chunks": 3,
    "anomalous_chunks_count": 3
  },
  "anomalous_chunks_count": 3
}
```

### **Search Results**

```json
{
  "query": "physical altercation",
  "results": [
    {
      "rank": 1,
      "similarity_score": 0.201,
      "video_name": "video_2",
      "chunk_data": {
        "overall_scene": {
          "location": "Indoor corridor",
          "activity_summary": "A physical altercation breaks out...",
          "description": "Full forensic description...",
          "critical_level": "High"
        },
        "chunk_metadata": {
          "start_time": 0.0,
          "end_time": 10.0
        }
      }
    }
  ],
  "total_results": 1
}
```

## ⚡ **Key Points**

1. **No Placeholder Text**: API never returns "Summary is being generated..."
2. **Keep Polling**: Frontend must poll `/summary/{video_name}` until `status: "complete"`
3. **Real Content Only**: Summary is only returned when it's actually ready
4. **Auto-Index Updates**: Search endpoints automatically update FAISS index
5. **Complete Chunk Data**: Search results include full forensic analysis details

The system now provides a clean, professional experience without any placeholder text!