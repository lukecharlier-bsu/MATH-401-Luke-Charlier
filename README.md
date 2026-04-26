# Understanding The NFL with Synthetic Power Rankings and Simulated Data

**Can we use synthetic data to evaluate how well the NFL identifies its best teams?**

This project simulates realistic NFL seasons using synthetic team strength data (FPI) as a known ground truth to better understand trends within the NFL.

Built for the Boise State Math Senior Showcase, Spring 2026 — Luke Charlier, advised by Dr. Michael Perlmutter.

---

## Background

It's hard to know whether NFL standings and playoff seeding truly reflect team quality. A 17-game season introduces a lot of variance. Sometimes good teams lose, sometimes bad teams win. And when two teams finish with identical records, the NFL's tiebreaker rules (head-to-head, division record, conference record, common games, strength of victory, strength of schedule) may or may not be picking the "true best" team. 


For this project, we need a "ground truth", ie, a reliable masure of each team's strength. We will use **FPI (ESPN's Football Power Index)** as that ground truth, generate syntehtic FPI data for all 32 teams and then simulate full NFL seasons and measure how different systems identify the "true strongest" team.

---

## Three Research Questions

**1. Do existing tiebreakers pick the best team?**
Compares the current NFL ruleset against two alternatives, total point margin and capped point margin. across 1,000 simulated seasons and 10 years of real NFL data (2015–2024).

**2. How often does the best team actually earn the #1 seed?**
Even with perfect tiebreakers, the top FPI team can miss the #1 seed due to schedule variance. This examines the distribution of FPI ranks among 1-seed teams across 10,000 simulated seasons.

**3. How does season length affect seeding accuracy?**
Tests season lengths from 12 to 10,000 games to show how more games allow the best team to rise to the top more reliably.

---

## Key Results

**Tiebreaker accuracy** — how often does the higher-FPI team win the tiebreak?

| Method | Simulated | Real NFL (2015–2024) |
|---|---|---|
| NFL Rules | ~50% | 55.6% |
| Total Margin | 65.8% | 74.6% |
| Capped Margin (±10 pts) | 73.2% | 55.6%* |

*Capped margin simulation vs real data was statistically significantly different (p=0.032) — the only comparison that was.

NFL rules perform no better than a coin flip in simulation (binomial test p=0.225). Total margin substantially outperforms both.

**1-seed distribution** — across 10,000 simulated 17-game seasons, the #1 FPI team in a conference earns the 1-seed 38.8% of the time. The probability drops sharply by rank — the top 3 FPI teams account for over 70% of all 1-seeds.

**Season length** — the probability of the best team earning the 1-seed grows near-exponentially with season length. At 17 games it's ~39%. At 500+ games it approaches 95%.

---

## How the Simulation Works

**Synthetic FPI ratings:**
```
FPI ~ N(-0.016, 3²)
```
Mean and σ chosen to match real-world NFL win distributions.

**Game simulation:**
```
Margin = (FPI₁ - FPI₂) + HF + ε,   ε ~ N(0,1) · σ₂
```
- `HF = 2` — home field advantage
- `σ₂ = 9` — per-game variance

**Season:** 32 teams, 17-game schedule built to match real NFL structure (divisional, cross-divisional, and cross-conference matchups).

**Playoff field:** 4 division winners + 3 wild cards per conference, seeded by wins with tiebreakers applied. Validated against real NFL results from 2002–2025 via `nflreadpy`.

---

## Repo Structure

```
├── Official Analysis.ipynb      # Full analysis — all three questions
├── Graphs for Poster.ipynb      # Generates the 3 poster figures
├── playoffs.py                  # All 3 tiebreaker modes
├── sim_season.py                # Full season simulation
├── sim_game.py                  # Single game simulation
├── generate_schedule.py         # Schedule generation (16/17-game + arbitrary length)
├── real_nfl_schedule.py         # Real NFL results via nflreadpy
├── random_fpi.py                # Synthetic FPI generation
├── simulate_playoffs.py         # Full playoff bracket simulation
├── FPI-1-11-26.csv              # Current season FPI data
├── FPI_Years/                   # Historical ESPN FPI (2015–2024)
└── archive/                     # Older scripts kept for reference
```

---

## Running It

```bash
pip install pandas numpy matplotlib scipy statsmodels streamlit nflreadpy
```

```bash
jupyter notebook "Official Analysis.ipynb"   # full analysis
```

---

## Data

- **Synthetic FPI:** drawn from `N(-0.016, 3²)` each simulation
- **Historical FPI:** ESPN data for 2015–2024, stored in `FPI_Years/`
- **Real game results:** `nflreadpy`, 2002–2025 regular seasons
- FPI accuracy on real data uses 2015–2024 only (years with actual FPI available)
