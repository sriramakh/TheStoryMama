#!/usr/bin/env python3
"""
TheStoryMama Reel Studio — Web UI for creating Instagram Reels.
Run: python reel_studio.py
Access: http://localhost:8001
"""

import os
import json
import subprocess
import textwrap
import shutil
import uuid
import time
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

# Job progress tracking
jobs: dict[str, dict] = {}  # job_id -> {status, progress, message, result}

# Cache: story_id -> latest reel result (video url, captions, settings)
REEL_CACHE_FILE = "reel_studio_cache/reel_cache.json"


def _load_reel_cache() -> dict:
    if os.path.exists(REEL_CACHE_FILE):
        try:
            with open(REEL_CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}


def _save_reel_cache(cache: dict):
    os.makedirs(os.path.dirname(REEL_CACHE_FILE), exist_ok=True)
    with open(REEL_CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


reel_cache: dict[str, dict] = _load_reel_cache()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from config import Config

app = FastAPI(title="Reel Studio")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = OpenAI(api_key=Config.OPENAI_API_KEY)

STORIES_DIR = Config.OUTPUT_DIR
TTS_CACHE_DIR = "reel_studio_cache/tts"
REELS_DIR = "reel_studio_cache/reels"
ASSETS_DIR = "reels_assets"
W, H = 1080, 1920

os.makedirs(TTS_CACHE_DIR, exist_ok=True)
os.makedirs(REELS_DIR, exist_ok=True)

# Serve generated reels as static files
app.mount("/reels", StaticFiles(directory=REELS_DIR), name="reels")

BGM_TRACKS = {
    "Joyful": "reels_audio/Joyful.mp3",
    "Adventurous1": "reels_audio/Adventurous1.mp3",
    "Adventurous2": "reels_audio/Adventurous2.mp3",
    "Enchanted": "reels_audio/Enchanted.mp3",
    "Playful": "reels_audio/Playful.mp3",
}

VOICE_INSTRUCTIONS = {
    "sage": """Voice Affect: Light, warm, and playful; slightly soft but not hushed, with a gentle sense of curiosity and wonder.
Tone: Friendly and magical with a hint of mystery — intriguing but never scary, like a bedtime adventure.
Pacing: Moderate and rhythmic; slow down slightly during important or magical moments.
Emotion: Expressive and animated — use gentle excitement, curiosity, and soft surprise.
Pronunciation: Clear, slightly rounded vowels with a musical, sing-song quality; soften edges.
Pauses: Use short, gentle pauses for storytelling rhythm.""",
    "nova": """Voice Affect: Gentle, warm, and soothing — like a loving parent reading to their child. Soft but clear.
Tone: Tender and reassuring with quiet wonder. Every sentence feels like a warm hug.
Pacing: Slow and deliberate. Let each word breathe. Pause after sentences.
Emotion: Calm joy. Peaceful and loving. Smile in the voice.
Pronunciation: Soft, rounded, unhurried.
Pauses: Longer, contemplative pauses between sentences.""",
}


def get_font(size):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
              "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def get_dur(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def generate_tts(story_id, voice):
    """Generate TTS for all scenes of a story. Cached."""
    cache_dir = os.path.join(TTS_CACHE_DIR, story_id, voice)
    os.makedirs(cache_dir, exist_ok=True)

    story_path = os.path.join(STORIES_DIR, story_id, "story_data.json")
    with open(story_path) as f:
        story = json.load(f)

    instructions = VOICE_INSTRUCTIONS[voice]
    generated = 0

    for scene in story["scenes"]:
        sn = scene["scene_number"]
        tts_path = os.path.join(cache_dir, f"scene_{sn:02d}.mp3")
        if os.path.exists(tts_path):
            continue

        response = client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=scene["text"],
            instructions=instructions,
            response_format="mp3",
        )
        with open(tts_path, "wb") as f:
            f.write(response.content)
        generated += 1

    return {"cached": len(story["scenes"]) - generated, "generated": generated}


