import re
from dataclasses import dataclass, field
from pathlib import Path

EMAIL_PATTERN = re.compile(
    r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(?<!\w)(?:\+?\d{1,3}[\s().-]*)?(?:\d[\s().-]*){7,14}\d(?!\w)"
)
YEARS_EXPERIENCE_PATTERN = re.compile(
    r"\b(\d{1,2}(?:\.\d)?)\+?\s+years?(?:\s+of)?\s+(?:professional\s+)?experience\b",
    re.IGNORECASE,
)
SECTION_PATTERN = re.compile(
    r"^(education|academic background|experience|work experience|"
    r"professional experience|employment history|skills|technical skills|"
    r"core competencies)\s*:?\s*$",
    re.IGNORECASE,
)

NAME_EXCLUDED_WORDS = {
    "resume",
    "curriculum",
    "vitae",
    "profile",
    "summary",
    "experience",
    "education",
    "developer",
    "engineer",
    "designer",
    "manager",
}

COMMON_SKILLS = {
    "AWS",
    "Azure",
    "B2B SaaS",
    "CSS",
    "Design Systems",
    "Docker",
    "FastAPI",
    "Figma",
    "Git",
    "Java",
    "JavaScript",
    "Kubernetes",
    "Next.js",
    "Node.js",
    "PostgreSQL",
    "Prototyping",
    "Python",
    "React",
    "Redis",
    "SQL",
    "Tailwind CSS",
    "Testing",
    "TypeScript",
    "User Research",
}


@dataclass(frozen=True, slots=True)
class ExtractedCandidate:
    full_name: str
    email: str
    phone: str | None = None
    location: str | None = None
    education: list[dict[str, str]] = field(default_factory=list)
    experience: list[dict[str, str]] = field(default_factory=list)
    total_experience_years: float | None = None
    skills: list[str] = field(default_factory=list)


class CandidateExtractor:
    def extract(
        self,
        text: str,
        *,
        fallback_email: str,
        file_name: str,
        job_skills: list[str],
    ) -> ExtractedCandidate:
        email_match = EMAIL_PATTERN.search(text)
        email = (
            email_match.group(0).casefold()
            if email_match
            else fallback_email.casefold()
        )
        phone_match = PHONE_PATTERN.search(text)
        phone = self._normalize_phone(phone_match.group(0)) if phone_match else None
        return ExtractedCandidate(
            full_name=self._extract_name(text, email, file_name),
            email=email,
            phone=phone,
            location=self._extract_location(text),
            education=self._extract_section_lines(text, {"education", "academic background"}),
            experience=self._extract_section_lines(
                text,
                {"experience", "work experience", "professional experience", "employment history"},
            ),
            total_experience_years=self._extract_total_experience(text),
            skills=self._extract_skills(text, job_skills),
        )

    @staticmethod
    def _extract_name(text: str, email: str, file_name: str) -> str:
        for line in text.splitlines()[:12]:
            candidate = " ".join(line.split()).strip(" -|,")
            words = candidate.split()
            if not 2 <= len(words) <= 5 or len(candidate) > 80:
                continue
            if any(character.isdigit() for character in candidate):
                continue
            if "@" in candidate or PHONE_PATTERN.search(candidate):
                continue
            if any(word.casefold() in NAME_EXCLUDED_WORDS for word in words):
                continue
            if all(
                word.replace("-", "").replace("'", "").isalpha()
                for word in words
            ):
                return candidate.title() if candidate.isupper() else candidate

        stem = re.sub(r"[_-]+", " ", Path(file_name).stem)
        cleaned_stem = re.sub(
            r"\b(resume|cv|curriculum vitae)\b",
            "",
            stem,
            flags=re.IGNORECASE,
        )
        cleaned_stem = " ".join(cleaned_stem.split())
        if cleaned_stem and any(character.isalpha() for character in cleaned_stem):
            return cleaned_stem[:160].title()
        return email.split("@", maxsplit=1)[0].replace(".", " ").title()[:160]

    @staticmethod
    def _extract_location(text: str) -> str | None:
        for line in text.splitlines()[:15]:
            match = re.match(
                r"^(?:location|address)\s*:\s*(.+)$",
                line.strip(),
                re.IGNORECASE,
            )
            if match:
                return match.group(1).strip()[:200]
        return None

    @staticmethod
    def _extract_section_lines(
        text: str,
        target_sections: set[str],
    ) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        active = False
        for raw_line in text.splitlines():
            line = raw_line.strip()
            section_match = SECTION_PATTERN.match(line)
            if section_match:
                active = section_match.group(1).casefold() in target_sections
                continue
            if active and line:
                items.append({"text": line[:500]})
                if len(items) >= 20:
                    break
        return items

    @staticmethod
    def _extract_total_experience(text: str) -> float | None:
        match = YEARS_EXPERIENCE_PATTERN.search(text)
        return float(match.group(1)) if match else None

    @staticmethod
    def _extract_skills(text: str, job_skills: list[str]) -> list[str]:
        normalized_text = f" {re.sub(r'[^a-z0-9+#.]+', ' ', text.casefold())} "
        skill_catalog = sorted(
            {*COMMON_SKILLS, *job_skills},
            key=lambda value: (-len(value), value.casefold()),
        )
        matches: list[str] = []
        matched_tokens: list[set[str]] = []
        for skill in skill_catalog:
            normalized_skill = re.sub(
                r"[^a-z0-9+#.]+",
                " ",
                skill.casefold(),
            ).strip()
            skill_tokens = set(normalized_skill.split())
            if (
                normalized_skill
                and f" {normalized_skill} " in normalized_text
                and not any(skill_tokens < tokens for tokens in matched_tokens)
            ):
                matches.append(skill)
                matched_tokens.append(skill_tokens)
        return matches[:100]

    @staticmethod
    def _normalize_phone(value: str) -> str:
        return " ".join(value.strip().split())[:50]
