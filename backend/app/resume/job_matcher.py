import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any
from uuid import UUID

SUBJECT_NOISE = re.compile(
    r"\b(application|applying|applicant|resume|cv|for|position|role|job)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class JobMatch:
    job_id: UUID
    title: str
    required_skills: list[str]
    confidence: float


class JobMatcher:
    def match(
        self,
        subject: str,
        jobs: list[dict[str, Any]],
    ) -> JobMatch | None:
        normalized_subject = self._normalize(subject)
        if not normalized_subject:
            return None

        candidates: list[JobMatch] = []
        for job in jobs:
            title = str(job["title"])
            normalized_title = self._normalize(title)
            if normalized_title in normalized_subject:
                confidence = 1.0
            else:
                cleaned_subject = self._normalize(SUBJECT_NOISE.sub(" ", subject))
                confidence = SequenceMatcher(
                    None,
                    cleaned_subject,
                    normalized_title,
                ).ratio()
            candidates.append(
                JobMatch(
                    job_id=UUID(str(job["id"])),
                    title=title,
                    required_skills=list(job.get("required_skills") or []),
                    confidence=confidence,
                )
            )

        best_match = max(candidates, key=lambda candidate: candidate.confidence)
        return best_match if best_match.confidence >= 0.72 else None

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(re.sub(r"[^a-z0-9+#.]+", " ", value.casefold()).split())
