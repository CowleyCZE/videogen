from __future__ import annotations
import subprocess
from pathlib import Path

def render_clip(source: str | Path, out_path: str | Path, start: float, end: float, resolution: str = "1080x1920") -> None:
    source, out_path = Path(source), Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    duration = max(0.1, end - start)
    # Zachová střed obrazu; pro produkci lze nahradit face/subject trackingem.
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-i", str(source), "-t", str(duration),
        "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_path)
    ], check=True)

def render_plan(source: str | Path, plan: dict, output_root: str | Path) -> list[dict]:
    output_root = Path(output_root)
    results = []
    for clip in plan.get("clips", []):
        for platform in clip["platforms"]:
            folder = {"youtube_shorts": "shorts", "instagram_reels": "reels", "tiktok": "tiktok"}[platform]
            path = output_root / folder / f"{clip['id']}.mp4"
            render_clip(source, path, float(clip["start"]), float(clip["end"]), clip.get("resolution", "1080x1920"))
            results.append({"clip_id": clip["id"], "platform": platform, "path": str(path)})
    return results
