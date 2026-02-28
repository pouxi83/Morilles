import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel Hunter - Haut-Var", page_icon="🍄", layout="wide")

# --- 1. MÉTÉO ---
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.60&longitude=6.05&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        return sum(data['daily']['precipitation_sum'][:7]), data['daily']['temperature_2m_max'][0]
    except: return 0.0, 15.0

precip_reelle, tmax = get_weather()

# --- 2. INTERFACE ---
st.sidebar.title("🧭 Réglages de Chasse")
mode_test = st.sidebar.checkbox("Simuler Pluie (Activer Zones)", value=True)
alt_target = st.sidebar.slider("Altitude que je vise (m)", 300, 1000, 420)

precip = 20.0 if mode_test else precip_reelle
is_ideal = precip >= 15 and 10 <= tmax <= 22

# --- 3. TOUS LES HOTSPOTS ---
hotspots = [
    {"nom": "Tavernes - Ferrages", "coords": [43.5985, 6.0260], "alt": 420, "info": "Vallon humide."},
    {"nom": "Tavernes - St-Cassien", "coords": [43.5920, 5.9950], "alt": 395, "info": "Marnes argileuses."},
    {"nom": "Tavernes - Lauves", "coords": [43.6120, 6.0180], "alt": 540, "info": "Bordure plateau."},
    {"nom": "Fox - Plaine", "coords": [43.5950, 6.1020], "alt": 450, "info": "Lisières feuillus."},
    {"nom": "Fox - Vieux Fox", "coords": [43.5820, 6.0950], "alt": 520, "info": "Pente Nord."},
    {"nom": "Montmeyan - Ravin", "coords": [43.6350, 6.0450], "alt": 480, "info": "Encaissé et frais."},
    {"nom": "Montmeyan - Hauts", "coords": [43.6180, 6.0620], "alt": 580, "info": "Cuvettes calcaires."},
    {"nom": "Varages - Vallon Orb", "coords": [43.5850, 5.9550], "alt": 360, "info": "Près des sources."},
    {"nom": "Varages - St-Porphyre", "coords": [43.6050, 5.9420], "alt": 580, "info": "Transition forêt."},
    {"nom": "Aups - Contreforts", "coords": [43.6450, 6.2050], "alt": 650, "info": "Saison tardive."}
]

# --- 4. CARTE ---
st.title("🍄 Morel Sniper : Secteur Haut-Var")

m = folium.Map(location=[43.60, 6.05], zoom_start=12, tiles=None)

folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='Relief').add_to(m)

# Couches SIG
for layer in [
    {"url": "https://data.geopf.ign.fr/wms-r/wms", "lay": "LANDCOVER.FORESTINVENTORY.V2", "name": "Végétation"},
    {"url": "https://geoservices.brgm.fr/geologie", "lay": "GEOLOGIE", "name": "Géologie"},
    {"url": "https://data.geopf.ign.fr/wms-r/wms", "lay": "HYDROGRAPHY.NETWORK", "name": "Ruisseaux"}
]:
    folium.WmsTileLayer(url=layer["url"], layers=layer["lay"], name=layer["name"], 
                        transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

# AFFICHAGE AVEC FILTRE SOUPLE (+/- 200m)
if is_ideal:
    for spot in hotspots:
        if abs(spot["alt"] - alt_target) <= 200:
            folium.Circle(
                location=spot["coords"], radius=300, color="red", fill=True, fill_opacity=0.3,
                popup=f"<b>{spot['nom']}</b><br>Alt: {spot['alt']}m"
            ).add_to(m)
            folium.Marker(location=spot["coords"], icon=folium.Icon(color='red', icon='bullseye', prefix='fa')).add_to(m)

plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)
st_folium(m, width="100%", height=700)
