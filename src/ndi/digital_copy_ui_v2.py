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

Runner=Callable[[DigitalCopyJob],DigitalCopyJob]
Archiver=Callable[[DigitalCopyJob],DigitalCopyJob]
VIEWS=("Overview","Extraction","Structure","Discrepancies","Digital Copy","Graphical Verification","Verification","Acceptance","Revision History","Export / Handoff")
STATES=(DigitalCopyStatus.NEW,DigitalCopyStatus.IDENTIFYING,DigitalCopyStatus.EXTRACTING,DigitalCopyStatus.RECONCILING,DigitalCopyStatus.DIGITALIZING,DigitalCopyStatus.GRAPHICAL_VERIFICATION,DigitalCopyStatus.VERIFICATION_REQUIRED,DigitalCopyStatus.REGRESSION_REQUIRED,DigitalCopyStatus.DIGITAL_ACCEPTED,DigitalCopyStatus.BLOCKED)


def _json(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()

def _cls(s): return "accepted" if s==DigitalCopyStatus.DIGITAL_ACCEPTED else "blocked" if s==DigitalCopyStatus.BLOCKED else "review" if s in (DigitalCopyStatus.VERIFICATION_REQUIRED,DigitalCopyStatus.REGRESSION_REQUIRED) else "active"

def _jobs(root):
    out=[]
    for p in sorted(root.glob("*/job.json")):
        try: out.append(load_job(p))
        except (OSError,ValueError,KeyError,TypeError): pass
    return out

def _page(title,body):
    css="body{font-family:system-ui;margin:0;background:#f5f7fa;color:#18202a}header{background:#18202a;color:#fff;padding:16px 22px}main{max-width:1500px;margin:auto;padding:16px}.shell{display:grid;grid-template-columns:210px 1fr;gap:14px}nav,.card{background:#fff;border:1px solid #dce2e8;border-radius:8px}.card{padding:15px;margin-bottom:12px}nav{padding:8px;height:max-content;position:sticky;top:10px}nav a{display:block;padding:8px;color:#174ea6;text-decoration:none}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}.badge{padding:4px 8px;border-radius:999px;font-size:12px;font-weight:700}.accepted{background:#d9f5df;color:#155724}.blocked{background:#fde0e0;color:#8a1c1c}.review{background:#fff0c7;color:#765500}.active{background:#e4ecff;color:#234b9a}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:7px;border-bottom:1px solid #e5e9ee}pre,code{background:#f1f3f5;padding:2px 5px}pre{padding:10px;overflow:auto}.viewer{display:grid;grid-template-columns:minmax(0,1fr) 320px;gap:12px}.pdf{background:#20252b;padding:12px;border-radius:8px}.toolbar{color:#fff;display:flex;gap:6px;align-items:center;flex-wrap:wrap}.stage{position:relative;width:max-content;max-width:100%;margin:10px auto}.stage img{display:block;max-width:100%}.stage canvas{position:absolute;left:0;top:0}.evidence{border:1px solid #dce2e8;border-radius:6px;padding:8px;margin:6px 0;cursor:pointer}.small{font-size:12px;color:#65717d}.danger{border-left:4px solid #b42318}.success{border-left:4px solid #217a36}@media(max-width:900px){.shell,.viewer{grid-template-columns:1fr}nav{position:static}}"
    return ("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>"+escape(title)+" — NDI</title><style>"+css+"</style></head><body><header><b>NDI — Digital Copy Workspace</b><span>Evidence-first · fail-closed</span></header><main>"+body+"</main></body></html>").encode()

class DigitalCopyUI:
    def __init__(self,workspace_root:Path,runner:Runner|None=None,archiver:Archiver|None=None):
        self.workspace_root=workspace_root.resolve();self.workspace_root.mkdir(parents=True,exist_ok=True);self.runner=runner;self.archiver=archiver
    def _job(self,jid):
        if not jid or Path(jid).name!=jid:return None
        p=self.workspace_root/jid/"job.json"
        try:return load_job(p) if p.resolve().parent.parent==self.workspace_root and p.is_file() else None
        except (OSError,ValueError,KeyError,TypeError):return None
    def _source(self,j):
        root=(self.workspace_root/j.job_id/"source").resolve();p=(root/j.source.filename).resolve();return p if p.parent==root and p.is_file() else None
    def _artifact(self,j,name):
        v=j.artifacts.get(name)
        if not v:return None
        root=Path(j.artifact_root or "").resolve();p=(Path(v) if Path(v).is_absolute() else root/v).resolve()
        try:p.relative_to(root)
        except ValueError:return None
        try:return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None
        except (OSError,ValueError,TypeError):return None
    def _resp(self,start,status,body,ctype="text/html; charset=utf-8"):
        if not isinstance(body,bytes):body=body.encode();start(status,[("Content-Type",ctype),("Content-Length",str(len(body)))])
        else:start(status,[("Content-Type",ctype),("Content-Length",str(len(body)))])
        return [body]
    def _dash(self):
        cards="".join("<div class='card'><a href='/jobs/"+escape(j.job_id)+"'><h3>"+escape(j.source.filename)+"</h3></a><span class='badge "+_cls(j.status)+"'>"+escape(j.status.value)+"</span><p>Revision: <code>"+escape(j.revision_id or "not locked")+"</code></p></div>" for j in _jobs(self.workspace_root)) or "<div class='card'>No Digital Copies yet.</div>"
        return _page("Digital Copies","<h1>Digital Copies</h1><div class='card'><h2>Create Digital Copy</h2><form id='f'><input id='file' type='file' accept='application/pdf' required><input type='submit' value='Create'></form><p id='err'></p></div><div class='grid'>"+cards+"</div><script>f.onsubmit=async e=>{e.preventDefault();let x=file.files[0],r=await fetch('/api/jobs',{method:'POST',headers:{'X-Filename':x.name},body:x});if(r.ok)location='/jobs/'+(await r.json()).job_id;else err.textContent=await r.text()}</script>")
    def _detail(self,j):
        ge=self._artifact(j,"graphical_evidence");ev=ge.get("items",[]) if isinstance(ge,dict) and isinstance(ge.get("items"),list) else []
        nodes=[]
        for name in ("canonical","canonical_document","digital_revision"):
            d=self._artifact(j,name)
            if isinstance(d,dict):
                nodes=d.get("nodes",[])
                if not nodes and isinstance(d.get("document"),dict):nodes=d["document"].get("nodes",[])
                if nodes:break
        ds=[]
        for name in ("discrepancies","external_comparison","reconciliation"):
            d=self._artifact(j,name)
            if isinstance(d,dict):
                for k in ("discrepancies","issues","conflicts","findings"):
                    if isinstance(d.get(k),list):ds+=d[k]
        nav="".join("<a href='#v"+str(i)+"'>"+x+"</a>" for i,x in enumerate(VIEWS))
        evui="".join("<div class='evidence' data-id='"+escape(str(e.get("evidence_id","")))+"'><b>"+escape(str(e.get("element_kind","")))+"</b> · p."+escape(str(e.get("region",{}).get("page","")))+"<br>"+escape(str(e.get("source_text","")))+"</div>" for e in ev) or "<p class='small'>No graphical evidence recorded.</p>"
        nrows="".join("<tr><td>"+escape(str(n.get("node_type",n.get("type","node"))))+"</td><td>"+escape(str(n.get("text",n.get("source_text",""))))+"</td><td>"+escape(str(n.get("source_anchor",n.get("anchor",""))))+"</td></tr>" for n in nodes) or "<tr><td colspan='3'>Canonical structure artifact is not available yet.</td></tr>"
        drows="".join("<tr><td>"+escape(str(x.get("id",x.get("discrepancy_id",""))))+"</td><td>"+escape(str(x.get("status",x.get("result",""))))+"</td><td>"+escape(str(x.get("reason",x.get("message",x.get("description","")))))+"</td></tr>" for x in ds) or "<tr><td colspan='3'>No persisted discrepancies.</td></tr>"
        runner="<form action='/api/jobs/"+escape(j.job_id)+"/run' method='post'><input type='submit' value='Run workflow'></form>" if self.runner else ""
        archive=j.metadata.get("operational_archive");arch="<p>Archive <code>"+escape(str(archive.get("archive_id","")))+"</code> · "+("VALID" if archive.get("verified") else "UNVERIFIED")+"</p>" if archive else "<p class='small'>Available after DIGITAL_ACCEPTED.</p>"
        body="<div class='shell'><nav><a href='/'>← Digital Copies</a>"+nav+"</nav><section><div class='card'><h1>"+escape(j.source.filename)+"</h1><span class='badge "+_cls(j.status)+"'>"+escape(j.status.value)+"</span><p>Document <code>"+escape(j.document_id or "not identified")+"</code> · Revision <code>"+escape(j.revision_id or "not locked")+"</code><br>SHA-256 <code>"+escape(j.source.sha256)+"</code></p>"+runner+"</div>"
        body+="<section id='v0' class='card'><h2>Overview</h2><div class='grid'><b>"+str(len(ev))+" graphical evidence</b><b>"+str(len(nodes))+" canonical nodes</b><b>"+str(len(ds))+" discrepancies</b><b>"+("YES" if j.accepted else "NO")+" DIGITAL_ACCEPTED</b></div></section>"
        body+="<section id='v1' class='card'><h2>Extraction</h2><ul>"+"".join("<li><code>"+escape(k)+"</code></li>" for k in sorted(j.artifacts))+"</ul></section>"
        body+="<section id='v2' class='card'><h2>Structure</h2><table><tr><th>Type</th><th>Text</th><th>Anchor</th></tr>"+nrows+"</table></section>"
        body+="<section id='v3' class='card'><h2>Discrepancies</h2><table><tr><th>ID</th><th>Status</th><th>Finding</th></tr>"+drows+"</table></section>"
        body+="<section id='v4' class='card'><h2>Digital Copy</h2><p>Engine-derived; no manual acceptance control.</p><pre>"+escape(json.dumps(j.as_dict(),ensure_ascii=False,sort_keys=True,indent=2))+"</pre></section>"
        body+="<section id='v5' class='card'><h2>Graphical Verification</h2><div class='viewer'><div class='pdf'><div class='toolbar'><button id='prev'>◀</button><input id='pg' value='1' type='number' min='1' style='width:45px'><button id='next'>▶</button><button id='zin'>+</button><button id='zout'>−</button><span id='zs'>100%</span><a style='color:white' target='_blank' href='/jobs/"+escape(j.job_id)+"/source'>Open original PDF</a></div><div class='stage'><img id='pdf'><canvas id='cv'></canvas></div></div><aside><p class='small'>Rendered directly from immutable source PDF. Stored page/bbox evidence is overlaid without rewriting the source.</p>"+evui+"</aside></div></section>"
        body+="<section id='v6' class='card'><h2>Verification</h2><pre>"+escape(json.dumps(j.metadata.get("verification",{}),ensure_ascii=False,sort_keys=True,indent=2))+"</pre></section>"
        body+="<section id='v7' class='card "+("success" if j.accepted else "danger")+"'><h2>Acceptance</h2><b>"+("DIGITAL_ACCEPTED" if j.accepted else "NOT ACCEPTED")+"</b><p>Derived from engine gates; not manually selectable.</p><ul>"+"".join("<li>"+escape(x)+"</li>" for x in j.blockers)+"</ul></section>"
        body+="<section id='v8' class='card'><h2>Revision History</h2><p>Revision <code>"+escape(j.revision_id or "not locked")+"</code><br>Source SHA-256 <code>"+escape(j.source.sha256)+"</code></p>"+arch+"</section>"
        body+="<section id='v9' class='card'><h2>Export / Handoff</h2><p>Exact revision, source hash, manifest and evidence hashes define the handoff.</p>"+arch+"</section></section></div>"
        js="""<script>const E=__E__,J='__J__';let p=1,z=1;const i=document.getElementById('pdf'),c=document.getElementById('cv'),x=c.getContext('2d');function r(){i.src='/jobs/'+J+'/page/'+p+'.png';}i.onload=()=>{c.width=i.clientWidth;c.height=i.clientHeight;x.clearRect(0,0,c.width,c.height);const s=c.clientWidth/i.naturalWidth;E.forEach(e=>{let q=e.region||{};if(Number(q.page)==p){x.strokeStyle='#d22';x.strokeRect(Number(q.x0||0)*s,Number(q.y0||0)*s,(Number(q.x1||0)-Number(q.x0||0))*s,(Number(q.y1||0)-Number(q.y0||0))*s)}})};prev.onclick=()=>{if(p>1){p--;r()}};next.onclick=()=>{p++;r()};pg.onchange=e=>{p=Math.max(1,Number(e.target.value));r()};zin.onclick=()=>{z=Math.min(2,z+.25);i.style.width=(z*100)+'%'};zout.onclick=()=>{z=Math.max(.5,z-.25);i.style.width=(z*100)+'%'};r();</script>""".replace("__E__",json.dumps(ev,ensure_ascii=False)).replace("__J__",j.job_id)
        return _page("Digital Copy",body+js)
    def __call__(self,environ,start):
        m=environ.get("REQUEST_METHOD","GET").upper();path=unquote(environ.get("PATH_INFO","/"))
        if m=="GET" and path=="/":return self._resp(start,"200 OK",self._dash())
        if m=="GET" and path.startswith("/jobs/"):
            a=path.strip('/').split('/');j=self._job(a[1]) if len(a)>1 else None
            if not j:return self._resp(start,"404 Not Found",b"Not found","text/plain")
            if len(a)==2:return self._resp(start,"200 OK",self._detail(j))
            if len(a)==3 and a[2]=="source":
                s=self._source(j);return self._resp(start,"200 OK",s.read_bytes(),"application/pdf") if s else self._resp(start,"404 Not Found",b"Not found","text/plain")
            if len(a)==4 and a[2]=="page" and a[3].endswith('.png'):
                s=self._source(j)
                try:
                    n=int(a[3][:-4]);doc=fitz.open(s)
                    if n<1 or n>len(doc):doc.close();return self._resp(start,"404 Not Found",b"Page not found","text/plain")
                    pix=doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False);doc.close();return self._resp(start,"200 OK",pix.tobytes('png'),"image/png")
                except (OSError,RuntimeError,ValueError):return self._resp(start,"422 Unprocessable Entity",b"PDF render failed","text/plain")
        if m=="GET" and path=="/api/jobs":return self._resp(start,"200 OK",_json([self._data(j) for j in _jobs(self.workspace_root)]),"application/json")
        if m=="GET" and path.startswith("/api/jobs/"):
            j=self._job(path.split('/')[3]);return self._resp(start,"200 OK",_json(self._data(j)),"application/json") if j else self._resp(start,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
        if m=="POST" and path=="/api/jobs":
            try:n=int(environ.get('CONTENT_LENGTH') or 0)
            except ValueError:n=0
            name=Path(environ.get('HTTP_X_FILENAME','source.pdf')).name
            if n<=0 or n>100*1024*1024:return self._resp(start,"400 Bad Request",_json({"error":"invalid_source_size"}),"application/json")
            if not name.lower().endswith('.pdf'):return self._resp(start,"400 Bad Request",_json({"error":"source_must_be_pdf"}),"application/json")
            jid=uuid4().hex;inc=self.workspace_root/'.incoming'/jid/name;inc.parent.mkdir(parents=True);inc.write_bytes(environ['wsgi.input'].read(n))
            try:
                j=new_job(jid,DigitalCopySource.from_file(inc));root=self.workspace_root/jid;persist_package(j,root);j.source=DigitalCopySource(str((root/'source'/name).resolve()),name,j.source.sha256);j.artifact_root=str(root);persist_job_file(j,root/'job.json')
            finally:inc.unlink(missing_ok=True)
            return self._resp(start,"201 Created",_json(self._data(j)),"application/json")
        if m=="POST" and path.startswith('/api/jobs/') and path.endswith('/run'):
            j=self._job(path.split('/')[3])
            if not j:return self._resp(start,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
            if not self.runner:return self._resp(start,"409 Conflict",_json({"error":"runner_not_configured"}),"application/json")
            try:r=self.runner(j);persist_job_file(r,self.workspace_root/r.job_id/'job.json');return self._resp(start,"200 OK",_json(self._data(r)),"application/json")
            except Exception as e:return self._resp(start,"409 Conflict",_json({"error":type(e).__name__,"detail":str(e)}),"application/json")
        if m=="POST" and path.startswith('/api/jobs/') and path.endswith('/archive'):
            j=self._job(path.split('/')[3])
            if not j:return self._resp(start,"404 Not Found",_json({"error":"job_not_found"}),"application/json")
            if not j.accepted:return self._resp(start,"409 Conflict",_json({"error":"job_not_accepted"}),"application/json")
            if not self.archiver:return self._resp(start,"409 Conflict",_json({"error":"archiver_not_configured"}),"application/json")
            try:r=self.archiver(j);persist_job_file(r,self.workspace_root/r.job_id/'job.json');return self._resp(start,"200 OK",_json(self._data(r)),"application/json")
            except Exception as e:return self._resp(start,"409 Conflict",_json({"error":type(e).__name__,"detail":str(e)}),"application/json")
        return self._resp(start,"404 Not Found",_json({"error":"not_found"}),"application/json")
    def _data(self,j):
        d=j.as_dict();d['accepted']=j.accepted;d['artifact_names']=sorted(j.artifacts);d['operational_archive']=j.metadata.get('operational_archive');return d

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,default=Path('.ndi-workspace'));p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=8000);a=p.parse_args()
    with make_server(a.host,a.port,DigitalCopyUI(a.workspace)) as s:s.serve_forever()
