import threading
import time
import os
import sys
import subprocess
from datetime import datetime

# Cross-platform sound support
if sys.platform == 'win32':
    import winsound
else:
    # Use sounddevice for Linux/Mac
    try:
        import sounddevice as sd
        import numpy as np
    except ImportError:
        sd = None
        np = None

class Notifier:
    def __init__(self):
        self.notification_sound = self._setup_notification_sound()
        self._plyer_notification = None
        self._plyer_available = False
        self._winotify = None
        self._winotify_available = False
        self._init_notification_backends()
        self.last_notification_time = 0
        self.notification_cooldown = 1.0  # Reduced cooldown for testing

    def _setup_notification_sound(self):
        """Setup notification sound - cross-platform"""
        return None
    
    def _init_notification_backends(self):
        """Initialize notification backends with graceful fallback."""
        # Windows toast via winotify (preferred on Windows)
        if sys.platform == "win32":
            try:
                from winotify import Notification, audio
                self._winotify = (Notification, audio)
                self._winotify_available = True
            except Exception:
                self._winotify_available = False
        
        # Cross-platform fallback via plyer
        try:
            from plyer import notification as plyer_notification
            self._plyer_notification = plyer_notification
            self._plyer_available = True
        except Exception:
            self._plyer_available = False

    def _play_tone(self, frequency, duration):
        """Play a tone - cross-platform"""
        if sys.platform == 'win32':
            try:
                winsound.Beep(frequency, duration)
                return
            except:
                pass
        else:
            # Linux/Mac using sounddevice
            if sd is not None and np is not None:
                try:
                    sample_rate = 44100
                    t = np.linspace(0, duration/1000, int(sample_rate * duration/1000), False)
                    wave = np.sin(2 * np.pi * frequency * t)
                    sd.play(wave, sample_rate)
                    sd.wait()
                    return
                except:
                    pass
        # Fallback - just print
        print("🔊 BEEP", end=" ", flush=True)

    def play_alert_sound(self):
        """Play alert sound when keyword is detected - non-blocking"""
        try:
            # Play system beep in non-blocking way
            def _play_async():
                try:
                    self._play_tone(800, 200)  # Shorter, faster beeps
                    self._play_tone(1000, 150)  # Second beep at higher frequency
                except:
                    pass
            
            thread = threading.Thread(target=_play_async, daemon=True)
            thread.start()
        except:
            # Fallback to simple print if sound fails
            print("🚨 KEYWORD DETECTED!")
    
    def send_notification(self, keyword: str, context: str, max_chars: int = 240):
        """Send Windows notification with keyword and context - non-blocking"""
        try:
            # Check cooldown to prevent spam
            current_time = time.time()
            if current_time - self.last_notification_time < self.notification_cooldown:
                # Skip notification due to cooldown, just print to console
                print(f"[Cooldown] '{keyword.upper()}' detected")
                return

            # Truncate context to max characters
            truncated_context = context[:max_chars-30] + "..." if len(context) > max_chars-30 else context
            message = f"Phrase: {keyword.upper()}\nContext: {truncated_context}"
            title = "🚨 PigSpy Alert"

            # Send desktop notification (Windows toast preferred) - non-blocking
            self._send_windows_toast(title, message)

            # Play alert sound - non-blocking
            self.play_alert_sound()

            # Update last notification time
            self.last_notification_time = current_time

        except Exception as e:
            print(f"Notification error: {e}")
            # Fallback to console output
            print(f"🚨 ALERT: '{keyword.upper()}' detected!")
            print(f"Context: {context}")

    def _send_plyer_notification(self, title: str, message: str):
        """Send notification via plyer if available - non-blocking."""
        if not self._plyer_available or not self._plyer_notification:
            return False
        try:
            def _send_async():
                try:
                    self._plyer_notification.notify(
                        title=title,
                        message=message,
                        app_name="PigSpy",
                        timeout=10
                    )
                except:
                    pass
            
            thread = threading.Thread(target=_send_async, daemon=True)
            thread.start()
            return True
        except Exception:
            return False
    
    def _send_windows_toast(self, title: str, message: str):
        """Send a Windows toast notification. Returns True if sent - non-blocking."""
        if sys.platform != "win32":
            return False
        
        # Preferred: winotify
        if self._winotify_available and self._winotify:
            try:
                def _show_toast_async():
                    try:
                        Notification, audio = self._winotify
                        toast = Notification(
                            app_id="PigSpy.Portable",
                            title=title,
                            msg=message,
                            duration="short"
                        )
                        toast.set_audio(audio.Default, loop=False)
                        toast.show()
                    except:
                        pass
                
                thread = threading.Thread(target=_show_toast_async, daemon=True)
                thread.start()
                return True
            except Exception:
                pass
        
        # Fallback: PowerShell toast (no extra deps)
        return self._send_windows_toast_powershell(title, message)
    
    def _send_windows_toast_powershell(self, title: str, message: str):
        """Fallback Windows toast using PowerShell. Returns True if sent - non-blocking."""
        try:
            def _escape_xml(value: str) -> str:
                return (
                    value.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;")
                    .replace("'", "&apos;")
                )
            
            safe_title = _escape_xml(title.replace("\r", " ").replace("\n", " "))
            safe_message = _escape_xml(message.replace("\r", " ").replace("\n", " "))
            
            ps_script = f"$AppId='PigSpy.Portable';[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]|Out-Null;[Windows.Data.Xml.Dom.XmlDocument,Windows.Data.Xml.Dom.XmlDocument,ContentType=WindowsRuntime]|Out-Null;$xml=New-Object Windows.Data.Xml.Dom.XmlDocument;$xml.LoadXml(\"<toast><visual><binding template='ToastGeneric'><text>{safe_title}</text><text>{safe_message}</text></binding></visual></toast>\");$toast=New-Object Windows.UI.Notifications.ToastNotification $xml;[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($AppId).Show($toast)"
            
            subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except Exception:
            return False
    
    def send_status_notification(self, message: str):
        """Send status notification"""
        try:
            title = "PigSpy Status"
            sent = self._send_windows_toast(title, message)
            if not sent:
                self._send_plyer_notification(title, message)
        except:
            print(f"PigSpy: {message}")

class AudioAlertSystem:
    """Advanced audio alert system with different sounds for different keywords"""

    def __init__(self):
        self.keyword_sounds = {
            'officer': (1200, 400), # Higher pitch for officer
            'emergency': (1400, 600),
            'car': (1000, 300),      # Medium pitch for car
            'license': (900, 200),   # Lower for license
        }
        self.notifier = Notifier()

    def play_keyword_sound(self, keyword: str):
        """Play specific sound for specific keyword"""
        freq, duration = self.keyword_sounds.get(keyword.lower(), (800, 500))

        try:
            self.notifier._play_tone(freq, duration)
            time.sleep(0.05)
            self.notifier._play_tone(freq + 200, duration // 2)  # Harmonic beep
        except:
            print(f"Sound alert for: {keyword}")

    def play_general_alert(self):
        """Play general alert sound"""
        try:
            # Rapid succession beeps
            for _ in range(3):
                self.notifier._play_tone(1000, 200)
                time.sleep(0.1)
        except:
            print("🚨 GENERAL ALERT!")

def create_test_notification():
    """Test function to verify notification system works"""
    notifier = Notifier()
    notifier.send_notification("test", "This is a test notification for keyword detection")
    
    # Test audio
    notifier.play_alert_sound()
    print("Test notification and sound played successfully!")

if __name__ == "__main__":
    create_test_notification()
