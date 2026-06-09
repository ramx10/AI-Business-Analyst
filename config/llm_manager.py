import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_DIR = Path("data/config")
CONFIG_FILE = CONFIG_DIR / "llm_config.json"

DEFAULT_PROVIDER = "groq"
DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20241022",
    "ollama": "llama3",
}

PROVIDERS_REQUIRING_KEY = {"groq", "openai", "anthropic"}

_llm_instance = None
_llm_config_hash = None


class LLMConfig:
    def __init__(self, provider=None, api_key=None, model=None):
        self.provider = provider or DEFAULT_PROVIDER
        self.api_key = api_key
        self.model = model or DEFAULT_MODELS.get(self.provider, DEFAULT_MODELS[DEFAULT_PROVIDER])

    def to_dict(self):
        d = {"provider": self.provider, "model": self.model}
        if self.api_key:
            d["api_key"] = self.api_key
        return d

    @classmethod
    def from_dict(cls, data):
        return cls(
            provider=data.get("provider"),
            api_key=data.get("api_key"),
            model=data.get("model"),
        )


def _ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _read_config():
    if not CONFIG_FILE.exists():
        return LLMConfig()
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
        return LLMConfig.from_dict(data)
    except (json.JSONDecodeError, IOError):
        return LLMConfig()


def _write_config(config):
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config.to_dict(), f, indent=2)


def _get_api_key_from_env(provider):
    env_var_map = {
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    env_var = env_var_map.get(provider)
    if env_var:
        return os.getenv(env_var)
    return None


def _resolve_config(provider=None, api_key=None, model=None):
    existing = _read_config()
    resolved = LLMConfig(
        provider=provider if provider is not None else existing.provider,
        api_key=api_key if api_key is not None else existing.api_key,
        model=model if model is not None else existing.model,
    )
    if not resolved.api_key:
        resolved.api_key = _get_api_key_from_env(resolved.provider)
    if not resolved.model:
        resolved.model = DEFAULT_MODELS.get(resolved.provider, DEFAULT_MODELS[DEFAULT_PROVIDER])
    return resolved


def _create_llm(config):
    provider = config.provider
    api_key = config.api_key
    model = config.model

    if provider == "groq":
        if not api_key:
            raise ValueError("GROQ_API_KEY is required for Groq provider")
        from langchain_groq import ChatGroq
        return ChatGroq(model=model, groq_api_key=api_key, temperature=0.3)

    if provider == "openai":
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=model, openai_api_key=api_key, temperature=0.3)

    if provider == "anthropic":
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model=model, anthropic_api_key=api_key, temperature=0.3)

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=model, temperature=0.3)

    raise ValueError(f"Unsupported provider: {provider}")


def get_llm():
    global _llm_instance, _llm_config_hash
    config = _resolve_config()
    h = hash((config.provider, config.api_key, config.model))
    if _llm_instance is None or h != _llm_config_hash:
        _llm_instance = _create_llm(config)
        _llm_config_hash = h
    return _llm_instance


def update_config(provider=None, api_key=None, model=None):
    existing = _read_config()
    new_provider = provider if provider is not None else existing.provider
    new_api_key = api_key if api_key is not None else existing.api_key
    new_model = model if model is not None else existing.model

    if new_provider in PROVIDERS_REQUIRING_KEY:
        effective_key = new_api_key or _get_api_key_from_env(new_provider)
        if not effective_key:
            raise ValueError(f"{new_provider.upper()}_API_KEY is not set")

    new_config = LLMConfig(provider=new_provider, api_key=new_api_key, model=new_model)
    _write_config(new_config)

    global _llm_instance, _llm_config_hash
    _llm_instance = None
    _llm_config_hash = None

    return new_config


def get_config():
    config = _read_config()
    return {
        "provider": config.provider,
        "model": config.model or DEFAULT_MODELS.get(config.provider, DEFAULT_MODELS[DEFAULT_PROVIDER]),
        "has_api_key": {
            "groq": bool(config.api_key or _get_api_key_from_env("groq")),
            "openai": bool(config.api_key or _get_api_key_from_env("openai")),
            "anthropic": bool(config.api_key or _get_api_key_from_env("anthropic")),
            "ollama": True,
        },
    }


def get_available_models(provider=None):
    models = {
        "groq": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        "openai": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        "anthropic": [
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-haiku-20240307",
        ],
        "ollama": [
            "llama3",
            "llama3.1",
            "mistral",
            "codellama",
        ],
    }
    if provider:
        return models.get(provider, [])
    return models


def test_connection(provider=None, api_key=None, model=None):
    config = _resolve_config(provider=provider, api_key=api_key, model=model)
    try:
        llm = _create_llm(config)
        response = llm.invoke("Reply with only the word 'ok'.")
        return {"success": True, "message": response.content}
    except Exception as e:
        return {"success": False, "message": str(e)}