def create_intro_video(title, out_path):
    """Create intro video with title overlay."""
    intro_template = os.path.join(ASSETS_DIR, "TheStoryMama Intro.mp4")
    if not os.path.exists(intro_template):
        return None

    tmp = f"/tmp/reel_intro_{uuid.uuid4().hex[:8]}"
    os.makedirs(tmp, exist_ok=True)

    subprocess.run(["ffmpeg", "-y", "-i", intro_template,
                    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                    f"{tmp}/f%04d.png"], capture_output=True)

    frames = sorted([f for f in os.listdir(tmp) if f.endswith(".png")])
    fps = 32
    font = get_font(58)
    lines = textwrap.wrap(title, width=22)

    for i, fn in enumerate(frames):
        t = i / fps
        if t < 1.5:
            alpha = 0
        elif t < 2.0:
            alpha = (t - 1.5) * 2
        else:
            alpha = 1.0
        if alpha <= 0:
            continue

        fp = os.path.join(tmp, fn)
        img = Image.open(fp).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        a = int(alpha * 255)
        y = 1120
        for line in lines:
            bb = d.textbbox((0, 0), line, font=font)
            tw = bb[2] - bb[0]
            d.text(((W - tw) // 2 + 2, y + 2), line, fill=(80, 50, 30, int(a * 0.2)), font=font)
            d.text(((W - tw) // 2, y), line, fill=(101, 67, 33, a), font=font)
            y += 70
        img = Image.alpha_composite(img, ov).convert("RGB")
        img.save(fp, "PNG")

    subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i", f"{tmp}/f%04d.png",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
                    out_path], capture_output=True)
    shutil.rmtree(tmp)
    return out_path


class ReelRequest(BaseModel):
    story_id: str
    voice: str = "nova"
    bgm: str = "Joyful"
    tts_volume: float = 1.05
    bgm_volume: float = 0.097
    tts_tempo: float = 0.9  # 0.7=slow, 1.0=normal, 0.9=default
    include_intro: bool = True
    include_outro: bool = True


# ── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/stories")
def list_stories():
    """List all available stories."""
    stories = []
    for folder in sorted(os.listdir(STORIES_DIR), reverse=True):
        json_path = os.path.join(STORIES_DIR, folder, "story_data.json")
        if not os.path.exists(json_path):
            continue
        with open(json_path) as f:
            data = json.load(f)
        stories.append({
            "id": folder,
            "title": data.get("title", "Untitled"),
            "scenes": len(data.get("scenes", [])),
            "style": data.get("animation_style", ""),
        })
    return {"stories": stories}


@app.get("/api/stories/{story_id}/image/{scene_num}")
def get_scene_image(story_id: str, scene_num: int):
    """Serve a scene image."""
    for ext in [".jpg", "_web.jpg", "_raw.png"]:
        path = os.path.join(STORIES_DIR, story_id, f"scene_{scene_num:02d}{ext}")
        if os.path.exists(path):
            return FileResponse(path)
    raise HTTPException(404, "Image not found")


@app.get("/api/bgm")
def list_bgm():
    """List available BGM tracks."""
    return {"tracks": list(BGM_TRACKS.keys())}


@app.post("/api/generate-tts")
def api_generate_tts(story_id: str, voice: str = "both"):
    """Pre-generate TTS for a story."""
    results = {}
    if voice in ("both", "sage"):
        results["sage"] = generate_tts(story_id, "sage")
    if voice in ("both", "nova"):
        results["nova"] = generate_tts(story_id, "nova")
    return results


@app.get("/api/tts-status/{story_id}")
def tts_status(story_id: str):
    """Check if TTS is pre-generated for a story."""
    result = {}
    for v in ["sage", "nova"]:
        cache_dir = os.path.join(TTS_CACHE_DIR, story_id, v)
        if os.path.exists(cache_dir):
            count = len([f for f in os.listdir(cache_dir) if f.endswith(".mp3")])
            result[v] = count
        else:
            result[v] = 0
    return result


@app.get("/api/job/{job_id}")
def get_job_status(job_id: str):
    """Get the status of a reel generation job."""
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@app.get("/api/reel-cache/{story_id}")
def get_reel_cache(story_id: str):
    """Get cached reel result for a story (if exists)."""
    cached = reel_cache.get(story_id)
    if not cached:
        return {"cached": False}
    return {"cached": True, "result": cached}


@app.post("/api/generate-reel")
def api_generate_reel(req: ReelRequest):
    """Start reel generation in background, return job_id for polling."""
    story_path = os.path.join(STORIES_DIR, req.story_id, "story_data.json")
    if not os.path.exists(story_path):
        raise HTTPException(404, "Story not found")

    job_id = uuid.uuid4().hex[:10]
    jobs[job_id] = {"status": "running", "progress": 0, "message": "Starting...", "result": None}

    def run_job():
        try:
            _generate_reel_impl(req, job_id)
        except Exception as e:
            jobs[job_id] = {"status": "failed", "progress": 0, "message": str(e), "result": None}

    thread = threading.Thread(target=run_job, daemon=True)
    thread.start()

    return {"job_id": job_id}


def _generate_reel_impl(req: ReelRequest, job_id: str):
    """Actual reel generation with progress updates."""
    story_path = os.path.join(STORIES_DIR, req.story_id, "story_data.json")
    with open(story_path) as f:
        story = json.load(f)

    # Step 1: TTS
    jobs[job_id] = {"status": "running", "progress": 10, "message": "Generating narration...", "result": None}
    tts_dir = os.path.join(TTS_CACHE_DIR, req.story_id, req.voice)
    if not os.path.exists(tts_dir) or len([f for f in os.listdir(tts_dir) if f.endswith(".mp3")]) < len(story["scenes"]):
        generate_tts(req.story_id, req.voice)
    jobs[job_id]["progress"] = 30
    jobs[job_id]["message"] = "Narration ready"

    bgm_path = BGM_TRACKS.get(req.bgm)
    if not bgm_path or not os.path.exists(bgm_path):
        raise HTTPException(400, f"BGM not found: {req.bgm}")

    scenes = story["scenes"]
    n = len(scenes)
    tr = 0.5

    # Scene data
    sdata = []
    for sc in scenes:
        sn = sc["scene_number"]
        tp = os.path.join(tts_dir, f"scene_{sn:02d}.mp3")
        dur = max(4.0, get_dur(tp) / req.tts_tempo + 0.5)
        ip = os.path.join(STORIES_DIR, req.story_id, f"scene_{sn:02d}.jpg")
        if not os.path.exists(ip):
            ip = os.path.join(STORIES_DIR, req.story_id, f"scene_{sn:02d}_web.jpg")
        if not os.path.exists(ip):
            ip = os.path.join(STORIES_DIR, req.story_id, f"scene_{sn:02d}_raw.png")
        sdata.append({"sn": sn, "tts": tp, "dur": dur, "img": ip})

    # Prepare intro/outro
    intro_vid = None
    outro_vid = None
    intro_dur = 0
    outro_dur = 0

    if req.include_intro:
        intro_vid = os.path.join(REELS_DIR, f"intro_{req.story_id}.mp4")
        create_intro_video(story["title"], intro_vid)
        intro_dur = get_dur(intro_vid) if intro_vid and os.path.exists(intro_vid) else 0

    if req.include_outro:
        outro_template = os.path.join(ASSETS_DIR, "TheStoryMama Outro.mp4")
        if os.path.exists(outro_template):
            outro_vid = os.path.join(REELS_DIR, "outro_scaled.mp4")
            subprocess.run(["ffmpeg", "-y", "-i", outro_template,
                            "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps=30",
                            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
                            "-an", outro_vid], capture_output=True)
            outro_dur = get_dur(outro_vid)

    # BUILD VIDEO — simple linear xfade chain: [intro] + scenes + [outro]
    # Collect all visual segments in order
    all_segments = []  # list of {"dur": float, "input_args": list}

    inputs_v = []
    if intro_vid and os.path.exists(intro_vid):
        inputs_v.extend(["-i", intro_vid])
        all_segments.append({"dur": intro_dur})

    for sd in sdata:
        inputs_v.extend(["-loop", "1", "-t", str(sd["dur"]), "-i", sd["img"]])
        all_segments.append({"dur": sd["dur"]})

    if outro_vid and os.path.exists(outro_vid):
        inputs_v.extend(["-i", outro_vid])
        all_segments.append({"dur": outro_dur})

    total_segs = len(all_segments)
    vf = []

    # Scale all inputs
    for i in range(total_segs):
        vf.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30[v{i}]")

    # Xfade chain
    offset = all_segments[0]["dur"] - tr
    vf.append(f"[v0][v1]xfade=transition=slideleft:duration={tr}:offset={offset:.3f}[xf1]")
    cum = offset + all_segments[1]["dur"] - tr

    for i in range(2, total_segs):
        prev = f"xf{i-1}"
        curr = f"xf{i}" if i < total_segs - 1 else "vout"
        vf.append(f"[{prev}][v{i}]xfade=transition=slideleft:duration={tr}:offset={cum:.3f}[{curr}]")
        cum += all_segments[i]["dur"] - tr

    if total_segs == 2:
        vf[-1] = vf[-1].replace("[xf1]", "[vout]")

    total_vid = cum + all_segments[-1]["dur"]

    # Cache video track — same for all BGM/volume combos of this story+voice+intro+outro combo
    intro_flag = "i" if (intro_vid and os.path.exists(intro_vid)) else "n"
    outro_flag = "o" if (outro_vid and os.path.exists(outro_vid)) else "n"
    video_cache_key = f"{req.story_id}_{req.voice}_{intro_flag}{outro_flag}"
    jobs[job_id] = {"status": "running", "progress": 40, "message": "Building video track...", "result": None}
    video_only = os.path.join(REELS_DIR, f"vcache_{video_cache_key}.mp4")

    if not os.path.exists(video_only):
        r_vid = subprocess.run(["ffmpeg", "-y", *inputs_v, "-filter_complex", ";".join(vf),
                        "-map", "[vout]", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                        "-pix_fmt", "yuv420p", "-t", str(total_vid), "-an", video_only],
                       capture_output=True, text=True)
        if r_vid.returncode != 0:
            raise Exception(f"Video generation failed: {r_vid.stderr[-300:]}")
    else:
        jobs[job_id]["progress"] = 60
        jobs[job_id]["message"] = "Using cached video track"
    # else: reuse cached video track

    # BUILD AUDIO
    inputs_a = []
    af = []
    t = intro_dur if intro_vid else 0
    for i, sd in enumerate(sdata):
        inputs_a.extend(["-i", sd["tts"]])
        ms = int(t * 1000)
        af.append(f"[{i}:a]aformat=channel_layouts=mono,atempo={req.tts_tempo},volume={req.tts_volume},adelay={ms}|{ms}[a{i}]")
        t += sd["dur"] - tr

    amix = "".join(f"[a{i}]" for i in range(n))
    af.append(f"{amix}amix=inputs={n}:duration=longest:normalize=0,apad=whole_dur={total_vid}[tts_mix]")

    inputs_a.extend(["-stream_loop", "-1", "-i", bgm_path])
    af.append(f"[{n}:a]aformat=channel_layouts=mono,atrim=0:{total_vid:.1f},volume={req.bgm_volume},"
              f"afade=t=in:d=2,afade=t=out:st={total_vid - 3:.1f}:d=3,asetpts=PTS-STARTPTS[bgm_a]")
    af.append(f"[tts_mix][bgm_a]amix=inputs=2:duration=first:normalize=0,"
              f"aformat=channel_layouts=stereo[aout]")

    jobs[job_id] = {"status": "running", "progress": 65, "message": "Mixing audio...", "result": None}
    audio_only = os.path.join(REELS_DIR, f"tmp_a_{uuid.uuid4().hex[:8]}.m4a")
    r_aud = subprocess.run(["ffmpeg", "-y", *inputs_a, "-filter_complex", ";".join(af),
                    "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", audio_only],
                   capture_output=True, text=True)
    if r_aud.returncode != 0:
        if os.path.exists(video_only) and "vcache_" not in video_only:
            os.remove(video_only)
        raise Exception(f"Audio generation failed: {r_aud.stderr[-300:]}")

    # MUX
    jobs[job_id] = {"status": "running", "progress": 85, "message": "Combining video + audio...", "result": None}
    reel_id = f"{req.story_id}_{req.voice}_{req.bgm}_{uuid.uuid4().hex[:6]}"
    out = os.path.join(REELS_DIR, f"{reel_id}.mp4")
    subprocess.run(["ffmpeg", "-y", "-i", video_only, "-i", audio_only,
                    "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart",
                    "-t", str(total_vid), out], capture_output=True)

    # Cleanup (keep video cache, remove temp audio)
    if os.path.exists(audio_only):
        os.remove(audio_only)

    if os.path.exists(out):
        mb = os.path.getsize(out) / (1024 * 1024)

        # Generate social media captions
        jobs[job_id] = {"status": "running", "progress": 92, "message": "Writing captions...", "result": None}
        captions = _generate_captions(story)

        # Save captions alongside the reel
        caption_path = os.path.join(REELS_DIR, f"{reel_id}_captions.json")
        with open(caption_path, "w") as f:
            json.dump(captions, f, indent=2)

        result_data = {
            "url": f"/reels/{reel_id}.mp4",
            "filename": f"{reel_id}.mp4",
            "size_mb": round(mb, 1),
            "duration": round(total_vid, 1),
            "captions": captions,
            "voice": req.voice,
            "bgm": req.bgm,
            "tts_volume": req.tts_volume,
            "bgm_volume": req.bgm_volume,
            "tts_tempo": req.tts_tempo,
        }

        # Cache the result for this story (persisted to disk)
        reel_cache[req.story_id] = result_data
        _save_reel_cache(reel_cache)

        jobs[job_id] = {
            "status": "done",
            "progress": 100,
            "message": "Reel ready!",
            "result": result_data,
        }
    else:
        raise Exception("Failed to generate reel")


def _generate_captions(story: dict) -> dict:
    """Generate Instagram and YouTube captions using GPT-4o-mini."""
    title = story.get("title", "")
    moral = story.get("moral", "")
    characters = ", ".join(c["name"] for c in story.get("characters", []))
    scene_texts = " ".join(s["text"] for s in story.get("scenes", [])[:3])

    prompt = f"""You are the social media manager for TheStoryMama — a children's bedtime story brand.

Generate captions for this story. Follow the EXACT format templates below.

STORY: {title}
CHARACTERS: {characters}
MORAL: {moral or 'None'}
OPENING: {scene_texts}

Return JSON with these fields:

{{
  "instagram_caption": "Follow this EXACT format:\n\n[One warm, emotional opening line about the story — make parents feel something]\n\n[One line describing what happens in the story — create curiosity]\n\nRead the full story free — link in bio\n\nFollow @thestorymama for daily bedtime stories\n\n[15-20 hashtags on a new line, always include: #bedtimestories #toddlermom #kidsstories #storytime #thestorymama #readtogether #picturebooks #toddlerlife #momlife #freestories — add 5-10 more relevant ones]",

  "youtube_title": "[Story Title] | Bedtime Story for Kids | TheStoryMama (under 60 chars total)",

  "youtube_description": "Follow this EXACT format:\n\n[Story Title] — A beautiful illustrated bedtime story\n\n[2 sentences: what the story is about and what kids will love]\n\nRead this story and 150+ more free at www.thestorymama.club\n\nSubscribe to @thestorymamaofficial for new stories every week!\n\n#bedtimestories #kidsstories #storytime #toddler #readaloud #thestorymama",

  "pinterest_description": "[Story Title] — A free illustrated bedtime story for toddlers aged 2-4. [One sentence about the plot]. Perfect for bedtime reading or quiet time. Read free at thestorymama.club. #bedtimestories #toddlerstories #freekidsbooks #illustratedstories #picturebooks"
}}

IMPORTANT: Follow the templates exactly. Keep the consistent brand voice — warm, personal, parent-to-parent. Hashtags can vary per story but always include the core set."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception as e:
        print(f"Caption generation failed: {e}")
        return {
            "instagram_caption": f"{title}\n\nRead the full story free — link in bio\n\n#bedtimestories #toddlermom #kidsstories #storytime",
            "youtube_title": f"{title} — Free Bedtime Story for Kids",
            "youtube_description": f"Watch {title}, a beautiful illustrated bedtime story. Read free at thestorymama.club",
            "pinterest_description": f"{title} — A free illustrated bedtime story for toddlers. Read at thestorymama.club",
        }


# ── QC / Correction API ──────────────────────────────────────────────────────

class CorrectionRequest(BaseModel):
    story_id: str
    scene_number: int
    feedback: str  # e.g. "Lily should have brown skin not white", "Remove the fox from this scene"


@app.get("/api/stories/{story_id}/details")
def get_story_details(story_id: str):
    """Get full story data for QC."""
    story_path = os.path.join(STORIES_DIR, story_id, "story_data.json")
    if not os.path.exists(story_path):
        raise HTTPException(404, "Story not found")
    with open(story_path) as f:
        story = json.load(f)
    # Load QC scores if available
    qc_scores = {}
    qc_path = os.path.join(STORIES_DIR, story_id, "qc_scores.json")
    if os.path.exists(qc_path):
        with open(qc_path) as f:
            qc_data = json.load(f)
            for s in qc_data.get("scores", []):
                qc_scores[s["scene_number"]] = s

    return {
        "id": story_id,
        "title": story.get("title"),
        "characters": story.get("characters", []),
        "scenes": [
            {
                "scene_number": s["scene_number"],
                "text": s["text"],
                "image_description": s.get("image_description", ""),
                "background": s.get("background", ""),
                "image_url": f"/api/stories/{story_id}/image/{s['scene_number']}",
                "qc_score": qc_scores.get(s["scene_number"], {}).get("score"),
                "qc_status": qc_scores.get(s["scene_number"], {}).get("status"),
            }
            for s in story.get("scenes", [])
        ],
    }


@app.post("/api/correct-scene")
def correct_scene(req: CorrectionRequest):
    """Regenerate a scene image based on QC feedback. Returns job_id for polling."""
    story_path = os.path.join(STORIES_DIR, req.story_id, "story_data.json")
    if not os.path.exists(story_path):
        raise HTTPException(404, "Story not found")

    job_id = uuid.uuid4().hex[:10]
    jobs[job_id] = {"status": "running", "progress": 0, "message": "Starting correction...", "result": None}

    def run():
        try:
            _correct_scene_impl(req, job_id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            jobs[job_id] = {"status": "failed", "progress": 0, "message": str(e), "result": None}

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return {"job_id": job_id}


def _correct_scene_impl(req: CorrectionRequest, job_id: str):
    """Regenerate a scene image with correction feedback."""
    import base64

    story_path = os.path.join(STORIES_DIR, req.story_id, "story_data.json")
    with open(story_path) as f:
        story = json.load(f)

    scene = None
    for s in story["scenes"]:
        if s["scene_number"] == req.scene_number:
            scene = s
            break
    if not scene:
        raise Exception(f"Scene {req.scene_number} not found")

    style_key = story.get("animation_style", Config.DEFAULT_ANIMATION_STYLE)
    style = Config.ANIMATION_STYLES.get(style_key, Config.ANIMATION_STYLES[Config.DEFAULT_ANIMATION_STYLE])

    # Step 1: Analyze context — get visual reference from adjacent scenes
    jobs[job_id] = {"status": "running", "progress": 10, "message": "Analyzing context...", "result": None}

    char_block = "\n".join(f"- {c['name']} ({c['type']}): {c['description']}" for c in story["characters"])

    # Get visual reference from scene before (if exists)
    visual_ref = ""
    ref_scene_num = req.scene_number - 1 if req.scene_number > 1 else req.scene_number + 1
    ref_img_path = None
    for ext in ["_web.jpg", "_raw.png", ".jpg"]:
        p = os.path.join(STORIES_DIR, req.story_id, f"scene_{ref_scene_num:02d}{ext}")
        if os.path.exists(p):
            ref_img_path = p
            break

    if ref_img_path:
        with open(ref_img_path, "rb") as f:
            ref_b64 = base64.b64encode(f.read()).decode()

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe each character in this image in ONE dense line each. Include: exact skin/fur color, hair/fur style, clothing with colors, accessories. Be extremely specific."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{ref_b64}", "detail": "low"}}
                ]
            }],
            max_tokens=300,
        )
        visual_ref = resp.choices[0].message.content.strip()

    # Step 2: Generate corrected image
    jobs[job_id] = {"status": "running", "progress": 30, "message": "Generating corrected image...", "result": None}

    prompt = f"""{style['description']}

BACKGROUND: {scene.get('background', story.get('setting', ''))}

CHARACTERS:
{char_block}

{"CHARACTER VISUAL REFERENCE FROM ADJACENT SCENE (match exactly):" + chr(10) + visual_ref if visual_ref else ""}

SCENE {scene['scene_number']} of {len(story['scenes'])}:
{scene['image_description']}

CORRECTION REQUESTED:
{req.feedback}

Apply the correction precisely. Everything else should remain the same as described.

RULES:
- {style['image_rules']}
- Apply the correction feedback exactly
- Keep character designs consistent with the visual reference
- Warm, friendly expressions appropriate for a children's book
- DO NOT include any text, words, letters, or numbers in the image"""

    result = client.images.generate(
        model="gpt-image-1-mini",
        prompt=prompt,
        size=Config.IMAGE_SIZE,
        quality="medium",
    )

    # Save corrected image
    sn = req.scene_number
    story_dir = os.path.join(STORIES_DIR, req.story_id)

    # Backup original
    for ext in ["_raw.png", "_web.jpg", ".jpg"]:
        orig = os.path.join(story_dir, f"scene_{sn:02d}{ext}")
        backup = os.path.join(story_dir, f"scene_{sn:02d}{ext}.bak")
        if os.path.exists(orig) and not os.path.exists(backup):
            shutil.copy2(orig, backup)

    # Save new raw
    image_bytes = base64.b64decode(result.data[0].b64_json)
    new_raw = os.path.join(story_dir, f"scene_{sn:02d}_raw.png")
    with open(new_raw, "wb") as f:
        f.write(image_bytes)

    jobs[job_id] = {"status": "running", "progress": 60, "message": "Creating web version...", "result": None}

    # Generate web-optimized version
    img = Image.open(new_raw).convert("RGB")
    web_path = os.path.join(story_dir, f"scene_{sn:02d}_web.jpg")
    img.save(web_path, "JPEG", quality=82, optimize=True)

    # Generate text overlay version
    jobs[job_id] = {"status": "running", "progress": 75, "message": "Adding text overlay...", "result": None}

    from text_overlay import TextOverlay
    overlay = TextOverlay()
    overlay_path = os.path.join(story_dir, f"scene_{sn:02d}.jpg")
    overlay.overlay_text_on_image(
        image_path=new_raw,
        text=scene["text"],
        output_path=overlay_path,
        scene_number=sn,
        total_scenes=len(story["scenes"]),
        title=story["title"] if sn == 1 else None,
        moral=story.get("moral") if sn == len(story["scenes"]) else None,
    )

    # Invalidate video cache for this story
    for f in os.listdir(REELS_DIR):
        if f.startswith(f"vcache_{req.story_id}"):
            os.remove(os.path.join(REELS_DIR, f))

    jobs[job_id] = {
        "status": "done",
        "progress": 100,
        "message": "Correction complete!",
        "result": {
            "scene_number": sn,
            "new_image_url": f"/api/stories/{req.story_id}/image/{sn}?t={int(time.time())}",
            "backup_exists": True,
        },
    }


@app.post("/api/approve-correction/{story_id}/{scene_num}")
def approve_correction(story_id: str, scene_num: int):
    """Approve a correction — delete backups."""
    story_dir = os.path.join(STORIES_DIR, story_id)
    removed = 0
    for ext in ["_raw.png.bak", "_web.jpg.bak", ".jpg.bak"]:
        bak = os.path.join(story_dir, f"scene_{scene_num:02d}{ext}")
        if os.path.exists(bak):
            os.remove(bak)
            removed += 1
    return {"approved": True, "backups_removed": removed}


@app.post("/api/reject-correction/{story_id}/{scene_num}")
def reject_correction(story_id: str, scene_num: int):
    """Reject a correction — restore from backups."""
    story_dir = os.path.join(STORIES_DIR, story_id)
    restored = 0
    for ext in ["_raw.png", "_web.jpg", ".jpg"]:
        bak = os.path.join(story_dir, f"scene_{scene_num:02d}{ext}.bak")
        orig = os.path.join(story_dir, f"scene_{scene_num:02d}{ext}")
        if os.path.exists(bak):
            shutil.move(bak, orig)
            restored += 1

    # Invalidate video cache
    for f in os.listdir(REELS_DIR):
        if f.startswith(f"vcache_{story_id}"):
            os.remove(os.path.join(REELS_DIR, f))

    return {"rejected": True, "files_restored": restored}


# ── Frontend ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def frontend():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TheStoryMama Reel Studio</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Nunito', Arial, sans-serif; background: #FFF9EB; color: #4A3728; padding: 20px; max-width: 1200px; margin: 0 auto; }
h1 { color: #654321; margin-bottom: 8px; }
.subtitle { color: #8B7D6B; margin-bottom: 24px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; min-width: 0; }
@media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }

.panel { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.panel h2 { font-size: 18px; color: #654321; margin-bottom: 16px; }

.story-list { max-height: 400px; overflow-y: auto; }
.story-item { padding: 10px 12px; border-radius: 10px; cursor: pointer; margin-bottom: 6px; transition: all 0.15s; display: flex; justify-content: space-between; align-items: center; }
.story-item:hover { background: #FFF3E0; }
.story-item.selected { background: #FFD6E0; font-weight: 600; }
.story-item .title { font-size: 14px; }
.story-item .meta { font-size: 11px; color: #8B7D6B; }

.controls label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px; margin-top: 14px; }
.controls select, .controls input[type=range] { width: 100%; }
.controls select { padding: 8px 12px; border-radius: 10px; border: 1px solid #EDE5D8; font-size: 14px; background: white; }

.slider-row { display: flex; align-items: center; gap: 10px; }
.slider-row input { flex: 1; }
.slider-row span { font-size: 13px; color: #8B7D6B; min-width: 40px; text-align: right; }

.checkbox-row { display: flex; align-items: center; gap: 8px; margin-top: 14px; }
.checkbox-row input { width: 18px; height: 18px; }
.checkbox-row label { font-size: 14px; margin: 0; }

.btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.btn-primary { background: #FFD6E0; color: #654321; }
.btn-primary:hover { background: #F5C6D0; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.btn-download { background: #D4F5E9; color: #2D5F4A; margin-left: 10px; }
.btn-download:hover { background: #B8E8D5; }

.btn-tts { background: #E8D5F5; color: #5B4370; font-size: 13px; padding: 8px 16px; margin-top: 10px; }
.btn-tts:hover { background: #D4C0E8; }

.preview-area { margin-top: 20px; }
.preview-area video { width: 100%; max-height: 500px; border-radius: 12px; background: #000; }

.status { margin-top: 12px; padding: 10px 14px; border-radius: 10px; font-size: 13px; }
.status.info { background: #E8D5F5; color: #5B4370; }
.status.success { background: #D4F5E9; color: #2D5F4A; }
.status.error { background: #FFE0E0; color: #C94B4B; }
.status.loading { background: #FFF3E0; color: #8B6914; }

.tts-status { font-size: 12px; color: #8B7D6B; margin-top: 6px; }
.tts-status .ready { color: #2D5F4A; }

.scene-preview { display: flex; gap: 8px; overflow-x: auto; padding: 10px 0; max-width: 100%; }
.caption-box { background: #FFF9EB; border-radius: 10px; padding: 14px; margin-bottom: 10px; }
.caption-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.caption-label { font-size: 13px; font-weight: 600; color: #654321; }
.btn-copy { font-size: 12px; padding: 4px 12px; border: 1px solid #EDE5D8; border-radius: 8px; background: white; cursor: pointer; color: #654321; }
.btn-copy:hover { background: #D4F5E9; }
.caption-text { font-size: 13px; color: #4A3728; white-space: pre-wrap; word-wrap: break-word; font-family: inherit; margin: 0; line-height: 1.5; background: none; border: none; }
.scene-preview img { height: 280px; border-radius: 8px; flex-shrink: 0; cursor: pointer; transition: transform 0.15s; }
.scene-preview img:hover { transform: scale(1.05); }
.panel { min-width: 0; overflow: hidden; }
</style>
</head>
<body>

<h1>TheStoryMama Reel Studio</h1>
<p class="subtitle">Create Instagram Reels from your stories</p>

<div class="grid">
  <!-- Left: Story Selection -->
  <div class="panel">
    <h2>Select Story</h2>
    <input type="text" id="search" placeholder="Search stories..." style="width:100%; padding:8px 12px; border-radius:10px; border:1px solid #EDE5D8; margin-bottom:12px; font-size:14px;">
    <div class="story-list" id="storyList">Loading...</div>
  </div>

  <!-- Right: Controls + Preview -->
  <div class="panel">
    <h2>Reel Settings</h2>
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
      <div id="selectedStory" style="font-size:14px; color:#8B7D6B;">No story selected</div>
      <div id="storyActions" style="display:none; flex-shrink:0;">
        <button class="btn" id="btnToggleVisibility" onclick="toggleVisibility()" style="font-size:11px; padding:5px 12px; background:#FFE0E0; color:#C94B4B;">Hide from Website</button>
        <button class="btn" id="btnToggleFeatured" onclick="toggleFeatured()" style="font-size:11px; padding:5px 12px; background:#FFF3E0; color:#8B6914;">Add to Featured</button>
      </div>
    </div>
    <div class="scene-preview" id="scenePreview"></div>

    <div class="controls">
      <label>TTS Voice</label>
      <select id="voice">
        <option value="nova">Nova (gentle, maternal)</option>
        <option value="sage">Sage (warm, playful)</option>
      </select>
      <div class="tts-status" id="ttsStatus"></div>
      <button class="btn btn-tts" onclick="pregenTTS()">Pre-generate TTS (both voices)</button>

      <label>Background Music</label>
      <select id="bgm">
        <option value="Joyful">Joyful (warm, happy)</option>
        <option value="Playful">Playful (bouncy, fun)</option>
        <option value="Enchanted">Enchanted (soft, dreamy)</option>
        <option value="Adventurous1">Adventurous 1 (upbeat)</option>
        <option value="Adventurous2">Adventurous 2 (driving)</option>
      </select>

      <label>TTS Volume</label>
      <div class="slider-row">
        <input type="range" id="ttsVol" min="0.3" max="2.0" step="0.05" value="1.05">
        <span id="ttsVolVal">1.05</span>
      </div>

      <label>Voice Speed</label>
      <div class="slider-row">
        <input type="range" id="ttsTempo" min="0.7" max="1.0" step="0.05" value="0.9">
        <span id="ttsTempoVal">0.9x</span>
      </div>

      <label>BGM Volume</label>
      <div class="slider-row">
        <input type="range" id="bgmVol" min="0.01" max="0.5" step="0.005" value="0.097">
        <span id="bgmVolVal">0.097</span>
      </div>

      <div class="checkbox-row">
        <input type="checkbox" id="introCheck" checked>
        <label for="introCheck">Include intro (with story title)</label>
      </div>
      <div class="checkbox-row">
        <input type="checkbox" id="outroCheck" checked>
        <label for="outroCheck">Include outro</label>
      </div>
    </div>

    <div style="margin-top:20px;">
      <button class="btn btn-primary" id="generateBtn" onclick="generateReel()" disabled>Generate Reel</button>
      <a id="downloadLink" style="display:none;"><button class="btn btn-download">Download</button></a>
    </div>

    <div id="progressContainer" style="display:none; margin-top:16px;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
        <span id="progressText" style="font-size:13px; color:#8B7D6B;">Starting...</span>
        <span id="progressPct" style="font-size:13px; font-weight:600; color:#654321;">0%</span>
      </div>
      <div style="height:8px; background:#EDE5D8; border-radius:4px; overflow:hidden;">
        <div id="progressBar" style="height:100%; width:0%; background:linear-gradient(to right,#FFD6E0,#E8D5F5); border-radius:4px; transition:width 0.3s;"></div>
      </div>
    </div>

    <div id="status"></div>

    <div class="preview-area" id="previewArea" style="display:none;">
      <video id="videoPlayer" controls></video>
    </div>

    <div id="captionsArea" style="display:none; margin-top:20px;">
      <h3 style="font-size:16px; color:#654321; margin-bottom:12px;">Social Media Captions</h3>

      <div class="caption-box" id="igCaption">
        <div class="caption-header">
          <span class="caption-label">Instagram</span>
          <button class="btn-copy" onclick="copyCaption('igCaptionText', this)">Copy</button>
        </div>
        <pre class="caption-text" id="igCaptionText"></pre>
      </div>

      <div class="caption-box" id="ytTitle">
        <div class="caption-header">
          <span class="caption-label">YouTube Title</span>
          <button class="btn-copy" onclick="copyCaption('ytTitleText', this)">Copy</button>
        </div>
        <pre class="caption-text" id="ytTitleText"></pre>
      </div>

      <div class="caption-box" id="ytDesc">
        <div class="caption-header">
          <span class="caption-label">YouTube Description</span>
          <button class="btn-copy" onclick="copyCaption('ytDescText', this)">Copy</button>
        </div>
        <pre class="caption-text" id="ytDescText"></pre>
      </div>

      <div class="caption-box" id="pinDesc">
        <div class="caption-header">
          <span class="caption-label">Pinterest</span>
          <button class="btn-copy" onclick="copyCaption('pinDescText', this)">Copy</button>
        </div>
        <pre class="caption-text" id="pinDescText"></pre>
      </div>
    </div>
  </div>
</div>

<script>
let stories = [];
let selectedStory = null;

// Load stories and restore last selected
fetch('/api/stories').then(r => r.json()).then(data => {
  stories = data.stories;
  renderStories(stories);
  // Auto-restore last selected story
  const lastStory = localStorage.getItem('lastStoryId');
  if (lastStory && stories.find(s => s.id === lastStory)) {
    selectStory(lastStory);
  }
});

function renderStories(list) {
  const el = document.getElementById('storyList');
  el.innerHTML = list.map(s => `
    <div class="story-item" onclick="selectStory('${s.id}')" id="story-${s.id}">
      <div>
        <div class="title">${s.title}</div>
        <div class="meta">${s.scenes} scenes · ${s.style}</div>
      </div>
    </div>
  `).join('');
}

document.getElementById('search').addEventListener('input', e => {
  const q = e.target.value.toLowerCase();
  renderStories(stories.filter(s => s.title.toLowerCase().includes(q)));
});

function selectStory(id) {
  selectedStory = stories.find(s => s.id === id);
  localStorage.setItem('lastStoryId', id);
  document.querySelectorAll('.story-item').forEach(el => el.classList.remove('selected'));
  const el = document.getElementById('story-' + id);
  if (el) el.classList.add('selected');
  document.getElementById('selectedStory').textContent = selectedStory.title;
  document.getElementById('generateBtn').disabled = false;

  // Hide previous results
  document.getElementById('previewArea').style.display = 'none';
  document.getElementById('downloadLink').style.display = 'none';
  document.getElementById('captionsArea').style.display = 'none';
  document.getElementById('status').innerHTML = '';

  // Show scene previews
  const preview = document.getElementById('scenePreview');
  let imgs = '';
  for (let i = 1; i <= selectedStory.scenes; i++) {
    imgs += '<img src="/api/stories/' + id + '/image/' + i + '" loading="lazy">';
  }
  preview.innerHTML = imgs;

  // Check TTS status
  checkTTSStatus(id);

  // Show action buttons and check visibility/featured status
  document.getElementById('storyActions').style.display = 'flex';
  updateStoryActions(id);

  // Check for cached reel
  fetch('/api/reel-cache/' + id).then(r => r.json()).then(data => {
    if (data.cached && data.result) {
      const r = data.result;
      setStatus('Previous reel available (' + r.size_mb + ' MB, ' + r.duration + 's)', 'info');
      const player = document.getElementById('videoPlayer');
      player.src = r.url;
      document.getElementById('previewArea').style.display = 'block';
      const dl = document.getElementById('downloadLink');
      dl.href = r.url;
      dl.download = r.filename;
      dl.style.display = 'inline';
      if (r.captions) showCaptions(r.captions);
      // Restore slider values from cached settings
      if (r.voice) document.getElementById('voice').value = r.voice;
      if (r.bgm) document.getElementById('bgm').value = r.bgm;
      if (r.tts_volume) { document.getElementById('ttsVol').value = r.tts_volume; document.getElementById('ttsVolVal').textContent = r.tts_volume; }
      if (r.bgm_volume) { document.getElementById('bgmVol').value = r.bgm_volume; document.getElementById('bgmVolVal').textContent = r.bgm_volume; }
      if (r.tts_tempo) { document.getElementById('ttsTempo').value = r.tts_tempo; document.getElementById('ttsTempoVal').textContent = r.tts_tempo + 'x'; }
    }
  }).catch(() => {});
}

function checkTTSStatus(id) {
  fetch('/api/tts-status/' + id).then(r => r.json()).then(data => {
    const el = document.getElementById('ttsStatus');
    const total = selectedStory.scenes;
    let parts = [];
    if (data.sage >= total) parts.push('<span class="ready">Sage ready</span>');
    else if (data.sage > 0) parts.push('Sage: ' + data.sage + '/' + total);
    else parts.push('Sage: not generated');
    if (data.nova >= total) parts.push('<span class="ready">Nova ready</span>');
    else if (data.nova > 0) parts.push('Nova: ' + data.nova + '/' + total);
    else parts.push('Nova: not generated');
    el.innerHTML = parts.join(' · ');
  });
}

function pregenTTS() {
  if (!selectedStory) return;
  setStatus('Generating TTS for both voices... (this takes ~30s)', 'loading');
  fetch('/api/generate-tts?story_id=' + selectedStory.id + '&voice=both', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      setStatus('TTS ready for both voices!', 'success');
      checkTTSStatus(selectedStory.id);
    })
    .catch(() => setStatus('TTS generation failed', 'error'));
}

// Sliders
document.getElementById('ttsVol').addEventListener('input', e => {
  document.getElementById('ttsVolVal').textContent = e.target.value;
});
document.getElementById('ttsTempo').addEventListener('input', e => {
  document.getElementById('ttsTempoVal').textContent = e.target.value + 'x';
});
document.getElementById('bgmVol').addEventListener('input', e => {
  document.getElementById('bgmVolVal').textContent = e.target.value;
});

function setStatus(msg, type) {
  document.getElementById('status').innerHTML = '<div class="status ' + type + '">' + msg + '</div>';
}

function generateReel() {
  if (!selectedStory) return;
  const btn = document.getElementById('generateBtn');
  btn.disabled = true;
  btn.textContent = 'Generating...';
  document.getElementById('downloadLink').style.display = 'none';
  document.getElementById('previewArea').style.display = 'none';
  document.getElementById('status').innerHTML = '';

  // Show progress bar
  const pc = document.getElementById('progressContainer');
  pc.style.display = 'block';
  updateProgress(0, 'Starting...');

  const body = {
    story_id: selectedStory.id,
    voice: document.getElementById('voice').value,
    bgm: document.getElementById('bgm').value,
    tts_volume: parseFloat(document.getElementById('ttsVol').value),
    tts_tempo: parseFloat(document.getElementById('ttsTempo').value),
    bgm_volume: parseFloat(document.getElementById('bgmVol').value),
    include_intro: document.getElementById('introCheck').checked,
    include_outro: document.getElementById('outroCheck').checked,
  };

  fetch('/api/generate-reel', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  .then(r => r.json())
  .then(data => {
    if (data.job_id) {
      pollJob(data.job_id);
    } else {
      setStatus('Failed to start: ' + (data.detail || 'Unknown error'), 'error');
      btn.disabled = false;
      btn.textContent = 'Generate Reel';
      pc.style.display = 'none';
    }
  })
  .catch(e => {
    setStatus('Error: ' + e.message, 'error');
    btn.disabled = false;
    btn.textContent = 'Generate Reel';
    pc.style.display = 'none';
  });
}

function updateProgress(pct, msg) {
  document.getElementById('progressBar').style.width = pct + '%';
  document.getElementById('progressPct').textContent = pct + '%';
  document.getElementById('progressText').textContent = msg;
}

function showCaptions(captions) {
  document.getElementById('captionsArea').style.display = 'block';
  document.getElementById('igCaptionText').textContent = captions.instagram_caption || '';
  document.getElementById('ytTitleText').textContent = captions.youtube_title || '';
  document.getElementById('ytDescText').textContent = captions.youtube_description || '';
  document.getElementById('pinDescText').textContent = captions.pinterest_description || '';
}

function copyCaption(elementId, btn) {
  const text = document.getElementById(elementId).textContent;
  // Fallback for HTTP (clipboard API requires HTTPS)
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.style.position = 'fixed';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
  btn.textContent = 'Copied!';
  btn.style.background = '#D4F5E9';
  setTimeout(() => { btn.textContent = 'Copy'; btn.style.background = 'white'; }, 2000);
}

let storyConfig = { hidden: [], featured: [] };

function updateStoryActions(id) {
  fetch('/api/stories/' + id + '/config').then(r => {
    if (!r.ok) {
      // Endpoint might not exist on studio, fetch from main API
      return fetch('https://api.thestorymama.club/api/v1/library/config').then(r2 => r2.json());
    }
    return r.json();
  }).then(cfg => {
    storyConfig = cfg;
    const isHidden = (cfg.hidden || []).includes(id);
    const isFeatured = (cfg.featured || []).includes(id);

    const btnVis = document.getElementById('btnToggleVisibility');
    btnVis.textContent = isHidden ? 'Show on Website' : 'Hide from Website';
    btnVis.style.background = isHidden ? '#D4F5E9' : '#FFE0E0';
    btnVis.style.color = isHidden ? '#2D5F4A' : '#C94B4B';

    const btnFeat = document.getElementById('btnToggleFeatured');
    btnFeat.textContent = isFeatured ? 'Remove from Featured' : 'Add to Featured';
    btnFeat.style.background = isFeatured ? '#FFE0E0' : '#FFF3E0';
    btnFeat.style.color = isFeatured ? '#C94B4B' : '#8B6914';
  }).catch(() => {});
}

function toggleVisibility() {
  if (!selectedStory) return;
  const isHidden = (storyConfig.hidden || []).includes(selectedStory.id);
  const endpoint = isHidden ? '/library/show' : '/library/hide';

  fetch('https://api.thestorymama.club/api/v1' + endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ story_id: selectedStory.id }),
  }).then(r => r.json()).then(() => {
    updateStoryActions(selectedStory.id);
    setStatus(isHidden ? 'Story is now visible on website' : 'Story hidden from website', 'success');
  }).catch(e => setStatus('Error: ' + e.message, 'error'));
}

function toggleFeatured() {
  if (!selectedStory) return;
  const isFeatured = (storyConfig.featured || []).includes(selectedStory.id);
  const endpoint = isFeatured ? '/library/unfeature' : '/library/feature';

  fetch('https://api.thestorymama.club/api/v1' + endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ story_id: selectedStory.id }),
  }).then(r => r.json()).then(() => {
    updateStoryActions(selectedStory.id);
    setStatus(isFeatured ? 'Removed from featured' : 'Added to featured on homepage', 'success');
  }).catch(e => setStatus('Error: ' + e.message, 'error'));
}

function pollJob(jobId) {
  fetch('/api/job/' + jobId)
    .then(r => r.json())
    .then(data => {
      updateProgress(data.progress, data.message);

      if (data.status === 'done' && data.result) {
        setStatus('Reel ready! ' + data.result.size_mb + ' MB, ' + data.result.duration + 's', 'success');
        const player = document.getElementById('videoPlayer');
        player.src = data.result.url;
        document.getElementById('previewArea').style.display = 'block';
        const dl = document.getElementById('downloadLink');
        dl.href = data.result.url;
        dl.download = data.result.filename;
        dl.style.display = 'inline';
        document.getElementById('generateBtn').disabled = false;
        document.getElementById('generateBtn').textContent = 'Generate Reel';
        setTimeout(() => { document.getElementById('progressContainer').style.display = 'none'; }, 2000);

        // Show captions
        if (data.result.captions) {
          showCaptions(data.result.captions);
        }
      } else if (data.status === 'failed') {
        setStatus('Failed: ' + data.message, 'error');
        document.getElementById('generateBtn').disabled = false;
        document.getElementById('generateBtn').textContent = 'Generate Reel';
        document.getElementById('progressContainer').style.display = 'none';
      } else {
        // Still running — poll again in 1.5s
        setTimeout(() => pollJob(jobId), 1500);
      }
    })
    .catch(() => setTimeout(() => pollJob(jobId), 2000));
}
</script>
</body>
</html>"""


@app.get("/qc", response_class=HTMLResponse)
def qc_page():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Story QC - TheStoryMama</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Nunito', Arial, sans-serif; background: #FFF9EB; color: #4A3728; padding: 20px; max-width: 1400px; margin: 0 auto; }
h1 { color: #654321; margin-bottom: 4px; }
.subtitle { color: #8B7D6B; margin-bottom: 20px; font-size: 14px; }
a { color: #E8829A; }

.top-bar { display: flex; gap: 16px; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }
.top-bar select { padding: 8px 12px; border-radius: 10px; border: 1px solid #EDE5D8; font-size: 14px; min-width: 300px; }

.scene-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.scene-card { background: white; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); cursor: pointer; transition: all 0.15s; }
.scene-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.12); transform: translateY(-2px); }
.scene-card.selected { ring: 3px solid #E8829A; outline: 3px solid #E8829A; }
.scene-card.needs-review { border: 2px solid #C94B4B; }
.scene-card img { width: 100%; display: block; }
.scene-card .info { padding: 10px 12px; }
.scene-card .info .num { font-size: 11px; color: #8B7D6B; font-weight: 600; }
.scene-card .info .text { font-size: 13px; margin-top: 4px; line-height: 1.4; }

.correction-panel { background: white; border-radius: 14px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-top: 20px; display: none; }
.correction-panel h3 { font-size: 16px; color: #654321; margin-bottom: 12px; }

.compare { display: flex; gap: 16px; margin: 16px 0; flex-wrap: wrap; }
.compare .img-box { flex: 1; min-width: 200px; }
.compare .img-box img { width: 100%; border-radius: 10px; }
.compare .img-box .label { font-size: 12px; font-weight: 600; text-align: center; margin-top: 6px; color: #8B7D6B; }

textarea { width: 100%; padding: 12px; border-radius: 10px; border: 1px solid #EDE5D8; font-size: 14px; resize: vertical; min-height: 80px; font-family: inherit; }

.btn { display: inline-flex; align-items: center; gap: 6px; padding: 10px 20px; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-fix { background: #FFD6E0; color: #654321; }
.btn-fix:hover { background: #F5C6D0; }
.btn-approve { background: #D4F5E9; color: #2D5F4A; }
.btn-approve:hover { background: #B8E8D5; }
.btn-reject { background: #FFE0E0; color: #C94B4B; }
.btn-reject:hover { background: #FFD0D0; }
.btn-row { display: flex; gap: 10px; margin-top: 16px; flex-wrap: wrap; }

.progress-bar { height: 6px; background: #EDE5D8; border-radius: 3px; margin: 12px 0; overflow: hidden; display: none; }
.progress-bar .fill { height: 100%; background: linear-gradient(to right, #FFD6E0, #E8D5F5); border-radius: 3px; transition: width 0.3s; }
.progress-msg { font-size: 13px; color: #8B7D6B; }

.status { padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-top: 12px; }
.status.success { background: #D4F5E9; color: #2D5F4A; }
.status.error { background: #FFE0E0; color: #C94B4B; }

.context-images { display: flex; gap: 8px; margin: 12px 0; }
.context-images img { height: 120px; border-radius: 6px; border: 2px solid transparent; }
.context-images img.current { border-color: #E8829A; }
.context-images .ctx-label { font-size: 10px; color: #8B7D6B; text-align: center; }
</style>
</head>
<body>

<h1>Story QC & Correction</h1>
<p class="subtitle">Select a story and click any scene to correct it. <a href="/">Back to Reel Studio</a></p>

<div class="top-bar">
  <select id="storySelect" onchange="loadStory(this.value)">
    <option value="">Select a story...</option>
  </select>
  <span id="storyInfo" style="font-size:13px; color:#8B7D6B;"></span>
</div>

<div class="scene-grid" id="sceneGrid"></div>

<div class="correction-panel" id="correctionPanel">
  <h3>Correct Scene <span id="corrSceneNum"></span></h3>

  <div class="context-images" id="contextImages"></div>

  <div style="margin-bottom:12px;">
    <div style="font-size:12px; color:#8B7D6B; margin-bottom:4px;">Scene text:</div>
    <div id="sceneText" style="font-size:14px; background:#FFF9EB; padding:10px; border-radius:8px;"></div>
  </div>

  <label style="font-size:13px; font-weight:600; display:block; margin-bottom:4px;">What needs to be corrected?</label>
  <textarea id="feedbackInput" placeholder="e.g. Lily should have brown skin matching scene 2. The fox should not be in this scene. Change the background to a sunny meadow."></textarea>

  <div class="btn-row">
    <button class="btn btn-fix" id="fixBtn" onclick="submitCorrection()">Regenerate Scene</button>
  </div>

  <div class="progress-bar" id="corrProgress"><div class="fill" id="corrProgressFill"></div></div>
  <div class="progress-msg" id="corrProgressMsg"></div>

  <div class="compare" id="compareArea" style="display:none;">
    <div class="img-box">
      <img id="beforeImg">
      <div class="label">Before</div>
    </div>
    <div class="img-box">
      <img id="afterImg">
      <div class="label">After</div>
    </div>
  </div>

  <div class="btn-row" id="approvalBtns" style="display:none;">
    <button class="btn btn-approve" onclick="approveCorrection()">Approve & Publish</button>
    <button class="btn btn-reject" onclick="rejectCorrection()">Reject & Revert</button>
    <button class="btn btn-fix" onclick="submitCorrection()">Try Again with More Feedback</button>
  </div>

  <div id="corrStatus"></div>
</div>

<script>
let storyData = null;
let selectedScene = null;
let beforeImageUrl = null;

fetch('/api/stories').then(r => r.json()).then(data => {
  const sel = document.getElementById('storySelect');
  data.stories.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.id;
    opt.textContent = s.title + ' (' + s.scenes + ' scenes)';
    sel.appendChild(opt);
  });
});

function loadStory(id) {
  if (!id) return;
  fetch('/api/stories/' + id + '/details').then(r => r.json()).then(data => {
    storyData = data;
    document.getElementById('storyInfo').textContent = data.characters.map(c => c.name + ' (' + c.type + ')').join(', ');
    renderScenes();
    document.getElementById('correctionPanel').style.display = 'none';
  });
}

function renderScenes() {
  const grid = document.getElementById('sceneGrid');
  grid.innerHTML = storyData.scenes.map(s => {
    const score = s.qc_score;
    const hasScore = score !== null && score !== undefined;
    const scoreColor = !hasScore ? '#8B7D6B' : score >= 0.75 ? '#2D5F4A' : '#C94B4B';
    const scoreBg = !hasScore ? '#EDE5D8' : score >= 0.75 ? '#D4F5E9' : '#FFE0E0';
    const scoreLabel = !hasScore ? 'No QC' : score.toFixed(2);
    return `
    <div class="scene-card ${s.qc_status === 'needs_review' ? 'needs-review' : ''}" id="sc-${s.scene_number}" onclick="selectScene(${s.scene_number})">
      <img src="${s.image_url}?t=${Date.now()}" loading="lazy">
      <div class="info">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div class="num">Scene ${s.scene_number}</div>
          <span style="font-size:11px; font-weight:600; padding:2px 8px; border-radius:6px; background:${scoreBg}; color:${scoreColor};">${scoreLabel}</span>
        </div>
        <div class="text">${s.text}</div>
      </div>
    </div>`;
  }).join('');
}

function selectScene(num) {
  selectedScene = storyData.scenes.find(s => s.scene_number === num);
  document.querySelectorAll('.scene-card').forEach(el => el.classList.remove('selected'));
  document.getElementById('sc-' + num).classList.add('selected');

  document.getElementById('corrSceneNum').textContent = '#' + num;
  document.getElementById('sceneText').textContent = selectedScene.text;
  document.getElementById('correctionPanel').style.display = 'block';
  document.getElementById('compareArea').style.display = 'none';
  document.getElementById('approvalBtns').style.display = 'none';
  document.getElementById('corrStatus').innerHTML = '';
  document.getElementById('feedbackInput').value = '';

  beforeImageUrl = selectedScene.image_url + '?t=' + Date.now();

  // Show context: prev, current, next
  const ctx = document.getElementById('contextImages');
  let html = '';
  const prev = storyData.scenes.find(s => s.scene_number === num - 1);
  if (prev) html += '<div><img src="' + prev.image_url + '?t=' + Date.now() + '"><div class="ctx-label">Scene ' + (num-1) + '</div></div>';
  html += '<div><img src="' + beforeImageUrl + '" class="current"><div class="ctx-label">Scene ' + num + ' (current)</div></div>';
  const next = storyData.scenes.find(s => s.scene_number === num + 1);
  if (next) html += '<div><img src="' + next.image_url + '?t=' + Date.now() + '"><div class="ctx-label">Scene ' + (num+1) + '</div></div>';
  ctx.innerHTML = html;

  window.scrollTo({ top: document.getElementById('correctionPanel').offsetTop - 20, behavior: 'smooth' });
}

function submitCorrection() {
  const feedback = document.getElementById('feedbackInput').value.trim();
  if (!feedback) { alert('Please describe what needs to be corrected'); return; }

  document.getElementById('fixBtn').disabled = true;
  document.getElementById('corrProgress').style.display = 'block';
  document.getElementById('compareArea').style.display = 'none';
  document.getElementById('approvalBtns').style.display = 'none';
  updateCorrProgress(0, 'Starting...');

  fetch('/api/correct-scene', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      story_id: storyData.id,
      scene_number: selectedScene.scene_number,
      feedback: feedback,
    }),
  })
  .then(r => r.json())
  .then(data => {
    if (data.job_id) pollCorrectionJob(data.job_id);
    else {
      document.getElementById('corrStatus').innerHTML = '<div class="status error">Failed: ' + (data.detail || 'Unknown') + '</div>';
      document.getElementById('fixBtn').disabled = false;
    }
  })
  .catch(e => {
    document.getElementById('corrStatus').innerHTML = '<div class="status error">Error: ' + e.message + '</div>';
    document.getElementById('fixBtn').disabled = false;
  });
}

function updateCorrProgress(pct, msg) {
  document.getElementById('corrProgressFill').style.width = pct + '%';
  document.getElementById('corrProgressMsg').textContent = msg + ' (' + pct + '%)';
}

function pollCorrectionJob(jobId) {
  fetch('/api/job/' + jobId).then(r => r.json()).then(data => {
    updateCorrProgress(data.progress, data.message);

    if (data.status === 'done') {
      document.getElementById('corrProgress').style.display = 'none';
      document.getElementById('fixBtn').disabled = false;

      // Show before/after comparison
      document.getElementById('beforeImg').src = beforeImageUrl;
      document.getElementById('afterImg').src = data.result.new_image_url;
      document.getElementById('compareArea').style.display = 'flex';
      document.getElementById('approvalBtns').style.display = 'flex';
      document.getElementById('corrStatus').innerHTML = '<div class="status success">New image generated! Compare and approve or reject.</div>';
    } else if (data.status === 'failed') {
      document.getElementById('corrProgress').style.display = 'none';
      document.getElementById('fixBtn').disabled = false;
      document.getElementById('corrStatus').innerHTML = '<div class="status error">Failed: ' + data.message + '</div>';
    } else {
      setTimeout(() => pollCorrectionJob(jobId), 1500);
    }
  }).catch(() => setTimeout(() => pollCorrectionJob(jobId), 2000));
}

function approveCorrection() {
  fetch('/api/approve-correction/' + storyData.id + '/' + selectedScene.scene_number, { method: 'POST' })
    .then(r => r.json())
    .then(() => {
      document.getElementById('corrStatus').innerHTML = '<div class="status success">Approved! Changes published to thestorymama.club.</div>';
      document.getElementById('approvalBtns').style.display = 'none';
      // Refresh the scene grid
      renderScenes();
    });
}

function rejectCorrection() {
  fetch('/api/reject-correction/' + storyData.id + '/' + selectedScene.scene_number, { method: 'POST' })
    .then(r => r.json())
    .then(() => {
      document.getElementById('corrStatus').innerHTML = '<div class="status error">Rejected. Original image restored.</div>';
      document.getElementById('compareArea').style.display = 'none';
      document.getElementById('approvalBtns').style.display = 'none';
      renderScenes();
    });
}
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
