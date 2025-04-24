import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# --- App Configuration ---
st.set_page_config(
    page_title="Norway Hexagonal Map",
    page_icon="🇳🇴",
    layout="wide" # Use wide layout for better map display
)

# --- Title and Introduction ---
st.title("🇳🇴 Norway Data Visualization")
st.subheader("Using Uber-style Hexagonal Mapping (Pydeck HexagonLayer)")
st.markdown("""
This app demonstrates visualizing data points across Norway using a hexagonal heatmap.
Random data points are generated within the approximate bounding box of Norway.
The density of points within each hexagon determines its height and color intensity.
You can adjust the number of points and the hexagon radius using the sliders below.
""")

# --- Sidebar Controls ---
st.sidebar.header("Map Controls")
num_points_slider = st.sidebar.slider(
    "Number of data points to generate",
    min_value=100,
    max_value=10000,
    value=5000,
    step=100
)
hexagon_radius_slider = st.sidebar.slider(
    "Hexagon radius (meters)",
    min_value=1000,
    max_value=50000,
    value=10000,
    step=1000
)
elevation_scale_slider = st.sidebar.slider(
    "Elevation Scale",
    min_value=1,
    max_value=100,
    value=20,
    step=1
)

# --- Data Generation ---
# Approximate bounding box for Norway
NORWAY_BOUNDS = {
    "min_lon": 4.0,
    "max_lon": 31.5,
    "min_lat": 57.5,
    "max_lat": 71.5
}

# Generate random points within the bounding box
@st.cache_data # Cache data generation for performance
def generate_data(num_points):
    """Generates a DataFrame with random lat/lon points within Norway's bounds."""
    lat = np.random.uniform(NORWAY_BOUNDS["min_lat"], NORWAY_BOUNDS["max_lat"], num_points)
    lon = np.random.uniform(NORWAY_BOUNDS["min_lon"], NORWAY_BOUNDS["max_lon"], num_points)
    return pd.DataFrame({'lat': lat, 'lon': lon})

data = generate_data(num_points_slider)

st.sidebar.markdown("---") # Separator
st.sidebar.write(f"Generated {len(data)} data points.")
if st.sidebar.button("Regenerate Data"):
    st.cache_data.clear() # Clear cache to regenerate
    st.rerun() # Rerun the app to reflect changes

# --- Map Visualization (Pydeck) ---

# Define the Hexagon Layer
layer = pdk.Layer(
    "HexagonLayer",
    data=data,
    get_position=["lon", "lat"],
    radius=hexagon_radius_slider, # Use slider value for radius
    elevation_scale=elevation_scale_slider, # Use slider value for elevation
    elevation_range=[0, 1000], # Fixed elevation range for consistency
    extruded=True, # Make hexagons 3D
    pickable=True, # Allow hovering to see details
    auto_highlight=True, # Highlight hexagon on hover
    coverage=1, # Controls the overlap of hexagons
    # Color Range: Example using a blue-to-red scale
    color_range=[
        [255, 255, 178, 100], # Light Yellow (low density)
        [254, 204, 92, 120],
        [253, 141, 60, 150],
        [240, 59, 32, 180],
        [189, 0, 38, 220]  # Dark Red (high density)
    ]
)

# Define the initial view state (centered roughly on Norway)
view_state = pdk.ViewState(
    longitude=10.0, # Central longitude for Norway
    latitude=64.0,  # Central latitude for Norway
    zoom=4,         # Zoom level to see most of Norway
    pitch=50,       # Angle looking down at the map
    bearing=0       # North-up orientation
)

# Create the Deck object
deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v10", # Use a light map background
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>Elevation Value:</b> {elevationValue}<br/><b>Number of Points:</b> {count}",
        "style": {"color": "white"}
    }
)

# --- Display Map ---
st.pydeck_chart(deck)

# --- Display Raw Data (Optional) ---
if st.checkbox("Show Raw Data Sample"):
    st.subheader("Raw Data Sample (first 100 rows)")
    st.write(data.head(100))

st.markdown("---")
st.caption("Map powered by Pydeck and Streamlit.")

