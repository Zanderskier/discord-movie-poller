# 🎬 Weekly Movie Night Poll Generator

This Python script automates the creation of weekly movie night polls based on your Plex library. It applies intelligent filtering using metadata from TMDB and posts formatted polls directly into a Discord channel via simulated keyboard input.

---

## 📌 Features

- 🔍 **Smart Filtering**
  - Excludes previously used movies
  - Optional filters for G-rated, R-rated, and nudity-related content
  - Excludes kid/family-targeted genres

- 🎞️ **Series-Aware Ordering**
  - Detects movie collections via TMDB
  - Ensures sequels are not shown out of order

- 🗳️ **Discord Poll Automation**
  - Automatically types out `/poll` commands into Discord using `pyautogui`
  - Formats the poll for [Simple Poll](https://discord.com/discovery/applications/324631108731928587) App or similar bots

- 🧾 **CSV Export**
  - Saves selected movies to a weekly CSV log to prevent repetition

---

## ⚙️ Requirements

- Python 3.9+
- A Plex Media Server
- A Discord client (foregrounded)
- TMDB API key

### 📦 Python Dependencies

Install with:

```bash
pip install -r requirements.txt
```
# 📦 Dependencies

Install using pip:

```bash
pip install plexapi pandas requests pyautogui pyperclip requests_toolbelt
```

Or include in your `requirements.txt`:

```
plexapi
pandas
requests
pyautogui
pyperclip
requests_toolbelt
```

---

# 🚀 Usage

## 🛠️ Edit the Configuration File

Create a `config.json` file based on `config_template.json` and update the following fields:

- `PLEX_URL` and `PLEX_TOKEN`
- `TMDB_API_KEY`
- `OUT_FOLDER`

## ▶️ Run the Script

```bash
python poll_generator.py
```

## 🎛️ Answer Prompt Filters

You'll be asked whether to exclude:
- G-rated movies  
- R-rated movies  
- Movies with nudity-related tags

## 📤 Post the Poll to Discord

After the movie list is generated:

- ✅ The formatted poll message is copied to your clipboard  
- ⏳ The script will wait 2 seconds  
- 🧠 It begins typing into Discord using your keyboard  
- 🎯 **Make sure Discord is in focus and the message box is selected**

> The script uses `pyautogui` to simulate keystrokes and build the poll line by line.

---

# ⚠️ Important Note: Discord Must Be Ready

Before the script starts typing, you **must manually click into the text input box** of your target Discord channel (e.g., `#python-message-generated`).

❗ If the input box is not selected, the script may type into the wrong window—or do nothing.

---

# 📁 Output

Each run will:

- Create a folder like `week1`, `week2`, etc.
- Save a CSV of selected movies
- Print the formatted poll message
- Copy poll choices to your clipboard

---

# 🔐 Safety & Notes

- Poster downloading is currently **disabled** (can be re-enabled)  

---

## 🖼️ How to Re-Enable Poster Downloading

If you'd like the script to automatically download movie posters from TMDB and save them alongside the weekly poll:

---

### ✅ Step 1: Update `get_metadata()` to Include Poster URL

In your Python script, locate the `get_metadata()` function and replace it with the following:

```python
def get_metadata(name):
    info = tmdb_search_movie(name)
    if not info:
        return None
    mid = info["id"]
    release = info.get("release_date", "9999-01-01")
    details = requests.get(TMDB_MOVIE.format(id=mid), params={"api_key": TMDB_API_KEY}).json()
    coll = details.get("belongs_to_collection", {})
    coll_id = coll["id"] if coll else None
    keys = requests.get(TMDB_KEYWORDS.format(id=mid), params={"api_key": TMDB_API_KEY}).json().get("keywords", [])
    nude = any(k["name"].lower() in NUDITY_KEYWORDS for k in keys)
    poster_url = f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get("poster_path") else None
    return {
        "title": name,
        "tmdb_id": mid,
        "release": release,
        "col": coll_id,
        "nude": nude,
        "poster_url": poster_url
    }
```

This enhancement extracts the `poster_path` from TMDB and constructs a full image URL for later use.

---

### 📥 Step 2: Add Poster Download Logic

After the section where the weekly CSV is saved, insert this block of code:

```python
for movie in weekly:
    title = movie["title"]
    poster_url = meta_cache[title].get("poster_url")
    if not poster_url:
        continue
    file_name = os.path.join(week_folder, sanitize(title) + ".jpg")
    try:
        img_data = requests.get(poster_url).content
        with open(file_name, "wb") as f:
            f.write(img_data)
        print(f"🖼️ Saved poster for {title}")
    except Exception as e:
        print(f"❌ Failed to download poster for {title}: {e}")
```

Place this block right after the line that looks like:

```python
print(f"\n📜 Saved weekly poll: {csv}")
```

---

### 🛑 Already Avoids Duplicate Downloads

The script already checks for existing posters using the `poster_exists()` function, so this will not re-download posters if they’re already saved.

--- 

# 🧠 Roadmap Ideas

- [ ] Optional poster download/upload to Discord  
- [ ] Auto-detect correct Discord channel before typing  
- [ ] GUI for filter configuration  
- [ ] Replace keyboard simulation with Discord Bot API

---

# 📄 License

MIT License

---

# 🙌 Credits

Built with ❤️ for weekly community movie nights.  
Powered by **Plex**, **TMDB**, and your own movie collection.  
Uses [Simple Poll on Discord](https://discord.com/discovery/applications/324631108731928587) to collect votes.

