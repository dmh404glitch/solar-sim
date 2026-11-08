import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Solar + Battery Simulator", page_icon="☀️", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Inter', system-ui, sans-serif; }

/* ---------- Animated gradient backdrop ---------- */
.stApp {
    background:
        radial-gradient(900px 600px at 12% 8%, rgba(122,162,255,0.38), transparent 60%),
        radial-gradient(800px 600px at 88% 12%, rgba(255,140,200,0.28), transparent 60%),
        radial-gradient(900px 700px at 70% 95%, rgba(94,234,212,0.24), transparent 60%),
        radial-gradient(700px 500px at 5% 90%, rgba(255,184,77,0.20), transparent 60%),
        #0a0e1f;
    background-attachment: fixed;
    animation: drift 28s ease-in-out infinite alternate;
    background-size: 140% 140%, 140% 140%, 140% 140%, 140% 140%, 100% 100%;
}
@keyframes drift {
    0%   { background-position: 0% 0%, 100% 0%, 100% 100%, 0% 100%, 0 0; }
    100% { background-position: 25% 15%, 75% 20%, 80% 85%, 20% 80%, 0 0; }
}

/* ---------- Liquid glass recipe ---------- */
:root {
    --glass-bg: linear-gradient(135deg, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0.05) 100%);
    --glass-border: 1px solid rgba(255,255,255,0.20);
    --glass-shadow: inset 0 1px 0 rgba(255,255,255,0.35),
                    inset 0 -1px 0 rgba(255,255,255,0.05),
                    0 10px 40px rgba(0,0,0,0.35);
    --glass-blur: blur(24px) saturate(180%);
}

/* Header / chrome */
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1250px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.03));
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border-right: 1px solid rgba(255,255,255,0.14);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: rgba(238,241,255,0.65); font-weight: 600; margin-top: 0.6rem;
}

/* Hero */
.hero {
    background: var(--glass-bg); border: var(--glass-border); box-shadow: var(--glass-shadow);
    backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
    border-radius: 28px; padding: 2rem 2.4rem; margin-bottom: 1.6rem;
    position: relative; overflow: hidden;
}
.hero::after {
    content: ""; position: absolute; top: -60%; left: -20%; width: 60%; height: 220%;
    background: linear-gradient(100deg, transparent, rgba(255,255,255,0.10), transparent);
    transform: rotate(8deg);
}
.hero h1 {
    font-size: 2.3rem; font-weight: 700; margin: 0; letter-spacing: -0.02em;
    background: linear-gradient(90deg, #ffffff, #b9ccff 60%, #ffd9a0);
    -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { margin: 0.5rem 0 0; color: rgba(238,241,255,0.72); font-size: 1.02rem; }
.badge {
    display: inline-block; padding: 0.25rem 0.8rem; border-radius: 999px; font-size: 0.75rem;
    font-weight: 500; margin: 0.9rem 0.4rem 0 0; color: #eef1ff;
    background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.22);
    backdrop-filter: blur(10px);
}

/* Section titles */
.section-title {
    font-size: 0.8rem; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 600;
    color: rgba(238,241,255,0.6); margin: 1.4rem 0 0.7rem 0.3rem;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--glass-bg); border: var(--glass-border); box-shadow: var(--glass-shadow);
    backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
    border-radius: 22px; padding: 1.1rem 1.3rem;
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    border-color: rgba(255,255,255,0.38);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.45), 0 18px 50px rgba(0,0,0,0.45);
}
[data-testid="stMetricLabel"] p {
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em;
    color: rgba(238,241,255,0.62); font-weight: 500;
}
[data-testid="stMetricValue"] { font-size: 1.9rem; font-weight: 650; letter-spacing: -0.02em; }

/* Chart containers (st.container(border=True)) */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--glass-bg); border: var(--glass-border) !important;
    box-shadow: var(--glass-shadow); border-radius: 26px;
    backdrop-filter: var(--glass-blur); -webkit-backdrop-filter: var(--glass-blur);
    padding: 0.6rem 0.8rem;
}

/* Inputs */
[data-testid="stNumberInput"] input, [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.07) !important; border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
}
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.18);
    border-radius: 16px; backdrop-filter: blur(12px);
}
.stCaption, [data-testid="stCaptionContainer"] { color: rgba(238,241,255,0.55); }
</style>
""",
    unsafe_allow_html=True,
)


def style_fig(fig, title):
    """Transparent, glass-friendly Plotly styling."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#eef1ff")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="rgba(238,241,255,0.8)"),
        legend=dict(orientation="h", y=1.12, x=0, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=60, b=10),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor="rgba(255,255,255,0.15)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zeroline=False)
    return fig


