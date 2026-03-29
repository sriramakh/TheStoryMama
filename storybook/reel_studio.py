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
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont

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


@app.post("/api/generate-reel")
def api_generate_reel(req: ReelRequest):
    """Generate a reel with specified settings."""
    story_path = os.path.join(STORIES_DIR, req.story_id, "story_data.json")
    if not os.path.exists(story_path):
        raise HTTPException(404, "Story not found")

    with open(story_path) as f:
        story = json.load(f)

    # Ensure TTS exists
    tts_dir = os.path.join(TTS_CACHE_DIR, req.story_id, req.voice)
    if not os.path.exists(tts_dir) or len(os.listdir(tts_dir)) < len(story["scenes"]):
        generate_tts(req.story_id, req.voice)

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
        dur = max(4.0, get_dur(tp) / 0.9 + 0.5)
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

    # BUILD VIDEO
    inputs_v = []
    vi = 0
    if intro_vid and os.path.exists(intro_vid):
        inputs_v.extend(["-i", intro_vid])
        vi += 1
    for sd in sdata:
        inputs_v.extend(["-loop", "1", "-t", str(sd["dur"]), "-i", sd["img"]])
    if outro_vid and os.path.exists(outro_vid):
        inputs_v.extend(["-i", outro_vid])

    total_inputs = (1 if intro_vid else 0) + n + (1 if outro_vid else 0)
    vf = []
    for i in range(total_inputs):
        vf.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30[v{i}]")

    # Xfade chain
    first_scene_idx = 1 if intro_vid else 0
    if intro_vid:
        offset = intro_dur - tr
        vf.append(f"[v0][v{first_scene_idx}]xfade=transition=slideleft:duration={tr}:offset={offset:.3f}[xf1]")
        cum = offset + sdata[0]["dur"] - tr
    else:
        offset = sdata[0]["dur"] - tr
        vf.append(f"[v0][v1]xfade=transition=slideleft:duration={tr}:offset={offset:.3f}[xf1]")
        cum = offset + sdata[1]["dur"] - tr if n > 1 else offset

    start_i = 1 if intro_vid else 1
    for i in range(start_i, n - (0 if intro_vid else 1)):
        scene_vi = first_scene_idx + i + (0 if intro_vid else 1)
        prev = f"xf{i + (1 if intro_vid else 0)}"
        curr_label = f"xf{i + 1 + (1 if intro_vid else 0)}"
        vf.append(f"[{prev}][v{scene_vi}]xfade=transition=slideleft:duration={tr}:offset={cum:.3f}[{curr_label}]")
        cum += sdata[i + (0 if intro_vid else 1)]["dur"] - tr

    last_xf = f"xf{n + (1 if intro_vid else 0) - 1}"
    if outro_vid:
        outro_vi = total_inputs - 1
        vf.append(f"[{last_xf}][v{outro_vi}]xfade=transition=slideleft:duration={tr}:offset={cum:.3f}[vout]")
        total_vid = cum + outro_dur
    else:
        vf[-1] = vf[-1].rsplit("[", 1)[0] + "[vout]"
        total_vid = cum + sdata[-1]["dur"]

    video_only = os.path.join(REELS_DIR, f"tmp_v_{uuid.uuid4().hex[:8]}.mp4")
    subprocess.run(["ffmpeg", "-y", *inputs_v, "-filter_complex", ";".join(vf),
                    "-map", "[vout]", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                    "-pix_fmt", "yuv420p", "-t", str(total_vid), "-an", video_only],
                   capture_output=True)

    # BUILD AUDIO
    inputs_a = []
    af = []
    t = intro_dur if intro_vid else 0
    for i, sd in enumerate(sdata):
        inputs_a.extend(["-i", sd["tts"]])
        ms = int(t * 1000)
        af.append(f"[{i}:a]aformat=channel_layouts=mono,atempo=0.9,volume={req.tts_volume},adelay={ms}|{ms}[a{i}]")
        t += sd["dur"] - tr

    amix = "".join(f"[a{i}]" for i in range(n))
    af.append(f"{amix}amix=inputs={n}:duration=longest:normalize=0,apad=whole_dur={total_vid}[tts_mix]")

    inputs_a.extend(["-stream_loop", "-1", "-i", bgm_path])
    af.append(f"[{n}:a]aformat=channel_layouts=mono,atrim=0:{total_vid:.1f},volume={req.bgm_volume},"
              f"afade=t=in:d=2,afade=t=out:st={total_vid - 3:.1f}:d=3,asetpts=PTS-STARTPTS[bgm_a]")
    af.append(f"[tts_mix][bgm_a]amix=inputs=2:duration=first:normalize=0,"
              f"aformat=channel_layouts=stereo[aout]")

    audio_only = os.path.join(REELS_DIR, f"tmp_a_{uuid.uuid4().hex[:8]}.m4a")
    subprocess.run(["ffmpeg", "-y", *inputs_a, "-filter_complex", ";".join(af),
                    "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", audio_only],
                   capture_output=True)

    # MUX
    reel_id = f"{req.story_id}_{req.voice}_{req.bgm}_{uuid.uuid4().hex[:6]}"
    out = os.path.join(REELS_DIR, f"{reel_id}.mp4")
    subprocess.run(["ffmpeg", "-y", "-i", video_only, "-i", audio_only,
                    "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart",
                    "-t", str(total_vid), out], capture_output=True)

    # Cleanup
    for f in [video_only, audio_only]:
        if os.path.exists(f):
            os.remove(f)

    if os.path.exists(out):
        mb = os.path.getsize(out) / (1024 * 1024)
        return {
            "url": f"/reels/{reel_id}.mp4",
            "filename": f"{reel_id}.mp4",
            "size_mb": round(mb, 1),
            "duration": round(total_vid, 1),
        }
    else:
        raise HTTPException(500, "Failed to generate reel")


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
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
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

