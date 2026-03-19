import subprocess
import os
import sys
import time

def run_services():
    print("🚀 Starting FraudSentinel AI services...")
    
    # 1. Start FastAPI Backend
    print("📡 Initializing Backend (FastAPI)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # 2. Wait for backend to start
    time.sleep(2)
    
    # 3. Start React Frontend (Vite)
    print("🎨 Initializing Frontend (React)...")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=os.path.join(os.getcwd(), "frontend"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True if os.name == 'nt' else False
    )
    
    print("\n✅ System Operational!")
    print("🔗 Backend API: http://localhost:8000")
    print("🔗 Frontend UI: http://localhost:3000")
    print("\nPress Ctrl+C to terminate all services.\n")

    try:
        while True:
            # You can optionally read output here
            # line = backend_proc.stdout.readline()
            # if line: print(f"[BACKEND] {line.strip()}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Terminating services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done.")

if __name__ == "__main__":
    if not os.path.exists("frontend/node_modules"):
        print("⚠️ node_modules not found. Please run 'npm install' in the 'frontend' directory first.")
        sys.exit(1)
    run_services()
