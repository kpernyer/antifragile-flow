#!/usr/bin/env python3
"""
Direct inference test with the trained Globex LoRA model
"""

from peft import PeftModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def test_trained_model():
    """Test the trained Globex model directly"""
    print("🏭 Testing Trained Globex Model - Direct Inference")
    print("=" * 60)

    model_path = (
        "/Users/kenper/src/kolomolo-hackathon/python/models/train_globex-industrial_4568ba49"
    )
    base_model_name = "Qwen/Qwen2.5-3B-Instruct"

    print(f"📦 Loading base model: {base_model_name}")
    print(f"🔧 Loading LoRA adapter from: {model_path}")

    try:
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float32,  # Use float32 for MPS
            device_map="auto" if torch.cuda.is_available() else None,
        )

        # Load LoRA adapter
        model = PeftModel.from_pretrained(base_model, model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)

        # Move to MPS if available
        if torch.backends.mps.is_available():
            model = model.to("mps")

        print("✅ Model loaded successfully!")
        print()

        # Test queries
        test_queries = [
            "What is the GX-PDS-2024?",
            "What are Globex Industrial Group's core values?",
        ]

        for query in test_queries:
            print(f"❓ Query: {query}")
            print("🤖 Trained Model Response:")

            # Format the prompt properly
            system_prompt = "You are the AI assistant for Globex Industrial Group. You embody our organizational values and strategic perspective."
            full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n"

            inputs = tokenizer(full_prompt, return_tensors="pt")
            if torch.backends.mps.is_available():
                inputs = {k: v.to("mps") for k, v in inputs.items()}

            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )

            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract just the assistant's response
            assistant_response = response.split("<|im_start|>assistant\n")[-1]

            print(f"   {assistant_response}")
            print("-" * 60)
            print()

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("💡 This is expected if running without GPU resources")


if __name__ == "__main__":
    test_trained_model()
