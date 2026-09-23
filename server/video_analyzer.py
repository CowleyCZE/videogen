from __future__ import annotations
import json, subprocess
from pathlib import Path

def _run(args: list[str]) -> str:
    p = subprocess.run(args, check=True, capture_output=True, text=True)
    return p.stdout

def analyze_video(path: str | Path, work_dir: str | Path) -> dict:
    path, work_dir = Path(path), Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    raw = _run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    probe = json.loads(raw)
    video = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
    audio = next((s for s in probe.get("streams", []) if s.get("codec_type") == "audio"), {})
    metadata = {
        "file": path.name,
        "duration": float(probe.get("format", {}).get("duration", 0)),
        "size_bytes": path.stat().st_size,
        "width": video.get("width"), "height": video.get("height"),
        "fps": video.get("r_frame_rate"), "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"), "has_audio": bool(audio),
    }
    (work_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata

def extract_audio(path: str | Path, out_path: str | Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(out_path)], check=True)
