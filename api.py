"""
FraudSentinel AI – FastAPI Backend
Exposes the 6-layer agentic detection pipeline via REST + SSE.

IMPORTANT: All heavy imports (ScamDetectorOrchestrator, sentence-transformers,
torch, etc.) are done LAZILY inside request handlers so the server starts instantly.
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
import os
import sys
import tempfile
import traceback
from typing import Optional

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="FraudSentinel AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for the orchestrator (created lazily on first request)
_orchestrator_cache = {}


def _get_orchestrator(api_key, model, base_url):
    """Lazily import and create orchestrator. Caches by config."""
    cache_key = f"{api_key}:{model}:{base_url}"
    if cache_key not in _orchestrator_cache:
        from scam_detector import ScamDetectorOrchestrator
        _orchestrator_cache[cache_key] = ScamDetectorOrchestrator(
            api_key=api_key, model=model, base_url=base_url
        )
    return _orchestrator_cache[cache_key]


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/demos")
async def get_demos():
    """Return available demo transcripts (lazy import)."""
    try:
        from demo_transcripts import DEMO_TRANSCRIPTS
        return DEMO_TRANSCRIPTS
    except ImportError:
        return {}


@app.post("/analyze")
async def analyze_transcript(
    transcript: str = Form(...),
    api_key: Optional[str] = Form(None),
    model: str = Form("openai/gpt-4o-mini"),
    base_url: str = Form("https://openrouter.ai/api/v1"),
):
    """Analyze a transcript. Returns SSE stream of progress + final result."""
    if not transcript or not transcript.strip():
        raise HTTPException(status_code=400, detail="Empty transcript")

    if api_key is not None and not api_key.strip():
        api_key = None

    async def event_generator():
        # Let the frontend know we've connected and are starting
        yield f"data: {json.dumps({'type': 'progress', 'step': 1, 'message': 'Initializing AI Models...', 'progress': 10})}\n\n"

        queue = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def progress_callback(step, total, message):
            # Map the 6 layers to progress percentages (10% to 90%)
            if total > 0:
                p = 10 + int((step / total) * 80)
            else:
                p = 50
            
            event = {"type": "progress", "step": step, "message": message, "progress": p}
            loop.call_soon_threadsafe(queue.put_nowait, event)

        def run_analysis():
            try:
                loop.call_soon_threadsafe(queue.put_nowait, {"type": "progress", "step": 1, "message": "Warming up Semantic Models (may take ~15s on first run)...", "progress": 15})
                from scam_detector import ScamDetectorOrchestrator
                orchestrator = ScamDetectorOrchestrator(
                    api_key=api_key if api_key else None,
                    model=model,
                    base_url=base_url
                )
                loop.call_soon_threadsafe(queue.put_nowait, {"type": "progress", "step": 1, "message": "Starting concurrent analysis layers...", "progress": 20})
                result = orchestrator.analyze_transcript(transcript, progress_callback)
                loop.call_soon_threadsafe(queue.put_nowait, {"type": "result", "data": result})
            except Exception as e:
                import traceback
                error_msg = str(e)
                tb = traceback.format_exc()
                print(f"[API ERROR] {error_msg}\n{tb}")
                loop.call_soon_threadsafe(queue.put_nowait, {"type": "error", "message": error_msg})

        # Start analysis in a background thread
        loop.run_in_executor(None, run_analysis)

        # Stream events from the queue to the client
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
            if event["type"] in ["result", "error"]:
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    api_key: Optional[str] = Form(None),
    model: str = Form("openai/gpt-4o-mini"),
    base_url: str = Form("https://openrouter.ai/api/v1"),
):
    """Upload audio/video, transcribe it, return transcript."""
    try:
        from speech_to_text import SpeechAgent
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Speech-to-Text module not available. Install faster-whisper.",
        )

    content = await file.read()
    filename = file.filename or "upload.wav"
    file_ext = os.path.splitext(filename)[1].lower()

    try:
        agent = SpeechAgent()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load speech model: {str(e)}",
        )

    if not agent.is_available:
        raise HTTPException(
            status_code=503,
            detail="Speech-to-Text model is not available. Faster-Whisper could not be loaded.",
        )

    is_video = file_ext in [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    audio_content = content
    audio_ext = file_ext

    if is_video:
        try:
            from pydub import AudioSegment

            # Use mkstemp instead of NamedTemporaryFile to cleanly bypass Windows file locking
            fd_vid, tmp_vid_path = tempfile.mkstemp(suffix=file_ext)
            with os.fdopen(fd_vid, 'wb') as tmp_vid:
                tmp_vid.write(content)

            video = AudioSegment.from_file(tmp_vid_path)
            
            fd_aud, tmp_aud_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd_aud) # Close immediately, let pydub write to it
            
            video.export(tmp_aud_path, format="mp3")

            with open(tmp_aud_path, "rb") as f:
                audio_content = f.read()
            audio_ext = ".mp3"
            os.unlink(tmp_aud_path)
            os.unlink(tmp_vid_path)
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="pydub is required for video processing.",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Video extraction failed: {str(e)}"
            )

    transcript_text, error = agent.transcribe(audio_content, audio_ext)
    if error:
        raise HTTPException(status_code=500, detail=f"Transcription error: {error}")

    return {"transcript": transcript_text, "filename": filename}

# --- Serve React Frontend Static Files (For Hugging Face Spaces / Production) ---
if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")

    @app.exception_handler(404)
    async def custom_404_handler(request, __):
        # Fallback to index.html for React Router to handle client-side routing
        return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
