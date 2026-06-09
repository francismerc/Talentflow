import json

from app.ai.gemini import GeminiClient
from app.schemas.ai import AIRecommendation


def test_parse_output_accepts_json_with_surrounding_text() -> None:
    output = GeminiClient._parse_output(
        "```json\n"
        + json.dumps(
            {
                "score": 82,
                "summary": "Relevant frontend evidence is present.",
                "strengths": ["React experience is clearly stated."],
                "weaknesses": ["Next.js evidence is not explicit."],
                "recommendation": "yes",
                "recommendation_reason": "Core role evidence is strong enough to review.",
            }
        )
        + "\n```"
    )

    assert output.score == 82
    assert output.recommendation is AIRecommendation.YES

