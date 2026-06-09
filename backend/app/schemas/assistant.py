from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AssistantMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        return " ".join(value.split())


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[AssistantMessage] = Field(default_factory=list, max_length=12)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        return " ".join(value.split())


class AssistantCandidateReference(BaseModel):
    applicant_id: UUID
    name: str = Field(min_length=1, max_length=160)
    job_title: str = Field(min_length=1, max_length=160)
    score: float | None = Field(default=None, ge=0, le=100)
    status: str = Field(min_length=1, max_length=50)
    reason: str = Field(min_length=1, max_length=500)


class AssistantActionType(StrEnum):
    MARK_UNDER_REVIEW = "mark_under_review"
    SHORTLIST_CANDIDATE = "shortlist_candidate"
    MOVE_TO_INTERVIEW = "move_to_interview"
    MARK_HIRED = "mark_hired"
    REJECT_CANDIDATE = "reject_candidate"
    SEND_SHORTLISTED_EMAIL = "send_shortlisted_email"
    SEND_REJECTED_EMAIL = "send_rejected_email"


class AssistantActionOutput(BaseModel):
    action_type: AssistantActionType
    applicant_id: UUID


class AssistantOutput(BaseModel):
    answer: str = Field(min_length=1, max_length=4000)
    candidate_ids: list[UUID] = Field(default_factory=list, max_length=8)
    suggested_prompts: list[str] = Field(default_factory=list, max_length=4)
    proposed_actions: list[AssistantActionOutput] = Field(
        default_factory=list,
        max_length=1,
    )

    @field_validator("answer")
    @classmethod
    def normalize_answer(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("candidate_ids")
    @classmethod
    def unique_candidate_ids(cls, values: list[UUID]) -> list[UUID]:
        return list(dict.fromkeys(values))

    @field_validator("suggested_prompts")
    @classmethod
    def normalize_prompts(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        for value in values:
            prompt = " ".join(value.split())[:160]
            if prompt and prompt.casefold() not in {
                existing.casefold() for existing in normalized
            }:
                normalized.append(prompt)
        return normalized


class AssistantActionProposal(BaseModel):
    action_type: AssistantActionType
    applicant_id: UUID
    candidate_name: str
    title: str
    description: str
    confirm_label: str
    tone: Literal["default", "danger"] = "default"


class AssistantChatData(BaseModel):
    answer: str
    candidates: list[AssistantCandidateReference] = Field(default_factory=list)
    suggested_prompts: list[str] = Field(default_factory=list)
    proposed_actions: list[AssistantActionProposal] = Field(default_factory=list)


class AssistantChatResponse(BaseModel):
    success: bool = True
    message: str
    data: AssistantChatData


class AssistantActionRequest(BaseModel):
    action_type: AssistantActionType
    applicant_id: UUID


class AssistantActionData(BaseModel):
    action_type: AssistantActionType
    applicant_id: UUID
    candidate_name: str
    status: str
    message: str


class AssistantActionResponse(BaseModel):
    success: bool = True
    message: str
    data: AssistantActionData
