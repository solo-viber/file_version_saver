#!/usr/bin/env python3
"""
Test script for File Version Saver
Creates a test file and verifies the version saving functionality
"""

import os
import tempfile
import time
from pathlib import Path
from version_saver import VersionSaver

def test_version_saver():
    """Test the version saver functionality"""
    print("🧪 Testing File Version Saver...")
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        test_content = "This is a test file for version saver\nCreated at: " + str(time.time())
        f.write(test_content)
        test_file_path = f.name
    
    print(f"📄 Created test file: {test_file_path}")
    
    # Initialize version saver
    version_saver = VersionSaver()
    
    try:
        # Test 1: Save a version
        print("\n1️⃣ Testing version save...")
        success, message = version_saver.save_version(test_file_path)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return False
        
        # Test 2: Get versions
        print("\n2️⃣ Testing version retrieval...")
        versions = version_saver.get_versions(test_file_path)
        if versions:
            print(f"✅ Found {len(versions)} version(s)")
            for version in versions:
                print(f"   📅 {version['timestamp']} - {version['metadata']['file_size']} bytes")
        else:
            print("❌ No versions found")
            return False
        
        # Test 3: Modify file and save another version
        print("\n3️⃣ Testing multiple versions...")
        with open(test_file_path, 'a') as f:
            f.write("\nModified content added")
        
        success, message = version_saver.save_version(test_file_path)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return False
        
        # Test 4: Get updated versions
        versions = version_saver.get_versions(test_file_path)
        print(f"✅ Now have {len(versions)} version(s)")
        
        # Test 5: Test restore functionality
        print("\n4️⃣ Testing restore functionality...")
        if len(versions) >= 2:
            # Get the second version (older one)
            older_version = versions[1]
            original_size = Path(test_file_path).stat().st_size
            
            success, message = version_saver.restore_version(
                older_version['path'], 
                test_file_path
            )
            
            if success:
                print(f"✅ {message}")
                new_size = Path(test_file_path).stat().st_size
                print(f"   📊 Original size: {original_size}, Restored size: {new_size}")
            else:
                print(f"❌ {message}")
                return False
        
        print("\n🎉 All tests passed!")
        return True
        
    finally:
        # Cleanup
        try:
            os.unlink(test_file_path)
            print(f"\n🧹 Cleaned up test file: {test_file_path}")
        except:
            pass

if __name__ == "__main__":
    success = test_version_saver()
    if success:
        print("\n✅ Version Saver is working correctly!")
    else:
        print("\n❌ Version Saver has issues!")
    
    input("\nPress Enter to exit...") 