import pandas as pd
import requests
from bs4 import BeautifulSoup

# -----------------------
# 1. Load players CSV
# -----------------------
players = pd.read_csv("players.csv")  # Columns: player_id, player_name, team_id, position, depth, roster_url, injury_status, espn_id

# -----------------------
# 2. Define games to scrape
# -----------------------
games = {
    401752665: "Alabama vs Florida State",
    401752669: "Georgia vs Marshall"
}

snap_data = []

# -----------------------
# 3. Scrape each game
# -----------------------
for game_id, desc in games.items():
    url = f"https://www.espn.com/college-football/game/_/gameId/{game_id}"
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"⚠️ Failed to fetch game {game_id}: {resp.status_code}")
        continue

    soup = BeautifulSoup(resp.text, "html.parser")

    # Find all team stats tables
    tables = soup.find_all("table")
    if not tables:
        print(f"⚠️ No tables found for game {game_id}")
        continue

    for table in tables:
        # Table caption (usually team name + stat type)
        caption = table.find("caption")
        if not caption:
            continue
        caption_text = caption.get_text().lower()
        if "passing" in caption_text or "rushing" in caption_text:
            rows = table.find("tbody").find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if not cols or len(cols) < 2:
                    continue
                player_name = cols[0].get_text(strip=True)
                stat = cols[1].get_text(strip=True)
                
                # Determine snaps based on stat type
                if "passing" in caption_text:
                    # QB: first number in "C/A" passing stat
                    try:
                        snaps = int(stat.split("/")[1])
                    except:
                        continue
                elif "rushing" in caption_text:
                    # RB: rushing attempts
                    try:
                        snaps = int(stat)
                    except:
                        continue
                else:
                    continue

                # Map to player_id
                matched = players[players["player_name"].str.contains(player_name, case=False)]
                if matched.empty:
                    continue
                player_id = matched.iloc[0]["player_id"]
                team_id = matched.iloc[0]["team_id"]
                snap_data.append({
                    "player_id": player_id,
                    "team_id": team_id,
                    "snaps": snaps
                })

# -----------------------
# 4. Save snap counts CSV
# -----------------------
if snap_data:
    snap_df = pd.DataFrame(snap_data)
    snap_df = snap_df.groupby(["player_id", "team_id"], as_index=False)["snaps"].sum()
    snap_df.to_csv("espn_snapcounts.csv", index=False)
    print("✅ Snap counts saved to espn_snapcounts.csv")
else:
    print("⚠️ No snap data captured.")