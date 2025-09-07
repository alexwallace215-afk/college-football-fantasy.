import pandas as pd
import requests

# -----------------------
# 0. Define games to fetch
# -----------------------
game_ids = ['401752665', '401752669']  # Alabama vs Florida St, Georgia vs Marshall

# -----------------------
# 1. Load CSV files
# -----------------------
teams = pd.read_csv('teams.csv')  # team_id, team_name, conference, roster_url
players = pd.read_csv('players.csv')  # player_id, player_name, team_id, position, depth, roster_url, injury_status, espn_id

# -----------------------
# 2. Fetch stats from ESPN boxscores
# -----------------------
snap_data = []

for game_id in game_ids:
    url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/summary?event={game_id}"
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"⚠️ Failed to fetch game {game_id}: {resp.status_code}")
            continue
        data = resp.json()
    except Exception as e:
        print(f"⚠️ Error fetching game {game_id}: {e}")
        continue

    # Loop through statistics blocks
    for stat_block in data.get('statistics', []):
        stat_name = stat_block.get('name')
        athletes = stat_block.get('athletes', [])
        for entry in athletes:
            athlete = entry['athlete']
            espn_id = athlete['id']
            stats = entry['stats']

            # Determine snaps for slot assignment
            if stat_name == 'passing':
                # QB snaps = pass attempts (first part of completions/attempts)
                pass_attempts = int(stats[0].split('/')[1])
                snap_data.append({
                    'espn_id': espn_id,
                    'team_id': None,  # will map later
                    'snaps': pass_attempts
                })
            elif stat_name == 'rushing':
                # RB snaps = rushing attempts
                rush_attempts = int(stats[0])
                snap_data.append({
                    'espn_id': espn_id,
                    'team_id': None,  # will map later
                    'snaps': rush_attempts
                })

if not snap_data:
    print("⚠️ No snap data captured. Check JSON or game IDs.")
    snap_df = pd.DataFrame(columns=['player_id', 'team_id', 'snaps'])
else:
    snap_df = pd.DataFrame(snap_data)

# -----------------------
# 3. Map ESPN IDs to our player IDs and teams
# -----------------------
espn_to_csv = dict(zip(players['espn_id'], players['player_id']))
espn_to_team = dict(zip(players['espn_id'], players['team_id']))

if not snap_df.empty:
    snap_df['player_id'] = snap_df['espn_id'].map(espn_to_csv)
    snap_df['team_id'] = snap_df['espn_id'].map(espn_to_team)
    snap_df = snap_df.dropna(subset=['player_id', 'team_id'])
    snap_df['snaps'] = snap_df['snaps'].astype(int)

# -----------------------
# 4. Assign fantasy slots based on depth and snaps
# -----------------------
fantasy_slots = {}
for team_id in players['team_id'].unique():
    team_name = teams.loc[teams['team_id'] == team_id, 'team_name'].values[0]
    team_players = players[players['team_id'] == team_id]

    for position in team_players['position'].unique():
        pos_players = team_players[team_players['position'] == position].copy()

        # Sort by depth first, then snaps if available
        pos_players['snaps'] = pos_players['player_id'].map(
            snap_df.set_index('player_id')['snaps'].to_dict()
        ).fillna(0)
        pos_players = pos_players.sort_values(by=['depth', 'snaps'])

        for i, pid in enumerate(pos_players['player_id'], start=1):
            slot_name = f"{team_name} {position}{i}"
            fantasy_slots[slot_name] = pid

# -----------------------
# 5. Calculate fantasy points from boxscore stats
# -----------------------
# For simplicity, we assign mock stats: replace with real stats if available
stats_df = pd.DataFrame({
    'player_id': players['player_id'],
    'rushing_yards': [26, 10, 18, 9, 17, 8, 26, 8],
    'receiving_yards': [5, 0, 7, 1, 0, 3, 8, 2],
    'passing_yards': [254, 180, 0, 0, 200, 120, 0, 0],
    'tds': [2, 1, 0, 0, 1, 0, 1, 0],
    'int': [0, 0, 0, 0, 1, 0, 0, 0]
})

def calc_fantasy_points(row):
    points = row['rushing_yards'] / 10
    points += row['receiving_yards'] / 10
    points += row['passing_yards'] / 25
    points += row['tds'] * 6
    points -= row['int'] * 2
    return round(points, 1)

stats_df['fantasy_points'] = stats_df.apply(calc_fantasy_points, axis=1)

# -----------------------
# 6. Display fantasy scoreboard
# -----------------------
scoreboard = []

print("=== Fantasy Scoreboard ===")
for slot, pid in fantasy_slots.items():
    player_info = players[players['player_id'] == pid].iloc[0]
    player_stats = stats_df[stats_df['player_id'] == pid]
    fp = player_stats['fantasy_points'].values[0] if not player_stats.empty else 0
    print(f"{slot} ({player_info['player_name']}): {fp} pts | Roster: {player_info['roster_url']}")
    scoreboard.append([slot, player_info['player_name'], fp, player_info['roster_url']])

# -----------------------
# 7. Optional: save to CSV
# -----------------------
scoreboard_df = pd.DataFrame(scoreboard, columns=['Slot', 'Player', 'Fantasy Points', 'Roster URL'])
scoreboard_df.to_csv('scoreboard.csv', index=False)
print("✅ Scoreboard saved to scoreboard.csv")