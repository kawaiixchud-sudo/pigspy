#!/usr/bin/env python
"""Test notification responsiveness and speed."""
import time
from notifier import Notifier

notifier = Notifier()

print("Testing notification speed...")
start_time = time.time()

# Send multiple notifications rapidly to test responsiveness
for i in range(3):
    print(f"Sending notification {i+1}/3...")
    notifier.send_notification(
        f"test_keyword_{i}",
        f"This is test notification {i+1} to check speed and responsiveness"
    )
    time.sleep(0.1)  # Small delay between notifications

end_time = time.time()
total_time = end_time - start_time

print(f"\nAll notifications sent in {total_time:.2f} seconds")
print(f"Average per notification: {total_time/3:.2f} seconds")
print("\nNotifications should appear in bottom right corner immediately")
