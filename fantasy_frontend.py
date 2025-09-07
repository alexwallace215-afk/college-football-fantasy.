# fantasy_frontend.py
import pandas as pd
import streamlit as st
from pathlib import Path

# -----------------------
# Load scoreboard CSV
# -----------------------
CSV_PATH = Path("fantasy_scoreboard.csv")
if not CSV_PATH.exists():
    st.error("fantasy_scoreboard.csv not found in repository root. Add it and redeploy.")
    st.stop()

scoreboard = pd.read_csv(CSV_PATH)
# sanitize column names
scoreboard.columns = scoreboard.columns.str.strip()

# -----------------------
# Basic validation & setup
# -----------------------
required_cols = {'Slot', 'Player', 'Fantasy Points', 'Roster URL'}
if not required_cols.issubset(set(scoreboard.columns)):
    st.error(f"fantasy_scoreboard.csv is missing one of the required columns: {required_cols}")
    st.stop()

# Extract team and position
scoreboard['team'] = scoreboard['Slot'].apply(lambda x: x.split()[0])
def get_position(slot):
    # Takes the 'QB1' part and strips digits to 'QB'
    try:
        return ''.join([c for c in slot.split()[1] if not c.isdigit()])
    except Exception:
        return ''

scoreboard['position'] = scoreboard['Slot'].apply(get_position)

teams = scoreboard['team'].unique()
if len(teams) != 2:
    st.warning("Expected exactly 2 teams (for a single matchup). Found: " + ", ".join(map(str, teams)))
    # still continue; allow broad display if more/less teams
    if len(teams) < 2:
        st.stop()

team_left = teams[0]
team_right = teams[1]

left_df = scoreboard[scoreboard['team'] == team_left].copy().reset_index(drop=True)
right_df = scoreboard[scoreboard['team'] == team_right].copy().reset_index(drop=True)

# -----------------------
# lineup slots (standard)
# -----------------------
lineup = {
    "QB": 1,
    "RB": 2,
    "WR": 2,
    "TE": 1,
    "K": 1,
    "DEF": 1
}

# -----------------------
# colors
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
# App UI
# -----------------------
st.set_page_config(layout="wide", page_title="College Football Fantasy Matchup")
st.markdown("## 🏈 College Football Fantasy Matchup (Slot-based)")

st.write("Select which team slot (e.g. `Alabama RB1`) fills each positional starter. Dropdowns only show that team's available slots for the position.")
st.write("---")

# keep totals
left_total = 0.0
right_total = 0.0

# We'll create stable keys by using slot name plus side
for pos, count in lineup.items():
    for slot_index in range(count):
        cols = st.columns([4, 2, 4])  # left select | pos card | right select

        # left options: list of "Slot" values for left_df with this position
        left_options = left_df[left_df['position'] == pos]['Slot'].tolist()
        # right options
        right_options = right_df[right_df['position'] == pos]['Slot'].tolist()

        with cols[0]:
            label_left = f"{team_left} {pos}" if count == 1 else f"{team_left} {pos}"
            # If there are no available slots, show a disabled selectbox with placeholder
            if left_options:
                chosen_left = st.selectbox(label_left, options=left_options, key=f"left_{pos}_{slot_index}")
            else:
                st.write("—")
                chosen_left = None

            # Display points for chosen left slot (slot label, not player name)
            if chosen_left:
                row = left_df[left_df['Slot'] == chosen_left].iloc[0]
                points = pd.to_numeric(row['Fantasy Points'], errors='coerce')
                if not pd.isna(points):
                    left_total += float(points)
                # show slot label & points & roster link (no player's personal name in the dropdown)
                st.markdown(f"**{chosen_left}** — {points:.1f} pts  \n[Roster]({row['Roster URL']})")

        with cols[1]:
            color = pos_colors.get(pos, "#FFFFFF")
            st.markdown(f"""
                <div style="
                    text-align:center;
                    background-color:{color};
                    padding:12px;
                    border-radius:8px;
                    font-weight:700;
                    font-size:16px;
                    margin:auto;
                ">{pos}</div>
            """, unsafe_allow_html=True)

        with cols[2]:
            label_right = f"{team_right} {pos}" if count == 1 else f"{team_right} {pos}"
            if right_options:
                chosen_right = st.selectbox(label_right, options=right_options, key=f"right_{pos}_{slot_index}")
            else:
                st.write("—")
                chosen_right = None

            if chosen_right:
                row = right_df[right_df['Slot'] == chosen_right].iloc[0]
                points = pd.to_numeric(row['Fantasy Points'], errors='coerce')
                if not pd.isna(points):
                    right_total += float(points)
                st.markdown(f"**{chosen_right}** — {points:.1f} pts  \n[Roster]({row['Roster URL']})")

st.write("---")
# Totals
left_total = round(left_total, 1)
right_total = round(right_total, 1)

tot_cols = st.columns([4,2,4])
with tot_cols[0]:
    st.markdown(f"### Team 1 Total: **{left_total} pts**")
with tot_cols[1]:
    st.write("")  # center gap
with tot_cols[2]:
    st.markdown(f"### Team 2 Total: **{right_total} pts**")

st.markdown("---")
st.caption("Dropdowns select slots (e.g. `Alabama RB1`) that map internally to an actual player. No player names are shown in the selectors.")

