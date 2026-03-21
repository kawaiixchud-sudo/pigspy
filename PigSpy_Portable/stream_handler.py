import asyncio
import aiohttp
import threading
import queue
import time
import io
from typing import Callable, Optional
import numpy as np

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

class StreamHandler:
    def __init__(self, stream_url: str, callback: Callable[[bytes], None]):
        self.stream_url = stream_url
        self.callback = callback
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.session = None
        self.loop = None
        self.buffer = io.BytesIO()
        self.buffer_lock = threading.Lock()

    async def start_stream(self):
        """Start receiving audio stream from the URL"""
        self.is_running = True
        # Use a custom header to mimic a standard player and avoid some ad-injection triggers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Icy-MetaData': '1'
        }
        timeout = aiohttp.ClientTimeout(total=0)
        self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)

        try:
            # Use a specific URL parameter that sometimes bypasses pre-roll ads
            url = self.stream_url
            if '?' not in url:
                url += "?nocache=1&ad=0"
            
            async with self.session.get(url, allow_redirects=True) as response:
                content_type = response.headers.get('Content-Type', '')
                
                # If we get an HTML response instead of audio, it's likely an ad-gate
                if 'text/html' in content_type:
                    print("Ad-gate detected, retrying...")
                    await asyncio.sleep(1)
                    return await self.start_stream()

                metaint = int(response.headers.get('icy-metaint', 0))
                buffer = bytearray()
                
                async for chunk in response.content.iter_any():
                    if not self.is_running: break
                    
                    if metaint > 0:
                        buffer.extend(chunk)
                        while len(buffer) > metaint:
                            # Send audio data before metadata
                            if self.callback: self.callback(bytes(buffer[:metaint]))
                            
                            # Read metadata length byte
                            meta_len = buffer[metaint] * 16
                            meta_start = metaint + 1
                            meta_end = meta_start + meta_len
                            
                            if len(buffer) >= meta_end:
                                metadata = bytes(buffer[meta_start:meta_end]).decode('utf-8', errors='ignore')
                                if any(word in metadata.lower() for word in ['ad', 'commercial', 'preroll', 'spot']):
                                    print("Ad detected in metadata, reconnecting...")
                                    return await self.start_stream()
                                buffer = buffer[meta_end:]
                            else:
                                break
                    else:
                        if self.callback: self.callback(chunk)

        except Exception as e:
            print(f"Stream error: {e}")
        finally:
            if self.session:
                await self.session.close()

    def start(self):
        """Start the stream in a separate thread"""
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever)
        self.thread.daemon = True
        self.thread.start()
        asyncio.run_coroutine_threadsafe(self.start_stream(), self.loop)

    def stop(self):
        """Stop the stream"""
        self.is_running = False
        if self.loop and self.session:
            try:
                future = asyncio.run_coroutine_threadsafe(self.session.close(), self.loop)
                future.result(timeout=2)
            except:
                pass
        if self.loop:
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            except:
                pass

class AudioPlayer:
    """Audio player that handles MP3 stream chunks by decoding to PCM"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, format_: int = 8):
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self.sd = None
        self.volume = 1.0
        self.mp3_buffer = io.BytesIO()
        
        try:
            import sounddevice as sd
            self.sd = sd
            self.setup_stream()
        except Exception as e:
            print(f"Warning: sounddevice not available: {e}")

    def setup_stream(self):
        if not self.sd:
            return
        try:
            self.stream = self.sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16'
            )
            self.stream.start()
        except Exception as e:
            print(f"Failed to setup audio stream: {e}")

    def play_audio(self, mp3_chunk: bytes):
        """Decodes MP3 chunk and plays PCM"""
        if not HAS_PYDUB or not self.sd or not self.stream:
            return

        try:
            # We need enough data to decode a frame
            self.mp3_buffer.write(mp3_chunk)
            if self.mp3_buffer.tell() < 8192: # Buffer small chunks
                return

            self.mp3_buffer.seek(0)
            try:
                segment = AudioSegment.from_file(self.mp3_buffer, format="mp3")
                # Resample to match output
                segment = segment.set_frame_rate(self.sample_rate).set_channels(self.channels)
                samples = np.array(segment.get_array_of_samples(), dtype=np.int16)
                
                if self.volume != 1.0:
                    samples = (samples * self.volume).astype(np.int16)
                
                self.stream.write(samples)
            except:
                pass
            
            # Clear buffer but keep remainder if any (simplified for now)
            self.mp3_buffer = io.BytesIO()
        except Exception:
            pass

    def set_volume(self, volume: float):
        self.volume = max(0.0, volume)

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()