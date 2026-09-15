from __future__ import annotations

"""Interactive evidence-first Digital Copy workspace."""

from html import escape
import json
from pathlib import Path
from typing import Callable
from urllib.parse import unquote
from uuid import uuid4
from wsgiref.simple_server import make_server

import fitz

from .digital_copy_package import persist_package
from .digital_copy_workflow import DigitalCopyJob, DigitalCopySource, DigitalCopyStatus, load_job, new_job, persist_job_file

Runner = Callable[[DigitalCopyJob], DigitalCopyJob]
Archiver = Callable[[DigitalCopyJob], DigitalCopyJob]

_STATUS_ORDER = (DigitalCopyStatus.NEW, DigitalCopyStatus.IDENTIFYING, DigitalCopyStatus.EXTRACTING, DigitalCopyStatus.RECONCILING, DigitalCopyStatus.DIGITALIZING, DigitalCopyStatus.GRAPHICAL_VERIFICATION, DigitalCopyStatus.VERIFICATION_REQUIRED, DigitalCopyStatus.REGRESSION_REQUIRED, DigitalCopyStatus.DIGITAL_ACCEPTED, DigitalCopyStatus.BLOCKED)
_VIEWS = (("overview", "Overview"), ("extraction", "Extraction"), ("structure", "Structure"), ("discrepancies", "Discrepancies"), ("digital-copy", "Digital Copy"), ("graphical", "Graphical Verification"), ("verification", "Verification"), ("acceptance", "Acceptance"), ("revision", "Revision History"), ("export", "Export / Handoff"))


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
    if status == DigitalCopyStatus.DIGITAL_ACCEPTED: return "accepted"
    if status == DigitalCopyStatus.BLOCKED: return "blocked"
    if status in {DigitalCopyStatus.VERIFICATION_REQUIRED, DigitalCopyStatus.REGRESSION_REQUIRED}: return "review"
    return "active"


def _safe_artifact(job: DigitalCopyJob, value: str) -> Path | None:
    root = Path(job.artifact_root or "").resolve()
    candidate = (Path(value) if Path(value).is_absolute() else root / value).resolve()
    try: candidate.relative_to(root)
    except ValueError: return None
    return candidate if candidate.is_file() else None


def _artifact_json(job: DigitalCopyJob, name: str) -> object:
    value = job.artifacts.get(name)
    if not value: return None
    path = _safe_artifact(job, value)
    if not path: return None
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError): return None


