from io import BytesIO

import fitz
import pytest
from docx import Document

from app.resume.parser import ResumeParser, ResumeParsingError


def make_pdf(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def make_docx(lines: list[str]) -> bytes:
    document = Document()
    for line in lines:
        document.add_paragraph(line)
    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_extracts_pdf_text() -> None:
    text = ResumeParser().extract_text(
        make_pdf(
            "Francis Barluado\nfrancis@example.com\n"
            "Frontend Engineer with 5 years of experience in React and TypeScript."
        ),
        "application/pdf",
    )

    assert "Francis Barluado" in text
    assert "React" in text


def test_extracts_docx_text() -> None:
    text = ResumeParser().extract_text(
        make_docx(
            [
                "Francis Barluado",
                "francis@example.com",
                "Frontend Engineer with React and TypeScript experience.",
            ]
        ),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    assert "Francis Barluado" in text
    assert "TypeScript" in text


def test_legacy_doc_requires_conversion() -> None:
    with pytest.raises(ResumeParsingError, match="Legacy DOC"):
        ResumeParser().extract_text(b"legacy-doc", "application/msword")


def test_image_only_pdf_requires_review() -> None:
    document = fitz.open()
    document.new_page()
    content = document.tobytes()
    document.close()

    with pytest.raises(ResumeParsingError, match="too little"):
        ResumeParser().extract_text(content, "application/pdf")
