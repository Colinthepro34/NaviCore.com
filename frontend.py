import streamlit as st
import pandas as pd
import io
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

# Ensure local imports for GPS logic
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from GPS import MumbaiData, Router

# ──────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG & STYLES
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="NaviCore", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=DM+Sans:wght@400;500;700&display=swap');
    
    /* Remove default top padding */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 0rem !important; }

    /* Global Styles */
    body { color: black; background-color: white; }

    /* ============================
       HEADER
    ============================ */

    .ub-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 60px;
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border);
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .ub-logo {
        font-family: 'Syne', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -1px;
    }

    .ub-nav-links {
        display: flex;
        gap: 36px;
        list-style: none;
        margin: 0; padding: 0;
    }

    .ub-nav-links li a {
        color: var(--text-muted);
        text-decoration: none;
        font-size: 14px;
        font-weight: 500;
        transition: color .2s;
    }

    .ub-nav-links li a:hover { color: var(--text-primary); }
    .ub-nav-actions { display: flex; gap: 16px; align-items: center; }

    .ub-btn-ghost {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--text-primary);
        padding: 9px 22px;
        border-radius: 500px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: background .2s, color .2s;
    }
    .ub-btn-ghost:hover { background: var(--bg-card); }

    .ub-btn-solid {
        background: var(--btn-bg);
        border: none;
        color: var(--btn-text);
        padding: 9px 22px;
        border-radius: 500px;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        transition: background .2s;
    }
    .ub-btn-solid:hover { background: var(--accent-hover); }

    /* Primary Buttons (Black) */
    div.stButton > button[kind="primary"] {
        background-color: black;
        color: white;
        border: none;
        padding: 0.55rem 1.2rem;
        font-weight: 600;
        border-radius: 8px;
        font-family: 'DM Sans', sans-serif;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #222;
        border: none;
        color: white;
    }

    /* MIDDLE BLACK SECTION STYLING */
    .black-section-container {
        background-color: black;
        color: white;
        padding: 4rem;
        border-radius: 16px;
        margin: 2rem 0;
    }

    .black-section-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
    }

    .black-section-text {
        font-size: 1.1rem;
        line-height: 1.7;
        color: #aaaaaa;
        margin-bottom: 2rem;
    }

    .white-btn {
        background-color: white;
        color: black;
        padding: 11px 24px;
        text-decoration: none;
        font-weight: 700;
        border-radius: 8px;
        display: inline-block;
        font-size: 0.9rem;
        transition: background 0.15s;
    }

    .white-btn:hover {
        background-color: #f0f0f0;
        color: black;
    }

    /* Sticky Bottom Bar */
    .sticky-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 15px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        text-align: center;
        z-index: 999;
    }

    .sticky-btn {
        background-color: black;
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 16px;
        border: none;
        cursor: pointer;
        width: 100%;
        max-width: 400px;
    }

    .sticky-btn:hover { background-color: #333; }

    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1.5px solid #e0e0e0;
        padding: 0.5rem 0.75rem;
        font-family: 'DM Sans', sans-serif;
    }

    .stTextInput > div > div > input:focus {
        border-color: #111;
        box-shadow: none;
    }

    /* Combined Leg Card Styling */
    .leg-card {
        background: #111d35; border-radius: 10px; border-left: 5px solid #ccc;
        padding: 14px 16px; margin-bottom: 12px; color: #e8eaf6;
    }
    .leg-header {
        font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 700;
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;
    }
    .leg-route { color: #9aa7c4; font-size: 0.85rem; }
    .leg-stats { font-size: 0.8rem; color: #9aa7c4; background: #1c2d4a; border-radius: 6px; padding: 2px 8px; }
    .stop-chip {
        display: inline-block; border-radius: 12px; padding: 2px 9px;
        font-size: 0.78rem; margin: 2px; font-weight: 600;
    }

    /* Feature cards */
    .feature-card {
        background: linear-gradient(145deg, #1a2540, #0f1d35);
        border: 1px solid #2a3a60;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        transition: transform 0.2s;
    }
    .feature-card:hover { transform: translateY(-3px); }
    .feature-icon { font-size: 2rem; margin-bottom: 8px; }
    .feature-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; margin: 0 0 6px; }
    .feature-desc  { font-size: 0.9rem; color: #9aa7c4; margin: 0; }

    /* ============================
       MOBILE RESPONSIVE
    ============================ */

    @media (max-width: 768px) {

        /* Navbar: logo flush left, compact actions */
        .ub-nav {
            padding: 12px 16px;
            justify-content: flex-start;
            gap: 0;
        }

        .ub-logo {
            font-size: 22px;
            flex: 1;
            text-align: left;
        }

        .ub-nav-links { display: none; }

        .ub-nav-actions {
            gap: 8px;
            flex-shrink: 0;
        }

        .ub-btn-ghost, .ub-btn-solid {
            padding: 7px 13px;
            font-size: 12px;
        }

        /* Tighten page padding */
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }

        /* Black section */
        .black-section-container {
            padding: 2rem 1.2rem;
            border-radius: 12px;
        }

        .black-section-title {
            font-size: 2rem;
        }

        .black-section-text {
            font-size: 0.95rem;
        }

        /* Feature cards: full-width stack */
        .feature-card {
            margin-bottom: 12px;
        }

        /* Sticky bottom bar */
        .sticky-btn {
            font-size: 14px;
            padding: 10px 20px;
        }

        /* Leg cards: compact */
        .leg-card {
            padding: 10px 12px;
        }

        .leg-header {
            font-size: 0.9rem;
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;
        }

        .leg-stats {
            font-size: 0.75rem;
        }

        .stop-chip {
            font-size: 0.72rem;
            padding: 2px 7px;
        }
    }

    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 2. DATA INITIALIZATION
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_core_data():
    try:
        data = MumbaiData()
        router = Router(data)
        return data, router
    except Exception as e:
        st.error(f"Failed to load Mumbai transport data: {e}")
        return None, None

@st.cache_data
def get_landmark_list():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Mumbai Landmarks.csv")
    if not os.path.exists(path):
        st.error("Mumbai Landmarks.csv not found in directory.")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df = df.dropna(subset=["latitude", "longitude", "name"])
    df["label"] = df.apply(lambda r: f"{r['name']} — {str(r.get('category','')).replace('_',' ')}", axis=1)
    return df.sort_values("name")

# RUN DATA LOADING
data, router = load_core_data()
landmarks_df = get_landmark_list()

# DEFINE THE MISSING VARIABLES GLOBALLY
if not landmarks_df.empty:
    landmark_labels = ["📍 Custom coordinates..."] + landmarks_df["label"].tolist()
    landmark_map = {row["label"]: (row["latitude"], row["longitude"]) for _, row in landmarks_df.iterrows()}
else:
    landmark_labels = ["📍 Custom coordinates..."]
    landmark_map = {}

MODE_HEX = {"train": "#ff3333", "metro": "#00e5c0", "bus": "#1e90ff", "walk": "#aaaaaa", "car": "#ffd700"}
MODE_EMOJI = {"walk": "🚶", "train": "🚆", "metro": "🚇", "bus": "🚌", "car": "🚖"}

# ──────────────────────────────────────────────────────────────────────────────
# 3. HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
def friendly_node(node_id: str, data: MumbaiData) -> str:
    if node_id == "start": return "Start"
    if node_id == "end": return "Destination"
    if node_id.startswith("train_"): return node_id[len("train_"):].split("__")[0].title()
    if node_id.startswith("bus_"):
        stop_id = node_id[len("bus_"):]
        rows = data.bus_df[data.bus_df["stop_id"] == stop_id]["stop_name"]
        return rows.iloc[0].title() if not rows.empty else stop_id
    return node_id

def group_into_legs(steps):
    legs = []
    for step in steps:
        mode = step["mode"]
        route = step.get("route", "")
        if legs and legs[-1]["mode"] == mode and legs[-1]["route"] == route:
            legs[-1]["steps"].append(step)
            legs[-1]["distance_km"] += step["distance_km"]
            legs[-1]["time_min"] += step["time_min"]
        else:
            legs.append({
                "mode": mode, "route": route, "steps": [step],
                "distance_km": step["distance_km"], "time_min": step["time_min"],
            })
    return legs

# ──────────────────────────────────────────────────────────────────────────────
# 4. ROUTE POP-UP
# ──────────────────────────────────────────────────────────────────────────────
@st.dialog("Route Details", width="large")
def show_route_popup(start_coords, end_coords, mode_choice):
    with st.status("Analyzing routes and rendering multimodal map...", expanded=True) as status:
        st.write("Optimizing transport path...")
        result = router.route(start_coords, end_coords, mode_choice)
        
        if not result or result[0] is None:
            status.update(label="No route found.", state="error")
            st.warning("No path found for this mode. Try 'Earliest Arrival'.")
            return

        st.write("Fetching map geometry...")
        path, steps, total_time, advisories, G_multi = result
        legs = group_into_legs(steps)
        total_dist = sum(s["distance_km"] for s in steps)

        # ── Collect all route coordinates ──────────────────────────────────
        route_lats, route_lons = [], []
        for s in steps:
            if s.get("seg_start") and s.get("seg_end"):
                route_lats += [s["seg_start"][0], s["seg_end"][0]]
                route_lons += [s["seg_start"][1], s["seg_end"][1]]

        # Fallback to start/end coords if no seg geometry
        if not route_lats:
            route_lats = [start_coords[0], end_coords[0]]
            route_lons = [start_coords[1], end_coords[1]]

        # ── Compute padded bounding box ────────────────────────────────────
        PAD = 0.012  # ~1.3 km padding in degrees
        min_lat, max_lat = min(route_lats) - PAD, max(route_lats) + PAD
        min_lon, max_lon = min(route_lons) - PAD, max(route_lons) + PAD

        # ── Draw background road graph cropped to bbox ─────────────────────
        fig, ax = ox.plot_graph(
            data.G_road,
            show=False, close=False,
            node_size=0,
            edge_color="#2a3a5c",
            edge_linewidth=0.5,
            edge_alpha=0.6,
            bgcolor="#0a1628",
            figsize=(8, 8),
        )

        # Zoom into route bounding box
        ax.set_xlim(min_lon, max_lon)
        ax.set_ylim(min_lat, max_lat)

        # ── Draw route segments ────────────────────────────────────────────
        for s in steps:
            if s.get("seg_start") and s.get("seg_end"):
                color = MODE_HEX.get(s["mode"], "white")
                # Draw thick glow underneath
                ax.plot(
                    [s["seg_start"][1], s["seg_end"][1]],
                    [s["seg_start"][0], s["seg_end"][0]],
                    color=color, lw=7, alpha=0.25, zorder=4, solid_capstyle="round"
                )
                # Draw main line
                ax.plot(
                    [s["seg_start"][1], s["seg_end"][1]],
                    [s["seg_start"][0], s["seg_end"][0]],
                    color=color, lw=3, zorder=5, solid_capstyle="round"
                )

        # ── Walk legs: dashed yellow lines ────────────────────────────────
        for s in steps:
            if s["mode"] == "walk" and s.get("seg_start") and s.get("seg_end"):
                ax.plot(
                    [s["seg_start"][1], s["seg_end"][1]],
                    [s["seg_start"][0], s["seg_end"][0]],
                    color="#f5c518", lw=2.5, linestyle="--", zorder=6,
                    dash_capstyle="round"
                )

        # ── Intermediate stop dots ─────────────────────────────────────────
        seen = set()
        for s in steps:
            for coord_key in ("seg_start", "seg_end"):
                c = s.get(coord_key)
                if c and c not in seen:
                    seen.add(c)
                    mode_color = MODE_HEX.get(s["mode"], "#ccc")
                    ax.plot(c[1], c[0], "o",
                            color=mode_color, markersize=5,
                            markeredgecolor="white", markeredgewidth=0.8, zorder=7)

        # ── START marker ───────────────────────────────────────────────────
        ax.plot(start_coords[1], start_coords[0],
                marker="*", color="#00e5c0", markersize=18,
                markeredgecolor="white", markeredgewidth=0.8, zorder=10)
        ax.annotate(
            " START", (start_coords[1], start_coords[0]),
            fontsize=9, fontweight="bold", color="#00e5c0",
            xytext=(6, 4), textcoords="offset points", zorder=11,
            fontfamily="monospace"
        )

        # ── END marker ────────────────────────────────────────────────────
        ax.plot(end_coords[1], end_coords[0],
                marker="*", color="#ff3333", markersize=18,
                markeredgecolor="white", markeredgewidth=0.8, zorder=10)
        ax.annotate(
            " END", (end_coords[1], end_coords[0]),
            fontsize=9, fontweight="bold", color="#ff3333",
            xytext=(6, 4), textcoords="offset points", zorder=11,
            fontfamily="monospace"
        )

        fig.tight_layout(pad=0)
        status.update(label="Route Loaded Successfully!", state="complete", expanded=False)

    st.subheader(f"⏱ {total_time:.1f} min | 📏 {total_dist:.2f} km")
    col_map, col_list = st.columns([1.2, 1])
    
    with col_map:
        st.pyplot(fig)

    with col_list:
        st.markdown("### 📋 Journey Breakdown")
        for leg in legs:
            color = MODE_HEX.get(leg["mode"], "#888")
            emoji = MODE_EMOJI.get(leg["mode"], "•")
            stops = [friendly_node(s["from"], data) for s in leg["steps"]]
            stops.append(friendly_node(leg["steps"][-1]["to"], data))
            unique_stops = list(dict.fromkeys(stops))
            chips = "".join([f"<span class='stop-chip' style='background:{color}33; color:{color}; border:1px solid {color}55;'>{s}</span>" for s in unique_stops])

            st.markdown(f"""
            <div class="leg-card" style="border-left-color:{color};">
              <div class="leg-header">
                <span>{emoji} {leg['mode'].title()} <span class="leg-route">{f'— {leg["route"]}' if leg['route'] else ''}</span></span>
                <span class="leg-stats">{leg['distance_km']:.2f} km | {leg['time_min']:.1f} min</span>
              </div>
              <div class="leg-body">
                <div><strong>{unique_stops[0]}</strong> → <strong>{unique_stops[-1]}</strong></div>
                <div style="margin-top:8px;">{chips}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# 5. MAIN UI
# ──────────────────────────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <nav class="ub-nav">
      <div class="ub-logo">NaviCore</div>
      <div class="ub-nav-actions">
        <button class="ub-btn-ghost">Log in</button>
        <button class="ub-btn-solid">Sign up</button>
      </div>
    </nav>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("Find the smartest route now")

        s_name = st.selectbox("Start Point", options=landmark_labels)
        e_name = st.selectbox("Destination", options=landmark_labels, index=min(10, len(landmark_labels)-1))

        mode_option = st.selectbox("Preferred Mode", options=["earliest_arrival", "public_transport", "train", "metro", "bus", "car"])

        if st.button("Calculate Route", type="primary", use_container_width=True):
            s_coords = landmark_map.get(s_name, (19.0760, 72.8777))
            e_coords = landmark_map.get(e_name, (19.1972, 72.9780))
            show_route_popup(s_coords, e_coords, mode_option)

    with col_right:
        st.image("https://cn-geo1.uber.com/image-proc/crop/resizecrop/udam/format=auto/width=552/height=552/srcb64=aHR0cHM6Ly90Yi1zdGF0aWMudWJlci5jb20vcHJvZC91ZGFtLWFzc2V0cy80MmEyOTE0Ny1lMDQzLTQyZjktODU0NC1lY2ZmZmUwNTMyZTkucG5n")

    # ==========================================
    # PART 2: THE BLACK SECTION
    # ==========================================
    st.markdown("""
    <div class="black-section-container">
        <div style="display: flex; flex-wrap: wrap; gap: 2rem; align-items: center;">
            <div style="flex: 1; min-width: 300px;">
                <div class="black-section-title">PAT.ai</div>
                <div class="black-section-text">
                    PAT.ai (Perform • Analyze • Transform) is a smart data assistant that lets users upload a dataset and analyze it using simple natural language commands.
                    It automatically interprets prompts to perform statistical analysis, visualization, data cleaning, and predictions.
                </div>
                <a href="#" class="white-btn">Try it</a>
            </div>
            <div style="flex: 1; min-width: 300px; text-align: center;">
                <img src="https://cn-geo1.uber.com/image-proc/crop/resizecrop/udam/format=auto/width=552/height=368/srcb64=aHR0cHM6Ly90Yi1zdGF0aWMudWJlci5jb20vcHJvZC91ZGFtLWFzc2V0cy9jNjQyNWRmNC0zMTkwLTRmZTEtODY2Ni02YTVhZjJjMGEwNDkucG5n"
                     alt="NaviCore Pro"
                     style="max-width: 100%; height: auto; border-radius: 12px;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # PART 3: BOTTOM WHITE SECTION
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)

    col3, col4 = st.columns([1, 1], gap="large")

    with col3:
        st.image(
            "https://cn-geo1.uber.com/image-proc/crop/resizecrop/udam/format=auto/width=552/height=311/srcb64=aHR0cHM6Ly90Yi1zdGF0aWMudWJlci5jb20vcHJvZC91ZGFtLWFzc2V0cy9kNjQ4ZjViNi1iYjVmLTQ1MGUtODczMy05MGFlZmVjYmQwOWUuanBn"
        )

    with col4:
        st.title("How we works?")
        st.markdown("""
        NaviCore is a multimodal transit engine designed for Mumbai that solves the "last-mile" problem by merging road data with local train, metro, monorail, and BEST bus networks. Using a weighted Dijkstra algorithm, the system evaluates millions of combinations to find the most efficient path based on user preferences, such as "Earliest Arrival" to minimize time or "Least Interchange" to reduce transfers.
        The system applies a dynamic speed model—walking at 12 min/km, buses at 4 min/km, and cabs at 3 min/km—while incorporating fixed rail timetables and "snap" logic to ensure every route is realistic and navigable.
        """)

    # ==========================================
    # FEATURE CARDS SECTION
    # ==========================================
    if 'compute_clicked' not in st.session_state or not st.session_state.compute_clicked:
        st.subheader("Choose your routing strategy")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div class='feature-card'>
              <div class='feature-icon'>⚡</div>
              <div class='feature-title'>Earliest Arrival</div>
              <p class='feature-desc'>Dijkstra across all modes — local train, metro,
              monorail, bus, cab and walk — minimising total journey time.</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class='feature-card'>
              <div class='feature-icon'>🔄</div>
              <div class='feature-title'>Least Interchange</div>
              <p class='feature-desc'>Uses all modes but penalises every line or
              mode change heavily, so you transfer as few times as possible.</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class='feature-card'>
              <div class='feature-icon'>🚏</div>
              <div class='feature-title'>Public Transport Only</div>
              <p class='feature-desc'>All transit systems, walk-only access — no cabs.
              Forces the route to stay on trains, metro, monorail and buses.</p>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

    # ==========================================
    # STICKY BOTTOM BAR
    # ==========================================
    st.markdown("""
        <div class="sticky-bottom">
            <button class="sticky-btn" onclick="window.scrollTo(0,0);">Calculate Route</button>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
