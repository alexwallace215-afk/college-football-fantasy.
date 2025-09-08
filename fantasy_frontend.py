import pandas as pd
import streamlit as st

# -----------------------
# 1. Load Fantasy Scoreboard CSV
# -----------------------
scoreboard = pd.read_csv("fantasy_scoreboard.csv")

# -----------------------
# 2. Define Teams
# -----------------------
scoreboard['team'] = scoreboard['Slot'].apply(lambda x: x.split()[0])
teams = scoreboard['team'].unique()

if len(teams) != 2:
    st.warning("Expected exactly 2 teams for matchup view.")
    st.stop()

team1_name, team2_name = teams

team1_df = scoreboard[scoreboard['team'] == team1_name].copy()
team2_df = scoreboard[scoreboard['team'] == team2_name].copy()

# -----------------------
# 3. Define Positions & Color Mapping
# -----------------------
positions_order = ["QB", "RB", "RB", "WR", "WR", "TE", "K", "DEF"]

pos_colors = {
    'QB': '#FFD700',  # Gold
    'RB': '#87CEFA',  # Light Blue
    'WR': '#90EE90',  # Light Green
    'TE': '#FFA07A',  # Light Salmon
    'K':  '#D3D3D3',  # Light Gray
    'DEF':'#FFB6C1'   # Light Pink
}

# -----------------------
# 4. Prepare Options for SelectBoxes
# -----------------------
def get_slot_label(row):
    return f"{row['team']} {row['position']}{row['depth']}"

team1_df['slot_label'] = team1_df.apply(get_slot_label, axis=1)
team2_df['slot_label'] = team2_df.apply(get_slot_label, axis=1)

options_by_pos = {}
for pos in positions_order:
    options_by_pos[pos] = list(team1_df[team1_df['position']==pos]['slot_label']) + \
                           list(team2_df[team2_df['position']==pos]['slot_label'])

# -----------------------
# 5. Streamlit Layout & Styles
# -----------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, #000000, #1a1a1a);
        color: white;
    }
    a {color: #00FFFF;}
</style>
""", unsafe_allow_html=True)

st.markdown("## 🏈 College Football Fantasy Matchup")

cols = st.columns([1,0.5,1])  # Team1 | Position | Team2

# -----------------------
# 6. Selection Widgets
# -----------------------
team1_lineup = {}
team2_lineup = {}

with cols[0]:
    st.markdown(f"### {team1_name}")
    for idx, pos in enumerate(positions_order):
        unique_key = f"team1_{pos}_{idx}"
        team1_lineup[pos] = st.selectbox(
            f"{pos} Slot",
            options_by_pos[pos],
            key=unique_key
        )

with cols[2]:
    st.markdown(f"### {team2_name}")
    for idx, pos in enumerate(positions_order):
        unique_key = f"team2_{pos}_{idx}"
        team2_lineup[pos] = st.selectbox(
            f"{pos} Slot",
            options_by_pos[pos],
            key=unique_key
        )

# -----------------------
# 7. Position Indicators
# -----------------------
with cols[1]:
    for pos in positions_order:
        color = pos_colors.get(pos, '#FFFFFF')
        st.markdown(f"""
        <div style="
            background-color:{color};
            padding:8px;
            border-radius:5px;
            text-align:center;
            font-weight:bold;
            margin-bottom:10px;
        ">{pos}</div>
        """, unsafe_allow_html=True)

# -----------------------
# 8. Helper Function to Get Fantasy Points
# -----------------------
def get_points(slot_label):
    row = scoreboard[scoreboard['Slot'] == slot_label]
    if not row.empty:
        return float(row['Fantasy Points'].values[0])
    else:
        return 0.0

# -----------------------
# 9. Calculate Team Totals
# -----------------------
team1_points = sum(get_points(slot) for slot in team1_lineup.values())
team2_points = sum(get_points(slot) for slot in team2_lineup.values())

# -----------------------
# 10. Display Live Scoring Table
# -----------------------
st.markdown("## 🏟️ Live Matchup Table")

live_table = pd.DataFrame({
    "Position": positions_order,
    f"{team1_name} Slot": [team1_lineup[pos] for pos in positions_order],
    f"{team1_name} Points": [get_points(team1_lineup[pos]) for pos in positions_order],
    "Position Indicator": positions_order,
    f"{team2_name} Slot": [team2_lineup[pos] for pos in positions_order],
    f"{team2_name} Points": [get_points(team2_lineup[pos]) for pos in positions_order],
})

# Display table with Streamlit
st.dataframe(live_table, use_container_width=True)

st.markdown(f"### {team1_name} Total: {team1_points:.1f} pts | {team2_name} Total: {team2_points:.1f} pts")
