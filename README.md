# Xingchen Reminder 星辰提醒

<p align="center">
  <img src="assets/icon.ico" width="128" height="128" alt="Xingchen Reminder">
</p>

<p align="center">
  <b>Your faithful time guardian | 你忠实的时间守护者</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows-blue" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.8+-green" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange" alt="License">
</p>

---

## Features | 功能特性

- **One-time & Repeating Reminders** | 一次性和重复提醒
  - Daily, Weekly, Weekdays modes
  - Custom repeat intervals
- **Flexible Notifications** | 灵活的通知方式
  - Windows Toast notifications (normal)
  - Popup + Sound alerts (important)
- **Custom Sounds** | 自定义提示音
  - Support MP3, WAV, OGG, FLAC
  - Adjustable playback duration
- **Beautiful GUI** | 美观的图形界面
  - Dark theme design
  - Easy-to-use interface
- **Background Service** | 后台服务
  - Silent background checker
  - Runs every minute

## Screenshots | 截图

<p align="center">
  <i>GUI Interface coming soon...</i>
</p>

## Installation | 安装

### Requirements | 系统要求

- Windows 10/11
- Python 3.8 or higher
- pip (Python package manager)

### Quick Install | 快速安装

**Method 1: Batch Script (Recommended)**
```cmd
# Double-click install.bat
# Or run in Command Prompt:
install.bat
```

**Method 2: PowerShell**
```powershell
# Run in PowerShell:
.\install.ps1
```

### Manual Install | 手动安装

```bash
# 1. Install dependencies
pip install winotify pygame pillow

# 2. Copy files to your preferred location
# 3. Create a scheduled task to run reminder_checker.py every minute
```

## Usage | 使用方法

### GUI Mode | 图形界面模式

1. Double-click the desktop shortcut "Xingchen Reminder"
2. Click "+ Add New" to create a reminder
3. Fill in the details and click "Add"

### Command Line | 命令行

```bash
# Add a one-time reminder
python reminder_manager.py add "Meeting" 14:00

# Add a daily reminder
python reminder_manager.py add "Drink water" 15:00 --repeat daily

# Add an important reminder
python reminder_manager.py add "Deadline!" 23:00 --important

# List all reminders
python reminder_manager.py list

# Delete a reminder
python reminder_manager.py delete <id>
```

## Uninstall | 卸载

**PowerShell:**
```powershell
.\install.ps1 -Uninstall
```

**Manual:**
1. Delete the scheduled task: `schtasks /delete /tn "XingchenReminder" /f`
2. Delete the desktop shortcut
3. Delete the installation folder: `%USERPROFILE%\.xingchen-reminder`

## File Structure | 文件结构

```
xingchen-reminder/
├── src/
│   ├── reminder_manager.py    # Core reminder management
│   ├── notification.py        # Windows notifications & sounds
│   ├── reminder_checker.py    # Background checker
│   └── reminder_gui.py        # GUI application
├── assets/
│   └── icon.ico              # Application icon
├── install.bat               # Batch installer
├── install.ps1               # PowerShell installer
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Configuration | 配置

Reminders are stored in JSON format at:
```
%USERPROFILE%\.xingchen-reminder\reminders.json
```

## License | 许可证

MIT License

## Author | 作者

Created by **Xingchen** (星辰) for **Lanniny**

---

<p align="center">
  <i>"Time is the dimension in which we evolve."</i>
</p>
