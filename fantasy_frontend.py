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
st.markdown("<h1 style='text-align: center;'>🏈 College Football Fantasy Matchup</h1>", unsafe_allow_html=True)

# ----------------------------
# Interactive selection
# ----------------------------
all_positions = sorted(set(team1_df['position']).union(set(team2_df['position'])))

team1_total, team2_total = 0, 0

for pos in all_positions:
    col1, col2, col3 = st.columns([4, 2, 4])

    team1_players = team1_df[team1_df['position'] == pos]
    team2_players = team2_df[team2_df['position'] == pos]

    color = pos_colors.get(pos, '#444444')

    # Left: Team 1 selection
    with col1:
        if not team1_players.empty:
            label_options = team1_players['Slot'].tolist()
            choice = st.selectbox(f"{team1} {pos}", label_options, key=f"{team1}_{pos}")
            row = team1_players[team1_players['Slot'] == choice].iloc[0]
            st.markdown(
                f"""
                <div class="card">
                    <div style="background-color:{color}; padding:6px; border-radius:6px; font-weight:bold;">
                        {row['Slot']}
                    </div>
                    <div style="margin-top:6px;">
                        {row['Fantasy Points']} pts <br>
                        <a href="{row['Roster URL']}" target="_blank">Roster</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            team1_total += row['Fantasy Points']

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

    # Right: Team 2 selection
    with col3:
        if not team2_players.empty:
            label_options = team2_players['Slot'].tolist()
            choice = st.selectbox(f"{team2} {pos}", label_options, key=f"{team2}_{pos}")
            row = team2_players[team2_players['Slot'] == choice].iloc[0]
            st.markdown(
                f"""
                <div class="card">
                    <div style="background-color:{color}; padding:6px; border-radius:6px; font-weight:bold;">
                        {row['Slot']}
                    </div>
                    <div style="margin-top:6px;">
                        {row['Fantasy Points']} pts <br>
                        <a href="{row['Roster URL']}" target="_blank">Roster</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            team2_total += row['Fantasy Points']

# ----------------------------
# Team totals
# ----------------------------
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<h2 style='text-align: center;'>{team1} Total: {team1_total:.1f} pts</h2>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<h2 style='text-align: center;'>{team2} Total: {team2_total:.1f} pts</h2>", unsafe_allow_html=True)
