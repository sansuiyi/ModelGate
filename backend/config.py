import os
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

# ------------------------------------------------------------
# DeepSeek 直连（合同解析 + 测试台共用；正式代理仍走 OPENROUTER）
# ------------------------------------------------------------
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
# 所有 DeepSeek 调用是否关闭思考模式（默认关闭）
DEEPSEEK_DISABLE_THINKING = os.getenv("DEEPSEEK_DISABLE_THINKING", "true").lower() in (
    "1",
    "true",
    "yes",
    "on",
)

# 合同解析（单次抽取）使用的模型
EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "deepseek-flash")
# ReAct 合同抽取 Agent 用的模型，可配置为更便宜快速的模型以降低多步调用成本
REACT_MODEL = os.getenv("REACT_MODEL", EXTRACTION_MODEL)

# 测试台按复杂度实际调用的模型
PLAYGROUND_MODEL_SIMPLE = os.getenv("PLAYGROUND_MODEL_SIMPLE", "deepseek-flash")
PLAYGROUND_MODEL_MEDIUM = os.getenv("PLAYGROUND_MODEL_MEDIUM", "deepseek-flash")
PLAYGROUND_MODEL_COMPLEX = os.getenv("PLAYGROUND_MODEL_COMPLEX", "deepseek-v4-pro")

# 合同抽取成本估算用的每百万 token 单价（美元）；为 0 时不估算成本
DEEPSEEK_INPUT_PRICE_PER_M = float(os.getenv("DEEPSEEK_INPUT_PRICE_PER_M", "0") or 0)
DEEPSEEK_OUTPUT_PRICE_PER_M = float(os.getenv("DEEPSEEK_OUTPUT_PRICE_PER_M", "0") or 0)

# ------------------------------------------------------------
# Agent harness 预算（阈值按实测留 3-5 倍余量）
# ------------------------------------------------------------
# 合同文本长度闸门：超过则直接拒绝，避免首次调用就撑爆上下文
MAX_CONTRACT_CHARS = int(os.getenv("MAX_CONTRACT_CHARS", "200000"))
# 轮次预算：达到后不再调查，强制 finalize
AGENT_MAX_ITERS = int(os.getenv("AGENT_MAX_ITERS", "14"))
# 累计 token 硬预算：达到后强制 finalize
AGENT_MAX_TOKENS = int(os.getenv("AGENT_MAX_TOKENS", "80000"))
# 软预算比例：达到该比例时提示模型收敛
AGENT_SOFT_TOKEN_RATIO = float(os.getenv("AGENT_SOFT_TOKEN_RATIO", "0.7"))
# 整轮 wall-clock 预算（秒）
AGENT_MAX_SECONDS = float(os.getenv("AGENT_MAX_SECONDS", "90"))
# 单次回复的 max_tokens，防止输出失控
AGENT_MAX_OUTPUT_TOKENS = int(os.getenv("AGENT_MAX_OUTPUT_TOKENS", "2000"))
# 单轮最多执行的工具调用数，超出部分回灌错误让模型重发
AGENT_MAX_TOOL_CALLS_PER_ROUND = int(
    os.getenv("AGENT_MAX_TOOL_CALLS_PER_ROUND", "8")
)

CLASSIFIER_GGUF_PATH = os.getenv(
    "CLASSIFIER_GGUF_PATH",
    str(PROJECT_ROOT / "finetuning" / "nocot_arch_router.Q8_0.gguf"),
)
CLASSIFIER_N_CTX = int(os.getenv("CLASSIFIER_N_CTX", "512"))
CLASSIFIER_N_GPU_LAYERS = int(os.getenv("CLASSIFIER_N_GPU_LAYERS", "-1"))

# Ollama 分类器配置（方案 B：通过 Ollama 调用本地 modelgate 模型）
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CLASSIFIER_MODEL = os.getenv("OLLAMA_CLASSIFIER_MODEL", "modelgate:latest")

DB_PATH = Path(__file__).parent / "data" / "controlplane.db"
CONTRACTS_DIR = Path(__file__).parent / "data" / "contracts"
SAMPLE_CONTRACTS_DIR = Path(__file__).parent / "data" / "sample_contracts"
FALLBACK_PROFILES_DIR = Path(__file__).parent / "data" / "fallback_profiles"

if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY not set. Proxy calls will fail.")
if not DEEPSEEK_API_KEY:
    print("WARNING: DEEPSEEK_API_KEY not set. Contract extraction and playground calls will fail.")
