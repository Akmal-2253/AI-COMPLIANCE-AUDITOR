#app.py
import streamlit as st
import tempfile
import os
import re
from report_gen import create_pdf_report  
from loader import load_document_with_fitz
from embedder import embed_documents, clear_vectorstore 
from auditor import run_audit

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

st.set_page_config(page_title="Global AI Compliance Auditor", layout="wide", page_icon="🛡️")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ GROQ API Key not found. Set it in Hugging Face Secrets.")
    st.stop()


st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .main-title {
        font-size: 3.5rem !important; font-weight: 800;
        background: linear-gradient(to right, #ffffff, #94a3b8); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin-bottom: 0.2rem;
    }
    .sub-title { font-size: 1.2rem; color: #94a3b8 !important; text-align: center; margin-bottom: 3rem; }
    div.stButton > button {
        background-color: #1e293b !important; color: #f1f5f9 !important;
        border: 1px solid #334155 !important; padding: 12px 24px !important;
        border-radius: 10px !important; font-weight: 600 !important;
        transition: all 0.3s ease; width: 100%;
    }
    div.stButton > button:hover {
        border: 1px solid #cbd5e1 !important; color: #ffffff !important;
        background-color: #334155 !important;
        box-shadow: 0px 0px 15px rgba(255, 255, 255, 0.1);
    }
    [data-testid="stFileUploader"] {
        background-color: #1e293b; border: 1px dashed #334155;
        border-radius: 15px; padding: 20px;
    }
    [data-testid="stMetric"] {
        background-color: #1e293b; border: 1px solid #334155;
        padding: 20px; border-radius: 15px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    [data-testid="stMetricValue"] { color: #f8fafc !important; }
    .stAlert {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important; color: #e2e8f0 !important;
    }
    </style>
""", unsafe_allow_html=True)


def extract_score(text):
    match = re.search(r"RISK SCORE:\s*(\d+)", text, re.IGNORECASE)
    if match:
        return min(int(match.group(1)), 100)
    return 0


st.markdown('<h1 class="main-title">⚡ Global AI Compliance Auditor</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Expert-level legal analysis powered by advanced AI agents</p>', unsafe_allow_html=True)

if 'audit_mode' not in st.session_state:
    st.session_state.audit_mode = "single"

col1, col2, col3 = st.columns([1, 1, 1.2])
with col1:
    if st.button("📄 Single Document Audit", use_container_width=True):
        st.session_state.audit_mode = "single"
with col2:
    if st.button("🔀 Compare Two Documents", use_container_width=True):
        st.session_state.audit_mode = "compare"
with col3:
    st.markdown(f"""
        <div style="background: rgba(251,191,36,0.1); padding: 12px; border-radius: 10px; 
                    border: 1px solid #fbbf24; text-align: center;">
            <span style="color: #fbbf24; font-weight: bold; font-size: 0.9rem;">🤖 AI AUDITOR STATUS</span><br>
            <span style="color: white; font-size: 0.85rem;">Mode: 
                <b style="color: #fbbf24;">{st.session_state.audit_mode.upper()}</b> | Ready for Scan
            </span>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# ── SINGLE AUDIT MODE ──────────────────────────────────
if st.session_state.audit_mode == "single":
    st.subheader("🔍 Single Policy Analysis")
    uploaded_file = st.file_uploader("Upload Policy (PDF)", type="pdf")

    if uploaded_file:
        st.info(f"📄 '{uploaded_file.name}' ready for audit.")
        if st.button("🚀 Run AI Audit"):
            with st.spinner("Analyzing legal frameworks..."):
                clear_vectorstore()
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    chunks = load_document_with_fitz(tmp_path)
                    embed_documents(chunks, collection_name="compliance_docs")
                    result = run_audit("Audit this document for legal gaps, missing clauses, and risks.")

                    st.success("✅ Audit Complete!")

                    score = extract_score(result)
                    gap = 100 - score if score > 0 else 85

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Legal Gap", f"{gap}%", delta="High Risk" if gap > 50 else "Safe", delta_color="inverse")
                    m2.metric("Safety Score", f"{score}/100")
                    m3.metric("Status", "Critical" if score < 40 else "Needs Work" if score < 70 else "Compliant")

                    if score < 40:
                        st.error("🚨 Critical Non-Compliance Detected.")
                    elif score < 70:
                        st.warning("⚠️ Gaps Identified. Review needed.")
                    else:
                        st.success("✅ Document is largely compliant.")

                    st.write("---")
                    res_col1, res_col2 = st.columns([2, 1])
                    with res_col1:
                        st.markdown("### 📋 Audit Report")
                        st.text_area("", result, height=500)
                    with res_col2:
                        st.markdown("### 📥 Export")
                        pdf_file = create_pdf_report(result)
                        with open(pdf_file, "rb") as f:
                            st.download_button("⬇️ Download PDF Report", f, file_name="Audit_Report.pdf", use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.unlink(tmp_path)

# ── COMPARE MODE ────────────────────────────────────────
elif st.session_state.audit_mode == "compare":
    st.subheader("Comparative Compliance Analysis")

    file_col1, file_col2 = st.columns(2)
    with file_col1:
        st.markdown("**📜 Reference Law (Doc A)**")
        doc1 = st.file_uploader("e.g. GDPR / PECA", type="pdf", key="doc_a")
    with file_col2:
        st.markdown("**📄 Target Policy (Doc B)**")
        doc2 = st.file_uploader("Document to be audited", type="pdf", key="doc_b")

    if doc1 and doc2:
        st.success("✅ Both documents uploaded!")
        if st.button("🚀 Start Comparative Analysis", use_container_width=True):
            with st.spinner("⚖️ Comparing documents and calculating legal gaps..."):
                clear_vectorstore()
                path_a, path_b = None, None  # define before try

                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t1, \
                         tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t2:
                        t1.write(doc1.read()); path_a = t1.name
                        t2.write(doc2.read()); path_b = t2.name

                    from comparator import load_and_embed_two_docs, compare_policies
                    load_and_embed_two_docs(path_a, path_b)

                    result, risk = compare_policies(
                        "Compare these two documents. Find all conflicts, legal gaps, and compliance issues."
                    )

                    st.success("✅ Comparison Complete!")
                    st.markdown("### 📊 Compliance Insights")

                    current_score = risk["score"]
                    gap = 100 - current_score if current_score > 0 else 85

                    m_col1, m_col2, m_col3 = st.columns(3)
                    m_col1.metric("Legal Gap", f"{gap}%", delta="High Risk" if gap > 50 else "Safe", delta_color="inverse")
                    m_col2.metric("Safety Score", f"{current_score}/100")
                    m_col3.metric("Status", "Critical" if current_score < 40 else "Needs Work" if current_score < 70 else "Compliant")

                    badge_color = {"LOW": "#22c55e", "MEDIUM": "#f59e0b", "HIGH": "#ef4444"}
                    color = badge_color.get(risk["level"], "#f59e0b")
                    st.markdown(f"""
                        <div style="background:{color}22; border:1px solid {color}; 
                                    padding:12px; border-radius:10px; text-align:center; margin:10px 0;">
                            <span style="color:{color}; font-size:1.2rem; font-weight:bold;">
                                {risk['badge']} Risk Level: {risk['level']} 
                                &nbsp;|&nbsp; Score: {current_score}/100 
                                &nbsp;|&nbsp; [{risk['bar']}]
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

                    if current_score < 40:
                        st.error("🚨 Critical Non-Compliance Detected. Follow recommendations below.")
                    elif current_score < 70:
                        st.warning("⚠️ Gaps Identified. Review needed.")
                    else:
                        st.success("✅ Documents are largely compliant.")

                    st.write("---")
                    det_col1, det_col2 = st.columns([3, 1])
                    with det_col1:
                        st.markdown("#### 📋 Detailed AI Analysis")
                        st.text_area("", result, height=500)
                    with det_col2:
                        st.markdown("#### 📄 Actions")
                        pdf_file = create_pdf_report(result)
                        with open(pdf_file, "rb") as f:
                            st.download_button("⬇️ Download Full PDF", f, file_name="Comparison_Report.pdf", use_container_width=True)

                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    if path_a and os.path.exists(path_a): os.unlink(path_a)
                    if path_b and os.path.exists(path_b): os.unlink(path_b)
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
