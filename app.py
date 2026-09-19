import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IPL Data Analysis Dashboard", layout="wide")

# ---------- Data loading & cleaning (mirrors the notebook) ----------
@st.cache_data
def load_data():
    matches = pd.read_csv("data/matches.csv")
    deliveries = pd.read_csv("data/deliveries.csv")

    team_mapping = {
        "Delhi Daredevils": "Delhi Capitals",
        "Kings XI Punjab": "Punjab Kings",
        "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
        "Rising Pune Supergiant": "Rising Pune Supergiants",
    }
    for col in ["team1", "team2", "toss_winner", "winner"]:
        matches[col] = matches[col].replace(team_mapping)
    for col in ["batting_team", "bowling_team"]:
        deliveries[col] = deliveries[col].replace(team_mapping)

    matches["toss_match_winner"] = matches["toss_winner"] == matches["winner"]
    return matches, deliveries


matches, deliveries = load_data()

st.title("🏏 IPL Data Analysis Dashboard")
st.caption("Interactive version of the IPL match & ball-by-ball analysis notebook.")

# ---------- Sidebar filters ----------
seasons = sorted(matches["season"].dropna().unique().tolist())
selected_seasons = st.sidebar.multiselect("Filter by season", seasons, default=seasons)

filtered_matches = matches[matches["season"].isin(selected_seasons)]
filtered_match_ids = filtered_matches["id"].unique()
filtered_deliveries = deliveries[deliveries["match_id"].isin(filtered_match_ids)]

st.sidebar.markdown("---")
st.sidebar.caption(f"{len(filtered_matches)} matches in current selection")

tabs = st.tabs([
    "Overview",
    "Toss Analysis",
    "Team Performance",
    "Batting",
    "Bowling",
    "Venue & Margins",
    "Head-to-Head",
])

# ---------- Overview ----------
with tabs[0]:
    col1, col2, col3 = st.columns(3)
    col1.metric("Matches", len(filtered_matches))
    col2.metric("Seasons", filtered_matches["season"].nunique())
    col3.metric("Teams", pd.concat([filtered_matches["team1"], filtered_matches["team2"]]).nunique())
    st.dataframe(filtered_matches.head(20), use_container_width=True)

