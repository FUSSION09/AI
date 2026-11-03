import os
from pathlib import Path

# Base workspace directory: strictly d:\AI
BASE_DIR = Path(__file__).resolve().parent.parent

# Subdirectories
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"
CONFIGS_DIR = BASE_DIR / "configs"
CACHE_DIR = BASE_DIR / "cache"
SRC_DIR = BASE_DIR / "src"
EVOLUTION_DIR = BASE_DIR / "evolution"

# Enforce Hugging Face and PyTorch caches to remain strictly within d:\AI
os.environ["HF_HOME"] = str(CACHE_DIR / "huggingface")
os.environ["TRANSFORMERS_CACHE"] = str(CACHE_DIR / "huggingface" / "hub")
os.environ["HF_DATASETS_CACHE"] = str(CACHE_DIR / "huggingface" / "datasets")
os.environ["TORCH_HOME"] = str(CACHE_DIR / "torch")

def print_environment_paths():
    print(f"Project Base: {BASE_DIR}")
    print(f"Data Dir:     {DATA_DIR}")
    print(f"Models Dir:   {MODELS_DIR}")
    print(f"Cache Dir:    {CACHE_DIR}")

if __name__ == "__main__":
    print_environment_paths()