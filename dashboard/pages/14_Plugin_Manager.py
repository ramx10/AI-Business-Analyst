import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import pandas as pd
from dashboard.styles import apply_page_styling
from utils.plugin_manager import get_plugin_manager, PLUGIN_DIR

apply_page_styling()

st.title("◈ Plugin Manager")

st.markdown("""
<div style="font-size: 16px; color: #94a3b8; margin-bottom: 25px;">
Extend functionality with community and custom plugins.
</div>
""", unsafe_allow_html=True)

if "session_id" not in st.session_state:
    st.warning("No active session. Please upload a dataset first.")
    st.stop()

session_id = st.session_state["session_id"]

pm = get_plugin_manager()

tab1, tab2, tab3 = st.tabs(["⧉ Installed Plugins", "▶ Run Plugin", "↓ Install Plugin"])

with tab1:
    plugins = pm.get_plugins()
    if plugins:
        for p in plugins:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"**{p['name']}** v{p['version']}")
                st.caption(p.get("description", "") or "No description")
            with col2:
                st.markdown(f"`{p['category']}`")
            with col3:
                if st.button("Uninstall", key=f"uninst_{p['name']}"):
                    plugin_dir = PLUGIN_DIR
                    import importlib, inspect
                    from utils.plugin_base import BasePlugin
                    for fname in os.listdir(plugin_dir):
                        if not fname.endswith(".py") or fname.startswith("_"):
                            continue
                        mod_name = fname[:-3]
                        try:
                            mod = importlib.import_module(mod_name)
                            for _, obj in inspect.getmembers(mod):
                                if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj is not BasePlugin:
                                    instance = obj()
                                    if instance.name == p["name"]:
                                        os.remove(os.path.join(plugin_dir, fname))
                                        st.success(f"Plugin '{p['name']}' uninstalled!")
                                        st.rerun()
                        except Exception:
                            continue
    else:
        st.info("No plugins installed.")

with tab2:
    plugins = pm.get_plugins()
    if not plugins:
        st.info("No plugins available. Install one first.")
    else:
        plugin_names = [p["name"] for p in plugins]
        selected = st.selectbox("Select Plugin", plugin_names)
        plugin = pm.get_plugin(selected)
        with st.form("run-plugin-form"):
            params_str = st.text_area("Parameters (JSON)", value='{"column": ""}', height=100)
            submitted = st.form_submit_button("Run Plugin", type="primary", use_container_width=True)
        if submitted:
            try:
                params = eval(params_str) if params_str.strip() else {}
                if not isinstance(params, dict):
                    st.error("Parameters must be a valid JSON object.")
                    st.stop()
            except Exception:
                st.error("Invalid JSON parameters.")
                st.stop()
            df = st.session_state.get("df")
            if df is None:
                st.warning("No dataset loaded in session.")
                st.stop()
            with st.spinner("Running plugin…"):
                result = pm.run_plugin(selected, df, **params)
            if result.get("success"):
                st.success(result.get("summary", "Plugin ran successfully."))
                if isinstance(result.get("result"), pd.DataFrame):
                    st.dataframe(result["result"])
                st.json(result)
            else:
                st.error(result.get("error", "Plugin execution failed."))

with tab3:
    uploaded_file = st.file_uploader("Upload a .py plugin file", type="py")
    if uploaded_file is not None:
        dest_path = os.path.join(PLUGIN_DIR, uploaded_file.name)
        with open(dest_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        pm.reload()
        st.success(f"Plugin '{uploaded_file.name}' installed!")
        st.rerun()
