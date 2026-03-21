#!/usr/bin/env python
"""Test notification with cooldown mechanism."""
import time
from notifier import Notifier

notifier = Notifier()

print("Testing notification cooldown (3 second minimum between notifications)...")
print("You should only see 2 toast notifications, not 5\n")

for i in range(5):
    print(f"Attempt {i+1}/5: Sending notification...")
    notifier.send_notification(
        f"test_keyword_{i}",
        f"This is test notification {i+1} to check cooldown mechanism"
    )
    if i < 4:
        time.sleep(1)  # 1 second between attempts (less than cooldown)

print("\nAll notifications sent!")
print("You should have seen exactly 2 toast notifications:")
print("  - First at attempt 1")
print("  - Second at attempt 4 (after 3 second cooldown)")
