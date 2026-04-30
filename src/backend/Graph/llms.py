"""LLM 实例集中定义。

- 使用 langchain-core 0.3 / langgraph 0.6 兼容的 Chat 模型构造方式。
- DeepSeek 使用 ``langchain_deepseek.ChatDeepSeek``。
- 通义系列继续使用 ``langchain_community.chat_models.tongyi.ChatTongyi``。
- API Key / Base URL 优先从用户配置文件 ``~/Documents/FlowCalendar/llm_config.json`` 读取，
  其次从环境变量读取，最后回退到内置默认值。
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_deepseek import ChatDeepSeek

load_dotenv(override=True)

# 配置文件路径，与前端设置面板共享
LLM_CONFIG_PATH = Path(os.path.expanduser("~")) / "Documents" / "FlowCalendar" / "llm_config.json"

# API Key 必须由用户在「设置」面板或环境变量中提供，不再内置任何默认密钥
_DEFAULT_DEEPSEEK_API_KEY = ""
_DEFAULT_DASHSCOPE_API_KEY = ""
_DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com"
_DEFAULT_DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"


def _load_llm_config() -> dict:
    """读取用户配置文件，返回 deepseek/dashscope 两组配置。

    优先级：配置文件 → 环境变量 → 空字符串（用户未配置时由前端设置面板补全）。
    """
    file_cfg: dict = {}
    try:
        if LLM_CONFIG_PATH.is_file():
            with open(LLM_CONFIG_PATH, "r", encoding="utf-8") as f:
                file_cfg = json.load(f) or {}
    except (OSError, json.JSONDecodeError) as exc:  # noqa: BLE001
        print(f"[llms] 读取配置文件失败，将使用环境变量/默认值：{exc}")
        file_cfg = {}

    deepseek_cfg = file_cfg.get("deepseek") or {}
    dashscope_cfg = file_cfg.get("dashscope") or {}

    deepseek_api_key = (
        (deepseek_cfg.get("api_key") or "").strip()
        or os.getenv("DEEPSEEK_API_KEY", "").strip()
        or _DEFAULT_DEEPSEEK_API_KEY
    )
    deepseek_base_url = (
        (deepseek_cfg.get("base_url") or "").strip()
        or os.getenv("DEEPSEEK_BASE_URL", "").strip()
        or _DEFAULT_DEEPSEEK_BASE_URL
    )
    dashscope_api_key = (
        (dashscope_cfg.get("api_key") or "").strip()
        or os.getenv("DASHSCOPE_API_KEY", "").strip()
        or _DEFAULT_DASHSCOPE_API_KEY
    )
    dashscope_base_url = (
        (dashscope_cfg.get("base_url") or "").strip()
        or os.getenv("DASHSCOPE_BASE_URL", "").strip()
        or _DEFAULT_DASHSCOPE_BASE_URL
    )

    return {
        "deepseek": {"api_key": deepseek_api_key, "base_url": deepseek_base_url},
        "dashscope": {"api_key": dashscope_api_key, "base_url": dashscope_base_url},
    }


_cfg = _load_llm_config()
DEEPSEEK_API_KEY = _cfg["deepseek"]["api_key"]
DEEPSEEK_BASE_URL = _cfg["deepseek"]["base_url"]
DASHSCOPE_API_KEY = _cfg["dashscope"]["api_key"]
DASHSCOPE_BASE_URL = _cfg["dashscope"]["base_url"]

if not DEEPSEEK_API_KEY:
    print("[llms] 警告：DeepSeek API Key 未配置，请在应用「设置」面板或 DEEPSEEK_API_KEY 环境变量中填写。")
if not DASHSCOPE_API_KEY:
    print("[llms] 警告：DashScope API Key 未配置，请在应用「设置」面板或 DASHSCOPE_API_KEY 环境变量中填写。")

# DashScope SDK 通过模块全局变量配置 base url（ChatTongyi 无显式参数）
if DASHSCOPE_BASE_URL:
    try:
        import dashscope as _dashscope

        _dashscope.base_http_api_url = DASHSCOPE_BASE_URL
    except Exception as _exc:  # noqa: BLE001
        print(f"[llms] 设置 dashscope base_url 失败：{_exc}")

# DeepSeek 主模型：复杂推理 / 终答
llm = ChatDeepSeek(
    model="deepseek-v4-flash",
    api_key=DEEPSEEK_API_KEY,
    api_base=DEEPSEEK_BASE_URL,
    tags=[],
)

# 路由专用模型，tags=["router"] 让前端在流式 metadata 中识别"思考需求中..."
router = ChatTongyi(
    model_name="qwen3-coder-flash",
    dashscope_api_key=DASHSCOPE_API_KEY,
    tags=["router"],
)

# 通用快模型
fastllm = ChatTongyi(
    model_name="qwen-flash",
    dashscope_api_key=DASHSCOPE_API_KEY,
    tags=[],
)

# 结构化输出快模型
fast_structured_llm = ChatTongyi(
    model_name="qwen3-coder-flash",
    dashscope_api_key=DASHSCOPE_API_KEY,
    tags=[],
)

# 视觉 OCR 模型
visionllm = ChatTongyi(
    model_name="qwen-vl-ocr",
    dashscope_api_key=DASHSCOPE_API_KEY,
    tags=[],
)
