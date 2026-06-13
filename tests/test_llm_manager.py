import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from config.llm_manager import (
    LLMConfig,
    get_llm,
    update_config,
    get_config,
    get_available_models,
    _read_config,
    _write_config,
    CONFIG_FILE,
)


@pytest.fixture(autouse=True)
def clear_config_cache():
    import config.llm_manager as m
    m._llm_instance = None
    m._llm_config_hash = None
    yield
    m._llm_instance = None
    m._llm_config_hash = None


@pytest.fixture(autouse=True)
def backup_and_restore_config():
    existed = CONFIG_FILE.exists()
    if existed:
        backup = CONFIG_FILE.read_text()
    yield
    if existed:
        CONFIG_FILE.write_text(backup)
    elif CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


@pytest.fixture
def temp_config(tmp_path):
    import config.llm_manager as m
    orig_file = m.CONFIG_FILE
    m.CONFIG_FILE = tmp_path / "llm_config.json"
    yield m.CONFIG_FILE
    m.CONFIG_FILE = orig_file


class TestLLMConfig:
    def test_default_construction(self):
        cfg = LLMConfig()
        assert cfg.provider == "groq"
        assert cfg.model == "llama-3.3-70b-versatile"
        assert cfg.api_key is None

    def test_custom_construction(self):
        cfg = LLMConfig(provider="openai", api_key="sk-test", model="gpt-4o")
        assert cfg.provider == "openai"
        assert cfg.api_key == "sk-test"
        assert cfg.model == "gpt-4o"

    def test_to_dict_excludes_null_key(self):
        cfg = LLMConfig(provider="groq", model="llama-3.3-70b-versatile")
        d = cfg.to_dict()
        assert "api_key" not in d

    def test_to_dict_includes_key_when_set(self):
        cfg = LLMConfig(provider="groq", api_key="gsk-test", model="llama-3.3-70b-versatile")
        d = cfg.to_dict()
        assert d["api_key"] == "gsk-test"

    def test_from_dict_roundtrip(self):
        original = LLMConfig(provider="anthropic", api_key="sk-ant-test", model="claude-3-5-sonnet-20241022")
        data = original.to_dict()
        restored = LLMConfig.from_dict(data)
        assert restored.provider == original.provider
        assert restored.api_key == original.api_key
        assert restored.model == original.model


class TestReadWriteConfig:
    def test_read_without_file_returns_defaults(self, temp_config):
        assert not temp_config.exists()
        cfg = _read_config()
        assert cfg.provider == "groq"

    def test_write_and_read(self, temp_config):
        original = LLMConfig(provider="openai", api_key="sk-123", model="gpt-4o")
        _write_config(original)
        assert temp_config.exists()
        restored = _read_config()
        assert restored.provider == "openai"
        assert restored.api_key == "sk-123"
        assert restored.model == "gpt-4o"

    def test_read_corrupted_file_returns_defaults(self, temp_config):
        temp_config.write_text("not json")
        cfg = _read_config()
        assert cfg.provider == "groq"


class TestGetLLM:
    @patch("config.llm_manager._get_api_key_from_env", return_value="gsk-test")
    @patch("langchain_groq.ChatGroq")
    def test_get_llm_groq_from_env(self, MockChatGroq, mock_env):
        MockChatGroq.return_value = MagicMock()
        llm = get_llm()
        MockChatGroq.assert_called_once()
        kwargs = MockChatGroq.call_args.kwargs
        assert kwargs["model"] == "llama-3.3-70b-versatile"
        assert kwargs["groq_api_key"] == "gsk-test"
        assert kwargs["temperature"] == 0.3

    @patch("config.llm_manager._get_api_key_from_env", return_value="sk-test")
    @patch("langchain_openai.ChatOpenAI")
    def test_get_llm_openai_from_env(self, MockChatOpenAI, mock_env):
        config = LLMConfig(provider="openai", model="gpt-4o")
        _write_config(config)
        llm = get_llm()
        MockChatOpenAI.assert_called_once()
        kwargs = MockChatOpenAI.call_args.kwargs
        assert kwargs["model"] == "gpt-4o"
        assert kwargs["openai_api_key"] == "sk-test"

    @patch("config.llm_manager._get_api_key_from_env", return_value="ant-test")
    @patch("langchain_anthropic.ChatAnthropic")
    def test_get_llm_anthropic_from_env(self, MockChatAnthropic, mock_env):
        config = LLMConfig(provider="anthropic", model="claude-3-5-sonnet-20241022")
        _write_config(config)
        llm = get_llm()
        MockChatAnthropic.assert_called_once()
        kwargs = MockChatAnthropic.call_args.kwargs
        assert kwargs["model"] == "claude-3-5-sonnet-20241022"
        assert kwargs["anthropic_api_key"] == "ant-test"

    @patch("langchain_ollama.ChatOllama")
    def test_get_llm_ollama_no_key(self, MockChatOllama):
        config = LLMConfig(provider="ollama", model="llama3")
        _write_config(config)
        llm = get_llm()
        MockChatOllama.assert_called_once()
        kwargs = MockChatOllama.call_args.kwargs
        assert kwargs["model"] == "llama3"
        assert kwargs["temperature"] == 0.3

    @patch("config.llm_manager._get_api_key_from_env", return_value=None)
    def test_get_llm_groq_missing_key_raises(self, mock_env):
        config = LLMConfig(provider="groq", model="llama-3.3-70b-versatile")
        _write_config(config)
        with pytest.raises(ValueError, match="GROQ_API_KEY is required"):
            get_llm()

    @patch("config.llm_manager._get_api_key_from_env", return_value=None)
    def test_get_llm_openai_missing_key_raises(self, mock_env):
        config = LLMConfig(provider="openai", model="gpt-4o")
        _write_config(config)
        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            get_llm()

    @patch("config.llm_manager._get_api_key_from_env", return_value=None)
    def test_get_llm_anthropic_missing_key_raises(self, mock_env):
        config = LLMConfig(provider="anthropic", model="claude-3-5-sonnet-20241022")
        _write_config(config)
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is required"):
            get_llm()

    def test_get_llm_unsupported_provider_raises(self):
        config = LLMConfig(provider="unknown", model="test")
        _write_config(config)
        with pytest.raises(ValueError, match="Unsupported provider"):
            get_llm()


