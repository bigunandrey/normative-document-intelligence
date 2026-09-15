from __future__ import annotations

"""Dependency-free user-facing Digital Copy workspace."""

from html import escape
import json
from pathlib import Path
from typing import Callable
from urllib.parse import unquote
from uuid import uuid4
from wsgiref.simple_server import make_server

from .digital_copy_package import persist_package
from .digital_copy_workflow import DigitalCopyJob, DigitalCopySource, DigitalCopyStatus, load_job, new_job

Runner = Callable[[DigitalCopyJob], DigitalCopyJob]
Archiver = Callable[[DigitalCopyJob], DigitalCopyJob]

_STATUS_ORDER = (
    DigitalCopyStatus.NEW, DigitalCopyStatus.IDENTIFYING, DigitalCopyStatus.EXTRACTING,
    DigitalCopyStatus.RECONCILING, DigitalCopyStatus.DIGITALIZING,
    DigitalCopyStatus.GRAPHICAL_VERIFICATION, DigitalCopyStatus.VERIFICATION_REQUIRED,
    DigitalCopyStatus.REGRESSION_REQUIRED, DigitalCopyStatus.DIGITAL_ACCEPTED,
    DigitalCopyStatus.BLOCKED,
)


def _json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def _read_jobs(root: Path) -> list[DigitalCopyJob]:
    jobs = []
    for path in sorted(root.glob("*/job.json")):
        try:
            jobs.append(load_job(path))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return sorted(jobs, key=lambda item: item.job_id)


def _job_payload(job: DigitalCopyJob) -> dict[str, object]:
    payload = job.as_dict()
    payload["accepted"] = job.accepted
    payload["artifact_names"] = sorted(job.artifacts)
    payload["operational_archive"] = job.metadata.get("operational_archive")
    return payload


def _status_class(status: DigitalCopyStatus) -> str:
    if status == DigitalCopyStatus.DIGITAL_ACCEPTED:
        return "accepted"
    if status == DigitalCopyStatus.BLOCKED:
        return "blocked"
    if status in {DigitalCopyStatus.VERIFICATION_REQUIRED, DigitalCopyStatus.REGRESSION_REQUIRED}:
        return "review"
    return "active"


