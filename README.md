# IPL Data Analysis

Exploratory data analysis of IPL (Indian Premier League) match and ball-by-ball data using Python, Pandas, Matplotlib, and Seaborn.

## Project Structure
```
├── data/
│   ├── matches.csv        # Match-level data (teams, toss, venue, result, margin)
│   └── deliveries.csv     # Ball-by-ball data (runs, wickets, extras)
├── notebooks/
│   └── ipl_analysis.ipynb # Main analysis notebook
├── app.py                
└── README.md
```

## What This Analysis Covers
1. **Data Loading & Understanding** — shape, structure, null/duplicate checks
2. **Data Cleaning** — standardizing renamed/relocated franchise names (e.g. Delhi Daredevils → Delhi Capitals)
3. **Toss Analysis** — does winning the toss predict winning the match, and does the bat/field decision matter
4. **Team Performance** — win percentage by team, and which team topped each season
5. **Batting Analysis** — top run scorers, and top strike rates among qualified batters (100+ balls faced)
6. **Bowling Analysis** — top wicket-takers, most economical bowlers, best bowling strike rate
7. **Venue & Match Margin Analysis** — highest/lowest scoring venues, biggest winning margins
8. **Head-to-Head Analysis** — win/loss record between the most-played team rivalries
9. **Visualization & Insights** — a chart plus a written takeaway for each of the above

## Key Findings
- Winning the toss has almost no bearing on winning the match (50.83% vs 49.17%).
- Fielding first after winning the toss wins more often (53.86%) than batting first (45.38%).
- Gujarat Titans (62.2%) and Chennai Super Kings (57.98%) have the best all-time win percentages.
- V Kohli leads all-time run scoring (8,014 runs); the highest strike rate belongs to a different player entirely (J Fraser-McGurk, 220.0).
- YS Chahal leads all bowlers with 205 wickets; A Kumble has the best economy rate (6.58/over).
- Scoring varies meaningfully by venue — Visakhapatnam averages 200 runs/innings vs. Newlands' 128.4.
- Chennai Super Kings vs Mumbai Indians is the most-played rivalry (37 matches), and it's close (MI lead 20–17).

## How to Run
1. Create and activate a virtual environment, then install dependencies:
   ```
   pip install pandas numpy matplotlib seaborn jupyter
   ```
2. Open `notebooks/ipl_analysis.ipynb` in VS Code or Jupyter.
3. Run all cells top to bottom.

## Tools Used
Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook

## Status
Analysis and visualization complete. Streamlit dashboard (`app.py`) is a planned next step, not yet built.
