from __future__ import annotations

from io import BytesIO
from pathlib import Path

from ndi.digital_copy_ui import DigitalCopyUI
from ndi.digital_copy_workflow import DigitalCopyStatus


def request(app, method: str, path: str, body: bytes = b"", filename: str = "source.pdf"):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(body)),
        "CONTENT_TYPE": "application/octet-stream",
        "HTTP_X_FILENAME": filename,
        "wsgi.input": BytesIO(body),
    }
    response = b"".join(app(environ, start_response))
    return captured, response


def test_dashboard_and_api_are_empty(tmp_path: Path):
    app = DigitalCopyUI(tmp_path)
    status, body = request(app, "GET", "/")
    assert status["status"] == "200 OK"
    assert b"Digital Copies" in body
    status, body = request(app, "GET", "/api/jobs")
    assert status["status"] == "200 OK"
    assert body.strip() == b"[]"


def test_create_job_persists_immutable_source_and_exposes_detail(tmp_path: Path):
    app = DigitalCopyUI(tmp_path)
    source = b"%PDF-1.4\n% NDI fixture\n"
    status, body = request(app, "POST", "/api/jobs", source, "fixture.pdf")
    assert status["status"] == "201 Created"
    payload = __import__("json").loads(body)
    job_id = payload["job_id"]
    assert payload["status"] == DigitalCopyStatus.NEW.value
    stored = tmp_path / job_id / "source" / "fixture.pdf"
    assert stored.read_bytes() == source

    status, body = request(app, "GET", f"/jobs/{job_id}")
    assert status["status"] == "200 OK"
    assert b"fixture.pdf" in body
    assert b"not locked" in body

    status, body = request(app, "GET", f"/jobs/{job_id}/source")
    assert status["status"] == "200 OK"
    assert body == source


def test_create_rejects_non_pdf_and_oversized_input(tmp_path: Path):
    app = DigitalCopyUI(tmp_path)
    status, body = request(app, "POST", "/api/jobs", b"data", "notes.txt")
    assert status["status"] == "400 Bad Request"
    assert b"source_must_be_pdf" in body


def test_run_requires_injected_runner(tmp_path: Path):
    app = DigitalCopyUI(tmp_path)
    _, body = request(app, "POST", "/api/jobs", b"%PDF-1.4\n", "a.pdf")
    job_id = __import__("json").loads(body)["job_id"]
    status, body = request(app, "POST", f"/api/jobs/{job_id}/run")
    assert status["status"] == "409 Conflict"
    assert b"runner_not_configured" in body


def test_run_uses_injected_runner(tmp_path: Path):
    def runner(job):
        job.status = DigitalCopyStatus.DIGITAL_ACCEPTED
        return job

    app = DigitalCopyUI(tmp_path, runner=runner)
    _, body = request(app, "POST", "/api/jobs", b"%PDF-1.4\n", "a.pdf")
    job_id = __import__("json").loads(body)["job_id"]
    status, body = request(app, "POST", f"/api/jobs/{job_id}/run")
    assert status["status"] == "200 OK"
    assert __import__("json").loads(body)["accepted"] is True
