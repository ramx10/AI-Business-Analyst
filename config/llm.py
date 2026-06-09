from config.llm_manager import get_llm, update_config, LLMConfig


class _LLMProxy:
    def __getattr__(self, name):
        return getattr(get_llm(), name)


llm = _LLMProxy()
