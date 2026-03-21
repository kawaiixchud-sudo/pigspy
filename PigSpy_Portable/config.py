import os
from datetime import datetime

class Config:
    # Audio stream settings
    STREAM_URL = "YOUR_STREAM_URL_HERE"  # Replace with your broadcastify stream URL
    
    # Common Radar/Scanner Testing Keywords
    KEYWORDS = [
        'speed', 'radar', 'clock', 'pace', 'laser', 
        'stop', 'mile', 'marker', 'plate', 'check', 
        'copy', 'clear', 'radio', 'unit', 'north', 
        'south', 'east', 'west', 'road', 'highway'
    ]
    
    # Audio settings
    CHUNK_SIZE = 1024
    SAMPLE_RATE = 16000
    CHANNELS = 1
    FORMAT = 8
    
    # Speech Recognition Adaptation
    WHISPER_MODEL = "base"  # Using 'base' instead of 'tiny' for better accuracy with garbled speech
    ENERGY_THRESHOLD = 300  # Lower threshold to catch quieter/garbled speech
    DYNAMIC_ENERGY = True
    
    # Buffer settings
    TRANSCRIPTION_BUFFER_SIZE = 100
    CONTEXT_WORDS_BEFORE = 5
    CONTEXT_WORDS_AFTER = 5
    
    # Logging
    LOGS_DIR = "logs"
    EVENTS_DIR = os.path.join(LOGS_DIR, "events")
    
    # Notification settings
    NOTIFICATION_DURATION = 5
    
    @classmethod
    def setup_directories(cls):
        os.makedirs(cls.LOGS_DIR, exist_ok=True)
        os.makedirs(cls.EVENTS_DIR, exist_ok=True)