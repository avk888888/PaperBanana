#!/usr/bin/env python3
"""PaperBanana - AutoFigure Web Interface"""
import os, sys, json, webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "pb_output"
os.chdir(str(BASE_DIR))
OUTPUT_DIR.mkdir(exist_ok=True)

KEY_FILE = BASE_DIR / ".paperbanana_key"

def get_key():
    if KEY_FILE.exists():
        k = KEY_FILE.read_text().strip()
        if len(k) > 20:
            return k
    k = os.environ.get("OPENROUTER_API_KEY", "")
    if len(k) > 20:
        return k
    print("\nFirst time setup - Enter your OpenRouter API Key:")
    print("(https://openrouter.ai/keys)\n")
    k = input("API Key: ").strip()
    if k and len(k) > 20:
        KEY_FILE.write_text(k)
        return k
    return ""

from flask import Flask, request, jsonify
from autofigure import AutoFigureAgent, Config

app = Flask(__name__)

def do_gen(desc, iters):
    key = get_key()
    if not key or len(key) < 20:
        return {"success": False, "error": "API Key not set"}
    try:
        config = Config(generation_api_key=key, generation_provider="openrouter",
                        refinement_iterations=iters, output_dir=str(OUTPUT_DIR / "runs"))
        agent = AutoFigureAgent(config)
        result = agent.generate(description=desc, max_iterations=iters)
        if result.success:
            return {"success": True, "iters": iters}
        return {"success": False, "error": result.error or "Failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route("/")
def index():
    return open(str(BASE_DIR / "index.html")).read() if (BASE_DIR / "index.html").exists() else "<h1>PaperBanana</h1>"

@app.route("/api/generate", methods=["POST"])
def gen():
    d = request.get_json(force=True)
    desc = (d.get("description") or "").strip()
    if not desc:
        return jsonify({"success": False, "error": "Enter description"})
    return jsonify(do_gen(desc, max(1, min(10, int(d.get("iterations", 2))))))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5051))
    print(f"PaperBanana at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, threaded=True)
