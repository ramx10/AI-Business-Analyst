import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from dashboard.styles import apply_page_styling
from utils.sharing import create_share_link, list_shares, revoke_share

apply_page_styling()

st.title("➔ Share Dashboard")

if "session_id" not in st.session_state:
    st.warning("No active session. Please upload a dataset first.")
    st.stop()

session_id = st.session_state["session_id"]

st.markdown("### Create Share Link")

col1, col2 = st.columns(2)
with col1:
    expiry = st.selectbox("Expiry", ["1 Hour", "6 Hours", "24 Hours", "7 Days", "30 Days"], index=2)
with col2:
    password = st.text_input("Password (optional)", type="password")

expiry_map = {"1 Hour": 1, "6 Hours": 6, "24 Hours": 24, "7 Days": 168, "30 Days": 720}

if st.button("➔ Generate Share Link", use_container_width=True):
    result = create_share_link(session_id, expiry_hours=expiry_map[expiry], password=password or None)
    share_url = f"{st.get_option('server.baseUrlPath') or ''}/share.html?token={result['token']}"
    st.success(f"Share link created!")
    st.code(share_url, language="text")
    st.markdown(f"Expires: **{result['expiry']}**")
    if password:
        st.markdown("⊡ **Password protected**")

st.markdown("---")
st.markdown("### Active Shares")

shares = list_shares(session_id)
if shares:
    for s in shares:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown(f"Token: `{s['token']}`")
            st.caption(f"Expires: {s['expiry']} {'⊡' if s['has_password'] else ''}")
        with col2:
            share_url = f"{st.get_option('server.baseUrlPath') or ''}/share.html?token={s['token']}"
            st.markdown(f"[Open]({share_url})")
        with col3:
            if st.button(f"Revoke", key=f"revoke_{s['token']}"):
                revoke_share(s["token"])
                st.rerun()
else:
    st.info("No active share links.")