class TestUpdateConfig:
    @patch("config.llm_manager._get_api_key_from_env", return_value="sk-test")
    def test_update_config_changes_provider(self, mock_env):
        config = update_config(provider="openai", model="gpt-4o")
        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        read_back = _read_config()
        assert read_back.provider == "openai"

    @patch("config.llm_manager._get_api_key_from_env", return_value=None)
    def test_update_config_without_api_key_raises(self, mock_env):
        with pytest.raises(ValueError, match="API_KEY is not set"):
            update_config(provider="groq", model="llama-3.3-70b-versatile")

    @patch("config.llm_manager._get_api_key_from_env", return_value="gsk-test")
    def test_update_config_ollama_without_key_succeeds(self, mock_env):
        config = update_config(provider="ollama", model="llama3")
        assert config.provider == "ollama"
        assert config.model == "llama3"

    @patch("config.llm_manager._get_api_key_from_env", return_value="gsk-test")
    def test_update_config_only_model(self, mock_env):
        update_config(provider="groq", model="llama-3.3-70b-versatile")
        config = update_config(model="mixtral-8x7b-32768")
        assert config.model == "mixtral-8x7b-32768"
        assert config.provider == "groq"


class TestGetConfig:
    def test_get_config_returns_booleans_not_keys(self):
        cfg = get_config()
        assert "provider" in cfg
        assert "model" in cfg
        assert "has_api_key" in cfg
        assert isinstance(cfg["has_api_key"]["groq"], bool)

    @patch("config.llm_manager._get_api_key_from_env", return_value="gsk-test")
    def test_get_config_shows_key_set(self, mock_env):
        cfg = get_config()
        assert cfg["has_api_key"]["groq"] is True
        assert cfg["has_api_key"]["ollama"] is True

    @patch("config.llm_manager._get_api_key_from_env", return_value=None)
    def test_get_config_shows_key_not_set(self, mock_env):
        cfg = get_config()
        assert cfg["has_api_key"]["groq"] is False


class TestGetAvailableModels:
    def test_returns_list_for_valid_provider(self):
        models = get_available_models("groq")
        assert isinstance(models, list)
        assert len(models) > 0
        assert "llama-3.3-70b-versatile" in models

    def test_returns_empty_for_unknown_provider(self):
        models = get_available_models("nonexistent")
        assert models == []

    def test_returns_all_when_no_provider(self):
        all_models = get_available_models()
        assert "groq" in all_models
        assert "openai" in all_models
        assert "anthropic" in all_models
        assert "ollama" in all_models


class TestTestConnection:
    @patch("config.llm_manager._get_api_key_from_env", return_value="gsk-test")
    @patch("langchain_groq.ChatGroq")
    def test_test_connection_success(self, MockChatGroq, mock_env):
        from config.llm_manager import test_connection as tc
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "ok"
        mock_instance.invoke.return_value = mock_response
        MockChatGroq.return_value = mock_instance
        result = tc(provider="groq", model="llama-3.3-70b-versatile")
        assert result["success"] is True

    @patch("config.llm_manager._get_api_key_from_env", return_value="gsk-test")
    @patch("langchain_groq.ChatGroq")
    def test_test_connection_failure(self, MockChatGroq, mock_env):
        from config.llm_manager import test_connection as tc
        mock_instance = MagicMock()
        mock_instance.invoke.side_effect = Exception("API error")
        MockChatGroq.return_value = mock_instance
        result = tc(provider="groq", model="llama-3.3-70b-versatile")
        assert result["success"] is False
        assert "API error" in result["message"]
