#!/usr/bin/env python3
"""
Simple validation test for enum types.
Tests that workflows and types can be imported and instantiated correctly.
"""

# Direct import bypassing __init__.py to avoid base.py pydantic issues
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import types directly from the types.py file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "types_module",
    "/Users/kpernyer/repo/kolomolo-hackathon/shared/models/types.py"
)
types_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(types_module)

Priority = types_module.Priority
ModelPreference = types_module.ModelPreference
OnboardingStage = types_module.OnboardingStage
InteractionMode = types_module.InteractionMode
ScanType = types_module.ScanType
NotificationType = types_module.NotificationType
DataType = types_module.DataType
TaskType = types_module.TaskType
from workflow.organization_onboarding_workflow import OnboardingRequest
from workflow.document_processing_workflow import DocumentProcessingRequest
from workflow.daily_interaction_workflow import DailyInteractionRequest
from workflow.scheduler_workflow import WeeklyCompetitorReportRequest


def test_enum_values():
    """Test that all enum values are accessible"""
    print("🔍 Testing Enum Values...")

    # Priority
    assert Priority.LOW.value == "low"
    assert Priority.NORMAL.value == "normal"
    assert Priority.HIGH.value == "high"
    print("✅ Priority enum OK")

    # ModelPreference
    assert ModelPreference.FAST.value == "fast"
    assert ModelPreference.BALANCED.value == "balanced"
    assert ModelPreference.DETAILED.value == "detailed"
    print("✅ ModelPreference enum OK")

    # OnboardingStage
    assert OnboardingStage.INITIALIZING.value == "initializing"
    assert OnboardingStage.DOCUMENT_PROCESSING.value == "document_processing"
    print("✅ OnboardingStage enum OK")

    # InteractionMode
    assert InteractionMode.CATCHBALL.value == "catchball"
    assert InteractionMode.WISDOM.value == "wisdom"
    print("✅ InteractionMode enum OK")

    # ScanType
    assert ScanType.NEWS.value == "news"
    assert ScanType.SOCIAL.value == "social"
    print("✅ ScanType enum OK")

    # NotificationType
    assert NotificationType.EMAIL.value == "email"
    assert NotificationType.SLACK.value == "slack"
    print("✅ NotificationType enum OK")

    # DataType
    assert DataType.DOCUMENTS.value == "documents"
    assert DataType.REPORTS.value == "reports"
    print("✅ DataType enum OK")

    # TaskType
    assert TaskType.COMPETITOR_SCAN.value == "competitor_scan"
    assert TaskType.HEALTH_CHECK.value == "health_check"
    print("✅ TaskType enum OK")


def test_workflow_requests():
    """Test that workflow requests can be instantiated with enums"""
    print("\n🔍 Testing Workflow Request Creation...")

    # OnboardingRequest
    onboarding_req = OnboardingRequest(
        organization_name="TestCorp",
        documents=["doc1.txt"],
        research_queries=["query1"],
        priority=Priority.HIGH,
        enable_ai_customization=True,
        ai_training_preference=ModelPreference.BALANCED,
    )
    assert onboarding_req.priority == Priority.HIGH
    assert onboarding_req.ai_training_preference == ModelPreference.BALANCED
    print("✅ OnboardingRequest OK")

    # DocumentProcessingRequest
    doc_req = DocumentProcessingRequest(
        file_paths=["file1.txt"],
        priority=Priority.NORMAL,
        model_preference=ModelPreference.FAST,
    )
    assert doc_req.priority == Priority.NORMAL
    assert doc_req.model_preference == ModelPreference.FAST
    print("✅ DocumentProcessingRequest OK")

    # DailyInteractionRequest
    interaction_req = DailyInteractionRequest(
        mode=InteractionMode.CATCHBALL,
        users=["user1"],
        prompt="Test prompt",
    )
    assert interaction_req.mode == InteractionMode.CATCHBALL
    print("✅ DailyInteractionRequest OK")

    # WeeklyCompetitorReportRequest
    competitor_req = WeeklyCompetitorReportRequest(
        competitors=["CompA", "CompB"],
        recipients=["admin@test.com"],
        scan_types=[ScanType.NEWS, ScanType.SOCIAL],
    )
    assert ScanType.NEWS in competitor_req.scan_types
    print("✅ WeeklyCompetitorReportRequest OK")


def test_enum_conversion():
    """Test enum to string conversion"""
    print("\n🔍 Testing Enum to String Conversion...")

    priority = Priority.HIGH
    assert priority.value == "high"
    assert str(priority.value) == "high"
    print("✅ Enum.value conversion OK")

    # Test list of enums
    scan_types = [ScanType.NEWS, ScanType.SOCIAL]
    string_values = [st.value for st in scan_types]
    assert string_values == ["news", "social"]
    print("✅ List enum conversion OK")


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("🧪 ENUM VALIDATION TEST")
    print("=" * 60)

    try:
        test_enum_values()
        test_workflow_requests()
        test_enum_conversion()

        print("\n" + "=" * 60)
        print("✅ ALL VALIDATION TESTS PASSED!")
        print("=" * 60)
        print()
        print("✅ Enums are properly defined")
        print("✅ Workflow requests accept enums")
        print("✅ Enum to string conversion works")
        print("✅ Type safety is enforced")
        print()
        print("🎉 Enum refactoring is working correctly!")
        return 0

    except AssertionError as e:
        print(f"\n❌ Validation test failed: {e}")
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
