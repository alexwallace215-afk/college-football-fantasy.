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

# Fantasy lineup structure
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
    for i in range(1, count + 1):
        cols = st.columns([4, 2, 4])  # Team1 | Slot | Team2

        with cols[0]:
            player1 = st.selectbox(
                f"Team 1 {pos}{i}",
                options=team1_df[team1_df['position'] == pos]['Player'].tolist(),
                key=f"team1_{pos}{i}"
            )
            if player1:
                row = team1_df[team1_df['Player'] == player1].iloc[0]
                st.markdown(f"**{player1}** — {row['Fantasy Points']} pts  \n[Roster Link]({row['Roster URL']})")

        with cols[1]:
            color = pos_colors.get(pos, '#FFFFFF')
            st.markdown(f"""
            <div style="text-align:center; background-color:{color}; padding:10px; 
                        border-radius:8px; font-weight:bold; margin:5px;">
                {pos}{i}
            </div>
            """, unsafe_allow_html=True)

        with cols[2]:
            player2 = st.selectbox(
                f"Team 2 {pos}{i}",
                options=team2_df[team2_df['position'] == pos]['Player'].tolist(),
                key=f"team2_{pos}{i}"
            )
            if player2:
                row = team2_df[team2_df['Player'] == player2].iloc[0]
                st.markdown(f"**{player2}** — {row['Fantasy Points']} pts  \n[Roster Link]({row['Roster URL']})")

