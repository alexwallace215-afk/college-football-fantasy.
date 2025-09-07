import pandas as pd
import streamlit as st

# -----------------------
# 1. Load scoreboard
# -----------------------
scoreboard = pd.read_csv("fantasy_scoreboard.csv")

# Extract team and position from Slot
scoreboard['team'] = scoreboard['Slot'].apply(lambda x: x.split()[0])
scoreboard['position'] = scoreboard['Slot'].apply(lambda x: ''.join([c for c in x.split()[1] if not c.isdigit()]))

teams = scoreboard['team'].unique()
if len(teams) != 2:
    st.warning("Expected exactly 2 teams for matchup view.")
    st.stop()
team1, team2 = teams

team1_df = scoreboard[scoreboard['team'] == team1].copy()
team2_df = scoreboard[scoreboard['team'] == team2].copy()

# -----------------------
# 2. Filters for positions
# -----------------------
positions_filter = st.multiselect(
    "Filter by position",
    options=['QB', 'RB', 'WR', 'TE', 'K', 'DEF'],
    default=['QB', 'RB', 'WR', 'TE', 'K', 'DEF']
)

team1_df = team1_df[team1_df['position'].isin(positions_filter)]
team2_df = team2_df[team2_df['position'].isin(positions_filter)]

# -----------------------
# 3. Color mapping for positions
# -----------------------
pos_colors = {
    'QB': '#FFD700',   # Gold
    'RB': '#87CEFA',   # Light Blue
    'WR': '#90EE90',   # Light Green
    'TE': '#FFA07A',   # Light Salmon
    'K':  '#D3D3D3',   # Light Gray
    'DEF':'#FFB6C1'    # Light Pink
}

# -----------------------
# 4. Title
# -----------------------
st.markdown("## 🏈 College Football Fantasy Scoreboard")

# -----------------------
# 5. Render horizontal matchup columns
# -----------------------
cols = st.columns(2)

def render_slot_picker(df, col_title):
    col_selected = {}
    col.markdown(f"### {col_title}")
    for _, row in df.iterrows():
        # Available players for this position
        available_players = scoreboard[scoreboard['position'] == row['position']]['Player'].tolist()
        # Dropdown to select player
        selected = col.selectbox(f"{row['Slot']}", available_players, key=row['Slot'])
        col_selected[row['Slot']] = selected
    return col_selected

with cols[0]:
    team1_selected = render_slot_picker(team1_df, "Team 1")

with cols[1]:
    team2_selected = render_slot_picker(team2_df, "Team 2")

# -----------------------
# 6. Display selected lineups as color-coded cards
# -----------------------
st.markdown("### Your Selected Lineups")

lineup_cols = st.columns(2)

def render_cards(selected_dict, df, col):
    for slot, player_name in selected_dict.items():
        row = df[df['Slot'] == slot].iloc[0]
        color = pos_colors.get(row['position'], '#FFFFFF')
        col.markdown(f"""
        <div style="
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        ">
            <div style="background-color:{color}; padding:5px; border-radius:5px; font-weight:bold;">
                {slot}
            </div>
            <div style="margin-top:5px;">
                {player_name} | {row['Fantasy Points']} pts <br>
                <a href="{row['Roster URL']}" target="_blank">Roster</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

with lineup_cols[0]:
    render_cards(team1_selected, team1_df, st)

with lineup_cols[1]:
    render_cards(team