.scene-preview { display: flex; gap: 6px; overflow-x: auto; padding: 10px 0; }
.scene-preview img { height: 80px; border-radius: 6px; flex-shrink: 0; }
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
    <div id="selectedStory" style="font-size:14px; color:#8B7D6B; margin-bottom:10px;">No story selected</div>
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

    <div id="status"></div>

    <div class="preview-area" id="previewArea" style="display:none;">
      <video id="videoPlayer" controls></video>
    </div>
  </div>
</div>

<script>
let stories = [];
let selectedStory = null;

// Load stories
fetch('/api/stories').then(r => r.json()).then(data => {
  stories = data.stories;
  renderStories(stories);
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
  document.querySelectorAll('.story-item').forEach(el => el.classList.remove('selected'));
  const el = document.getElementById('story-' + id);
  if (el) el.classList.add('selected');
  document.getElementById('selectedStory').textContent = selectedStory.title;
  document.getElementById('generateBtn').disabled = false;

  // Show scene previews
  const preview = document.getElementById('scenePreview');
  let imgs = '';
  for (let i = 1; i <= selectedStory.scenes; i++) {
    imgs += '<img src="/api/stories/' + id + '/image/' + i + '" loading="lazy">';
  }
  preview.innerHTML = imgs;

  // Check TTS status
  checkTTSStatus(id);
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
  setStatus('Generating reel... This takes 1-2 minutes.', 'loading');
  document.getElementById('downloadLink').style.display = 'none';
  document.getElementById('previewArea').style.display = 'none';

  const body = {
    story_id: selectedStory.id,
    voice: document.getElementById('voice').value,
    bgm: document.getElementById('bgm').value,
    tts_volume: parseFloat(document.getElementById('ttsVol').value),
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
    if (data.url) {
      setStatus('Reel ready! ' + data.size_mb + ' MB, ' + data.duration + 's', 'success');
      const player = document.getElementById('videoPlayer');
      player.src = data.url;
      document.getElementById('previewArea').style.display = 'block';
      const dl = document.getElementById('downloadLink');
      dl.href = data.url;
      dl.download = data.filename;
      dl.style.display = 'inline';
    } else {
      setStatus('Generation failed: ' + (data.detail || 'Unknown error'), 'error');
    }
  })
  .catch(e => setStatus('Error: ' + e.message, 'error'))
  .finally(() => {
    btn.disabled = false;
    btn.textContent = 'Generate Reel';
  });
}
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
