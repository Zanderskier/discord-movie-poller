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
  - Formats the poll for Simple Poll or similar bots

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
