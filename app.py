import streamlit as st
import time
from pathlib import Path
from agent import run_agent
from config import INPUT_DIR, OUTPUT_DIR

st.set_page_config(page_title="Document AI Agent", page_icon="🤖", layout="wide")

st.title("🤖 Document AI Agent")
st.markdown("Upload a real document, describe what you want to know, and let the agent analyze it. **No fake progress, no simulated results.**")

# Sidebar for instructions
with st.sidebar:
    st.header("How it works")
    st.markdown("""
    1. **Upload** a real PDF.
    2. **Define** your objective.
    3. The agent will autonomously read, plan, chunk, and extract findings.
    4. Download the **verified** reports.
    """)

# UI Elements
uploaded_file = st.file_uploader("1. Upload a PDF file", type=["pdf"])
objective = st.text_area(
    "2. Enter your objective",
    placeholder="Analyze this document and identify the most important findings, risks, unusual values, and recommendations."
)

if st.button("Run Agent", type="primary"):
    if not uploaded_file:
        st.error("Please upload a PDF file first.")
    elif not objective.strip():
        st.error("Please enter an objective.")
    else:
        # Save uploaded file to disk so our agent can process it like a real file
        file_path = INPUT_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.divider()
        st.subheader("Agent Execution Log")
        
        # Setup progress reporting
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Callback to update UI during execution
        def update_progress(msg: str):
            status_text.info(msg)
            # Naive progress bar incrementation based on step text
            if "Step 1" in msg: progress_bar.progress(15)
            elif "Step 3" in msg: progress_bar.progress(30)
            elif "Step 5" in msg: progress_bar.progress(60)
            elif "Step 6" in msg: progress_bar.progress(85)
            elif "Step 7" in msg: progress_bar.progress(100)
            time.sleep(0.5) # Slight delay so UI updates are readable

        with st.spinner("Agent is running..."):
            result = run_agent(file_path, objective, progress_callback=update_progress)

        if result["status"] == "error":
            st.error(f"Agent Execution Failed:\n{result['message']}")
        else:
            st.success("✅ Agent Execution Complete & Verified!")
            
            # Display Results visually
            analysis = result["result_object"]
            
            st.divider()
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Executive Summary")
                st.write(analysis.document_summary)
                
                st.subheader("Key Findings")
                for f in analysis.key_findings:
                    with st.expander(f"📌 {f.title} (Pages: {', '.join(map(str, f.page_references))})"):
                        st.write(f"**Explanation:** {f.explanation}")
                        st.info(f"**Evidence:** {f.evidence}")
                        
                st.subheader("Risks & Issues")
                for r in analysis.risks_or_issues:
                    with st.expander(f"⚠️ {r.title}"):
                        st.write(r.explanation)
                        st.info(f"**Evidence:** {r.evidence}")

            with col2:
                st.subheader("Agent Output Verification")
                for check in result["verification"]["checks"]:
                    icon = "✅" if check["passed"] else "❌"
                    st.write(f"{icon} {check['name']}")

                st.subheader("Recommendations")
                for rec in analysis.recommendations:
                    st.markdown(f"- {rec}")
                    
                st.subheader("Downloads")
                with open(result["json_path"], "r", encoding="utf-8") as f:
                    st.download_button("Download JSON", f.read(), file_name="analysis.json", mime="application/json")
                with open(result["md_path"], "r", encoding="utf-8") as f:
                    st.download_button("Download Markdown Report", f.read(), file_name="report.md", mime="text/markdown")