def _page(title: str, body: str) -> bytes:
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} — NDI</title>
<style>
:root {{font-family:system-ui,sans-serif;color:#18202a;background:#f5f7fa}} body{{margin:0}}
header{{padding:18px 28px;background:#18202a;color:white}} main{{max-width:1200px;margin:24px auto;padding:0 20px}}
.card{{background:white;border:1px solid #dce2e8;border-radius:10px;padding:18px;margin:14px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}}
.badge{{display:inline-block;padding:4px 9px;border-radius:999px;font-size:12px;font-weight:700}}
.accepted{{background:#d9f5df;color:#155724}} .blocked{{background:#fde0e0;color:#8a1c1c}}
.review{{background:#fff0c7;color:#765500}} .active{{background:#e4ecff;color:#234b9a}}
a{{color:#174ea6;text-decoration:none}} a:hover{{text-decoration:underline}}
button,input[type=submit]{{padding:9px 13px;border:1px solid #b9c3ce;border-radius:7px;background:white;cursor:pointer}}
input[type=file]{{margin:8px 0}} code,pre{{background:#f1f3f5;border-radius:5px;padding:2px 5px}}
table{{width:100%;border-collapse:collapse}} th,td{{text-align:left;padding:8px;border-bottom:1px solid #e5e9ee}}
.viewer{{display:grid;grid-template-columns:minmax(0,2fr) minmax(280px,1fr);gap:16px}}
iframe{{width:100%;height:720px;border:1px solid #ccd3db;border-radius:8px;background:white}}
@media(max-width:800px){{.viewer{{grid-template-columns:1fr}}iframe{{height:520px}}}}
</style></head><body><header><strong>NDI — Digital Copy Workspace</strong></header><main>{body}</main></body></html>'''
    return html.encode()


class DigitalCopyUI:
    """Thin presentation/API boundary over persisted Digital Copy packages."""

    def __init__(self, workspace_root: Path, runner: Runner | None = None, archiver: Archiver | None = None):
        self.workspace_root = workspace_root.resolve()
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.runner = runner
        self.archiver = archiver

    def _job(self, job_id: str) -> DigitalCopyJob | None:
        candidate = self.workspace_root / job_id / "job.json"
        if candidate.resolve().parent.parent != self.workspace_root or not candidate.is_file():
            return None
        try:
            return load_job(candidate)
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def _respond(self, start_response, status: str, body: bytes, content_type: str = "text/html; charset=utf-8"):
        start_response(status, [("Content-Type", content_type), ("Content-Length", str(len(body)))])
        return [body]

    def _dashboard(self):
        jobs = _read_jobs(self.workspace_root)
        cards = "".join(
            f'<div class="card"><a href="/jobs/{escape(job.job_id)}"><h3>{escape(job.source.filename)}</h3></a>'
            f'<span class="badge {_status_class(job.status)}">{escape(job.status.value)}</span>'
            f'<p>Job: <code>{escape(job.job_id)}</code><br>Revision: <code>{escape(job.revision_id or "not locked")}</code>'
            f'<br>Archive: <code>{escape(str(job.metadata.get("operational_archive", {}).get("archive_id", "not archived")))}</code></p></div>'
            for job in jobs
        ) or '<div class="card">No Digital Copies yet.</div>'
        body = f'''<h1>Digital Copies</h1><div class="card"><h2>Create Digital Copy</h2>
<form id="create-form"><input id="source-file" type="file" accept="application/pdf" required>
<p><small>The PDF is stored as the immutable package-local source. Processing requires configured stage executors.</small></p>
<input type="submit" value="Create"></form><p id="create-error"></p></div>
<div class="grid">{cards}</div>
<script>
document.getElementById('create-form').addEventListener('submit', async (event) => {{
  event.preventDefault();
  const file = document.getElementById('source-file').files[0];
  if (!file) return;
  const response = await fetch('/api/jobs', {{method:'POST', headers:{{'X-Filename':file.name,'Content-Type':'application/pdf'}}, body:file}});
  if (response.ok) {{ const job = await response.json(); location.href = '/jobs/' + job.job_id; }}
  else {{ document.getElementById('create-error').textContent = (await response.text()); }}
}});
</script>'''
        return _page("Digital Copies", body)

    def _detail(self, job: DigitalCopyJob):
        evidence = []
        graphical = job.artifacts.get("graphical_evidence")
        if graphical and Path(graphical).is_file():
            try:
                evidence = json.loads(Path(graphical).read_text(encoding="utf-8")).get("items", [])
            except (OSError, ValueError, TypeError):
                evidence = []
        rows = "".join(
            f'<tr><td>{escape(str(item.get("element_kind", "")))}</td>'
            f'<td>p.{escape(str(item.get("region", {}).get("page", "")))}</td>'
            f'<td>{escape(str(item.get("source_text", "")))}</td>'
            f'<td>{escape(str(item.get("observed_text", "")))}</td>'
            f'<td>{"PASS" if item.get("match") else "BLOCKED"}</td></tr>' for item in evidence
        ) or '<tr><td colspan="5">No graphical evidence recorded.</td></tr>'
        blockers = "".join(f"<li>{escape(item)}</li>" for item in job.blockers) or "<li>None</li>"
        run = (f'<form action="/api/jobs/{escape(job.job_id)}/run" method="post"><input type="submit" value="Run workflow"></form>'
               if self.runner else '<p><small>Workflow runner is not configured in this generic UI process.</small></p>')
        archive = job.metadata.get("operational_archive")
        archive_controls = (
            f'<p><strong>Archived:</strong> <code>{escape(str(archive.get("archive_id", "")))}</code> '
            f'<span class="badge accepted">{escape(str(archive.get("result", "")))}</span> '
            f'<br>Manifest SHA-256 <code>{escape(str(archive.get("manifest_sha256", "")))}</code>'
            f'<br>Archive verification <strong>{"VALID" if archive.get("verified") else "UNVERIFIED"}</strong></p>'
            if archive else (
                f'<form action="/api/jobs/{escape(job.job_id)}/archive" method="post"><input type="submit" value="Archive accepted revision"></form>'
                if self.archiver and job.accepted else '<p><small>Operational archive is available after DIGITAL_ACCEPTED and requires a configured archive service.</small></p>'
            )
        )
        source_url = f"/jobs/{escape(job.job_id)}/source"
        body = f'''<p><a href="/">← Digital Copies</a></p><h1>{escape(job.source.filename)}</h1>
<div class="card"><span class="badge {_status_class(job.status)}">{escape(job.status.value)}</span>
<p>Job <code>{escape(job.job_id)}</code><br>Document <code>{escape(job.document_id or "not identified")}</code><br>
Revision <code>{escape(job.revision_id or "not locked")}</code><br>SHA-256 <code>{escape(job.source.sha256)}</code></p>{run}</div>
<div class="card"><h2>Operational Archive</h2>{archive_controls}</div>
<div class="card"><h2>Lifecycle</h2><table><tr><th>State</th><th>Marker</th></tr>'''
        for status in _STATUS_ORDER:
            body += f'<tr><td>{escape(status.value)}</td><td>{"CURRENT" if status == job.status else ""}</td></tr>'
        body += f'''</table></div><div class="card"><h2>Blockers</h2><ul>{blockers}</ul></div>
<div class="card"><h2>Graphical Verification</h2><div class="viewer">
<iframe src="{source_url}#page=1" title="Source PDF"></iframe>
<div><p>Source page is rendered by the browser PDF viewer. Evidence remains source-hash-bound and records page/region coordinates.</p>
<table><tr><th>Kind</th><th>Page</th><th>Source</th><th>Observed</th><th>Match</th></tr>{rows}</table></div></div></div>
<div class="card"><h2>Artifacts</h2><ul>'''
        for name, path in sorted(job.artifacts.items()):
            body += f'<li><code>{escape(name)}</code> — <code>{escape(path)}</code></li>'
        body += '</ul></div>'
        return _page("Digital Copy", body)

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = unquote(environ.get("PATH_INFO", "/"))
        if method == "GET" and path == "/":
            return self._respond(start_response, "200 OK", self._dashboard())
        if method == "GET" and path.startswith("/jobs/"):
            parts = path.strip("/").split("/")
            job = self._job(parts[1]) if len(parts) >= 2 else None
            if job is None:
                return self._respond(start_response, "404 Not Found", _page("Not found", "<h1>Job not found</h1>"))
            if len(parts) == 2:
                return self._respond(start_response, "200 OK", self._detail(job))
            if len(parts) == 3 and parts[2] == "source":
                source = (self.workspace_root / job.job_id / "source" / job.source.filename).resolve()
                source_root = (self.workspace_root / job.job_id / "source").resolve()
                if source.parent != source_root or not source.is_file():
                    return self._respond(start_response, "404 Not Found", b"Not found", "text/plain; charset=utf-8")
                return self._respond(start_response, "200 OK", source.read_bytes(), "application/pdf")
        if method == "GET" and path == "/api/jobs":
            return self._respond(start_response, "200 OK", _json([_job_payload(job) for job in _read_jobs(self.workspace_root)]), "application/json")
        if method == "GET" and path.startswith("/api/jobs/"):
            job = self._job(path.split("/")[3])
            if job is None:
                return self._respond(start_response, "404 Not Found", _json({"error": "job_not_found"}), "application/json")
            return self._respond(start_response, "200 OK", _json(_job_payload(job)), "application/json")
        if method == "POST" and path == "/api/jobs":
            try:
                length = int(environ.get("CONTENT_LENGTH") or "0")
            except ValueError:
                length = 0
            if length <= 0 or length > 100 * 1024 * 1024:
                return self._respond(start_response, "400 Bad Request", _json({"error": "invalid_source_size"}), "application/json")
            filename = Path(environ.get("HTTP_X_FILENAME", "source.pdf")).name
            if not filename.lower().endswith(".pdf"):
                return self._respond(start_response, "400 Bad Request", _json({"error": "source_must_be_pdf"}), "application/json")
            job_id = uuid4().hex
            incoming_dir = self.workspace_root / ".incoming" / job_id
            incoming = incoming_dir / filename
            incoming_dir.mkdir(parents=True, exist_ok=True)
            incoming.write_bytes(environ["wsgi.input"].read(length))
            try:
                job = new_job(job_id, DigitalCopySource.from_file(incoming))
                root = self.workspace_root / job.job_id
                persist_package(job, root)
                job.source = DigitalCopySource(str((root / "source" / filename).resolve()), filename, job.source.sha256)
                job.artifact_root = str(root)
                job.metadata["ui_created"] = True
                (root / "job.json").write_text(json.dumps(job.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            finally:
                incoming.unlink(missing_ok=True)
                incoming_dir.rmdir()
            return self._respond(start_response, "201 Created", _json(_job_payload(job)), "application/json")
        if method == "POST" and path.startswith("/api/jobs/") and path.endswith("/run"):
            job = self._job(path.split("/")[3])
            if job is None:
                return self._respond(start_response, "404 Not Found", _json({"error": "job_not_found"}), "application/json")
            if self.runner is None:
                return self._respond(start_response, "409 Conflict", _json({"error": "runner_not_configured"}), "application/json")
            try:
                result = self.runner(job)
            except Exception as exc:  # noqa: BLE001
                return self._respond(start_response, "409 Conflict", _json({"error": type(exc).__name__, "detail": str(exc)}), "application/json")
            return self._respond(start_response, "200 OK", _json(_job_payload(result)), "application/json")
        if method == "POST" and path.startswith("/api/jobs/") and path.endswith("/archive"):
            job = self._job(path.split("/")[3])
            if job is None:
                return self._respond(start_response, "404 Not Found", _json({"error": "job_not_found"}), "application/json")
            if self.archiver is None:
                return self._respond(start_response, "409 Conflict", _json({"error": "archiver_not_configured"}), "application/json")
            if not job.accepted:
                return self._respond(start_response, "409 Conflict", _json({"error": "job_not_accepted"}), "application/json")
            try:
                result = self.archiver(job)
            except Exception as exc:  # noqa: BLE001
                return self._respond(start_response, "409 Conflict", _json({"error": type(exc).__name__, "detail": str(exc)}), "application/json")
            return self._respond(start_response, "200 OK", _json(_job_payload(result)), "application/json")
        return self._respond(start_response, "404 Not Found", _page("Not found", "<h1>Not found</h1>"))

    def serve(self, host: str = "127.0.0.1", port: int = 8080):
        with make_server(host, port, self) as server:
            server.serve_forever()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Run the NDI Digital Copy UI")
    parser.add_argument("--root", type=Path, default=Path("digital-copies"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    DigitalCopyUI(args.root).serve(args.host, args.port)
