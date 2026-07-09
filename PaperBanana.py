#!/usr/bin/env python3
"""
PaperBanana All-in-One — 雙擊執行，一鍵啟動
=============================================
使用方式：雙擊此檔案，或執行 python PaperBanana.py
首次使用會要求輸入 API Key，之後自動記憶。
"""
import os, sys, webbrowser, json, asyncio, traceback
from pathlib import Path
from datetime import datetime

# ====== API Key 管理（內嵌，首次執行後存檔） ======
KEY_CONTENT = ""  # ← 你的 OpenRouter API Key 可貼在這裡（選填）

KEY_FILE = Path(__file__).parent / ".paperbanana_key"

def get_key():
    if KEY_CONTENT and len(KEY_CONTENT) > 20:
        return KEY_CONTENT
    if KEY_FILE.exists():
        k = KEY_FILE.read_text().strip()
        if len(k) > 20:
            return k
    print()
    print("=" * 50)
    print("  PaperBanana - First Time Setup")
    print("=" * 50)
    print()
    print("  Enter your OpenRouter API Key:")
    print("  (https://openrouter.ai/keys)")
    print()
    k = input("  API Key: ").strip()
    if k and len(k) > 20:
        KEY_FILE.write_text(k)
        print("  Key saved!")
        return k
    print("  Invalid key")
    return ""

# ====== 路徑設定 ======
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "pb_output"
os.chdir(str(BASE_DIR))
OUTPUT_DIR.mkdir(exist_ok=True)
os.environ["PATH"] = r"C:\Program Files\Gtk-Runtime\bin;" + os.environ.get("PATH", "")

# ====== Flask + PaperBanana ======
from flask import Flask, request, jsonify, Response
from paperbanana import PaperBananaPipeline, GenerationInput, GenerationOutput
from paperbanana.core.config import Settings

app = Flask(__name__)

def do_gen(desc: str, iters: int) -> dict:
    key = get_key()
    if not key or len(key) < 20:
        return {"success": False, "error": "API Key not set"}
    settings = Settings(
        vlm_provider="openrouter", vlm_model="google/gemini-2.5-flash",
        image_provider="openrouter_imagen", image_model="google/gemini-3.1-flash-lite-image",
        openrouter_api_key=key, refinement_iterations=iters,
        output_dir=str(OUTPUT_DIR / "runs"), save_prompts=False,
        optimize_inputs=False, auto_refine=False, num_candidates=1,
    )
    gi = GenerationInput(source_context=desc, communicative_intent=f"Figure: {desc[:80]}", diagram_type="methodology")
    try:
        out = asyncio.run(PaperBananaPipeline(settings=settings).generate(input=gi))
        p = Path(out.image_path) if out.image_path else None
        rel = None
        if p and p.exists() or (p := Path.cwd() / p) and p.exists():
            rel = str(p.relative_to(OUTPUT_DIR)).replace("\\", "/")
        if not rel and out.vector_svg_path:
            p2 = Path(out.vector_svg_path)
            rel = str(p2.relative_to(OUTPUT_DIR)).replace("\\", "/") if p2.exists() else None
        safe = "".join(c if c.isascii() and c.isalnum() else "_" for c in desc[:30]).strip("_") or "figure"
        name = f"{safe}_{datetime.now():%Y%m%d_%H%M%S}.png"
        return {"success": True, "output_rel": rel, "ext": "png" if rel else None, "name": name,
                "iters": len(out.iterations or []), "desc": (out.description or "")[:200]}
    except Exception as e:
        return {"success": False, "error": traceback.format_exc()}

@app.route("/")
def index():
    return HTML

@app.route("/api/generate", methods=["POST"])
def gen():
    d = request.get_json(force=True)
    desc = (d.get("description") or "").strip()
    if not desc:
        return jsonify({"success": False, "error": "Enter description"})
    return jsonify(do_gen(desc, max(1, min(10, int(d.get("iterations", 2))))))

