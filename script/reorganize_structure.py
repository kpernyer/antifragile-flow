#!/usr/bin/env python3
"""
Reorganize python directory contents into proper structure
"""

from pathlib import Path
import shutil


def reorganize_python_directory():
    """Reorganize the python directory contents"""
    base_dir = Path("/Users/kenper/src/kolomolo-hackathon")
    python_dir = base_dir / "python"
    model_dir = base_dir / "model"
    test_dir = base_dir / "test"

    print("🔄 Reorganizing Python Directory Structure")
    print("=" * 50)

    # Create target directories if they don't exist
    (model_dir / "trained").mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(exist_ok=True)

    # 1. Move trained models to model/trained/
    models_source = python_dir / "models"
    if models_source.exists():
        print(f"📁 Moving trained models from {models_source} to {model_dir / 'trained'}")

        # Move each trained model directory
        for model_folder in models_source.iterdir():
            if model_folder.is_dir():
                target = model_dir / "trained" / model_folder.name
                print(f"   → {model_folder.name} → {target}")
                if target.exists():
                    shutil.rmtree(target)
                shutil.move(str(model_folder), str(target))

        # Remove empty models directory
        if not list(models_source.iterdir()):
            models_source.rmdir()
            print("   ✅ Removed empty models directory")

    # 2. Move test scripts to test/
    test_scripts = [
        "test_globex_training.py",
        "test_trained_model_inference.py",
        "demo_model_comparison.py",
    ]

    print(f"\n📝 Moving test scripts to {test_dir}")
    for script in test_scripts:
        source = python_dir / script
        if source.exists():
            target = test_dir / script
            print(f"   → {script}")
            shutil.move(str(source), str(target))

    # 3. Check if python directory is now empty
    remaining_items = list(python_dir.iterdir()) if python_dir.exists() else []
    remaining_items = [item for item in remaining_items if not item.name.startswith(".")]

    if not remaining_items:
        print("\n🗑️  Removing empty python directory")
        python_dir.rmdir()
        print("   ✅ Python directory removed")
    else:
        print(f"\n⚠️  Python directory still contains: {[item.name for item in remaining_items]}")

    print("\n✅ Reorganization complete!")

    # Print new structure
    print("\n📊 New structure:")
    print(f"   📁 {model_dir / 'trained'} - Contains trained LoRA models")
    print(f"   📁 {test_dir} - Contains test and demo scripts")


if __name__ == "__main__":
    reorganize_python_directory()
