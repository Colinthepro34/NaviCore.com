# NaviCore 🚇

**Mumbai's Multimodal Transit Engine** — find the smartest route across local trains, metro, monorail, BEST buses, walking, and cabs in one unified system.

🔗 **Live Demo:** [navicore.streamlit.app](https://navicore.streamlit.app)

---

## What is NaviCore?

NaviCore solves Mumbai's "last-mile" problem. Mumbai has one of the world's densest transit networks — Western Line, Central Line, Harbour Line, Trans-Harbour Line, 3 metro lines, monorail, and thousands of BEST bus routes — but no single tool that plans a journey across all of them simultaneously.

NaviCore builds a unified multimodal graph at query time and runs weighted Dijkstra to find the optimal path, whether that means hopping trains, transferring to a bus, or taking a cab to a better-connected station.

---

## Features

- **6 routing modes** — Earliest Arrival, Least Interchange, Public Transport Only, Train Only, Metro & Monorail, Bus Only, Cab Only
- **Real timetable data** — local train and metro travel times sourced from actual schedules, not estimated
- **Smart transfer logic** — inter-line transfers at the same station (e.g. Western ↔ Central at Dadar) with configurable penalties
- **Last-mile handling** — walk within 1 km, cab within 8 km radius of any station automatically considered
- **Snap zone** — stations within 200 m get zero-cost platform-bridge edges (no phantom walk penalty)
- **Directional lines** — Yellow Line (2A) and Red Line (7) correctly modelled as one-way
- **Live route map** — zoomed dark-mode matplotlib map with glow effects, color-coded by mode, START/END star markers
- **Journey breakdown** — per-leg cards with stop chips, distance, time, and mode badges
- **Mobile responsive** — works on phones, tablets, and desktop

---

## Routing Algorithm

NaviCore uses a **weighted Dijkstra shortest-path** on a unified `NetworkX MultiDiGraph` built fresh for each query.

### Graph Structure

```
Node types:
  train_<StationName>__<Line>   — one node per (station, line) pair
  bus_<stop_id>                 — one node per BEST bus stop
  start / end                   — query endpoints

Edge types:
  Rail edges      — timetable time between consecutive stations
  Bus edges       — haversine distance × 4 min/km
  Walk edges      — haversine × 1.3 (road factor) × 12 min/km
  Cab edges       — haversine × 1.3 × 3 min/km (min 1 km)
  Transfer edges  — 5 min platform penalty between lines
  Snap edges      — 0 cost within 200 m of station
```

### Speed Model

| Mode     | Speed         | Notes                          |
|----------|---------------|--------------------------------|
| Walk     | 12 min/km     | haversine × 1.3 road factor    |
| Bus      | 4 min/km      | haversine between stops        |
| Train    | Timetable     | actual schedule data           |
| Metro    | Timetable     | actual schedule data           |
| Cab      | 3 min/km      | min 1 km, haversine × 1.3      |

### Mode Logic

| Mode               | Allowed Networks                        | Access          |
|--------------------|-----------------------------------------|-----------------|
| Earliest Arrival   | All modes                               | Walk + Cab      |
| Least Interchange  | All modes + transfer penalty            | Walk + Cab      |
| Public Transport   | Train + Metro + Monorail + Bus          | Walk only       |
| Train              | Western, Central, Harbour, Trans-Harbour| Walk + Cab      |
| Metro              | Metro Lines + Monorail                  | Walk + Cab      |
| Bus                | BEST Bus                                | Walk + Cab      |
| Cab                | Direct cab                              | —               |

---

## Project Structure

```
NaviCore/
├── frontend.py                    # Streamlit UI — NaviCore interface
├── GPS.py                         # Routing engine — graph builder + Dijkstra
├── Final Train Dataset.csv        # Station coordinates + timetable data
├── Final Bus Dataset.csv          # BEST bus stops + routes
├── Mumbai_Landmarks_filtered.csv  # 599 curated Mumbai landmarks for dropdown
├── mumbai_graph.graphml.gz        # OSMnx road graph (CLI visualizer only)
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Frontend     | Streamlit, HTML/CSS, Matplotlib     |
| Routing      | NetworkX (MultiDiGraph + Dijkstra)  |
| Data         | Pandas                              |
| Geometry     | Haversine formula                   |
| Road graph   | OSMnx (CLI only, not loaded on web) |
| Deployment   | Streamlit Cloud                     |

---

## Installation

```bash
git clone https://github.com/yourusername/navicore.git
cd navicore
pip install -r requirements.txt
streamlit run frontend.py
```

### Requirements

```
streamlit
pandas
networkx
matplotlib
osmnx
```

> **Note:** `osmnx` is listed for CLI use. The web app does **not** load the road graph at runtime — all routing uses haversine distance, keeping memory well within Streamlit Cloud's free tier.

---

## Data Sources

- **Mumbai Local Train** — Western, Central, Harbour, and Trans-Harbour line station sequences and inter-station travel times
- **Mumbai Metro** — Lines 1, 2A, 3, 7, Navi Mumbai Metro with timetable data
- **Mumbai Monorail** — Chembur–Wadala–Jacob Circle
- **BEST Bus** — Routes, stops, and sequences from BEST Undertaking GTFS data
- **Landmarks** — 599 curated Mumbai points of interest (railway stations, malls, colleges, government offices, markets, attractions)

---

## Architecture Decisions

**Why haversine instead of road graph for walk/cab distances?**

The OSMnx Mumbai road graph (~500k edges) consumes ~800 MB of RAM when loaded. On Streamlit Cloud's free tier (1 GB limit), loading it caused OOM crashes. Haversine × 1.3 (road factor) gives distances accurate to within 5–10% of actual road distance for the short hops involved in transit access — well within acceptable margin for transit planning.

**Why build the graph per query instead of precomputing?**

With 5,000+ landmarks × 7 modes = 35,000+ possible route combinations, precomputation would take days and produce gigabytes of data. Per-query graph building takes 0.5–2 seconds and uses ~50 MB peak.

**Why one node per (station, line) pair instead of one per station?**

A physical station like Dadar appears on the Western Line and Central Line. Merging them into one node would hide the transfer penalty. Separate nodes with transfer edges correctly model the 5-minute platform change cost.

---

## Known Limitations

- Bus routes are directional (ascending stop sequence only) — reverse directions are treated as separate trips
- Metro Lines 2A and 7 are one-way in the dataset
- Cab time estimates don't account for Mumbai traffic — actual times will vary significantly during peak hours
- The 8 km cab radius for station access is intentionally generous; Dijkstra will only use it if it produces a faster overall route

---

## Related Project

**PAT.ai** — a natural language data analysis assistant. Upload any dataset, ask questions in plain English, get statistical analysis, visualizations, and predictions automatically.

🔗 [pat-ai.streamlit.app](https://pat-ai-maf6edxnuysrl84qfmjgwt.streamlit.app/)

---

## License

MIT License — see `LICENSE` for details.