@app.route("/output/<path:fn>")
def serve(fn):
    p = OUTPUT_DIR / fn
    if p.exists():
        return Response(p.read_bytes(), mimetype="image/svg+xml" if ".svg" in fn.lower() else "image/png",
                        headers={"Content-Disposition": f'attachment; filename="{request.args.get("name") or p.name}"'})
    return "Not found", 404

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PaperBanana</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;display:flex;justify-content:center;padding:20px}
.container{max-width:1000px;width:100%}
h1{text-align:center;padding:30px 0;font-size:28px;background:linear-gradient(135deg,#38bdf8,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.card{background:#1e293b;border-radius:16px;border:1px solid #334155;padding:24px;margin-bottom:20px}
.card h2{font-size:16px;color:#94a3b8;margin-bottom:12px}
textarea{width:100%;min-height:140px;padding:14px;background:#0f172a;border:1px solid #334155;border-radius:10px;font-size:15px;color:#e2e8f0;resize:vertical;font-family:inherit}
textarea:focus{outline:none;border-color:#6366f1}
.param{display:inline-block;margin:12px 16px 0 0}
.param label{font-size:13px;color:#64748b;display:block;margin-bottom:4px}
.param input{width:100px;padding:8px;background:#0f172a;border:1px solid #334155;border-radius:8px;font-size:14px;color:#e2e8f0}
.btn-row{margin-top:16px;display:flex;gap:12px}
button,.dl-btn{padding:10px 28px;border:none;border-radius:10px;font-size:15px;font-weight:600;cursor:pointer;text-decoration:none;display:inline-block}
.btn-pri{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff}
.btn-pri:disabled{opacity:.5;cursor:default}
.btn-sec{background:#334155;color:#94a3b8}
.dl-btn{background:#059669;color:#fff}
.spinner{display:none;width:20px;height:20px;border:3px solid rgba(255,255,255,.2);border-top-color:#fff;border-radius:50%;animation:s .6s linear infinite;margin:0 auto}
@keyframes s{to{transform:rotate(360deg)}}
.hidden{display:none}
#prev img{max-width:100%;border-radius:12px;border:1px solid #334155}
#info{margin-top:12px;font-size:14px;color:#94a3b8}
#info span{background:#0f172a;padding:4px 12px;border-radius:8px;border:1px solid #334155;margin-right:8px}
#err{color:#fca5a5;background:#450a0a;border:1px solid #991b1b;padding:12px;border-radius:10px;margin-top:12px;font-size:13px;white-space:pre-wrap}
.place{border:2px dashed #334155;border-radius:12px;padding:60px 20px;text-align:center;color:#475569}
.st{display:none;margin-top:12px;padding:10px;background:#0f172a;border:1px solid #334155;border-radius:8px;font-size:13px;color:#64748b}
.st .bar{height:4px;background:#1e293b;border-radius:2px;margin-top:8px;overflow:hidden}
.st .fill{height:100%;width:0;background:linear-gradient(90deg,#6366f1,#8b5cf6);border-radius:2px;transition:width .5s}
</style>
</head>
<body>
<div class="container">
<h1>🍌 PaperBanana</h1>
<div class="card">
<h2>Describe your diagram (English)</h2>
<textarea id="desc">We propose a novel transformer with multi-head attention, feed-forward network, and classification head.</textarea>
<div class="param"><label>Refine</label><input type="number" id="iter" value="2" min="1" max="10"></div>
<div class="btn-row">
<button class="btn-pri" id="go"><span id="bt">🍌 Generate</span><div class="spinner" id="sp"></div></button>
<button class="btn-sec" id="cl">Clear</button>
</div>
<div class="st" id="st"><span id="stxt">Ready</span><div class="bar"><div class="fill" id="fill"></div></div></div>
</div>
<div class="card hidden" id="res">
<h2>Result</h2>
<div id="prev" class="place"><p>Generated image will appear here</p></div>
<div id="info"></div>
<div class="btn-row" id="dl"></div>
<div id="err" class="hidden"></div>
</div>
</div>
<script>
document.getElementById('go').onclick=async()=>{
const d=document.getElementById('desc').value.trim();if(!d)return alert('Enter description');
const b=document.getElementById('go'),bt=document.getElementById('bt'),sp=document.getElementById('sp');
const r=document.getElementById('res'),p=document.getElementById('prev'),e=document.getElementById('err');
const i=document.getElementById('info'),dl=document.getElementById('dl'),st=document.getElementById('st');
const stx=document.getElementById('stxt'),f=document.getElementById('fill');
b.disabled=1;bt.textContent='Generating...';sp.style.display='block';
r.classList.add('hidden');e.classList.add('hidden');st.style.display='block';
stx.textContent='Generating (40-60 sec)...';f.style.width='20%';
try{
const x=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({description:d,iterations:+document.getElementById('iter').value||2})});
f.style.width='70%';stx.textContent='Processing...';
if(!x.ok)throw Error(await x.text());
const dt=await x.json();r.classList.remove('hidden');f.style.width='100%';
if(dt.success){
p.innerHTML=dt.output_rel?'<img src="/output/'+dt.output_rel+'">':'<p>Done</p>';
i.innerHTML='<span>Iterations: '+(dt.iters??'N/A')+'</span>'+(dt.desc?'<span>'+dt.desc.slice(0,50)+'...</span>':'');
var h='';if(dt.output_rel)h+='<a class="dl-btn" href="/output/'+dt.output_rel+'?name='+encodeURIComponent(dt.name)+'" download="'+dt.name+'">Download '+(dt.ext==='svg'?'SVG':'PNG')+'</a>';
dl.innerHTML=h;stx.textContent='Done!';
}else{p.innerHTML='<p>Failed</p>';e.textContent=dt.error;e.classList.remove('hidden');stx.textContent='Failed';}
}catch(e){r.classList.remove('hidden');p.innerHTML='<p>Error</p>';e.textContent=e+'';e.classList.remove('hidden');stx.textContent='Error';}
finally{b.disabled=0;bt.textContent='Generate';sp.style.display='none';}
};
document.getElementById('cl').onclick=()=>{document.getElementById('desc').value='';document.getElementById('res').classList.add('hidden');document.getElementById('err').classList.add('hidden');document.getElementById('st').style.display='none';};
</script>
</body>
</html>"""

if __name__ == "__main__":
    key = get_key()
    if not key:
        input("Press Enter to exit...")
        sys.exit(1)
    print(f"Starting PaperBanana at http://localhost:5051")
    webbrowser.open("http://localhost:5051")
    app.run(host="0.0.0.0", port=5051, threaded=True)
