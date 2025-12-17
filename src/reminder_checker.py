"""
Reminder Checker - Background Service Script
---------------------------------------------
This script is called by Windows Task Scheduler to check for due reminders.
Created by: Xingchen (for Lanniny)
"""

import sys
import os
from pathlib import Path

# Add skill directory to path
SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

from reminder_manager import get_due_reminders, mark_triggered
from notification import notify_reminder

import logging
from datetime import datetime

# Setup logging
LOG_FILE = SKILL_DIR / "reminder_checker.log"


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def check_and_notify():
    """Check for due reminders and send notifications."""
    try:
        due_reminders = get_due_reminders()

        if not due_reminders:
            return 0

        count = 0
        for reminder in due_reminders:
            try:
                # Send notification
                notify_reminder(reminder)

                # Mark as triggered (updates next trigger time for repeating reminders)
                mark_triggered(reminder["id"])

                logging.info(f"Triggered reminder: {reminder['id']} - {reminder['title']}")
                count += 1

            except Exception as e:
                logging.error(f"Failed to trigger reminder {reminder['id']}: {e}")

        return count

    except Exception as e:
        logging.error(f"Check failed: {e}")
        return -1


def main():
    """Main entry point."""
    setup_logging()

    # Run check
    result = check_and_notify()

    if result > 0:
        logging.info(f"Triggered {result} reminder(s)")
    elif result == 0:
        # Don't log every check with no reminders (too verbose)
        pass
    else:
        logging.error("Check failed with error")

    return result


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result >= 0 else 1)
