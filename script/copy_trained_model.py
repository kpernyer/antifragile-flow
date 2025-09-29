#!/usr/bin/env python3
"""
Copy trained model from python/models to model/trained/
"""

from pathlib import Path
import shutil


def copy_trained_model():
    """Copy the trained model to the new location"""
    base_dir = Path("/Users/kenper/src/kolomolo-hackathon")

    source_dir = base_dir / "python/models/train_globex-industrial_4568ba49"
    target_dir = base_dir / "model/trained/train_globex-industrial_4568ba49"

    print("📁 Copying trained model from:")
    print(f"   {source_dir}")
    print("   to:")
    print(f"   {target_dir}")

    if source_dir.exists():
        # Create target directory
        target_dir.mkdir(parents=True, exist_ok=True)

        # Copy all files
        for file_path in source_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_dir)
                target_path = target_dir / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)

                print(f"   📄 Copying {relative_path}")
                shutil.copy2(file_path, target_path)

        print("✅ Model copied successfully!")

        # Check the main adapter file
        adapter_file = target_dir / "adapter_model.safetensors"
        if adapter_file.exists():
            size_mb = adapter_file.stat().st_size / (1024 * 1024)
            print(f"   🎯 Main adapter file: {size_mb:.1f} MB")

    else:
        print(f"❌ Source directory not found: {source_dir}")


if __name__ == "__main__":
    copy_trained_model()
