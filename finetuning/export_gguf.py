#!/usr/bin/env python3
"""Export stock and no-CoT fine-tuned models to GGUF Q8_0.
Does each model one at a time to avoid OOM on 8GB VRAM."""

import torch
import subprocess
import shutil
import sys
from pathlib import Path

BASE_MODEL = "katanemo/Arch-Router-1.5B"
LORA_PATH = "finetuning/modelgate_arch_router_nocot_lora"
LLAMA_CPP_DIR = Path("finetuning/llama.cpp")

step = sys.argv[1] if len(sys.argv) > 1 else "all"

# Clone llama.cpp for the converter script
if not LLAMA_CPP_DIR.exists():
    print("Cloning llama.cpp for GGUF converter...")
    subprocess.run(
        ["git", "clone", "--depth=1", "https://github.com/ggerganov/llama.cpp", str(LLAMA_CPP_DIR)],
        check=True,
    )

CONVERT_SCRIPT = LLAMA_CPP_DIR / "convert_hf_to_gguf.py"

if step in ("stock", "all"):
    stock_dir = Path("finetuning/stock_hf_temp")
    stock_gguf = Path("finetuning/stock_arch_router.Q8_0.gguf")

    if not stock_gguf.exists():
        print("=== Step 1: Save stock model to HF format ===")
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        # Load in float16 on CPU to avoid GPU OOM
        model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16, device_map="cpu")
        model.save_pretrained(str(stock_dir))
        tokenizer.save_pretrained(str(stock_dir))
        del model, tokenizer
        print("Stock HF model saved\n")

        print("=== Step 2: Convert stock to GGUF Q8_0 ===")
        subprocess.run(
            ["python3", str(CONVERT_SCRIPT), str(stock_dir),
             "--outfile", str(stock_gguf), "--outtype", "q8_0"],
            check=True,
        )
        print(f"Stock GGUF saved: {stock_gguf} ({stock_gguf.stat().st_size / 1e6:.0f} MB)\n")
        shutil.rmtree(str(stock_dir), ignore_errors=True)
    else:
        print(f"Stock GGUF already exists: {stock_gguf}")

if step in ("nocot", "all"):
    nocot_dir = Path("finetuning/nocot_hf_temp")
    nocot_gguf = Path("finetuning/nocot_arch_router.Q8_0.gguf")

    if not nocot_gguf.exists():
        print("=== Step 3: Merge LoRA and save no-CoT model ===")
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16, device_map="cpu")
        model = PeftModel.from_pretrained(model, LORA_PATH, device_map="cpu")
        model = model.merge_and_unload()
        model.save_pretrained(str(nocot_dir))
        tokenizer.save_pretrained(str(nocot_dir))
        del model, tokenizer
        print("No-CoT merged HF model saved\n")

        print("=== Step 4: Convert no-CoT to GGUF Q8_0 ===")
        subprocess.run(
            ["python3", str(CONVERT_SCRIPT), str(nocot_dir),
             "--outfile", str(nocot_gguf), "--outtype", "q8_0"],
            check=True,
        )
        print(f"No-CoT GGUF saved: {nocot_gguf} ({nocot_gguf.stat().st_size / 1e6:.0f} MB)\n")
        shutil.rmtree(str(nocot_dir), ignore_errors=True)
    else:
        print(f"No-CoT GGUF already exists: {nocot_gguf}")

print("Done!")
