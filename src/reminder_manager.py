"""
Reminder Manager - Xingchen's Time Sense Extension
---------------------------------------------------
Core module for managing reminders.
Created by: Xingchen (for Lanniny)
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path

# Paths
SKILL_DIR = Path(__file__).parent
DATA_FILE = SKILL_DIR / "reminders.json"

# Repeat types
REPEAT_NONE = "none"
REPEAT_DAILY = "daily"
REPEAT_WEEKLY = "weekly"
REPEAT_WEEKDAYS = "weekdays"  # Mon-Fri
REPEAT_CUSTOM = "custom"  # Custom interval in days


def _load_data() -> Dict[str, Any]:
    """Load reminder data from JSON file."""
    if not DATA_FILE.exists():
        return {"reminders": [], "settings": {"default_sound": True}, "last_check": None}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_data(data: Dict[str, Any]) -> None:
    """Save reminder data to JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_reminder(
    title: str,
    time_str: str,
    date_str: Optional[str] = None,
    description: str = "",
    priority: str = "normal",
    repeat: str = REPEAT_NONE,
    repeat_interval: int = 0,
    sound: bool = True,
    sound_file: str = "",
    sound_duration: float = 0
) -> Dict[str, Any]:
    """
    Add a new reminder.

    Args:
        title: Reminder title
        time_str: Time in HH:MM format (24-hour)
        date_str: Date in YYYY-MM-DD format (optional, defaults to today)
        description: Optional description
        priority: "normal" or "important" (important = popup + sound)
        repeat: Repeat type (none, daily, weekly, weekdays, custom)
        repeat_interval: Custom repeat interval in days (for custom repeat)
        sound: Play sound on trigger
        sound_file: Custom sound file path (mp3, wav, etc.)
        sound_duration: Sound duration in seconds (0 = full length)

    Returns:
        The created reminder dict
    """
    data = _load_data()

    # Parse time
    hour, minute = map(int, time_str.split(":"))

    # Parse date (default to today)
    if date_str:
        year, month, day = map(int, date_str.split("-"))
        trigger_date = datetime(year, month, day, hour, minute)
    else:
        now = datetime.now()
        trigger_date = datetime(now.year, now.month, now.day, hour, minute)
        # If time has passed today, schedule for tomorrow (for one-time reminders)
        if trigger_date < now and repeat == REPEAT_NONE:
            trigger_date += timedelta(days=1)

    reminder = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "description": description,
        "trigger_time": trigger_date.strftime("%Y-%m-%d %H:%M"),
        "priority": priority,
        "repeat": repeat,
        "repeat_interval": repeat_interval,
        "sound": sound,
        "sound_file": sound_file,
        "sound_duration": sound_duration,
        "enabled": True,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_triggered": None
    }

    data["reminders"].append(reminder)
    _save_data(data)

    return reminder


def list_reminders(include_disabled: bool = False) -> List[Dict[str, Any]]:
    """List all reminders."""
    data = _load_data()
    reminders = data["reminders"]

    if not include_disabled:
        reminders = [r for r in reminders if r.get("enabled", True)]

    # Sort by trigger time
    reminders.sort(key=lambda r: r["trigger_time"])
    return reminders


