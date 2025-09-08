import pandas as pd
import streamlit as st

# ---------------- Load CSVs ----------------
try:
    scoreboard = pd.read_csv("fantasy_scoreboard.csv")
    scoreboard.columns = scoreboard.columns.str.strip()  # Remove extra spaces

    teams = pd.read_csv("teams.csv")
    teams.columns = teams.columns.str.strip()
except Exception as e:
    st.error(f"Error loading CSVs: {e}")
    st.stop()

# ---------------- Check required columns ----------------
required_scoreboard_cols = {"team_id", "position", "depth", "Fantasy Points"}
required_team_cols = {"team_id", "team_name", "roster_url"}

if not required_scoreboard_cols.issubset(scoreboard.columns):
    st.error(f"Missing columns in scoreboard CSV: {required_scoreboard_cols - set(scoreboard.columns)}")
    st.stop()

if not required_team_cols.issubset(teams.columns):
    st.error(f"Missing columns in teams CSV: {required_team_cols - set(teams.columns)}")
    st.stop()

# ---------------- Data preprocessing ----------------
team_name_map = dict(zip(teams['team_id'].astype(str), teams['team_name']))
team_roster_map = dict(zip(teams['team_id'].astype(str), teams['roster_url']))

# Generate Slot column dynamically: e.g., Alabama RB1
scoreboard['Slot'] = scoreboard.apply(
    lambda row: f"{team_name_map.get(str(row['team_id']), 'Team'+str(row['team_id']))} {row['position'].upper()}{int(row['depth'])}",
    axis=1
)

# Ensure numeric columns
scoreboard['Fantasy Points'] = pd.to_numeric(scoreboard['Fantasy Points'], errors='coerce').fillna(0)
scoreboard['depth'] = pd.to_numeric(scoreboard['depth'], errors='coerce').fillna(1)

# ---------------- CSS styling ----------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #1a1a1a, #2e2e2e);  /* Darker gradient */
        color: #ffffff;
    }
    .dropdown-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .middle-pos {
        text-align: center;
        font-weight: bold;
        border-radius: 5px;
        padding: 12px 0;
    }
    .row-even {
        background-color: #2a2a2a;
        padding: 4px;
        border-radius: 5px;
    }
    .row-odd {
        background-color: #383838;
        padding: 4px;
        border-radius: 5px;
    }
    a {
        color: #FFD700;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 🏈 College Football Fantasy Scoreboard")

positions_order = ["QB", "RB", "RB", "WR", "WR", "TE", "K"]
pos_colors = {
    "QB": "#FFD700",
    "RB": "#87CEFA",
    "WR": "#90EE90",
    "TE": "#FFA07A",
    "K": "#D3D3D3",
}

# Dropdown options per position
options_by_pos = {}
for pos in ["QB", "RB", "WR", "TE", "K"]:
    options_by_pos[pos] = scoreboard[scoreboard['position'] == pos]['Slot'].tolist()

# Initialize session state for independent slots
if "team1_lineup" not in st.session_state:
    st.session_state.team1_lineup = {}
if "team2_lineup" not in st.session_state:
    st.session_state.team2_lineup = {}

# ---------------- Team vs Team header ----------------
header_cols = st.columns([1, 0.3, 1])
header_cols[0].markdown("### Team 1")
header_cols[1].markdown("### vs")
header_cols[2].markdown("### Team 2")

# Track duplicates to generate unique slot keys
pos_count = {}
row_index = 0  # For alternating row shading

for pos in positions_order:
    if pos not in options_by_pos or not options_by_pos[pos]:
        continue
    pos_count[pos] = pos_count.get(pos, 0) + 1
    index_suffix = pos_count[pos]

    # Unique slot keys
    key1 = f"{pos}_{index_suffix}_team1"
    key2 = f"{pos}_{index_suffix}_team2"

    # Initialize session state if empty
    if key1 not in st.session_state.team1_lineup:
        st.session_state.team1_lineup[key1] = options_by_pos[pos][0]
    if key2 not in st.session_state.team2_lineup:
        st.session_state.team2_lineup[key2] = options_by_pos[pos][0]

    # Choose row style for zebra stripes
    row_class = "row-even" if row_index % 2 == 0 else "row-odd"
    row_index += 1

    # Outer 3 columns
    row_cols = st.columns([1, 0.3, 1])

    # ---------------- Team 1 dropdown + points ----------------
    with row_cols[0]:
        st.markdown(f"<div class='{row_class}'>", unsafe_allow_html=True)
        inner_cols = st.columns([2, 1])
        slot1 = st.session_state.team1_lineup[key1]
        selection1 = inner_cols[0].selectbox("", options_by_pos[pos], index=options_by_pos[pos].index(slot1), key=key1)
        st.session_state.team1_lineup[key1] = selection1

        player1_row = scoreboard[scoreboard['Slot'] == selection1].iloc[0]
        points1 = player1_row["Fantasy Points"]
        roster1 = team_roster_map.get(str(player1_row["team_id"]), "#")
        inner_cols[1].markdown(f"<div class='dropdown-row'><span style='font-weight:bold'>{points1} pts</span> | <a href='{roster1}' target='_blank'>Roster</a></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Middle position indicator ----------------
    row_cols[1].markdown(
        f"<div class='middle-pos' style='background-color:{pos_colors.get(pos,'#FFFFFF')}'>{pos}</div>",
        unsafe_allow_html=True
    )

    # ---------------- Team 2 dropdown + points ----------------
    with row_cols[2]:
        st.markdown(f"<div class='{row_class}'>", unsafe_allow_html=True)
        inner_cols = st.columns([2, 1])
        slot2 = st.session_state.team2_lineup[key2]
        selection2 = inner_cols[0].selectbox("", options_by_pos[pos], index=options_by_pos[pos].index(slot2), key=key2)
        st.session_state.team2_lineup[key2] = selection2

        player2_row = scoreboard[scoreboard['Slot'] == selection2].iloc[0]
        points2 = player2_row["Fantasy Points"]
        roster2 = team_roster_map.get(str(player2_row["team_id"]), "#")
        inner_cols[1].markdown(f"<div class='dropdown-row'><span style='font-weight:bold'>{points2} pts</span> | <a href='{roster2}' target='_blank'>Roster</a></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Total points ----------------
def calculate_total(lineup):
    total = 0
    for slot in lineup.values():
        row = scoreboard[scoreboard['Slot'] == slot].iloc[0]
        total += row["Fantasy Points"]
    return total

team1_total = calculate_total(st.session_state.team1_lineup)
team2_total = calculate_total(st.session_state.team2_lineup)

st.markdown(f"### Total Points: Team 1 = {team1_total} | Team 2 = {team2_total}")
