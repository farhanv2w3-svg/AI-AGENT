from pydantic import BaseModel, Field
from typing import List, Optional

class Finding(BaseModel):
    title: str = Field(description="A concise title for the finding.")
    explanation: str = Field(description="Detailed explanation of the finding.")
    evidence: str = Field(description="Direct quotes or explicit evidence from the text.")
    page_references: List[int] = Field(default_factory=list, description="List of page numbers where this evidence was found.")

class AnalysisPlan(BaseModel):
    objective_understanding: str = Field(description="The agent's understanding of what the user wants.")
    focus_areas: List[str] = Field(description="Specific themes, metrics, or sections to analyze based on the objective.")
    search_strategy: str = Field(description="How the agent plans to extract this information.")

class AnalysisResult(BaseModel):
    document_summary: str = Field(description="A brief executive summary of the document.")
    objective: str = Field(description="The original user objective.")
    key_findings: List[Finding] = Field(description="The most important findings from the document.")
    risks_or_issues: List[Finding] = Field(description="Any problems, risks, or unusual values identified.")
    trends: List[str] = Field(default_factory=list, description="Any notable trends or patterns observed.")
    recommendations: List[str] = Field(default_factory=list, description="AI-generated recommendations based on the findings.")
    limitations: List[str] = Field(default_factory=list, description="Limitations of this analysis (e.g., missing data in the document).")
    confidence_notes: str = Field(description="A statement on how confident the AI is in these findings based on document clarity.")