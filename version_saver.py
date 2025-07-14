#!/usr/bin/env python3
"""
File Version Saver - MVP
Right-click context menu integration for saving and restoring file versions
"""

import sys
import os
import shutil
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from pathlib import Path
import subprocess
import platform
import ctypes
from ctypes import wintypes

# DEBUG: Log arguments for troubleshooting context menu issues
try:
    with open("C:\\version_saver_args.log", "a", encoding="utf-8") as f:
        f.write("ARGS: " + repr(sys.argv) + "\\n")
except Exception:
    pass

class VersionSaver:
    def __init__(self):
        self.version_tracker_dir = Path.home() / ".versiontracker"
        self.version_tracker_dir.mkdir(exist_ok=True)
        # Ensure the .versiontracker folder is hidden on Windows
        if platform.system() == "Windows":
            try:
                subprocess.call(['attrib', '-h', str(self.version_tracker_dir)])
            except Exception:
                pass
        self.index_file = self.version_tracker_dir / "index.json"
        self.index = self._load_index()
        self._migrate_existing_versions()

    def get_file_id(self, path):
        if platform.system() != "Windows":
            raise OSError("NTFS File ID is only supported on Windows/NTFS.")
        FILE_READ_EA = 0x0008
        OPEN_EXISTING = 3
        class BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("dwFileAttributes", wintypes.DWORD),
                ("ftCreationTime", wintypes.FILETIME),
                ("ftLastAccessTime", wintypes.FILETIME),
                ("ftLastWriteTime", wintypes.FILETIME),
                ("dwVolumeSerialNumber", wintypes.DWORD),
                ("nFileSizeHigh", wintypes.DWORD),
                ("nFileSizeLow", wintypes.DWORD),
                ("nNumberOfLinks", wintypes.DWORD),
                ("nFileIndexHigh", wintypes.DWORD),
                ("nFileIndexLow", wintypes.DWORD),
            ]
        CreateFile = ctypes.windll.kernel32.CreateFileW
        GetFileInformationByHandle = ctypes.windll.kernel32.GetFileInformationByHandle
        CloseHandle = ctypes.windll.kernel32.CloseHandle
        handle = CreateFile(
            str(path),
            FILE_READ_EA,
            0,
            None,
            OPEN_EXISTING,
            0,
            None
        )
        if handle == -1 or handle == 0:
            raise OSError("Could not open file: " + str(path))
        info = BY_HANDLE_FILE_INFORMATION()
        res = GetFileInformationByHandle(handle, ctypes.byref(info))
        CloseHandle(handle)
        if not res:
            raise OSError("Could not get file information: " + str(path))
        file_id = (info.nFileIndexHigh << 32) + info.nFileIndexLow
        return str(file_id)

    def _load_index(self):
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                # Corrupt or unreadable index, start fresh
                return []
        else:
            return []

    def _save_index(self):
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving index: {e}")
        
    def save_version(self, file_path, comment=None, base_dir=None):
        """Save a version of the specified file, with optional comment and optional base_dir"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            # Abort if base_dir is an empty string (user cancelled folder picker)
            if base_dir == "":
                return False, "No directory chosen. Operation aborted."
            
            # Use custom base_dir if provided, else default
            if base_dir:
                base_dir = Path(base_dir)
                file_versions_dir = base_dir / ".versiontracker" / self.get_file_id(file_path)
                file_versions_dir.mkdir(exist_ok=True, parents=True)
                # Ensure the .versiontracker folder is hidden on Windows
                if platform.system() == "Windows":
                    try:
                        subprocess.call(['attrib', '-h', str(base_dir / ".versiontracker")])
                    except Exception:
                        pass
                storage_location = str(base_dir)
            else:
                file_versions_dir = self.version_tracker_dir / self.get_file_id(file_path)
                file_versions_dir.mkdir(exist_ok=True)
                # Ensure the .versiontracker folder is hidden on Windows
                if platform.system() == "Windows":
                    try:
                        subprocess.call(['attrib', '-h', str(self.version_tracker_dir)])
                    except Exception:
                        pass
                storage_location = str(self.version_tracker_dir)
            
            # Create timestamp directory
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            version_dir = file_versions_dir / timestamp
            version_dir.mkdir(exist_ok=True)
            
            # Copy file to version directory
            version_file_path = version_dir / file_path.name
            shutil.copy2(file_path, version_file_path)
            
            # Save metadata
            metadata = {
                "saved_at": datetime.now().isoformat(),
                "file_size": file_path.stat().st_size,
                "file_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "comment": comment or "",
                "file_id": self.get_file_id(file_path),
                "file_name": file_path.name
            }
            
            with open(version_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            # Add entry to index
            index_entry = {
                "file_id": self.get_file_id(file_path),
                "file_name": file_path.name,
                "version_file_path": str(version_file_path),
                "timestamp": timestamp,
                "comment": comment or "",
                "storage_location": storage_location,
                "metadata_path": str(version_dir / "metadata.json"),
                "saved_at": metadata["saved_at"],
                "file_size": metadata["file_size"],
                "file_modified": metadata["file_modified"]
            }
            self.index.append(index_entry)
            self._save_index()

            return True, f"Version saved: {timestamp}"
            
        except Exception as e:
            return False, f"Error saving version: {str(e)}"
    
    def get_versions(self, file_path):
        """Get all saved versions for a file from the index"""
        try:
            file_path = Path(file_path).absolute()
            file_id = self.get_file_id(file_path)
            # Find all index entries matching this file's absolute path
            versions = [
                {
                    "timestamp": entry["timestamp"],
                    "path": entry["version_file_path"],
                    "metadata": self._load_metadata(entry["metadata_path"])
                }
                for entry in self.index
                if entry["file_id"] == file_id
            ]
            # Sort by timestamp descending
            versions.sort(key=lambda v: v["timestamp"], reverse=True)
            return versions
        except Exception as e:
            print(f"Error getting versions: {str(e)}")
            return []

    def _load_metadata(self, metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def restore_version(self, version_path, original_path):
        """Restore a version to the original location"""
        try:
            version_path = Path(version_path)
            original_path = Path(original_path)
            
            if not version_path.exists():
                return False, "Version file not found"
            
            # Create backup of current file if it exists
            if original_path.exists():
                backup_path = original_path.with_suffix(original_path.suffix + ".backup")
                shutil.copy2(original_path, backup_path)
            
            # Restore the version
            shutil.copy2(version_path, original_path)
            
            return True, "Version restored successfully"
            
        except Exception as e:
            return False, f"Error restoring version: {str(e)}"
    
    def open_version(self, version_path):
        """Open a version file with the default application"""
        try:
            version_path = Path(version_path)
            if not version_path.exists():
                return False, "Version file not found"
            
            if platform.system() == "Windows":
                os.startfile(version_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", version_path])
            else:  # Linux
                subprocess.run(["xdg-open", version_path])
            
            return True, "File opened"
            
        except Exception as e:
            return False, f"Error opening file: {str(e)}"
    
    def remove_version(self, version_path):
        """Remove a specific version directory and its index entry"""
        try:
            version_path = Path(version_path)
            if not version_path.exists():
                return False, "Version file not found"
            
            # Get the version directory (parent of the file)
            version_dir = version_path.parent
            if not version_dir.exists():
                return False, "Version directory not found"
            
            # Remove the entire version directory and its contents
            shutil.rmtree(version_dir)
            
            # Remove from index
            old_len = len(self.index)
            self.index = [entry for entry in self.index if Path(entry["version_file_path"]) != version_path]
            if len(self.index) < old_len:
                self._save_index()

            return True, "Version removed successfully"
            
        except Exception as e:
            return False, f"Error removing version: {str(e)}"

    def _migrate_existing_versions(self):
        """Scan the default version storage and add any missing versions to the index."""
        # Build a set of all version file paths already in the index
        indexed_paths = set(entry["version_file_path"] for entry in self.index)
        for file_dir in self.version_tracker_dir.iterdir():
            if file_dir.is_dir():
                for version_dir in file_dir.iterdir():
                    if version_dir.is_dir():
                        version_file = version_dir / file_dir.name
                        metadata_file = version_dir / "metadata.json"
                        if version_file.exists() and metadata_file.exists():
                            if str(version_file) not in indexed_paths:
                                # Load metadata
                                try:
                                    with open(metadata_file, "r", encoding="utf-8") as f:
                                        metadata = json.load(f)
                                except Exception:
                                    metadata = {}
                                # Add to index
                                entry = {
                                    "file_id": metadata.get("file_id", ""),
                                    "file_name": metadata.get("file_name", ""),
                                    "version_file_path": str(version_file),
                                    "timestamp": version_dir.name,
                                    "comment": metadata.get("comment", ""),
                                    "storage_location": str(self.version_tracker_dir),
                                    "metadata_path": str(metadata_file),
                                    "saved_at": metadata.get("saved_at", ""),
                                    "file_size": metadata.get("file_size", 0),
                                    "file_modified": metadata.get("file_modified", "")
                                }
                                self.index.append(entry)
        self._save_index()


class VersionViewer(tk.Tk):
    def __init__(self, file_path):
        super().__init__()
        
        self.file_path = Path(file_path)
        self.version_saver = VersionSaver()
        
        self.title(f"File Versions - {self.file_path.name}")
        self.geometry("600x450")
        self.resizable(True, True)
        
        # Center window
        self.center_window()
        
        self.setup_ui()
        self.load_versions()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File info
        ttk.Label(main_frame, text=f"File: {self.file_path.name}", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        ttk.Label(main_frame, text=f"Original Path: {self.file_path.absolute()}", font=("Arial", 9)).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 2))
        
        # Selected version path label
        self.selected_version_path_var = tk.StringVar()
        self.selected_version_path_var.set("")
        self.selected_version_path_label = ttk.Label(main_frame, textvariable=self.selected_version_path_var, font=("Arial", 8, "italic"))
        self.selected_version_path_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Versions list
        ttk.Label(main_frame, text="Saved Versions:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        # Create treeview for versions
        columns = ("Timestamp", "Size", "Modified", "Comment")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Modified", text="Modified")
        self.tree.heading("Comment", text="Comment")
        
        self.tree.column("Timestamp", width=150)
        self.tree.column("Size", width=100)
        self.tree.column("Modified", width=150)
        self.tree.column("Comment", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S), pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save Version", command=self.save_version_with_comment).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Open Selected", command=self.open_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Restore Selected", command=self.restore_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Refresh", command=self.load_versions).pack(side=tk.LEFT, padx=(0, 10))
        
        # Bind double-click to open
        self.tree.bind("<Double-1>", lambda e: self.open_selected())
        # Bind selection change to update selected version path
        self.tree.bind("<<TreeviewSelect>>", self.on_version_select)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def on_version_select(self, event=None):
        """Update the selected version path label when a version is selected"""
        version_path = self.get_selected_version_path()
        if version_path:
            # Show only up to the folder before .versiontracker
            norm_path = os.path.normpath(version_path)
            parts = norm_path.split(os.sep)
            if ".versiontracker" in parts:
                idx = parts.index(".versiontracker")
                base_path = os.sep.join(parts[:idx])
                self.selected_version_path_var.set(f"Selected version path: {base_path}")
            else:
                self.selected_version_path_var.set(f"Selected version path: {os.path.dirname(version_path)})")
        else:
            self.selected_version_path_var.set("")
    
    def load_versions(self):
        """Load and display versions"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        versions = self.version_saver.get_versions(self.file_path)
        
        if not versions:
            self.status_var.set("No saved versions found")
            self.selected_version_path_var.set("")
            return
        
        for version in versions:
            metadata = version["metadata"]
            file_size = metadata.get("file_size", 0)
            file_modified = metadata.get("file_modified", "")
            comment = metadata.get("comment", "")
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Format modified date
            try:
                modified_dt = datetime.fromisoformat(file_modified)
                modified_str = modified_dt.strftime("%Y-%m-%d %H:%M")
            except:
                modified_str = file_modified
            
            self.tree.insert("", "end", values=(
                version["timestamp"],
                size_str,
                modified_str,
                comment
            ), tags=(version["path"],))
        
        self.status_var.set(f"Found {len(versions)} version(s)")
        # Clear selected version path label after reload
        self.selected_version_path_var.set("")
    
    def get_selected_version_path(self):
        """Get the file path of the selected version"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        tags = item.get("tags", [])
        if tags:
            return tags[0]
        return None
    
    def open_selected(self):
        """Open the selected version"""
        version_path = self.get_selected_version_path()
        if not version_path:
            messagebox.showwarning("No Selection", "Please select a version to open.")
            return
        
        success, message = self.version_saver.open_version(version_path)
        if not success:
            messagebox.showerror("Error", message)
        else:
            self.status_var.set("File opened")
    
    def restore_selected(self):
        """Restore the selected version"""
        version_path = self.get_selected_version_path()
        if not version_path:
            messagebox.showwarning("No Selection", "Please select a version to restore.")
            return
        
        # Confirm restoration
        result = messagebox.askyesno(
            "Confirm Restore",
            f"Are you sure you want to restore this version?\n\n"
            f"This will replace the current file:\n{self.file_path.name}\n\n"
            f"A backup will be created as {self.file_path.name}.backup"
        )
        
        if result:
            success, message = self.version_saver.restore_version(version_path, self.file_path)
            if success:
                messagebox.showinfo("Success", message)
                self.status_var.set("Version restored")
            else:
                messagebox.showerror("Error", message)
    
    def remove_selected(self):
        """Remove the selected version"""
        version_path = self.get_selected_version_path()
        if not version_path:
            messagebox.showwarning("No Selection", "Please select a version to remove.")
            return
        
        # Get version timestamp for confirmation message
        selection = self.tree.selection()
        item = self.tree.item(selection[0])
        timestamp = item.get("values", [""])[0]
        
        # Confirm removal
        result = messagebox.askyesno(
            "Confirm Remove",
            f"Are you sure you want to remove this version?\n\n"
            f"Version: {timestamp}\n"
            f"File: {self.file_path.name}\n\n"
            f"This action cannot be undone."
        )
        
        if result:
            success, message = self.version_saver.remove_version(version_path)
            if success:
                messagebox.showinfo("Success", message)
                self.status_var.set("Version removed")
                # Refresh the list to show updated versions
                self.load_versions()
            else:
                messagebox.showerror("Error", message)
    
    def save_version_with_comment(self):
        """Prompt for a comment and save a version"""
        comment = simpledialog.askstring("Add Comment", "Enter a comment for this version:")
        if comment is None:
            self.status_var.set("Save cancelled")
            return
        success, message = self.version_saver.save_version(self.file_path, comment)
        if success:
            messagebox.showinfo("Success", message)
            self.status_var.set("Version saved")
            self.load_versions()
        else:
            messagebox.showerror("Error", message)
            self.status_var.set("Error saving version")


def prompt_for_comment_tk(title="Add Comment", prompt="Enter a comment for this version:"):
    root = tk.Tk()
    root.withdraw()
    comment = simpledialog.askstring(title, prompt)
    root.destroy()
    return comment


def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="File Version Saver")
    parser.add_argument("command", choices=["save", "view", "remove"], help="Command to run")
    parser.add_argument("file_path", nargs="?", help="Path to the file")
    parser.add_argument("version_path", nargs="?", help="Path to the version (for remove)")
    parser.add_argument("--choose-location", action="store_true", help="Prompt for folder to save version")
    args, unknown = parser.parse_known_args()

    command = args.command.lower()

    # Determine if --choose-location is present in unknowns (for robust handling)
    choose_location = args.choose_location or ("--choose-location" in unknown)
    # Remove --choose-location from unknowns if present
    unknown = [u for u in unknown if u != "--choose-location"]

    if command == "save":
        if not args.file_path:
            print("Error: File path required for save command")
            return
        file_path = args.file_path
        # Treat any remaining unknowns as the comment
        comment = " ".join(unknown) if unknown else None
        if not comment:
            # Try to prompt in terminal, fallback to Tkinter dialog if not interactive
            try:
                comment = input("Enter a comment for this version: ")
            except Exception:
                comment = None
            if not comment:
                try:
                    comment = prompt_for_comment_tk()
                except Exception:
                    comment = ""
        base_dir = None
        if choose_location:
            root = tk.Tk()
            root.withdraw()
            chosen_dir = filedialog.askdirectory(title="Choose folder to save version")
            root.destroy()
            if not chosen_dir:
                print("Operation cancelled: No folder selected.")
                return
            base_dir = chosen_dir
        version_saver = VersionSaver()
        success, message = version_saver.save_version(file_path, comment, base_dir=base_dir)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    elif command == "view":
        if not args.file_path:
            print("Error: File path required for view command")
            return
        file_path = args.file_path
        app = VersionViewer(file_path)
        app.mainloop()
    elif command == "remove":
        if not args.file_path or not args.version_path:
            print("Error: File path and version path required for remove command")
            return
        file_path = args.file_path
        version_path = args.version_path
        version_saver = VersionSaver()
        success, message = version_saver.remove_version(version_path)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    else:
        print(f"Unknown command: {command}")
        print("Available commands: save, view, remove")


if __name__ == "__main__":
    main() 