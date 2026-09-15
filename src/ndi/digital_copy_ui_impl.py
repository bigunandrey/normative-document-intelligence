from __future__ import annotations

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

STATES = (DigitalCopyStatus.NEW, DigitalCopyStatus.IDENTIFYING, DigitalCopyStatus.EXTRACTING, DigitalCopyStatus.RECONCILING, DigitalCopyStatus.DIGITALIZING, DigitalCopyStatus.GRAPHICAL_VERIFICATION, DigitalCopyStatus.VERIFICATION_REQUIRED, DigitalCopyStatus.REGRESSION_REQUIRED, DigitalCopyStatus.DIGITAL_ACCEPTED, DigitalCopyStatus.BLOCKED)
VIEWS = (("overview", "Overview"), ("extraction", "Extraction"), ("structure", "Structure"), ("discrepancies", "Discrepancies"), ("digital", "Digital Copy"), ("graphical", "Graphical Verification"), ("verification", "Verification"), ("acceptance", "Acceptance"), ("revision", "Revision History"), ("export", "Export / Handoff"))


def _json(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def _jobs(root):
    out=[]
    for p in sorted(root.glob("*/job.json")):
        try: out.append(load_job(p))
        except (OSError, ValueError, KeyError, TypeError): pass
    return sorted(out, key=lambda x:x.job_id)


def _payload(job):
    data=job.as_dict(); data["accepted"]=job.accepted; data["artifact_names"]=sorted(job.artifacts); data["operational_archive"]=job.metadata.get("operational_archive"); return data


def _status_class(status):
    if status==DigitalCopyStatus.DIGITAL_ACCEPTED: return "accepted"
    if status==DigitalCopyStatus.BLOCKED: return "blocked"
    if status in {DigitalCopyStatus.VERIFICATION_REQUIRED, DigitalCopyStatus.REGRESSION_REQUIRED}: return "review"
    return "active"


def _html(title, body):
    css="""<style>body{font-family:system-ui;margin:0;background:#f5f7fa;color:#18202a}header{background:#18202a;color:white;padding:16px 22px}main{max-width:1500px;margin:auto;padding:16px}.shell{display:grid;grid-template-columns:210px 1fr;gap:14px}nav,.card{background:white;border:1px solid #dce2e8;border-radius:8px}.card{padding:15px;margin-bottom:12px}nav{padding:8px;height:max-content;position:sticky;top:10px}nav a{display:block;padding:8px;color:#174ea6;text-decoration:none}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}.badge{padding:4px 8px;border-radius:999px;font-size:12px;font-weight:700}.accepted{background:#d9f5df;color:#155724}.blocked{background:#fde0e0;color:#8a1c1c}.review{background:#fff0c7;color:#765500}.active{background:#e4ecff;color:#234b9a}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:7px;border-bottom:1px solid #e5e9ee}pre,code{background:#f1f3f5;padding:2px 5px}pre{padding:10px;overflow:auto}.viewer{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:12px}.pdf{background:#20252b;padding:12px;border-radius:8px}.toolbar{color:white;display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:10px}.stage{position:relative;width:max-content;max-width:100%;margin:auto}.stage img{display:block;max-width:100%}.stage canvas{position:absolute;left:0;top:0;pointer-events:none}.evidence{border:1px solid #dce2e8;border-radius:6px;padding:8px;margin:6px 0;cursor:pointer}.small{font-size:12px;color:#65717d}.danger{border-left:4px solid #b42318}.success{border-left:4px solid #217a36}@media(max-width:900px){.shell,.viewer{grid-template-columns:1fr}nav{position:static}}</style>"""
    return "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>"+escape(title)+" — NDI</title>"+css+"</head><body><header><strong>NDI — Digital Copy Workspace</strong><span>Evidence-first · fail-closed</span></header><main>"+body+"</main></body></html>"


class DigitalCopyUI:
    def __init__(self, workspace_root: Path, runner: Runner|None=None, archiver: Archiver|None=None):
        self.workspace_root=workspace_root.resolve(); self.workspace_root.mkdir(parents=True,exist_ok=True); self.runner=runner; self.archiver=archiver

    def _job(self, job_id):
        if not job_id or Path(job_id).name!=job_id: return None
        p=self.workspace_root/job_id/"job.json"
        if p.resolve().parent.parent!=self.workspace_root or not p.is_file(): return None
        try: return load_job(p)
        except (OSError,ValueError,KeyError,TypeError): return None

    def _source(self, job):
        root=(self.workspace_root/job.job_id/"source").resolve(); p=(root/job.source.filename).resolve()
        return p if p.parent==root and p.is_file() else None

    def _artifact(self, job, name):
        value=job.artifacts.get(name)
        if not value: return None
        root=Path(job.artifact_root or "").resolve(); p=(Path(value) if Path(value).is_absolute() else root/value).resolve()
        try: p.relative_to(root)
        except ValueError: return None
        if not p.is_file(): return None
        try: return json.loads(p.read_text(encoding="utf-8"))
        except (OSError,ValueError,TypeError): return None

    def _respond(self,start,status,body,ctype="text/html; charset=utf-8"):
        start(status,[("Content-Type",ctype),("Content-Length",str(len(body)))])
        return [body if isinstance(body,bytes) else body.encode()]

    def _dashboard(self):
        cards="".join("<div class='card'><a href='/jobs/"+escape(j.job_id)+"'><h3>"+escape(j.source.filename)+"</h3></a><span class='badge "+_status_class(j.status)+"'>"+escape(j.status.value)+"</span><p>Revision: <code>"+escape(j.revision_id or "not locked")+"</code></p></div>" for j in _jobs(self.workspace_root)) or "<div class='card'>No Digital Copies yet.</div>"
        body="<h1>Digital Copies</h1><div class='card'><h2>Create Digital Copy</h2><form id='create'><input id='file' type='file' accept='application/pdf' required><input type='submit' value='Create'></form><p id='error'></p></div><div class='grid'>"+cards+"</div><script>document.getElementById('create').onsubmit=async function(e){e.preventDefault();var f=document.getElementById('file').files[0];var r=await fetch('/api/jobs',{method:'POST',headers:{'X-Filename':f.name,'Content-Type':'application/pdf'},body:f});if(r.ok)location='/jobs/'+(await r.json()).job_id;else document.getElementById('error').textContent=await r.text()}</script>"
        return _html("Digital Copies",body).encode()

    def _detail(self,job):
        ge=self._artifact(job,"graphical_evidence"); evidence=ge.get("items",[]) if isinstance(ge,dict) and isinstance(ge.get("items"),list) else []
        nodes=[]
        for name in ("canonical","canonical_document","digital_revision"):
            data=self._artifact(job,name)
            if isinstance(data,dict):
                nodes=data.get("nodes",[])
                if not nodes and isinstance(data.get("document"),dict): nodes=data["document"].get("nodes",[])
                if nodes: break
        discrepancies=[]
        for name in ("discrepancies","external_comparison","reconciliation","semantic_evaluation"):
            data=self._artifact(job,name)
            if isinstance(data,dict):
                for key in ("discrepancies","issues","conflicts","findings"):
                    if isinstance(data.get(key),list): discrepancies += data[key]
        nav="".join("<a href='#view-"+k+"'>"+label+"</a>" for k,label in VIEWS)
        ev_cards="".join("<div class='evidence' data-id='"+escape(str(e.get("evidence_id","")))+"'><b>"+escape(str(e.get("element_kind","")))+"</b> · p."+escape(str(e.get("region",{}).get("page","")))+"<br><span class='small'>"+escape(str(e.get("source_text","")))+"</span></div>" for e in evidence) or "<p class='small'>No graphical evidence recorded.</p>"
        node_rows="".join("<tr><td><button class='node' data-id='"+escape(str(n.get("node_id",n.get("id",""))))+"'>"+escape(str(n.get("node_type",n.get("type","node")))+"</button></td><td>"+escape(str(n.get("text",n.get("source_text",""))))+"</td><td>"+escape(str(n.get("source_anchor",n.get("anchor",""))))+"</td></tr>" for n in nodes) or "<tr><td colspan='3'>Canonical structure artifact is not available yet.</td></tr>"
        disc_rows="".join("<tr><td>"+escape(str(d.get("id",d.get("discrepancy_id",""))))+"</td><td>"+escape(str(d.get("status",d.get("result",""))))+"</td><td>"+escape(str(d.get("reason",d.get("message",d.get("description","")))))+"</td></tr>" for d in discrepancies) or "<tr><td colspan='3'>No persisted discrepancies.</td></tr>"
        archive=job.metadata.get("operational_archive")
        archive_text=("<p>Archive <code>"+escape(str(archive.get("archive_id","")))+"</code> · "+escape(str(archive.get("result","")))+" · "+("VALID" if archive.get("verified") else "UNVERIFIED")+"</p>") if archive else "<p class='small'>Available after DIGITAL_ACCEPTED.</p>"
        runner=("<form action='/api/jobs/"+escape(job.job_id)+"/run' method='post'><input type='submit' value='Run workflow'></form>" if self.runner else "")
        lifecycle="".join("<tr><td>"+escape(s.value)+"</td><td>"+("CURRENT" if s==job.status else "")+"</td></tr>" for s in STATES)
        ev_json=json.dumps(evidence,ensure_ascii=False); node_json=json.dumps(nodes,ensure_ascii=False); job_json=json.dumps(job.job_id)
        script="""<script>
const evidence=__EVIDENCE__, nodes=__NODES__, jobId=__JOB__;
let page=1, zoom=1; const img=document.getElementById('pdf-page'), canvas=document.getElementById('overlay'), ctx=canvas.getContext('2d');
function draw(selected){ctx.clearRect(0,0,canvas.width,canvas.height);const scale=canvas.clientWidth/(img.naturalWidth||canvas.clientWidth);evidence.forEach(e=>{const r=e.region||{};if(Number(r.page)!==page)return;const x0=Number(r.x0||0)*scale,y0=Number(r.y0||0)*scale,x1=Number(r.x1||0)*scale,y1=Number(r.y1||0)*scale;ctx.strokeStyle=String(e.evidence_id)===String(selected)?'#ff8800':'#d22';ctx.lineWidth=2;ctx.strokeRect(x0,y0,x1-x0,y1-y0);});}
function render(){img.src='/jobs/'+jobId+'/page/'+page+'.png';document.getElementById('page').value=page;document.getElementById('zoom').textContent=Math.round(zoom*100)+'%';}
img.onload=()=>{canvas.width=img.clientWidth;canvas.height=img.clientHeight;draw();};
document.querySelectorAll('.evidence').forEach(x=>x.onclick=()=>{const e=evidence.find(v=>String(v.evidence_id)===x.dataset.id);if(e){page=Number(e.region?.page||1);render();setTimeout(()=>draw(x.dataset.id),100);}});
document.querySelectorAll('.node').forEach(x=>x.onclick=()=>{const n=nodes.find(v=>String(v.node_id||v.id)===x.dataset.id),a=n?.source_anchor||n?.anchor;if(a?.page){page=Number(a.page);render();}});
document.getElementById('prev').onclick=()=>{if(page>1){page--;render();}};document.getElementById('next').onclick=()=>{page++;render();};document.getElementById('page').onchange=e=>{page=Math.max(1,Number(e.target.value));render();};document.getElementById('zoom-in').onclick=()=>{zoom=Math.min(3,zoom+.25);img.style.width=(zoom*100)+'%';draw();};document.getElementById('zoom-out').onclick=()=>{zoom=Math.max(.5,zoom-.25);img.style.width=(zoom*100)+'%';draw();};document.getElementById('fit').onclick=()=>{zoom=1;img.style.width='auto';render();};render();
</script>""".replace("__EVIDENCE__",ev_json).replace("__NODES__",node_json).replace("__JOB__",job_json)
        body="<div class='shell'><nav><a href='/'>← Digital Copies</a>"+nav+"</nav><section><div class='card'><h1>"+escape(job.source.filename)+"</h1><span class='badge "+_status_class(job.status)+"'>"+escape(job.status.value)+"</span><p>Document <code>"+escape(job.document_id or "not identified")+"</code> · Revision <code>"+escape(job.revision_id or "not locked")+"</code><br>Source SHA-256 <code>"+escape(job.source.sha256)+"</code></p>"+runner+"</div>"
        body += "<section id='view-overview' class='card'><h2>Overview</h2><div class='grid'><div><b>"+str(len(evidence))+"</b> graphical evidence</div><div><b>"+str(len(nodes))+"</b> canonical nodes</div><div><b>"+str(len(discrepancies))+"</b> discrepancies</div><div><b>"+("YES" if job.accepted else "NO")+"</b> DIGITAL_ACCEPTED</div></div></section>"
        body += "<section id='view-extraction' class='card'><h2>Extraction</h2><ul>"+"".join("<li><code>"+escape(k)+"</code></li>" for k in sorted(job.artifacts))+"</ul></section>"
        body += "<section id='view-structure' class='card'><h2>Structure</h2><table><tr><th>Node</th><th>Text</th><th>Anchor</th></tr>"+node_rows+"</table></section>"
        body += "<section id='view-discrepancies' class='card'><h2>Discrepancies</h2><table><tr><th>ID</th><th>Status</th><th>Finding</th></tr>"+disc_rows+"</table></section>"
        body += "<section id='view-digital' class='card'><h2>Digital Copy</h2><p>Engine-derived representation; no manual acceptance control.</p><pre>"+escape(json.dumps(_payload(job),ensure_ascii=False,sort_keys=True,indent=2))+"</pre></section>"
        body += "<section id='view-graphical' class='card'><h2>Graphical Verification</h2><div class='viewer'><div class='pdf'><div class='toolbar'><button id='prev'>◀</button><span>Page <input id='page' value='1' type='number' min='1' style='width:50px'></span><button id='next'>▶</button><button id='zoom-out'>−</button><span id='zoom'>100%</span><button id='zoom-in'>+</button><button id='fit'>Fit</button><a href='/jobs/"+escape(job.job_id)+"/source' target='_blank' style='color:white'>Open original PDF</a></div><div class='stage'><img id='pdf-page' alt='Rendered source PDF page'><canvas id='overlay'></canvas></div></div><aside><p class='small'>Rendered directly from the immutable source PDF. Evidence overlays use stored page/bbox coordinates.</p>"+ev_cards+"</aside></div></section>"
        body += "<section id='view-verification' class='card'><h2>Verification</h2><pre>"+escape(json.dumps(job.metadata.get("verification",{}),ensure_ascii=False,sort_keys=True,indent=2))+"</pre></section>"
        body += "<section id='view-acceptance' class='card "+("success" if job.accepted else "danger")+"'><h2>Acceptance</h2><p><b>"+("DIGITAL_ACCEPTED" if job.accepted else "NOT ACCEPTED")+"</b></p><p>Derived from engine gates; cannot be manually set.</p><ul>"+"".join("<li>"+escape(x)+"</li>" for x in job.blockers) or "<li>None</li>"+"</ul></section>"
        body += "<section id='view-revision' class='card'><h2>Revision History</h2><p>Revision <code>"+escape(job.revision_id or "not locked")+"</code><br>Source SHA-256 <code>"+escape(job.source.sha256)+"</code></p>"+archive_text+"</section>"
        body += "<section id='view-export' class='card'><h2>Export / Handoff</h2><p>Exact accepted revision, source SHA-256, manifest and evidence hashes are the handoff identity.</p>"+archive_text+"</section>"
        body += "</section></div>"+script
        return _html("Digital Copy",body).encode()

    def __call__(self,environ,start_response):
        method=environ.get("REQUEST_METHOD","GET").upper(); path=unquote(environ.get("PATH_INFO","/"))
        if method=="GET" and path=="/": return self._respond(start_response,"200 OK",_html("Digital Copies",self._dashboard()))
        if method=="GET" and path.startswith("/jobs/"):
            parts=path.strip("/").split("/"); job=self._job(parts[1]) if len(parts)>1 else None
            if job is None:return self._respond(start_response,"404 Not Found",_html("Not found","<h1>Job not found</h1>"))
            if len(parts)==2:return self._respond(start_response,"200 OK",self._detail(job))
            if len(parts)==3 and parts[2]=="source":
                source=self._source(job)
                if source is None:return self._respond(start_response,"404 Not Found",b"Not found","text/plain; charset=utf-8")
                return self._respond(start_response,"200 OK",source.read_bytes(),"application/pdf")
            if len(parts)==4 and parts[2]=="page" and parts[3].endswith(".png"):
                try:n=int(parts[3][:-4])
                except ValueError:n=0
                source=self._source(job)
                if source is None or n<1:return self._respond(start_response,"404 Not Found",b"Not found","text/plain; charset=utf-8")
                try:
                    with fitz.open(source) as doc:
                        if n>len(doc):return self._respond(start_response,"404 Not Found",b"Page not found","text/plain; charset=utf-8")
                        pix=doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
                        return self._respond(start_response,"200 OK",pix.tobytes("png"),"image/png")
                except (OSError,RuntimeError,ValueError):return self._respond(start_response,"422 Unprocessable Entity",b"PDF render failed","text/plain; charset=utf-8")
        if method=="GET" and path=="/api/jobs":return self._respond(start_response,"200 OK",_json([_payload(j) for j in _jobs(self.workspace_root)]),"application/json")
        if method=="GET" and path.startswith("/api/jobs/"):
            job=self._job(path.split("/")[3])
            if job is None:return self._respond(start_response,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
            return self._respond(start_response,"200 OK",_json(_payload(job)),"application/json")
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
            return self._respond(start_response,"201 Created",_json(_payload(job)),"application/json")
        if method=="POST" and path.startswith("/api/jobs/") and path.endswith("/run"):
            job=self._job(path.split("/")[3])
            if job is None:return self._respond(start_response,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
            if self.runner is None:return self._respond(start_response,"409 Conflict",_json({"error":"runner_not_configured"}),"application/json")
            try:result=self.runner(job);persist_job_file(result,self.workspace_root/result.job_id/"job.json")
            except Exception as exc:return self._respond(start_response,"409 Conflict",_json({"error":type(exc).__name__,"detail":str(exc)}),"application/json")
            return self._respond(start_response,"200 OK",_json(_payload(result)),"application/json")
        if method=="POST" and path.startswith("/api/jobs/") and path.endswith("/archive"):
            job=self._job(path.split("/")[3])
            if job is None:return self._respond(start_response,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
            if not job.accepted:return self._respond(start_response,"409 Conflict",_json({"error":"job_not_accepted"}),"application/json")
            if self.archiver is None:return self._respond(start_response,"409 Conflict",_json({"error":"archiver_not_configured"}),"application/json")
            try:result=self.archiver(job);persist_job_file(result,self.workspace_root/result.job_id/"job.json")
            except Exception as exc:return self._respond(start_response,"409 Conflict",_json({"error":type(exc).__name__,"detail":str(exc)}),"application/json")
            return self._respond(start_response,"200 OK",_json(_payload(result)),"application/json")
        return self._respond(start_response,"404 Not Found",_json({"error":"not_found"}),"application/json")


def main():
    import argparse
    p=argparse.ArgumentParser(description="NDI Digital Copy UI");p.add_argument("--workspace",type=Path,default=Path(".ndi-workspace"));p.add_argument("--host",default="127.0.0.1");p.add_argument("--port",type=int,default=8000);a=p.parse_args()
    with make_server(a.host,a.port,DigitalCopyUI(a.workspace)) as server: print(f"NDI Digital Copy UI: http://{a.host}:{a.port}");server.serve_forever()
