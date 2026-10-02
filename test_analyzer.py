import unittest
from models import AnalysisPlan, AnalysisResult, Finding

class TestModels(unittest.TestCase):
    def test_analysis_plan_validation(self):
        data = {
            "objective_understanding": "User wants risks.",
            "focus_areas": ["Risks", "Finances"],
            "search_strategy": "Scan for keywords."
        }
        plan = AnalysisPlan(**data)
        self.assertEqual(len(plan.focus_areas), 2)
        
    def test_finding_requires_evidence(self):
        with self.assertRaises(ValueError):
            # Missing evidence field
            Finding(title="Test", explanation="Test exp")

if __name__ == "__main__":
    unittest.main()