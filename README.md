# Document AI Agent

A complete, working Document AI Agent that performs real document processing, LLM-based analysis planning, content extraction, and report verification without using abstract orchestration frameworks like LangChain or CrewAI.

## What This Project Does
It accepts a real PDF file and a natural language instruction. Instead of blindly pasting text into an LLM, the system operates as a true Agent:
1. **Observe:** Extracts and formats actual PDF text and page numbers.
2. **Plan:** Asks the LLM to formulate an Analysis Plan based on the document's metadata and the user's objective.
3. **Act:** Analyzes the document (chunking it by size if necessary) explicitly following the generated plan.
4. **Verify:** Generates structured Pydantic outputs and verifies the files/data integrity before displaying success.

## Architecture & Folders
```text
document-ai-agent/
├── app.py                     # Streamlit frontend
├── agent.py                   # Orchestration workflow & CLI
├── document_reader.py         # PyMuPDF extraction engine
├── analyzer.py                # Gemini LLM integration & Pydantic structures
├── report_generator.py        # Report serializers (.json / .md)
├── verifier.py                # Post-execution sanity checks
├── models.py                  # Pydantic schemas enforcing output rules
├── input/                     # Place your test PDFs here
└── output/                    # Generated reports appear here