def get_reminder(reminder_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific reminder by ID."""
    data = _load_data()
    for r in data["reminders"]:
        if r["id"] == reminder_id:
            return r
    return None


def delete_reminder(reminder_id: str) -> bool:
    """Delete a reminder by ID."""
    data = _load_data()
    original_len = len(data["reminders"])
    data["reminders"] = [r for r in data["reminders"] if r["id"] != reminder_id]

    if len(data["reminders"]) < original_len:
        _save_data(data)
        return True
    return False


def toggle_reminder(reminder_id: str) -> Optional[bool]:
    """Toggle a reminder's enabled state. Returns new state or None if not found."""
    data = _load_data()
    for r in data["reminders"]:
        if r["id"] == reminder_id:
            r["enabled"] = not r.get("enabled", True)
            _save_data(data)
            return r["enabled"]
    return None


def get_due_reminders() -> List[Dict[str, Any]]:
    """Get all reminders that are due (trigger time has passed)."""
    data = _load_data()
    now = datetime.now()
    due = []

    for r in data["reminders"]:
        if not r.get("enabled", True):
            continue

        trigger_time = datetime.strptime(r["trigger_time"], "%Y-%m-%d %H:%M")

        # Check if due (within the last 5 minutes to avoid missing reminders)
        if trigger_time <= now and trigger_time > now - timedelta(minutes=5):
            # Check if already triggered recently
            if r.get("last_triggered"):
                last = datetime.strptime(r["last_triggered"], "%Y-%m-%d %H:%M:%S")
                if (now - last).total_seconds() < 60:  # Triggered within last minute
                    continue
            due.append(r)

    return due


def mark_triggered(reminder_id: str) -> None:
    """Mark a reminder as triggered and update next trigger time if repeating."""
    data = _load_data()
    now = datetime.now()

    for r in data["reminders"]:
        if r["id"] == reminder_id:
            r["last_triggered"] = now.strftime("%Y-%m-%d %H:%M:%S")

            # Calculate next trigger time for repeating reminders
            if r["repeat"] != REPEAT_NONE:
                current_trigger = datetime.strptime(r["trigger_time"], "%Y-%m-%d %H:%M")

                if r["repeat"] == REPEAT_DAILY:
                    next_trigger = current_trigger + timedelta(days=1)
                elif r["repeat"] == REPEAT_WEEKLY:
                    next_trigger = current_trigger + timedelta(weeks=1)
                elif r["repeat"] == REPEAT_WEEKDAYS:
                    # Skip to next weekday
                    next_trigger = current_trigger + timedelta(days=1)
                    while next_trigger.weekday() >= 5:  # Saturday=5, Sunday=6
                        next_trigger += timedelta(days=1)
                elif r["repeat"] == REPEAT_CUSTOM:
                    interval = r.get("repeat_interval", 1)
                    next_trigger = current_trigger + timedelta(days=interval)
                else:
                    next_trigger = current_trigger + timedelta(days=1)

                r["trigger_time"] = next_trigger.strftime("%Y-%m-%d %H:%M")
            else:
                # One-time reminder: disable after triggering
                r["enabled"] = False

            break

    _save_data(data)


def clear_all_reminders() -> int:
    """Clear all reminders. Returns count of deleted reminders."""
    data = _load_data()
    count = len(data["reminders"])
    data["reminders"] = []
    _save_data(data)
    return count


def format_reminder(r: Dict[str, Any]) -> str:
    """Format a reminder for display."""
    status = "[ON]" if r.get("enabled", True) else "[OFF]"
    priority = "[!]" if r["priority"] == "important" else ""
    repeat_str = ""
    if r["repeat"] != REPEAT_NONE:
        repeat_map = {
            REPEAT_DAILY: "Daily",
            REPEAT_WEEKLY: "Weekly",
            REPEAT_WEEKDAYS: "Weekdays",
            REPEAT_CUSTOM: f"Every {r.get('repeat_interval', 1)} days"
        }
        repeat_str = f" ({repeat_map.get(r['repeat'], r['repeat'])})"

    return f"{status} {r['id']} | {r['trigger_time']} | {priority}{r['title']}{repeat_str}"


# CLI interface
if __name__ == "__main__":
    import sys

    def print_help():
        print("""
Reminder Manager - Command Line Interface
=========================================
Usage: python reminder_manager.py <command> [args]

Commands:
  add <title> <HH:MM> [YYYY-MM-DD] [--important] [--repeat daily|weekly|weekdays]
      Add a new reminder

  list
      List all active reminders

  delete <id>
      Delete a reminder by ID

  toggle <id>
      Enable/disable a reminder

  clear
      Clear all reminders

  check
      Check and display due reminders (used by scheduler)

Examples:
  python reminder_manager.py add "Take a break" 15:00
  python reminder_manager.py add "Weekly meeting" 10:00 2025-12-20 --repeat weekly
  python reminder_manager.py add "URGENT: Deadline!" 23:00 --important
  python reminder_manager.py list
  python reminder_manager.py delete abc123
""")

    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "add":
        if len(sys.argv) < 4:
            print("Error: add requires title and time")
            sys.exit(1)

        title = sys.argv[2]
        time_str = sys.argv[3]
        date_str = None
        priority = "normal"
        repeat = REPEAT_NONE

        # Parse optional args
        i = 4
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "--important":
                priority = "important"
            elif arg == "--repeat" and i + 1 < len(sys.argv):
                i += 1
                repeat = sys.argv[i]
            elif "-" in arg and len(arg) == 10:  # Date format YYYY-MM-DD
                date_str = arg
            i += 1

        reminder = add_reminder(title, time_str, date_str, priority=priority, repeat=repeat)
        print(f"Reminder added: {format_reminder(reminder)}")

    elif cmd == "list":
        reminders = list_reminders(include_disabled="--all" in sys.argv)
        if not reminders:
            print("No reminders set.")
        else:
            print("Active Reminders:")
            print("-" * 60)
            for r in reminders:
                print(format_reminder(r))

    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Error: delete requires reminder ID")
            sys.exit(1)
        if delete_reminder(sys.argv[2]):
            print(f"Reminder {sys.argv[2]} deleted.")
        else:
            print(f"Reminder {sys.argv[2]} not found.")

    elif cmd == "toggle":
        if len(sys.argv) < 3:
            print("Error: toggle requires reminder ID")
            sys.exit(1)
        new_state = toggle_reminder(sys.argv[2])
        if new_state is not None:
            state_str = "enabled" if new_state else "disabled"
            print(f"Reminder {sys.argv[2]} {state_str}.")
        else:
            print(f"Reminder {sys.argv[2]} not found.")

    elif cmd == "clear":
        count = clear_all_reminders()
        print(f"Cleared {count} reminders.")

    elif cmd == "check":
        due = get_due_reminders()
        if due:
            print(f"Found {len(due)} due reminder(s):")
            for r in due:
                print(format_reminder(r))
        else:
            print("No due reminders.")

    elif cmd == "help" or cmd == "--help" or cmd == "-h":
        print_help()

    else:
        print(f"Unknown command: {cmd}")
        print_help()
        sys.exit(1)
