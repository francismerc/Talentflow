from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class AIRecommendation(StrEnum):
    STRONG_YES = "strong_yes"
    YES = "yes"
    REVIEW = "review"
    NO = "no"
    STRONG_NO = "strong_no"


class CandidateAnalysisOutput(BaseModel):
    score: float = Field(ge=0, le=100)
    summary: str = Field(min_length=10, max_length=1200)
    strengths: list[str] = Field(min_length=1, max_length=6)
    weaknesses: list[str] = Field(min_length=1, max_length=6)
    recommendation: AIRecommendation
    recommendation_reason: str = Field(min_length=10, max_length=1200)

    @field_validator("summary", "recommendation_reason")
    @classmethod
    def normalize_paragraph(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("strengths", "weaknesses")
    @classmethod
    def normalize_points(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        for value in values:
            point = " ".join(value.split())[:300]
            if point and point.casefold() not in {
                existing.casefold() for existing in normalized
            }:
                normalized.append(point)
        if not normalized:
            raise ValueError("At least one evidence-based point is required.")
        return normalized
