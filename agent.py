import argparse
import sys
from pathlib import Path
from typing import Callable, Optional

from document_reader import read_pdf, DocumentReaderError
from analyzer import DocumentAnalyzer, AnalyzerError
from report_generator import save_analysis_json, generate_markdown_report
from verifier import verify_outputs
from config import OUTPUT_DIR, INPUT_DIR

def run_agent(file_path: Path, objective: str, progress_callback: Optional[Callable[[str], None]] = None) -> dict:
    """
    Main orchestration function for the Document AI Agent.
    
    Args:
        file_path (Path): Path to the uploaded PDF.
        objective (str): User's natural language goal.
        progress_callback (callable): Optional function to report step-by-step progress.
        
    Returns:
        dict: Final execution summary including paths and verification status.
    """
    def notify(msg: str):
        if progress_callback:
            progress_callback(msg)
        else:
            print(f"[*] {msg}")

    try:
        # Step 1 & 2: Validating and Extracting
        notify("Step 1 & 2 — Validating and Extracting document text")
        doc_data = read_pdf(file_path)
        notify(f"Extracted {doc_data['page_count']} pages successfully.")
        
        # Initialize Analyzer
        analyzer = DocumentAnalyzer()
        
        # Step 3 & 4: Objective Understanding & Planning
        notify("Step 3 & 4 — Understanding objective and Planning analysis")
        plan = analyzer.generate_plan(objective, doc_data["filename"], doc_data["page_count"])
        notify(f"Plan created. Focus areas: {', '.join(plan.focus_areas)}")
        
        # Step 5: Document Analysis
        notify("Step 5 — Analyzing document (this may take a moment)")
        analysis_result = analyzer.analyze(doc_data, plan, objective)
        
        # Step 6: Generating Report
        notify("Step 6 — Generating structured JSON and Markdown reports")
        json_path = save_analysis_json(analysis_result)
        md_path = generate_markdown_report(analysis_result, doc_data["filename"], doc_data["page_count"])
        
        # Step 7: Verifying Outputs
        notify("Step 7 — Verifying outputs")
        verification = verify_outputs(json_path, md_path)
        
        if not verification["success"]:
            notify("Warning: Verification step flagged issues with the output.")
        
        return {
            "status": "success",
            "document_name": doc_data["filename"],
            "page_count": doc_data["page_count"],
            "verification": verification,
            "json_path": json_path,
            "md_path": md_path,
            "result_object": analysis_result
        }

    except (DocumentReaderError, AnalyzerError) as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected system error occurred: {str(e)}"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Document AI Agent CLI")
    parser.add_argument("--file", type=str, required=True, help="Path to the real PDF file")
    parser.add_argument("--objective", type=str, required=True, help="What do you want to analyze?")
    
    args = parser.parse_args()
    file_path = Path(args.file)
    
    print("\n=============================================")
    print("🤖 Starting Document AI Agent (CLI Mode)")
    print("=============================================\n")
    
    result = run_agent(file_path, args.objective)
    
    print("\n=============================================")
    if result["status"] == "success":
        print("✅ Execution Successful")
        print(f"Document: {result['document_name']} ({result['page_count']} pages)")
        print("\nVerification Checks:")
        for check in result["verification"]["checks"]:
            status = "✅" if check["passed"] else "❌"
            print(f"  {status} {check['name']}")
        print(f"\nOutputs generated in: {OUTPUT_DIR.resolve()}")
    else:
        print("❌ Execution Failed")
        print(f"Error: {result['message']}")
    print("=============================================\n")