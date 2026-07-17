from __future__ import annotations

import os
import socket
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

BASE = Path(__file__).resolve().parent
app = Flask(__name__, static_folder=None)

MODEL_CACHE: dict[str, Any] = {}
MODEL_LOCK = threading.Lock()

PROFILES = {
    "fast": {"model": "base.en", "compute_type": "int8", "label": "Fast"},
    "balanced": {"model": "small.en", "compute_type": "int8", "label": "Balanced"},
}


def get_model(profile: str):
    if WhisperModel is None:
        raise RuntimeError("faster-whisper is not installed. Run the supplied setup file first.")
    cfg = PROFILES.get(profile, PROFILES["balanced"])
    key = f"{cfg['model']}:{cfg['compute_type']}"
    with MODEL_LOCK:
        if key not in MODEL_CACHE:
            MODEL_CACHE[key] = WhisperModel(
                cfg["model"],
                device="cpu",
                compute_type=cfg["compute_type"],
                cpu_threads=max(2, min(8, os.cpu_count() or 4)),
                num_workers=1,
            )
        return MODEL_CACHE[key], cfg


def local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


@app.get("/")
def index():
    return send_from_directory(BASE, "index.html")


@app.get("/manifest.webmanifest")
def manifest():
    return send_from_directory(BASE, "manifest.webmanifest")


@app.get("/sw.js")
def service_worker():
    return send_from_directory(BASE, "sw.js")


@app.get("/transcription-worker.js")
def transcription_worker():
    return send_from_directory(BASE, "transcription-worker.js")


@app.get("/icon-192.png")
def icon_192():
    return send_from_directory(BASE, "icon-192.png")


@app.get("/icon-512.png")
def icon_512():
    return send_from_directory(BASE, "icon-512.png")


@app.get("/api/status")
def status():
    return jsonify({
        "ok": True,
        "engine": "faster-whisper local",
        "installed": WhisperModel is not None,
        "computer_url": "http://localhost:8787",
        "phone_url": f"http://{local_ip()}:8787",
    })


@app.post("/api/transcribe")
def transcribe():
    if "audio" not in request.files:
        return jsonify({"ok": False, "error": "No audio file was supplied."}), 400

    audio = request.files["audio"]
    profile = request.form.get("profile", "balanced")
    language = request.form.get("language", "en") or "en"
    suffix = Path(audio.filename or "audio.m4a").suffix or ".m4a"

    fd, temp_name = tempfile.mkstemp(prefix="tasa_audio_", suffix=suffix)
    os.close(fd)
    started = time.time()

    try:
        audio.save(temp_name)
        model, cfg = get_model(profile)

        # VAD is deliberately disabled so quiet opening phrases are not discarded.
        segments, info = model.transcribe(
            temp_name,
            language=language,
            task="transcribe",
            beam_size=5,
            best_of=5,
            temperature=0.0,
            vad_filter=False,
            condition_on_previous_text=True,
            word_timestamps=False,
            no_speech_threshold=0.8,
            log_prob_threshold=-1.0,
            compression_ratio_threshold=2.4,
            initial_prompt=(
                "Verbatim customer voice note about printing, artwork, measurements, "
                "briefs, stores, delivery, WhatsApp messages and production instructions."
            ),
        )

        # Fully consume every segment. This is the key difference from the broken browser version.
        collected = []
        segment_rows = []
        for seg in segments:
            text = (seg.text or "").strip()
            if text:
                collected.append(text)
            segment_rows.append({
                "start": round(float(seg.start), 2),
                "end": round(float(seg.end), 2),
                "text": text,
            })

        full_text = " ".join(collected).strip()
        elapsed = round(time.time() - started, 1)

        if not full_text:
            return jsonify({
                "ok": False,
                "error": "The engine processed the recording but did not detect speech.",
                "segments": segment_rows,
            }), 422

        return jsonify({
            "ok": True,
            "text": full_text,
            "segments": segment_rows,
            "segment_count": len(segment_rows),
            "audio_duration": round(float(getattr(info, "duration", 0.0) or 0.0), 1),
            "language": getattr(info, "language", language),
            "language_probability": round(float(getattr(info, "language_probability", 0.0) or 0.0), 3),
            "model": cfg["model"],
            "elapsed_seconds": elapsed,
        })
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500
    finally:
        try:
            os.remove(temp_name)
        except OSError:
            pass


if __name__ == "__main__":
    ip = local_ip()
    print("\nTASA Audio to Text V12 is running")
    print("Computer: http://localhost:8787")
    print(f"Phone on same Wi-Fi: http://{ip}:8787\n")
    app.run(host="0.0.0.0", port=8787, threaded=True, debug=False)
