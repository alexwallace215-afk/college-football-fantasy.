import pandas as pd
import streamlit as st

# -----------------------
# Load scoreboard CSV
# -----------------------
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

# -----------------------
# Extract position for color mapping
# -----------------------
def get_position(slot):
    return ''.join([c for c in slot.split()[1] if not c.isdigit()])

team1_df['position'] = team1_df['Slot'].apply(get_position)
team2_df['position'] = team2_df['Slot'].apply(get_position)

# -----------------------
# Define color mapping
# -----------------------
pos_colors = {
    'QB': '#FFD700',  # Gold
    'RB': '#87CEFA',  # Light Blue
    'WR': '#90EE90',  # Light Green
    'TE': '#FFA07A',  # Light Salmon
    'K':  '#D3D3D3',  # Light Gray
    'DEF':'#FFB6C1'   # Light Pink
}

# -----------------------
# Title
# -----------------------
st.markdown("## 🏈 College Football Fantasy Scoreboard")

# -----------------------
# Matchup grid
# -----------------------
max_len = max(len(team1_df), len(team2_df))

for i in range(max_len):
    cols = st.columns(2)
    
    # Team 1 player
    if i < len(team1_df):
        row = team1_df.iloc[i]
        color = pos_colors.get(row['position'], '#FFFFFF')
        cols[0].markdown(f"""
        <div style="
            border-radius:10px; padding:10px; margin-bottom:5px;
            background-color:{color}; box-shadow:2px 2px 5px rgba(0,0,0,0.15);
        ">
            <strong>{row['Slot']}</strong><br>
            {row['Player']} | {row['Fantasy Points']} pts<br>
            <a href="{row['Roster URL']}" target="_blank">Roster</a>
        </div>
        """, unsafe_allow_html=True)
    
    # Team 2 player
    if i < len(team2_df):
        row = team2_df.iloc[i]
        color = pos_colors.get(row['position'], '#FFFFFF')
        cols[1].markdown(f"""
        <div style="
            border-radius:10px; padding:10px; margin-bottom:5px;
            background-color:{color}; box-shadow:2px 2px 5px rgba(0,0,0,0.15);
        ">
            <strong>{row['Slot']}</strong><br>
            {row['Player']} | {row['Fantasy Points']} pts<br>
            <a href="{row['Roster URL']}" target="_blank">Roster</a>
        </div>
        """, unsafe_allow_html=True)

