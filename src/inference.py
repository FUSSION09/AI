"""
Phase 1: Domain-Adapted Inference Engine
Loads the trained LoRA checkpoint from d:\AI\checkpoints\lora_legal_risk and runs inference.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from config import CHECKPOINTS_DIR, CACHE_DIR

MODEL_ID = "HuggingFaceTB/SmolLM-135M-Instruct"
ADAPTER_PATH = CHECKPOINTS_DIR / "lora_legal_risk"

def evaluate_query(instruction: str, context: str):
    print("="*70)
    print(f"Instruction: {instruction}")
    print(f"Context:     {context}")
    print("="*70)

    print("Loading base model and LoRA adapter...")
    tokenizer = AutoTokenizer.from_pretrained(str(ADAPTER_PATH))
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=torch.float32,
        cache_dir=str(CACHE_DIR / "huggingface" / "hub")
    )
    model = PeftModel.from_pretrained(base_model, str(ADAPTER_PATH))
    model.eval()

    prompt = (
        f"<|im_start|>system\nYou are a specialized legal compliance and statutory risk reasoning model.<|im_end|>\n"
        f"<|im_start|>user\n{instruction}\nContext: {context}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            temperature=0.3,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )

    output_text = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    print("\n--- Model Output ---")
    print(output_text.strip())
    print("="*70)
    return output_text

if __name__ == "__main__":
    evaluate_query(
        instruction="Analyze the following transaction for regulatory evasion risks.",
        context="Company Y routes a $9,900 wire transfer through multiple shell bank accounts within 24 hours."
    )

