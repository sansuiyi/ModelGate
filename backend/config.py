import os
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
EXTRACTION_MODEL = "openai/gpt-5.4"
CLASSIFIER_GGUF_PATH = os.getenv(
    "CLASSIFIER_GGUF_PATH",
    str(PROJECT_ROOT / "finetuning" / "nocot_arch_router.Q8_0.gguf"),
)
CLASSIFIER_N_CTX = int(os.getenv("CLASSIFIER_N_CTX", "512"))
CLASSIFIER_N_GPU_LAYERS = int(os.getenv("CLASSIFIER_N_GPU_LAYERS", "-1"))

DB_PATH = Path(__file__).parent / "data" / "controlplane.db"
CONTRACTS_DIR = Path(__file__).parent / "data" / "contracts"
SAMPLE_CONTRACTS_DIR = Path(__file__).parent / "data" / "sample_contracts"
FALLBACK_PROFILES_DIR = Path(__file__).parent / "data" / "fallback_profiles"

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set. LLM calls will fail.")
