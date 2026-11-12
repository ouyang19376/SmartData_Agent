
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


def create_llm() -> ChatOpenAI:
    """
    创建 OpenAI-compatible LLM 实例。

    配置从项目 .env 文件读取。
    不在代码中保存 API Key。
    """

    load_dotenv()

    base_url = os.getenv("LLM_BASE_URL")
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0"))

    missing = []

    if not api_key:
        missing.append("LLM_API_KEY")

    if not model:
        missing.append("LLM_MODEL")

    if missing:
        raise ValueError(
            f"缺少必要的 LLM 配置项：{', '.join(missing)}"
        )

    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url or None,
        temperature=temperature,
    )
