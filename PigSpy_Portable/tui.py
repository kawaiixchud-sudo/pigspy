from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Button, Static, Select, Label
from textual.containers import Container, Horizontal, Vertical, Grid
from datetime import datetime
import os
import time
from config import Config

class StreamSelector(Static):
    def compose(self) -> ComposeResult:
        states = [
            ("Kansas", "KS"), ("California", "CA"), ("Texas", "TX"), 
            ("New York", "NY"), ("Florida", "FL"), ("Illinois", "IL")
        ]
        yield Label("SELECT REGION (MAP REPLICA)")
        yield Select(states, id="state_select", prompt="Select State")
        yield Select([], id="city_select", prompt="Select City/County", disabled=True)
        yield Button("APPLY STREAM", id="apply_stream", variant="primary")

class PigSpyTUI(App):
    TITLE = "PigSpy - Police Scanner Monitor"
    CSS = """
    #main_container {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 3fr;
    }
    #sidebar {
        border: tall double white;
        padding: 1;
        background: $panel;
    }
    #controls {
        height: 3;
        margin: 1;
    }
    Button {
        margin-right: 1;
    }
    RichLog {
        border: solid green;
        margin: 1;
    }
    Select {
        margin-bottom: 1;
    }
    """

    def __init__(self, core=None):
        super().__init__()
        self.core = core
        self.is_monitoring = False
        self.city_data = {
            "KS": [("Sedgwick County Sheriff", "https://broadcastify.cdnstream1.com/19080"), ("Wichita Police", "https://broadcastify.cdnstream1.com/25124")],
            "CA": [("LAPD Dispatch", "https://broadcastify.cdnstream1.com/20296"), ("SFPD", "https://broadcastify.cdnstream1.com/23352")],
            "TX": [("Houston Police", "https://broadcastify.cdnstream1.com/25354"), ("Dallas Police", "https://broadcastify.cdnstream1.com/25355")]
        }
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main_container"):
            with Vertical(id="sidebar"):
                yield StreamSelector()
            with Vertical():
                with Horizontal(id="controls"):
                    yield Button("START", id="start", variant="success")
                    yield Button("STOP", id="stop", variant="error", disabled=True)
                    yield Button("AUDIO", id="audio_toggle", variant="default")
                    yield Button("SILENCE", id="silence_toggle", variant="default")
                    yield Button("NOTIF", id="notif_toggle", variant="default")
                    yield Button("CLEAR", id="clear_logs", variant="warning")
                yield RichLog(id="transcription_log", wrap=True, highlight=True, max_lines=5000)
        yield Footer()
    
    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "state_select":
            city_select = self.query_one("#city_select", Select)
            if event.value:
                cities = self.city_data.get(event.value, [])
                city_select.set_options([(name, url) for name, url in cities])
                city_select.disabled = False
            else:
                city_select.disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start": self.start_monitoring()
        elif event.button.id == "stop": self.stop_monitoring()
        elif event.button.id == "audio_toggle": self.toggle_audio()
        elif event.button.id == "silence_toggle": self.toggle_silence()
        elif event.button.id == "notif_toggle": self.toggle_notifications()
        elif event.button.id == "clear_logs": self.clear_logs()
        elif event.button.id == "apply_stream":
            url = self.query_one("#city_select", Select).value
            if url and url != Select.BLANK:
                Config.STREAM_URL = url
                self.add_transcription(f"Stream URL updated to: {url}")
                if self.is_monitoring:
                    self.add_transcription("Restart monitoring to apply new stream.")

    def on_mount(self) -> None:
        self.transcription_log = self.query_one("#transcription_log", RichLog)
        self.add_transcription("PigSpy starting up...")
        self.add_transcription("Select a State and City from the left panel to begin.")

    def start_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            if self.core: 
                self.core.start_monitoring()
                self.update_status_buttons()
            self.query_one("#start", Button).disabled = True
            self.query_one("#stop", Button).disabled = False
            self.add_transcription("Monitoring started...")

    def stop_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            if self.core: 
                self.core.stop_monitoring()
                self.update_status_buttons()
            self.query_one("#start", Button).disabled = False
            self.query_one("#stop", Button).disabled = True
            self.add_transcription("Monitoring stopped.")

    def toggle_audio(self):
        if self.core:
            result = self.core.toggle_audio_passthrough()
            self.add_transcription(f"Audio passthrough: {result}")
            self.update_status_buttons()

    def toggle_silence(self):
        if self.core:
            result = self.core.toggle_silence_mode()
            self.add_transcription(f"Silence mode: {result}")
            self.update_status_buttons()

    def toggle_notifications(self):
        if self.core:
            result = self.core.toggle_notifications()
            self.add_transcription(f"Notifications: {result}")
            self.update_status_buttons()

    def update_status_buttons(self):
        if not self.core: return
        audio_btn = self.query_one("#audio_toggle", Button)
        audio_btn.variant = "success" if self.core.audio_passthrough_enabled else "error"
        audio_btn.label = "AUDIO ON" if self.core.audio_passthrough_enabled else "AUDIO OFF"
        
        silence_btn = self.query_one("#silence_toggle", Button)
        silence_btn.variant = "warning" if self.core.silence_mode else "default"
        silence_btn.label = "SILENCE ON" if self.core.silence_mode else "SILENCE OFF"
        
        notif_btn = self.query_one("#notif_toggle", Button)
        notif_btn.variant = "success" if self.core.notifications_enabled else "error"
        notif_btn.label = "NOTIF ON" if self.core.notifications_enabled else "NOTIF OFF"

    def add_transcription(self, text: str):
        if not text.strip(): return
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.transcription_log.write(f"[{timestamp}] {text}")
        self.transcription_log.scroll_end()

    def clear_logs(self):
        self.transcription_log.clear()

    def exit_app(self):
        self.stop_monitoring()
        self.exit()