import unittest
from pathlib import Path
from document_reader import read_pdf, DocumentReaderError

class TestDocumentReader(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(__file__).parent
        self.dummy_pdf = self.test_dir / "dummy.pdf"
        self.not_a_pdf = self.test_dir / "dummy.txt"
        
        # Create a fake text file
        with open(self.not_a_pdf, "w") as f:
            f.write("This is not a PDF")

    def tearDown(self):
        if self.not_a_pdf.exists():
            self.not_a_pdf.unlink()

    def test_missing_file(self):
        missing_file = self.test_dir / "does_not_exist.pdf"
        with self.assertRaises(DocumentReaderError) as context:
            read_pdf(missing_file)
        self.assertIn("File not found", str(context.exception))

    def test_invalid_extension(self):
        with self.assertRaises(DocumentReaderError) as context:
            read_pdf(self.not_a_pdf)
        self.assertIn("File is not a PDF", str(context.exception))

    def test_corrupted_pdf(self):
        # The text file acts as a corrupted/invalid PDF if renamed
        fake_pdf = self.test_dir / "fake.pdf"
        with open(fake_pdf, "w") as f:
            f.write("Corrupted data")
            
        with self.assertRaises(DocumentReaderError):
            read_pdf(fake_pdf)
            
        fake_pdf.unlink()

if __name__ == "__main__":
    unittest.main()