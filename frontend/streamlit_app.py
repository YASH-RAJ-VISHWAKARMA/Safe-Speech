# frontend/streamlit_app.py
import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="SCSC - Gemini 2.5 Demo", layout="wide")

st.markdown("<h1 style='text-align:left'>SCSC — Socio-Cultural Sensitivity Checker</h1>", unsafe_allow_html=True)
st.write("Paste text below and click Evaluate. Backend uses Gemini 2.5 Flash for classification & rewrites.")

section = st.sidebar.selectbox("Section", ["Evaluate Text", "Batch Upload", "Logs", "About"])

if section == "Evaluate Text":
    txt = st.text_area("Enter text to evaluate", height=220)
    col1, col2 = st.columns([1,2])
    with col1:
        if st.button("Evaluate"):
            if not txt.strip():
                st.error("Enter text first.")
            else:
                with st.spinner("Calling backend..."):
                    try:
                        resp = requests.post(f"{API_URL}/evaluate", json={"text": txt}, timeout=60)
                        data = resp.json()
                    except Exception as e:
                        st.error(f"Failed to call backend: {e}")
                        data = None
                if data:
                    st.metric("Risk score", f"{data.get('risk', 0)}/100")
                    st.write("**Explanation:**", data.get("explanation", ""))
    with col2:
        if 'data' in locals() and data:
            st.subheader("Categories")
            for c in data.get("categories", []):
                st.write(f"- {c['category']} : {c['score']:.2f}")
            st.subheader("Suggested rewrites")
            for i, r in enumerate(data.get("rewrites", [])):
                st.code(r)
                if st.button(f"Copy rewrite {i+1}"):
                    st.write("Copied to clipboard (manually)")

elif section == "Batch Upload":
    st.write("Upload a text file (.txt) with one example per line.")
    uploaded = st.file_uploader("Upload .txt", type=["txt"])
    if uploaded:
        content = uploaded.getvalue().decode("utf-8").splitlines()
        st.info(f"Loaded {len(content)} lines.")
        if st.button("Run Batch"):
            results = []
            for line in content[:100]:  # limit to first 100
                try:
                    r = requests.post(f"{API_URL}/evaluate", json={"text": line}, timeout=30).json()
                    results.append({"text": line[:80], "risk": r.get("risk", 0)})
                except Exception as e:
                    results.append({"text": line[:80], "risk": "ERROR"})
            st.table(results)

elif section == "Logs":
    st.write("Recent logs from backend DB (read-only)")
    try:
        import sqlite3
        conn = sqlite3.connect("sensitive_checks.db")
        rows = conn.execute("SELECT id, substr(text,1,120), risk, categories, created_at FROM check_logs ORDER BY created_at DESC LIMIT 50").fetchall()
        st.table(rows)
        conn.close()
    except Exception as e:
        st.error(f"Cannot read DB: {e}")

else:
    st.write("About")
    st.write("- Backend: FastAPI + Gemini 2.5 Flash")
    st.write("- Frontend: Streamlit")
    st.write("Make sure you set your GOOGLE_API_KEY in backend/.env and start backend before frontend.")
