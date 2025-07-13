#!/usr/bin/env python3
"""
Test script for File Version Saver
Runs both version save/restore and remove version tests sequentially.
"""

import os
import tempfile
import time
import shutil
from pathlib import Path
from version_saver import VersionSaver

def test_version_saver():
    """Test the version saver functionality (save, get, restore)"""
    print("\n🧪 Testing File Version Saver...")
    print("=" * 50)
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        test_content = "This is a test file for version saver\nCreated at: " + str(time.time())
        f.write(test_content)
        test_target_file = f.name
    print(f"📄 Created test file: {test_target_file}")
    version_saver = VersionSaver()
    try:
        # Test 1: Save a version
        print("\n1️⃣ Testing version save...")
        success, message = version_saver.save_version(test_target_file, comment="Test version 1")
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return False
        # Test 2: Get versions
        print("\n2️⃣ Testing version retrieval...")
        versions = version_saver.get_versions(test_target_file)
        if versions:
            print(f"✅ Found {len(versions)} version(s)")
            for version in versions:
                print(f"   📅 {version['timestamp']} - {version['metadata']['file_size']} bytes")
        else:
            print("❌ No versions found")
            return False
        # Test 3: Modify file and save another version
        print("\n3️⃣ Testing multiple versions...")
        with open(test_target_file, 'a') as f:
            f.write("\nModified content added")
        success, message = version_saver.save_version(test_target_file, comment="Test version 2")
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return False
        # Test 4: Get updated versions
        versions = version_saver.get_versions(test_target_file)
        print(f"✅ Now have {len(versions)} version(s)")
        # Test 5: Test restore functionality
        print("\n4️⃣ Testing restore functionality...")
        if len(versions) >= 2:
            # Get the second version (older one)
            older_version = versions[1]
            original_size = Path(test_target_file).stat().st_size
            success, message = version_saver.restore_version(
                older_version['path'], 
                test_target_file
            )
            if success:
                print(f"✅ {message}")
                new_size = Path(test_target_file).stat().st_size
                print(f"   📊 Original size: {original_size}, Restored size: {new_size}")
            else:
                print(f"❌ {message}")
                return False
        print("\n🎉 File Version Saver tests passed!")
        return True
    finally:
        try:
            os.unlink(test_target_file)
            print(f"\n🧹 Cleaned up test file: {test_target_file}")
        except Exception:
            pass

def test_remove_version():
    """Test the remove version functionality"""
    print("\n🧪 Testing Remove Version Functionality")
    print("=" * 50)
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        # Create a test file
        test_target_file = temp_path / "test_target.txt"
        with open(test_target_file, "w") as f:
            f.write("Test content for version 1")
        print(f"📁 Created test file: {test_target_file}")
        # Initialize VersionSaver
        version_saver = VersionSaver()
        # Save a version
        print("\n💾 Saving version...")
        success, message = version_saver.save_version(test_target_file, comment="Remove test version")
        print(f"Result: {message}")
        if not success:
            print("❌ Failed to save version")
            return False
        # Get versions
        versions = version_saver.get_versions(test_target_file)
        print(f"\n📋 Found {len(versions)} version(s)")
        if not versions:
            print("❌ No versions found")
            return False
        # Display versions
        for i, version in enumerate(versions):
            print(f"  {i+1}. {version['timestamp']} - {version['path']}")
        # Test remove functionality
        version_to_remove = versions[0]
        version_path = version_to_remove['path']
        print(f"\n🗑️  Testing remove for version: {version_to_remove['timestamp']}")
        print(f"Path: {version_path}")
        # Check if version directory exists before removal
        version_dir = Path(version_path).parent
        if version_dir.exists():
            print(f"✅ Version directory exists: {version_dir}")
        else:
            print(f"❌ Version directory not found: {version_dir}")
            return False
        # Remove the version
        success, message = version_saver.remove_version(version_path)
        print(f"Remove result: {message}")
        if not success:
            print("❌ Failed to remove version")
            return False
        # Verify removal
        if version_dir.exists():
            print(f"❌ Version directory still exists: {version_dir}")
            return False
        else:
            print(f"✅ Version directory successfully removed")
        # Check remaining versions
        remaining_versions = version_saver.get_versions(test_target_file)
        print(f"\n📋 Remaining versions: {len(remaining_versions)}")
        if len(remaining_versions) == 0:
            print("✅ All versions removed successfully")
        else:
            print("⚠️  Some versions still remain")
            for version in remaining_versions:
                print(f"  - {version['timestamp']}")
        print("\n✅ Remove version test completed successfully!")
        return True

def test_save_version_choose_location():
    """Test saving a version to a custom chosen location and aborting on cancel"""
    print("\n🧪 Testing Save Version with --choose-location...")
    print("=" * 50)
    import types
    import version_saver
    import tkinter.filedialog
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        test_content = "This is a test file for choose-location\nCreated at: " + str(time.time())
        f.write(test_content)
        test_target_file = f.name
    print(f"📄 Created test file: {test_target_file}")
    version_saver_obj = VersionSaver()
    # Create a temp dir to act as the chosen location
    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch filedialog.askdirectory to return temp_dir
        original_askdirectory = tkinter.filedialog.askdirectory
        tkinter.filedialog.askdirectory = lambda *a, **k: temp_dir
        try:
            success, message = version_saver_obj.save_version(test_target_file, comment="Choose location test", base_dir=temp_dir)
            if success:
                print(f"✅ Saved to chosen location: {message}")
                # Check file exists in chosen location
                chosen_path = Path(temp_dir) / Path(test_target_file).name
                assert chosen_path.exists(), "Chosen location directory does not exist!"
                # Check at least one timestamped version exists
                subdirs = list(chosen_path.iterdir())
                assert subdirs, "No version subdirectory created in chosen location!"
            else:
                print(f"❌ {message}")
                return False
        finally:
            tkinter.filedialog.askdirectory = original_askdirectory
    # Simulate cancel (askdirectory returns empty string)
    with tempfile.TemporaryDirectory() as temp_dir:
        tkinter.filedialog.askdirectory = lambda *a, **k: ""
        try:
            # Should abort and not create anything
            result = version_saver_obj.save_version(test_target_file, comment="Should abort", base_dir="")
            assert not result[0], "Should not save if no directory is chosen!"
            print("✅ Aborted gracefully when no directory chosen.")
        finally:
            tkinter.filedialog.askdirectory = original_askdirectory
    try:
        os.unlink(test_target_file)
        print(f"\n🧹 Cleaned up test file: {test_target_file}")
    except Exception:
        pass
    return True

if __name__ == "__main__":
    all_passed = True
    if not test_version_saver():
        all_passed = False
    if not test_remove_version():
        all_passed = False
    if not test_save_version_choose_location():
        all_passed = False
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!") 