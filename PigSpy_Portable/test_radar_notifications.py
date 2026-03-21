import time
from notifier import Notifier
from keyword_detector import KeywordDetector
from config import Config

def test_radar_system():
    print("Starting Common Radar Notification System Test...")
    
    # Initialize components
    config = Config()
    detector = KeywordDetector(config.KEYWORDS)
    notifier = Notifier()
    
    # Very common radar/scanner testing words
    test_transcriptions = [
        "Unit 10, copy that, I'm on the highway.",
        "Radar check, I've got a vehicle at high speed.",
        "Stop the car, checking the plate now.",
        "Clear for radio traffic, mile marker 50."
    ]
    
    for text in test_transcriptions:
        print(f"\nProcessing: {text}")
        matches = detector.add_transcription(text)
        
        if matches:
            for keyword, context in matches:
                print(f"[ALERT] KEYWORD DETECTED: '{keyword.upper()}'")
                notifier.send_notification(keyword, context)
                time.sleep(0.5)
        else:
            print("No keywords detected.")

if __name__ == "__main__":
    test_radar_system()
    print("\nTest complete. Check your bottom right corner for notifications.")