"""
Xingchen Reminder GUI
---------------------
A beautiful GUI for managing reminders.
Created by: Xingchen (for Lanniny)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add skill directory to path
SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

from reminder_manager import (
    add_reminder, list_reminders, delete_reminder, toggle_reminder,
    REPEAT_NONE, REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_WEEKDAYS
)
from notification import play_music_file, stop_music, PYGAME_AVAILABLE


class ReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Xingchen Reminder")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # Set theme colors
        self.bg_color = "#1a1a2e"
        self.fg_color = "#eaeaea"
        self.accent_color = "#e94560"
        self.secondary_color = "#16213e"
        self.success_color = "#4ecca3"

        self.root.configure(bg=self.bg_color)

        # Configure styles
        self.setup_styles()

        # Create main layout
        self.create_header()
        self.create_reminder_list()
        self.create_buttons()

        # Load reminders
        self.refresh_list()

    def setup_styles(self):
        """Setup ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')

        # Treeview style
        style.configure("Treeview",
            background=self.secondary_color,
            foreground=self.fg_color,
            fieldbackground=self.secondary_color,
            rowheight=30
        )
        style.configure("Treeview.Heading",
            background=self.accent_color,
            foreground="white",
            font=('Segoe UI', 10, 'bold')
        )
        style.map("Treeview",
            background=[('selected', self.accent_color)],
            foreground=[('selected', 'white')]
        )

    def create_header(self):
        """Create header section."""
        header = tk.Frame(self.root, bg=self.bg_color)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))

        # Title
        title = tk.Label(header,
            text="Xingchen Reminder",
            font=('Segoe UI', 24, 'bold'),
            fg=self.accent_color,
            bg=self.bg_color
        )
        title.pack(side=tk.LEFT)

        # Subtitle
        subtitle = tk.Label(header,
            text="Your faithful time guardian",
            font=('Segoe UI', 10),
            fg="#888",
            bg=self.bg_color
        )
        subtitle.pack(side=tk.LEFT, padx=(10, 0), pady=(12, 0))

    def create_reminder_list(self):
        """Create reminder list section."""
        list_frame = tk.Frame(self.root, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Columns
        columns = ("status", "time", "title", "repeat", "sound")

        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)

        # Column headings
        self.tree.heading("status", text="Status")
        self.tree.heading("time", text="Time")
        self.tree.heading("title", text="Title")
        self.tree.heading("repeat", text="Repeat")
        self.tree.heading("sound", text="Sound")

        # Column widths
        self.tree.column("status", width=60, anchor="center")
        self.tree.column("time", width=140, anchor="center")
        self.tree.column("title", width=250)
        self.tree.column("repeat", width=100, anchor="center")
        self.tree.column("sound", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Double-click to edit
        self.tree.bind("<Double-1>", self.on_double_click)

    def create_buttons(self):
        """Create button section."""
        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, padx=20, pady=(10, 20))

        # Button style
        btn_style = {
            'font': ('Segoe UI', 10),
            'width': 12,
            'cursor': 'hand2',
            'relief': tk.FLAT,
            'bd': 0
        }

        # Add button
        add_btn = tk.Button(btn_frame,
            text="+ Add New",
            bg=self.success_color,
            fg="white",
            activebackground="#3db892",
            command=self.show_add_dialog,
            **btn_style
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Delete button
        delete_btn = tk.Button(btn_frame,
            text="Delete",
            bg=self.accent_color,
            fg="white",
            activebackground="#d63850",
            command=self.delete_selected,
            **btn_style
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Toggle button
        toggle_btn = tk.Button(btn_frame,
            text="Enable/Disable",
            bg=self.secondary_color,
            fg=self.fg_color,
            activebackground="#1f2b47",
            command=self.toggle_selected,
            **btn_style
        )
        toggle_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Refresh button
        refresh_btn = tk.Button(btn_frame,
            text="Refresh",
            bg=self.secondary_color,
            fg=self.fg_color,
            activebackground="#1f2b47",
            command=self.refresh_list,
            **btn_style
        )
        refresh_btn.pack(side=tk.RIGHT)

    def refresh_list(self):
        """Refresh the reminder list."""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load reminders
        reminders = list_reminders(include_disabled=True)

        repeat_names = {
            "none": "-",
            "daily": "Daily",
            "weekly": "Weekly",
            "weekdays": "Weekdays"
        }

        for r in reminders:
            status = "ON" if r.get("enabled", True) else "OFF"
            time_str = r.get("trigger_time", "")
            title = r.get("title", "")
            repeat = repeat_names.get(r.get("repeat", "none"), r.get("repeat", ""))

            # Sound info
            sound_file = r.get("sound_file", "")
            if sound_file:
                sound_name = Path(sound_file).name[:15] + "..." if len(Path(sound_file).name) > 15 else Path(sound_file).name
            else:
                sound_name = "System"

            # Insert with id as tag
            self.tree.insert("", tk.END,
                values=(status, time_str, title, repeat, sound_name),
                tags=(r["id"],)
            )

    def get_selected_id(self):
        """Get the ID of the selected reminder."""
        selection = self.tree.selection()
        if not selection:
            return None
        item = selection[0]
        tags = self.tree.item(item, "tags")
        return tags[0] if tags else None

    def delete_selected(self):
        """Delete the selected reminder."""
        reminder_id = self.get_selected_id()
        if not reminder_id:
            messagebox.showwarning("Warning", "Please select a reminder to delete.")
            return

        if messagebox.askyesno("Confirm", "Delete this reminder?"):
            delete_reminder(reminder_id)
            self.refresh_list()

    def toggle_selected(self):
        """Toggle the selected reminder."""
        reminder_id = self.get_selected_id()
        if not reminder_id:
            messagebox.showwarning("Warning", "Please select a reminder to toggle.")
            return

        toggle_reminder(reminder_id)
        self.refresh_list()

    def on_double_click(self, event):
        """Handle double-click on reminder."""
        # For now, just toggle
        self.toggle_selected()

    def show_add_dialog(self):
        """Show dialog to add new reminder."""
        dialog = AddReminderDialog(self.root, self)
        self.root.wait_window(dialog.window)
        self.refresh_list()


class AddReminderDialog:
    def __init__(self, parent, app):
        self.app = app
        self.sound_file = ""

        self.window = tk.Toplevel(parent)
        self.window.title("Add Reminder")
        self.window.geometry("450x500")
        self.window.configure(bg=app.bg_color)
        self.window.transient(parent)
        self.window.grab_set()

        # Center the dialog
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.window.geometry(f"+{x}+{y}")

        self.create_form()

    def create_form(self):
        """Create the form elements."""
        bg = self.app.bg_color
        fg = self.app.fg_color
        secondary = self.app.secondary_color
        accent = self.app.accent_color

        # Title
        header = tk.Label(self.window,
            text="New Reminder",
            font=('Segoe UI', 18, 'bold'),
            fg=accent,
            bg=bg
        )
        header.pack(pady=(20, 20))

        form = tk.Frame(self.window, bg=bg)
        form.pack(fill=tk.BOTH, expand=True, padx=30)

        label_style = {'font': ('Segoe UI', 10), 'fg': fg, 'bg': bg, 'anchor': 'w'}
        entry_style = {'font': ('Segoe UI', 11), 'bg': secondary, 'fg': fg,
                      'insertbackground': fg, 'relief': tk.FLAT, 'bd': 5}

        # Title field
        tk.Label(form, text="Title", **label_style).pack(fill=tk.X, pady=(0, 5))
        self.title_entry = tk.Entry(form, **entry_style)
        self.title_entry.pack(fill=tk.X, pady=(0, 15))

        # Time frame
        time_frame = tk.Frame(form, bg=bg)
        time_frame.pack(fill=tk.X, pady=(0, 15))

        # Date
        date_frame = tk.Frame(time_frame, bg=bg)
        date_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        tk.Label(date_frame, text="Date (YYYY-MM-DD)", **label_style).pack(fill=tk.X, pady=(0, 5))
        self.date_entry = tk.Entry(date_frame, **entry_style)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(fill=tk.X)

        # Time
        time_inner = tk.Frame(time_frame, bg=bg)
        time_inner.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Label(time_inner, text="Time (HH:MM)", **label_style).pack(fill=tk.X, pady=(0, 5))
        self.time_entry = tk.Entry(time_inner, **entry_style)
        self.time_entry.insert(0, (datetime.now() + timedelta(minutes=5)).strftime("%H:%M"))
        self.time_entry.pack(fill=tk.X)

        # Priority
        priority_frame = tk.Frame(form, bg=bg)
        priority_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(priority_frame, text="Priority", **label_style).pack(fill=tk.X, pady=(0, 5))
        self.priority_var = tk.StringVar(value="normal")
        priorities = [("Normal (Toast)", "normal"), ("Important (Popup)", "important")]
        for text, value in priorities:
            tk.Radiobutton(priority_frame, text=text, variable=self.priority_var,
                value=value, bg=bg, fg=fg, selectcolor=secondary,
                activebackground=bg, activeforeground=fg
            ).pack(side=tk.LEFT, padx=(0, 20))

        # Repeat
        repeat_frame = tk.Frame(form, bg=bg)
        repeat_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(repeat_frame, text="Repeat", **label_style).pack(fill=tk.X, pady=(0, 5))
        self.repeat_var = tk.StringVar(value="none")
        repeats = [("Once", "none"), ("Daily", "daily"), ("Weekly", "weekly"), ("Weekdays", "weekdays")]
        for text, value in repeats:
            tk.Radiobutton(repeat_frame, text=text, variable=self.repeat_var,
                value=value, bg=bg, fg=fg, selectcolor=secondary,
                activebackground=bg, activeforeground=fg
            ).pack(side=tk.LEFT, padx=(0, 15))

        # Sound file
        sound_frame = tk.Frame(form, bg=bg)
        sound_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(sound_frame, text="Custom Sound (optional)", **label_style).pack(fill=tk.X, pady=(0, 5))

        sound_inner = tk.Frame(sound_frame, bg=bg)
        sound_inner.pack(fill=tk.X)

        self.sound_label = tk.Label(sound_inner, text="System default",
            font=('Segoe UI', 10), fg="#888", bg=secondary, anchor='w', padx=10, pady=8)
        self.sound_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(sound_inner, text="Browse", bg=secondary, fg=fg,
            relief=tk.FLAT, command=self.browse_sound, cursor='hand2'
        ).pack(side=tk.LEFT, padx=(5, 0))

        tk.Button(sound_inner, text="Preview", bg=secondary, fg=fg,
            relief=tk.FLAT, command=self.preview_sound, cursor='hand2'
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Sound duration
        duration_frame = tk.Frame(form, bg=bg)
        duration_frame.pack(fill=tk.X, pady=(0, 15))
        tk.Label(duration_frame, text="Sound Duration (seconds, 0 = full)", **label_style).pack(fill=tk.X, pady=(0, 5))
        self.duration_entry = tk.Entry(duration_frame, width=10, **entry_style)
        self.duration_entry.insert(0, "0")
        self.duration_entry.pack(anchor='w')

        # Buttons
        btn_frame = tk.Frame(self.window, bg=bg)
        btn_frame.pack(fill=tk.X, padx=30, pady=20)

        tk.Button(btn_frame, text="Cancel", bg=secondary, fg=fg,
            font=('Segoe UI', 10), width=10, relief=tk.FLAT,
            command=self.window.destroy, cursor='hand2'
        ).pack(side=tk.RIGHT, padx=(10, 0))

        tk.Button(btn_frame, text="Add", bg=self.app.success_color, fg="white",
            font=('Segoe UI', 10, 'bold'), width=10, relief=tk.FLAT,
            command=self.add_reminder, cursor='hand2'
        ).pack(side=tk.RIGHT)

    def browse_sound(self):
        """Browse for sound file."""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.ogg *.flac"),
            ("MP3 files", "*.mp3"),
            ("WAV files", "*.wav"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Sound File",
            filetypes=filetypes
        )
        if filename:
            self.sound_file = filename
            name = Path(filename).name
            if len(name) > 30:
                name = name[:27] + "..."
            self.sound_label.config(text=name, fg=self.app.fg_color)

    def preview_sound(self):
        """Preview the selected sound."""
        if self.sound_file:
            try:
                duration = float(self.duration_entry.get() or 0)
            except ValueError:
                duration = 0
            play_music_file(self.sound_file, duration if duration > 0 else 3)
        else:
            messagebox.showinfo("Info", "No custom sound selected. Will use system default.")

    def add_reminder(self):
        """Add the reminder."""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Please enter a title.")
            return

        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()

        # Validate time format
        try:
            datetime.strptime(time_str, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM (24-hour).")
            return

        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        try:
            duration = float(self.duration_entry.get() or 0)
        except ValueError:
            duration = 0

        # Add reminder
        add_reminder(
            title=title,
            time_str=time_str,
            date_str=date_str,
            priority=self.priority_var.get(),
            repeat=self.repeat_var.get(),
            sound_file=self.sound_file,
            sound_duration=duration
        )

        self.window.destroy()


def main():
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
