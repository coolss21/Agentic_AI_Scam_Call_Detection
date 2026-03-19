"""
FraudSentinel – Agent 1: Speech Agent
Converts uploaded audio files to text using Faster-Whisper.
"""

import os
import tempfile
from typing import Optional, Tuple


class SpeechAgent:
    """Agent 1 – Converts audio to transcript using Faster-Whisper."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
        self._available = False
        self._load_model()

    def _load_model(self):
        """Attempt to load the Faster-Whisper model."""
        try:
            from faster_whisper import WhisperModel

            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="auto",
            )
            self._available = True
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"[SpeechAgent] Warning: Could not load Faster-Whisper: {e}")
            print(f"[SpeechAgent] Error details: {error_details}")
            print("[SpeechAgent] Audio transcription will not be available.")
            self._available = False

    @property
    def is_available(self) -> bool:
        """Check if the speech model is loaded and ready."""
        return self._available

    def transcribe(self, audio_bytes: bytes, file_extension: str = ".wav") -> Tuple[str, Optional[str]]:
        """
        Transcribe audio bytes to text.

        Args:
            audio_bytes: Raw audio file bytes
            file_extension: File extension for temp file (e.g., '.wav', '.mp3')

        Returns:
            Tuple of (transcript_text, error_message)
            If successful, error_message is None.
            If failed, transcript_text is empty and error_message describes the issue.
        """
        if not self._available:
            return "", "Faster-Whisper model is not available. Please install faster-whisper."

        tmp_path = None
        try:
            # Create a unique temp file name using mkstemp to avoid Windows locking issues
            fd, tmp_path = tempfile.mkstemp(suffix=file_extension)
            with os.fdopen(fd, 'wb') as tmp:
                tmp.write(audio_bytes)

            segments, info = self.model.transcribe(
                tmp_path,
                beam_size=5,
                language=None,  # auto-detect
                vad_filter=True,
            )

            transcript_parts = []
            for segment in segments:
                transcript_parts.append(segment.text.strip())

            transcript = " ".join(transcript_parts).strip()

            if not transcript:
                return "", "No speech detected in the audio file."

            return transcript, None

        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            print(f"Error in transcribe: {str(e)}\n{tb}")
            return "", f"Error transcribing audio: {str(e)}\nTraceback: {tb}"
            
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass

    def transcribe_file(self, file_path: str) -> Tuple[str, Optional[str]]:
        """
        Transcribe an audio file from a file path.

        Args:
            file_path: Path to the audio file.

        Returns:
            Tuple of (transcript_text, error_message)
        """
        if not self._available:
            return "", "Faster-Whisper model is not available."

        try:
            with open(file_path, "rb") as f:
                audio_bytes = f.read()

            ext = os.path.splitext(file_path)[1]
            return self.transcribe(audio_bytes, ext)

        except FileNotFoundError:
            return "", f"Audio file not found: {file_path}"
        except Exception as e:
            return "", f"Error reading audio file: {str(e)}"
