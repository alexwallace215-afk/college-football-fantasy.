import pandas as pd
import streamlit as st

# Load scoreboard CSV
scoreboard = pd.read_csv("fantasy_scoreboard.csv")

# Extract teams
scoreboard['team'] = scoreboard['Slot'].apply(lambda x: x.split()[0])
teams = scoreboard['team'].unique()

if len(teams) != 2:
    st.warning("Expected exactly 2 teams for matchup view.")
    st.stop()

team1, team2 = teams

team1_df = scoreboard[scoreboard['team'] == team1].copy()
team2_df = scoreboard[scoreboard['team'] == team2].copy()

# Extract position for filtering
def get_position(slot):
    return ''.join([c for c in slot.split()[1] if not c.isdigit()])

team1_df['position'] = team1_df['Slot'].apply(get_position)
team2_df['position'] = team2_df['Slot'].apply(get_position)

# Color mapping
pos_colors = {
    'QB': '#FFD700',  # Gold
    'RB': '#87CEFA',  # Light Blue
    'WR': '#90EE90',  # Light Green
    'TE': '#FFA07A',  # Light Salmon
    'K':  '#D3D3D3',  # Light Gray
    'DEF':'#FFB6C1'   # Light Pink
}

# Fantasy lineup structure (slots per position)
lineup = {
    "QB": 1,
    "RB": 2,
    "WR": 2,
    "TE": 1,
    "K": 1,
    "DEF": 1
}

st.markdown("## 🏈 College Football Fantasy Matchup")

# Loop through each position slot
for pos, count in lineup.items():
    for _ in range(count):  # no numbering, just repeat RB twice, WR twice, etc.
       

