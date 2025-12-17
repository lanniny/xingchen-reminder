"""
Notification Module - Xingchen's Alert System
----------------------------------------------
Handles Windows notifications, popups, and custom sounds.
Created by: Xingchen (for Lanniny)
"""

import os
import sys
import ctypes
import winsound
import threading
import time
from pathlib import Path
from typing import Optional

# For toast notifications
TOAST_AVAILABLE = False
toast_notifier = None

try:
    from winotify import Notification, audio
    TOAST_AVAILABLE = True
    TOAST_LIB = "winotify"
except ImportError:
    try:
        from win10toast import ToastNotifier
        toast_notifier = ToastNotifier()
        TOAST_AVAILABLE = True
        TOAST_LIB = "win10toast"
    except ImportError:
        TOAST_LIB = None

# For music playback (mp3, etc.)
PYGAME_AVAILABLE = False
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    pass

# Paths
SKILL_DIR = Path(__file__).parent
SOUNDS_DIR = SKILL_DIR / "sounds"
SOUNDS_DIR.mkdir(exist_ok=True)


def show_toast(title: str, message: str, duration: int = 5) -> bool:
    """Show a Windows toast notification."""
    if not TOAST_AVAILABLE:
        print(f"\n[REMINDER] {title}: {message}")
        return False

    try:
        if TOAST_LIB == "winotify":
            toast = Notification(
                app_id="Xingchen Reminder",
                title=title,
                msg=message,
                duration="short"
            )
            toast.show()
            return True
        elif TOAST_LIB == "win10toast":
            def show():
                toast_notifier.show_toast(title, message, duration=duration, threaded=True)
            threading.Thread(target=show, daemon=True).start()
            return True
    except Exception as e:
        print(f"Toast notification failed: {e}")
        return False


def show_popup(title: str, message: str, icon: str = "info") -> int:
    """Show a Windows message box popup."""
    icons = {
        "info": 0x40,
        "warning": 0x30,
        "error": 0x10,
        "question": 0x20
    }
    flags = 0x00 | 0x1000 | icons.get(icon, 0x40)
    result = ctypes.windll.user32.MessageBoxW(0, message, title, flags)
    return result


def play_sound(sound_type: str = "default", duration: float = 0) -> bool:
    """
    Play a notification sound.

    Args:
        sound_type: "default", "important", "alarm", or path to audio file
        duration: Duration in seconds (0 = play full file, >0 = stop after duration)

    Returns:
        True if sound was played
    """
    try:
        if sound_type == "default":
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif sound_type == "important":
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif sound_type == "alarm":
            for _ in range(3):
                winsound.MessageBeep(winsound.MB_ICONHAND)
                time.sleep(0.3)
        elif os.path.exists(sound_type):
            play_music_file(sound_type, duration)
        else:
            winsound.MessageBeep()
        return True
    except Exception as e:
        print(f"Sound playback failed: {e}")
        return False


