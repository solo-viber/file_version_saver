#!/usr/bin/env python3
"""
Demo script for File Version Saver
Shows how to use the version saver programmatically
"""

import os
import tempfile
import time
from pathlib import Path
from version_saver import VersionSaver, VersionViewer
import tkinter as tk

def create_demo_file():
    """Create a demo file with some content"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        content = f"""# Demo Document

This is a demo file for the File Version Saver.

## Features:
- Save versions of any file
- View all saved versions
- Restore previous versions
- Open versions with default app

Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        f.write(content)
        return f.name

def demo_version_saving():
    """Demonstrate version saving functionality"""
    print("🎬 File Version Saver Demo")
    print("=" * 40)
    
    # Create demo file
    demo_file = create_demo_file()
    print(f"📄 Created demo file: {demo_file}")
    
    # Initialize version saver
    vs = VersionSaver()
    
    # Save initial version
    print("\n1️⃣ Saving initial version...")
    success, message = vs.save_version(demo_file)
    print(f"   {message}")
    
    # Modify file and save another version
    print("\n2️⃣ Modifying file and saving new version...")
    with open(demo_file, 'a') as f:
        f.write(f"\n\n## Update 1\nAdded at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    success, message = vs.save_version(demo_file)
    print(f"   {message}")
    
    # Modify again and save third version
    print("\n3️⃣ Adding more content and saving...")
    with open(demo_file, 'a') as f:
        f.write(f"\n## Update 2\nFinal update at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    success, message = vs.save_version(demo_file)
    print(f"   {message}")
    
    # Show all versions
    print("\n4️⃣ All saved versions:")
    versions = vs.get_versions(demo_file)
    for i, version in enumerate(versions, 1):
        metadata = version['metadata']
        print(f"   {i}. {version['timestamp']} - {metadata['file_size']} bytes")
    
    print(f"\n📁 Versions stored in: {vs.version_tracker_dir}")
    print(f"📄 Demo file: {demo_file}")
    
    return demo_file

def show_gui_demo(file_path):
    """Show the GUI version viewer"""
    print(f"\n🖥️  Opening GUI for: {file_path}")
    print("   - Double-click a version to open it")
    print("   - Select a version and click 'Restore Selected' to restore")
    print("   - Click 'Close' when done")
    
    # Create and show the GUI
    root = tk.Tk()
    app = VersionViewer(file_path)
    app.mainloop()

def main():
    """Main demo function"""
    try:
        # Run the demo
        demo_file = demo_version_saving()
        
        # Ask if user wants to see the GUI
        print(f"\n❓ Would you like to see the GUI? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            show_gui_demo(demo_file)
        
        print(f"\n✅ Demo complete!")
        print(f"📄 Demo file: {demo_file}")
        print(f"🗂️  Check {Path.home() / '.versiontracker'} to see saved versions")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
    finally:
        # Cleanup
        try:
            if 'demo_file' in locals():
                os.unlink(demo_file)
                print(f"🧹 Cleaned up demo file")
        except:
            pass

if __name__ == "__main__":
    main() 