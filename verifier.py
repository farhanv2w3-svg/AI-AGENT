import json
from pathlib import Path
from typing import Dict, Any

def verify_outputs(json_path: Path, md_path: Path) -> Dict[str, Any]:
    """
    Verifies that the generated outputs exist, are not empty, and contain valid data.
    """
    results = {
        "success": True,
        "checks": []
    }
    
    def add_check(name: str, passed: bool):
        results["checks"].append({"name": name, "passed": passed})
        if not passed:
            results["success"] = False

    # Check 1: Files exist
    json_exists = json_path.exists()
    md_exists = md_path.exists()
    add_check("analysis.json exists", json_exists)
    add_check("report.md exists", md_exists)
    
    if not json_exists or not md_exists:
        return results

    # Check 2: Files are not empty
    json_size = json_path.stat().st_size
    md_size = md_path.stat().st_size
    add_check("analysis.json is not empty", json_size > 0)
    add_check("report.md is not empty", md_size > 0)
    
    if json_size == 0 or md_size == 0:
        return results

    # Check 3: JSON is valid and conforms roughly to expected schema
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        add_check("JSON is valid", True)
        
        # Check required fields exist
        required_fields = ["document_summary", "objective", "key_findings"]
        has_fields = all(field in data for field in required_fields)
        add_check("JSON contains required fields", has_fields)
        
    except json.JSONDecodeError:
        add_check("JSON is valid", False)
        
    # Check 4: Markdown contains meaningful content (basic check)
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()
        has_content = "## Key Findings" in md_content and len(md_content) > 100
        add_check("report.md has meaningful structure", has_content)

    return results