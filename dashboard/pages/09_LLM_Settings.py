import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from dashboard.styles import apply_page_styling
from config.llm_manager import get_config, update_config, get_available_models, test_connection

apply_page_styling()

st.title("LLM Settings")
st.markdown("Configure which AI provider powers the analysis agents.")

config = get_config()

providers = ["groq", "openai", "anthropic", "ollama"]
provider_labels = {
    "groq": "Groq",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "ollama": "Ollama (local)",
}

col1, col2 = st.columns(2)

with col1:
    provider = st.selectbox(
        "Provider",
        options=providers,
        format_func=lambda p: provider_labels[p],
        index=providers.index(config["provider"]) if config["provider"] in providers else 0,
    )

    models = get_available_models(provider)
    model = st.selectbox(
        "Model",
        options=models,
        index=models.index(config["model"]) if config["model"] in models else 0,
    )

with col2:
    needs_key = provider != "ollama"
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder=f"Enter {provider.upper()} API key" if needs_key else "No API key needed",
        disabled=not needs_key,
        help=f"Set via environment variable or enter here" if needs_key else "Ollama runs locally — no key needed",
    )

    has_key = config["has_api_key"].get(provider, False)
    if needs_key:
        if has_key:
            st.success("API key is configured")
        else:
            st.warning("No API key set for this provider")

if st.button("Test Connection", type="secondary"):
    with st.spinner("Testing..."):
        result = test_connection(provider=provider, api_key=api_key or None, model=model)
        if result["success"]:
            st.success(f"Connection successful: {result['message']}")
        else:
            st.error(f"Connection failed: {result['message']}")

if st.button("Save Settings", type="primary"):
    try:
        update_config(provider=provider, api_key=api_key or None, model=model)
        st.success("Settings saved successfully!")
        st.rerun()
    except ValueError as e:
        st.error(str(e))

with st.expander("Current Configuration"):
    st.json(config)
