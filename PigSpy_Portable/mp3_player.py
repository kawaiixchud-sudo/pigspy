"""
Simple MP3 Stream Player for Windows
Uses VLC or system player for MP3 playback
"""

import sys
import subprocess
import threading
import tempfile
import os

class SimpleMP3Player:
    """
    Simple MP3 player that works on Windows
    Tries VLC first, then falls back to system player
    """
    
    def __init__(self):
        self.vlc = None
        self.instance = None
        self.player = None
        self.is_playing = False
        self.temp_file = None
        self._setup_vlc()
    
    def _setup_vlc(self):
        """Setup VLC player"""
        try:
            import vlc
            self.vlc = vlc
            self.instance = vlc.Instance('--no-video')
            print("VLC player ready")
        except ImportError:
            print("VLC not available, using fallback mode")
            self.vlc = None
    
    def play_stream(self, url: str):
        """Play stream from URL"""
        if self.vlc and self.instance:
            try:
                self.player = self.instance.media_player_new()
                media = self.instance.media_new(url)
                self.player.set_media(media)
                self.player.play()
                self.is_playing = True
                print(f"Playing stream via VLC: {url}")
                return True
            except Exception as e:
                print(f"VLC playback error: {e}")
        
        # Fallback: try to open in default player
        return self._open_in_default_player(url)
    
    def _open_in_default_player(self, url: str):
        """Open stream in system default player"""
        try:
            if sys.platform == 'win32':
                # Windows - use start command
                subprocess.Popen(['start', url], shell=True)
                print(f"Opened stream in default player")
                self.is_playing = True
                return True
            elif sys.platform == 'darwin':
                # macOS
                subprocess.Popen(['open', url])
                self.is_playing = True
                return True
            else:
                # Linux
                subprocess.Popen(['xdg-open', url])
                self.is_playing = True
                return True
        except Exception as e:
            print(f"Failed to open in default player: {e}")
            return False
    
    def stop(self):
        """Stop playback"""
        if self.player:
            try:
                self.player.stop()
            except:
                pass
        self.is_playing = False
    
    def toggle_pause(self):
        """Toggle pause"""
        if self.player:
            self.player.pause()


class PyDubPlayer:
    """
    MP3 player using pydub for decoding
    Requires: pip install pydub
    Also requires ffmpeg installed on system
    """
    
    def __init__(self):
        self.sd = None
        self.is_running = False
        self._setup()
    
    def _setup(self):
        """Setup audio output"""
        try:
            import sounddevice as sd
            self.sd = sd
        except ImportError:
            print("sounddevice not available")
    
    def play_mp3_data(self, mp3_bytes: bytes):
        """Play MP3 data"""
        if not self.sd:
            return
        
        try:
            from pydub import AudioSegment
            from io import BytesIO
            import numpy as np
            
            # Decode MP3
            segment = AudioSegment.from_file(BytesIO(mp3_bytes), format="mp3")
            
            # Convert to numpy
            samples = np.array(segment.get_array_of_samples())
            
            # Reshape for stereo
            if segment.channels == 2:
                samples = samples.reshape((-1, 2))
            
            # Play
            self.sd.play(samples, segment.frame_rate)
            
        except ImportError:
            print("pydub not available - install with: pip install pydub")
        except Exception as e:
            pass  # Silently fail


def test_audio():
    """Test audio playback"""
    print("Testing audio...")
    
    # Test 1: Try VLC
    player = SimpleMP3Player()
    print(f"VLC available: {player.vlc is not None}")
    
    # Test 2: Try PyDub
    try:
        from pydub import AudioSegment
        print("pydub available: Yes")
    except ImportError:
        print("pydub available: No - install with: pip install pydub")
    
    # Test 3: Try sounddevice
    try:
        import sounddevice as sd
        print("sounddevice available: Yes")
    except ImportError:
        print("sounddevice available: No")

if __name__ == "__main__":
    test_audio()
