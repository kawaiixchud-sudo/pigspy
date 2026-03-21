import os
import json
from datetime import datetime
from typing import Dict, List
import threading
from config import Config

class Logger:
    def __init__(self):
        Config.setup_directories()
        self.main_log_file = os.path.join(Config.LOGS_DIR, "transcriptions.log")
        self.events_dir = Config.EVENTS_DIR
        self.lock = threading.Lock()
        
    def log_transcription(self, text: str):
        """Log transcription to main log file with rolling buffer"""
        with self.lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Append to main log
            with open(self.main_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {text}\n")
            
            # Maintain rolling buffer - keep only recent entries
            self._maintain_main_log_buffer()
    
    def log_keyword_event(self, keyword: str, context: str, full_text: str = ""):
        """Log keyword event with context to separate event file"""
        with self.lock:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            event_filename = f"event_{timestamp}_{keyword.replace(' ', '_')}.log"
            event_path = os.path.join(self.events_dir, event_filename)
            
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "keyword": keyword,
                "context": context,
                "full_text": full_text,
                "formatted_context": self._format_context_for_display(context)
            }
            
            with open(event_path, 'w', encoding='utf-8') as f:
                json.dump(event_data, f, indent=2, ensure_ascii=False)
    
    def _format_context_for_display(self, context: str) -> str:
        """Format context string for better readability"""
        # Extract the actual context from the [start:end] format
        if '] ' in context:
            return context.split('] ', 1)[1]
        return context
    
    def _maintain_main_log_buffer(self):
        """Maintain rolling buffer of main log file"""
        try:
            if os.path.exists(self.main_log_file):
                with open(self.main_log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Keep only the last N lines to prevent file from growing too large
                if len(lines) > Config.TRANSCRIPTION_BUFFER_SIZE:
                    lines = lines[-Config.TRANSCRIPTION_BUFFER_SIZE:]
                
                with open(self.main_log_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
        except Exception as e:
            print(f"Error maintaining log buffer: {e}")
    
    def get_recent_transcriptions(self, count: int = 10) -> List[str]:
        """Get recent transcriptions from main log"""
        try:
            if not os.path.exists(self.main_log_file):
                return []
            
            with open(self.main_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Return last N lines
            recent_lines = lines[-count:] if len(lines) >= count else lines
            return [line.strip() for line in recent_lines if line.strip()]
        except Exception as e:
            print(f"Error reading recent transcriptions: {e}")
            return []
    
    def get_keyword_events(self) -> List[Dict]:
        """Get all keyword event files"""
        events = []
        try:
            for filename in os.listdir(self.events_dir):
                if filename.startswith('event_') and filename.endswith('.log'):
                    filepath = os.path.join(self.events_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            event_data = json.load(f)
                            events.append(event_data)
                    except Exception as e:
                        print(f"Error reading event file {filename}: {e}")
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x['timestamp'], reverse=True)
            return events
        except Exception as e:
            print(f"Error getting keyword events: {e}")
            return []
    
    def clear_main_log(self):
        """Clear the main transcription log"""
        with self.lock:
            try:
                if os.path.exists(self.main_log_file):
                    os.remove(self.main_log_file)
            except Exception as e:
                print(f"Error clearing main log: {e}")
    
    def clear_event_logs(self):
        """Clear all event logs"""
        with self.lock:
            try:
                for filename in os.listdir(self.events_dir):
                    if filename.startswith('event_') and filename.endswith('.log'):
                        filepath = os.path.join(self.events_dir, filename)
                        os.remove(filepath)
            except Exception as e:
                print(f"Error clearing event logs: {e}")
    
    def get_log_stats(self) -> Dict:
        """Get statistics about logs"""
        try:
            main_log_size = os.path.getsize(self.main_log_file) if os.path.exists(self.main_log_file) else 0
            event_count = len([f for f in os.listdir(self.events_dir) if f.startswith('event_')])
            
            return {
                "main_log_size_bytes": main_log_size,
                "event_log_count": event_count,
                "main_log_entries": len(self.get_recent_transcriptions(1000)),  # Approximate
                "events_directory": self.events_dir
            }
        except Exception as e:
            print(f"Error getting log stats: {e}")
            return {"main_log_size_bytes": 0, "event_log_count": 0, "main_log_entries": 0, "events_directory": self.events_dir}

class LogManager:
    """Manager class to handle multiple loggers and log rotation"""
    
    def __init__(self):
        self.logger = Logger()
        self.daily_rotation_enabled = True
    
    def rotate_logs_if_needed(self):
        """Rotate logs daily if needed"""
        if self.daily_rotation_enabled:
            # Check if we need to rotate (simple daily rotation)
            today = datetime.now().strftime("%Y-%m-%d")
            # Implementation for daily rotation would go here
            pass