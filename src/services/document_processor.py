from __future__ import annotations

import re
from pathlib import Path

import docx2txt
from docx import Document as DocxDocument
from pypdf import PdfReader

from src.models import IngestedSection


class DocumentProcessor:
    """Extracts structured sections from supported document formats."""

    supported_extensions = {".pdf", ".docx", ".txt"}

    def load(self, file_path: Path) -> list[IngestedSection]:
        extension = file_path.suffix.lower()
        if extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {extension}")

        if extension == ".pdf":
            return self._load_pdf(file_path)
        if extension == ".docx":
            return self._load_docx(file_path)
        return self._load_txt(file_path)

    def _load_pdf(self, file_path: Path) -> list[IngestedSection]:
        reader = PdfReader(str(file_path))
        sections: list[IngestedSection] = []
        for page_index, page in enumerate(reader.pages, start=1):
            text = self._clean_text(page.extract_text() or "")
            if not text:
                continue
            sections.append(
                IngestedSection(
                    text=text,
                    file_name=file_path.name,
                    file_type="pdf",
                    page_number=page_index,
                    section_title=f"Page {page_index}",
                    order=page_index,
                )
            )
        return sections

    def _load_docx(self, file_path: Path) -> list[IngestedSection]:
        raw_text = docx2txt.process(str(file_path)) or ""
        if not raw_text.strip():
            return []

        doc = DocxDocument(str(file_path))
        sections: list[IngestedSection] = []
        current_heading = "Overview"
        buffer: list[str] = []
        order = 0

        for paragraph in doc.paragraphs:
            text = self._clean_text(paragraph.text)
            if not text:
                continue
            style_name = paragraph.style.name.lower() if paragraph.style else ""
            if "heading" in style_name:
                if buffer:
                    order += 1
                    sections.append(
                        IngestedSection(
                            text="\n".join(buffer),
                            file_name=file_path.name,
                            file_type="docx",
                            section_title=current_heading,
                            order=order,
                        )
                    )
                    buffer = []
                current_heading = text
            else:
                buffer.append(text)

        if buffer:
            order += 1
            sections.append(
                IngestedSection(
                    text="\n".join(buffer),
                    file_name=file_path.name,
                    file_type="docx",
                    section_title=current_heading,
                    order=order,
                )
            )

        if sections:
            return sections

        return [
            IngestedSection(
                text=self._clean_text(raw_text),
                file_name=file_path.name,
                file_type="docx",
                section_title="Overview",
                order=1,
            )
        ]

    def _load_txt(self, file_path: Path) -> list[IngestedSection]:
        raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
        cleaned = self._clean_text(raw_text)
        if not cleaned:
            return []

        blocks = [block.strip() for block in re.split(r"\n\s*\n", cleaned) if block.strip()]
        sections: list[IngestedSection] = []
        for index, block in enumerate(blocks, start=1):
            first_line = block.splitlines()[0][:80]
            section_title = first_line if len(first_line) > 6 else f"Block {index}"
            sections.append(
                IngestedSection(
                    text=block,
                    file_name=file_path.name,
                    file_type="txt",
                    section_title=section_title,
                    order=index,
                )
            )
        return sections

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
