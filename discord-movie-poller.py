import random, re, os, requests, pandas as pd
from datetime import datetime
from plexapi.server import PlexServer
import json
import pyautogui
import pyperclip
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# === LOAD CONFIGURATION ===
CONFIG_PATH = "config.json"
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Missing {CONFIG_PATH}. Please create it from config_template.json.")

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

PLEX_URL = config["PLEX_URL"]
PLEX_TOKEN = config["PLEX_TOKEN"]
TMDB_API_KEY = config["TMDB_API_KEY"]
OUT_FOLDER = config["OUT_FOLDER"]
MOVIE_SECTION = config.get("MOVIE_SECTION", "Movies")

# === STATIC CONFIG ===
MOVIES_PER_WEEK = 10
RUNTIME = 135  # minutes

KID_KEYWORDS = {
    "family", "animation", "children", "kids", "disney",
    "pixar", "dreamworks", "barbie", "nickelodeon"
}
NUDITY_KEYWORDS = {
    "nudity", "female nudity", "male nudity", "explicit sex", "erotic",
    "graphic nudity", "topless", "sex scene", "sexual content"
}

TMDB_SEARCH = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE = "https://api.themoviedb.org/3/movie/{id}"
TMDB_KEYWORDS = "https://api.themoviedb.org/3/movie/{id}/keywords"

# === CACHING ===
METADATA_CACHE_FILE = "metadata_cache.json"
if os.path.exists(METADATA_CACHE_FILE):
    with open(METADATA_CACHE_FILE, "r") as f:
        metadata_cache = json.load(f)
else:
    metadata_cache = {}

