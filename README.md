# 🧪 File Version Saver - MVP

A simple Windows utility that adds "Save Version" and "View Versions" options to your right-click context menu, allowing you to easily track and restore file versions.

## 🚀 Quick Download (For End Users)

**Ready to use! No building required.**

1. **Download** `version_saver.exe` from the `dist` folder
2. **Copy** it to `C:\Program Files\FileVersionSaver\` (create the folder if it doesn't exist)
3. **Right-click** `install_context_menu.reg` and select "Merge" (Run as Administrator)
4. **Done!** Right-click any file to see "Save Version" and "View Versions" options

## ✨ Features

- **Save Version**: Right-click any file and save a timestamped version with a required comment
- **View Versions**: Browse all saved versions of a file with a clean GUI
- **Restore Versions**: Restore any previous version with automatic backup
- **Open Versions**: Open any saved version with its default application
- **Automatic Backup**: Creates `.backup` files when restoring to prevent data loss

## 🚀 Quick Start

### For End Users (Recommended)
1. **Download** `version_saver.exe` from the `dist` folder
2. **Copy** it to `C:\Program Files\FileVersionSaver\` (create the folder if it doesn't exist)
3. **Right-click** `install_context_menu.reg` and select "Merge" (Run as Administrator)
4. **Done!** Right-click any file to see "Save Version" and "View Versions" options

### For Developers (Building from Source)

#### Prerequisites
- Windows 10/11
- Python 3.7+ (for development)
- PyInstaller (for building executable)

#### Installation

1. **Build the executable:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Build executable
   pyinstaller version_saver.spec --clean
   ```

2. **Install the context menu:**
   - Copy `dist/version_saver.exe` to `C:\Program Files\FileVersionSaver\`
   - Right-click `install_context_menu.reg` and select "Merge" (Run as Administrator)

3. **Verify installation:**
   - Right-click any file in Windows Explorer
   - You should see "Save Version" and "View Versions" options

## 📁 File Structure

```
file_version_saver/
├── version_saver.py          # Main Python script
├── version_saver.spec        # PyInstaller specification
├── install_context_menu.reg  # Windows registry file
├── build.bat                 # Build script
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🎯 Usage

### Saving a Version
1. Right-click any file in Windows Explorer
2. Select "Save Version"
3. You will be prompted to enter a comment for this version. The file is then copied to `%USERPROFILE%\.versiontracker\<filename>\<timestamp>\` along with your comment.

### Viewing Versions
1. Right-click any file in Windows Explorer
2. Select "View Versions"
3. A window opens showing all saved versions with:
   - Timestamp
   - File size
   - Original modification date
   - Open and Restore buttons

### Restoring a Version
1. Open the "View Versions" window
2. Select the version you want to restore
3. Click "Restore Selected"
4. Confirm the action
5. The current file is backed up as `.backup` and the selected version is restored

## 🗂 Storage Structure

Versions are stored in your user profile:
```
%USERPROFILE%\.versiontracker\
├── document.docx\
│   ├── 2025-01-15T14-30-25\
│   │   ├── document.docx
│   │   └── metadata.json
│   └── 2025-01-14T09-15-10\
│       ├── document.docx
│       └── metadata.json
└── image.jpg\
    └── 2025-01-13T16-45-30\
        ├── image.jpg
        └── metadata.json
```

## 🔧 Development

### Running from Source
```bash
# Save a version (will prompt for a comment)
python version_saver.py save "path/to/file.txt" [comment]

# View versions
python version_saver.py view "path/to/file.txt"
```

### Building the Executable
```bash
# Option 1: Use the build script
build.bat

# Option 2: Manual build
pip install pyinstaller
pyinstaller version_saver.spec --clean
```

## 🛠 Technical Details

### Dependencies
- **Python Standard Library**: `os`, `sys`, `shutil`, `json`, `tkinter`, `pathlib`, `datetime`, `subprocess`, `platform`
- **PyInstaller**: For creating standalone executable

### Architecture
- **VersionSaver Class**: Core functionality for saving, retrieving, and restoring versions (now supports comments)
- **VersionViewer Class**: Tkinter GUI for browsing and managing versions (shows comments)
- **Command Line Interface**: Supports `save` and `view` commands, always prompts for a comment when saving
- **Windows Integration**: Registry-based context menu integration, prompts for a comment when saving

### Security Features
- Automatic backup creation before restoration
- File existence validation
- Error handling and user feedback
- Safe file operations with proper exception handling

## 🐛 Troubleshooting

### Context Menu Not Appearing
1. Ensure `version_saver.exe` is in `C:\Program Files\FileVersionSaver\`
2. Run `install_context_menu.reg` as Administrator
3. Restart Windows Explorer or reboot

### "File Not Found" Errors
- Check that the file path is correct
- Ensure the file exists and is accessible
- Verify file permissions

### Permission Errors
- Run the registry file as Administrator
- Check that the target directory is writable
- Ensure antivirus isn't blocking the application

## 🔮 Future Enhancements

- **File Comparison**: Diff tool to compare versions
- **Version Tags**: Add custom labels to versions
- **Cloud Storage**: Sync versions to cloud services
- **Version Limits**: Automatic cleanup of old versions
- **File Filters**: Exclude certain file types
- **Batch Operations**: Save/restore multiple files
- **Rename Support**: Allow users to rename tracked files and migrate their version history
- **Remove Support**: Allow users to remove a file and all its version history from tracking

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Note**: This is an MVP (Minimum Viable Product). The focus is on core functionality and ease of use. Future versions will include additional features based on user feedback. 