from __future__ import annotations

import re
from pathlib import Path

import pytest

from ndi.digital_copy_orchestrator import DigitalCopyOrchestrator, OrchestrationStage
from ndi.digital_copy_stage_contracts import StageEvidence, StageEvidenceKind
from ndi.digital_copy_workflow import DigitalCopySource, DigitalCopyStatus, new_job
from ndi.extractor import ExtractionError, extract_pdf_evidence, pdf_page_text


def _text_pdf(text: str) -> bytes:
    content = f"BT /F1 12 Tf 72 720 Td ({text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')}) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(content.encode('latin-1'))} >>\nstream\n{content}\nendstream".encode("latin-1"),
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


def _image_only_pdf() -> bytes:
    # Valid PDF page with no text layer. This is the relevant extraction property
    # of a scanned/OCR-like source before an OCR engine has produced text.
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << >> /Contents 4 0 R >>",
        b"<< /Length 0 >>\nstream\n\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


def test_text_native_fixture_runs_through_extraction_boundary(tmp_path: Path):
    source = tmp_path / "text-native.pdf"
    source.write_bytes(_text_pdf("TABLE 1: Fire resistance 120 min"))
    markdown = tmp_path / "extract" / "document.md"
    pages = tmp_path / "extract" / "pages.txt"

    evidence = extract_pdf_evidence(source, markdown, pages)
    assert evidence["page_count"] == 1
    assert evidence["markdown_characters"] > 0
    assert "Fire resistance" in markdown.read_text(encoding="utf-8")
    assert "Fire resistance" in pages.read_text(encoding="utf-8")


def test_ocr_like_no_text_layer_is_explicitly_detectable(tmp_path: Path):
    source = tmp_path / "ocr-like.pdf"
    source.write_bytes(_image_only_pdf())
    pages = pdf_page_text(source)
    assert len(pages) == 1
    assert pages[0].strip() == ""


def test_ocr_like_missing_text_blocks_extraction_stage(tmp_path: Path):
    source = tmp_path / "ocr-like.pdf"
    source.write_bytes(_image_only_pdf())
    job = new_job("extraction-e2e", DigitalCopySource.from_file(source))

    def extraction(job, root):
        text = pdf_page_text(source)
        if not any(page.strip() for page in text):
            return StageEvidence(
                StageEvidenceKind.EXTRACTION,
                False,
                {"extraction-log.json": "no text layer detected; OCR evidence required\n"},
                blockers=("OCR evidence required: source has no extractable text layer",),
            )
        return StageEvidence(StageEvidenceKind.EXTRACTION, True, {"extraction-log.json": "text present\n"})

    executors = {
        stage: lambda job, root, stage=stage: StageEvidence(
            StageEvidenceKind(stage.value), True, {f"{stage.value.lower()}.json": "{}\n"}
        )
        for stage in OrchestrationStage
    }
    executors[OrchestrationStage.EXTRACTION] = extraction

    with pytest.raises(RuntimeError, match="OCR evidence required"):
        DigitalCopyOrchestrator(tmp_path / "package", executors).run(job)
    assert job.status == DigitalCopyStatus.BLOCKED