# ---------- Toss Analysis ----------
with tabs[1]:
    st.subheader("Does winning the toss help win the match?")
    decided = filtered_matches[filtered_matches["winner"].notna()]

    toss_impact = decided["toss_match_winner"].value_counts(normalize=True).rename(
        index={True: "Toss winner won", False: "Toss winner lost"}
    ) * 100
    fig1 = px.bar(
        toss_impact, x=toss_impact.index, y=toss_impact.values,
        labels={"x": "", "y": "% of matches"}, text_auto=".1f",
        title="Toss Winner vs Match Winner",
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Bat first or field first?")
    toss_decision_success = decided.groupby("toss_decision")["toss_match_winner"].mean() * 100
    fig2 = px.bar(
        toss_decision_success, x=toss_decision_success.index, y=toss_decision_success.values,
        labels={"x": "Toss decision", "y": "Win % when chosen"}, text_auto=".1f",
        title="Toss Winner Success Rate by Decision",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Team Performance ----------
with tabs[2]:
    st.subheader("Win percentage by team")
    played = (filtered_matches["team1"].value_counts() + filtered_matches["team2"].value_counts()).fillna(0)
    wins = filtered_matches["winner"].value_counts()
    win_percentage = (wins / played * 100).dropna().sort_values(ascending=True)

    fig3 = px.bar(
        win_percentage, x=win_percentage.values, y=win_percentage.index,
        orientation="h", labels={"x": "Win %", "y": "Team"}, text_auto=".1f",
        title="Win Percentage by Team",
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Wins by team, per season")
    season_team_pivot = filtered_matches.groupby(["season", "winner"]).size().unstack(fill_value=0)

    # Order teams by total wins (most successful at top) instead of alphabetically,
    # and only keep teams that actually won at least one match in the selected seasons.
    team_totals = season_team_pivot.sum(axis=0).sort_values(ascending=False)
    ordered_teams = team_totals[team_totals > 0].index
    heatmap_data = season_team_pivot[ordered_teams].T

    fig4 = px.imshow(
        heatmap_data, aspect="auto", color_continuous_scale="YlGnBu",
        text_auto=True,  # show the actual win count in every cell
        labels=dict(x="Season", y="Team", color="Wins"),
        title="Team Wins by Season (sorted by total wins, top to bottom)",
    )
    fig4.update_layout(height=max(400, 28 * len(ordered_teams)))
    fig4.update_xaxes(type="category")
    st.plotly_chart(fig4, use_container_width=True)

# ---------- Batting ----------
with tabs[3]:
    st.subheader("Top run scorers")
    top_run_scorer = filtered_deliveries.groupby("batter")["batsman_runs"].sum().sort_values(ascending=False).head(10)
    fig5 = px.bar(
        top_run_scorer, x=top_run_scorer.values, y=top_run_scorer.index,
        orientation="h", labels={"x": "Total runs", "y": "Batter"},
        title="Top 10 Run Scorers",
    )
    fig5.update_yaxes(autorange="reversed")
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Best strike rates (min 100 balls faced)")
    batting_stats = filtered_deliveries.groupby("batter").agg(
        runs=("batsman_runs", "sum"), balls=("batter", "count")
    )
    batting_stats["strike_rate"] = batting_stats["runs"] / batting_stats["balls"] * 100
    qualified_batters = batting_stats[batting_stats["balls"] >= 100].sort_values("strike_rate", ascending=False).head(10)
    fig6 = px.bar(
        qualified_batters, x="strike_rate", y=qualified_batters.index,
        orientation="h", labels={"strike_rate": "Strike rate", "y": "Batter"},
        title="Top 10 Strike Rates",
    )
    fig6.update_yaxes(autorange="reversed")
    st.plotly_chart(fig6, use_container_width=True)

# ---------- Bowling ----------
with tabs[4]:
    st.subheader("Top wicket takers")
    dismissal_exclude = ["run out", "retired out", "obstructing the field", "retired hurt"]
    bowler_wickets = filtered_deliveries[~filtered_deliveries["dismissal_kind"].isin(dismissal_exclude)]
    wickets = bowler_wickets.groupby("bowler")["is_wicket"].sum().sort_values(ascending=False).head(10)
    fig7 = px.bar(
        wickets, x=wickets.values, y=wickets.index,
        orientation="h", labels={"x": "Wickets", "y": "Bowler"},
        title="Top 10 Wicket Takers",
    )
    fig7.update_yaxes(autorange="reversed")
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Best economy rate (min 300 legal balls bowled)")
    bowling_runs = filtered_deliveries[~filtered_deliveries["extras_type"].isin(["byes", "legbyes", "penalty"])].groupby("bowler")["total_runs"].sum()
    legal_balls = filtered_deliveries[~filtered_deliveries["extras_type"].isin(["wides", "noballs"])].groupby("bowler").size()
    bowling_stats = pd.DataFrame({"runs_conceded": bowling_runs, "legal_balls": legal_balls})
    bowling_stats["economy_rate"] = bowling_stats["runs_conceded"] / bowling_stats["legal_balls"] * 6
    qualified_bowlers = bowling_stats[bowling_stats["legal_balls"] >= 300].sort_values("economy_rate").head(10)
    fig8 = px.bar(
        qualified_bowlers, x="economy_rate", y=qualified_bowlers.index,
        orientation="h", labels={"economy_rate": "Economy rate", "y": "Bowler"},
        title="Best Economy Rate",
    )
    fig8.update_yaxes(autorange="reversed")
    st.plotly_chart(fig8, use_container_width=True)

# ---------- Venue & Margins ----------
with tabs[5]:
    st.subheader("Highest scoring venues (avg runs per innings)")
    venue_team_runs = filtered_deliveries.merge(
        filtered_matches[["id", "venue"]], left_on="match_id", right_on="id", how="left"
    ).groupby(["venue", "match_id"])["total_runs"].sum().reset_index()
    avg_venue_runs = venue_team_runs.groupby("venue")["total_runs"].mean().sort_values(ascending=False).head(10)
    fig9 = px.bar(
        avg_venue_runs, x=avg_venue_runs.values, y=avg_venue_runs.index,
        orientation="h", labels={"x": "Average runs", "y": "Venue"},
        title="Highest Scoring Venues",
    )
    fig9.update_yaxes(autorange="reversed")
    st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Biggest winning margins (by runs)")
    biggest_run_wins = filtered_matches[filtered_matches["result"] == "runs"].sort_values("result_margin", ascending=False).head(10).copy()
    biggest_run_wins["matchup_label"] = (
        biggest_run_wins["team1"] + " vs " + biggest_run_wins["team2"] + " (" + biggest_run_wins["season"].astype(str) + ")"
    )
    fig10 = px.bar(
        biggest_run_wins, x="result_margin", y="matchup_label",
        orientation="h", labels={"result_margin": "Margin (runs)", "matchup_label": ""},
        title="Biggest Winning Margins",
    )
    fig10.update_yaxes(autorange="reversed")
    st.plotly_chart(fig10, use_container_width=True)

# ---------- Head-to-Head ----------
with tabs[6]:
    st.subheader("Most-played rivalries")
    decided = filtered_matches[filtered_matches["winner"].notna()].copy()
    decided["team_a"] = decided[["team1", "team2"]].min(axis=1)
    decided["team_b"] = decided[["team1", "team2"]].max(axis=1)
    decided["matchup"] = decided["team_a"] + " vs " + decided["team_b"]

    head_to_head = decided.groupby(["matchup", "winner"]).size().reset_index(name="wins")
    matchup_totals = head_to_head.groupby("matchup")["wins"].sum().sort_values(ascending=False)
    top_rivalries = matchup_totals.head(8).index

    h2h_pivot = head_to_head[head_to_head["matchup"].isin(top_rivalries)].pivot(
        index="matchup", columns="winner", values="wins"
    ).fillna(0)

    fig11 = px.imshow(
        h2h_pivot, text_auto=True, aspect="auto", color_continuous_scale="Blues",
        labels=dict(x="Winner", y="Matchup", color="Wins"),
        title="Head-to-Head Wins - Most Played Rivalries",
    )
    st.plotly_chart(fig11, use_container_width=True)

    st.subheader("Pick two teams to compare directly")
    all_teams = sorted(pd.concat([matches["team1"], matches["team2"]]).unique())
    c1, c2 = st.columns(2)
    team_a = c1.selectbox("Team A", all_teams, index=0)
    team_b = c2.selectbox("Team B", all_teams, index=1)

    if team_a != team_b:
        h2h_matches = matches[
            ((matches["team1"] == team_a) & (matches["team2"] == team_b)) |
            ((matches["team1"] == team_b) & (matches["team2"] == team_a))
        ]
        h2h_decided = h2h_matches[h2h_matches["winner"].notna()]
        st.write(f"**Total matches:** {len(h2h_matches)}")
        st.dataframe(h2h_decided["winner"].value_counts().rename("Wins"), use_container_width=True)
    else:
        st.info("Select two different teams to compare.")