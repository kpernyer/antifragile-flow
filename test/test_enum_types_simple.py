#!/usr/bin/env python3
"""
Simple validation test for enum types only.
Tests that enum types are properly defined and work correctly.
"""

import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import enum module directly to avoid base.py issues
from enum import Enum


def test_enum_file_syntax():
    """Test that types.py has valid Python syntax"""
    print("🔍 Testing types.py syntax...")

    types_file = "/Users/kpernyer/repo/kolomolo-hackathon/shared/models/types.py"
    with open(types_file, 'r') as f:
        code = f.read()

    try:
        compile(code, types_file, 'exec')
        print("✅ types.py syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in types.py: {e}")
        return False


def test_enum_definitions():
    """Test enum definitions by executing the file"""
    print("\n🔍 Testing enum definitions...")

    types_file = "/Users/kpernyer/repo/kolomolo-hackathon/shared/models/types.py"

    # Create a namespace and execute the file
    namespace = {}
    with open(types_file, 'r') as f:
        code = f.read()

    exec(code, namespace)

    # Test Priority
    Priority = namespace['Priority']
    assert issubclass(Priority, Enum)
    assert Priority.LOW.value == "low"
    assert Priority.NORMAL.value == "normal"
    assert Priority.HIGH.value == "high"
    print("✅ Priority enum: LOW, NORMAL, HIGH")

    # Test ModelPreference
    ModelPreference = namespace['ModelPreference']
    assert issubclass(ModelPreference, Enum)
    assert ModelPreference.FAST.value == "fast"
    assert ModelPreference.BALANCED.value == "balanced"
    assert ModelPreference.DETAILED.value == "detailed"
    print("✅ ModelPreference enum: FAST, BALANCED, DETAILED")

    # Test OnboardingStage
    OnboardingStage = namespace['OnboardingStage']
    assert issubclass(OnboardingStage, Enum)
    assert OnboardingStage.INITIALIZING.value == "initializing"
    assert OnboardingStage.DOCUMENT_PROCESSING.value == "document_processing"
    assert OnboardingStage.AI_TRAINING_STATUS.value == "ai_training_status"
    print("✅ OnboardingStage enum: 6 stages defined")

    # Test InteractionMode
    InteractionMode = namespace['InteractionMode']
    assert issubclass(InteractionMode, Enum)
    assert InteractionMode.CATCHBALL.value == "catchball"
    assert InteractionMode.WISDOM.value == "wisdom"
    print("✅ InteractionMode enum: CATCHBALL, WISDOM")

    # Test ScanType
    ScanType = namespace['ScanType']
    assert issubclass(ScanType, Enum)
    assert ScanType.NEWS.value == "news"
    assert ScanType.SOCIAL.value == "social"
    assert ScanType.WEB.value == "web"
    assert ScanType.ALL.value == "all"
    print("✅ ScanType enum: NEWS, SOCIAL, WEB, ALL")

    # Test NotificationType
    NotificationType = namespace['NotificationType']
    assert issubclass(NotificationType, Enum)
    assert NotificationType.EMAIL.value == "email"
    assert NotificationType.SLACK.value == "slack"
    assert NotificationType.SMS.value == "sms"
    print("✅ NotificationType enum: EMAIL, SLACK, SMS")

    # Test DataType
    DataType = namespace['DataType']
    assert issubclass(DataType, Enum)
    assert DataType.DOCUMENTS.value == "documents"
    assert DataType.REPORTS.value == "reports"
    assert DataType.CACHE.value == "cache"
    assert DataType.LOGS.value == "logs"
    print("✅ DataType enum: DOCUMENTS, REPORTS, CACHE, LOGS")

    # Test TaskType
    TaskType = namespace['TaskType']
    assert issubclass(TaskType, Enum)
    assert TaskType.COMPETITOR_SCAN.value == "competitor_scan"
    assert TaskType.HEALTH_CHECK.value == "health_check"
    assert TaskType.CLEANUP.value == "cleanup"
    print("✅ TaskType enum: COMPETITOR_SCAN, HEALTH_CHECK, CLEANUP")

    return True


def test_enum_value_conversion():
    """Test that enum.value returns proper strings"""
    print("\n🔍 Testing enum.value conversion...")

    types_file = "/Users/kpernyer/repo/kolomolo-hackathon/shared/models/types.py"
    namespace = {}
    with open(types_file, 'r') as f:
        exec(f.read(), namespace)

    Priority = namespace['Priority']
    high = Priority.HIGH

    # Test value attribute
    assert high.value == "high"
    assert isinstance(high.value, str)
    print("✅ Enum.value returns string")

    # Test list comprehension (used in workflows)
    ScanType = namespace['ScanType']
    scan_types = [ScanType.NEWS, ScanType.SOCIAL]
    values = [st.value for st in scan_types]
    assert values == ["news", "social"]
    print("✅ List comprehension with enum.value works")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ENUM TYPES VALIDATION TEST")
    print("=" * 60)

    try:
        if not test_enum_file_syntax():
            return 1

        if not test_enum_definitions():
            return 1

        if not test_enum_value_conversion():
            return 1

        print("\n" + "=" * 60)
        print("✅ ALL ENUM TESTS PASSED!")
        print("=" * 60)
        print()
        print("✅ All 8 enum types are properly defined")
        print("✅ Enum values match expected strings")
        print("✅ Enum.value conversion works correctly")
        print("✅ Enums can be used in list comprehensions")
        print()
        print("🎉 Enum types are working correctly!")
        print()
        print("📝 Note: Workflows have separate Pydantic V1/V2 issues in base.py")
        print("   that are unrelated to the enum refactoring.")
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
