import pandas as pd

# -----------------------
# 1. Load CSVs
# -----------------------
players = pd.read_csv("players.csv")  # Columns: player_id, player_name, team_id, position, depth, roster_url, injury_status, espn_id
teams = pd.read_csv("teams.csv")      # Columns: team_id, team_name, conference, roster_url
scoreboard = pd.read_csv("scoreboard 3.csv")  # Your manual points CSV

# -----------------------
# 2. Inspect columns in scoreboard
# -----------------------
print("Scoreboard columns detected:", scoreboard.columns.tolist())

# Attempt to find columns for player and points
player_col = None
points_col = None

for col in scoreboard.columns:
    if 'player' in col.lower():
        player_col = col
    if 'point' in col.lower():
        points_col = col

if player_col is None or points_col is None:
    raise Exception("Could not detect player or points column in scoreboard 3.csv")

# Rename for consistency
scoreboard = scoreboard.rename(columns={player_col: 'player_name', points_col: 'fantasy_points'})

# -----------------------
# 3. Merge players with points
# -----------------------
players_points = pd.merge(
    players,
    scoreboard[['player_name', 'fantasy_points']],
    on="player_name",
    how="left"
)

# Fill missing points with 0
players_points['fantasy_points'] = players_points['fantasy_points'].fillna(0)

# -----------------------
# 4. Assign fantasy slots by team and position/depth
# -----------------------
fantasy_slots = {}
for team_id, team_group in players_points.groupby('team_id'):
    team_name = teams.loc[teams['team_id'] == team_id, 'team_name'].values[0]
    for position, pos_group in team_group.groupby('position'):
        pos_sorted = pos_group.sort_values('depth')
        for slot_num, row in enumerate(pos_sorted.itertuples(), start=1):
            slot_name = f"{team_name} {position}{slot_num}"
            fantasy_slots[slot_name] = row.player_name

# -----------------------
# 5. Display Fantasy Scoreboard
# -----------------------
print("\n=== Fantasy Scoreboard ===")
scoreboard_list = []
for slot, player_name in fantasy_slots.items():
    player_row = players_points[players_points['player_name'] == player_name].iloc[0]
    fp = player_row['fantasy_points']
    roster_url = player_row['roster_url']
    print(f"{slot} ({player_name}): {fp} pts | Roster: {roster_url}")
    scoreboard_list.append([slot, player_name, fp, roster_url])

# -----------------------
# 6. Save Scoreboard CSV
# -----------------------
scoreboard_df = pd.DataFrame(scoreboard_list, columns=['Slot', 'Player', 'Fantasy Points', 'Roster URL'])
scoreboard_df.to_csv("fantasy_scoreboard.csv", index=False)
print("\n✅ Scoreboard saved to fantasy_scoreboard.csv")

