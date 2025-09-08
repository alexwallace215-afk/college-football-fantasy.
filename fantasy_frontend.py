import pandas as pd
import streamlit as st

# ==========================
# Load scoreboard CSV
# ==========================
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

# Extract position (QB, RB, WR, etc.)
def get_position(slot):
    return ''.join([c for c in slot.split()[1] if not c.isdigit()])

team1_df['position'] = team1_df['Slot'].apply(get_position)
team2_df['position'] = team2_df['Slot'].apply(get_position)

# ==========================
# Custom CSS for UI
# ==========================
st.markdown("""
    <style>
    /* Whole page background */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }

    /* Team headers */
    .team-header {
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .team1-header {
        background: rgba(220,20,60,0.8); /* Crimson Red */
        color: white;
    }
    .team2-header {
        background: rgba(30,144,255,0.8); /* Dodger Blue */
        color: white;
    }

    /* Position label (middle slot indicator) */
    .position-label {
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin-top: 12px;
        margin-bottom: 12px;
        color: #FFD700;  /* Gold highlight */
    }

    /* Player cards */
    .card {
        border-radius: 12px;
        padding: 10px;
        margin: 5px 0px;
        background: rgba(255,255,255,0.1);  /* semi-transparent */
        box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        color: white;
    }

    /* Slot label (QB1, RB1, etc.) */
    .slot-label {
        border-radius: 6px;
        padding: 6px;
        font-weight: bold;
        margin-bottom: 5px;
        color: black;
    }

    /* Points style */
    .points {
        font-size: 16px;
        font-weight: bold;
        color: #FFD700;
    }

    /* Links */
    a {
        color: #87CEFA;
        text-decoration: none;
        font-weight: bold;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================
# Title
# ==========================
st.markdown("## 🏈 College Football Fantasy Matchup")

# ==========================
# Matchup columns
# ==========================
cols = st.columns([4, 1, 4])

# Render team headers
with cols[0]:
    st.markdown('<div class="team-header team1-header">Team 1</div>', unsafe_allow_html=True)
with cols[2]:
    st.markdown('<div class="team-header team2-header">Team 2</div>', unsafe_allow_html=True)

# Group by position (so we get QB, RB, WR, etc.)
positions = sorted(set(team1_df['position']).union(set(team2_df['position'])))

for pos in positions:
    team1_pos = team1_df[team1_df['position'] == pos]
    team2_pos = team2_df[team2_df['position'] == pos]

    max_len = max(len(team1_pos), len(team2_pos))

    for i in range(max_len):
        p1 = team1_pos.iloc[i] if i < len(team1_pos) else None
        p2 = team2_pos.iloc[i] if i < len(team2_pos) else None

        with cols[0]:
            if p1 is not None:
                st.markdown(f"""
                <div class="card">
                    <div class="slot-label" style="background-color:#444;">{p1['Slot']}</div>
                    {p1['Player']} <br>
                    <span class="points">{p1['Fantasy Points']} pts</span><br>
                    <a href="{p1['Roster URL']}" target="_blank">Roster</a>
                </div>
                """, unsafe_allow_html=True)

        with cols[1]:
            st.markdown(f'<div class="position-label">{pos}</div>', unsafe_allow_html=True)

        with cols[2]:
            if p2 is not None:
                st.markdown(f"""
                <div class="card">
                    <div class="slot-label" style="background-color:#444;">{p2['Slot']}</div>
                    {p2['Player']} <br>
                    <span class="points">{p2['Fantasy Points']} pts</span><br>
                    <a href="{p2['Roster URL']}" target="_blank">Roster</a>
                </div>
                """, unsafe_allow_html=True)