DT = 0.25  # time step in hours (15 minutes)

CITIES = {
    "Algiers": (36.75, 3.06),
    "St. Petersburg": (59.93, 30.34),
    "Paris": (48.86, 2.35),
    "Dubai": (25.20, 55.27),
    "Custom": None,
}


@st.cache_data(ttl=3600)
def get_weather(lat, lon, days):
    """Hourly solar radiation (W/m²) for the next `days` days from Open-Meteo (free, no key)."""
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "shortwave_radiation",
            "forecast_days": days,
            "timezone": "auto",
        },
        timeout=10,
    )
    r.raise_for_status()
    return np.array(r.json()["hourly"]["shortwave_radiation"], dtype=float)


def household_load(hours, daily_kwh):
    """Fake but realistic load curve in kW: small base + morning + evening peaks."""
    h = hours % 24
    shape = 0.4 + 0.8 * np.exp(-((h - 7.5) ** 2) / 2) + 1.4 * np.exp(-((h - 20) ** 2) / 3)
    one_day = np.arange(0, 24, DT)
    day_shape = 0.4 + 0.8 * np.exp(-((one_day - 7.5) ** 2) / 2) + 1.4 * np.exp(-((one_day - 20) ** 2) / 3)
    return shape / (day_shape.sum() * DT) * daily_kwh


def simulate(solar, load, capacity, max_kw, round_trip_eff):
    """Step through time: charge/discharge the battery (with losses), import/export the rest."""
    eta = np.sqrt(round_trip_eff)  # loss applied once on the way in, once on the way out
    soc = capacity * 0.5  # start half full
    soc_list, grid_list, export_list = [], [], []
    for s, l in zip(solar, load):
        net = s - l
        if net > 0:  # surplus: charge battery, export the rest
            charge = min(net, max_kw, (capacity - soc) / (DT * eta))
            soc += charge * DT * eta
            export, grid = net - charge, 0.0
        else:  # deficit: discharge battery, import the rest
            discharge = min(-net, max_kw, soc * eta / DT)
            soc -= discharge * DT / eta
            export, grid = 0.0, -net - discharge
        soc_list.append(soc)
        grid_list.append(grid)
        export_list.append(export)
    return np.array(soc_list), np.array(grid_list), np.array(export_list)


# ---------- Sidebar ----------
st.sidebar.header("Time")
days = st.sidebar.slider("Days to simulate", 1, 7, 3)
hours = np.arange(0, 24 * days, DT)

st.sidebar.header("Solar panels")
panel_area = st.sidebar.slider("Panel area (m²)", 1, 100, 12)
efficiency = st.sidebar.slider("Panel efficiency (%)", 10, 25, 18) / 100

st.sidebar.header("Weather")
mode = st.sidebar.radio("Data source", ["Simulated", "Real weather (Open-Meteo)"])

irradiance = None
live_data = False
if mode == "Real weather (Open-Meteo)":
    city = st.sidebar.selectbox("Location", list(CITIES))
    if city == "Custom":
        lat = st.sidebar.number_input("Latitude", value=48.86)
        lon = st.sidebar.number_input("Longitude", value=2.35)
    else:
        lat, lon = CITIES[city]
    try:
        hourly = get_weather(lat, lon, days)
        irradiance = np.interp(hours, np.arange(len(hourly)), hourly)
        live_data = True
        st.sidebar.success(f"Live forecast loaded ({days} days)")
    except Exception as e:
        st.sidebar.warning(f"Could not load weather ({e}). Using simulation.")

if irradiance is None:
    peak_sun = st.sidebar.slider("Peak sunlight (W/m²)", 200, 1000, 800)
    cloud_cover = st.sidebar.slider("Cloud cover (%)", 0, 100, 20) / 100
    sun_shape = np.clip(np.sin(((hours % 24) - 6) / 12 * np.pi), 0, None)
    irradiance = peak_sun * sun_shape * (1 - 0.75 * cloud_cover)

st.sidebar.header("Home and battery")
daily_kwh = st.sidebar.slider("Household use per day (kWh)", 3, 40, 12)
capacity = st.sidebar.slider("Battery capacity (kWh)", 0, 30, 5)
max_kw = st.sidebar.slider("Battery max power (kW)", 1, 10, 3)
round_trip = st.sidebar.slider("Battery round-trip efficiency (%)", 70, 100, 90) / 100