def play_music_file(file_path: str, duration: float = 0, block: bool = False) -> bool:
    """
    Play a music file (mp3, wav, ogg, etc.).

    Args:
        file_path: Path to the audio file
        duration: Duration in seconds (0 = play full file)
        block: Whether to block until playback finishes

    Returns:
        True if playback started successfully
    """
    file_path = str(file_path)

    # Check file extension
    ext = os.path.splitext(file_path)[1].lower()

    # For WAV files, can use winsound
    if ext == ".wav" and duration == 0:
        try:
            if block:
                winsound.PlaySound(file_path, winsound.SND_FILENAME)
            else:
                winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except:
            pass

    # For other formats or duration control, use pygame
    if PYGAME_AVAILABLE:
        try:
            def play_thread():
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play()

                if duration > 0:
                    time.sleep(duration)
                    pygame.mixer.music.stop()
                elif block:
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)

            if block:
                play_thread()
            else:
                threading.Thread(target=play_thread, daemon=True).start()
            return True
        except Exception as e:
            print(f"Pygame playback failed: {e}")

    # Fallback: try winsound for wav
    if ext == ".wav":
        try:
            winsound.PlaySound(file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        except:
            pass

    print(f"Cannot play {ext} files. Install pygame: pip install pygame")
    return False


def stop_music():
    """Stop currently playing music."""
    if PYGAME_AVAILABLE:
        try:
            pygame.mixer.music.stop()
        except:
            pass


def notify(
    title: str,
    message: str,
    priority: str = "normal",
    sound: bool = True,
    sound_file: str = "",
    sound_duration: float = 0
) -> None:
    """
    Send a notification with appropriate urgency level.

    Args:
        title: Notification title
        message: Notification message
        priority: "normal" or "important"
        sound: Whether to play sound
        sound_file: Custom sound file path (empty = use default)
        sound_duration: Sound duration in seconds (0 = full length)
    """
    if priority == "important":
        # Important: Play sound first, then popup (popup blocks)
        if sound:
            if sound_file and os.path.exists(sound_file):
                play_music_file(sound_file, sound_duration)
            else:
                play_sound("important")
        show_popup(f"[!] {title}", message, icon="warning")
    else:
        # Normal: Toast notification
        show_toast(title, message)
        if sound:
            if sound_file and os.path.exists(sound_file):
                play_music_file(sound_file, sound_duration)
            else:
                play_sound("default")


def notify_reminder(reminder: dict) -> None:
    """
    Notify user of a triggered reminder.

    Args:
        reminder: Reminder dict from reminder_manager
    """
    title = reminder.get("title", "Reminder")
    description = reminder.get("description", "")
    priority = reminder.get("priority", "normal")
    sound = reminder.get("sound", True)
    sound_file = reminder.get("sound_file", "")
    sound_duration = reminder.get("sound_duration", 0)

    # Build message
    message = title
    if description:
        message += f"\n\n{description}"

    # Add time info
    trigger_time = reminder.get("trigger_time", "")
    if trigger_time:
        time_part = trigger_time.split(" ")[-1] if " " in trigger_time else trigger_time
        message = f"[{time_part}] {message}"

    notify(f"Xingchen Reminder", message, priority, sound, sound_file, sound_duration)


# CLI test
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test notification system")
    parser.add_argument("--toast", action="store_true", help="Test toast notification")
    parser.add_argument("--popup", action="store_true", help="Test popup")
    parser.add_argument("--sound", action="store_true", help="Test sound")
    parser.add_argument("--music", type=str, help="Test music file playback")
    parser.add_argument("--duration", type=float, default=0, help="Music duration (seconds)")
    parser.add_argument("--all", action="store_true", help="Test all")
    parser.add_argument("--important", action="store_true", help="Test important notification")

    args = parser.parse_args()

    if args.all or args.toast:
        print("Testing toast notification...")
        show_toast("Test Reminder", "This is a test toast notification from Xingchen!")

    if args.all or args.sound:
        print("Testing sound...")
        play_sound("default")
        time.sleep(1)
        print("Testing important sound...")
        play_sound("important")

    if args.music:
        print(f"Testing music file: {args.music} (duration: {args.duration}s)")
        play_music_file(args.music, args.duration, block=True)

    if args.all or args.popup:
        print("Testing popup...")
        show_popup("Test Popup", "This is a test popup from Xingchen!", icon="info")

    if args.important:
        print("Testing important notification...")
        notify("IMPORTANT TEST", "This is an important reminder test!", priority="important")

    if not any([args.toast, args.popup, args.sound, args.all, args.important, args.music]):
        print("Notification module loaded successfully!")
        print(f"Toast available: {TOAST_AVAILABLE} (using: {TOAST_LIB})")
        print(f"Pygame available: {PYGAME_AVAILABLE}")
        print("\nUsage:")
        print("  python notification.py --toast")
        print("  python notification.py --popup")
        print("  python notification.py --sound")
        print("  python notification.py --music path/to/file.mp3 --duration 5")
        print("  python notification.py --all")
        print("  python notification.py --important")
