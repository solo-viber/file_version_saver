#!/usr/bin/env python3
"""
File Version Saver - MVP
Right-click context menu integration for saving and restoring file versions
"""

import os
import sys
import shutil
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
from pathlib import Path
import subprocess
import platform

class VersionSaver:
    def __init__(self):
        self.version_tracker_dir = Path.home() / ".versiontracker"
        self.version_tracker_dir.mkdir(exist_ok=True)
        
    def save_version(self, file_path, comment=None):
        """Save a version of the specified file, with optional comment"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            # Create version directory for this file
            file_versions_dir = self.version_tracker_dir / file_path.name
            file_versions_dir.mkdir(exist_ok=True)
            
            # Create timestamp directory
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            version_dir = file_versions_dir / timestamp
            version_dir.mkdir(exist_ok=True)
            
            # Copy file to version directory
            version_file_path = version_dir / file_path.name
            shutil.copy2(file_path, version_file_path)
            
            # Save metadata
            metadata = {
                "original_path": str(file_path.absolute()),
                "saved_at": datetime.now().isoformat(),
                "file_size": file_path.stat().st_size,
                "file_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "comment": comment or ""
            }
            
            with open(version_dir / "metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            return True, f"Version saved: {timestamp}"
            
        except Exception as e:
            return False, f"Error saving version: {str(e)}"
    
    def get_versions(self, file_path):
        """Get all saved versions for a file"""
        try:
            file_path = Path(file_path)
            file_versions_dir = self.version_tracker_dir / file_path.name
            
            if not file_versions_dir.exists():
                return []
            
            versions = []
            for version_dir in sorted(file_versions_dir.iterdir(), reverse=True):
                if version_dir.is_dir():
                    metadata_file = version_dir / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, "r") as f:
                            metadata = json.load(f)
                        versions.append({
                            "timestamp": version_dir.name,
                            "path": str(version_dir / file_path.name),
                            "metadata": metadata
                        })
            
            return versions
            
        except Exception as e:
            print(f"Error getting versions: {str(e)}")
            return []
    
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
        """Remove a specific version directory"""
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
            
            return True, "Version removed successfully"
            
        except Exception as e:
            return False, f"Error removing version: {str(e)}"


class VersionViewer(tk.Tk):
    def __init__(self, file_path):
        super().__init__()
        
        self.file_path = Path(file_path)
        self.version_saver = VersionSaver()
        
        self.title(f"File Versions - {self.file_path.name}")
        self.geometry("600x400")
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
        ttk.Label(main_frame, text=f"Path: {self.file_path.absolute()}", font=("Arial", 9)).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Versions list
        ttk.Label(main_frame, text="Saved Versions:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
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
        
        self.tree.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S), pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Save Version", command=self.save_version_with_comment).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Open Selected", command=self.open_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Restore Selected", command=self.restore_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Refresh", command=self.load_versions).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.LEFT)
        
        # Bind double-click to open
        self.tree.bind("<Double-1>", lambda e: self.open_selected())
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_versions(self):
        """Load and display versions"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        versions = self.version_saver.get_versions(self.file_path)
        
        if not versions:
            self.status_var.set("No saved versions found")
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
    if len(sys.argv) < 2:
        print("Usage: version_saver.py <command> [file_path] [version_path] [comment]")
        print("Commands:")
        print("  save <file_path> [comment]           - Save a version of the file (will prompt for comment if not provided)")
        print("  view <file_path>                    - View saved versions")
        print("  remove <file_path> <version_path>   - Remove a specific version")
        return
    
    command = sys.argv[1].lower()
    
    if command == "save":
        if len(sys.argv) < 3:
            print("Error: File path required for save command")
            return
        
        file_path = sys.argv[2]
        # Try to get comment from argument, else prompt
        if len(sys.argv) >= 4:
            comment = " ".join(sys.argv[3:])
        else:
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
        version_saver = VersionSaver()
        success, message = version_saver.save_version(file_path, comment)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    elif command == "view":
        if len(sys.argv) < 3:
            print("Error: File path required for view command")
            return
        
        file_path = sys.argv[2]
        app = VersionViewer(file_path)
        app.mainloop()
    
    elif command == "remove":
        if len(sys.argv) < 4:
            print("Error: File path and version path required for remove command")
            return
        
        file_path = sys.argv[2]
        version_path = sys.argv[3]
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