import unittest
import json
from pathlib import Path
from verifier import verify_outputs

class TestVerifier(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.json_path = self.test_dir / "test_out.json"
        self.md_path = self.test_dir / "test_out.md"
        
    def tearDown(self):
        if self.json_path.exists(): self.json_path.unlink()
        if self.md_path.exists(): self.md_path.unlink()

    def test_missing_files(self):
        result = verify_outputs(self.json_path, self.md_path)
        self.assertFalse(result["success"])

    def test_valid_files(self):
        with open(self.json_path, "w") as f:
            json.dump({"document_summary": "Sum", "objective": "Obj", "key_findings": []}, f)
        
        with open(self.md_path, "w") as f:
            f.write("# Document Analysis Report\n\n## Key Findings\nContent goes here.")
            
        result = verify_outputs(self.json_path, self.md_path)
        self.assertTrue(result["success"])

if __name__ == "__main__":
    unittest.main()