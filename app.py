import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Morel Sniper Pro - Tavernes",
    page_icon="🎯",
    layout="wide"
)

# --- 1. FONCTIONS TECHNIQUES (MÉTÉO & LOGIQUE) ---
def get_weather():
    try:
        # Coordonnées Tavernes (Var)
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.59&longitude=6.01&daily=precipitation_sum,temperature_2m_max&timezone=Europe%2FBerlin"
        data = requests.get(url, timeout=5).json()
        precip_7j = sum(data['daily']['precipitation_sum'][:7])
        tmax = data['daily']['temperature_2m_max'][0]
        return precip_7j, tmax
    except:
        return 0.0, 15.0 # Valeurs par défaut si l'API échoue

precip_reelle, tmax = get_weather()

# --- 2. INTERFACE LATÉRALE (DASHBOARD) ---
st.sidebar.title("🍄 Contrôle Sniper")

# Mode Simulation
st.sidebar.subheader("🛠️ Simulation")
mode_test = st.sidebar.checkbox("Forcer Mode Pluie (>15mm)", value=True)
precip = 20.0 if mode_test else precip_reelle

# Analyse Altitude
st.sidebar.markdown("---")
st.sidebar.subheader("📐 Analyse Altitude")
alt_target = st.sidebar.slider("Altitude de recherche (m)", 300, 1000, 450)

# Conditions de pousse
is_ideal = precip >= 15 and 10 <= tmax <= 22

if is_ideal:
    st.sidebar.success(f"🚀 CONDITIONS IDÉALES\nPluie: {precip}mm | T°: {tmax}°C")
else:
    st.sidebar.warning(f"⏳ ATTENDRE LA PLUIE\nPluie: {precip}mm | T°: {tmax}°C")

# --- 3. LÉGENDE TECHNIQUE ---
with st.sidebar.expander("📚 Légende des Couches", expanded=True):
    st.write("🔵 **Lignes Bleues** : Ruisseaux (L'Humidité)")
    st.write("🟢 **Zones Vertes** : Feuillus (L'Habitat)")
    st.write("🟡 **Zones Colorées** : Calcaire (Le Sol)")
    st.write("🔴 **Cercles** : Zones à 90% de probabilité")

# --- 4. DÉFINITION DES HOTSPOTS (Bases SIG) ---
hotspots = [
    {"nom": "ZONE A : Vallon des Ferrages", "coords": [43.5985, 6.0260], "alt": 420, "info": "Calcaire dur + Thalweg humide."},
    {"nom": "ZONE B : Pied du Petit Bessillon", "coords": [43.5875, 6.0145], "alt": 480, "info": "Éboulis calcaires et lierre."},
    {"nom": "ZONE C : Ravin de la Blanquière", "coords": [43.6060, 6.0380], "alt": 510, "info": "Ubac frais (Exposition Nord-Est)."},
    {"nom": "ZONE D : Marnes de Saint-Cassien", "coords": [43.5920, 5.9950], "alt": 395, "info": "Marnes argileuses (Morilles blondes)."},
    {"nom": "ZONE E : Plateau des Lauves", "coords": [43.6120, 6.0180], "alt": 540, "info": "Bordures de plateau et cuvettes."}
]

# --- 5. CONSTRUCTION DE LA CARTE ---
st.title("🎯 Morel Sniper : Cartographie Prédictive Tavernes")

# Centrage sur Tavernes
m = folium.Map(location=[43.5936, 6.0167], zoom_start=14, tiles=None)

# A. Fond Relief
folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='1. Relief Topo').add_to(m)

# B. Couche Végétation (IGN)
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="LANDCOVER.FORESTINVENTORY.V2",
    name="2. Forêts (Feuillus)",
    transparent=True, fmt="image/png", overlay=True, opacity=0.4, attr="IGN"
).add_to(m)

# C. Couche Géologie (BRGM)
folium.WmsTileLayer(
    url="https://geoservices.brgm.fr/geologie",
    layers="GEOLOGIE",
    name="3. Géologie (Calcaire)",
    transparent=True, fmt="image/png", overlay=True, opacity=0.4, attr="BRGM"
).add_to(m)

# D. Couche Hydrographie (IGN)
folium.WmsTileLayer(
    url="https://data.geopf.ign.fr/wms-r/wms",
    layers="HYDROGRAPHY.NETWORK",
    name="4. Ruisseaux (Eau)",
    transparent=True, fmt="image/png", overlay=True, opacity=0.8, attr="IGN"
).add_to(m)

# E. AFFICHAGE DES CIBLES SI CONDITIONS OK
if is_ideal:
    for spot in hotspots:
        # Filtrage par altitude (marge de 100m par rapport au curseur)
        if abs(spot["alt"] - alt_target) <= 100:
            folium.Circle(
                location=spot["coords"],
                radius=200,
                color="red",
                fill=True,
                fill_opacity=0.3,
                popup=f"<b>{spot['nom']}</b><br>Alt: {spot['alt']}m<br>{spot['info']}"
            ).add_to(m)
            folium.Marker(
                location=spot["coords"],
                icon=folium.Icon(color='red', icon='screenshot', prefix='fa')
            ).add_to(m)

# --- 6. OUTILS & AFFICHAGE ---
plugins.LocateControl(flyTo=True, keepCurrentZoomLevel=True).add_to(m)
plugins.Fullscreen().add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# Affichage final
st_folium(m, width="100%", height=700)

st.caption("Données : BRGM, IGN, Open-Meteo. Logiciel de prospection amateur.")
