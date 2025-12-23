#!/usr/bin/env python3
"""
Startup script to run both video analysis and search services
"""

import subprocess
import time
import sys
import os

def start_service(script_name, port, service_name):
    """Start a service in a separate process"""
    print(f"🚀 Starting {service_name} on port {port}...")
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        f"{script_name}:app", 
        "--host", "0.0.0.0", 
        "--port", str(port),
        "--reload"
    ]
    
    process = subprocess.Popen(
        cmd,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    return process

if __name__ == "__main__":
    print("🎬 OpenSeeWe Video Analysis System")
    print("=" * 50)
    
    # Start video analysis service (port 8000)
    analysis_process = start_service("indexing_video", 8000, "Video Analysis Service")
    
    # Wait a moment
    time.sleep(2)
    
    # Start search service (port 8001)  
    search_process = start_service("search", 8001, "Search Service")
    
    print("\n✅ Services Started Successfully!")
    print("-" * 50)
    print("📹 Video Analysis API: http://localhost:8000")
    print("🔍 Search API: http://localhost:8001")
    print("📖 API Documentation:")
    print("   - Analysis: http://localhost:8000/docs")
    print("   - Search: http://localhost:8001/docs")
    print("-" * 50)
    print("Press Ctrl+C to stop all services")
    
    try:
        # Keep both processes running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if analysis_process.poll() is not None:
                print("❌ Video Analysis service stopped")
                break
                
            if search_process.poll() is not None:
                print("❌ Search service stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        
        # Terminate processes
        analysis_process.terminate()
        search_process.terminate()
        
        # Wait for clean shutdown
        analysis_process.wait()
        search_process.wait()
        
        print("✅ All services stopped")