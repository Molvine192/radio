import os
import time
from flask import Flask, Response, jsonify, render_template_string

app = Flask(__name__)
TRACKS_DIR = os.path.join(os.path.dirname(__file__), "tracks")

# Current track state
current_track = {"name": None}


def get_tracks():
    if not os.path.exists(TRACKS_DIR):
        os.makedirs(TRACKS_DIR)
    return sorted([f for f in os.listdir(TRACKS_DIR) if f.endswith(".mp3")])


def stream_track(filename):
    path = os.path.join(TRACKS_DIR, filename)
    while True:
        try:
            with open(path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk
        except FileNotFoundError:
            time.sleep(1)


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/tracks")
def list_tracks():
    return jsonify(get_tracks())


@app.route("/stream/<filename>")
def stream(filename):
    tracks = get_tracks()
    if filename not in tracks:
        return "Track not found", 404
    current_track["name"] = filename
    return Response(
        stream_track(filename),
        mimetype="audio/mpeg",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
        },
    )


@app.route("/current")
def current():
    return jsonify({"track": current_track["name"]})


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dragon Radio</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0a;
    --surface: #111;
    --border: #222;
    --accent: #ff4d00;
    --accent2: #ff8c00;
    --text: #e8e8e8;
    --muted: #555;
    --active-bg: #1a0d00;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Share Tech Mono', monospace;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(255,77,0,0.015) 2px,
      rgba(255,77,0,0.015) 4px
    );
    pointer-events: none;
    z-index: 0;
  }

  .container {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 560px;
  }

  .header {
    margin-bottom: 2.5rem;
  }

  .title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3rem, 10vw, 5rem);
    line-height: 0.9;
    letter-spacing: 0.05em;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    color: var(--muted);
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.4rem;
  }

  .status-bar {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 0.75rem 1rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.8rem;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--muted);
    flex-shrink: 0;
    transition: background 0.3s;
  }

  .dot.live {
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .status-text {
    color: var(--muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex: 1;
  }

  .status-text.active { color: var(--text); }

  .tracks-label {
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.75rem;
  }

  .tracks-list {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .track-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.85rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
    text-decoration: none;
    color: inherit;
  }

  .track-item:hover {
    border-color: var(--accent);
    background: var(--active-bg);
  }

  .track-item.active {
    border-color: var(--accent);
    background: var(--active-bg);
  }

  .track-num {
    color: var(--muted);
    font-size: 0.7rem;
    width: 2ch;
    flex-shrink: 0;
  }

  .track-item.active .track-num { color: var(--accent); }

  .track-name {
    flex: 1;
    font-size: 0.85rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .copy-btn {
    padding: 0.25rem 0.6rem;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--muted);
    font-family: inherit;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    cursor: pointer;
    transition: all 0.15s;
    flex-shrink: 0;
  }

  .copy-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
  }

  .copy-btn.copied {
    border-color: #00c853;
    color: #00c853;
  }

  .empty {
    padding: 2rem;
    text-align: center;
    color: var(--muted);
    font-size: 0.8rem;
    border: 1px dashed var(--border);
    letter-spacing: 0.1em;
  }

  .footer {
    margin-top: 1.5rem;
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.1em;
  }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="title">DRAGON<br>RADIO</div>
    <div class="subtitle">Minecraft Stream Server</div>
  </div>

  <div class="status-bar">
    <div class="dot" id="dot"></div>
    <div class="status-text" id="status">NO SIGNAL</div>
  </div>

  <div class="tracks-label">Available Tracks</div>
  <div class="tracks-list" id="tracks"></div>

  <div class="footer">
    PUT .MP3 FILES INTO /tracks FOLDER &nbsp;·&nbsp; COPY LINK → PASTE INTO RADIO
  </div>
</div>

<script>
const BASE = window.location.origin;
let activeName = null;

async function loadTracks() {
  const res = await fetch('/tracks');
  const tracks = await res.json();
  const container = document.getElementById('tracks');

  if (tracks.length === 0) {
    container.innerHTML = '<div class="empty">NO TRACKS FOUND<br><br>Add .mp3 files to the /tracks folder</div>';
    return;
  }

  container.innerHTML = tracks.map((name, i) => `
    <div class="track-item" id="track-${i}" data-name="${name}">
      <span class="track-num">${String(i + 1).padStart(2, '0')}</span>
      <span class="track-name">${name.replace('.mp3', '')}</span>
      <button class="copy-btn" data-url="${BASE}/stream/${encodeURIComponent(name)}">COPY URL</button>
    </div>
  `).join('');

  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', e => {
      e.stopPropagation();
      navigator.clipboard.writeText(btn.dataset.url);
      btn.textContent = 'COPIED!';
      btn.classList.add('copied');
      setTimeout(() => {
        btn.textContent = 'COPY URL';
        btn.classList.remove('copied');
      }, 2000);
    });
  });
}

async function updateStatus() {
  try {
    const res = await fetch('/current');
    const data = await res.json();
    const dot = document.getElementById('dot');
    const status = document.getElementById('status');

    document.querySelectorAll('.track-item').forEach(el => el.classList.remove('active'));

    if (data.track) {
      dot.classList.add('live');
      status.textContent = '● LIVE  —  ' + data.track.replace('.mp3', '');
      status.classList.add('active');
      const active = document.querySelector(`[data-name="${data.track}"]`);
      if (active) active.classList.add('active');
    } else {
      dot.classList.remove('live');
      status.textContent = 'NO SIGNAL';
      status.classList.remove('active');
    }
  } catch {}
}

loadTracks();
updateStatus();
setInterval(updateStatus, 5000);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
