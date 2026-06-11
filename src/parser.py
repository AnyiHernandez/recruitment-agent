from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from pypdf import PdfReader


@dataclass(frozen=True)
class ParsedDocument:
    path: Path
    file_name: str
    raw_text: str


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def normalize_text(text: str) -> str:
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_pdf(path: Path) -> ParsedDocument:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return ParsedDocument(path=path, file_name=path.name, raw_text=normalize_text(text))


def parse_text(path: Path) -> ParsedDocument:
    return ParsedDocument(
        path=path,
        file_name=path.name,
        raw_text=normalize_text(path.read_text(encoding="utf-8")),
    )


def parse_document(path: Path) -> ParsedDocument:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(path)
    if suffix in {".txt", ".md"}:
        return parse_text(path)
    raise ValueError(f"Unsupported document type: {path}")


def parse_documents(directory: Path) -> list[ParsedDocument]:
    if not directory.exists():
        raise FileNotFoundError(f"Input directory does not exist: {directory}")

    documents: list[ParsedDocument] = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            documents.append(parse_document(path))
    return documents
