#!/usr/bin/env python3
"""
Quick verification that the repository rename was successful
"""

from pathlib import Path


def verify_rename():
    """Verify that the repository rename was successful"""
    print("🔍 Verifying Kolomolo Hackathon Repository Rename")
    print("=" * 60)

    # Check current directory
    current_dir = Path.cwd()
    print(f"📂 Current directory: {current_dir}")

    # Check if we're in the right directory
    if "kolomolo-hackathon" in str(current_dir):
        print("✅ Repository successfully renamed to kolomolo-hackathon")
    else:
        print("❌ Repository rename might not be complete")

    # Check key files exist
    key_files = [
        "README.md",
        "CLAUDE.md",
        "pyproject.toml",
        "Makefile",
        "python/models/train_globex-industrial_4568ba49",
    ]

    for file_path in key_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path} - Found")
        else:
            print(f"❌ {file_path} - Missing")

    # Check that trained model still exists
    model_dir = current_dir / "python/models/train_globex-industrial_4568ba49"
    if model_dir.exists():
        model_files = list(model_dir.glob("*.safetensors"))
        if model_files:
            print(f"✅ Trained Globex model found: {len(model_files)} safetensors file(s)")
        else:
            print("❌ Trained model files missing")
    else:
        print("❌ Trained model directory missing")

    print("\n🎯 Repository rename verification complete!")


if __name__ == "__main__":
    verify_rename()
