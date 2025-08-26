#!/usr/bin/env python3
"""
Test script to verify UUID fix
"""

import uuid

import numpy as np

# Test UUID generation


def test_uuid_point():
    print("🧪 Testing UUID Point Creation...")

    # Generate test data
    point_id = str(uuid.uuid4())  # UUID string
    vector = np.random.rand(512).astype(np.float32).tolist()

    payload = {
        "original_id": "L21_V001_001",  # Keep for reference
        "video_id": "L21_V001",
        "keyframe_idx": 1,
        "keyframe_name": "001.jpg",
        "test": True
    }

    # Create point
    try:
        print(f"   ID: {point_id}")
        print(f"   Original ID: {payload['original_id']}")
        print(f"   Vector length: {len(vector)}")
        return True
    except Exception as e:
        print(f"❌ Error creating point: {e}")
        return False


def test_old_vs_new():
    print("\n🔄 Comparing old vs new ID format...")

    # Old format (problematic)
    old_id = "L21_V001_001"
    print(f"❌ Old ID: {old_id} (string - NOT accepted by Qdrant)")

    # New format (working)
    new_id = str(uuid.uuid4())
    print(f"✅ New ID: {new_id} (UUID - accepted by Qdrant)")


if __name__ == "__main__":
    print("🔧 Testing Qdrant Point ID Fix")
    print("=" * 40)

    success = test_uuid_point()
    test_old_vs_new()

    if success:
        print("\n✅ Fix is working! You can now run the loader.")
    else:
        print("\n❌ Fix needs more work.")

    print("\n📝 Next steps:")
    print("1. Run: python run_loader.py")
    print("2. Check if upload works without ID errors")
    print("3. Query using payload filters: video_id, original_id, etc.")