# === UTILITIES ===
def sanitize(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def alt_queries(name):
    return [
        name,
        re.sub(r"\(.*?\)", "", name).strip(),
        name.replace(":", "").replace("-", "").strip()
    ]

# === USER PROMPTS ===
runtime_hours = round(RUNTIME / 60, 1)
print("Configure filtering for movie selection:")
filter_g = input("❓ Exclude G-rated movies? (y/n): ").strip().lower() == "y"
filter_r = input("❓ Exclude R-rated movies? (y/n): ").strip().lower() == "y"
filter_nudity = input("❓ Exclude movies with any nudity-related tags? (y/n): ").strip().lower() == "y"
filter_runtime = input(f"❓ Exclude movies over {runtime_hours} hours? (y/n): ").strip().lower() == "y"

print("\n🔧 Filters Applied:")
print(f" - Exclude G-rated: {filter_g}")
print(f" - Exclude R-rated: {filter_r}")
print(f" - Exclude nudity: {filter_nudity}")
print(f" - Exclude over {runtime_hours}hr runtime: {filter_runtime}\n")

# === PATH HANDLING ===
def get_next_folder(base):
    os.makedirs(base, exist_ok=True)
    weeks = sorted(
        int(re.findall(r"\d+", d)[0])
        for d in os.listdir(base)
        if re.match(r"week\d+", d)
    )
    n = weeks[-1] + 1 if weeks else 1
    path = os.path.join(base, f"week{n}")
    os.makedirs(path, exist_ok=True)
    return path, n

def load_history(base):
    used = set()
    entries = []
    for r, _, files in os.walk(base):
        for f in files:
            if f.endswith(".csv"):
                try:
                    df = pd.read_csv(os.path.join(r, f), usecols=["title"])
                    for t in df["title"].dropna():
                        t = t.strip()
                        used.add(t.lower())
                        entries.append(t)
                except Exception:
                    continue
    return used, entries

def build_poster_set(base):
    posters = set()
    for r, _, files in os.walk(base):
        posters.update({f.lower() for f in files if f.endswith(".jpg")})
    return posters

def poster_exists(name, poster_set):
    for q in alt_queries(name):
        if sanitize(q).lower() + ".jpg" in poster_set:
            return True
    return False

# === TMDB ===
def tmdb_search_movie(name, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(TMDB_SEARCH, params={"api_key": TMDB_API_KEY, "query": name}, timeout=10)
            return response.json().get("results", [])[0]
        except requests.exceptions.RequestException as e:
            print(f"⚠️ TMDB search failed for '{name}' (attempt {attempt+1}/{retries}): {e}")
            time.sleep(delay)
    return None

def get_metadata(name):
    if name in metadata_cache:
        return metadata_cache[name]

    info = tmdb_search_movie(name)
    if not info:
        return None

    mid = info["id"]
    release = info.get("release_date", "9999-01-01")
    try:
        details = requests.get(TMDB_MOVIE.format(id=mid), params={"api_key": TMDB_API_KEY}, timeout=10).json()
        coll = details.get("belongs_to_collection", {})
        coll_id = coll["id"] if coll else None
        runtime = details.get("runtime", 0)
        keys = requests.get(TMDB_KEYWORDS.format(id=mid), params={"api_key": TMDB_API_KEY}, timeout=10).json().get("keywords", [])
        nude = any(k["name"].lower() in NUDITY_KEYWORDS for k in keys)

        result = {
            "title": name,
            "tmdb_id": mid,
            "release": release,
            "col": coll_id,
            "nude": nude,
            "runtime": runtime
        }
        metadata_cache[name] = result
        return result
    except Exception as e:
        print(f"⚠️ Metadata fetch failed for {name}: {e}")
        return None

# === SETUP ===
week_folder, week_no = get_next_folder(OUT_FOLDER)
used_titles, used_list = load_history(OUT_FOLDER)
poster_set = build_poster_set(OUT_FOLDER)

print(f"📁 Loaded {len(used_titles)} previously used movies")
plex = PlexServer(PLEX_URL, PLEX_TOKEN)
movies = plex.library.section(MOVIE_SECTION).all()

# === FILTERING ===
candidates = []
for m in movies:
    if not m: continue
    t = m.title.strip()
    tl = t.lower()
    cr = (getattr(m, "contentRating", "") or "").upper()
    summ = getattr(m, "summary", "") or ""
    gen = [g.tag.lower() for g in getattr(m, "genres", [])]

    if tl == "what is a woman": continue
    if filter_g and cr == "G": continue
    if filter_r and cr == "R": continue
    if tl in used_titles: continue
    if any(k in summ.lower() for k in KID_KEYWORDS): continue
    if any(k in gen for k in KID_KEYWORDS): continue
    if any(k in tl for k in KID_KEYWORDS): continue
    if poster_exists(t, poster_set): continue
    candidates.append({"title": t, "guid": m.guid})

print(f"✅ {len(candidates)} movies after basic filtering")

# === BUILD SERIES MAP FROM USED TITLES ===
series_map = {}
for title in used_list:
    md = get_metadata(title)
    if md and md["col"]:
        series_map.setdefault(md["col"], []).append(md)

# === PARALLEL METADATA LOOKUPS ===
final = []
meta_cache = {}

with ThreadPoolExecutor(max_workers=10) as executor:
    future_map = {executor.submit(get_metadata, movie["title"]): movie for movie in candidates}
    for future in as_completed(future_map):
        movie = future_map[future]
        md = future.result()
        if not md: continue
        if filter_nudity and md["nude"]:
            print(f"🚫 Skipping {md['title']} due to nudity tag")
            continue
        if filter_runtime and md["runtime"] and md["runtime"] > RUNTIME:
            print(f"⏱️ Skipping {md['title']} due to runtime ({md['runtime']} min)")
            continue
        meta_cache[movie["title"]] = md
        cid = md["col"]
        used_in_series = series_map.get(cid, []) if cid else []
        if not cid or not used_in_series or all(md["release"] > prev["release"] for prev in used_in_series):
            final.append({**movie, **md})

print(f"🎯 {len(final)} candidates after metadata filtering")

# === UNIQUE SERIES ===
seen = set()
unique = []
for m in final:
    key = m["col"] or m["title"].lower()
    if key not in seen:
        seen.add(key)
        unique.append(m)

if len(unique) < MOVIES_PER_WEEK:
    raise Exception("❌ Not enough valid movies to choose")

weekly = random.sample(unique, MOVIES_PER_WEEK)

# === SAVE TO CSV ===
df = pd.DataFrame(weekly)
csv = f"movie_poll_week_{week_no}_{datetime.now():%Y-%m-%d}.csv"
df.to_csv(os.path.join(week_folder, csv), index=False)
print(f"\n📜 Saved weekly poll: {csv}")
for m in weekly:
    print(" -", m["title"])

# === POLL OUTPUT ===
poll_lines = [m["title"] for m in weekly]
manual_poll_lines = [f"/poll 🎮 Movie Night Poll - Week {week_no}"]
for i, m in enumerate(weekly):
    manual_poll_lines.append(f"choice_{chr(97 + i)} {m['title']}")
manual_poll_lines.append("You can vote for more than one")
manual_poll_text = "\n".join(manual_poll_lines)

print("\n📋 Copy-paste version of poll message:")
print("========================================")
print(manual_poll_text)
print("========================================\n")

# === CLIPBOARD + AUTOTYPE ===
pyperclip.copy("\n".join(poll_lines))
print("📋 Poll titles copied to clipboard.")

print("⌨️ Switching to Discord and typing poll in 5 seconds...")
time.sleep(5)
pyautogui.typewrite(f"/poll 🎮 Movie Night Poll - Week {week_no} Thursday at 19:30. Voting closes Wednesday", interval=0.05)
pyautogui.keyDown("ctrl")
pyautogui.press("tab")
pyautogui.keyUp("ctrl")
time.sleep(0.5)

for line in poll_lines:
    pyautogui.typewrite("choice_", interval=0.05)
    time.sleep(0.5)
    pyautogui.press("enter")
    time.sleep(0.5)
    pyautogui.typewrite(line, interval=0.05)
    time.sleep(0.5)
    pyautogui.keyDown("ctrl")
    pyautogui.press("tab")
    pyautogui.keyUp("ctrl")

time.sleep(1)
pyautogui.press("enter")
pyautogui.typewrite("You can vote for more than one", interval=0.05)
pyautogui.press("enter")
print("✅ Poll message sent via keyboard emulation.")

# === SAVE METADATA CACHE ===
with open(METADATA_CACHE_FILE, "w") as f:
    json.dump(metadata_cache, f, indent=2)
