import pandas as pd
import streamlit as st

# -----------------------
# 1. Load CSV
# -----------------------
scoreboard = pd.read_csv("fantasy_scoreboard.csv")

# -----------------------
# 2. Extract teams
# -----------------------
scoreboard['team'] = scoreboard['Slot'].apply(lambda x: x.split()[0])
teams = scoreboard['team'].unique()

if len(teams) != 2:
    st.warning("Expected exactly 2 teams for matchup view.")
    st.stop()

team1, team2 = teams
team1_df = scoreboard[scoreboard['team'] == team1].copy()
team2_df = scoreboard[scoreboard['team'] == team2].copy()

# -----------------------
# 3. Extract position from Slot for color coding
# -----------------------
def get_position(slot):
    # Example: 'Alabama QB1' -> 'QB'
    return ''.join([c for c in slot.split()[1] if not c.isdigit()])

team1_df['position'] = team1_df['Slot'].apply(get_position)
team2_df['position'] = team2_df['Slot'].apply(get_position)

# -----------------------
# 4. Define color mapping for positions
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
# 5. Title
# -----------------------
st.markdown("## 🏈 College Football Fantasy Scoreboard")

# -----------------------
# 6. Horizontal matchup layout
# -----------------------
cols = st.columns(2)

def render_cards(df, col):
    for _, row in df.iterrows():
        color = pos_colors.get(row['position'], '#FFFFFF')
        col.markdown(f"""
        <div style="
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        ">
            <div style="background-color:{color}; padding:5px; border-radius:5px; font-weight:bold;">
                {row['Slot']}
            </div>
            <div style="margin-top:5px;">
                {row['Player']} | {row['Fantasy Points']} pts <br>
                <a href="{row['Roster URL']}" target="_blank">Roster</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

with cols[0]:
    st.markdown("### Team 1")
    render_cards(team1_df, st)

with cols[1]:
    st.markdown("### Team 2")
    render_cards(team2_df, st)

