import json
import google.generativeai as genai
from typing import Dict, Any, List

from config import GEMINI_API_KEY, GEMINI_MODEL_NAME, MAX_CHARS_PER_CHUNK
from models import AnalysisPlan, AnalysisResult

class AnalyzerError(Exception):
    """Custom exception for analysis errors."""
    pass

class DocumentAnalyzer:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise AnalyzerError("GEMINI_API_KEY is not set. Please check your .env file.")
        
        genai.configure(api_key=GEMINI_API_KEY)
        # We use a model configured to enforce JSON output using Pydantic schemas where possible.
        self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    def generate_plan(self, objective: str, doc_filename: str, page_count: int) -> AnalysisPlan:
        """Asks the LLM to plan the analysis based on the user's objective."""
        prompt = f"""
        You are a Document Analysis Agent. 
        Document Name: {doc_filename} ({page_count} pages)
        User Objective: "{objective}"
        
        Create a detailed plan on how to analyze this document to fulfill the user's objective.
        Identify the focus areas and the search strategy.
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=AnalysisPlan
                )
            )
            return AnalysisPlan.model_validate_json(response.text)
        except Exception as e:
            raise AnalyzerError(f"Failed to generate analysis plan: {str(e)}")

    def _chunk_document(self, doc_data: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
        """Splits the document into manageable chunks based on character limits."""
        chunks = []
        current_chunk = []
        current_chars = 0
        
        for page in doc_data["pages"]:
            page_chars = len(page["text"])
            if current_chars + page_chars > MAX_CHARS_PER_CHUNK and current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_chars = 0
                
            current_chunk.append(page)
            current_chars += page_chars
            
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def analyze(self, doc_data: Dict[str, Any], plan: AnalysisPlan, objective: str) -> AnalysisResult:
        """Executes the analysis, chunking the document if necessary."""
        chunks = self._chunk_document(doc_data)
        
        if len(chunks) == 1:
            return self._analyze_chunk(chunks[0], plan, objective)
        else:
            # Multi-chunk processing
            chunk_results = []
            for i, chunk in enumerate(chunks):
                chunk_results.append(self._analyze_chunk(chunk, plan, objective, chunk_index=i+1, total_chunks=len(chunks)))
            return self._merge_results(chunk_results, plan, objective)

    def _analyze_chunk(self, pages: List[Dict[str, Any]], plan: AnalysisPlan, objective: str, chunk_index: int = 1, total_chunks: int = 1) -> AnalysisResult:
        """Analyzes a specific chunk of the document."""
        # Format the text with clear page boundaries for the LLM
        formatted_text = "\n\n".join([f"--- PAGE {p['page_number']} ---\n{p['text']}" for p in pages])
        
        prompt = f"""
        You are a Document Analysis Agent. This is chunk {chunk_index} of {total_chunks}.
        
        User Objective: "{objective}"
        
        Analysis Plan:
        - Focus Areas: {', '.join(plan.focus_areas)}
        - Search Strategy: {plan.search_strategy}
        
        Instructions:
        1. Read the document text below carefully.
        2. Extract key findings, risks, and trends matching the plan.
        3. For EVERY finding, you MUST include the exact source page number from the "--- PAGE X ---" headers.
        4. Distinguish between facts in the text and your own AI recommendations.
        
        DOCUMENT TEXT:
        {formatted_text}
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=AnalysisResult,
                    temperature=0.2 # Low temperature for factual extraction
                )
            )
            return AnalysisResult.model_validate_json(response.text)
        except Exception as e:
            raise AnalyzerError(f"Failed to analyze chunk {chunk_index}: {str(e)}")

    def _merge_results(self, results: List[AnalysisResult], plan: AnalysisPlan, objective: str) -> AnalysisResult:
        """Merges multiple chunk results into one cohesive final result."""
        # Convert Pydantic objects to JSON strings to feed back into the LLM
        combined_json = json.dumps([r.model_dump() for r in results])
        
        prompt = f"""
        You are a Document Analysis Agent. I have chunked a large document and analyzed it in parts.
        Below is a JSON array containing the analysis results from all the chunks.
        
        User Objective: "{objective}"
        
        Your task:
        Merge these disparate findings into a single, cohesive, final AnalysisResult.
        Remove duplicates, combine related findings, and maintain all page references accurately.
        
        CHUNK RESULTS:
        {combined_json}
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=AnalysisResult,
                    temperature=0.2
                )
            )
            return AnalysisResult.model_validate_json(response.text)
        except Exception as e:
            raise AnalyzerError(f"Failed to merge chunk results: {str(e)}")