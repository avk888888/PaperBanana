#!/usr/bin/env python3
"""PaperBanana - AutoFigure Web Interface"""
import os, sys, json, webbrowser, asyncio, traceback
from pathlib import Path

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "pb_output"
os.chdir(str(BASE_DIR))
OUTPUT_DIR.mkdir(exist_ok=True)

from flask import Flask, request, jsonify, Response
from autofigure import AutoFigureAgent, Config

app = Flask(__name__)

def do_gen(desc: str, iters: int) -> dict:
    try:
        config = Config(
            generation_api_key=os.environ.get("OPENROUTER_API_KEY", ""),
            generation_provider="openrouter",
            refinement_iterations=iters,
            output_dir=str(OUTPUT_DIR / "runs"),
        )
        agent = AutoFigureAgent(config)
        result = agent.generate(description=desc, max_iterations=iters)
        if result.success:
            return {"success": True, "iters": iters, "desc": desc[:200]}
        return {"success": False, "error": result.error or "Generation failed"}
    except Exception as e:
        return {"success": False, "error": traceback.format_exc()}

@app.route("/")
def index():
    return "<h1>PaperBanana</h1><p>Set OPENROUTER_API_KEY, then POST to /api/generate</p>"

@app.route("/api/generate", methods=["POST"])
def gen():
    d = request.get_json(force=True)
    desc = (d.get("description") or "").strip()
    if not desc:
        return jsonify({"success": False, "error": "Enter description"})
    return jsonify(do_gen(desc, max(1, min(10, int(d.get("iterations", 2))))))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5051))
    print(f"PaperBanana running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, threaded=True)
