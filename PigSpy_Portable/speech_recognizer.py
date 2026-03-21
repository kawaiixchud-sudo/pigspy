import os
import threading
import io
import time
import numpy as np
from faster_whisper import WhisperModel
from pydub import AudioSegment
import queue


class SpeechRecognizer:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.model = None
        self.model_loading = False
        self.model_loaded = False
        self.buffer = bytearray()
        self.callback = None

        # Load model in background thread
        self._load_model_async()

    def _load_model_async(self):
        """Load Whisper model asynchronously to prevent blocking startup"""
        def _load():
            try:
                self.model_loading = True
                print("Loading Whisper model (this may take a moment)...")
                # Accuracy-first default model for scanner traffic.
                # Override with env var, e.g. PIGSPY_WHISPER_MODEL=tiny.en for speed.
                model_name = os.getenv("PIGSPY_WHISPER_MODEL", "base.en")
                self.model = WhisperModel(model_name, device="cpu", compute_type="int8")
                self.model_loaded = True
                self.model_loading = False
                print("Whisper model loaded successfully!")
            except Exception as e:
                print(f"Error loading Whisper model: {e}")
                self.model_loading = False

        load_thread = threading.Thread(target=_load, daemon=True)
        load_thread.start()

    def set_callback(self, callback):
        self.callback = callback

    def start_listening(self):
        self.is_running = True
        self.process_thread = threading.Thread(target=self._process_loop)
        self.process_thread.daemon = True
        self.process_thread.start()

    def stop_listening(self):
        self.is_running = False

    def add_audio_data(self, mp3_chunk: bytes):
        if not self.is_running:
            return
        try:
            segment = AudioSegment.from_file(io.BytesIO(mp3_chunk), format="mp3")
            segment = segment.set_frame_rate(16000).set_channels(1)
            self.buffer.extend(segment.raw_data)

            # Process every 4 seconds for better context/accuracy.
            if len(self.buffer) > 16000 * 2 * 4:
                audio_data = np.frombuffer(self.buffer, dtype=np.int16).astype(np.float32) / 32768.0
                self.audio_queue.put(audio_data)
                self.buffer = bytearray()
        except Exception:
            pass

    def _process_loop(self):
        while self.is_running:
            # Wait for model to be loaded
            if not self.model_loaded:
                time.sleep(0.1)
                continue

            try:
                audio_data = self.audio_queue.get(timeout=1)
                segments, _ = self.model.transcribe(
                    audio_data,
                    beam_size=8,
                    best_of=5,
                    language="en",
                    condition_on_previous_text=True,
                    vad_filter=True,
                    vad_parameters={"min_silence_duration_ms": 250},
                    initial_prompt=(
                        "Police scanner dispatch traffic, radar enforcement, and traffic stops. "
                        "Common words: speed, radar, clock, pace, laser, stop, mile, marker, plate, check, copy, clear, radio, unit, north, south, east, west, road, highway."
                    ),
                )
                for segment in segments:
                    text = segment.text.strip()
                    if text and self.callback:
                        self.callback(text)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Transcription error: {e}")
