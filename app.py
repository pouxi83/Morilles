import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Morel Hunter - Haut-Var", page_icon="🍄", layout="wide")

# --- 1. MÉTÉO ÉLARGIE ---
def get_weather():
    try:
        # Coordonnées centrales du Haut-Var
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.60&longitude=6.05&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        return sum(data['daily']['precipitation_sum'][:7]), data['daily']['temperature_2m_max'][0]
    except: return 0.0, 15.0

precip_reelle, tmax = get_weather()

# --- 2. INTERFACE & SIMULATION ---
st.sidebar.title("🧭 Prospection Haut-Var")
mode_test = st.sidebar.checkbox("Activer Zones de Chasse", value=True)
alt_target = st.sidebar.slider("Altitude cible (m)", 300, 1000, 450)
precip = 20.0 if mode_test else precip_reelle
is_ideal = precip >= 15 and 10 <= tmax <= 22

# --- 3. BASE DE DONNÉES DES HOTSPOTS ÉLARGIE ---
hotspots = [
    # TAVERNES
    {"nom": "Tavernes - Vallon des Ferrages", "coords": [43.5985, 6.0260], "alt": 420, "info": "Thalweg humide + Calcaire."},
    {"nom": "Tavernes - Saint-Cassien", "coords": [43.5920, 5.9950], "alt": 395, "info": "Marnes argileuses."},
    # FOX-AMPHOUX
    {"nom": "Fox - Bois de la Plaine", "coords": [43.5950, 6.1020], "alt": 450, "info": "Chênes truffiers et lisières."},
    {"nom": "Fox - Vieux Fox (Ubac)", "coords": [43.5820, 6.0950], "alt": 520, "info": "Pente Nord très humide."},
    # MONTMEYAN
    {"nom": "Montmeyan - Ravin du Beau de Ri", "coords": [43.6350, 6.0450], "alt": 480, "info": "Ravin calcaire très encaissé."},
    {"nom": "Montmeyan - Plateau Sud", "coords": [43.6180, 6.0620], "alt": 550, "info": "Cuvettes de terre rouge."},
    # VARAGES
    {"nom": "Varages - Vallon de l'Orb", "coords": [43.5850, 5.9550], "alt": 360, "info": "Proximité de l'eau et des sources."},
    {"nom": "Varages - Saint-Porphyre", "coords": [43.6050, 5.9420], "alt": 580, "info": "Zone de transition calcaire/forêt."},
    # AUPS (Limite)
    {"nom": "Aups - Contreforts du Verdon", "coords": [43.6450, 6.2050], "alt": 650, "info": "Altitude plus haute, idéal en avril."}
]

# --- 4. CARTE ---
st.title("🍄 Morel Hunter : Secteur Tavernes - Fox - Montmeyan")

# Centrage élargi
m = folium.Map(location=[43.60, 6.05], zoom_start=12, tiles=None)

# Couches SIG
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='1. Relief').add_to(m)

folium.WmsTileLayer(url="https://data.geopf.ign.fr/wms-r/wms", layers="LANDCOVER.FORESTINVENTORY.V2", 
                    name="2. Végétation (Feuillus)", transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

folium.WmsTileLayer(url="https://geoservices.brgm.fr/geologie", layers="GEOLOGIE", 
                    name="3. Géologie (Calcaire)", transparent=True, fmt="image/png", overlay=True, opacity=0.4).add_to(m)

folium.WmsTileLayer(url="https://data.geopf.ign.fr/wms-r/wms", layers="HYDROGRAPHY.NETWORK", 
                    name="4. Ruisseaux (Humidité)", transparent=True, fmt="image/png", overlay=True, opacity=0.7).add_to(m)

# AFFICHAGE DES CIBLES
if is_ideal:
    for spot in hotspots:
        # Filtre altitude +/- 150m
        if abs(spot["alt"] - alt_target) <= 150:
            folium.Circle(
                location=spot["coords"], radius=300, color="red", fill=True, fill_opacity=0.3,
                popup=f"<b>{spot['nom']}</b><br>Alt: {spot['alt']}m<br>{spot['info']}"
            ).add_to(m)

# Outils
plugins.LocateControl(flyTo=True).add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

st_folium(m, width="100%", height=700)
