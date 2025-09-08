import pandas as pd
import streamlit as st

# ----------------------------
# Load scoreboard CSV
# ----------------------------
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

# Extract position for color mapping
def get_position(slot):
    return ''.join([c for c in slot.split()[1] if not c.isdigit()])

team1_df['position'] = team1_df['Slot'].apply(get_position)
team2_df['position'] = team2_df['Slot'].apply(get_position)

# ----------------------------
# Position color mapping
# ----------------------------
pos_colors = {
    'QB': '#FFD700',   # Gold
    'RB': '#87CEFA',   # Light Blue
    'WR': '#90EE90',   # Light Green
    'TE': '#FFA07A',   # Light Salmon
    'K':  '#D3D3D3',   # Light Gray
    'DEF':'#FFB6C1'    # Light Pink
}

# ----------------------------
# Background styling
# ----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom, #000000, #1a1a1a);
        color: white;
    }
    .card {
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.5);
        background-color: #2c2c2c;
    }
    .position-label {
        font-weight: bold;
        text-align: center;
        padding: 8px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Title
# ----------------------------
st.markdown("<h1 style='text-align: center;'>🏈 College Football Fantasy Scoreboard</h1>", unsafe_allow_html=True)

# ----------------------------
# Align matchups by position
# ----------------------------
all_positions = sorted(set(team1_df['position']).union(set(team2_df['position'])))

for pos in all_positions:
    col1, col2, col3 = st.columns([4, 2, 4])  # left, middle, right

    team1_players = team1_df[team1_df['position'] == pos]
    team2_players = team2_df[team2_df['position'] == pos]

    color = pos_colors.get(pos, '#444444')

    # Left: Team 1 players
    with col1:
        for _, row in team1_players.iterrows():
            st.markdown(
                f"""
                <div class="card">
                    <div style="background-color:{color}; padding:6px; border-radius:6px; font-weight:bold;">
                        {row['Slot']}
                    </div>
                    <div style="margin-top:6px;">
                        {row['Player']} | {row['Fantasy Points']} pts <br>
                        <a href="{row['Roster URL']}" target="_blank">Roster</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # Middle: Position indicator
    with col2:
        st.markdown(
            f"""
            <div class="position-label" style="background-color:{color};">
                {pos}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Right: Team 2 players
    with col3:
        for _, row in team2_players.iterrows():
            st.markdown(
                f"""
                <div class="card">
                    <div style="background-color:{color}; padding:6px; border-radius:6px; font-weight:bold;">
                        {row['Slot']}
                    </div>
                    <div style="margin-top:6px;">
                        {row['Player']} | {row['Fantasy Points']} pts <br>
                        <a href="{row['Roster URL']}" target="_blank">Roster</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