def _page(title: str, body: str) -> bytes:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)} — NDI</title><style>
:root{{font-family:system-ui,-apple-system,sans-serif;color:#18202a;background:#f5f7fa}}*{{box-sizing:border-box}}body{{margin:0}}header{{height:58px;padding:16px 22px;background:#18202a;color:#fff;display:flex;justify-content:space-between}}main{{max-width:1500px;margin:auto;padding:16px}}.shell{{display:grid;grid-template-columns:220px minmax(0,1fr);gap:16px}}nav,.card{{background:#fff;border:1px solid #dce2e8;border-radius:9px}}nav{{padding:8px;height:max-content;position:sticky;top:12px}}nav a{{display:block;padding:9px 10px;border-radius:6px}}nav a:hover{{background:#edf2f8;text-decoration:none}}.card{{padding:16px;margin-bottom:14px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}}.metric{{font-size:25px;font-weight:700}}.badge{{display:inline-block;padding:4px 9px;border-radius:999px;font-size:12px;font-weight:700}}.accepted{{background:#d9f5df;color:#155724}}.blocked{{background:#fde0e0;color:#8a1c1c}}.review{{background:#fff0c7;color:#765500}}.active{{background:#e4ecff;color:#234b9a}}a{{color:#174ea6;text-decoration:none}}button,input[type=submit]{{padding:8px 12px;border:1px solid #b9c3ce;border-radius:6px;background:#fff;cursor:pointer}}code,pre{{background:#f1f3f5;border-radius:5px;padding:2px 5px}}pre{{padding:12px;overflow:auto;white-space:pre-wrap}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:8px;border-bottom:1px solid #e5e9ee;vertical-align:top}}.workspace{{display:grid;grid-template-columns:minmax(0,1fr) 330px;gap:14px}}.pdf-panel{{background:#20252b;padding:14px;border-radius:9px;min-height:760px}}.pdf-toolbar{{display:flex;gap:7px;align-items:center;flex-wrap:wrap;color:#fff;margin-bottom:10px}}.pdf-stage{{position:relative;margin:auto;width:max-content;max-width:100%;box-shadow:0 2px 12px #1118}}#pdf-page{{display:block;max-width:100%;height:auto}}#overlay{{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}}.evidence-list{{max-height:700px;overflow:auto}}.evidence{{border:1px solid #dce2e8;border-radius:7px;padding:9px;margin:7px 0;cursor:pointer}}.evidence:hover{{background:#f7f9fb}}.tree button{{display:block;width:100%;text-align:left;border:0;background:transparent;padding:7px;cursor:pointer}}.tree button:hover{{background:#edf2f8}}.small{{font-size:12px;color:#5f6b76}}.danger{{border-left:4px solid #b42318}}.success{{border-left:4px solid #217a36}}@media(max-width:900px){{.shell,.workspace{{grid-template-columns:1fr}}nav{{position:static}}.pdf-panel{{min-height:500px}}}}
</style></head><body><header><strong>NDI — Digital Copy Workspace</strong><span>Evidence-first · fail-closed</span></header><main>{body}</main></body></html>'''.encode()


class DigitalCopyUI:
    """Presentation/API boundary over persisted Digital Copy packages."""

    def __init__(self, workspace_root: Path, runner: Runner | None = None, archiver: Archiver | None = None):
        self.workspace_root = workspace_root.resolve(); self.workspace_root.mkdir(parents=True, exist_ok=True); self.runner = runner; self.archiver = archiver

    def _job(self, job_id: str) -> DigitalCopyJob | None:
        if not job_id or Path(job_id).name != job_id: return None
        candidate = self.workspace_root / job_id / "job.json"
        if candidate.resolve().parent.parent != self.workspace_root or not candidate.is_file(): return None
        try: return load_job(candidate)
        except (OSError, ValueError, KeyError, TypeError): return None

    def _source(self, job: DigitalCopyJob) -> Path | None:
        root=(self.workspace_root/job.job_id/"source").resolve(); source=(root/job.source.filename).resolve()
        return source if source.parent == root and source.is_file() else None

    def _evidence(self, job: DigitalCopyJob) -> list[dict]:
        data=_artifact_json(job,"graphical_evidence")
        return [x for x in data.get("items",[]) if isinstance(x,dict)] if isinstance(data,dict) and isinstance(data.get("items"),list) else []

    def _structure(self, job: DigitalCopyJob) -> list[dict]:
        for name in ("canonical","canonical_document","digital_revision"):
            data=_artifact_json(job,name)
            if isinstance(data,dict):
                nodes=data.get("nodes")
                if isinstance(nodes,list): return [x for x in nodes if isinstance(x,dict)]
                doc=data.get("document")
                if isinstance(doc,dict) and isinstance(doc.get("nodes"),list): return [x for x in doc["nodes"] if isinstance(x,dict)]
        return []

    def _discrepancies(self, job: DigitalCopyJob) -> list[dict]:
        out=[]
        for name in ("discrepancies","external_comparison","reconciliation","semantic_evaluation"):
            data=_artifact_json(job,name)
            if isinstance(data,dict):
                for key in ("discrepancies","issues","conflicts","findings"):
                    if isinstance(data.get(key),list): out.extend(x for x in data[key] if isinstance(x,dict))
        return out

    def _respond(self, start_response, status: str, body: bytes, content_type: str="text/html; charset=utf-8"):
        start_response(status,[("Content-Type",content_type),("Content-Length",str(len(body)))])
        return [body]

    def _dashboard(self):
        jobs=_read_jobs(self.workspace_root)
        cards="".join(f'<div class="card"><a href="/jobs/{escape(j.job_id)}"><h3>{escape(j.source.filename)}</h3></a><span class="badge {_status_class(j.status)}">{escape(j.status.value)}</span><p>Job <code>{escape(j.job_id)}</code><br>Revision: <code>{escape(j.revision_id or "not locked")}</code><br>Archive: <code>{escape(str(j.metadata.get("operational_archive",{}).get("archive_id","not archived")))}</code></p></div>' for j in jobs) or '<div class="card">No Digital Copies yet.</div>'
        body=f'''<h1>Digital Copies</h1><div class="card"><h2>Create Digital Copy</h2><form id="create-form"><input id="source-file" type="file" accept="application/pdf" required><p><small>The PDF is stored as the immutable package-local source.</small></p><input type="submit" value="Create"></form><p id="create-error"></p></div><div class="grid">{cards}</div><script>document.getElementById('create-form').addEventListener('submit',async(e)=>{{e.preventDefault();const f=document.getElementById('source-file').files[0];if(!f)return;const r=await fetch('/api/jobs',{{method:'POST',headers:{{'X-Filename':f.name,'Content-Type':'application/pdf'}},body:f}});if(r.ok)location.href='/jobs/'+(await r.json()).job_id;else document.getElementById('create-error').textContent=await r.text()}});</script>'''
        return _page("Digital Copies",body)

    def _detail(self, job: DigitalCopyJob):
        evidence=self._evidence(job); nodes=self._structure(job); discrepancies=self._discrepancies(job); archive=job.metadata.get("operational_archive")
        blockers="".join(f"<li>{escape(x)}</li>" for x in job.blockers) or "<li>None</li>"
        nav=''.join(f'<a href="#view-{k}">{label}</a>' for k,label in _VIEWS)
        run=f'<form action="/api/jobs/{escape(job.job_id)}/run" method="post"><input type="submit" value="Run workflow"></form>' if self.runner else '<p class="small">Workflow runner is not configured.</p>'
        archive_ui=(f'<p><strong>Archive:</strong> <code>{escape(str(archive.get("archive_id","")))}</code> <span class="badge accepted">{escape(str(archive.get("result","")))}</span><br>Manifest SHA-256 <code>{escape(str(archive.get("manifest_sha256","")))}</code><br>Verification <strong>{"VALID" if archive.get("verified") else "UNVERIFIED"}</strong></p>' if archive else (f'<form action="/api/jobs/{escape(job.job_id)}/archive" method="post"><input type="submit" value="Archive accepted revision"></form>' if self.archiver and job.accepted else '<p class="small">Available after DIGITAL_ACCEPTED.</p>'))
        evcards=''.join(f'<div class="evidence" data-eid="{escape(str(x.get("evidence_id","")))}"><strong>{escape(str(x.get("element_kind","")))}</strong> · page {escape(str(x.get("region",{}).get("page","")))}<br><span class="small">{escape(str(x.get("source_text","")))}</span></div>' for x in evidence) or '<p class="small">No graphical evidence recorded.</p>'
        node_rows=''.join(f'<tr><td><button class="node" data-node="{escape(str(n.get("node_id",n.get("id",""))))}">{escape(str(n.get("node_type",n.get("type","node"))))}</button></td><td>{escape(str(n.get("text",n.get("source_text",""))))}</td><td>{escape(str(n.get("source_anchor",n.get("anchor",""))))}</td></tr>' for n in nodes) or '<tr><td colspan="3">Canonical structure artifact is not available yet.</td></tr>'
        disc_rows=''.join(f'<tr><td>{escape(str(x.get("id",x.get("discrepancy_id",""))))}</td><td>{escape(str(x.get("status",x.get("result",""))))}</td><td>{escape(str(x.get("reason",x.get("message",x.get("description","")))))}</td></tr>' for x in discrepancies) or '<tr><td colspan="3">No persisted discrepancies.</td></tr>'
        ev_json=json.dumps(evidence,ensure_ascii=False); node_json=json.dumps(nodes,ensure_ascii=False)
        lifecycle=''.join(f'<tr><td>{escape(s.value)}</td><td>{"CURRENT" if s==job.status else ""}</td></tr>' for s in _STATUS_ORDER)
        artifacts=''.join(f'<li><code>{escape(k)}</code> — <code>{escape(v)}</code></li>' for k,v in sorted(job.artifacts.items())) or '<li>No artifacts yet.</li>'
        body=f'''<div class="shell"><nav><a href="/">← Digital Copies</a>{nav}</nav><section><div class="card"><h1>{escape(job.source.filename)}</h1><span class="badge {_status_class(job.status)}">{escape(job.status.value)}</span><p>Document <code>{escape(job.document_id or "not identified")}</code> · Revision <code>{escape(job.revision_id or "not locked")}</code><br>Source SHA-256 <code>{escape(job.source.sha256)}</code></p>{run}</div>
<section id="view-overview" class="card"><h2>Overview</h2><div class="grid"><div><div class="metric">{len(evidence)}</div>graphical evidence items</div><div><div class="metric">{len(nodes)}</div>canonical nodes</div><div><div class="metric">{len(discrepancies)}</div>discrepancy findings</div><div><div class="metric">{"YES" if job.accepted else "NO"}</div>DIGITAL_ACCEPTED</div></div></section>
<section id="view-extraction" class="card"><h2>Extraction</h2><p>Parser and extraction artifacts exposed from the engine package.</p><ul>{artifacts}</ul></section>
<section id="view-structure" class="card"><h2>Structure</h2><p class="small">Canonical structure is distinct from parser observations. Selecting a node navigates to its source anchor when available.</p><table><tr><th>Node</th><th>Text</th><th>Anchor</th></tr>{node_rows}</table></section>
<section id="view-discrepancies" class="card"><h2>Discrepancies</h2><table><tr><th>ID</th><th>Status</th><th>Finding</th></tr>{disc_rows}</table></section>
<section id="view-digital-copy" class="card"><h2>Digital Copy</h2><p>The representation is engine-derived. The UI provides no manual acceptance control.</p><pre>{escape(json.dumps(_job_payload(job),ensure_ascii=False,sort_keys=True,indent=2))}</pre></section>
<section id="view-graphical" class="card"><h2>Graphical Verification</h2><div class="workspace"><div class="pdf-panel"><div class="pdf-toolbar"><button id="prev">◀</button><span>Page <input id="page" type="number" min="1" value="1" style="width:55px"></span><button id="next">▶</button><button id="zoom-out">−</button><span id="zoom">100%</span><button id="zoom-in">+</button><button id="fit">Fit</button><a href="/jobs/{escape(job.job_id)}/source" target="_blank" style="color:white">Open original PDF</a></div><div class="pdf-stage"><img id="pdf-page" alt="Rendered source PDF page"><canvas id="overlay"></canvas></div></div><aside><h3>Evidence</h3><p class="small">The page is rendered directly from the immutable source PDF. Overlays use stored page/bbox coordinates and scale with the rendered page.</p><div class="evidence-list">{evcards}</div></aside></div></section>
<section id="view-verification" class="card"><h2>Verification</h2><p>Verification is read from persisted engine evidence; independent verifiers and evidence hashes remain immutable inputs to acceptance.</p><pre>{escape(json.dumps(job.metadata.get("verification",{}),ensure_ascii=False,sort_keys=True,indent=2))}</pre></section>
<section id="view-acceptance" class="card {'success' if job.accepted else 'danger'}"><h2>Acceptance</h2><p><strong>{'DIGITAL_ACCEPTED' if job.accepted else 'NOT ACCEPTED'}</strong></p><p>Acceptance is derived from workflow gates; the UI cannot manually set it.</p><h3>Blockers</h3><ul>{blockers}</ul></section>
<section id="view-revision" class="card"><h2>Revision History</h2><p>Revision <code>{escape(job.revision_id or 'not locked')}</code><br>Source SHA-256 <code>{escape(job.source.sha256)}</code></p><p>Operational archive: {escape(str(archive.get('archive_id','not archived') if archive else 'not archived'))}</p></section>
<section id="view-export" class="card"><h2>Export / Handoff</h2><p>Export identifies the exact accepted revision, source SHA-256, manifest and evidence hashes.</p>{archive_ui}</section></section></div>
<script>const evidence={ev_json};const nodes={node_json};let page=1,zoom=1;const jobId={json.dumps(job.job_id)};const img=document.getElementById('pdf-page'),canvas=document.getElementById('overlay'),ctx=canvas.getContext('2d');function render(){{img.src=`/jobs/${{jobId}}/page/${{page}}.png?z=${{zoom}}`;document.getElementById('page').value=page;document.getElementById('zoom').textContent=Math.round(zoom*100)+'%'}}img.onload=()=>{{canvas.width=img.clientWidth;canvas.height=img.clientHeight;draw()}};function draw(selected){{ctx.clearRect(0,0,canvas.width,canvas.height);const scale=canvas.clientWidth/(img.naturalWidth||canvas.clientWidth);for(const e of evidence){{const r=e.region||{{}};if(Number(r.page)!==page)continue;const x0=Number(r.x0||0)*scale,y0=Number(r.y0||0)*scale,x1=Number(r.x1||0)*scale,y1=Number(r.y1||0)*scale;ctx.strokeStyle=String(e.evidence_id)===String(selected)?'#ff8800':'#d22';ctx.lineWidth=2;ctx.strokeRect(x0,y0,x1-x0,y1-y0)}}}document.querySelectorAll('.evidence').forEach(el=>el.onclick=()=>{{const e=evidence.find(x=>String(x.evidence_id)===el.dataset.eid);if(e){{page=Number(e.region?.page||1);render();setTimeout(()=>draw(el.dataset.eid),100)}}}});document.querySelectorAll('.node').forEach(el=>el.onclick=()=>{{const n=nodes.find(x=>String(x.node_id||x.id)===el.dataset.node),a=n?.source_anchor||n?.anchor;if(a?.page){{page=Number(a.page);render()}}}});document.getElementById('prev').onclick=()=>{{if(page>1){{page--;render()}}}};document.getElementById('next').onclick=()=>{{page++;render()}};document.getElementById('page').onchange=e=>{{page=Math.max(1,Number(e.target.value));render()}};document.getElementById('zoom-in').onclick=()=>{{zoom=Math.min(3,zoom+.25);render()}};document.getElementById('zoom-out').onclick=()=>{{zoom=Math.max(.5,zoom-.25);render()}};document.getElementById('fit').onclick=()=>{{zoom=1;render()}};render();</script>'''
        return _page("Digital Copy",body)

    def __call__(self,environ,start_response):
        method=environ.get("REQUEST_METHOD","GET").upper(); path=unquote(environ.get("PATH_INFO","/"))
        if method=="GET" and path=="/": return self._respond(start_response,"200 OK",self._dashboard())
        if method=="GET" and path.startswith("/jobs/"):
            parts=path.strip("/").split("/"); job=self._job(parts[1]) if len(parts)>=2 else None
            if job is None:return self._respond(start_response,"404 Not Found",_page("Not found","<h1>Job not found</h1>"))
            if len(parts)==2:return self._respond(start_response,"200 OK",self._detail(job))
            if len(parts)==3 and parts[2]=="source":
                source=self._source(job)
                if source is None:return self._respond(start_response,"404 Not Found",b"Not found","text/plain; charset=utf-8")
                return self._respond(start_response,"200 OK",source.read_bytes(),"application/pdf")
            if len(parts)==4 and parts[2]=="page" and parts[3].endswith(".png"):
                try: page_number=int(parts[3][:-4])
                except ValueError: page_number=0
                source=self._source(job)
                if source is None or page_number<1:return self._respond(start_response,"404 Not Found",b"Not found","text/plain; charset=utf-8")
                try:
                    with fitz.open(source) as doc:
                        if page_number>len(doc):return self._respond(start_response,"404 Not Found",b"Page not found","text/plain; charset=utf-8")
                        pix=doc[page_number-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
                        return self._respond(start_response,"200 OK",pix.tobytes("png"),"image/png")
                except (OSError,RuntimeError,ValueError): return self._respond(start_response,"422 Unprocessable Entity",b"PDF render failed","text/plain; charset=utf-8")
        if method=="GET" and path=="/api/jobs":return self._respond(start_response,"200 OK",_json([_job_payload(j) for j in _read_jobs(self.workspace_root)]),"application/json")
        if method=="GET" and path.startswith("/api/jobs/"):
            job=self._job(path.split("/")[3])
            if job is None:return self._respond(start_response,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
            return self._respond(start_response,"200 OK",_json(_job_payload(job)),"application/json")
        if method=="POST" and path=="/api/jobs":
            try:length=int(environ.get("CONTENT_LENGTH") or "0")
            except ValueError:length=0
            if length<=0 or length>100*1024*1024:return self._respond(start_response,"400 Bad Request",_json({"error":"invalid_source_size"}),"application/json")
            filename=Path(environ.get("HTTP_X_FILENAME","source.pdf")).name
            if not filename.lower().endswith(".pdf"):return self._respond(start_response,"400 Bad Request",_json({"error":"source_must_be_pdf"}),"application/json")
            job_id=uuid4().hex; incoming_dir=self.workspace_root/".incoming"/job_id; incoming=incoming_dir/filename; incoming_dir.mkdir(parents=True,exist_ok=True); incoming.write_bytes(environ["wsgi.input"].read(length))
            try:
                job=new_job(job_id,DigitalCopySource.from_file(incoming)); root=self.workspace_root/job.job_id; persist_package(job,root); job.source=DigitalCopySource(str((root/"source"/filename).resolve()),filename,job.source.sha256); job.artifact_root=str(root); job.metadata["ui_created"]=True; persist_job_file(job,root/"job.json")
            finally:
                incoming.unlink(missing_ok=True)
                try:incoming_dir.rmdir()
                except OSError:pass
            return self._respond(start_response,"201 Created",_json(_job_payload(job)),"application/json")
        if method=="POST" and path.startswith("/api/jobs/") and path.endswith("/run"):
            job=self._job(path.split("/")[3])
            if job is None:return self._respond(start_response,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
            if self.runner is None:return self._respond(start_response,"409 Conflict",_json({"error":"runner_not_configured"}),"application/json")
            try:result=self.runner(job);persist_job_file(result,self.workspace_root/result.job_id/"job.json")
            except Exception as exc:return self._respond(start_response,"409 Conflict",_json({"error":type(exc).__name__,"detail":str(exc)}),"application/json")
            return self._respond(start_response,"200 OK",_json(_job_payload(result)),"application/json")
        if method=="POST" and path.startswith("/api/jobs/") and path.endswith("/archive"):
            job=self._job(path.split("/")[3])
            if job is None:return self._respond(start_response,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
            if not job.accepted:return self._respond(start_response,"409 Conflict",_json({"error":"job_not_accepted"}),"application/json")
            if self.archiver is None:return self._respond(start_response,"409 Conflict",_json({"error":"archiver_not_configured"}),"application/json")
            try:result=self.archiver(job);persist_job_file(result,self.workspace_root/result.job_id/"job.json")
            except Exception as exc:return self._respond(start_response,"409 Conflict",_json({"error":type(exc).__name__,"detail":str(exc)}),"application/json")
            return self._respond(start_response,"200 OK",_json(_job_payload(result)),"application/json")
        return self._respond(start_response,"404 Not Found",_json({"error":"not_found"}),"application/json")


def main()->None:
    import argparse
    parser=argparse.ArgumentParser(description="NDI Digital Copy UI");parser.add_argument("--workspace",type=Path,default=Path(".ndi-workspace"));parser.add_argument("--host",default="127.0.0.1");parser.add_argument("--port",type=int,default=8000);args=parser.parse_args()
    with make_server(args.host,args.port,DigitalCopyUI(args.workspace)) as server: print(f"NDI Digital Copy UI: http://{args.host}:{args.port}");server.serve_forever()


if __name__=="__main__":main()
