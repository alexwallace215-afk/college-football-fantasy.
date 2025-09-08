import pandas as pd
import streamlit as st

# Load fantasy scoreboard CSV
scoreboard = pd.read_csv("fantasy_scoreboard.csv")

# Load teams CSV
teams = pd.read_csv("teams.csv")
team_name_map = dict(zip(teams['team_id'].astype(str), teams['team_name']))
team_roster_map = dict(zip(teams['team_id'].astype(str), teams['roster_url']))

# Generate Slot column dynamically: e.g., Alabama RB1
scoreboard['Slot'] = scoreboard.apply(
    lambda row: f"{team_name_map.get(str(row['team_id']), 'Team'+str(row['team_id']))} {row['position'].upper()}{int(row['depth'])}",
    axis=1
)

# Ensure Fantasy Points is numeric
scoreboard['Fantasy Points'] = pd.to_numeric(scoreboard['Fantasy Points'], errors='coerce').fillna(0)

# Set a lighter background gradient and style
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #f2f2f2, #e0e0e0);
        color: #111111;
    }
    a {
        color: #0073e6;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 🏈 College Football Fantasy Scoreboard")

# Define positions and color coding (for middle indicators)
positions_order = ["QB", "RB", "RB", "WR", "WR", "TE", "K"]
pos_colors = {
    "QB": "#FFD700",
    "RB": "#87CEFA",
    "WR": "#90EE90",
    "TE": "#FFA07A",
    "K": "#D3D3D3",
}

# Prepare dropdown options per position
options_by_pos = {}
for pos in ["QB", "RB", "WR", "TE", "K"]:
    options_by_pos[pos] = scoreboard[scoreboard['position'] == pos]['Slot'].tolist()

# Initialize session state for team lineups
if "team1_lineup" not in st.session_state:
    st.session_state.team1_lineup = {pos: options_by_pos[pos][0] for pos in positions_order if options_by_pos[pos]}
if "team2_lineup" not in st.session_state:
    st.session_state.team2_lineup = {pos: options_by_pos[pos][0] for pos in positions_order if options_by_pos[pos]}

# Create columns for horizontal matchup view
cols = st.columns([1, 0.2, 1])  # Team1 | Positions | Team2

team1_lineup = st.session_state.team1_lineup
team2_lineup = st.session_state.team2_lineup

# Helper to render dropdowns and show fantasy points
def render_team_lineup(col, lineup, team_name):
    pos_count = {}  # Track occurrence of positions for unique keys
    for pos in positions_order:
        if pos not in options_by_pos or not options_by_pos[pos]:
            continue

        # Count occurrence of the position
        pos_count[pos] = pos_count.get(pos, 0) + 1
        index_suffix = pos_count[pos]  # Unique key

        slot = lineup[pos]
        # Dropdown
        selection = col.selectbox(
            f"{team_name} {pos}",
            options_by_pos[pos],
            index=options_by_pos[pos].index(slot),
            key=f"{team_name}_{pos}_{index_suffix}"  # Unique key
        )
        lineup[pos] = selection

        # Display link to roster
        player_row = scoreboard[scoreboard['Slot'] == selection].iloc[0]
        roster_link = player_row.get("roster_url", team_roster_map.get(str(player_row["team_id"]), "#"))
        col.markdown(f"<a href='{roster_link}' target='_blank'>Roster</a>", unsafe_allow_html=True)
        col.markdown("---")

# Render Team 1
with cols[0]:
    st.markdown("### Team 1")
    render_team_lineup(st, team1_lineup, "team1")

# Render position indicators in middle, aligned with rows
with cols[1]:
    pos_count = {}
    for pos in positions_order:
        pos_count[pos] = pos_count.get(pos, 0) + 1
        st.markdown(f"<div style='text-align:center; font-weight:bold; margin:10px 0; background-color:{pos_colors.get(pos,'#FFFFFF')}; border-radius:5px; padding:5px'>{pos}</div>", unsafe_allow_html=True)

# Render Team 2
with cols[2]:
    st.markdown("### Team 2")
    render_team_lineup(st, team2_lineup, "team2")

# Calculate and display total points per team
def calculate_total(lineup):
    total = 0
    for slot in lineup.values():
        row = scoreboard[scoreboard['Slot'] == slot].iloc[0]
        total += row["Fantasy Points"]
    return total

team1_total = calculate_total(team1_lineup)
team2_total = calculate_total(team2_lineup)

st.markdown(f"### Total Points: Team 1 = {team1_total} | Team 2 = {team2_total}")
