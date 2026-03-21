from config import Config
from stream_handler import StreamHandler
from speech_recognizer import SpeechRecognizer
from tui import PigSpyTUI
from mp3_player import SimpleMP3Player
from keyword_detector import KeywordDetector
from notifier import Notifier


class PigSpyCore:
    def __init__(self):
        self.config = Config()
        self.recognizer = SpeechRecognizer(sample_rate=16000)
        self.stream_handler = StreamHandler(self.config.STREAM_URL, self.handle_audio_chunk)
        self.audio_player = SimpleMP3Player()
        self.audio_passthrough_enabled = True
        self.tui = None
        self.is_monitoring = False
        self.recognizer.set_callback(self.handle_transcription)
        
        # Initialize notification controls
        self.notifications_enabled = True
        self.silence_mode = True
        
        # Initialize keyword detector and notifier
        self.keyword_detector = KeywordDetector(self.config.KEYWORDS)
        self.notifier = Notifier()

    def handle_audio_chunk(self, chunk):
        if not self.is_monitoring:
            return
        self.recognizer.add_audio_data(chunk)

    def handle_transcription(self, text):
        if self.tui:
            self.tui.call_from_thread(self.tui.add_transcription, text)
        
        # Check for keywords and send notifications
        keyword_matches = self.keyword_detector.add_transcription(text)
        for keyword, context in keyword_matches:
            # Only send notification if notifications are enabled
            if self.notifications_enabled:
                # Send notification with keyword and context
                self.notifier.send_notification(keyword, context)
                
                # Also display in TUI for visual confirmation
                if self.tui:
                    self.tui.call_from_thread(
                        self.tui.add_transcription, 
                        f"🚨 KEYWORD DETECTED: '{keyword.upper()}'"
                    )

    def start_monitoring(self):
        if self.is_monitoring:
            return
        self.is_monitoring = True

        # Start audio passthrough via VLC/default player for stable playback.
        if self.audio_passthrough_enabled and self.audio_player:
            self.audio_player.play_stream(self.config.STREAM_URL)

        self.recognizer.start_listening()
        self.stream_handler.start()

    def stop_monitoring(self):
        if not self.is_monitoring:
            return
        self.is_monitoring = False
        self.stream_handler.stop()
        self.recognizer.stop_listening()
        if self.audio_player:
            self.audio_player.stop()
    
    def toggle_audio_passthrough(self):
        """Toggle audio passthrough"""
        self.audio_passthrough_enabled = not self.audio_passthrough_enabled
        if self.audio_passthrough_enabled:
            if self.is_monitoring and not self.silence_mode:
                self.audio_player.play_stream(self.config.STREAM_URL)
            return "Audio passthrough ON"
        else:
            if self.audio_player:
                self.audio_player.stop()
            return "Audio passthrough OFF"
    
    def toggle_silence_mode(self):
        """Toggle silence mode - notifications only, no audio"""
        self.silence_mode = not self.silence_mode
        if self.silence_mode:
            # Stop audio passthrough when in silence mode
            if self.audio_player:
                self.audio_player.stop()
            return "Silence mode ON - Notifications only"
        else:
            # Resume audio passthrough when leaving silence mode
            if self.audio_passthrough_enabled and self.audio_player and self.is_monitoring:
                self.audio_player.play_stream(self.config.STREAM_URL)
            return "Silence mode OFF - Audio + notifications"
    
    def toggle_notifications(self):
        """Toggle notification system"""
        self.notifications_enabled = not self.notifications_enabled
        if self.notifications_enabled:
            return "Notifications enabled"
        else:
            return "Notifications disabled"

    def run(self):
        self.tui = PigSpyTUI(core=self)
        self.tui.run()


if __name__ == "__main__":
    core = PigSpyCore()
    core.run()
