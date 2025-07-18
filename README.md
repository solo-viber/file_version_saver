# �� File Version Saver

A simple Windows utility that adds "Save Version" and "View Versions" options to your right-click context menu, allowing you to easily track and restore file versions.

---

## 🚀 Quick Start for End Users

1. **Download** the latest `setup.exe` or `version_saver.exe` from the [Releases page](https://github.com/yourusername/yourrepo/releases).
2. **Run** `setup.exe` (recommended) and follow the prompts, or manually copy `version_saver.exe` to `C:\Program Files\FileVersionSaver\`.
3. **Right-click** `install_context_menu.reg` (included in the install directory) and select "Merge" (Run as Administrator).
4. **Done!** Right-click any file to see "Save Version", "Save Version (Choose Location)", and "View Versions" options.

---

## 🏗️ Overall Build Guide (For Developers)

### 1. Prerequisites
- Windows 10/11
- Python 3.7+
- [PyInstaller](https://pyinstaller.org/)
- [Inno Setup Compiler](https://jrsoftware.org/isinfo.php) (for installer)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Build the Executable
You can use the provided batch script or run PyInstaller manually:
```bash
# Option 1: Use the build script
.\build.bat

# Option 2: Manual build
pyinstaller version_saver.spec --clean
```
The executable will be created in the `dist/` folder as `version_saver.exe`.

### 4. Create the Windows Installer (setup.exe)
1. Ensure `version_saver.exe`, `install_context_menu.reg`, and any other required files are present.
2. Open `create_installer.iss` in the Inno Setup Compiler.
3. Click **Compile**. The installer `setup.exe` will be generated (usually in the `Output` folder).

### 5. Publish a Release
1. Go to your repository's **Releases** page on GitHub.
2. Click **Draft a new release**.
3. Fill in the version, title, and description.
4. **Attach** the generated `setup.exe` (and optionally `version_saver.exe`).
5. Publish the release.

---

## ✨ Features
- **Save Version**: Right-click any file and save a timestamped version with a required comment
- **View Versions**: Browse all saved versions of a file with a clean GUI
- **Restore Versions**: Restore any previous version with automatic backup
- **Open Versions**: Open any saved version with its default application
- **Automatic Backup**: Creates `.backup` files when restoring to prevent data loss

---

## 📁 File Structure
```
file_version_saver/
├── version_saver.py          # Main Python script
├── version_saver.spec        # PyInstaller specification
├── install_context_menu.reg  # Windows registry file
├── build.bat                 # Build script
├── requirements.txt          # Python dependencies
├── create_installer.iss      # Inno Setup script
└── README.md                 # This file
```

---

## 🎯 Usage

### Saving a Version
1. Right-click any file in Windows Explorer
2. Select **"Save Version"** to save to the default location, or **"Save Version (Choose Location)"** to pick a folder.
3. Enter a comment when prompted. The file is copied to:
   - Default: `%USERPROFILE%\.versiontracker\<filename>\<timestamp>\`
   - Chosen: `<your selected folder>\<filename>\<timestamp>\`
   with your comment.

### Command Line Usage
You can also use the command line:
```bash
python version_saver.py save <file_path> [comment]
python version_saver.py save <file_path> --choose-location [comment]
```
- The `--choose-location` flag will prompt you to select a folder for saving the version.

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

---

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

---

## 🛠 Technical Details
- **Python Standard Library**: `os`, `sys`, `shutil`, `json`, `tkinter`, `pathlib`, `datetime`, `subprocess`, `platform`
- **PyInstaller**: For creating standalone executable
- **Inno Setup**: For creating the Windows installer

### Architecture
- **VersionSaver Class**: Core functionality for saving, retrieving, and restoring versions (supports comments)
- **VersionViewer Class**: Tkinter GUI for browsing and managing versions (shows comments)
- **Command Line Interface**: Supports `save` and `view` commands, always prompts for a comment when saving
- **Windows Integration**: Registry-based context menu integration, prompts for a comment when saving

### Security Features
- Automatic backup creation before restoration
- File existence validation
- Error handling and user feedback
- Safe file operations with proper exception handling

---

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

---

## 🔮 Future Enhancements
- **File Comparison**: Diff tool to compare versions
- **Version Tags**: Add custom labels to versions
- **Cloud Storage**: Sync versions to cloud services
- **Version Limits**: Automatic cleanup of old versions
- **File Filters**: Exclude certain file types
- **Batch Operations**: Save/restore multiple files
- **Rename Support**: Allow users to rename tracked files and migrate their version history
- **Remove Support**: Allow users to remove a file and all its version history from tracking

---

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