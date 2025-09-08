import pandas as pd
import streamlit as st

# Load player pool
scoreboard = pd.read_csv("fantasy_scoreboard.csv")

# Extract position (QB, RB, WR, etc.) from Slot
def get_position(slot):
    return ''.join([c for c in slot.split()[1] if not c.isdigit()])

scoreboard['position'] = scoreboard['Slot'].apply(get_position)

# Lineup template
lineup_template = ["QB", "RB", "RB", "WR", "WR", "TE", "K", "DEF"]

# Position color mapping
pos_colors = {
    'QB': '#FFD700',  # Gold
    'RB': '#87CEFA',  # Light Blue
    'WR': '#90EE90',  # Light Green
    'TE': '#FFA07A',  # Salmon
    'K':  '#D3D3D3',  # Gray
    'DEF':'#FFB6C1'   # Pink
}

# Title
st.markdown(
    """
    <h1 style='text-align:center; color:white;'>
        🏈 College Fantasy Matchup
    </h1>
    """,
    unsafe_allow_html=True,
)

team1_lineup = {}
team2_lineup = {}

# ------------------------
# Render lineup row by row
# ------------------------
for pos in lineup_template:
    col1, col2, col3 = st.columns([4, 2, 4])

    with col1:
        choice = st.selectbox(
            f"Team 1 {pos}",
            options=scoreboard[scoreboard['position'] == pos]['Slot'].tolist(),
            key=f"team1_{pos}_{len(team1_lineup)}"
        )
        team1_lineup[pos] = choice

    with col2:
        st.markdown(
            f"<div style='text-align:center; background-color:{pos_colors.get(pos, '#333')}; "
            f"color:black; font-weight:bold; padding:5px; border-radius:5px; margin:5px;'>{pos}</div>",
            unsafe_allow_html=True,
        )

    with col3:
        choice = st.selectbox(
            f"Team 2 {pos}",
            options=scoreboard[scoreboard['position'] == pos]['Slot'].tolist(),
            key=f"team2_{pos}_{len(team2_lineup)}"
        )
        team2_lineup[pos] = choice

# ------------------------
# Show scores + totals
# ------------------------
def calculate_score(lineup):
    total = 0
    details = []
    for pos, player_slot in lineup.items():
        row = scoreboard[scoreboard['Slot'] == player_slot].iloc[0]
        points = row['Fantasy Points']
        total += points
        details.append(f"{player_slot}: {points} pts")
    return total, details

team1_score, team1_details = calculate_score(team1_lineup)
team2_score, team2_details = calculate_score(team2_lineup)

st.markdown("---")
st.subheader("📊 Matchup Results")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Team 1")
    for d in team1_details:
        st.write(d)
    st.markdown(f"**Total: {team1_score} pts**")

with col2:
    st.markdown("### Team 2")
    for d in team2_details:
        st.write(d)
    st.markdown(f"**Total: {team2_score} pts**")
