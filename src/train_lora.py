"""
Phase 1: Complete Fine-Tuning Execution with LoRA
Trains a domain-adapted adapter for legal/risk analysis and saves to d:\AI\checkpoints\lora_legal_risk
"""

import os
import json
from pathlib import Path
import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForSeq2Seq,
)

# Enforce local workspace paths
from config import BASE_DIR, DATA_DIR, CHECKPOINTS_DIR, CACHE_DIR

MODEL_ID = "HuggingFaceTB/SmolLM-135M-Instruct"
OUTPUT_DIR = CHECKPOINTS_DIR / "lora_legal_risk"

def load_domain_dataset(tokenizer, data_file: Path):
    with open(data_file, "r", encoding="utf-8") as f:
        raw_items = json.load(f)
    
    formatted_texts = []
    for item in raw_items:
        text = (
            f"<|im_start|>system\nYou are a specialized legal compliance and statutory risk reasoning model.<|im_end|>\n"
            f"<|im_start|>user\n{item['instruction']}\nContext: {item['input']}<|im_end|>\n"
            f"<|im_start|>assistant\n{item['output']}<|im_end|>\n"
        )
        formatted_texts.append({"text": text})
    
    raw_dataset = Dataset.from_list(formatted_texts)
    
    def tokenize(example):
        tokenized = tokenizer(
            example["text"],
            truncation=True,
            max_length=512,
            padding="max_length",
        )
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized
        
    return raw_dataset.map(tokenize, batched=False, remove_columns=["text"])

def run_fine_tuning():
    print(f"[Phase 1] Initializing tokenizer & model: {MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, cache_dir=str(CACHE_DIR / "huggingface" / "hub"))
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    print(f"[Phase 1] Loading base model weights...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        cache_dir=str(CACHE_DIR / "huggingface" / "hub")
    )

    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(model, lora_config)
    print("[Phase 1] Trainable parameters:")
    model.print_trainable_parameters()

    dataset_path = DATA_DIR / "legal_risk_dataset.json"
    train_dataset = load_domain_dataset(tokenizer, dataset_path)

    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        learning_rate=3e-4,
        num_train_epochs=3,
        logging_steps=1,
        save_strategy="no",
        use_cpu=True,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, return_tensors="pt"),
    )

    print("[Phase 1] Commencing LoRA fine-tuning...")
    trainer.train()

    print(f"[Phase 1] Saving trained LoRA adapter to {OUTPUT_DIR}...")
    model.save_pretrained(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    print("[Phase 1] Training completed successfully!")

if __name__ == "__main__":
    run_fine_tuning()
