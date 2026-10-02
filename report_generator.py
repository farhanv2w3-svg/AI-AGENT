import json
from pathlib import Path
from models import AnalysisResult
from config import OUTPUT_DIR

def save_analysis_json(result: AnalysisResult) -> Path:
    """Saves the raw structured Pydantic model to a JSON file."""
    output_path = OUTPUT_DIR / "analysis.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, indent=4)
    return output_path

def generate_markdown_report(result: AnalysisResult, filename: str, page_count: int) -> Path:
    """Generates a human-readable Markdown report from the structured analysis."""
    output_path = OUTPUT_DIR / "report.md"
    
    md = [
        "# Document Analysis Report\n",
        "## Document Information",
        f"- **Filename:** {filename}",
        f"- **Pages:** {page_count}\n",
        "## User Objective",
        f"> {result.objective}\n",
        "## Executive Summary",
        f"{result.document_summary}\n",
        "## Key Findings\n"
    ]
    
    if not result.key_findings:
        md.append("*No key findings identified.*\n")
    else:
        for f in result.key_findings:
            pages = ", ".join(map(str, f.page_references)) if f.page_references else "N/A"
            md.append(f"### {f.title}")
            md.append(f"**Explanation:** {f.explanation}")
            md.append(f"**Evidence:** \"{f.evidence}\"")
            md.append(f"**Pages referenced:** {pages}\n")

    md.append("## Risks / Issues\n")
    if not result.risks_or_issues:
        md.append("*No specific risks or issues identified.*\n")
    else:
        for r in result.risks_or_issues:
            pages = ", ".join(map(str, r.page_references)) if r.page_references else "N/A"
            md.append(f"### {r.title}")
            md.append(f"**Explanation:** {r.explanation}")
            md.append(f"**Evidence:** \"{r.evidence}\"")
            md.append(f"**Pages referenced:** {pages}\n")

    md.append("## Trends")
    if not result.trends:
        md.append("*No trends identified.*\n")
    else:
        for t in result.trends:
            md.append(f"- {t}")
        md.append("\n")

    md.append("## Recommendations (AI Generated)")
    if not result.recommendations:
        md.append("*No recommendations provided.*\n")
    else:
        for r in result.recommendations:
            md.append(f"- {r}")
        md.append("\n")

    md.append("## Limitations & Confidence")
    for lim in result.limitations:
        md.append(f"- {lim}")
    md.append(f"\n**Confidence Note:** {result.confidence_notes}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    return output_path