import pandas as pd
import streamlit as st

# Load scoreboard CSV
scoreboard = pd.read_csv("fantasy_scoreboard.csv")

# Extract position from Slot (e.g. "Alabama QB1" → "QB")
def get_position(slot):
    return ''.join([c for c in slot.split()[1] if not c.isdigit()])

scoreboard['position'] = scoreboard['Slot'].apply(get_position)

# Define fantasy slots with duplicates (RB, WR, etc.)
fantasy_slots = ["QB", "RB", "RB", "WR", "WR", "TE", "K", "DEF"]

# Define position colors
pos_colors = {
    'QB': '#FFD700',   # Gold
    'RB': '#87CEFA',   # Light Blue
    'WR': '#90EE90',   # Light Green
    'TE': '#FFA07A',   # Light Salmon
    'K':  '#D3D3D3',   # Light Gray
    'DEF':'#FFB6C1'    # Light Pink
}

# Custom CSS for gradient background
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(180deg, #000000, #1a1a1a, #000000);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown("<h1 style='text-align:center;'>🏈 College Football Fantasy Matchup</h1>", unsafe_allow_html=True)

# Build player options
options_by_pos = {}
for pos in set(fantasy_slots):  # unique positions
    options = scoreboard[scoreboard['position'] == pos]['Slot'].tolist()
    options_by_pos[pos] = [""] + options  # empty option for unselected

# Team 1 and Team 2 lineups
st.markdown("### Team 1 vs Team 2")

cols = st.columns([4, 1, 4])  # left, middle, right

team1_lineup = {}
team2_lineup = {}

for i, pos in enumerate(fantasy_slots):
    with cols[0]:
        team1_lineup[f"{pos}{i}"] = st.selectbox(
            f"Team 1 {pos}",
            options_by_pos[pos],
            key=f"team1_{pos}_{i}"
        )
    with cols[1]:
        color = pos_colors.get(pos, "#FFFFFF")
        st.markdown(
            f"<div style='text-align:center; font-weight:bold; background-color:{color}; padding:8px; border-radius:5px; margin: 8px 0;'>{pos}</div>",
            unsafe_allow_html=True
        )
    with cols[2]:
        team2_lineup[f"{pos}{i}"] = st.selectbox(
            f"Team 2 {pos}",
            options_by_pos[pos],
            key=f"team2_{pos}_{i}"
        )

# Score calculation with safe lookup
def calculate_score(lineup):
    total = 0
    details = []
    for _, player_slot in lineup.items():
        if not player_slot:  # skip empty
            continue
        match = scoreboard[scoreboard['Slot'] == player_slot]
        if match.empty:  # skip invalid
            continue
        row = match.iloc[0]
        total += row['Fantasy Points']
        details.append(f"{player_slot}: {row['Fantasy Points']} pts")
    return total, details

# Compute team scores
team1_score, team1_details = calculate_score(team1_lineup)
team2_score, team2_details = calculate_score(team2_lineup)

# Show results
st.markdown("## 🏆 Results")
cols = st.columns(2)

with cols[0]:
    st.subheader(f"Team 1 Total: {team1_score:.1f} pts")
    st.write("\n".join(team1_details))

with cols[1]:
    st.subheader(f"Team 2 Total: {team2_score:.1f} pts")
    st.write("\n".join(team2_details))