st.sidebar.header("Money and CO₂")
buy_price = st.sidebar.number_input("Electricity price ($/kWh)", 0.01, 1.0, 0.20, 0.01)
sell_price = st.sidebar.number_input("Export price ($/kWh)", 0.0, 1.0, 0.05, 0.01)
panel_cost = st.sidebar.number_input("Panel cost ($ per m²)", 50, 600, 250, 10)
battery_cost = st.sidebar.number_input("Battery cost ($ per kWh)", 50, 1000, 350, 10)
co2_factor = st.sidebar.number_input("Grid CO₂ (kg per kWh)", 0.0, 1.2, 0.40, 0.05)

# ---------- Calculations ----------
solar = irradiance * panel_area * efficiency / 1000  # kW
load = household_load(hours, daily_kwh)
soc, grid, export = simulate(solar, load, capacity, max_kw, round_trip)

produced = solar.sum() * DT
consumed = load.sum() * DT
imported = grid.sum() * DT
exported = export.sum() * DT
self_suff = 100 * (1 - imported / consumed)

cost_without = consumed * buy_price
cost_with = imported * buy_price - exported * sell_price
saved = cost_without - cost_with
system_cost = panel_area * panel_cost + capacity * battery_cost
yearly_saving = saved / days * 365
payback = system_cost / yearly_saving if yearly_saving > 0 else float("inf")
co2_saved = (consumed - imported) * co2_factor

# ---------- Display ----------
source_label = "Live forecast" if live_data else "Simulated sun"
st.markdown(
    f"""
<div class="hero">
  <h1>☀️ Solar + Battery Home Simulator</h1>
  <p>See how panels, a battery and your daily habits shape your energy bill and carbon footprint.</p>
  <span class="badge">{days} day{'s' if days > 1 else ''}</span>
  <span class="badge">{panel_area} m² panels</span>
  <span class="badge">{capacity} kWh battery</span>
  <span class="badge">{source_label}</span>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Energy</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Solar produced", f"{produced:.1f} kWh")
c2.metric("Home used", f"{consumed:.1f} kWh")
c3.metric("Bought from grid", f"{imported:.1f} kWh")
c4.metric("Self-sufficiency", f"{self_suff:.0f}%")

st.markdown('<div class="section-title">Money and climate</div>', unsafe_allow_html=True)
d1, d2, d3, d4 = st.columns(4)
d1.metric("Money saved", f"${saved:.2f}")
d2.metric("System cost", f"${system_cost:,.0f}")
d3.metric("Payback (rough)", f"{payback:.1f} years" if payback != float("inf") else "never")
d4.metric("CO₂ avoided", f"{co2_saved:.1f} kg")
st.caption(
    f"Exported to grid: {exported:.1f} kWh. Payback assumes these {days} days "
    "repeat all year, so treat it as a rough estimate."
)

t = pd.Timestamp.today().normalize() + pd.to_timedelta(hours, unit="h")

st.markdown('<div class="section-title">Power over time</div>', unsafe_allow_html=True)
with st.container(border=True):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t, y=solar, name="Solar (kW)", fill="tozeroy",
        line=dict(color="#ffb84d", width=2.5), fillcolor="rgba(255,184,77,0.22)"))
    fig.add_trace(go.Scatter(
        x=t, y=load, name="Home use (kW)", line=dict(color="#7aa2ff", width=2.5)))
    fig.add_trace(go.Scatter(
        x=t, y=grid, name="From grid (kW)", line=dict(color="#ff7aa8", width=2, dash="dot")))
    style_fig(fig, "Solar vs. home use vs. grid")
    fig.update_yaxes(title_text="kW")
    st.plotly_chart(fig, width="stretch")

if capacity > 0:
    st.markdown('<div class="section-title">Battery</div>', unsafe_allow_html=True)
    with st.container(border=True):
        fig2 = go.Figure(go.Scatter(
            x=t, y=soc, name="Battery", fill="tozeroy",
            line=dict(color="#5eead4", width=2.5), fillcolor="rgba(94,234,212,0.20)"))
        style_fig(fig2, "Battery charge")
        fig2.update_yaxes(title_text="kWh", range=[0, capacity])
        st.plotly_chart(fig2, width="stretch")
