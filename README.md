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
- Compatible with `n8n` + Docker setups with volume mounts

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

