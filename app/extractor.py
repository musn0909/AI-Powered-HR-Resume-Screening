
from pathlib import Path

import pymupdf
from docx import Document


MAX_PDF_PAGES = 30
MAX_EXTRACTED_CHARS = 200_000


def extract_pdf_text(file_path: Path) -> str:
    parts = []

    with pymupdf.open(file_path) as pdf:
        if pdf.needs_pass:
            raise ValueError(
                "Password-protected PDFs are not supported"
            )

        if pdf.page_count > MAX_PDF_PAGES:
            raise ValueError(
                "PDF exceeds the 30-page limit"
            )

        for page in pdf:
            parts.append(
                page.get_text("text", sort=True)
            )

            if sum(map(len, parts)) > MAX_EXTRACTED_CHARS:
                raise ValueError(
                    "Extracted text exceeds the limit"
                )

    return "\n".join(parts).strip()


def extract_docx_text(file_path: Path) -> str:
    document = Document(file_path)
    parts = []
    char_count = 0

    # Read paragraphs and tables in document order
    for block in document.iter_inner_content():
        if hasattr(block, "text") and not hasattr(
            block, "rows"
        ):
            content = block.text.strip()
            if content:
                parts.append(content)
                char_count += len(content)

        elif hasattr(block, "rows"):
            for row in block.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                ]
                content = " | ".join(cells)
                parts.append(content)
                char_count += len(content)

        if char_count > MAX_EXTRACTED_CHARS:
            raise ValueError(
                "Extracted text exceeds the limit"
            )

    return "\n".join(parts).strip()


def extract_resume_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension == ".docx":
        return extract_docx_text(file_path)

    raise ValueError("Unsupported resume format")
